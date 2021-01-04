"""
Configuration for pytest - this file is automatically executed on startup.
"""

import os
import pathlib

import pytest


def pytest_addoption(parser):
    # Add command-line argument `sampledir`, which should point to a
    # checkout of https://github.com/ADAQ-AQI/cap-sample-data
    # By default assume it exists, with the default name, as a sibling
    # directory of this repo
    root = pathlib.Path(__file__).parent
    default = root.parent / "cap-sample-data"
    parser.addoption("--sampledir", default=default)

@pytest.fixture(scope="package")
def sampledir(pytestconfig):
    """
    Fixture to conveniently access the sample data directory.
    """
    return pathlib.Path(pytestconfig.getoption("sampledir"))
