#!/usr/bin/env python
import io
import re
from pathlib import Path

from setuptools import setup, find_packages


# Configs ##########

# Core dependencies
REQUIRED = [
    "scikit-learn>=1.0",
    "requests>=2.21.0",
    "eia-python>=1.22",
    "pyproj>=3.5",
    "shapely>=1.8",
    "numpy>=1.24",
    "pandas>=2.2",
    "pygam>=0.9.0",
    "scipy>=1.7",
    "statsmodels>=0.11; python_version<'3.11'",
    "statsmodels>=0.13.3; python_version=='3.11'",
    "tqdm>=4.28.1",
    "matplotlib>=3.6",
    "bokeh>=3.3",
    "attrs>=22.2",
    "pytz",
    "pyyaml",
    "tabulate",
    "ipython",
]

# Testing-only dependencies
TESTS = ["pytest>=5.4.2", "pytest-cov>=2.8.1"]

# All extra dependencies (see keys for breakdown by purpose)
EXTRAS = {
    "docs": [
        "Sphinx>=5.0,!=7.2.0",
        "pydata-sphinx-theme",
        "sphinx_design>=0.3",
        "sphinxcontrib-bibtex",
        "myst-nb",
        "myst-parser",
    ],
    "develop": [
        "pre-commit",
        "black",
        "isort",
        "flake8",
        "flake8-docstrings",
        "pyupgrade",
    ],
    "examples": [
        "jupyterlab",
    ],
    "nrel-wind": ["h5pyd"],
    "reanalysis": [
        "cdsapi",
        "xarray[parallel]",  # Dask required for loading data
        "h5py",  # Required for netcdf4
        "netcdf4",
    ],
}
EXTRAS["develop"] += TESTS
EXTRAS["examples"] += EXTRAS["reanalysis"] + EXTRAS["nrel-wind"]
EXTRAS["all"] = EXTRAS["develop"] + EXTRAS["docs"] + EXTRAS["examples"]


# Read the version from the __init__.py file without importing it
def read(*names, **kwargs):
    directory = Path(__file__).resolve().parent
    with open(Path(directory, *names), encoding=kwargs.get("encoding", "utf8")) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def read_file(filename):
    this_directory = Path(__file__).resolve().parent
    with open(this_directory / filename, encoding="utf-8") as f:
        f_text = f.read()
    return f_text


# setup.py main ##########

setup(
    name="OpenOA",
    version=find_version("openoa", "__init__.py"),
    description="A package for collecting and assigning wind turbine metrics",
    long_description=read_file("readme.md"),
    long_description_content_type="text/markdown",
    author="NREL PRUF OA Team",
    author_email="openoa@nrel.gov",
    url="https://github.com/NREL/OpenOA",
    packages=find_packages(exclude=["test", "examples"]),
    include_package_data=True,
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    python_requires=">=3.8, <3.12",
)
