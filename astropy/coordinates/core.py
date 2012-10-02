# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
This module contains the fundamental classes used for representing
coordinates in astropy.
"""

import math
from types import *
import numpy as np

import conversions as convert
from .. import units as u

__all__ = ['Angle', 'RA', 'Dec']

twopi = math.pi * 2.0 # no need to calculate this all the time

class Angle(object):
    """ This class represents an Angle. 
        
        Units must be specified by the units parameter.
        Degrees and hours both accept either a string like '15:23:14.231,' or a
        decimal representation of the value, e.g. 15.387.
        
        Parameters
        ----------
        angle : float, int, str
            The angle value
        units : {'degrees', 'radians', 'hours'}

    """
    
    def __init__(self, angle, unit=None, bounds=[-360,360]):
        
        self.bounds = bounds
        
        if isinstance(angle, type(self)):
            angle = angle.radians
            unit = u.radian
        
        # short circuit arrays for now
        if isinstance(angle, list):
            raise TypeError("Angles as lists are not yet supported.")
        
        self.isArray = type(angle) in [list, np.ndarray]
        
        if angle == None:
            raise ValueError("The Angle class requires a unit")

        #angle_type = type(angle[0]) if self.isArray else type(angle)
        
        # -------------------------------
        # unit validation and angle value
        # -------------------------------
        if isinstance(unit, u.Unit):
            pass
        elif isinstance(unit, str):
            unit = u.Unit(unit)
        elif unit == None:
            # try to determine unit from the "angle" value
            if self.isArray:
                try:
                    angle = [x.lower() for x in angle]
                except AttributeError:
                        # If units are not specified as a parameter, the only chance
                        # to determine them is in a string value - if it's not a string,
                        # then there's not enough information to create an Angle.
                        raise ValueError("Could not parse an angle value in the array provided"
                                         "- units could not be determined.".format(angle[idx]))
                for idx, a in enumerate(angle):
                    a_unit = None
                    # order is important here - longest name first
                    for unitStr in ["degrees", "degree", "deg", "°"]:
                        if unitStr in a:
                            a_unit = u.radian
                            a = angle.replace(unitStr, "")
                            angle[idx] = math.radians(convert.parseDegrees(a))
                            break
                    if unit == None:
                        for unitStr in ["hours", "hour", "hr"]:
                            if unitStr in a:
                                a_unit = u.radian
                                a = angle.replace(unitStr, "")
                                angle[idx] = math.radians(convert.parseHours(a)*15.)
                                break
                    if unit == None:
                        for unitStr in ["radians", "radian", "rad"]:
                            if unitStr in angle:
                                a_unit = u.radian
                                a = angle.replace(unitStr, "")
                                angle[idx] = convert.parseRadians(a)
                                break
                    if a_unit == None:
                        raise ValueError("Could not parse the angle value '{0}' "
                                         "- units could not be determined.".format(angle[idx]))
                unit = u.radian
                
            else: # single value
                if type(angle) == str:
                    angle = angle.lower()
                else:
                    raise ValueError("Could not parse the angle value '{0}' "
                                     "- units could not be determined.".format(angle))

                for unitStr in ["degrees", "degree", "deg", "°"]:
                    if unitStr in angle:
                        unit = u.degree
                        angle = angle.replace(unitStr, "")
                if unit == None:
                    for unitStr in ["hours", "hour", "hr"]:
                        if unitStr in angle:
                            unit = u.hour
                            angle = angle.replace(unitStr, "")
                if unit == None:
                    for unitStr in ["radians", "radian", "rad"]:
                        if unitStr in angle:
                            unit = u.radian
                            angle = angle.replace(unitStr, "")


        if unit == None:
            raise ValueError("The unit parameter should be an object from the "
                             "astropy.unit module (e.g. 'from astropy import units as u',"
                             "then use 'u.degree').")
        
        if self.isArray:
            pass # already performed conversions to radians above
        else:
            if unit == u.degree:
                self._radians = math.radians(convert.parseDegrees(angle))
            elif unit == u.radian:
                self._radians = float(angle)
            elif unit == u.hour:
                self._radians = convert.hoursToRadians(convert.parseHours(angle))
            else:
                raise IllegalUnitsError(units)

        # ---------------
        # bounds checking
        # ---------------
        # TODO: handle arrays
        # handle bounds units, convert to radians
        if bounds == None:
           pass # no range checking performed
        else:
            try:
                if unit == u.radian:
                    lower_bound = bounds[0]
                    upper_bound = bounds[1]
                elif unit == u.degree:
                    lower_bound = math.radians(bounds[0])
                    upper_bound = math.radians(bounds[1])
                elif unit == u.hour:
                    lower_bound = math.radians(bounds[0]*15.)
                    upper_bound = math.radians(bounds[1]*15.)
                # invalid units handled above
            except TypeError:
                raise TypeError("Bounds specified for Angle must be a two element list, "
                                "e.g. [0,360] (was given '{0}').".format(type(bounds).__name__))
            
            # bounds check
            if lower_bound < self._radians < upper_bound:
                pass # looks good
            else:
                if self._radians > upper_bound:
                    while True:
                        self._radians -= twopi
                        if self._radians < lower_bound:
                            raise RangeError("The angle given falls outside of the specified bounds.")
                        elif lower_bound < self._radians < upper_bound:
                            break
                
                if self._radians < lower_bound:
                    while True:
                        self._radians += twopi
                        if self._radians > upper_bound:
                            raise RangeError("The angle given falls outside of the specified bounds.")
                        elif lower_bound < self._radians < upper_bound:
                            break
           

    @property
    def degrees(self):
        """ Returns the angle's value in degrees (read-only property). """
        return math.degrees(self.radians) # converts radians to degrees

    @property
    def radians(self):
        """ Returns the angle's value in radians (read-only property). """
        return self._radians

    @property
    def hours(self):
        """ Returns the angle's value in hours (read-only property). """
        return convert.radiansToHours(self.radians)

    @property
    def hms(self):
        """ Returns the angle's value in hours, and print as an (h,m,s) tuple (read-only property). """
        return convert.radiansToHMS(self.radians)

    @property
    def dms(self):
        """ Returns the angle's value in degrees, and print as an (d,m,s) tuple (read-only property). """
        return convert.radiansToDMS(self.radians)

    # ----------------------------------------------------------------------------
    # Emulating numeric types
    # -----------------------
    # Ref: http://docs.python.org/reference/datamodel.html#emulating-numeric-types
    # ----------------------------------------------------------------------------

    # Addition
    def __add__(self, other):
        if self.bounds != other.bounds:
            raise ValueError("An {0} object can only be subtracted from another "
                             "{0} object.".format(type(self).__name__))
        if isinstance(other, type(self)):
            return Angle(self.radians + other.radians, unit=u.radian)
        else:
            raise NotImplementedError("An {0} object can only be added to another "
                                      "{0} object.".format(type(self).__name__))
    
    # Subtraction
    def __sub__(self, other):
        if self.bounds != other.bounds:
            raise ValueError("An {0} object can only be subtracted from another "
                             "{0} object.".format(type(self).__name__))
        if isinstance(other, type(self)):
            return Angle(self.radians - other.radians, unit=u.radian)
        else:
            raise NotImplementedError("An {0} object can only be subtracted from another "
                                      "{0} object.".format(type(self).__name__))
    
    # Multiplication
    def __mul__(self, other):
        raise NotImplementedError("Multiplication is not supported between two {0} "
                                  "objects ".format(type(self).__name__))
    
    # Division
    def __div__(self, other):
        raise NotImplementedError("Division is not supported between two {0} "
                                  "objects ".format(type(self).__name__))
    
    def __truediv__(self, other):
        raise NotImplementedError("Division is not supported between two {0} "
                                  "objects ".format(type(self).__name__))

    def __neg__(self):
        return Angle(-self.radians, unit=u.radian)

    def __eq__(self, other):
        return self.radians == other.radians
    
    def __ne__(self, other):
        return not self.radians == other.radians

    def __lt__(self, other):
        return self.radians < other.radians
    
    def __gt__(self, other):
        return self.radians > other.radians
    
    def __ge__(self, other):
        return self.radians >= other.radians
        
    def __le__(self, other):
        return self.radians <= other.radians
    
    def __abs__(self):
        return Angle(abs(self.radians), unit=u.radian)
    
class RA(Angle):
    """ Represents a J2000 Right Ascension 
    
        Accepts a right ascension angle value. The angle parameter accepts degrees, 
        hours, or radians. There is no default unit.
        Degrees and hours both accept either a string like '15:23:14.231,' or a
        decimal representation of the value, e.g. 15.387.
        
        Parameters
        ----------
        angle : float, int
            The angle value
        unit : an instance of astropy.Unit or an equivalent string
            The unit of the angle value
    
    """
    
    def __init__(self, angle, unit=None):
        if unit == None:
            raise ValueError("Units must be specified for RA, one of u.degree, u.hour, or u.radian.")
    
        super(RA, self).__init__(angle, unit)
    
    def hourAngle(self, lst, unit=None):
        """ Given a Local Sidereal Time (LST), calculate the hour angle for this RA
        
            Parameters
            ----------
            lst : float, str, `Angle`
                A Local Sidereal Time (LST)
            unit : str
                The units of the LST, if not an `Angle` object or datetime.datetime object
                .. note::
                    * if lst is **not** an `Angle`-like object, you can specify the units by passing a `unit` parameter into the call
                    * this function currently returns an `Angle` object
        """
        # TODO : this should return an HA() object, and accept an Angle or LST object
        if not isinstance(lst, Angle):
            lst = Angle(lst, units)
        
        return Angle(lst.radians - self.radians, unit=u.radian)
    
    def lst(self, hourAngle, unit=u.hour):
        """ Given an Hour Angle, calculate the Local Sidereal Time (LST) for this RA
    
            Parameters
            ----------
            ha :  float, str, `Angle`
                An Hour Angle
            units : str
                The units of the ha, if not an `Angle` object
            
            .. note:: if ha is *not* an Angle object, you can specify the units by passing a 'units' parameter into the call
                'units' can be radians, degrees, or hours
                this function always returns an Angle object
        """
        # TODO : I guess this should return an HA() object, and accept an Angle or LST object
        if not isinstance(ha, Angle):
            ha = Angle(ha, unit)
            
        return Angle(ha.radians + self.radians, units="radians")

class Dec(Angle):
    """ Represents a J2000 Declination """
    
    def __init__(self, angle, unit=u.degree):
        """ Accepts a Declination angle value. The angle parameter accepts degrees, 
            hours, or radians and the default units are hours.
            Degrees and hours both accept either a string like '15:23:14.231,' or a
            decimal representation of the value, e.g. 15.387.
        
            Parameters
            ----------
            angle : float, int
                The angular value
            units : str 
                The units of the specified declination
            
        """
        super(Dec, self).__init__(angle, unit)
