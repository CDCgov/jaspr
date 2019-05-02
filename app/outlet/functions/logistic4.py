#!/usr/bin/env python

from outlet import FunctionRegistry


class Logistic4(FunctionRegistry):
    name = 'logistic4'
    description = '4-parameter logistic'

    def _guess_params(self, concs, data):
        """Fit a non-linear inhibition curve using least squares."""
        vmax_guess = max(data) * 1.3
        h_guess = 1.0
        for d, ki_guess in zip(data, concs):
            if d < vmax_guess / 2:
                yield (vmax_guess, ki_guess, h_guess)
        yield (vmax_guess, concs[-1]/4, h_guess)

    def _calculate(self, params, concs):
        """Evaluate rate as a function of concentration

        * Vmax is the reaction rate when no inhibitor is present.

        * Ki is the equilibrium constant for the interation between the
          inhibitor and the enzyme.  It is equal to the concentration of
          inhibitor where rate/Vmax = 1/2.  This is also known as IC50.

        * h is the Hill coefficient (a slope correction factor)

        """
        Vmax = params[0]
        Ki = params[1]
        h = params[2]

        return Vmax * (1 - (1 /(1 + pow(concs/Ki, -h))))

    def labels(self, params):
        Vmax = params[0]
        Ki = params[1]
        h = params[2]
        titer = 1 / Ki

        return {
            'titer': f'{titer:.0f}',
            'h': f'{h:.2f}',
            'Vmax': f'{Vmax:.0f}',
            'IC50': f'{Ki:.3g}',
        }
