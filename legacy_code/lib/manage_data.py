#!/usr/bin/env python
# file jaspr/lib/manage_data.py

"""JASPR utilities for working with data files."""

# Python library imports
import re
import csv
import os.path
import datetime

# local imports
import sys
sys.path.extend(['.', 'lib'])
from easy_xls import read_excel


class JasprDataError(Exception):
    """Error class for all data manipulation errors"""
    pass


class JasprDataParser(object):
    """Parse data files for jaspr"""

    def __init__(self):
        self.well_re = re.compile(
                r'(\d+)\t\d\t([A-H])(\d{2})\t\w+\t[\d:\.]+\t(\d+)')

    def _parse_generic_workbook(self, workbook):
        """Parse a generic workbook, regardless of the source"""
        msg = 'Bad data file'
        # we always look for data in the first sheet
        name, data, max_rows, max_cols = workbook[0]
        # 0 based in sheet space, letters in plate space
        row_labels = dict(enumerate('ABCDEFGH'))
        data_rows = []
        for row, col in data:
            if not col == 11:
                continue
            try:
                value = int(data[(row, col)])
            except ValueError:
                continue
            data_rows.append(row)
        data_rows.sort()
        if not len(data_rows) % 8 == 0:
            raise JasprDataError(msg)
        plate = 0
        cols = range(12)
        raw_data = {}
        while True:
            plate += 1
            plate_rows = data_rows[(plate-1)*8:plate*8]
            if not plate_rows:
                break
            if plate_rows[7] - plate_rows[0] != 7:
                raise JasprDataError(msg)
            for row_num, row in enumerate(plate_rows):
                for col in cols:
                    key = (plate, row_labels[row_num], col+1, )
                    try:
                        value = data[(row, col)]
                    except KeyError:
                        raise JasprDataError(msg)
                    raw_data[key] = value
        return raw_data

    def _parse_victor_txt(self, datafile_name):
        """Read data from a Victor-style text file"""
        raw_data = {}
        with open(datafile_name, 'r') as datafile_handle:
            state = 'header'
            for line in datafile_handle:
                if state == 'header':
                    if line.startswith('Plate\tRepeat\tWell\tType\tTime'):
                        state = 'data'
                    else:
                        msg = 'Bad file type'
                        raise JasprDataError(msg)
                elif state == 'data':
                    match = self.well_re.match(line)
                    if match:
                        # key is (plate #, row, col)
                        key = (int(match.group(1)), match.group(2),
                                int(match.group(3)))
                        raw_data[key] = int(match.group(4))
                    else:
                        break
        return raw_data

    def _parse_generic_txt(self, datafile_name):
        """Read data from a generic text file"""
        data = {}
        max_x, max_y = 0, 0
        with open(datafile_name) as handle:
            reader = csv.reader(handle)
            for row, line in enumerate(reader):
                for col, value in enumerate(line):
                    value = value.strip()
                    if not value:
                        continue
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                    data[(row, col)] = value
                    if row > max_x:
                        max_x = row
                    if col > max_y:
                        max_y = col
        workbook = [('', data, max_x, max_y), ]
        return self._parse_generic_workbook(workbook)

    def _parse_txt_datafile(self, datafile_name):
        """Read data from one of several possible text file formats"""
        try:
            data = self._parse_victor_txt(datafile_name)
        except JasprDataError:
            data = self._parse_generic_txt(datafile_name)
        return data

    def _parse_victor_xls(self, datafile_name):
        """Read data from a Victor-style xls file"""
        book = read_excel(datafile_name)
        raw_data = {}
        for sheet_name, sheet_data, max_x, max_y in book:
            if sheet_name.startswith('List'):
                for row in range(1, max_x):
                    plate = int(sheet_data[(row, 0, )])
                    well = sheet_data[(row, 2, )]
                    plate_row = well[0]
                    plate_col = int(well[1:])
                    key = (plate, plate_row, plate_col, )
                    value = int(sheet_data[(row, 5, )])
                    raw_data[key] = value
        return raw_data

    def _parse_generic_xls(self, datafile_name):
        return self._parse_generic_workbook(read_excel(datafile_name))

    def _parse_xls_datafile(self, datafile_name):
        """Read data from one of several possible excel file formats"""
        data = self._parse_victor_xls(datafile_name)
        if not data:
            data = self._parse_generic_xls(datafile_name)
        return data

    def __call__(self, datafile_name):
        """Read the raw data from one of several possible file formats"""
        parsers = {
            '.txt': self._parse_txt_datafile,
            '.csv': self._parse_txt_datafile,
            '.xls': self._parse_xls_datafile,
            '.xlsx': self._parse_xls_datafile,
        }
        ext = os.path.splitext(datafile_name)[1]
        parser = parsers[ext]
        return parser(datafile_name)


if __name__ == '__main__':

    def main():
        from pprint import pprint
        parser = JasprDataParser()
        path = r'C:\users\james\envs\jaspr\test\generic layout.csv'
        pprint(parser(path))

    main()
