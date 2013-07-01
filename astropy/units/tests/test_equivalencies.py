# coding: utf-8
# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Separate tests specifically for equivalencies
"""

from __future__ import (absolute_import, unicode_literals, division,
                        print_function)

import pytest
import numpy as np

from ...tests.compat import assert_allclose
from ...tests.helper import raises
from ...utils import isiterable
from ... import units as u


@pytest.mark.parametrize(('function',), 
        (u.doppler_optical,u.doppler_radio,u.doppler_relativistic))
def test_doppler_frequency_0(function):
    rest = 105.01 * u.GHz
    velo0 = rest.to(u.km/u.s, equivalencies=function(rest))
    assert velo0.value == 0

@pytest.mark.parametrize(('function',), 
        (u.doppler_optical,u.doppler_radio,u.doppler_relativistic))
def test_doppler_wavelength_0(function):
    rest = 105.01 * u.GHz
    q1 = 0.00285489437196 * u.m
    velo0 = q1.to(u.km/u.s, equivalencies=function(rest))
    np.testing.assert_almost_equal( velo0.value , 0 , decimal=6 )

@pytest.mark.parametrize(('function',), 
        (u.doppler_optical,u.doppler_radio,u.doppler_relativistic))
def test_doppler_energy_0(function):
    rest = 105.01 * u.GHz
    q1 = 0.000434286445543 * u.eV
    velo0 = q1.to(u.km/u.s, equivalencies=function(rest))
    np.testing.assert_almost_equal( velo0.value , 0 , decimal=6 )

@pytest.mark.parametrize(('function',), 
        (u.doppler_optical,u.doppler_radio,u.doppler_relativistic))
def test_doppler_frequency_circle(function):
    rest = 105.01 * u.GHz
    shifted = 105.03 * u.GHz
    velo = shifted.to(u.km/u.s, equivalencies=function(rest))
    freq = velo.to(u.GHz, equivalencies=function(rest))
    np.testing.assert_almost_equal( freq.value , shifted.value , decimal=7 )

@pytest.mark.parametrize(('function',), 
        (u.doppler_optical,u.doppler_radio,u.doppler_relativistic))
def test_doppler_wavelength_circle(function):
    rest = 105.01 * u.nm
    shifted = 105.03 * u.nm
    velo = shifted.to(u.km/u.s, equivalencies=function(rest))
    wav = velo.to(u.nm, equivalencies=function(rest))
    np.testing.assert_almost_equal( wav.value , shifted.value , decimal=7 )

@pytest.mark.parametrize(('function',), 
        (u.doppler_optical,u.doppler_radio,u.doppler_relativistic))
def test_doppler_energy_circle(function):
    rest = 1.0501 * u.eV
    shifted = 1.0503 * u.eV
    velo = shifted.to(u.km/u.s, equivalencies=function(rest))
    en = velo.to(u.eV, equivalencies=function(rest))
    np.testing.assert_almost_equal( en.value , shifted.value , decimal=7 )

