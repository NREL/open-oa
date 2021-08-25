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
import os
from zipfile import ZipFile

import numpy as np
import pandas as pd

import operational_analysis.toolkits.timeseries as ts
import operational_analysis.toolkits.unit_conversion as un
import operational_analysis.toolkits.met_data_processing as met
from operational_analysis import logging, logged_method_call
from operational_analysis.types import PlantData
from operational_analysis.toolkits import filters


logger = logging.getLogger(__name__)


class Project_Engie(PlantData):
    """This class loads data for the ENGIE La Haute Borne site into a PlantData
    object"""

    def __init__(
        self,
        path="data/la_haute_borne",
        name="Engie",
        engine="pandas",
        toolkit=["pruf_plant_analysis"],
    ):

        super(Project_Engie, self).__init__(path, name, engine, toolkit)

    def extract_data(self):
        """
        Extract data from zip files if they don't already exist.
        """
        if not os.path.exists(self._path):
            with ZipFile(self._path + ".zip") as zipfile:
                zipfile.extractall(self._path)

    def prepare(self):
        """
        Do all loading and preparation of the data for this plant.
        """

        # Extract data if necessary
        self.extract_data()

        # Set time frequencies of data in minutes
        self._meter_freq = "10T"  # Daily meter data
        self._curtail_freq = "10T"  # Daily curtailment data
        self._scada_freq = "10T"  # 10-min

        # Load meta data
        self._lat_lon = (48.452, 5.588)
        self._plant_capacity = 8.2  # MW
        self._num_turbines = 4
        self._turbine_capacity = 2.05  # MW

        ###################
        # SCADA DATA #
        ###################
        logger.info("Loading SCADA data")
        self._scada.load(self._path, "la-haute-borne-data-2014-2015", "csv")  # Load Scada data
        logger.info("SCADA data loaded")

        logger.info("Timestamp QC and conversion to UTC")
        # Get 'time' field in datetime format. Local time zone information is
        # encoded, so convert to UTC

        self._scada.df["time"] = pd.to_datetime(
            self._scada.df["Date_time"], utc=True
        ).dt.tz_localize(None)

        # Remove duplicated timestamps and turbine id
        self._scada.df = self._scada.df.drop_duplicates(
            subset=["time", "Wind_turbine_name"], keep="first"
        )

        # Set time as index
        self._scada.df.set_index("time", inplace=True, drop=False)

        logger.info("Correcting for out of range of temperature variables")
        # Handle extrema values for temperature. All other variables appear to
        # be reasonable.
        self._scada.df = self._scada.df[
            (self._scada.df["Ot_avg"] >= -15.0) & (self._scada.df["Ot_avg"] <= 45.0)
        ]

        logger.info("Flagging unresponsive sensors")
        # Due to data discretization, there appear to be a lot of repeating
        # values. But these filters seem to catch the obvious unresponsive
        # sensors.
        for id in self._scada.df.Wind_turbine_name.unique():
            temp_flag = filters.unresponsive_flag(
                self._scada.df.loc[self._scada.df.Wind_turbine_name == id, "Va_avg"], 3
            )
            self._scada.df.loc[
                (self._scada.df.Wind_turbine_name == id) & (temp_flag),
                ["Ba_avg", "P_avg", "Ws_avg", "Va_avg", "Ot_avg", "Ya_avg", "Wa_avg"],
            ] = np.nan
            temp_flag = filters.unresponsive_flag(
                self._scada.df.loc[self._scada.df.Wind_turbine_name == id, "Ot_avg"], 20
            )
            self._scada.df.loc[
                (self._scada.df.Wind_turbine_name == id) & (temp_flag), "Ot_avg"
            ] = np.nan

        # Put power in watts
        self._scada.df["Power_W"] = self._scada.df["P_avg"] * 1000

        # Convert pitch to range -180 to 180.
        self._scada.df["Ba_avg"] = self._scada.df["Ba_avg"] % 360
        self._scada.df.loc[self._scada.df["Ba_avg"] > 180.0, "Ba_avg"] = (
            self._scada.df.loc[self._scada.df["Ba_avg"] > 180.0, "Ba_avg"] - 360.0
        )

        # Calculate energy
        self._scada.df["energy_kwh"] = (
            un.convert_power_to_energy(self._scada.df["Power_W"], self._scada_freq) / 1000
        )

        logger.info("Converting field names to IEC 61400-25 standard")
        # Map to -25 standards

        # Note: there is no vane direction variable defined in -25, so
        # making one up
        scada_map = {
            "time": "time",
            "Wind_turbine_name": "id",
            "Power_W": "wtur_W_avg",
            "Ws_avg": "wmet_wdspd_avg",
            "Wa_avg": "wmet_HorWdDir_avg",
            "Va_avg": "wmet_VaneDir_avg",
            "Ya_avg": "wyaw_YwAng_avg",
            "Ot_avg": "wmet_EnvTmp_avg",
            "Ba_avg": "wrot_BlPthAngVal1_avg",
        }

        self._scada.df.rename(scada_map, axis="columns", inplace=True)

        # Remove the fields we are not yet interested in
        self._scada.df.drop(["Date_time", "time", "P_avg"], axis=1, inplace=True)

        ##############
        # METER DATA #
        ##############
        self._meter.load(self._path, "plant_data", "csv")  # Load Meter data

        # Create datetime field
        self._meter.df["time"] = pd.to_datetime(self._meter.df.time_utc).dt.tz_localize(None)
        self._meter.df.set_index("time", inplace=True, drop=False)

        # Drop the fields we don't need
        self._meter.df.drop(
            ["time_utc", "availability_kwh", "curtailment_kwh"], axis=1, inplace=True
        )

        self._meter.df.rename(columns={"net_energy_kwh": "energy_kwh"}, inplace=True)

        #####################################
        # Availability and Curtailment Data #
        #####################################
        self._curtail.load(self._path, "plant_data", "csv")  # Load Meter data

        # Create datetime field
        self._curtail.df["time"] = pd.to_datetime(self._curtail.df.time_utc).dt.tz_localize(None)
        self._curtail.df.set_index("time", inplace=True, drop=False)

        # Already have availability and curtailment in kwh, so not much to do.

        # Drop the fields we don't need
        self._curtail.df.drop(["time_utc", "net_energy_kwh"], axis=1, inplace=True)

        ###################
        # REANALYSIS DATA #
        ###################

        # Note that as an alternatvie to loading the existing csv files containing reanalysis data,
        # the data can be downloaded through the PlanetOS API using the
        # toolkits.reanalysis_downloading module with the "planetos" option:
        #
        # project._reanalysis.load(project._path,
        #                          project._name,
        #                          "planetos",
        #                          lat=project._lat_lon[0],
        #                          lon=project._lat_lon[1]
        #                          )
        #
        # However, wind direction and air density will still need to be calculated from the wind
        # speed, temperature, and surface pessure variables.

        # merra2
        self._reanalysis._product["merra2"].load(self._path, "merra2_la_haute_borne", "csv")

        # calculate wind direction from u, v
        self._reanalysis._product["merra2"].df["winddirection_deg"] = met.compute_wind_direction(
            self._reanalysis._product["merra2"].df["u_50"],
            self._reanalysis._product["merra2"].df["v_50"],
        )

        self._reanalysis._product["merra2"].rename_columns(
            {
                "time": "datetime",
                "windspeed_ms": "ws_50m",
                "u_ms": "u_50",
                "v_ms": "v_50",
                "temperature_K": "temp_2m",
                "rho_kgm-3": "dens_50m",
            }
        )
        self._reanalysis._product["merra2"].normalize_time_to_datetime("%Y-%m-%d %H:%M:%S")
        self._reanalysis._product["merra2"].df.set_index("time", inplace=True, drop=False)

        # Drop the fields we don't need
        self._reanalysis._product["merra2"].df.drop(
            ["Unnamed: 0", "datetime"], axis=1, inplace=True
        )

        # era5
        self._reanalysis._product["era5"].load(self._path, "era5_wind_la_haute_borne", "csv")

        # calculate wind direction from u, v
        self._reanalysis._product["era5"].df["winddirection_deg"] = met.compute_wind_direction(
            self._reanalysis._product["era5"].df["u_100"],
            self._reanalysis._product["era5"].df["v_100"],
        )

        self._reanalysis._product["era5"].rename_columns(
            {
                "time": "datetime",
                "windspeed_ms": "ws_100m",
                "u_ms": "u_100",
                "v_ms": "v_100",
                "temperature_K": "t_2m",
                "rho_kgm-3": "dens_100m",
            }
        )
        self._reanalysis._product["era5"].normalize_time_to_datetime("%Y-%m-%d %H:%M:%S")
        self._reanalysis._product["era5"].df.set_index("time", inplace=True, drop=False)

        # Drop the fields we don't need
        self._reanalysis._product["era5"].df.drop(["Unnamed: 0", "datetime"], axis=1, inplace=True)

        ##############
        # ASSET DATA #
        ##############
        self._asset.load(self._path, "la-haute-borne_asset_table", "csv")
        self._asset.rename_columns(
            {
                "id": "Wind_turbine_name",
                "latitude": "Latitude",
                "longitude": "Longitude",
                "rated_power_kw": "Rated_power",
                "hub_height_m": "Hub_height_m",
                "rotor_diameter_m": "Rotor_diameter_m",
            }
        )

        # Assign type to turbine for all assets
        self._asset._asset["type"] = "turbine"

        # Drop renamed fields
        self._asset._asset.drop(
            [
                "Wind_turbine_name",
                "Latitude",
                "Longitude",
                "Rated_power",
                "Hub_height_m",
                "Rotor_diameter_m",
            ],
            axis=1,
            inplace=True,
        )
