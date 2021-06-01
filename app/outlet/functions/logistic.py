#!/usr/bin/env python

"""A standard logistic curve fitting function

"""

from outlet import FunctionRegistry


class Logistic3(FunctionRegistry):
    name = 'logistic3'
    description = '3-parameter logistic'
    loss = 'linear'

    def __init__(self, *args, **kwargs):
        self.vmax_multiplier = 0.8
        super().__init__(*args, **kwargs)

    def _guess_params(self, concs, data):
        """Generate intial guesses for fit params"""
        vmax_guess = max(data) * self.vmax_multiplier
        for d, ki_guess in zip(data, concs):
            if d < vmax_guess:
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


class RobustLogistic3(Logistic3):
    name = 'robust_logistic3'
    description = '(Robust) 3-parameter logistic'
    loss = 'soft_l1'


class Logistic4(Logistic3):
    name = 'logistic4'
    description = '4-parameter logistic'
    loss = 'linear'

    def _guess_params(self, concs, data):
        """Generate initial guesses for fit params"""
        h_guess = 1.0
        for vmax_guess, ki_guess in super()._guess_params(concs, data):
            yield(vmax_guess, ki_guess, h_guess)

    def _calculate(self, params, concs):
        """Evaluate rate as a function of concentration

        * Vmax is the reaction rate when no inhibitor is present.

        * Ki is the equilibrium constant for the interation between the
          inhibitor and the enzyme.  It is equal to the concentration of
          inhibitor where rate/Vmax = 1/2.  This is also known as IC50.

        * h is the Hill coefficient - a slope correction factor, and
          measure of cooperativity

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


class RobustLogistic4(Logistic4):
    name = 'robust_logistic4'
    description = '(Robust) 4-parameter logistic'
    loss = 'soft_l1'
