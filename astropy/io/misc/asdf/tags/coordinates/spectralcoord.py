# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-

from asdf.tags.core import NDArrayType
from asdf.yamlutil import custom_tree_to_tagged_tree

from astropy.coordinates.spectral_coordinate import SpectralCoord
from astropy.io.misc.asdf.types import AstropyType
from astropy.io.misc.asdf.tags.unit.unit import UnitType


__all__ = ['SpectralCoordType']


class SpectralCoordType(AstropyType):
    """
    ASDF tag implementation used to serialize/derialize SpectralCoord objects
    """
    name = 'coordinates/spectralcoord'
    types = [SpectralCoord]
    version = '1.0.0'

    @classmethod
    def to_tree(cls, spec_coord, ctx):
        node = {}
        if isinstance(spec_coord, SpectralCoord):
            node['value'] = custom_tree_to_tagged_tree(spec_coord.value, ctx)
            node['unit'] = custom_tree_to_tagged_tree(spec_coord.unit, ctx)
            node['observer'] = custom_tree_to_tagged_tree(spec_coord.observer, ctx)
            node['target'] = custom_tree_to_tagged_tree(spec_coord.target, ctx)
            return node
        raise TypeError(f"'{spec_coord}' is not a valid SpectralCoord")

    @classmethod
    def from_tree(cls, node, ctx):
        if isinstance(node, SpectralCoord):
            return node

        unit = UnitType.from_tree(node['unit'], ctx)
        value = node['value']
        observer = node['observer'] if 'observer' in node else None
        target = node['target'] if 'observer' in node else None
        if isinstance(value, NDArrayType):
            value = value._make_array()
        return SpectralCoord(value, unit=unit, observer=observer, target=target)
