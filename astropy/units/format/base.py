# Licensed under a 3-clause BSD style license - see LICENSE.rst

class _FormatterMeta(type):
    registry = {}

    def __new__(mcls, name, bases, members):
        if 'name' in members:
            formatter_name = members['name'].lower()
        else:
            formatter_name = members['name'] = name.lower()

        cls = super().__new__(mcls, name, bases, members)

        mcls.registry[formatter_name] = cls

        return cls


class Base(metaclass=_FormatterMeta):
    """
    The abstract base class of all unit formats.
    """

    def __new__(cls, *args, **kwargs):
        # This __new__ is to make it clear that there is no reason to
        # instantiate a Formatter--if you try to you'll just get back the
        # class
        return cls

    @classmethod
    def parse(cls, s):
        """
        Convert a string to a unit object.
        """

        raise NotImplementedError(
            f"Can not parse with {cls.__name__} format")

    @classmethod
    def to_string(cls, u):
        """
        Convert a unit object to a string.
        """

        raise NotImplementedError(
            f"Can not output in {cls.__name__} format")
