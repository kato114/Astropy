# Licensed under a 3-clause BSD style license - see LICENSE.rst

# TEST_UNICODE_LITERALS
import numpy as np

from ... import units as u
from .. import Longitude, Latitude, EarthLocation
# test on frame with most complicated frame attributes.
from ..builtin_frames import ICRS, AltAz
from ...time import Time
from ...utils.compat.numpycompat import NUMPY_LT_1_9


class TestManipulation():
    """Manipulation of Frame shapes.

    Checking that attributes are manipulated correctly.

    Even more exhaustive tests are done in time.tests.test_methods
    """

    def setup(self):
        lon = Longitude(np.arange(0, 24, 4), u.hourangle)
        lat = Latitude(np.arange(-90, 91, 30), u.deg)
        # With same-sized arrays, no attributes
        self.s0 = ICRS(lon[:, np.newaxis] * np.ones(lat.shape),
                       lat * np.ones(lon.shape)[:, np.newaxis])
        self.obstime = Time('2012-01-01')
        self.location = EarthLocation(20.*u.deg, lat, 100*u.m)
        self.pressure = 1000 * u.hPa
        self.temperature = np.random.uniform(
            0., 20., size=(lon.size, lat.size)) * u.deg_C
        self.s1 = AltAz(az=lon[:, np.newaxis], alt=lat,
                        obstime=self.obstime,
                        location=self.location,
                        pressure=self.pressure,
                        temperature=self.temperature)


    def test_ravel(self):
        s0_ravel = self.s0.ravel()
        assert s0_ravel.shape == (self.s0.size,)
        assert np.all(s0_ravel.data.lon == self.s0.data.lon.ravel())
        assert np.may_share_memory(s0_ravel.data.lon, self.s0.data.lon)
        assert np.may_share_memory(s0_ravel.data.lat, self.s0.data.lat)
        # Since s1 lon, lat were broadcast, ravel needs to make a copy.
        s1_ravel = self.s1.ravel()
        assert s1_ravel.shape == (self.s1.size,)
        assert np.all(s1_ravel.data.lon == self.s1.data.lon.ravel())
        assert not np.may_share_memory(s1_ravel.data.lat, self.s1.data.lat)
        assert s1_ravel.obstime == self.s1.obstime
        assert np.all(s1_ravel.location == self.s1.location.ravel())
        assert not np.may_share_memory(s1_ravel.location, self.s1.location)
        assert np.all(s1_ravel.temperature == self.s1.temperature.ravel())
        assert np.may_share_memory(s1_ravel.temperature, self.s1.temperature)
        assert s1_ravel.pressure == self.s1.pressure

    def test_flatten(self):
        s0_flatten = self.s0.flatten()
        assert s0_flatten.shape == (self.s0.size,)
        assert np.all(s0_flatten.data.lon == self.s0.data.lon.flatten())
        # Flatten always copies.
        assert not np.may_share_memory(s0_flatten.data.lat, self.s0.data.lat)
        s1_flatten = self.s1.flatten()
        assert s1_flatten.shape == (self.s1.size,)
        assert np.all(s1_flatten.data.lat == self.s1.data.lat.flatten())
        assert not np.may_share_memory(s1_flatten.data.lon, self.s1.data.lat)
        assert s1_flatten.obstime == self.s1.obstime
        assert np.all(s1_flatten.location == self.s1.location.flatten())
        assert not np.may_share_memory(s1_flatten.location, self.s1.location)
        assert np.all(s1_flatten.temperature == self.s1.temperature.flatten())
        assert not np.may_share_memory(s1_flatten.temperature,
                                       self.s1.temperature)
        assert s1_flatten.pressure == self.s1.pressure

    def test_transpose(self):
        s0_transpose = self.s0.transpose()
        assert s0_transpose.shape == (7, 6)
        assert np.all(s0_transpose.data.lon == self.s0.data.lon.transpose())
        assert np.may_share_memory(s0_transpose.data.lat, self.s0.data.lat)
        s1_transpose = self.s1.transpose()
        assert s1_transpose.shape == (7, 6)
        assert np.all(s1_transpose.data.lat == self.s1.data.lat.transpose())
        assert np.may_share_memory(s1_transpose.data.lon, self.s1.data.lon)
        assert s1_transpose.obstime == self.s1.obstime
        assert np.all(s1_transpose.location == self.s1.location.transpose())
        assert np.may_share_memory(s1_transpose.location, self.s1.location)
        assert np.all(s1_transpose.temperature ==
                      self.s1.temperature.transpose())
        assert np.may_share_memory(s1_transpose.temperature,
                                   self.s1.temperature)
        assert s1_transpose.pressure == self.s1.pressure
        # Only one check on T, since it just calls transpose anyway.
        s1_T = self.s1.T
        assert s1_T.shape == (7, 6)
        assert np.all(s1_T.temperature == self.s1.temperature.T)
        assert np.may_share_memory(s1_T.location, self.s1.location)

    def test_diagonal(self):
        s0_diagonal = self.s0.diagonal()
        assert s0_diagonal.shape == (6,)
        assert np.all(s0_diagonal.data.lat == self.s0.data.lat.diagonal())
        if not NUMPY_LT_1_9:
            assert np.may_share_memory(s0_diagonal.data.lat, self.s0.data.lat)

    def test_swapaxes(self):
        s1_swapaxes = self.s1.swapaxes(0, 1)
        assert s1_swapaxes.shape == (7, 6)
        assert np.all(s1_swapaxes.data.lat == self.s1.data.lat.swapaxes(0, 1))
        assert np.may_share_memory(s1_swapaxes.data.lat, self.s1.data.lat)
        assert s1_swapaxes.obstime == self.s1.obstime
        assert np.all(s1_swapaxes.location == self.s1.location.swapaxes(0, 1))
        assert s1_swapaxes.location.shape == (7, 6)
        assert np.may_share_memory(s1_swapaxes.location, self.s1.location)
        assert np.all(s1_swapaxes.temperature ==
                      self.s1.temperature.swapaxes(0, 1))
        assert np.may_share_memory(s1_swapaxes.temperature,
                                   self.s1.temperature)
        assert s1_swapaxes.pressure == self.s1.pressure

    def test_reshape(self):
        s0_reshape = self.s0.reshape(2, 3, 7)
        assert s0_reshape.shape == (2, 3, 7)
        assert np.all(s0_reshape.data.lon == self.s0.data.lon.reshape(2, 3, 7))
        assert np.all(s0_reshape.data.lat == self.s0.data.lat.reshape(2, 3, 7))
        assert np.may_share_memory(s0_reshape.data.lon, self.s0.data.lon)
        assert np.may_share_memory(s0_reshape.data.lat, self.s0.data.lat)
        s1_reshape = self.s1.reshape(3, 2, 7)
        assert s1_reshape.shape == (3, 2, 7)
        assert np.all(s1_reshape.data.lat == self.s1.data.lat.reshape(3, 2, 7))
        assert np.may_share_memory(s1_reshape.data.lat, self.s1.data.lat)
        assert s1_reshape.obstime == self.s1.obstime
        assert np.all(s1_reshape.location == self.s1.location.reshape(3, 2, 7))
        assert np.may_share_memory(s1_reshape.location, self.s1.location)
        assert np.all(s1_reshape.temperature ==
                      self.s1.temperature.reshape(3, 2, 7))
        assert np.may_share_memory(s1_reshape.temperature,
                                   self.s1.temperature)
        assert s1_reshape.pressure == self.s1.pressure
        # For reshape(3, 14), copying is necessary for lon, lat, location
        s1_reshape2 = self.s1.reshape(3, 14)
        assert s1_reshape2.shape == (3, 14)
        assert np.all(s1_reshape2.data.lon == self.s1.data.lon.reshape(3, 14))
        assert not np.may_share_memory(s1_reshape2.data.lon, self.s1.data.lon)
        assert s1_reshape2.obstime == self.s1.obstime
        assert np.all(s1_reshape2.location == self.s1.location.reshape(3, 14))
        assert not np.may_share_memory(s1_reshape2.location, self.s1.location)
        assert np.all(s1_reshape2.temperature ==
                      self.s1.temperature.reshape(3, 14))
        assert np.may_share_memory(s1_reshape2.temperature,
                                   self.s1.temperature)
        assert s1_reshape2.pressure == self.s1.pressure

    def test_squeeze(self):
        s0_squeeze = self.s0.reshape(3, 1, 2, 1, 7).squeeze()
        assert s0_squeeze.shape == (3, 2, 7)
        assert np.all(s0_squeeze.data.lat == self.s0.data.lat.reshape(3, 2, 7))
        assert np.may_share_memory(s0_squeeze.data.lat, self.s0.data.lat)

    def test_add_dimension(self):
        s0_adddim = self.s0[:, np.newaxis, :]
        assert s0_adddim.shape == (6, 1, 7)
        assert np.all(s0_adddim.data.lon == self.s0.data.lon[:, np.newaxis, :])
        assert np.may_share_memory(s0_adddim.data.lat, self.s0.data.lat)

    def test_take(self):
        s0_take = self.s0.take((5, 2))
        assert s0_take.shape == (2,)
        assert np.all(s0_take.data.lon == self.s0.data.lon.take((5, 2)))
