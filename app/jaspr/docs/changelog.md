`jaspr` Changelog
=================

Version 1.3.0 (03/04/2014)

### New Features ###

* Added new plate layout to accomidate new assay design

### Comments ###

* The new plate layout was driven by a request from NIID to allow 12
  experiments, 7 concentrations, with the 8th row blank.  This requires
  adding a new config option to specify row or col for blanks, rather than
  assuming column-oriented layouts would use a column, etc.

Version 1.2.0 (09/23/2011)
------------------------

### New Features ###

* Clean-up/clarify documentation.
* Added help menu to easily access documentation.
* Added management of the graph generation option.
* Added generic data layout to support non-Victor readers

### Bug Fixes ###

* Date checking removed (fixes bug with European style dates).
* S/B ratios are now reported as integers only.
* Fixed a bug where signals < 1 were not handled correctly

### Comments ###

* This version of `jaspr` is simpler and more accessible to the
  larger AVR community.  It includes bug fixes to avoid date formatting
  issues in excel, and it reads input files from more kinds of plate
  readers.
* Moved to Python 2.7.  This should have no impact on the end user, but
  will matter to anyone wanting to customize and redistribute the code.

Version 1.1.0 (04/12/2010)
------------------------

### New Features ###

*  External config files replace hard-coded values.
    *  Specify plate layout for column or row-based experiments.
    *  Specify drug dilution series.
    *  List most common drug panel and order.
    *  Specify detection methods and units for labeling graphs, rather
	   than trying to guess based on instrument files.
*  Key files are now required
    *  Blank rows can now be explicitly specified for column-based experiments.
*  Added support for `.xls` instrument files for Victor-class plate readers
   from PerkinElmer

### Bug Fixes ###

* Added a _ton_ of documentation.

### Comments ###

* Name changed to `jaspr` - <em>J</em>ames <em>A</em>.
<em>S</em>magala's <em>P</em>rogram for <em>R</em>esistance.  Thanks to
MET for a catchy-er name!
* Now includes licensing information to allow distribution of `jaspr` to
  other labs.

Version 1.0 (08/22/2008)
------------------------

* Initial release of `Inhibition` to the CDC MET.
