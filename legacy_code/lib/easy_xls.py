#!/usr/bin/env python
# file easy_xls.py

"""Easy read/write for excel documents.

Revision History:
    20090318 James Smagala: Written
    20101006 JS: updated for openpyxl and Django

"""

# standard library imports
from StringIO import StringIO
import datetime
import os.path

# installed library imports
import xlrd
import xlwt
import openpyxl

# default date formatting for Excel
DATE_STYLE = xlwt.XFStyle()
DATE_STYLE.num_format_str = 'M/D/YY'
DATE_STYLE_XLSX = 'mm/dd/yyyy'


def read_xlsx(path, file_contents=None):
    """Read an xlsx spreadsheet.

    Uses openpyxl to implement an improved version of pyExcelerator's
    parse_xls.  Use this to simply read in data.

    """

    def _parse_sheet(book, sheet_name):
        """Read data from one worksheet in the workbook."""
        sheet = book.get_sheet_by_name(sheet_name)
        sheet_data = {}
        for coordinate in sheet._cells:
            column, row = openpyxl.cell.coordinate_from_string(coordinate)
            col = openpyxl.cell.column_index_from_string(column) - 1
            row = row - 1
            sheet_data[(row, col)] = sheet.cell(coordinate).value
        return sheet_data, sheet.get_highest_row(), \
                sheet.get_highest_column()

    if file_contents:
        book = openpyxl.reader.excel.load_workbook(StringIO(file_contents))
    else:
        book = openpyxl.reader.excel.load_workbook(path)
    data = []
    for sheet_name in book.get_sheet_names():
        sheet_data, sheet_max_x, sheet_max_y = _parse_sheet(book, sheet_name)
        data.append((sheet_name, sheet_data, sheet_max_x, sheet_max_y, ))
    return data


def read_xls(path, file_contents=None):
    """Read an excel spreadsheet

    An improvement on the pyExcelerator parse_xls.

    Uses the xlrd module supporting many Excel versions.

    The data will be a list of tuples with sheet names and data, indexed
    by x, y coordinates.  Dates are automatically converted to datetime
    objects.

    """

    def _parse_sheet(book, sheet_name):
        """Get all of the data from one sheet"""
        sheet = book.sheet_by_name(sheet_name)
        sheet_data = {}
        for row in range(sheet.nrows):
            # get a row at a time
            for col, (data_type, value, ) in enumerate(zip(
                    sheet.row_types(row), sheet.row_values(row))):
                if data_type == 0:
                    # 0 - empty cell, do nothing
                    continue
                if data_type == 1:
                    # 1 - unicode string, don't change it
                    pass
                elif data_type == 2:
                    # 2 - number, check if it should be float or int
                    # this is never perfect because the Excel doesn't
                    # know the right answer, so we guess
                    if value == int(value):
                        value = int(value)
                elif data_type == 3:
                    # 3 - number date, needs to be converted
                    try:
                        value = datetime.datetime(*xlrd.xldate_as_tuple(
                                value, book.datemode))
                    except ValueError:
                        pass
                elif data_type == 4:
                    # 4 - number boolean, don't change it
                    pass
                elif data_type == 5:
                    # 5 - error code
                    value = xlrd.error_text_from_code[value]
                sheet_data[(row, col, )] = value
        return sheet_data, sheet.nrows, sheet.ncols

    if file_contents:
        book = xlrd.open_workbook(file_contents=file_contents)
    else:
        book = xlrd.open_workbook(path)
    data = []
    for sheet_name in book.sheet_names():
        sheet_data, sheet_max_x, sheet_max_y = _parse_sheet(book, sheet_name)
        data.append((sheet_name, sheet_data, sheet_max_x, sheet_max_y, ))
    return data


def read_excel(path, uploaded_file=None):
    """Allow Django to read an xls or xlsx spreadsheet

    uploaded_file is a Django object from a file upload form.

    """
    if uploaded_file:
        ext = os.path.splitext(uploaded_file.name)[1]
    elif path:
        ext = os.path.splitext(path)[1]
    else:
        ext = None
    if '.xls' == ext:
        data = read_xls(path, uploaded_file.read() if uploaded_file else None)
    elif '.xlsx' == ext:
        data = read_xlsx(path, uploaded_file.read() if uploaded_file else None)
    else:
        raise IOError('Failed to read file')
    return data


def write_cell(worksheet, row, col, value):
    """Write the value for one cell, with date formatting if needed"""
    if isinstance(value, datetime.datetime):
        # convert datetime objects to excel date values
        value = xlrd.xldate.xldate_from_datetime_tuple(
                (value.year, value.month, value.day,
                value.hour, value.minute, value.second, ), 0)
        worksheet.write(row, col, value, DATE_STYLE)
    elif isinstance(value, datetime.date):
        # convert date objects to excel date values
        value = xlrd.xldate.xldate_from_date_tuple(
                (value.year, value.month, value.day, ), 0)
        worksheet.write(row, col, value, DATE_STYLE)
    else:
        worksheet.write(row, col, value)


def write_xls(outfile, sheets):
    """Write data from sheets to an Excel workbook.

    outfile can be either a path to a file or a file-like object.

    The basic structure for a workbook with multiple sheets is this:
    [ # a workbook is a list of worksheets
        ('', {}, max_x, max_y), # each worksheet is a 2-tuple
        (
            '', # element 0 is a worksheet name
            {}, # element 1 contains a dict with cell locations
                #     and values like -> (x, y): u'value'
                #                  or -> (x, y): #
                #
                # x and y are zero-based
                # the 'matrix' is sparse
        ),
        ('', {}, ),
    ]

    """
    # create a workbook
    workbook = xlwt.Workbook()
    for sheet in sheets:
        sheet_name, data = sheet[0:2]
        worksheet = workbook.add_sheet(sheet_name)
        for row, col in data:
            key = (row, col, )
            value = data[key]
            write_cell(worksheet, row, col, value)
    workbook.save(outfile)


def write_xlsx(outfile, sheets):
    """Write data from sheets to an xlsx workbook."""
    book = openpyxl.workbook.Workbook()
    book.worksheets = []
    for sheet in sheets:
        sheet_name, data = sheet[0:2]
        ws = openpyxl.worksheet.Worksheet(book, sheet_name)
        for row, col in data:
            value = data[(row, col)]
            cell = ws.cell(row=row + 1, column=col + 1)
            cell.value = value
            if isinstance(value, (datetime.datetime, datetime.date)):
                style = ws.get_style('%s%s' % \
                        (openpyxl.cell.get_column_letter(col + 1), row + 1))
                style.number_format.format_code = DATE_STYLE_XLSX
        book.add_sheet(ws)
    if hasattr(outfile, 'write'):
        outfile.write(openpyxl.writer.excel.save_virtual_workbook(book))
    else:
        openpyxl.writer.excel.save_workbook(book, outfile)        


def write_xls_rows(outfile, sheets):
    """Write row formatted excel sheets

    Takes a list of sheets like this:
    [('sheet_name', [[], [], [], ], ), (...), (...)]
    and writes it into a workbook.
    
    """
    # create a workbook
    workbook = xlwt.Workbook()
    for sheet in sheets:
        sheet_name, sheet_data = sheet[0:2]
        worksheet = workbook.add_sheet(sheet_name)
        for row, row_data in enumerate(sheet_data):
            for col, value in enumerate(row_data):
                write_cell(worksheet, row, col, value)
    workbook.save(outfile)


def write_xlsx_rows(outfile, sheets):
    """Write row formatted xlsx sheets"""
    book = openpyxl.workbook.Workbook()
    book.worksheets = []
    for sheet in sheets:
        sheet_name, sheet_data = sheet[0:2]
        ws = openpyxl.worksheet.Worksheet(book, sheet_name)
        for row, row_data in enumerate(sheet_data):
            for col, value in enumerate(row_data):
                cell = ws.cell(row=row + 1, column=col + 1)
                cell.value = value
                if isinstance(value, (datetime.datetime, datetime.date)):
                    style = ws.get_style('%s%s' % \
                            (openpyxl.cell.get_column_letter(col + 1), row + 1))
                    style.number_format.format_code = DATE_STYLE_XLSX
        book.add_sheet(ws)
    if hasattr(outfile, 'write'):
        outfile.write(openpyxl.writer.excel.save_virtual_workbook(book))
    else:
        openpyxl.writer.excel.save_workbook(book, outfile)        
