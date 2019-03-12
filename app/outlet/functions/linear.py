#!/usr/bin/env python

from outlet import FunctionRegistry

class LinearRegression(FunctionRegistry):
    # regression line
    name = 'linear'
    description = 'Linear'

    def _guess_params(self, data, concs):
        """Initalial guesses for function parameters"""
        slope = (max(data)-min(data))/(max(concs)-min(concs))
        intercept = 0
        yield (slope, intercept)

    def _calculate(self, params, concs):
        """evaluate"""
        slope = params[0]
        intercept = params[1]
        print(params)
        self.labels = {'slope': slope, 'intercept': intercept}
        return slope * concs + intercept
