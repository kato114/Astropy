# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Distribution class and associated machinery.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np

from .. import visualization

__all__ = ['Distribution']


class Distribution:
    """
    A scalar value or array values with associated uncertainty distribution.

    This object will take its exact type from whatever the ``samples`` argument
    is. In general this is expected to be an `~astropy.units.Quantity` or
    `numpy.ndarray`, although anything compatible with `nump.asanyarray` is
    possible.

    Parameters
    ----------
    samples : array-like
        The distribution, with sampling along the *leading* axis. If 1D, the
        sole dimension is used as the sampling axis (i.e., it is a scalar
        distribution).
    """

    def __new__(cls, samples):
        if isinstance(samples, Distribution):
            samples = samples.distribution
        else:
            samples = np.asanyarray(samples, order='C')
        if samples.shape == ():
            raise TypeError('Attempted to initialize a Distribution with a scalar')

        new_dtype = np.dtype({'names': ['samples'],
                              'formats': [(samples.dtype, (samples.shape[-1],))]})
        samples_cls = type(samples)
        if not issubclass(samples_cls, Distribution):
            # Probably should have a dict on the class with these, so
            # we don't create new classes needlessly.
            new_name = samples_cls.__name__ + cls.__name__
            new_cls = type(new_name, (cls, samples_cls),
                           {'_samples_cls': samples_cls})
        self = samples.view(dtype=new_dtype, type=new_cls)
        # Get rid of trailing dimension of 1.
        self.shape = samples.shape[:-1]
        return self

    @property
    def distribution(self):
        return self['samples']

    def __getitem__(self, item):
        result = super().__getitem__(item)
        if item == 'samples':
            return super(Distribution, result).view(self._samples_cls)
        else:
            return Distribution.__new__(self.__class__, result['samples'])

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        converted = []
        outputs = kwargs.pop('out', None)
        if outputs:
            kwargs['out'] = tuple((output.distribution if
                                   isinstance(output, Distribution)
                                   else output) for output in outputs)
        if method in {'reduce', 'accumulate', 'reduceat'}:
            axis = kwargs.get('axis', None)
            if axis is None:
                assert isinstance(inputs[0], Distribution)
                kwargs['axis'] = tuple(range(inputs[0].ndim))

        for input_ in inputs:
            if isinstance(input_, Distribution):
                converted.append(input_.distribution)
            else:
                shape = getattr(input_, 'shape', ())
                if shape:
                    converted.append(input_[..., np.newaxis])
                else:
                    converted.append(input_)

        results = getattr(ufunc, method)(*converted, **kwargs)

        if not isinstance(results, tuple):
            results = (results,)
        if outputs is None:
            outputs = (None,) * len(results)

        finals = []
        for result, output in zip(results, outputs):
            if output is not None:
                finals.append(output)
            else:
                if getattr(result, 'shape', False):
                    finals.append(Distribution(result))
                else:
                    finals.append(result)

        return finals if len(finals) > 1 else finals[0]

    # Override view so that we stay a Distribution version of the new type.
    def view(self, dtype=None, type=None):
        if type is None:
            if issubclass(dtype, np.ndarray):
                type = dtype
                dtype = None
            else:
                raise ValueError('Cannot set just dtype for a Distribution.')

        result = self.distribution.view(dtype, type)
        return Distribution(result)

    def __repr__(self):
        reprarr = repr(self.distribution)
        if reprarr.endswith('>'):
            firstspace = reprarr.find(' ')
            reprarr = reprarr[firstspace+1:-1]  # :-1] removes the ending '>'
            return '<{} {} with n_samples={}>'.format(self.__class__.__name__,
                                                      reprarr, self.n_samples)
        else: # numpy array-like
            firstparen = reprarr.find('(')
            reprarr = reprarr[firstparen:]
            return '{}{} with n_samples={}'.format(self.__class__.__name__,
                                                    reprarr, self.n_samples)
            return reprarr

    def __str__(self):
        distrstr = str(self.distribution)
        toadd = ' with n_samples={}'.format(self.n_samples)
        return distrstr + toadd

    def _repr_latex_(self):
        superlatex = self.distribution._repr_latex_()
        toadd = r', \; n_{{\rm samp}}={}'.format(self.n_samples)
        return superlatex[:-1] + toadd + superlatex[-1]

    @property
    def n_samples(self):
        """
        The number of samples of this distribution.  A single `int`.
        """
        return self.dtype['samples'].shape[0]

    @property
    def pdf_mean(self):
        """
        The mean of this distribution.
        """
        return self.distribution.mean(axis=-1)

    @property
    def pdf_std(self):
        """
        The standard deviation of this distribution.
        """
        return self.distribution.std(axis=-1)

    @property
    def pdf_var(self):
        """
        The variance of this distribution.
        """
        return self.distribution.var(axis=-1)

    @property
    def pdf_median(self):
        """
        The median of this distribution.
        """
        return np.median(self.distribution, axis=-1)

    @property
    def pdf_mad(self):
        """
        The median absolute deviation of this distribution.
        """
        return np.abs(self - self.pdf_median).pdf_median

    # we set this by hand because the symbolic expression (below) requires scipy
    # _smad_scale_factor = 1 / scipy.stats.norm.ppf(0.75)
    _smad_scale_factor = 1.48260221850560203193936104071326553821563720703125

    @property
    def pdf_smad(self):
        """
        The median absolute deviation of this distribution rescaled to match the
        standard deviation for a normal distribution.
        """
        return self.pdf_mad * self._smad_scale_factor

    def pdf_percentiles(self, perc, **kwargs):
        """
        Compute percentiles of this Distribution.

        Parameters
        ----------
        perc : float or array of floats
            The desired  precentiles of the distribution (i.e., on [0,100]).
        kwargs
            Additional keywords are passed into `numpy.percentile`.

        Returns
        -------
        percs : `~astropy.units.Quantity`
            The ``fracs`` percentiles of this distribution.
        """
        perc = np.percentile(self.distribution, perc, axis=-1)
        # numpy.percentile strips units for unclear reasons, so we have to make
        # a new object with units
        if hasattr(self.distribution, '_new_view'):
            return self.distribution._new_view(perc)
        else:
            return perc

    def hist(self, maxtoshow=10, **kwargs):
        """
        Use `astropy.visualization.hist` (which uses matplotlib's ``hist``
        function) to visualize this distribution.  For N-D distributions, the
        array is flattened following standard numpy rules, and the distributions
        are shown as separate histograms for each element.

        Parameters
        ----------
        maxtoshow : int or `None`
            The maximum number of non-sampled distribution elements to show.
            I.e., the dimensions reflected in this object's ``shape``.  If
            `None`, there will be no limit, but this may overwhelm matplotlib if
            the distribution is large.
        Additional keywords are passed into `astropy.visualization.hist`
        """
        # FIXME: not adjusted to new structure!!
        labelset = 'label' in kwargs
        scalar_distr = len(self.shape) == 1
        if scalar_distr:
            reshaped = [self]
        else:
            reshaped = self.reshape(self.n_samples, self.size//self.n_samples).T

        hists = []
        for i, dat in enumerate(reshaped):
            if i >= maxtoshow:
                break
            if (not scalar_distr) and (not labelset):
                if len(self.shape) == 2:
                    idxstr = str(i)
                else:
                    idxstr = str(np.unravel_index(i, self.shape[1:]))
                kwargs['label'] = 'Distr ' + idxstr
            hists.append(visualization.hist(dat, **kwargs))
        return hists
