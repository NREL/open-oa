<img src="https://github.com/NREL/OpenOA/blob/develop/Open%20OA%20Final%20Logos/Color/Open%20OA%20Color%20Transparent%20Background.png?raw=true" alt="OpenOA" width="300"/>

-----

[![Journal of Open Source Software Badge](https://joss.theoj.org/papers/d635ef3c3784d49f6e81e07a0b35ff6b/status.svg)](https://joss.theoj.org/papers/d635ef3c3784d49f6e81e07a0b35ff6b)
[![PyPI version](https://badge.fury.io/py/openoa.svg)](https://badge.fury.io/py/openoa)
[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Gitter Badge](https://badges.gitter.im/NREL_OpenOA/community.svg)](https://gitter.im/NREL_OpenOA/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Binder Badge](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NREL/OpenOA/main?filepath=examples)

[![Documentation Badge](https://readthedocs.org/projects/openoa/badge/?version=latest)](https://openoa.readthedocs.io)
[![Code Coverage Badge](https://codecov.io/gh/NREL/OpenOA/branch/develop/graph/badge.svg)](https://codecov.io/gh/NREL/OpenOA)
[![PyPI downloads](https://img.shields.io/pypi/dm/openoa)](https://pypi.org/project/WOMBAT/)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

-----

# Overview

- Jump to [installation instructions](#installation-and-usage).
- Demo the code by running the [example notebooks on Binder](https://mybinder.org/v2/gh/NREL/OpenOA/main?filepath=examples).
- Read the [documentation](https://openoa.readthedocs.io/en/latest/).
- Learn how to [contribute](contributing.md).

This library provides a framework for assessing wind plant performance using operational assessment
(OA) methodologies that consume timeseries data from wind plants. Its development has been motivated
by the Wind Plant Performance Prediction (WP3) Benchmark project, led by the National Renewable
Energy Laboratory (NREL), which focuses on quantifying and understanding differences between the
expected and actual energy production of wind plants. To support the WP3 Benchmark project, OpenOA
was initially developed to provide a baseline implementation of a long-term operational annual
energy production (AEP) estimation method. It has since grown to incorporate several more OA
analysis methods, lower-level utility functions, and a schema for time-series data from wind power
plants.

> **Warning**
OpenOA is a research software library and is released under a BSD-3 license. Please refer to the
accompanying [license file](LICENSE.txt) for the full terms. The inclusion of any algorithms and
their implementations in the code or accompanying documentation **shal not** be interpreted as an
endorsement by the authors, NREL, nor the US Government for fitness in any particular purpose or
situation. While the authors believe the software may be useful for industry practitioners, we
encourage caution, use of best practices, and engagement with trained professionals when performing
any data analysis.

### Included Analysis Methods

| Name | Description | Citations |
| --- | --- | --- |
| ``MonteCarloAEP`` | This routine estimates the long-term annual energy production (AEP) of a wind power plant (typically over 10-20 years) based on operational data from a shorter period of record (e.g., 1-3 years), along with the uncertainty. | [^2], [^3] |
| ``TurbineLongTermGrossEnergy``| This routine estimates the long-term turbine ideal energy (TIE) of a wind plant, defined as the long-term AEP that would be generated by the wind plant if all turbines operated normally (i.e., no downtime, derating, or severe underperformance, but still subject to wake losses and moderate performance losses), along with the uncertainty. | [^4] |
| ``ElectricalLosses``| The ElectricalLosses routine estimates the average electrical losses at a wind plant, along with the uncertainty, by comparing the energy produced at the wind turbines to the energy delivered to the grid. | [^4] |
| ``EYAGapAnalysis``| This class is used to perform a gap analysis between the estimated AEP from a pre-construction energy yield estimate (EYA) and the actual AEP. The gap analysis compares different wind plant performance categories to help understand the sources of differences between EYA AEP estimates and actual AEP, specifically availability losses, electrical losses, and TIE. | [^4] |
| ``WakeLosses``| This routine estimates long-term internal wake losses experienced by a wind plant and for each individual turbine, along with the uncertainty. | [^5]. Based in part on approaches in [^6], [^7], [^8] |
| ``StaticYawMisalignment``| The StaticYawMisalignment routine estimates the static yaw misalignment for individual wind turbines as a function of wind speed by comparing the estimated wind vane angle at which power is maximized to the mean wind vane angle at which the turbines operate. The routine includes uncertainty quantification. **Warning: This method has not been validated using data from wind turbines with known static yaw misalignments and the results should be treated with caution.** | Based in part on approaches in [^9], [^10], [^11], [^12], [^13] |

[^1]: Fields, M. J., Optis, M., Perr-Sauer, J., Todd, A., Lee, J. C. Y., Meissner, J., Simley, E., Bodini, N., Williams, L., Sheng, S., and Hammond, R.. Wind plant performance prediction benchmark phase 1 technical report, NREL/TP-5000-78715. Technical Report, National Renewable Energy Laboratory, Golden, CO (2021). https://doi.org/10.2172/1826665.

[^2]: Bodini, N. & Optis, M. Operational-based annual energy production uncertainty: are its components actually uncorrelated? *Wind Energy Science* 5(4):1435–1448 (2020). https://doi.org/10.5194/wes-5-1435-2020.

[^3]: Bodini, N., Optis, M., Perr-Sauer, J., Simley, E., and Fields, M. J. Lowering post-construction yield assessment uncertainty through better wind plant power curves. *Wind Energy*, 25(1):5–22 (2022). https://doi.org/10.1002/we.2645.

[^4]: Todd, A. C., Optis, M., Bodini, N., Fields, M. J., Lee, J. C. Y., Simley, E., and Hammond, R. An independent analysis of bias sources and variability in wind plant pre‐construction energy yield estimation methods. *Wind Energy*, 25(10):1775-1790 (2022). https://doi.org/10.1002/we.2768.

[^5]: Simley, E., Fields, M. J., Perr-Sauer, J., Hammond, R., and Bodini, N. A Comparison of Preconstruction and Operational Wake Loss Estimates for Land-Based Wind Plants. Presented at the NAWEA/WindTech 2022 Conference, Newark, DE, September 20-22 (2022). https://www.nrel.gov/docs/fy23osti/83874.pdf.

[^6]: Barthelmie, R. J. and Jensen, L. E. Evaluation of wind farm efficiency and wind turbine wakes at the Nysted offshore wind farm, *Wind Energy* 13(6):573–586 (2010). https://doi.org/10.1002/we.408.

[^7]: Nygaard, N. G. Systematic quantification of wake model uncertainty. Proc. EWEA Offshore, Copenhagen, Denmark, March 10-12 (2015).

[^8]: Walker, K., Adams, N., Gribben, B., Gellatly, B., Nygaard, N. G., Henderson, A., Marchante Jimémez, M., Schmidt, S. R., Rodriguez Ruiz, J., Paredes, D., Harrington, G., Connell, N., Peronne, O., Cordoba, M., Housley, P., Cussons, R., Håkansson, M., Knauer, A., and Maguire, E.: An evaluation of the predictive accuracy of wake effects models for offshore wind farms. *Wind Energy* 19(5):979–996 (2016). https://doi.org/10.1002/we.1871.

[^9]: Bao, Y., Yang, Q., Fu, L., Chen, Q., Cheng, C., and Sun, Y. Identification of Yaw Error Inherent Misalignment for Wind Turbine Based on SCADA Data: A Data Mining Approach. Proc. 12th Asian Control Conference (ASCC), Kitakyushu, Japan, June 9-12 (2019). 1095-1100.

[^10]: Xue, J. and Wang, L. Online data-driven approach of yaw error estimation and correction of horizontal axis wind turbine. *IET J. Eng.* 2019(18):4937–4940 (2019). https://doi.org/10.1049/joe.2018.9293.

[^11]: Astolfi, D., Castellani, F., and Terzi, L. An Operation Data-Based Method for the Diagnosis of Zero-Point Shift of Wind Turbines Yaw Angle. *J. Solar Energy Engineering* 142(2):024501 (2020). https://doi.org/10.1115/1.4045081.

[^12]: Jing, B., Qian, Z., Pei, Y., Zhang, L., and Yang, T. Improving wind turbine efficiency through detection and calibration of yaw misalignment. *Renewable Energy* 160:1217-1227 (2020). https://doi.org/10.1016/j.renene.2020.07.063.

[^13]: Gao, L. and Hong, J. Data-driven yaw misalignment correction for utility-scale wind turbines. *J. Renewable Sustainable Energy* 13(6):063302 (2021). https://doi.org/10.1063/5.0056671.

### PlantData Schema

OpenOA contains a  `PlantData` class, which is based on Pandas data frames and provides a standardized base schema to combine raw data from wind turbines, meteorological (met) towers, revenue meters, and reanalysis products, such as MERRA-2 or ERA5. Additionally, the `PlantData` class can perform some basic validation for the data required to perform the operational analyses.

### Utility Functions

Lower-level utility modules are provided in the utils subpackage.
They can also be used individually to support general wind plant data analysis activities.
Some examples of utils modules include:

- **Quality Assurance**: This module provides quality assurance methods for identifying potential
  quality issues with SCADA data prior to importing it into a `PlantData` object.
- **Filters**: This module provides functions for flagging operational data based on a range of
  criteria (e.g., outlier detection).
- **Power Curve**: The power curve module contains methods for fitting power curve models to SCADA data.
- **Imputing**: This module provides methods for filling in missing data with imputed values.
- **Met Data Processing**: This module contains methods for processing meteorological data, such as
  computing air density and wind shear coefficients.
- **Plotting**: This module contains convenient functions for creating plots, such as power curve
  plots and maps showing the wind plant layout.

For further infromation about the features and citations, please see the [OpenOA documentation website](https://openoa.readthedocs.io/en/latest/).

## How to cite OpenOA

**To cite analysis methods or individual features:** Please cite the original authors of these methods, as noted in the [documentation](#included-analysis-methods) and inline comments.

**To cite the open-source software framework as a whole, or the OpenOA open source development effort more broadly,** please use the following citation:

```bibtex
   @article{Perr-Sauer2021,
      doi = {10.21105/joss.02171},
      url = {https://doi.org/10.21105/joss.02171},
      year = {2021},
      publisher = {The Open Journal},
      volume = {6},
      number = {58},
      pages = {2171},
      author = {Jordan Perr-Sauer and Mike Optis and Jason M. Fields and Nicola Bodini and Joseph C.Y. Lee and Austin Todd and Eric Simley and Robert Hammond and Caleb Phillips and Monte Lunacek and Travis Kemper and Lindy Williams and Anna Craig and Nathan Agarwal and Shawn Sheng and John Meissner},
      title = {OpenOA: An Open-Source Codebase For Operational Analysis of Wind Farms},
      journal = {Journal of Open Source Software}
   }
```

# Installation and Usage

### Requirements

- Python 3.8-3.11 with pip.

We strongly recommend using the Anaconda Python distribution and creating a new conda environment for OpenOA. You can download Anaconda through [their website.](https://www.anaconda.com/products/individual)

After installing Anaconda, create and activate a new conda environment with the name "openoa-env":

```bash
conda create --name openoa-env python=3.10
conda activate openoa-env
```

### Installation

Clone the repository and install the library and its dependencies using pip:

```bash
git clone https://github.com/NREL/OpenOA.git
cd OpenOA
pip install .
```

You should now be able to import openoa from the Python interpreter:

```bash
python
>>> import openoa
>>> openoa.__version__
```

#### Installation Options

There are a number of installation options that can be used, depending on the use case, which can be
installed with the following pattern `pip install "openoa[opt1,opt2]"` (`pip install .[opt1,opt2]` is also allowed).

- `develop`: for linting, automated formatting, and testing
- `docs`: for building the documentation
- `examples`: for the full Jupyter Lab suite (also contains `reanalysis` and `nrel-wind`)
- `renalysis`: for accessing and processing MERRA2 and ERA5 data
- `nrel-wind`: for accessing the NREL WIND Toolkit
- `all`: for the complete dependency stack

> **Important**
> If using Python 3.11, install `openoa` only, then reinstall adding the modifiers to reduce
> the amount of time it takes for pip to resolve the dependency stack.

#### Common Installation Issues

- In Windows you may get an error regarding geos_c.dll. To fix this install Shapely using:

```bash
conda install Shapely
```

- In Windows, an ImportError regarding win32api can also occur. This can be resolved by fixing the version of pywin32 as follows:

```bash
pip install --upgrade pywin32==255
```

#### Example Notebooks and Data

Be sure to install OpenOA using the `examples` modifier from [above](#installation-options). Such as: `pip install ".[examples]"`

The example data will be automaticaly extracted as needed by the tests. To manually extract the example data for use with the example notebooks, use the following command:

```bash
unzip examples/data/la_haute_borne.zip -d examples/data/la_haute_borne/
```

The example notebooks are located in the `examples` directory. We suggest installing the Jupyter notebook server to run the notebooks interactively. The notebooks can also be viewed statically on [Read The Docs](http://openoa.readthedocs.io/en/latest/examples).

```bash
jupyter lab  # "jupyter notebook" is also ok if that's your preference
```

Open the URL printed to your command prompt in your favorite browser. Once jupyter is open, navigate to the "examples" directory in the file explorer and open an example notebook.

### Development

Please see the developer section of the contributing guide [here](contributing.md), or on the [documentation site](https://openoa.readthedocs.io/en/latest/getting_started/contributing.html) for complete details.

Development dependencies are provided through the develop extra flag in setup.py. Here, we install
OpenOA, with development dependencies, in editable mode, and activate the pre-commit workflow (note:
this second step must be done before committing any changes):

```bash
cd OpenOA
pip install -e ".[develop, docs, examples]"
pre-commit install
```

Occasionally, you will need to update the dependencies in the pre-commit workflow, which will provide an error when this needs to happen. When it does, this can normally be resolved with the below code, after which you can continue with your normal git workflow:

```bash
pre-commit autoupdate
git add .pre-commit-config.yaml
```

#### Testing
Tests are written in the Python unittest or pytest framework and are runnable using pytest. There
are two types of tests, unit tests (located in `test/unit`) run quickly and are automatically for
every pull request to the OpenOA repository. Regression tests (located at `test/regression`) provide
a comprehensive suite of scientific tests that may take a long time to run (up to 20 minutes on our
machines). These tests should be run locally before submitting a pull request, and are run weekly on
the develop and main branches.

To run all unit and regresison tests:

```bash
pytest
```

To run unit tests only:

```bash
pytest --unit
```

To run all tests and generate a code coverage report

```bash
pytest --cov=openoa
```

#### Documentation

Documentation is automatically built by, and visible through
[Read The Docs](http://openoa.readthedocs.io/).

You can build the documentation with [sphinx](http://www.sphinx-doc.org/en/stable/), but will need
to ensure [Pandoc is installed](https://pandoc.org/installing.html) on your computer first.

```bash
cd OpenOA
pip install -e ".[docs]"
cd sphinx
make html
```

### Contributors
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

[![All Contributors](https://img.shields.io/github/all-contributors/NREL/OpenOA?color=ee8449&style=flat-square)](#contributors)

### References
