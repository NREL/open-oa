#################################################
# Data import script for La Haute Borne Project #
#################################################
"""
This is the import script for the example ENGIE La Haute Borne project. Below
is a description of data quality for each data frame and an overview of the
steps taken to correct the raw data for use in the PRUF OA code.

1. SCADA dataframe
- 10-minute SCADA data for each of the four turbines in the project
- Power, wind speed, wind direction, nacelle position, wind vane, temperature,
  blade pitch
- Corrects to UTC timezone when importing
- Removes some outliers and stuck sensor values

2. Meter data frame
- 10-minute performance data provided in energy units (kWh)
- Generated by adding artificial electrical loss and uncertaitny to SCADA data
- No need for timezone correction

3. Curtailment data frame
- 10-minute availability and curtailment data in kwh
- Generated by estimating availability and curtailment from SCADA data
- Below-normal production classified as curtailment if present at all turbines.
  Otherwise, classified as availability loss
- No need for timezone correction

4. Reanalysis products
- Import MERRA-2 and ERA5 1-hour reanalysis data
- Wind speed, wind direction, temperature, and density

"""
from __future__ import annotations

import re
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

import openoa.utils.unit_conversion as un
import openoa.utils.met_data_processing as met
from openoa.logging import logging
from openoa.plant import PlantData
from openoa.utils import filters, timeseries


logger = logging.getLogger()


def extract_data(path="data/la_haute_borne"):
    """
    Extract zip file containing project engie data.
    """
    path = Path(path).resolve()
    if not path.exists():
        logger.info("Extracting compressed data files")
        with ZipFile(path.with_suffix(".zip")) as zipfile:
            zipfile.extractall(path)


def clean_scada(scada_file: str | Path) -> pd.DataFrame:
    """Reads in and cleans up the SCADA data

    Args:
        scada_file (:obj: `str` | `Path`): The file object corresponding to the SCADA data.

    Returns:
        pd.DataFrame: The cleaned up SCADA data that is ready for loading into a `PlantData` object.
    """
    scada_freq = "10T"

    logger.info("Loading SCADA data")
    scada_df = pd.read_csv(scada_file)
    logger.info("SCADA data loaded")

    # We know that the timestamps are in local time, so we want to convert them to UTC
    logger.info("Timestamp conversion to datetime and UTC")
    scada_df["time"] = pd.to_datetime(scada_df["Date_time"], utc=True).dt.tz_localize(None)

    # There are duplicated timestamps, so let's ensure we drop the duplicates for each turbine
    scada_df = scada_df.drop_duplicates(subset=["time", "Wind_turbine_name"], keep="first")

    # Remove extreme values from the temperature field
    logger.info("Removing out of range of temperature readings")
    scada_df = scada_df[(scada_df["Ot_avg"] >= -15.0) & (scada_df["Ot_avg"] <= 45.0)]

    # Filter out the unresponsive sensors
    # Due to data discretization, there appear to be a large number of repeating values
    logger.info("Flagging unresponsive sensors")
    turbine_id_list = scada_df.Wind_turbine_name.unique()
    sensor_cols = ["Ba_avg", "P_avg", "Ws_avg", "Va_avg", "Ot_avg", "Ya_avg", "Wa_avg"]
    for t_id in turbine_id_list:
        ix_turbine = scada_df["Wind_turbine_name"] == t_id

        # Cancel out readings where the wind vane direction repeats more than 3 times in a row
        ix_flag = filters.unresponsive_flag(scada_df.loc[ix_turbine], 3, col=["Va_avg"])
        scada_df.loc[ix_turbine].loc[ix_flag.values, sensor_cols]

        # Cancel out the temperature readings where the value repeats more than 20 times in a row
        ix_flag = filters.unresponsive_flag(scada_df.loc[ix_turbine], 20, col=["Ot_avg"])

        # NOTE: ix_flag is flattened here because as a series it's shape = (N, 1) and
        # incompatible with this style of indexing, so we need it as shape = (N,)
        scada_df.loc[ix_turbine, "Ot_avg"].loc[ix_flag.values.flatten()] = np.nan

    logger.info("Converting pitch to the range [-180, 180]")
    scada_df.loc[:, "Ba_avg"] = scada_df["Ba_avg"] % 360
    ix_gt_180 = scada_df["Ba_avg"] > 180.0
    scada_df.loc[ix_gt_180, "Ba_avg"] = scada_df.loc[ix_gt_180, "Ba_avg"] - 360.0

    logger.info("Calculating energy production")
    scada_df["energy_kwh"] = un.convert_power_to_energy(scada_df.P_avg * 1000, scada_freq) / 1000

    return scada_df


def prepare(path: str | Path = "data/la_haute_borne", return_value="plantdata"):
    """
    Do all loading and preparation of the data for this plant.
    args:
    - path (str): Path to la_haute_borne data folder. If it doesn't exist, we will try to extract a zip file of the same name.
    - scada_df (pandas.DataFrame): Override the scada dataframe with one provided by the user.
    - return_value (str): "plantdata" will return a fully constructed PlantData object. "dataframes" will return a list of dataframes instead.
    """

    if type(path) == str:
        path = Path(path)

    # Extract data if necessary
    extract_data(path)

    ###################
    # Plant Metadata - not used
    ###################

    # lat_lon = (48.452, 5.588)
    # plant_capacity = 8.2  # MW
    # num_turbines = 4
    # turbine_capacity = 2.05  # MW

    ###################
    # SCADA DATA #
    ###################
    scada_df = clean_scada(path / "la-haute-borne-data-2014-2015.csv")

    ##############
    # METER DATA #
    ##############
    logger.info("Reading in the meter data")
    meter_df = pd.read_csv(path / "plant_data.csv")

    # Create datetime field
    meter_df["time"] = pd.to_datetime(meter_df.time_utc).dt.tz_localize(None)

    # Drop the fields we don't need
    meter_df.drop(["time_utc", "availability_kwh", "curtailment_kwh"], axis=1, inplace=True)

    #####################################
    # Availability and Curtailment Data #
    #####################################
    logger.info("Reading in the curtailment data")
    curtail_df = pd.read_csv(path / "plant_data.csv")  # Load Availability and Curtail data

    # Create datetime field with a UTC base
    curtail_df["time"] = pd.to_datetime(curtail_df.time_utc).dt.tz_localize(None)

    # Drop the fields we don't need
    curtail_df.drop(["time_utc"], axis=1, inplace=True)

    ###################
    # REANALYSIS DATA #
    ###################
    logger.info("Reading in the reanalysis data and calculating the extra fields")

    # MERRA2
    reanalysis_merra2_df = pd.read_csv(path / "merra2_la_haute_borne.csv")

    # Create datetime field with a UTC base
    reanalysis_merra2_df["datetime"] = pd.to_datetime(
        reanalysis_merra2_df["datetime"], utc=True
    ).dt.tz_localize(None)

    # calculate wind direction from u, v
    reanalysis_merra2_df["winddirection_deg"] = met.compute_wind_direction(
        reanalysis_merra2_df["u_50"],
        reanalysis_merra2_df["v_50"],
    )

    # Drop the fields we don't need
    reanalysis_merra2_df.drop(["Unnamed: 0"], axis=1, inplace=True)

    # ERA5
    reanalysis_era5_df = pd.read_csv(path / "era5_wind_la_haute_borne.csv")

    # remove a duplicated datetime column
    reanalysis_era5_df = reanalysis_era5_df.loc[:, ~reanalysis_era5_df.columns.duplicated()].copy()

    # Create datetime field with a UTC base
    reanalysis_era5_df["datetime"] = pd.to_datetime(
        reanalysis_era5_df["datetime"], utc=True
    ).dt.tz_localize(None)

    # Fill the 2 missing time stamps with NaN values
    reanalysis_era5_df = reanalysis_era5_df.set_index(pd.DatetimeIndex(reanalysis_era5_df.datetime))
    reanalysis_era5_df = reanalysis_era5_df.asfreq("1H")
    reanalysis_era5_df["datetime"] = reanalysis_era5_df.index

    # calculate wind direction from u, v
    reanalysis_era5_df["winddirection_deg"] = met.compute_wind_direction(
        reanalysis_era5_df["u_100"],
        reanalysis_era5_df["v_100"],
    )

    # Drop the fields we don't need
    reanalysis_era5_df.drop(["Unnamed: 0"], axis=1, inplace=True)

    ##############
    # ASSET DATA #
    ##############

    logger.info("Reading in the asset data")
    asset_df = pd.read_csv(path / "la-haute-borne_asset_table.csv")

    # Assign type to turbine for all assets
    asset_df["type"] = "turbine"

    # Return the appropriate data format
    if return_value == "dataframes":
        return (
            scada_df,
            meter_df,
            curtail_df,
            asset_df,
            dict(era5=reanalysis_era5_df, merra2=reanalysis_merra2_df),
        )
    elif return_value == "plantdata":
        # Build and return PlantData
        engie_plantdata = PlantData(
            analysis_type="MonteCarloAEP",  # Choosing a random type that doesn't fail validation
            metadata=path.parent / "plant_meta.yml",
            scada=scada_df,
            meter=meter_df,
            curtail=curtail_df,
            asset=asset_df,
            reanalysis=dict(era5=reanalysis_era5_df, merra2=reanalysis_merra2_df),
        )

        return engie_plantdata


if __name__ == "__main__":
    prepare()
