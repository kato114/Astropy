# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This module contains convenience functions for retrieving solar system
ephemerides from jplephem.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import OrderedDict
import numpy as np
from .sky_coordinate import SkyCoord
from ..utils.data import download_file
from ..utils.decorators import classproperty
from ..utils.state import ScienceState
from .. import units as u
from .. import _erfa as erfa
from ..constants import c as speed_of_light
from .representation import CartesianRepresentation
from .builtin_frames import GCRS, ICRS
from .builtin_frames.utils import get_jd12, cartrepr_from_matmul
from .. import _erfa
from ..extern import six

__all__ = ["get_body", "get_moon", "get_body_barycentric",
           "solar_system_ephemeris"]


DEFAULT_JPL_EPHEMERIS = 'de430'

"""List of kernel pairs needed to calculate positions of a given object."""
BODY_NAME_TO_KERNEL_SPEC = OrderedDict(
                                      (('sun', [(0, 10)]),
                                       ('mercury', [(0, 1), (1, 199)]),
                                       ('venus', [(0, 2), (2, 299)]),
                                       ('earth-moon-barycenter', [(0, 3)]),
                                       ('earth',  [(0, 3), (3, 399)]),
                                       ('moon', [(0, 3), (3, 301)]),
                                       ('mars', [(0, 4)]),
                                       ('jupiter', [(0, 5)]),
                                       ('saturn', [(0, 6)]),
                                       ('uranus', [(0, 7)]),
                                       ('neptune', [(0, 8)]),
                                       ('pluto', [(0, 9)]))
                                      )

"""Indices to the plan94 routine for the given object."""
PLAN94_BODY_NAME_TO_PLANET_INDEX = OrderedDict(
    (('mercury', 1),
     ('venus', 2),
     ('earth-moon-barycenter', 3),
     ('mars', 4),
     ('jupiter', 5),
     ('saturn', 6),
     ('uranus', 7),
     ('neptune', 8)))

_EPHEMERIS_NOTE = """
You can either give an explicit ephemeris or use a default, which is normally
an approximate ephemeris that does not require ephemeris files.  To change
the default to be a JPL ephemeris::

    >>> from astropy import coordinates as coord
    >>> coord.solar_system_ephemeris.set('jpl')

This requires the jplephem package (https://pypi.python.org/pypi/jplephem).
If needed, the ephemeris file will be downloaded (and cached).

One can check which bodies are covered by a given ephemeris using::
    >>> coord.solar_system_ephemeris.bodies
    ('earth', 'sun', 'mercury', 'venus', 'earth-moon-barycentre', 'mars',
     'jupiter', 'saturn', 'uranus', 'neptune')
"""[1:-1]


class solar_system_ephemeris(ScienceState):
    """Default ephemerides for calculating positions of Solar-System bodies.

    This can be a URL to a JPL ephemerides, or one of the following::

    - 'approximate': polynomial approximations to the orbital elements.
    - 'de430' or 'de432s': short-cuts for recent JPL dynamical models.
    - 'jpl': Alias for the default JPL ephemeris (currently, 'de430').
    - `None`: Ensure an Exception is raised without an explicit ephemeris.

    The default is 'approximate', which uses the ``epv00`` and ``plan94``
    routines from the Standards Of Fundamental Astronomy library (as
    implemented in ``erfa``).

    Notes
    -----
    The default Satellite Planet Kernel (SPK) file from NASA JPL (de430) is
    ~120MB, and covers years ~1550-2650 CE [1]_.  The smaller de432s file is
    ~10MB, and covers years 1950-2050 [2]_.  Older versions of the JPL
    ephemerides (such as the widely used de200) can be used via their URL [3]_.

    .. [1] http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/aareadme_de430-de431.txt
    .. [2] http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/aareadme_de432s.txt
    .. [3] http://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/
    """
    _value = 'approximate'
    _kernel = None

    @classmethod
    def validate(cls, value):
        # Set up Kernel; if the file is not in cache, this will dowload it.
        cls.get_kernel(value)
        return value

    @classmethod
    def get_kernel(cls, value):
        # ScienceState only ensures the `_value` attribute is up to date,
        # so we need to be sure any kernel returned is consistent.
        if cls._kernel is None or cls._kernel.origin != value:
            kernel = _get_kernel(value)
            if kernel is not None:
                kernel.origin = value
            cls._kernel = kernel
        return cls._kernel

    @classproperty
    def kernel(cls):
        return cls.get_kernel(cls._value)

    @classproperty
    def bodies(cls):
        if cls._value is None:
            return None
        if cls._value.lower() == 'approximate':
            return (('earth', 'sun') +
                    tuple(PLAN94_BODY_NAME_TO_PLANET_INDEX.keys()))
        else:
            return tuple(BODY_NAME_TO_KERNEL_SPEC.keys())



def _get_kernel(value):
    """
    Try importing jplephem, download/retrieve from cache the Satellite Planet
    Kernel corresponding to the given ephemeris.
    """
    if value is None or value.lower() == 'approximate':
        return None

    if value.lower() == 'jpl':
        value = DEFAULT_JPL_EPHEMERIS

    if value.lower() in ('de430', 'de432s'):
        value = ('http://naif.jpl.nasa.gov/pub/naif/generic_kernels'
                 '/spk/planets/{:s}.bsp'.format(value.lower()))
    else:
        try:
            six.moves.urllib.parse.urlparse(value)
        except:
            raise ValueError('{} was not one of the standard strings and '
                             'could not be parsed as a URL'.format(value))

    try:
        from jplephem.spk import SPK
    except ImportError:
        raise ImportError("Solar system JPL ephemeris calculations require "
                          "the jplephem package "
                          "(https://pypi.python.org/pypi/jplephem)")

    return SPK.open(download_file(value, cache=True))


def get_body_barycentric(body, time, ephemeris=None):
    """Calculate the barycentric position of a solar system body.

    Parameters
    ----------
    body : str
        The solar system body for which to calculate positions.
    time : `~astropy.time.Time`
        Time of observation.
    ephemeris : str, optional
        Ephemeris to use.  By default, use the one set with
        :func:`~astropy.coordinates.solar_system_ephemeris.set`

    Returns
    -------
    cartesian_position : `~astropy.coordinates.CartesianRepresentation`
        Barycentric (ICRS) position of the body in cartesian coordinates

    Notes
    -----
    """ + _EPHEMERIS_NOTE

    if ephemeris is None:
        ephemeris = solar_system_ephemeris.get()
        if ephemeris is None:
            raise ValueError(_EPHEMERIS_NOTE)
        kernel = solar_system_ephemeris.kernel
    else:
        kernel = _get_kernel(ephemeris)

    jd1, jd2 = get_jd12(time, 'tdb')
    body = body.lower()
    if kernel is None:
        earth_pv_helio, earth_pv_bary = erfa.epv00(jd1, jd2)
        if body == 'earth':
            cartesian_position_body = earth_pv_bary[..., 0, :]

        else:
            sun_bary = earth_pv_bary[..., 0, :] - earth_pv_helio[..., 0, :]
            if body == 'sun':
                cartesian_position_body = sun_bary
            else:
                try:
                    body_index = PLAN94_BODY_NAME_TO_PLANET_INDEX[body]
                except KeyError:
                    raise KeyError("{0}'s position cannot be calculated with "
                                   "the '{1}' ephemeris."
                                   .format(body, ephemeris))
                body_pv_helio = erfa.plan94(jd1, jd2, body_index)
                cartesian_position_body = body_pv_helio[..., 0, :] + sun_bary

        barycen_to_body_vector = u.Quantity(
            np.rollaxis(cartesian_position_body, -1, 0), u.au)

    else:
        # Lookup chain for JPL ephemeris.
        try:
            kernel_spec = BODY_NAME_TO_KERNEL_SPEC[body.lower()]
        except KeyError:
            raise KeyError("{0}'s position cannot be calculated with "
                           "the {1} ephemeris.".format(body, ephemeris))

        cartesian_position_body = sum([kernel[pair].compute(jd1, jd2)
                                       for pair in kernel_spec])

        barycen_to_body_vector = u.Quantity(cartesian_position_body, unit=u.km)

    return CartesianRepresentation(barycen_to_body_vector)


def _get_apparent_body_position(body, time, ephemeris):
    """Calculate the apparent position of body ``body`` relative to Earth.

    This corrects for the light-travel time to the object.

    Parameters
    ----------
    body : str
        The solar system body for which to calculate positions.
    time : `~astropy.time.Time`
        Time of observation.
    ephemeris : str, optional
        Ephemeris to use.  By default, use the one set with
        :func:`~astropy.coordinates.solar_system_ephemeris.set`

    Returns
    -------
    cartesian_position : `~astropy.coordinates.CartesianRepresentation`
        Barycentric (ICRS) apparent position of the body in cartesian coordinates
    """ + _EPHEMERIS_NOTE
    # Calculate position given approximate light travel time.
    delta_light_travel_time = 20. * u.s
    emitted_time = time
    light_travel_time = 0. * u.s
    earth_loc = get_body_barycentric('earth', time, ephemeris)
    while np.any(np.fabs(delta_light_travel_time) > 1.0e-8*u.s):
        body_loc = get_body_barycentric(body, emitted_time, ephemeris)
        earth_body_vector = body_loc.xyz - earth_loc.xyz
        earth_distance = np.sqrt(np.sum(earth_body_vector**2, axis=0))
        delta_light_travel_time = (light_travel_time -
                                   earth_distance/speed_of_light)
        light_travel_time = earth_distance/speed_of_light
        emitted_time = time - light_travel_time

    return get_body_barycentric(body, emitted_time, ephemeris)


def get_body(body, time, location=None, ephemeris=None):
    """
    Get a `~astropy.coordinates.SkyCoord` for a solar system body as observed
    from a location on Earth.

    Parameters
    ----------
    body : str
        The solar system body for which to calculate positions.
    time : `~astropy.time.Time`
        Time of observation.
    location : `~astropy.coordinates.EarthLocation`, optional
        Location of observer on the Earth.  If not given, will be taken from
        ``time`` (if not present, a geocentric observer will be assumed).
    ephemeris : str, optional
        Ephemeris to use.  If not given, use the one set with
        :func:`~astropy.coordinates.solar_system_ephemeris.set` (which is
        set to 'approximate' by default).

    Returns
    -------
    skycoord : `~astropy.coordinates.SkyCoord`
        GCRS Coordinate for the body

    Notes
    -----
    """ + _EPHEMERIS_NOTE
    if location is None:
        location = time.location

    cartrep = _get_apparent_body_position(body, time, ephemeris)
    icrs = ICRS(cartrep)
    if location is not None:
        obsgeoloc, obsgeovel = location.get_gcrs_posvel(time)
        gcrs = icrs.transform_to(GCRS(obstime=time,
                                      obsgeoloc=obsgeoloc,
                                      obsgeovel=obsgeovel))
    else:
        gcrs = icrs.transform_to(GCRS(obstime=time))
    return SkyCoord(gcrs)


def get_moon(time, location=None, ephemeris=None):
    """
    Get a `~astropy.coordinates.SkyCoord` for the Earth's Moon as observed
    from a location on Earth.

    Parameters
    ----------
    time : `~astropy.time.Time`
        Time of observation
    location : `~astropy.coordinates.EarthLocation`
        Location of observer on the Earth. If none is supplied, taken from
        ``time`` (if not present, a geocentric observer will be assumed).
    ephemeris : str, optional
        Ephemeris to use.  If not given, use the one set with
        :func:`~astropy.coordinates.solar_system_ephemeris.set` (which is
        set to 'approximate' by default).

    Returns
    -------
    skycoord : `~astropy.coordinates.SkyCoord`
        Coordinate for the Moon

    Notes
    -----
    """ +_EPHEMERIS_NOTE

    return get_body('moon', time, location=location, ephemeris=ephemeris)


def _apparent_position_in_true_coordinates(skycoord):
    """
    Convert Skycoord in GCRS frame into one in which RA and Dec
    are defined w.r.t to the true equinox and poles of the Earth
    """
    jd1, jd2 = get_jd12(skycoord.obstime, 'tt')
    _, _, _, _, _, _, _, rbpn = _erfa.pn00a(jd1, jd2)
    return SkyCoord(skycoord.frame.realize_frame(cartrepr_from_matmul(rbpn, skycoord)))
