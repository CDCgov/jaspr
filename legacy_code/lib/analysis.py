#!/usr/bin/env python
# file jaspr/lib/analysis.py

"""JASPR utilities for running analysis."""

# Python 2.6 features
from __future__ import with_statement

# Python library imports
import sys
import csv

# PIL fix
#from PIL import Image
import PIL.Image
sys.modules['Image'] = PIL.Image

# 3rd-party package import
import wx
import matplotlib
import numpy as nx
from scipy.optimize import leastsq
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter

# local imports
sys.path.extend(['.', 'lib'])
from easy_xls import read_excel


def inhibition(p, c):
    """Evaluate rate as a function of concentration

    rate = Vmax * (1 - (c / (Ki + c)))

    * Vmax is the reaction rate when no inhibitor is present.

    * Ki is the equilibrium constant for the interation between the
      inhibitor and the enzyme.  It is equal to the concentration of
      inhibitor where rate/Vmax = 1/2.  This is also known as IC50.

    * c is the concentration of inhibitor.

    """
    vmax =  p[0]
    ki = p[1]
    return vmax*(1-(c/(ki+c)))


def residuals(p, data, c):
    """Calculate y-distances of points to a fit line"""
    return data - inhibition(p, c)


def fit_curve(concs, corrected):
    """Fit a non-linear inhibition curve using least squares."""
    vmax_guess = max(corrected)
    for index, value in enumerate(corrected):
        if value > (vmax_guess / 2):
            break
    while index >= 0:
        ki_guess = concs[index]
        if ki_guess == 0:
            index = index - 1
            continue
        param_guess = (vmax_guess, ki_guess)
        fit = leastsq(residuals, param_guess, args=(corrected, concs))
        if 0 < fit[1] < 5:
            break
        index = index - 1
    return fit


def format_ic50(ic50):
    if 1000 > ic50 >= .2:
        ic50_str = '%.2f' % ic50
    else:
        ic50_str = '%.2e' % ic50
        mantissa, exponent = ic50_str.split('e')
        ic50_str = '%se%s' % (mantissa, int(exponent))
    return ic50_str


class JasprAnalysisManagerError(Exception):
    """Error class for all data manipulation errors"""
    pass


class JasprAnalysisManager(object):
    """Run analysis for a given experiment"""

    def __init__(self, experiment, drugs, ids, raw_data, reverse_axis):
        self.orientation = experiment['orientation']
        self.reverse_dilution = experiment['reverse_dilution']
        self.detection_method = experiment['detection_method']
        self.detection_units = experiment['detection_units']
        self.drugs = drugs
        self.conc_unit = experiment['conc_unit']
        self.fitting_concs = nx.array(experiment['concs'])
        self.graphing_concs = self.fitting_concs.copy()
        self.graphing_concs[-1] = experiment['graph_zero']
        self.ids = ids
        self.raw_data = raw_data
        self.reverse_axis = reverse_axis

        self._check_sanity()
        self.ids = [id for id in self.ids if id[0] != '']
        self.clean_data = self._collate_data()

    def _check_sanity(self):
        """Ensure that our experiment configuration works"""
        if not self.fitting_concs[-1] == nx.float_(0):
            msg = 'Experiment dilution series does not end with 0'
            raise JasprAnalysisManagerError(msg)
        if (self.orientation == 'row' and \
                len(self.fitting_concs) > 11) or \
                (self.orientation == 'col' and \
                len(self.fitting_concs) > 8):
            msg = 'Dilution series is too long for plate orientation'
            raise JasprAnalysisManagerError(msg)
        if ('', '', ) in self.ids:
            if self.orientation == 'row':
                msg = 'Key should not contain "blank" for row-based ' \
                        'experiments'
                raise JasprAnalysisManagerError(msg)
            msg = 'Not all plates contain "blank" columns ' \
                    'in the last column'
            for col_index in range(0, len(self.ids), 12):
                try:
                    if not ('', '', ) == self.ids[col_index+11]:
                        raise JasprAnalysisManagerError(msg)
                except IndexError:
                    if not self.ids[-1] == ('', '', ):
                        raise JasprAnalysisManagerError(msg)

    def _collate_col_data(self):
        """Compile data from a row-based experiment"""
        plate = 0
        batch = -1
        clean_data = dict((id[0], dict((drug, {}) for drug in self.drugs))
                for id in self.ids)
        rows = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        while True:
            drug_index = plate % len(self.drugs)
            drug = self.drugs[drug_index]
            plate = plate + 1
            if drug_index == 0:
                batch = batch + 1
            id_batch = self.ids[batch*11:batch*11+11]
            if not id_batch:
                return clean_data
            blank_col = len(id_batch) + 1
            background = nx.array([self.raw_data[(plate, row, blank_col)]
                    for row in rows]).astype('float')
            avg_bkg = background.mean()
            stdev_bkg = background.std()
            for col, (current_id, strain_name) in zip(range(1, 13), id_batch):
                raw = nx.array([self.raw_data[(plate, row, col)]
                        for row in rows[:len(self.fitting_concs)]]
                        ).astype('float')
                if self.reverse_dilution:
                    raw = raw[::-1]
                corrected = raw - avg_bkg
                result = fit_curve(self.fitting_concs, corrected)
                vmax, ic50 = result[0]
                clean_data[current_id][drug]['strain_name'] = strain_name
                clean_data[current_id][drug]['values'] = raw
                clean_data[current_id][drug]['corrected'] = corrected
                clean_data[current_id][drug]['vmax'] = vmax
                clean_data[current_id][drug]['ic50'] = ic50
                clean_data[current_id][drug]['ic50_str'] = format_ic50(ic50)
                clean_data[current_id][drug]['result'] = result[0]
                clean_data[current_id][drug]['sbr'] = corrected[-1] / avg_bkg
                clean_data[current_id][drug]['snr'] = corrected[-1] / stdev_bkg
                clean_data[current_id][drug]['bkg'] = avg_bkg
                clean_data[current_id][drug]['stdev'] = stdev_bkg
            
    def _collate_row_data(self):
        """Compile data from a row-based experiment"""
        # get the blank column
        # we assume that there will be a full blank column on every plate
        blank_col = len(self.fitting_concs) + 1
        plate = 0
        batch = -1
        clean_data = dict((id[0], dict((drug, {}) for drug in self.drugs))
                for id in self.ids)
        rows = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        while True:
            drug_index = plate % len(self.drugs)
            drug = self.drugs[drug_index]
            plate = plate + 1
            if drug_index == 0:
                batch = batch + 1
            id_batch = self.ids[batch*8:batch*8+8]
            if not id_batch:
                return clean_data
            # calcuate background for the plate
            background = nx.array([self.raw_data[(plate, row, blank_col)]
                    for row in rows]).astype('float')
            avg_bkg = background.mean()
            stdev_bkg = background.std()
            for row, (current_id, strain_name) in zip(rows, id_batch):
                raw = nx.array([self.raw_data[(plate, row, col)]
                        for col in range(1, len(self.fitting_concs)+1)]
                        ).astype('float')
                if self.reverse_dilution:
                    raw = raw[::-1]
                corrected = raw - avg_bkg
                result = fit_curve(self.fitting_concs, corrected)
                vmax, ic50 = result[0]
                clean_data[current_id][drug]['strain_name'] = strain_name
                clean_data[current_id][drug]['values'] = raw
                clean_data[current_id][drug]['corrected'] = corrected
                clean_data[current_id][drug]['vmax'] = vmax
                clean_data[current_id][drug]['ic50'] = ic50
                clean_data[current_id][drug]['ic50_str'] = format_ic50(ic50)
                clean_data[current_id][drug]['result'] = result[0]
                clean_data[current_id][drug]['sbr'] = corrected[-1] / avg_bkg
                clean_data[current_id][drug]['snr'] = corrected[-1] / stdev_bkg
                clean_data[current_id][drug]['bkg'] = avg_bkg
                clean_data[current_id][drug]['stdev'] = stdev_bkg

    def _collate_data(self):
        """Get experiments out of plate data"""
        if self.orientation == 'row':
            return self._collate_row_data()
        else:
            return self._collate_col_data()

    def save_results(self, filename):
        """Generate the results file"""
        rows = []
        rows.append(['Detection method', self.detection_method,
                self.detection_units])
        rows.append(['Conc units', self.conc_unit])
        rows.append([])
        drug_labels = ['','']
        labels = ['ID#', 'Strain Name']
        for drug in self.drugs:
            drug_labels.extend([drug, '', ''])
            labels.extend(['IC50', 'Fold', 'S/B'])
        rows.append(drug_labels)
        rows.append([])
        rows.append(labels)
        ids = [id for id, strain_name in self.ids if id]
        for index, id in enumerate(ids):
            row = [id, self.clean_data[id][drug]['strain_name']]
            for drug in self.drugs:
                row.append(self.clean_data[id][drug]['ic50_str'])
                row.append('')
                row.append('%.0f' % self.clean_data[id][drug]['sbr'])
            rows.append(row)
        with open(filename, 'wb') as handle:
            writer = csv.writer(handle)
            writer.writerows(rows)
        return filename

    def _gen_graph(self, id, drug, best_fit_concs):
        """Generate a single graph"""
        record = self.clean_data[id][drug]
        corrected = record['corrected']
        best_fit = record['result']
        ic50 = record['ic50']
        vmax = record['vmax']

        # generate a new plot
        fig = Figure(figsize=(3.42, 2.11))
        fig.set_facecolor('white')
        ax = fig.add_subplot(111)
        ax.set_position([0.2, 0.25, 0.75, 0.6])
        ax.semilogx()
        ax.grid(True)
        ax.plot(self.graphing_concs, corrected, '.', best_fit_concs,
                inhibition(best_fit, best_fit_concs), 'r', markersize=9,
                linewidth=2)
        labels = ax.get_xticklabels() + ax.get_yticklabels()
        for label in labels:
            label.set_size(8)
        ax.set_xlabel('[%s] (%s)' % (drug, self.conc_unit), size=10)
        ax.set_ylabel('%s (%s)' % (self.detection_method,
                self.detection_units), size=10)
        ax.set_title(id, size=12)
        xmin, xmax, ymin, ymax = ax.axis()
        ic50_str = format_ic50(best_fit[1])
        if self.reverse_axis:
            ax.invert_xaxis()
            ax.text(xmax - (xmax - xmin) * 0.45,
                    ymax - (ymax - ymin) * 0.20,
                    '$IC_{50}=%s$' % ic50_str,
                    va='bottom', ha='left', size=10,  
                    bbox=dict(facecolor='white', edgecolor='white'))
        else:
            ax.text(xmax - (xmax - xmin) * 0.30,
                    ymax - (ymax - ymin) * 0.20,
                    '$IC_{50}=%s$' % ic50_str,
                    va='bottom', ha='right', size=10,  
                    bbox=dict(facecolor='white', edgecolor='white'))
        canvas = FigureCanvasAgg(fig)
        # bug in FigureCanvasAgg - the renderer isn't set unless you
        # call this, but tostring_rgb doesn't call it
        canvas.get_renderer()
        #canvas.print_figure('tmp.png', dpi=72)
        #sys.exit(1)
        size = canvas.get_width_height()
        canvas.draw()
        buffer = fig.canvas.tostring_rgb()
        image = PIL.Image.frombytes('RGB', size, buffer, 'raw', 'RGB', 0, 1)
        return image

    def save_graph(self, filename):
        """Draw a semilog plot of an inhibition binding data"""
        pdf = Canvas(filename, pagesize=letter)
        positions = [(60, 580), (308, 580), (60, 406), (308, 406),
                     (60, 232), (308, 232), (60, 58), (308, 58)]
        max_log = nx.log10(self.graphing_concs.max())
        min_log = nx.log10(self.graphing_concs.min())
        log_range = max_log - min_log
        points = 50
        best_fit_concs = nx.array([pow(10,
                max_log - log_range * float(x) / points)
                for x in range(0, points+1)]).astype('float')
        # start a progress dialog, as this step can be slow
        progress = wx.GenericProgressDialog(title='Progress',
                message='Generating Graphs',
                maximum=len(self.ids) * len(self.drugs), parent=None,
                style=wx.PD_AUTO_HIDE|wx.PD_REMAINING_TIME)
        #style=wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT|wx.PD_REMAINING_TIME)
        plot_num = 0
        try:
            for id, strain_name in self.ids:
                for drug in self.drugs:
                    # update the progress bar before drawing
                    cont, skip = progress.Update(plot_num,
                            'Drawing graph %s %s' % (id, drug))
                    if not cont:
                        msg = 'Graph generation canceled'
                        raise JasprAnalysisManagerError(msg)
                    position_index = plot_num % len(positions)
                    if plot_num > 0 and position_index == 0:
                        pdf.showPage()
                    image = self._gen_graph(id, drug, best_fit_concs)
                    x, y = positions[position_index]
                    pdf.drawInlineImage(image, x, y, width=246, height=152)
                    plot_num = plot_num + 1
        except Exception:
            raise
        finally:
            progress.Destroy()
            pdf.save()
        return filename


if __name__ == '__main__':

    def main():
        from manage_data import read_datafile
        from manage_key import read_keyfile
        from manage_config import load_experiment_configs
        raw_data = read_datafile(r'..\..\..\test\chemi\07252008.txt')
        drugs, ids = read_keyfile(r'..\..\..\test\chemi\inhibition_key.csv')
        default, junk, experiments = load_experiment_configs(path=r'..\config')
        experiment = experiments[default]
        jam = JasprAnalysisManager(experiment, drugs, ids, raw_data)
        jam.save_results('test.csv')
        jam.save_graph('test.pdf')

    main()
