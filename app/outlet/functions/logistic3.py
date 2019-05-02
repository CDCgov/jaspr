#!/usr/bin/env python

from outlet import FunctionRegistry


class Logistic3(FunctionRegistry):
    name = 'logistic3'
    description = '3-parameter logistic'

    def _guess_params(self, concs, data):
        """Fit a non-linear inhibition curve using least squares."""
        vmax_guess = max(data)
        for d, ki_guess in zip(data, concs):
            if d < vmax_guess / 2:
                yield (vmax_guess, ki_guess)
        yield (vmax_guess, concs[-1]/4)

    def _calculate(self, params, concs):
        """Evaluate rate as a function of concentration

        * Vmax is the reaction rate when no inhibitor is present.

        * Ki is the equilibrium constant for the interation between the
          inhibitor and the enzyme.  It is equal to the concentration of
          inhibitor where rate/Vmax = 1/2.  This is also known as IC50.

        """
        Vmax =  params[0]
        Ki = params[1]
        self.labels = {'IC50': Ki, 'titer': 1 / Ki}
        return Vmax * (1 - (concs / (Ki + concs)))

    def labels(self, params):
        Vmax = params[0]
        Ki = params[1]
        titer = 1 / Ki

        return {
            'titer': f'{titer:.0f}',
            'Vmax': f'{Vmax:.0f}',
            'IC50': f'{Ki:.3g}',
        }
