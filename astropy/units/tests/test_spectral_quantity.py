import pytest

import numpy as np
from numpy.testing import assert_allclose

from astropy import units as u
from astropy.tests.helper import assert_quantity_allclose
from astropy.constants import c


from ..spectral_quantity import SpectralQuantity

SPECTRAL_UNITS = (u.GHz, u.micron, u.keV, (1 / u.nm).unit, u.km / u.s)


class TestSpectralQuantity:

    @pytest.mark.parametrize('unit', SPECTRAL_UNITS)
    def test_init_value(self, unit):
        SpectralQuantity(1, unit=unit)

    @pytest.mark.parametrize('unit', SPECTRAL_UNITS)
    def test_init_quantity(self, unit):
        SpectralQuantity(1 * unit)

    @pytest.mark.parametrize('unit', SPECTRAL_UNITS)
    def test_init_spectralquantity(self, unit):
        SpectralQuantity(SpectralQuantity(1, unit=unit))

    @pytest.mark.parametrize('unit', (u.kg, u.byte))
    def test_init_invalid(self, unit):
        with pytest.raises(u.UnitsError, match='SpectralQuantity instances require units'):
            SpectralQuantity(1, unit=unit)
        with pytest.raises(u.UnitsError, match='SpectralQuantity instances require units'):
            SpectralQuantity(1 * unit)

    @pytest.mark.parametrize(('unit1', 'unit2'), zip(SPECTRAL_UNITS, SPECTRAL_UNITS))
    def test_spectral_conversion(self, unit1, unit2):
        sq1 = SpectralQuantity(1 * unit1)
        sq2 = sq1.to(unit2)
        sq3 = sq2.to(unit1)
        assert_quantity_allclose(sq1, sq3)

    def test_doppler_conversion(self):

        sq1 = SpectralQuantity(1 * u.km / u.s, doppler_convention='optical', doppler_rest=500 * u.nm)

        sq2 = sq1.to(u.m / u.s)
        assert_allclose(sq2.value, 1000)

        sq3 = sq1.to(u.m / u.s, doppler_convention='radio')
        assert_allclose(sq3.value, 999.996664)

        sq4 = sq1.to(u.m / u.s, doppler_convention='relativistic')
        assert_allclose(sq4.value, 999.998332)

        sq5 = sq1.to(u.m / u.s, doppler_rest=499.9 * u.nm)
        assert_allclose(sq5.value, 60970.685737)

        val5 = sq1.to_value(u.m / u.s, doppler_rest=499.9 * u.nm)
        assert_allclose(val5, 60970.685737)

    def test_doppler_conversion_validation(self):

        sq1 = SpectralQuantity(1 * u.GHz)
        sq2 = SpectralQuantity(1 * u.km / u.s)

        with pytest.raises(ValueError, match='doppler_convention not set, cannot convert to/from velocities'):
            sq1.to(u.km / u.s)

        with pytest.raises(ValueError, match='doppler_convention not set, cannot convert to/from velocities'):
            sq2.to(u.GHz)

        with pytest.raises(ValueError, match='doppler_rest not set, cannot convert to/from velocities'):
            sq1.to(u.km / u.s, doppler_convention='radio')

        with pytest.raises(ValueError, match='doppler_rest not set, cannot convert to/from velocities'):
            sq2.to(u.GHz, doppler_convention='radio')

        with pytest.raises(u.UnitsError, match="Argument 'doppler_rest' to function 'to' must be in units"):
            sq1.to(u.km / u.s, doppler_convention='radio', doppler_rest=5 * u.kg)

        with pytest.raises(u.UnitsError, match="Argument 'doppler_rest' to function 'to' must be in units"):
            sq2.to(u.GHz, doppler_convention='radio', doppler_rest=5 * u.kg)

        with pytest.raises(ValueError, match="doppler_convention should be one of optical/radio/relativistic"):
            sq1.to(u.km / u.s, doppler_convention='banana', doppler_rest=5 * u.GHz)

        with pytest.raises(ValueError, match="doppler_convention should be one of optical/radio/relativistic"):
            sq2.to(u.GHz, doppler_convention='banana', doppler_rest=5 * u.GHz)

        with pytest.raises(ValueError, match='Original doppler_convention not set'):
            sq2.to(u.km / u.s, doppler_convention='radio')

        with pytest.raises(ValueError, match='Original doppler_rest not set'):
            sq2.to(u.km / u.s, doppler_rest=5 * u.GHz)

    def test_doppler_set_parameters(self):

        sq1 = SpectralQuantity(1 * u.km / u.s)

        with pytest.raises(ValueError, match="doppler_convention should be one of optical/radio/relativistic"):
            sq1.doppler_convention = 'banana'

        assert sq1.doppler_convention is None

        sq1.doppler_convention = 'radio'

        assert sq1.doppler_convention == 'radio'

        with pytest.raises(AttributeError, match="doppler_convention has already been set, and cannot be changed"):
            sq1.doppler_convention = 'optical'

        assert sq1.doppler_convention == 'radio'

        with pytest.raises(u.UnitsError, match="Argument 'value' to function 'doppler_rest' must be in units"):
            sq1.doppler_rest = 5 * u.kg

        sq1.doppler_rest = 5 * u.GHz

        assert_quantity_allclose(sq1.doppler_rest, 5 * u.GHz)

        with pytest.raises(AttributeError, match="doppler_rest has already been set, and cannot be changed"):
            sq1.doppler_rest = 4 * u.GHz

        assert_quantity_allclose(sq1.doppler_rest, 5 * u.GHz)

    def test_apply_relativistic_doppler_shift(self):

        # Frequency
        sq1 = SpectralQuantity(1 * u.GHz)
        sq2 = sq1._apply_relativistic_doppler_shift(0.5 * c)
        assert_quantity_allclose(sq2, np.sqrt(1. / 3.) * u.GHz)

        # Wavelength
        sq3 = SpectralQuantity(500 * u.nm)
        sq4 = sq3._apply_relativistic_doppler_shift(0.5 * c)
        assert_quantity_allclose(sq4, np.sqrt(3) * 500 * u.nm)

        # Energy
        sq5 = SpectralQuantity(300 * u.eV)
        sq6 = sq5._apply_relativistic_doppler_shift(0.5 * c)
        assert_quantity_allclose(sq6, np.sqrt(1. / 3.) * 300 * u.eV)

        # Wavenumber
        sq7 = SpectralQuantity(0.01 / u.micron)
        sq8 = sq7._apply_relativistic_doppler_shift(0.5 * c)
        assert_quantity_allclose(sq8, np.sqrt(1. / 3.) * 0.01 / u.micron)

        # Velocity (doppler_convention='relativistic')
        sq9 = SpectralQuantity(200 * u.km / u.s, doppler_convention='relativistic', doppler_rest=1 * u.GHz)
        sq10 = sq9._apply_relativistic_doppler_shift(300 * u.km / u.s)
        assert_quantity_allclose(sq10, 500 * u.km / u.s)
        assert sq10.doppler_convention == 'relativistic'

        # Velocity (doppler_convention='optical')
        sq11 = SpectralQuantity(200 * u.km / u.s, doppler_convention='radio', doppler_rest=1 * u.GHz)
        sq12 = sq11._apply_relativistic_doppler_shift(300 * u.km / u.s)
        assert_quantity_allclose(sq12, 499.650341 * u.km / u.s)
        assert sq12.doppler_convention == 'radio'

        # Velocity (doppler_convention='radio')
        sq13 = SpectralQuantity(200 * u.km / u.s, doppler_convention='optical', doppler_rest=1 * u.GHz)
        sq14 = sq13._apply_relativistic_doppler_shift(300 * u.km / u.s)
        assert_quantity_allclose(sq14, 500.350827 * u.km / u.s)
        assert sq14.doppler_convention == 'optical'
