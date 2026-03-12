`jaspr` Data Formats
====================

Perkin Elmer Victor Plate Readers
---------------------------------

`jaspr` was originally designed to work with Victor plate readers that
can read multiple plates and generate one result file.  The analysis can
use either the text or excel result file.

Other Plate Readers
-------------------

Many other plate readers exist and can now be used with `jaspr`, with a
little additional work.  By creating a generic data file containing data
from multiple plates, it is now possible to analyze an experiment of any
size, measured on any appropriate plate reader.

Files may be in csv, xls, or xlsx format, and all data must be in the
first sheet of the file if using one of the Excel formats.  Each plate
must be oriented to have 8 rows and 12 columns, with column 1 of the
plate in column 1 of the spreadsheet.  Plate labels can be included if
needed, but will not be used by `jaspr`.

