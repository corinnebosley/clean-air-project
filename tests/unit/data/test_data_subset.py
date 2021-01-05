import os

import pytest
import numpy as np
import iris
import shapely, shapely.geometry

from clean_air.data import DataSubset
from clean_air import util


def test_point_subset(sampledir):
    # Create example dataset
    ds = DataSubset(
        None,
        "aqum",
        os.path.join(sampledir, "model_full", "aqum_daily*"),
        point=(100, 200),
    )
    cube = ds.as_cube()

    xcoord, ycoord = util.cubes.get_xy_coords(cube)

    # Check we have the point we asked for
    assert iris.util.array_equal(xcoord.points, [100])
    assert iris.util.array_equal(ycoord.points, [200])


def test_box_subset(sampledir):
    # Create example dataset
    ds = DataSubset(
        None,
        "aqum",
        os.path.join(sampledir, "model_full", "aqum_daily*"),
        box=(-1000, -2000, 3000, 4000),
    )
    cube = ds.as_cube()

    xcoord, ycoord = util.cubes.get_xy_coords(cube)

    # Check we have the points we asked for (multiples of 2000m within
    # each range)
    assert iris.util.array_equal(xcoord.points, [0, 2000])
    assert iris.util.array_equal(ycoord.points, [-2000, 0, 2000, 4000])


class TestPolygonSubset:
    @staticmethod
    @pytest.fixture(scope="class")
    def polygon_cube(sampledir):
        # Define a test polygon (an extremely simple representation of Exeter)
        shape = shapely.geometry.Polygon([
            (289271.9, 93197.0),
            (289351.3, 95110.1),
            (293405.1, 96855.0),
            (296721.1, 94960.3),
            (297165.1, 86966.9),
            (294181.6, 89357.2),
            (291388.0, 89272.6),
        ])

        # Create example dataset
        ds = DataSubset(
            None,
            "aqum",
            os.path.join(sampledir, "model_full", "aqum_hourly_o3_20200520.nc"),
            shape=shape,
        )
        return ds.as_cube()

    def test_subset_mask(self, polygon_cube):
        # Define corresponding mask (note: this "looks" upside down compared
        # to how it would be plotted)
        expected_mask = np.array(
            [[1, 1, 1, 1, 0],
             [1, 1, 0, 0, 0],
             [0, 0, 0, 0, 0],
             [0, 0, 0, 0, 1],
             [0, 0, 0, 0, 1],
             [0, 0, 0, 0, 1]]
        )

        # Check we have the right mask (on a 2d slice of this 3d cube)
        subcube = next(polygon_cube.slices_over("time"))
        assert iris.util.array_equal(subcube.data.mask, expected_mask)

    def test_subset_data(self, polygon_cube):
        # Simple data check, which, as the mask is taken into account, should
        # be a pretty reliable test
        assert round(polygon_cube.data.mean(), 8) == 57.66388811
