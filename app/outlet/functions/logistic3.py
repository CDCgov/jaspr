#!/usr/bin/env python

from outlet import FunctionRegistry


class Logistic3(FunctionRegistry):
    name = 'logistic3'
    description = '3-parameter logistic'

    def _guess_params(self, data, concs):
        """Fit a non-linear inhibition curve using least squares."""
        vmax_guess = max(data)
        for index, ki_guess in enumerate(concs):
            yield (vmax_guess, ki_guess)

    def _calculate(self, params, concs):
        """Evaluate rate as a function of concentration

            rate = Vmax * (1 - (c / (Ki + c)))

        * Vmax is the reaction rate when no inhibitor is present.

        * Ki is the equilibrium constant for the interation between the
          inhibitor and the enzyme.  It is equal to the concentration of
          inhibitor where rate/Vmax = 1/2.  This is also known as IC50.

        * c is the concentration of inhibitor.

        """
        Vmax =  params[0]
        Ki = params[1]
        self.labels = {"IC50": Ki}
        return Vmax * (1 - (concs / (Ki + concs)))

    def _labels(self):
        return self.labels
