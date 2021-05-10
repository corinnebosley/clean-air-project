import os
from setuptools import setup


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_NAME = "clean_air"


setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=[PACKAGE_NAME],
    install_requires=[
        "scitools-iris",
        "xarray",
        "pandas",
        "geopandas",
        "hvplot",
        "holoviews",
        "geoviews",
        "datashader",
    ],
    extras_require={
        "dev": ["pytest", "flake8"],
    },
)
