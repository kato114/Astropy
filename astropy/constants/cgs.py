# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Astronomical and physics constants in cgs units.  The constants
available (with approximate values) are:
"""
# This docstring is extended by __init__.py

from .constant import Constant
from .._constants import cgs as _cgs
from .._constants.definition import ConstantDefinition

# Define actual Quantity-based Constants. Need to use _c in the loop instead
# of c to avoid overwriting the speed of light constant.
for nm, val in sorted(_cgs.__dict__.items()):
    if isinstance(val, ConstantDefinition):
        _c = Constant(val.value, val.units, val.uncertainty, val.name, val.origin)
        locals()[nm] = _c

del _cgs, nm, val, _c
