#!/usr/bin/env python

import datetime
import xlrd
from wextractor.extractors.extractor import Extractor

class ExcelExtractor(Extractor):
    def transform_row(self, row, header, excel_date):
        '''
        Attempts to reconcile excel data types with native
        python types. If the ExcelExtractor is initialized with
        a list of dtypes, attempt to coerce to the given types.

        If the coercion fails, drop the cell value. This is certainly
        not the optimal strategy, but the current design decision
        favors flexibilty over completeness.
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

        for idx, cell in enumerate(row):
            converted_val = ctype_conversions[cell.ctype](cell.value)
            if cell.ctype == 3:
                converted_val = datetime.datetime(*xlrd.xldate_as_tuple(cell.value, excel_date))
            elif cell.ctype == 4:
                converted_val = bool(cell.value)

            if type(converted_val) != self.dtypes[idx]:
                try:
                    # for native types, try converting
                    if self.dtypes[idx] == bool:
                        converted_val = None
                    else:
                        converted_val = self.dtypes[idx](converted_val)
                except TypeError:
                    # e.g. you are attempting to load a complex type
                    converted_val = None
                except ValueError:
                    # e.g. you try to coerce an empty string to an int
                    converted_val = None

            output.append(converted_val)

        return dict(zip(header, output))

    def extract(self):
        '''
        Returns a list of dictionaries structured as follows:
        [ 
            {field: value, ...},
            ...
        ]
        '''
        output = []

        workbook = xlrd.open_workbook(self.target)

        for sheet in workbook.sheet_names():

            current_sheet = workbook.sheet_by_name(sheet)
            current_row = 0

            if current_sheet.nrows == 0:
                # immediately continue if we have no rows
                continue

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
                if self.dtypes:
                    formatted_row = self.transform_row(
                        current_sheet.row(current_row), current_header, workbook.datemode
                    )
                else:
                    formatted_row = dict(zip(
                        current_header, [cell.value for cell in current_sheet.row(current_row)]
                    ))

                output.append(formatted_row)

                current_row += 1

        return output
