#!/usr/bin/env python

import datetime
import xlrd
from extractors.extractor import Extractor

class ExcelExtractor(Extractor):
    def convert_to_python_types(self, row, header, excel_date):
        '''
        Attempts to reconcile excel data types with native
        python types.
        '''

        output = []

        ctype_conversions = {
            0: unicode, # empty
            1: unicode, # text
            2: float, # number
            3: float, # date
            4: int, # boolean
            5: int, # error codes, use error_text_from_code for lookup
            6: unicode # blank (when formatting_info=True)
        }

        for cell in row:
            converted_val = ctype_conversions[cell.ctype](cell.value)
            if cell.ctype == 3:
                converted_val = datetime.datetime(*xlrd.xldate_as_tuple(cell.value, excel_date))
            elif cell.ctype == 4:
                converted_val = bool(cell.value)

            output.append(converted_val)

        return dict(zip(header, output))


    def extract(self):
        '''
        Returns a dictionary structured as follows:
        { 
            sheet name: [{field: value, ...}],
            ...
        }
        '''
        output = {}

        workbook = xlrd.open_workbook(self.target)

        for sheet in workbook.sheet_names():

            current_sheet = workbook.sheet_by_name(sheet)
            current_row = 0

            if current_sheet.nrows == 0:
                # immediately continue if we have no rows
                continue

            # since we definitely have data, we can add
            # the sheet name as a key to the output
            output[sheet] = []

            if not self.header:
                # if we don't have a header, assume that
                # the first row will be the header
                current_header = [
                    self.simple_cleanup(field.value) for field in current_sheet.row(0)
                ]
                current_row = 1
            else:
                current_header = self.header

            while current_row < current_sheet.nrows:
                output.get(sheet).append(
                    self.convert_to_python_types(current_sheet.row(current_row), current_header, workbook.datemode)
                )

                current_row += 1

        return output
