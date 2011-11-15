"""
This module handles the conversion of various VOTABLE datatypes
to/from TABLEDATA_ and BINARY_ formats.
"""

from __future__ import division, absolute_import

# STDLIB
import re
from struct import unpack as struct_unpack
from struct import pack as struct_pack
import sys

# THIRD-PARTY
import numpy as np

# LOCAL
from .xmlutil import xml_escape_cdata
from .exceptions import (vo_raise, vo_warn, warn_or_raise, W01, W26,
    W30, W31, W32, W39, W46, W47, W49, E01, E02, E03, E04, E05, E06)
from .util import IS_PY3K

if not IS_PY3K:
    def bytes(s, encoding):
        return str(s)

pedantic_array_splitter = re.compile(r" +")
array_splitter = re.compile(r"\s+|(?:\s*,\s*)")
"""
A regex to handle splitting values on either whitespace or commas.

SPEC: Usage of commas is not actually allowed by the spec, but many
files in the wild use them.
"""

_zero_int = bytes('\0\0\0\0', 'ascii')
_empty_bytes = bytes('', 'ascii')
_zero_byte = bytes('\0', 'ascii')


class Converter(object):
    """
    The base class for all converters.  Each subclass handles
    converting a specific VOTABLE data type to/from the TABLEDATA_ and
    BINARY_ on-disk representations.
    """
    def __init__(self, field, config={}, pos=None):
        """
        Parameters
        ----------
        field : `~astropy.io.vo.table.Field`
            object describing the datatype

        config : dict
            The parser configuration dictionary

        pos : tuple
            The position in the XML file where the FIELD object was
            found.  Used for error messages.
        """
        pass

    @staticmethod
    def _parse_length(read):
        return struct_unpack(">I", read(4))[0]

    @staticmethod
    def _write_length(length):
        return struct_pack(">I", int(length))

    def parse(self, value, config={}, pos=None):
        """
        Convert the string *value* from the TABLEDATA_ format into an
        object with the correct native in-memory datatype and mask flag.

        Parameters
        ----------
        value : str
            value in TABLEDATA format

        Returns
        -------
        native : tuple (value, mask)
            The value as a Numpy array or scalar, and *mask* is True
            if the value is missing.
        """
        raise NotImplementedError(
            "This datatype must implement a 'parse' method.")

    def parse_scalar(self, value, config={}, pos=None):
        """
        Parse a single scalar of the underlying type of the converter.
        For non-array converters, this is equivalent to parse.  For
        array converters, this is used to parse a single
        element of the array.

        Parameters
        ----------
        value : str
            value in TABLEDATA format

        Returns
        -------
        native : tuple (value, mask)
            The value as a Numpy array or scalar, and *mask* is True
            if the value is missing.
        """
        return self.parse(value, config, pos)

    def output(self, value, mask):
        """
        Convert the object *value* (in the native in-memory datatype)
        to a string suitable for serializing in the TABLEDATA_ format.

        Parameters
        ----------
        value : native type corresponding to this converter
            The value

        mask : bool
            If `True`, will return the string representation of a
            masked value.

        Returns
        -------
        tabledata_repr : str
        """
        raise NotImplementedError(
            "This datatype must implement a 'output' method.")

    def binparse(self, read):
        """
        Reads some number of bytes from the BINARY_ format
        representation by calling the function *read*, and returns the
        native in-memory object representation for the datatype
        handled by *self*.

        Parameters
        ----------
        read : function
            A function that given a number of bytes, returns a byte
            string.

        Returns
        -------
        native : tuple (value, mask)
            The value as a Numpy array or scalar, and *mask* is True
            if the value is missing.
        """
        raise NotImplementedError(
            "This datatype must implement a 'binparse' method.")

    def binoutput(self, value, mask):
        """
        Convert the object *value* in the native in-memory datatype to
        a string of bytes suitable for serialization in the BINARY_
        format.

        Parameters
        ----------
        value : native type corresponding to this converter
            The value

        mask : bool
            If `True`, will return the string representation of a
            masked value.

        Returns
        -------
        bytes : byte string
            The binary representation of the value, suitable for
            serialization in the BINARY_ format.
        """
        raise NotImplementedError(
            "This datatype must implement a 'binoutput' method.")


class Char(Converter):
    """
    Handles the char datatype. (7-bit unsigned characters)

    Missing values are not handled for string or unicode types.
    """
    default = _empty_bytes

    def __init__(self, field, config={}, pos=None):
        Converter.__init__(self, field, config, pos)

        if field.arraysize is None:
            vo_warn(W47, (), config, pos)
            field.arraysize = '1'

        if field.arraysize == '*':
            self.format = 'O'
            self.binparse = self._binparse_var
            self.binoutput = self._binoutput_var
            self.arraysize = '*'
        else:
            if field.arraysize.endswith('*'):
                field.arraysize = field.arraysize[:-1]
            try:
                self.arraysize = int(field.arraysize)
            except ValueError:
                vo_raise(E01, (field.arraysize, 'char', field.ID), config)
            self.format = 'S%d' % self.arraysize
            self.binparse = self._binparse_fixed
            self.binoutput = self._binoutput_fixed
            self._struct_format = ">%ds" % self.arraysize

        if config.get('pedantic'):
            self.parse = self._ascii_parse
        else:
            self.parse = self._str_parse

    def _ascii_parse(self, value, config={}, pos=None):
        if self.arraysize != '*' and len(value) > self.arraysize:
            vo_warn(W46, ('char', self.arraysize), config, pos)
        return value.encode('ascii'), False

    if IS_PY3K:
        def _str_parse(self, value, config={}, pos=None):
            if self.arraysize != '*' and len(value) > self.arraysize:
                vo_warn(W46, ('char', self.arraysize), config, pos)
            return bytes(value, 'ascii'), False
    else:
        def _str_parse(self, value, config={}, pos=None):
            if self.arraysize != '*' and len(value) > self.arraysize:
                vo_warn(W46, ('char', self.arraysize), config, pos)
            return str(value), False

    if IS_PY3K:
        def output(self, value, mask):
            if mask:
                return ''
            if not isinstance(value, str):
                value = value.decode('ascii')
            return xml_escape_cdata(value)
    else:
        def output(self, value, mask):
            if mask:
                return ''
            return xml_escape_cdata(value).encode('ascii')

    def _binparse_var(self, read):
        length = self._parse_length(read)
        return read(length), False

    def _binparse_fixed(self, read):
        s = struct_unpack(self._struct_format, read(self.arraysize))[0]
        end = s.find(_zero_byte)
        if end != -1:
            return s[:end], False
        return s, False

    def _binoutput_var(self, value, mask):
        if mask or value is None or value == '':
            return _zero_int
        return self._write_length(len(value)) + value

    def _binoutput_fixed(self, value, mask):
        if mask:
            value = _empty_bytes
        return struct_pack(self._struct_format, value)


class UnicodeChar(Converter):
    """
    Handles the unicodeChar data type. UTF-16-BE.

    Missing values are not handled for string or unicode types.
    """
    default = u''

    def __init__(self, field, config={}, pos=None):
        Converter.__init__(self, field, config, pos)

        if field.arraysize is None:
            vo_warn(W47, (), config, pos)
            field.arraysize = '1'

        if field.arraysize == '*':
            self.format = 'O'
            self.binparse = self._binparse_var
            self.binoutput = self._binoutput_var
            self.arraysize = '*'
        else:
            try:
                self.arraysize = int(field.arraysize)
            except ValueError:
                vo_raise(E01, (field.arraysize, 'unicode', field.ID), config)
            self.format = 'U%d' % self.arraysize
            self.binparse = self._binparse_fixed
            self.binoutput = self._binoutput_fixed
            self._struct_format = ">%ds" % (self.arraysize * 2)

    if IS_PY3K:
        def parse(self, value, config={}, pos=None):
            if self.arraysize != '*' and len(value) > self.arraysize:
                vo_warn(W46, ('unicodeChar', self.arraysize), config, pos)
            return value, False
    else:
        def parse(self, value, config={}, pos=None):
            if self.arraysize != '*' and len(value) > self.arraysize:
                vo_warn(W46, ('unicodeChar', self.arraysize), config, pos)
            return unicode(value, 'utf-8'), False

    if IS_PY3K:
        def output(self, value, mask):
            if mask:
                return ''
            return xml_escape_cdata(value)
    else:
        def output(self, value, mask):
            if mask:
                return ''
            return xml_escape_cdata(value).encode('utf-8')

    def _binparse_var(self, read):
        length = self._parse_length(read)
        return read(length * 2).decode('utf_16_be'), False

    def _binparse_fixed(self, read):
        s = struct_unpack(self._struct_format, read(self.arraysize * 2))[0]
        s = s.decode('utf_16_be')
        end = s.find('\0')
        if end != -1:
            return s[:end], False
        return s, False

    def _binoutput_var(self, value, mask):
        if mask or value is None or value == '':
            return _zero_int
        encoded = value.encode('utf_16_be')
        return self._write_length(len(encoded) / 2) + encoded

    def _binoutput_fixed(self, value, mask):
        if mask:
            value = u''
        return struct_pack(self._struct_format, value.encode('utf_16_be'))


class Array(Converter):
    """
    Handles both fixed and variable-lengths arrays.
    """
    def __init__(self, field, config={}, pos=None):
        Converter.__init__(self, field, config, pos)

        if config.get('pedantic'):
            self._splitter = self._splitter_pedantic
        else:
            self._splitter = self._splitter_lax

    def parse_scalar(self, value, config={}, pos=0):
        return self._base.parse_scalar(value, config, pos)

    @staticmethod
    def _splitter_pedantic(value, config={}, pos=None):
        return pedantic_array_splitter.split(value)

    @staticmethod
    def _splitter_lax(value, config={}, pos=None):
        if ',' in value:
            vo_warn(W01, (), config, pos)
        return array_splitter.split(value)


class VarArray(Array):
    """
    Handles variable lengths arrays (i.e. where *arraysize* is '*').
    """
    format = 'O'

    def __init__(self, field, base, arraysize, config={}, pos=None):
        Array.__init__(self, field, config)

        self._base = base
        self.default = np.array([], dtype=self._base.format)

    def output(self, value, mask):
        output = self._base.output
        result = [output(x, m) for x, m in np.broadcast(value, mask)]
        return ' '.join(result)

    def binparse(self, read):
        length = self._parse_length(read)

        result = []
        result_mask = []
        binparse = self._base.binparse
        for i in xrange(length):
            val, mask = binparse(read)
            result.append(val)
            result_mask.append(mask)
        return (np.array(result),
                np.array(result_mask, dtype='bool'))

    def binoutput(self, value, mask):
        if value is None or len(value) == 0:
            return _zero_int

        length = len(value)
        result = [self._write_length(length)]
        binoutput = self._base.binoutput
        for x, m in zip(value, mask):
            result.append(binoutput(x, m))
        return _empty_bytes.join(result)


class ArrayVarArray(VarArray):
    """
    Handles an array of variable-length arrays, i.e. where *arraysize*
    ends in '*'.
    """
    def parse(self, value, config={}, pos=None):
        if value.strip() == '':
            return np.array([]), True

        parts = self._splitter(value, config, pos)
        items = self._base._items
        parse_parts = self._base.parse_parts
        if len(parts) % items != 0:
            vo_raise(E02, (items, len(parts)), config, pos)
        result = []
        result_mask = []
        for i in xrange(0, len(parts), items):
            value, mask = parse_parts(parts[i:i+items], config, pos)
            result.append(value)
            result_mask.append(mask)
        return np.array(result), np.array(result_mask, dtype='bool')


class ScalarVarArray(VarArray):
    """
    Handles a variable-length array of numeric scalars.
    """
    def parse(self, value, config={}, pos=None):
        if value.strip() == '':
            return np.array([]), True

        parts = self._splitter(value, config, pos)

        parse = self._base.parse
        result = []
        result_mask = []
        for x in parts:
            value, mask = parse(x, config, pos)
            result.append(value)
            result_mask.append(mask)
        return (np.array(result, dtype=self._base.format),
                np.array(result_mask, dtype='bool'))


class NumericArray(Array):
    """
    Handles a fixed-length array of numeric scalars.
    """
    vararray_type = ArrayVarArray

    def __init__(self, field, base, arraysize, config={}, pos=None):
        Array.__init__(self, field, config, pos)

        self._base = base
        self._arraysize = arraysize
        self.format = "%s%s" % (tuple(arraysize), base.format)

        self._items = 1
        for dim in arraysize:
            self._items *= dim

        self._memsize = np.dtype(self.format).itemsize
        self._bigendian_format = '>' + self.format

        self.default = (
            np.ones(arraysize, dtype=self._base.format) *
            self._base.default)

    def parse(self, value, config={}, pos=None):
        parts = self._splitter(value, config, pos)
        if len(parts) != self._items:
            warn_or_raise(E02, E02, (self._items, len(parts)), config, pos)
        if config.get('pedantic'):
            return self.parse_parts(parts, config, pos)
        else:
            if len(parts) == self._items:
                pass
            elif len(parts) > self._items:
                parts = parts[:self._items]
            else:
                parts = (parts +
                         ([self._base.default] * (self._items - len(parts))))
            return self.parse_parts(parts, config, pos)

    def parse_parts(self, parts, config={}, pos=None):
        base_parse = self._base.parse
        result = []
        result_mask = []
        for x in parts:
            value, mask = base_parse(x, config, pos)
            result.append(value)
            result_mask.append(mask)
        result = np.array(result, dtype=self._base.format).reshape(
            self._arraysize)
        result_mask = np.array(result_mask, dtype='bool').reshape(
            self._arraysize)
        return result, result_mask

    def output(self, value, mask):
        base_output = self._base.output
        value = np.asarray(value)
        mask = np.asarray(mask)
        return ' '.join(base_output(x, m) for x, m in
                        zip(value.flat, mask.flat))

    def binparse(self, read):
        result = np.fromstring(read(self._memsize),
                               dtype=self._bigendian_format)[0]
        result_mask = self._base.is_null(result)
        return result, result_mask

    def binoutput(self, value, mask):
        filtered = self._base.filter_array(value, mask)
        if filtered.dtype.byteorder != '>':
            filtered = filtered.byteswap()
        return filtered.tostring()


class Numeric(Converter):
    """
    The base class for all numeric data types.
    """
    array_type = NumericArray
    vararray_type = ScalarVarArray
    null = None

    def __init__(self, field, config={}, pos=None):
        Converter.__init__(self, field, config, pos)

        self._memsize = np.dtype(self.format).itemsize
        self._bigendian_format = '>' + self.format
        if field.values.null is not None:
            self.null = np.asarray(field.values.null, dtype=self.format)
            self.default = self.null
            self.is_null = self._is_null
        else:
            self.is_null = np.isnan

    def binparse(self, read):
        result = np.fromstring(read(self._memsize),
                               dtype=self._bigendian_format)
        return result[0], self.is_null(result[0])

    def _is_null(self, value):
        return value == self.null


class FloatingPoint(Numeric):
    """
    The base class for floating-point datatypes.
    """
    default = np.nan

    def __init__(self, field, config={}, pos=None):
        Numeric.__init__(self, field, config, pos)

        precision = field.precision
        if precision is None:
            self._output_format = '%g'
        elif precision.startswith("E"):
            self._output_format = "%%.%dE" % (int(precision[1:]))
        elif precision.startswith("F"):
            self._output_format = "%%.%dg" % (int(precision[1:]))
        else:
            self._output_format = "%%.%dg" % (int(precision))

        self.nan = np.array(np.nan, self.format)

        if self.null is None:
            self._null_output = 'NaN'
            self._null_binoutput = self.binoutput(self.nan, False)
            self.filter_array = self._filter_nan
        else:
            self._null_output = self.output(np.asarray(self.null), False)
            self._null_binoutput = self.binoutput(np.asarray(self.null), False)
            self.filter_array = self._filter_null

        if config.get('pedantic'):
            self.parse = self._parse_pedantic
        else:
            self.parse = self._parse_permissive

    def _parse_pedantic(self, value, config={}, pos=None):
        if value.strip() == '':
            return self.null, True
        f = float(value)
        return f, self.is_null(f)

    def _parse_permissive(self, value, config={}, pos=None):
        try:
            f = float(value)
            return f, self.is_null(f)
        except ValueError:
            # IRSA VOTables use the word 'null' to specify empty values,
            # but this is not defined in the VOTable spec.
            if value.strip() != '':
                vo_warn(W30, value, config, pos)
            return self.null, True

    def output(self, value, mask):
        if mask:
            return self._null_output
        if np.isfinite(value):
            return self._output_format % value
        elif np.isnan(value):
            return 'NaN'
        elif np.isposinf(value):
            return '+InF'
        elif np.isneginf(value):
            return '-InF'
        # Should never raise
        vo_raise("Invalid floating point value '%s'" % value)

    def binoutput(self, value, mask):
        if mask:
            return self._null_binoutput

        if value.dtype.byteorder != '>':
            value = value.byteswap()
        return value.tostring()

    def _filter_nan(self, value, mask):
        return np.where(mask, np.nan, value)

    def _filter_null(self, value, mask):
        return np.where(mask, self.null, value)


class Double(FloatingPoint):
    """
    Handles the double datatype.  Double-precision IEEE
    floating-point.
    """
    format = 'f8'


class Float(FloatingPoint):
    """
    Handles the float datatype.  Single-precision IEEE floating-point.
    """
    format = 'f4'


class Integer(Numeric):
    """
    The base class for all the integral datatypes.
    """
    default = 0

    def __init__(self, field, config={}, pos=None):
        Numeric.__init__(self, field, config, pos)

    def parse(self, value, config={}, pos=None):
        mask = False
        if isinstance(value, basestring):
            value = value.lower()
            if value == '':
                warn_or_raise(W49, W49, (), config, pos)
                if self.null is not None:
                    value = self.null
                else:
                    value = self.default
            elif value == 'nan':
                mask = True
                if self.null is None:
                    warn_or_raise(W31, W31, (), config, pos)
                    value = self.default
                else:
                    value = self.null
            elif value.startswith('0x'):
                value = int(value[2:], 16)
            else:
                value = int(value, 10)
        else:
            value = int(value)
        if self.null is not None and value == self.null:
            mask = True
        return value, mask

    def output(self, value, mask):
        if mask:
            if self.null is None:
                warn_or_raise(W31, W31, (), config, pos)
                return 'NaN'
            return str(self.null)
        return str(value)

    def binoutput(self, value, mask):
        if mask:
            if self.null is None:
                vo_raise(W31, (), config, pos)
            else:
                value = self.null
        if value.dtype.byteorder != '>':
            value = value.byteswap()
        return value.tostring()

    def filter_array(self, value, mask):
        if np.any(mask):
            if self.null is not None:
                return np.where(mask, self.null, value)
            else:
                vo_raise(W31, (), config, pos)
        return value


class UnsignedByte(Integer):
    """
    Handles the unsignedByte datatype.  Unsigned 8-bit integer.
    """
    format = 'u1'


class Short(Integer):
    """
    Handles the short datatype.  Signed 16-bit integer.
    """
    format = 'i2'


class Int(Integer):
    """
    Handles the int datatype.  Signed 32-bit integer.
    """
    format = 'i4'


class Long(Integer):
    """
    Handles the long datatype.  Signed 64-bit integer.
    """
    format = 'i8'


class ComplexArrayVarArray(VarArray):
    """
    Handles an array of variable-length arrays of complex numbers.
    """
    def __init__(self, field, base, arraysize, config={}, pos=None):
        VarArray.__init__(self, field, base, arraysize, config, pos)

    def parse(self, value, config={}, pos=None):
        if value.strip() == '':
            return np.array([]), True

        parts = self._splitter(value, config, pos)
        items = self._base._items
        parse_parts = self._base.parse_parts
        if len(parts) % items != 0:
            vo_raise(E02, (items, len(parts)), config, pos)
        result = []
        result_mask = []
        for i in xrange(0, len(parts), items):
            value, mask = parse_parts(parts[i:i + items], config, pos)
            result.append(value)
            result_mask.append(mask)
        return np.array(result), np.array(result_mask, dtype='bool')


class ComplexVarArray(VarArray):
    """
    Handles a variable-length array of complex numbers.
    """
    def __init__(self, field, base, arraysize, config={}, pos=None):
        VarArray.__init__(self, field, base, arraysize, config, pos)

    def parse(self, value, config={}, pos=None):
        if value.strip() == '':
            return np.array([]), True

        parts = self._splitter(value, config, pos)
        parse_parts = self._base.parse_parts
        result = []
        result_mask = []
        for i in xrange(0, len(parts), 2):
            value = [float(x) for x in parts[i:i + 2]]
            value, mask = parse_parts(value, config, pos)
            result.append(value)
            result_mask.append(mask)
        return (np.array(result, dtype=self._base.format),
                np.array(result_mask, dtype='bool'))


class ComplexArray(NumericArray):
    """
    Handles a fixed-size array of complex numbers.
    """
    vararray_type = ComplexArrayVarArray

    def __init__(self, field, base, arraysize, config={}, pos=None):
        NumericArray.__init__(self, field, base, arraysize, config, pos)
        self._items *= 2

    def parse(self, value, config={}, pos=None):
        parts = self._splitter(value, config, pos)
        if parts == ['']:
            parts = []
        return self.parse_parts(parts, config, pos)

    def parse_parts(self, parts, config={}, pos=None):
        if len(parts) != self._items:
            vo_raise(E02, (self._items, len(parts)), config, pos)
        base_parse = self._base.parse_parts
        result = []
        result_mask = []
        for i in xrange(0, self._items, 2):
            value = [float(x) for x in parts[i:i + 2]]
            value, mask = base_parse(value, config, pos)
            result.append(value)
            result_mask.append(mask)
        result = np.array(
            result, dtype=self._base.format).reshape(self._arraysize)
        result_mask = np.array(
            result_mask, dtype='bool').reshape(self._arraysize)
        return result, result_mask


class Complex(FloatingPoint, Array):
    """
    The base class for complex numbers.
    """
    array_type = ComplexArray
    vararray_type = ComplexVarArray
    default = np.nan

    def __init__(self, field, config={}, pos=None):
        FloatingPoint.__init__(self, field, config, pos)
        Array.__init__(self, field, config, pos)

        self._output_format = self._output_format + " " + self._output_format

    def parse(self, value, config={}, pos=None):
        if value.strip() == '':
            return np.nan, True
        splitter = self._splitter
        parts = [float(x) for x in splitter(value, config, pos)]
        if len(parts) != 2:
            vo_raise(E03, (value,), config, pos)
        return self.parse_parts(parts, config, pos)
    _parse_permissive = parse
    _parse_pedantic = parse

    def parse_parts(self, parts, config={}, pos=None):
        value = complex(*parts)
        return value, self.is_null(value)

    def output(self, value, mask):
        if mask:
            if self.null is None:
                return 'NaN'
            else:
                value = self.null
        return self._output_format % (value.real, value.imag)


class FloatComplex(Complex):
    """
    Handle floatComplex datatype.  Pair of single-precision IEEE
    floating-point numbers.
    """
    format = 'c8'


class DoubleComplex(Complex):
    """
    Handle doubleComplex datatype.  Pair of double-precision IEEE
    floating-point numbers.
    """
    format = 'c16'


class BitArray(NumericArray):
    """
    Handles an array of bits.
    """
    vararray_type = ArrayVarArray

    def __init__(self, field, base, arraysize, config={}, pos=None):
        NumericArray.__init__(self, field, base, arraysize, config, pos)

        self._bytes = ((self._items - 1) // 8) + 1

    @staticmethod
    def _splitter_pedantic(value, config={}, pos=None):
        return list(re.sub('\s', '', value))

    @staticmethod
    def _splitter_lax(value, config={}, pos=None):
        if ',' in value:
            vo_warn(W01, (), config, pos)
        return list(re.sub('\s|,', '', value))

    def output(self, value, mask):
        value = np.asarray(value)
        mapping = {False: '0', True: '1'}
        return ''.join(mapping[x] for x in value.flat)

    def binparse(self, read):
        data = read(self._bytes)
        results = []
        for byte in data:
            if not IS_PY3K:
                byte = ord(byte)
            for bit_no in range(7, -1, -1):
                bit = byte & (1 << bit_no)
                bit = (bit != 0)
                results.append(bit)
                if len(results) == self._items:
                    break
            if len(results) == self._items:
                break

        result = np.array(results, dtype='b1').reshape(self._arraysize)
        result_mask = np.zeros(self._arraysize, dtype='b1')
        return result, result_mask

    def binoutput(self, value, mask):
        if np.any(mask):
            vo_warn(W39)

        x = value
        value = value.flat
        bit_no = 7
        byte = 0
        bytes = []
        for v in value:
            if v:
                byte |= 1 << bit_no
            if bit_no == 0:
                bytes.append(byte)
                bit_no = 7
                byte = 0
            else:
                bit_no -= 1
        if bit_no != 7:
            bytes.append(byte)

        assert len(bytes) == self._bytes

        return struct_pack("%sB" % len(bytes), *bytes)


class Bit(Converter):
    """
    Handles the bit datatype.
    """
    format = 'b1'
    array_type = BitArray
    vararray_type = ScalarVarArray
    default = False
    binary_one = bytes(chr(0x8), 'ascii')
    binary_zero = bytes(chr(0), 'ascii')

    def __init__(self, field, config={}, pos=None):
        Converter.__init__(self, field, config, pos)

    def parse(self, value, config={}, pos=None):
        mapping = {'1': True, '0': False}
        if value is False or value.strip() == '':
            warn_or_raise(W49, W49, (), config, pos)
            return False, True
        else:
            try:
                return mapping[value], False
            except KeyError:
                vo_raise(E04, (value,), config, pos)

    def output(self, value, mask):
        if mask:
            vo_warn(W39)

        if value:
            return '1'
        else:
            return '0'

    def binparse(self, read):
        data = read(1)
        return (ord(data) & 0x8) != 0, False

    def binoutput(self, value, mask):
        if mask:
            vo_warn(W39)

        if value:
            return self.binary_one
        return self.binary_zero


class BooleanArray(NumericArray):
    """
    Handles an array of boolean values.
    """
    vararray_type = VarArray

    def __init__(self, field, base, arraysize, config={}, pos=None):
        NumericArray.__init__(self, field, base, arraysize, config, pos)

    def binparse(self, read):
        data = read(self._items)
        binparse = self._base.binparse_value
        result = []
        result_mask = []
        for char in data:
            if not IS_PY3K:
                char = ord(char)
            value, mask = binparse(char)
            result.append(value)
            result_mask.append(mask)
        result = np.array(result, dtype='b1').reshape(
            self._arraysize)
        result_mask = np.array(result_mask, dtype='b1').reshape(
            self._arraysize)
        return result, result_mask

    def binoutput(self, value, mask):
        binoutput = self._base.binoutput
        value = np.asarray(value)
        mask = np.asarray(mask)
        result = [binoutput(x, m)
                  for x, m in np.broadcast(value.flat, mask.flat)]
        return _empty_bytes.join(result)


class Boolean(Converter):
    """
    Handles the boolean datatype.
    """
    format = 'b1'
    array_type = BooleanArray
    vararray_type = VarArray
    default = False
    binary_question_mark = bytes('?', 'ascii')
    binary_true = bytes('T', 'ascii')
    binary_false = bytes('F', 'ascii')

    def __init__(self, field, config={}, pos=None):
        Converter.__init__(self, field, config, pos)

    def parse(self, value, config={}, pos=None):
        if value is False:
            return False, True
        mapping = {'TRUE'  : (True, False),
                   'FALSE' : (False, False),
                   '1'     : (True, False),
                   '0'     : (False, False),
                   'T'     : (True, False),
                   'F'     : (False, False),
                   '\0'    : (False, True),
                   ' '     : (False, True),
                   '?'     : (False, True),
                   ''      : (False, True)}
        try:
            return mapping[value.upper()]
        except KeyError:
            vo_raise(E05, (value,), config, pos)

    def output(self, value, mask):
        if mask:
            return '?'
        if value:
            return 'T'
        return 'F'

    def binparse(self, read):
        value = ord(read(1))
        return self.binparse_value(value)

    _binparse_mapping = {
        ord('T')  : (True, False),
        ord('t')  : (True, False),
        ord('1')  : (True, False),
        ord('F')  : (False, False),
        ord('f')  : (False, False),
        ord('0')  : (False, False),
        ord('\0') : (False, True),
        ord(' ')  : (False, True),
        ord('?')  : (False, True)}

    def binparse_value(self, value):
        try:
            return self._binparse_mapping[value]
        except KeyError:
            vo_raise(E05, (value,))

    def binoutput(self, value, mask):
        if mask:
            return self.binary_question_mark
        if value:
            return self.binary_true
        return self.binary_false


converter_mapping = {
    'double'        : Double,
    'float'         : Float,
    'bit'           : Bit,
    'boolean'       : Boolean,
    'unsignedByte'  : UnsignedByte,
    'short'         : Short,
    'int'           : Int,
    'long'          : Long,
    'floatComplex'  : FloatComplex,
    'doubleComplex' : DoubleComplex,
    'char'          : Char,
    'unicodeChar'   : UnicodeChar }


def get_converter(field, config={}, pos=None):
    """
    Factory function to get an appropriate converter instance for a
    given field.

    Parameters
    ----------
    field : astropy.io.vo.tree.Field

    config : dict, optional
        Parser configuration dictionary

    pos : tuple
        Position in the input XML file.  Used for error messages.

    Returns
    -------
    converter : astropy.io.vo.converters.Converter
    """
    if field.datatype not in converter_mapping:
        vo_raise(E06, (field.datatype, field.ID), config)

    cls = converter_mapping[field.datatype]
    converter = cls(field, config, pos)

    arraysize = field.arraysize

    # With numeric datatypes, special things need to happen for
    # arrays.
    if (field.datatype not in ('char', 'unicodeChar') and
        arraysize is not None):
        if arraysize[-1] == '*':
            arraysize = arraysize[:-1]
            last_x = arraysize.rfind('x')
            if last_x == -1:
                arraysize = ''
            else:
                arraysize = arraysize[:last_x]
            fixed = False
        else:
            fixed = True

        if arraysize != '':
            arraysize = [int(x) for x in arraysize.split("x")]
            arraysize.reverse()
        else:
            arraysize = []

        if arraysize != []:
            converter = converter.array_type(
                field, converter, arraysize, config)

        if not fixed:
            converter = converter.vararray_type(
                field, converter, arraysize, config)

    return converter
