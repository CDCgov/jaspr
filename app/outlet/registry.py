#!/usr/bin/env python
# file outlet/registry.py

"""Plugin framework for use with jaspr

Based on http://martyalchin.com/2008/jan/10/simple-plugin-framework/

Plugins are dynamically discovered, imported, and registered with a
mount point.  New plugins can be implemented with minimal code as long
as they follow the documented pattern.

"""

from scipy.optimize import least_squares
from numpy import inf


class PluginMount(type):
    """Metaclass for classes that are plugin mountpoints"""

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # this is the mount point, set up a registry
            cls.plugins = {}
        else:
            # this is a plugin, register it
            cls.plugins[cls.name] = cls


class FunctionRegistry(object, metaclass=PluginMount):
    """Registry of known funcitons to use for curve fits

    Plugins implementing functions must provide:

        Attributes:
         * name        - A short, unique name of the function being defined
         * description - A longer description of the function describing
                         its use

        Functions:
         * _guess_params(data_array, independent_array):
               # a generator that returns initial guesses for the parameters
               ...
               yield [param1, param2, ..., ]

         * _calculate([param1, param2, ..., ], independent_array):
               # a function that calculates an array of dependent values
               # based on a list of parameters and an array of
               # independent values
               ...
               return dependent_array

    """

    def _residuals(self, params, independent_array, data_array):
        """Calculate the distance between each observed and calculated value"""
        return data_array - self._calculate(params, independent_array)

    def __call__(self, x_data, y_data, **kwargs):
        """Fit the function to the data

        Iterate through initial guesses for the fitting parameters until
        initial guesses are exhausted, or the least squares converges

        least_sqares uses Trust Region Reflective (TRF) algorithm, as
        opposed to Levenberg-Marquardt (LM) used previously.  The
        soft_l1 loss func minimizes influence of outliers.  There are
        options to go to constrained fits as needed.

        Loss options:
            - linear: standard least squares
            - soft_l1: smooth approximation of absolute value (try this!)
            - huber: like soft_l1
            - cauchy: signifcantly discounts outliers
            - arctan: similar to cauchy

        """
        for params in self._guess_params(x_data, y_data):
            fit = least_squares(self._residuals, params,
                    loss=self.loss, x_scale='jac', f_scale=0.1,
                    verbose=2, args=(x_data, y_data))

            #fit = least_squares(self._residuals, params, method='lm',
            #        verbose=2, args=(x_data, y_data))

            if fit.success:
                # indicates we've converged, stop guessing
                print (fit.fun)
                break
        return fit


class ParserRegistry(object, metaclass=PluginMount):
    """Registry of known parsers for various data formats

    Plugins implementing importers must provide:

        Attributes:
         * name        - A short, unique name of the function being defined
         * description - A longer description of the function describing
                         its use

        Functions:
            __call__():
                # returns a JASPR data structure

    """

    pass
