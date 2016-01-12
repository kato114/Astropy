# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
This module contains simple functions for dealing with circular statistics, for
instance, mean, variance, standard deviation, correlation coefficient, and so
on. This module also cover tests of uniformity, e.g the Rayleigh and V0 tests.
The Maximum Likelihood Estimator for the Von Mises distribution along with the
Cramer-Rao Lower Bounds are also implemented. Almost all of the implementations
are based on reference [1], which is also the basis for the R package
'CircStats'.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import numpy as np


__all__ = ['circmean','circvar', 'circmoment', 'circcorrcoef', 'rayleightest',
           'vtest', 'vonmisesmle', 'vonmisescrlb']
__doctest_requires__ = {'vtest': ['scipy.stats']}


def _components(data, w=None, p=1, phi=0.0, axis=None):
    # Utility function for computing the generalized rectangular components
    # of the circular data.
    data = np.asarray(data)
   
    assert type(p) is int
    if w is None:
        w = np.ones(data.shape)
    else:
        assert w.shape == data.shape
    
    C = np.sum(w*np.cos(p*(data-phi)), axis)/np.sum(w, axis)
    S = np.sum(w*np.sin(p*(data-phi)), axis)/np.sum(w, axis)

    return C,S

def _angle(data, w=None, p=1, phi=0.0, axis=None):
    # Utility function for computing the generalized sample mean angle
    C,S = _components(data,w,p,phi,axis)
    theta = np.arctan2(S,C)

    mask = (S == .0)*(C == .0)
    if mask.ndim > 0:
        theta[mask] = np.nan
    return theta

def _length(data, w=None, p=1, phi=0.0, axis=None):
    # Utility function for computing the generalized sample length 
    C,S = _components(data,w,p,phi,axis)
    return np.hypot(S,C)

def circmean(data, w=None, axis=None):
    """ Computes the circular mean angle of an array of circular data.

    Parameters
    ----------
    data : numpy.ndarray
        Array of circular (directional) data measured in radians. 
    w : numpy.ndarray, optional
        In case of grouped data, the i-th element of ``w`` represents a 
        weighting factor for each group such that sum(w,axis) equals the number
        of observations. See [1], remark 1.4, page 22, for detailed
        explanation.
    axis : int, optional
        Axis along which circular means are computed. The default is to compute
        the mean of the flattened array.

    Returns
    -------
    circmean : float
        Circular mean.
    
    References
    ---------
    ..  [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
        Series on Multivariate Analysis, Vol. 5, 2001.
    ..  [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in 
        Circular Statistics (2001)'". 2015.
        <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """

    return _angle(data,w,1,0.0,axis)

def circvar(data, w=None, axis=None):
    """ Computes the circular variance of an array of circular data.

    There are some concepts for defining measures of dispersion for circular 
    data. The variance implemented here is based on the definition given by [1]
    , which is also the same used by the R package 'CircStats'.

    Parameters
    ----------
    data : numpy.ndarray
        Array of circular (directional) data measured in radians. 
    w : numpy.ndarray, optional
        In case of grouped data, the i-th element of ``w`` represents a 
        weighting factor for each group such that sum(w,axis) equals the number
        of observations. See [1], remark 1.4, page 22, for detailed
        explanation.
    axis : int, optional
        Axis along which circular variances are computed. The default is to 
        compute the variance of the flattened array.
   
    Returns
    -------
    circvar : float
        Circular variance.
    
    References
    ---------
    ..  [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
        Series on Multivariate Analysis, Vol. 5, 2001.
    ..  [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in
        Circular Statistics (2001)'". 2015.
        <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """
    return 1.0 - _length(data,w,1,0.0,axis)

def circmoment(data, w=None, p=1, centered=False, axis=None):
    """ Computes the ``p``-th trigonometric circular moment for an array
    of circular data.

    Parameters
    ----------
    data : numpy.ndarray
        Array of circular (directional) data measured in radians. 
    w : numpy.ndarray, optional
        In case of grouped data, the i-th element of ``w`` represents a 
        weighting factor for each group such that sum(w,axis) equals the number
        of observations. See [1], remark 1.4, page 22, for detailed
        explanation.
    p : int, optional
        Order of the circular moment. Must be integer valued. 
    centered : Boolean, optinal
        If ``True``, central circular moments are computed. Default value is 
        ``False``.
    axis : int, optional
        Axis along which circular moments are computed. The default is to 
        compute the circular moment of the flattened array.
   
    Returns
    -------
    circmoment: np.ndarray
        The first are second elements correspond to the direction and length of
        the ``p``-th circular moment.
    
    References
    ---------
    ..  [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
        Series on Multivariate Analysis, Vol. 5, 2001.
    ..  [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in 
        Circular Statistics (2001)'". 2015.
        <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """
    
    phi = 0.0
    if centered:
        phi = circmean(data,w,axis)

    return _angle(data,w,p,phi,axis), _length(data,w,p,phi,axis)

def circcorrcoef(alpha, beta, w_alpha=None, w_beta=None, ax_alpha=None, 
                 ax_beta=None):
    """ Computes the circular correlation coefficient between two array of
    circular data.

    Parameters
    ----------
    alpha : numpy.ndarray
        Array of circular (directional) data measured in radians. 
    beta : numpy.ndarray
        Array of circular (directional) data measured in radians. 
    w_alpha : numpy.ndarray, optional
        In case of grouped data, the i-th element of ``w_alpha`` represents a 
        weighting factor for each group such that sum(w,axis) equals the number
        of observations. See [1], remark 1.4, page 22, for detailed
        explanation.
    w_beta : numpy.ndarray, optional
        See description of ``w_alpha``.
    ax_alpha : int, optional
        Axis along which circular correlation coefficients are computed. 
        The default is the compute the circular correlation coefficient of the 
        flattened array.
    ax_ beta : int, optional
        See description of ``ax_alpha``

    Returns
    -------
    rho : float
        Circular correlation coefficient
    
    References
    ---------
    ..  [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
        Series on Multivariate Analysis, Vol. 5, 2001.
    ..  [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in 
        Circular Statistics (2001)'". 2015.
        <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """

    alpha = np.asarray(alpha)
    beta = np.asarray(beta)

    assert np.size(alpha, axis=ax_alpha) == np.size(beta, axis=ax_beta)

    sin_a = np.sin(alpha - circmean(alpha,w_alpha,ax_alpha))
    sin_b = np.sin(beta - circmean(beta,w_beta,ax_beta))
    rho = np.sum(sin_a*sin_b)/np.sqrt(np.sum(sin_a*sin_a)*np.sum(sin_b*sin_b))

    return rho

def rayleightest(data, w=None, axis=None):
    """ Performs the Rayleigh test of uniformity.

    This test is  used to indentify a non-uniform distribution, i.e. it is
    designed for detecting an unimodal deviation from uniformity. More
    precisely, it assumes the following hypotheses:
        - H0 (null hypothesis): The population is distributed uniformly around
        the circle.
        - H1 (alternative hypothesis): The population is not distributed
        uniformly around the circle.
    Small p-values suggest to reject the null hypothesis.

    Parameters
    ----------
    data : numpy.ndarray
        Array of circular (directional) data measured in radians. 
    w : numpy.ndarray, optional
        In case of grouped data, the i-th element of ``w`` represents a 
        weighting factor for each group such that sum(w,axis) equals the number
        of observations. See [1], remark 1.4, page 22, for detailed
        explanation.
    axis : int, optional
        Axis along which the Rayleigh test will be performed.
    
    Returns
    -------
    p-value : float
        p-value.
    
    References
    ---------
    ..  [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
        Series on Multivariate Analysis, Vol. 5, 2001.
    ..  [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in 
        Circular Statistics (2001)'". 2015.
        <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """

    data = np.asarray(data)
    n = np.size(data,axis=axis) 
    Rbar = _length(data,w,1,0.0,axis)
    z = n*Rbar*Rbar 
    
    tmp = 1.0
    if(n < 50):
        tmp = 1.0 + (2.0*z - z*z)/(4.0*n) - (24.0*z - 132.0*z**2.0 +
                76.0*z**3.0 - 9.0*z**4.0)/(288.0*n*n)
    
    p_value = np.exp(-z)*tmp 
    return p_value
    
def vtest(data, w=None, mu=0.0, axis=None):
    """ Performs the Rayleigh test of uniformity where the alternative
    hypothesis H1 is assumed to have a known mean angle ``mu``.
    
    Parameters
    ----------
    data : numpy.ndarray
        Array of circular (directional) data measured in radians. 
    w : numpy.ndarray, optional
        In case of grouped data, the i-th element of ``w`` represents a 
        weighting factor for each group such that sum(w,axis) equals the number
        of observations. See [1], remark 1.4, page 22, for detailed
        explanation.
    mu : float, optional
        Assumed known mean angle.
    axis : int, optional
        Axis along which the V test will be performed.
    
    Returns
    -------
    p-value : float
        p-value.
    
    References
    ---------
    ..  [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
        Series on Multivariate Analysis, Vol. 5, 2001.
    ..  [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in 
        Circular Statistics (2001)'". 2015.
        <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """

    from scipy.stats import norm
    
    if w is None:
        w = np.ones(data.shape)
    else:
        assert w.shape == data.shape

    data = np.asarray(data)
    n = np.size(data,axis=axis) 

    R0bar = np.sum(w*np.cos(data-mu),axis)/np.sum(w, axis)
    z = np.sqrt(2.0*n)*R0bar

    pz = norm.cdf(z)
    fz = norm.pdf(z)

    p_value = 1 - pz + fz*((3*z - z**3)/(16.0*n) + (15*z + 305*z**3 - 125*z**5
        + 9*z**7)/(4608.0*n*n))
    return p_value

def _A1inv(x):
    # Utility function used to compute the inverse of the ratio between the 
    # modified Bessel function of first kind of orders one and zero.
    import scipy.optimize as opt
    import scipy.special as sps

    invfunc = lambda y: x*sps.ive(0.0,y) - sps.ive(1.0,y)
    kappa = opt.brentq(invfunc,0.0,100.0)
    return kappa

def _A1inv1(x):
    # Approximation for _A1inv(x) according R Package 'CircStats'
    if(x >= 0 and x < 0.53):
        return 2.0*x + x*x*x + (5.0*x**5)/6.0
    elif x < 0.85:
        return -0.4 + 1.39*x + 0.43/(1.0 - x)
    else:
        return 1.0/(x*x*x - 4.0*x*x + 3.0*x)

def vonmisesmle(data, axis=None):
    """ Computes the Maximum Likelihood Estimator (MLE) for the parameters of 
    the von Mises distribution. 

    Parameters
    ----------
    data : numpy.ndarray
        Array of circular (directional) data measured in radians.  
    axis : int, optional
        Axis along which the mle will be computed.
    
    Returns
    -------
    mu : float
        the mean (aka location parameter).
    kappa : float
        the concentration parameter.
    
    References
    ---------
    ..  [1] S. R. Jammalamadaka, A. SenGupta. "Topics in Circular Statistics".
        Series on Multivariate Analysis, Vol. 5, 2001.
    ..  [2] C. Agostinelli, U. Lund. "Circular Statistics from 'Topics in 
        Circular Statistics (2001)'". 2015.
        <https://cran.r-project.org/web/packages/CircStats/CircStats.pdf>
    """

    data = np.asarray(data)
    mu = circmean(data, axis=None)
    kappa = _A1inv1(np.mean(np.cos(data - mu), axis))
    return mu, kappa

def _A1(x):
    # Utility function that computes the ratio between the modified Bessel 
    # function of first kind of orders one and zero.

    import scipy.special as sps
    return sps.ive(1.0,x)/sps.ive(0.0,x)

def _A1deriv(x):
    # Derivative of A1(x)
    return 1.0 - A1(x)/x - A1(x)*A1(x)

def vonmisescrlb(data, axis=None):
    """ Computes the Cramer-Rao Lower Bound (CRLB) for the parameters of the 
    von Mises distribution.
    
    Theoreticaly, the Maximum Likelihood Estimator attains the CRLB.
    
    Parameters
    ----------
    data : numpy.ndarray
        Array of circular (directional) data measured in radians.  
    axis : int, optional
        Axis along which the mle will be computed.
    
    Returns
    -------
    crlb : numpy.array
        The first and second elements corresponds to the CRLB of the mean and
        the concentration parameter, respectively.
    
    References
    ---------
    ..  [1] D. L. Dowe et. al.. "Bayesian Estimation of the von Mises 
        Concentration Parameter". Proceedings of the Fifteenth International
        Workshop on Maximum Entropy and Bayesian Methods. doi=10.1.1.48.5719
    """

    n = np.size(data, axis)
    mu, kappa = vonmisesmle(data, axis)

    det = kappa*n*n*_A1(kappa)*_A1deriv(kappa)
    crlb = np.array([n*_A1deriv(kappa), kappa*n*_A1(kappa)])/det
    return crlb
