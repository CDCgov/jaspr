#!/usr/bin/env python

from outlet import FunctionRegistry


class LinearRegression(FunctionRegistry):
    # regression line
    name = 'LinearRegression'
    description = 'Simple Linear Regression'

    def _guess_params(self, data, concs):
        """Fit a linear curve using least squares."""
        slope = (max(data)-min(data))/(max(concs)-min(concs))
        intercept = 0
        yield (slope, intercept)

    def _calculate(self, params, concs):
        """Evaluate
        """
        slope =  params[0]
        intercept = params[1]
        return slope*concs + intercept
