import unittest
import datetime
from wextractor.extractors.excel import ExcelExtractor
from nose.tools import raises

class TestExcelExtractor(unittest.TestCase):
    def setUp(self):
        '''
        excel.xlsx is an Excel file set up as follows:

        # col   | str_col | date_col   |bool col
        --------|---------|------------|--------
        1       | foo     | 2015-05-01 | TRUE
        2       | bar     | 2015-01-01 | FALSE
        foo     | baz     | 1234       | n/a

        Running the extract method on this file should
        gives the following output:

        [{u'date_col': datetime.datetime(2014, 5, 1, 0, 0), u'number_col': 1, u'str_col': u'foo', 'bool_col': True},
         {u'date_col': datetime.datetime(2014, 1, 1, 0, 0), u'number_col': 2, u'str_col': u'bar', 'bool_col': False},
         {u'date_col': None, u'number_col': None, u'str_col': u'baz', 'bool_col': None}]
        '''
        self.extractor = ExcelExtractor('./test/mock/excel/excel.xlsx', dtypes=[int, unicode, datetime.datetime, bool])
        self.data = self.extractor.extract()

    def test_convert_to_python_types(self):
        '''
        Tests that the mock excel data has been successfully converted to python types.
        '''
        for row in self.data:
            if row['date_col'] is not None:
                # dates should be dates or None
                self.assertTrue(isinstance(row['date_col'], datetime.datetime))
            if row['number_col'] is not None:
                self.assertTrue(isinstance(row['number_col'], int))
            if row['str_col'] is not None:
                self.assertTrue((row['str_col'], unicode))
            if row['bool_col'] is not None:
                self.assertTrue((row['bool_col'], bool))

    def test_drop_incorrect_types(self):
        '''
        Tests that improper types in the excel are dropped.
        '''
        # assert that it is dropping one of the ints, dates, and bool
        self.assertEquals(
            len([i['date_col'] for i in self.data if i['date_col'] is not None]), 2
        )
        self.assertEquals(
            len([i['number_col'] for i in self.data if i['number_col'] is not None]), 2
        )
        self.assertEquals(
            len([i['bool_col'] for i in self.data if i['bool_col'] is not None]), 2
        )
        # assert that the string column isn't dropped
        self.assertEquals(
            len([i['str_col'] for i in self.data if i['str_col'] is not None]), 3
        )

    def test_column_headers(self):
        '''
        Tests that the column has been properly renamed
        '''
        self.assertTrue('number_col' in self.data[0].keys())
        self.assertTrue('bool_col' in self.data[0].keys())

    def test_working_column_headers(self):
        '''
        Tests that you can specify custom column headers
        '''
        headers = ['dt', 'num', 'bool', 'str']
        extractor = ExcelExtractor(
            './test/mock/excel/excel.xlsx', 
            header=headers,
            dtypes=[int, unicode, datetime.datetime, bool])
        data = extractor.extract()
        for row in data:
            self.assertEquals(
                sorted(headers), sorted(row.keys())
            )

    def test_no_dtypes(self):
        '''
        Tests that you still get the proper output without dtypes
        '''
        extractor = ExcelExtractor(
            './test/mock/excel/excel.xlsx'
        )
        data = extractor.extract()


if __name__ == '__main__':
    unittest.main()