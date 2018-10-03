Curve Fitting in jaspr
========================

jaspr uses the Levenberg-Marquardt least-squares curve fitting
algorithm from the SciPy (Scientific Python) package.  A brief
description of the background correction, calculation of signal ratios,
and the estimates for fitting curves follows.

Background Correction
---------------------

Average background is calculated from a blank column on each plate - it
is no longer assumed to follow the last column on the plate that
contains data from an experiment.  It is assumed that even if not all
available positions are used to run experiments, a full blank column
will still be run.

The average background is subtracted from every measurement on the plate
prior to curve fitting.  It can then be assumed that the enzyme turnover
rate will drop to 0 in the presence of excess quantities of the
inhibitor, eliminating the need to include an unknown constant offset
term in the fitting equation.  This will reduce error in the fit if the
error in the experimental setup is greater than the error introduced by
variability in the plate reader instrument.

Signal-to-Background Ratio (SBR)
--------------------------------

The max signal is always taken from the 0 drug concentration well of an
experiment after background correction -- this may not be the highest
signal of an experiment.  This value is then divided by the average
background.

SBR = (raw_signal<sub>0 conc</sub> - background<sub>average</sub>) / background<sub>average</sub>

Thus, an SBR of 0 means that the signal was equal to the average
background.

*Note*: Using the SBR as a quality metric for an experiment can be
somewhat misleading.  In the case of a high average background with a
low standard deviation, it is possible to observe a low SBR value but
still get a high quality curve fit and accurate IC<sub>50</sub> value.
Alternatively, in the case of a low average background with a high
standard deviation, it is possible to observe a high SBR value but get
an inaccurate IC<sub>50</sub> value.

Despite these objections, SBR has been empirically determined to be the
best measure of quality for these types of experiments.

Inhibition Equation
-------------------

The values are fit to a standard enzyme turnover rate inhibition curve.

rate = V<sub>max</sub> * (1 - (c / (K<sub>i</sub> + c)))

Here, V<sub>max</sub> is the reaction rate when no inhibitor is
present, and c is the concentration of the inhibitor.  K<sub>i</sub>
is the equilibrium constant for the interaction between the inhibitor
and the enzyme.  It is equal to the concentration of the inhibitor where
rate/V<sub>max</sub> = 1/2, also know as the IC<sub>50</sub>.

Initial Constants Guess
-----------------------

Least-squares curve fitting requires that an initial guess be supplied
for the unknown values in the fit.  jaspr guesses a V<sub>max</sub>
by choosing the maximum value from an experiment, and a K<sub>i</sub>
value based on the first concentration with a signal greater than
1/2 * V<sub>max</sub>.  This estimate is likely to be larger than the
final answer, but approximately correct, meaning the fitting algorithm
should converge quickly to the correct answer.

In some rare cases, these initial guesses will fail to converge to a
solution.  Typically, this means that the K<sub>i</sub> value is several
orders of magnitude too large.  jaspr will attempt to use decreasing
values from the dilution series for the initial K<sub>i</sub> guess to
improve the fit.  jaspr should never fail to find a fit for any
reasonable data. 

