# `jaspr` Configuration Files

The `jaspr` config files are designed to allow power users to create a
new experiment description for use in `jaspr` with a minimum of effort.
`jaspr` is designed to work with data from 96-well plate readers to fit
inhibition binding data.  As such, it has a number of quirks that are
due to the experiment design needed to fit an 8x12 plate layout.

This file describes `jaspr` experiment config files in detail.  While it
serves as a useful reference, the config files are relatively simple to
work with.  For a config file with heavy comments, find the jaspr
install folder and look at '~\\jaspr\\config\\aus_3drug_fluoro_11samples'.
For a more minimal config file, see
'~\\jaspr\\config\\met_3drug_chemi_8samples'.

## Assumptions

1.  All experiments are run in 96-well plates with 8 rows (A-H) and 12
    columns (1-12)

2.  An experiment cycles through N drugs, one per plate.  Therefore, the
    number of plates should be a multiple of the number of drugs.

3.  Samples run in batches of 7, 8, 11, or 12 depending on the detection
    technology and dilution series.  Each batch of samples repeats for
    N plates.

## The `default_settings` Config File

This file does not contain an experiment configuration.  It allows the
user to specify which experiment will be considered the default.  It can
be managed by the `jaspr` software, and does not need to be edited by the
user.

### `[selected]`

-   `experiment`
-   `generate_graphs`

The `[selected] experiment` should be set to the `[experiment] name` of
one of the experimental configurations, exactly as it appears in that
config file.  It changes as the user selects different settings in the
program, reflecting the setting used most recently.

`[selected] generate_graphs` is a Boolean that manages whether a user
has selected the generate_graphs option, maintaining that state across
sessions.  This is useful if a user always generates graphs, or never
generates graphs.

## Config File Sections

Each configuration file contains four sections, with several settings
per section.  With some care, these files can be modified or created
from scratch to describe a wide variety of experiments that `jaspr` can
analyze.

### `[experiment]`

-   `name`
-   `description`

The `[experiment]` section tracks the `name` and `description` of an
experiment.  The `name` must be unique - it will be used to build a menu
option within `jaspr`.  The `description` becomes the help text for the
menu option.  This allows the user to better understand what the
experiment designer had in mind.

It is good practice to have the name of the config file reflect the name
of the experiment.  This should make it easy to ensure that both file
names and experiment names remain unique.

### `[plate]`

-   `orientation`
-   `blank_position`
-   `blank_orientation`
-   `reverse_dilution`

The `[plate]` section tracks how experiments are situated in the plate.
The `orientation` tracks whether a dilution series runs across a row, or
down a column of the plate.  The value of `orientation` must either be
`row` or `col`.  The `reverse_dilution` setting is used with
column-based assays that run from lowest dilution in row A to highest in
row H.

`blank_position` and `blank_orientation` together determine the location
of several blanks.  The value of `blank_orientation` should be either
`row` `col`.  The value of `blank_position` should be either `first` or
`last`.  Note that `firs`t is an absolute position, while `last`
immediately follows the last sample on the plate.

### `[detection]`

-   `method`
-   `units`

The `[detection]` section is used to specify the `method` and `units`
used.  These values become the y-axis labels for graphs.

### `[drug]`

-   `drugs`
-   `concs`
-   `conc_unit`
-   `graph_zero`

The `[drug]` section tracks all the information about drugs used by
default in the experiment.  The `drugs` setting contains a
comma-separated list of drugs, in the order they appear in the
experiment.  `concs` tracks a comma-separated list of dilution values.
The list should contain positive numbers run from highest concentration
to lowest, ending with a value of 0.  The length of the list is expected
to be 8 for `col` plate orientations, or 11 for `row` plate
orientations.

The `conc_unit` setting is combined with the drug names to generate
x-axis labels for the graphs.  All values in the `concs` list should have
units equal to the `conc_unit`.

The `graph_zero` setting is needed to avoid trying to graph a
concentration of 0 on a log-scale axis, as lim x->0 log(x) = -infinity.
To avoid this, curve fitting is done with the actual drug concentration
of 0, but for graphing, 0 is replaced with the `graph_zero`, which
should be a positive number, 1-1.5 dilutions smaller than the smallest
non-zero dilution.

Currently, `jaspr` assumes that all `drugs` will be used with the same
dilution profile specified in `concs`.  The list of drugs actually used
can be changed in the key file, but the concentrations cannot.  To run
an experiment using a different concentration profile, create a new
experiment.  There is currently no way to specify a per-drug dilution
profile.

## The `default` Config File

The default config file should not be modified by the user.  It tracks
the most recently used configuration, and is managed by `jaspr` any time
the user changes the current experiment.

## Example Plate Layouts

### Row Orientation

The chemiluminescence experiment uses a row-based layout, half-log10
dilutions from highest (1000 nM) in column 1 to lowest (0.032 nM) in column 10,
no drug in column 11 (0 nM), and a blank in column 12.

A (partial) config file for this plate layout would look like:

    [plate]
    orientation = row
    reverse_dilution = False
    blank_position = last
    blank_orientation = col

    [drugs]
    concs = 1000,320,100,32,10,3.2,1,0.32,0.1,0.032,0

<table>
  <caption><em>Chemiluminescence Plate Layout<em></caption>
  <tr><th colspan="2" rowspan="2"></th><th colspan="11"></th><th>blank</th></tr>
  <tr>                                 <th>   1</th><th>  2</th><th>  3</th><th> 4</th><th> 5</th><th>  6</th><th>7</th><th>   8</th><th>  9</th><th>   10</th><th>11</th><th>   12</th></tr>
  <tr><th>Sample #1</th><th>     A</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
  <tr><th>Sample #2</th><th>     B</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
  <tr><th>Sample #3</th><th>     C</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
  <tr><th>Sample #4</th><th>     D</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
  <tr><th>Sample #5</th><th>     E</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
  <tr><th>Sample #6</th><th>     F</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
  <tr><th>Sample #7</th><th>     G</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
  <tr><th>Sample #8</th><th>     H</th><td>1000</td><td>320</td><td>100</td><td>32</td><td>10</td><td>3.2</td><td>1</td><td>0.32</td><td>0.1</td><td>0.032</td><td> 0</td><td>blank</td></tr>
</table>

### Col Orientation

The 11-sample fluorescence experiment uses a column-based layout, log10
dilutions from no drug in row A, lowest (0.01 nM) in column B to highest
(10000 nM) in column H, and a 'blank' experiment in the last column on
each plate.  By setting `reverse_dilution = True`, `jaspr` will know to
reverse the order of the dilution series to match the high -> low
ordering of the drug concentrations.  Also, because the the blank wells
are not in a fixed position, an ID of 'blank' needs to be added to the
key file for every blank position.

A (partial) config file for this plate layout would look like:

    [plate]
    orientation = col
    reverse_dilution = True
    blank_position = last
    blank_orientation = col

    [drugs]
    concs = 10000,1000,100,10,1,0.1,0.01,0

<table>
  <caption><em>Fluorescence Plate Layout<em></caption>
  <tr><th> </th><th>Sample #1</th><th>Sample #2</th><th>Sample #3</th><th>Sample #4</th><th>Sample #5</th><th>Sample #6</th><th>Sample #7</th><th>Sample #8</th><th>Sample #9</th><th>Sample #10</th><th>Sample #11</th><th>blank</th></tr>
  <tr><th> </th><th>        1</th><th>        2</th><th>        3</th><th>        4</th><th>        5</th><th>        6</th><th>        7</th><th>        8</th><th>        9</th><th>        10</th><th>        11</th><th>   12</th></tr>
  <tr><th>A</th><td>     0   </td><td>     0   </td><td>     0   </td><td>     0   </td><td>     0   </td><td>     0   </td><td>     0   </td><td>     0   </td><td>     0   </td><td>      0   </td><td>      0   </td><td>blank</td></tr>
  <tr><th>B</th><td>     0.01</td><td>     0.01</td><td>     0.01</td><td>     0.01</td><td>     0.01</td><td>     0.01</td><td>     0.01</td><td>     0.01</td><td>     0.01</td><td>      0.01</td><td>      0.01</td><td>blank</td></tr>
  <tr><th>C</th><td>     0.1 </td><td>     0.1 </td><td>     0.1 </td><td>     0.1 </td><td>     0.1 </td><td>     0.1 </td><td>     0.1 </td><td>     0.1 </td><td>     0.1 </td><td>      0.1 </td><td>      0.1 </td><td>blank</td></tr>
  <tr><th>D</th><td>     1   </td><td>     1   </td><td>     1   </td><td>     1   </td><td>     1   </td><td>     1   </td><td>     1   </td><td>     1   </td><td>     1   </td><td>      1   </td><td>      1   </td><td>blank</td></tr>
  <tr><th>E</th><td>    10   </td><td>    10   </td><td>    10   </td><td>    10   </td><td>    10   </td><td>    10   </td><td>    10   </td><td>    10   </td><td>    10   </td><td>     10   </td><td>     10   </td><td>blank</td></tr>
  <tr><th>F</th><td>   100   </td><td>   100   </td><td>   100   </td><td>   100   </td><td>   100   </td><td>   100   </td><td>   100   </td><td>   100   </td><td>   100   </td><td>    100   </td><td>    100   </td><td>blank</td></tr>
  <tr><th>G</th><td>  1000   </td><td>  1000   </td><td>  1000   </td><td>  1000   </td><td>  1000   </td><td>  1000   </td><td>  1000   </td><td>  1000   </td><td>  1000   </td><td>   1000   </td><td>   1000   </td><td>blank</td></tr>
  <tr><th>H</th><td> 10000   </td><td> 10000   </td><td> 10000   </td><td> 10000   </td><td> 10000   </td><td> 10000   </td><td> 10000   </td><td> 10000   </td><td> 10000   </td><td>  10000   </td><td>  10000   </td><td>blank</td></tr>
</table>
