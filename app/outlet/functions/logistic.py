#!/usr/bin/env python

"""A standard logistic curve fitting function

"""
from scipy.optimize import fsolve
from outlet import FunctionRegistry
import pprint

from datetime import datetime
from tempfile import NamedTemporaryFile
from outlet import ParserRegistry

from io import BytesIO
import time

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
        print("v_max guess")
        pprint(vmax_guess)

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

class ICPRobustLogistic3(FunctionRegistry):
    name = 'ICP_robust_logistic3'
    description = 'ICP (Robust) 3-parameter logistic'
    loss = 'soft_l1'

    def __init__(self, *args, **kwargs):
        self.vmax_multiplier = .95
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
        
        Vmax = params[0]
        Ki = params[1]
        ICP1000 = -(1000*Ki)/(1000-Vmax)
        # return Vmax / (1 + e**(-Ki*concs))
        # return (Ki*((Vmax-concs)/Vmax))*concs
        # pprint.pprint(Vmax * ((concs / (Ki + concs))))
        fit = Vmax * (concs / (Ki + concs))
        #print("Fit:")
        #print(fit)
        #print("Vmax:")
        #print(Vmax)
        
        return Vmax * (concs / (Ki + concs))
      
    def labels(self, params):

        print("params-")
        pprint.pprint(params)
        
        Vmax = params[0]
        Ki = params[1]
        ICP1000 = -(1000*(params[1]))/(1000-(params[0]))

        print("ICP1000=")
        print(ICP1000)
        
        return {   
            'ICP1000': f'{ICP1000:.10g}',
        #    'Vmax': f'{Vmax:.0f}',
        #    'IC50': f'{Ki:.3g}',
        }
        
class ICP_Logistic3(ICPRobustLogistic3):
    name = 'ICP_logistic3'
    description = 'linear 3-parameter logistic'
    loss = 'linear'

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

    #jm=JasprModel()
    #    for experiment in jm.experiment_list:
    #        pprint.pprint(experiment)

        return {
            'titer': f'{titer:.0f}',
            'h': f'{h:.2f}',
            'Vmax': f'{Vmax:.0f}',
            'IC50': f'{Ki:.3g}',
        }
    
    def model_convergence(self, params):
     
        jm=JasprModel()
    
        output=BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')

        headerList = ["Virus"]
        for sample in jm.sample_list:
            headerList.append(sample)
        
        rowList = []

        for experiment in jm.experiment_list:
            rowAdd = []
            rowAdd.append(experiment)
            pprint.pprint(experiment)

            for sample in jm.sample_list:
                print("sample:")
                pprint.pprint(sample)
                pprint.pprint (jm.experiments[experiment]['results'])
                rowAdd.append(jm.experiments[experiment]['results'][jm.curr_function][sample])

            rowList.append(rowAdd)

        df = pd.DataFrame(rowList, columns=headerList)
        print(df)
        df.to_excel(writer, sheet_name="Full_Report", index=False)

        writer.close()

        output.seek(0)

        convergence = make_response(send_file(output, attachment_filename='Full_Report_' + str(datetime.now().strftime('%Y_%m_%d')) +'.xlsx', as_attachment=True))
        response.headers['cache-control'] = 'no-cache'
        return convergence    


    

class RobustLogistic4(Logistic4):
    name = 'robust_logistic4'
    description = '(Robust) 4-parameter logistic'
    loss = 'soft_l1'
