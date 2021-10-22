"""Unit tests for functions in file_converter.py"""

import os

import pytest
import pandas as pd
import json
import yaml
import csv
import datetime as dt

from clean_air.util import file_converter as fc


@pytest.fixture()
def excel_filepath(sampledir):
    filepath = os.path.join(sampledir, "test_data",
                            "metadata_form_responses.xlsx")
    return filepath


@pytest.fixture
def netcdf_filepath(sampledir):
    netcdf_filepath = os.path.join(sampledir, "aircraft",
                                   "MOCCA_M251_20190903.nc")
    return netcdf_filepath


@pytest.fixture
def csv_filepath(sampledir):
    csv_filepath = os.path.join(sampledir, "obs", "ABD_2015.csv")
    return csv_filepath


@pytest.fixture()
def tmp_output_path(tmp_path):
    tmp_output_path = tmp_path / "tmp_output_path"
    tmp_output_path.mkdir()
    return tmp_output_path


@pytest.fixture()
def saved_json(excel_filepath, tmp_output_path):
    json_fname = tmp_output_path / "form_response0.json"
    fc.convert_excel(excel_filepath, json_fname)
    saved_json = json.load(json_fname.open())
    return saved_json


@pytest.fixture()
def saved_yaml(excel_filepath, tmp_output_path):
    yaml_fname = tmp_output_path / "form_response0.yaml"
    fc.convert_excel(excel_filepath, yaml_fname)
    saved_yaml = yaml.safe_load(yaml_fname.open())
    return saved_yaml


def test_read_excel_data(excel_filepath):
    """Test that excel files are read and converted successfully to
    temporary dataframe objects"""
    temp_df = fc.generate_dataframe(filepath=excel_filepath)
    assert isinstance(temp_df, pd.DataFrame)


def test_read_netcdf_data(netcdf_filepath):
    """
    Test that netcdf files are read and converted successfully into
    temporary dataframe objects.
    """
    temp_df = fc.generate_dataframe(filepath=netcdf_filepath)
    assert isinstance(temp_df, pd.DataFrame)


def test_bad_input_data(csv_filepath):
    with pytest.raises(Exception):
        fc.generate_dataframe(filepath=csv_filepath)


def test_slice_data(excel_filepath):
    """Test that data from temporary dataframes (read from excel files) are
    split into single dataframes for each row of data.  Test excel file has
    three rows, so should be split into three separate files here."""
    # First, read and slice the test file:
    temp_df = fc.generate_dataframe(filepath=excel_filepath)
    sliced_data = fc.slice_data(temp_df)
    # Now check that three separate files have been generated:
    assert len(sliced_data) == 3


def test_json_reformat_chemicals(saved_json):
    """Test that the single excel entry for each chemical is reformatted
    into three seperate lines representing 'name', 'shortname' and
    'chart' information."""
    for chem in range(len(saved_json["pollutants"])):
        assert saved_json["pollutants"][chem]["name"] and \
               saved_json["pollutants"][chem]["shortname"] and \
               saved_json["pollutants"][chem]["chart"]


def test_json_file_structure(saved_json):
    """Test that new_file has index names; 'pollutants', environmentType'
    and 'dateRange'."""
    keys_required = ['pollutants', 'environmentType', 'dateRange']
    for key in keys_required:
        assert key in saved_json


def test_json_date_range(saved_json):
    """Test that item in new_file contains both start and end dates."""
    assert saved_json["dateRange"]["startDate"] and \
        saved_json["dateRange"]["endDate"]


def test_json_date_format(saved_json):
    """Test that saved json file contains dates in isoformat."""
    assert dt.datetime.fromisoformat(saved_json["dateRange"]["startDate"])
    assert dt.datetime.fromisoformat(saved_json["dateRange"]["endDate"])


def test_yaml_reformat_chemicals(saved_yaml):
    """Test that all chemical entries are reformatted to contain their
    shortname only (i.e. 'PM10' as opposed to
    'Course Particulate Matter (PM10)')."""
    for entry in saved_yaml['chemical species']:
        assert len(entry) <= 7


def test_yaml_file_structure(saved_yaml):
    """Test that yaml file structure contains all keys required for yaml
    output."""
    keys_required = ['title', 'description', 'authors', 'bbox',
                     'chemical species', 'observation level/model',
                     'data source', 'time range', 'lineage', 'quality', 'docs']
    for key in keys_required:
        assert key in saved_yaml


def test_yaml_authors_subset(saved_yaml):
    """Test that all required keys are present in authors subset."""
    keys_required = ['firstname', 'surname']
    for key in keys_required:
        assert key in saved_yaml['authors'][0]


def test_yaml_bbox_subset(saved_yaml):
    """Test that all required keys are present in bbox subset."""
    keys_required = ['north', 'south', 'east', 'west']
    for key in keys_required:
        assert key in saved_yaml['bbox']


def test_yaml_timerange_subset(saved_yaml):
    """Test that all required keys are present in time range subset."""
    keys_required = ['start', 'end']
    for key in keys_required:
        assert key in saved_yaml['time range']


def test_yaml_remove_nan_names(saved_yaml):
    """Test that all names (of users), if NAN values, are removed from yaml
    output (including keys)."""
    # Note: This test works specifically with this test file as the second
    # set of names in the file are nans.
    assert len(saved_yaml['authors']) == 1


def test_yaml_datetime_format(saved_yaml):
    """Test that saved yaml file contains dates in isoformat."""
    assert dt.datetime.fromisoformat(saved_yaml["time range"]["start"])
    assert dt.datetime.fromisoformat(saved_yaml["time range"]["end"])


def test_bad_output_type(excel_filepath, csv_filepath):
    """Test that an exception is raised when an invalid filetype is
    specified (or not specified at all)."""
    with pytest.raises(ValueError):
        fc.convert_excel(excel_filepath, csv_filepath)


def test_csv_no_index(tmp_output_path, netcdf_filepath):
    """Test that indexes have not been added to the converted csv file."""
    # NOTE: Due to the behaviour of the csv reader, this file can only be
    # examined within the condition 'with open...', so more set-up tasks must
    # be performed here as opposed to inside a fixture.
    csv_fname = tmp_output_path / "flightpath.csv"
    fc.convert_netcdf(netcdf_filepath, csv_fname)
    with open(csv_fname, newline='') as csvfile:
        saved_csv = csv.reader(csvfile)
        for n, row in enumerate(saved_csv):
            if n == 0:
                # First line of csv is headers, no check required here.
                pass
            else:
                assert dt.datetime.fromisoformat(row[0])

