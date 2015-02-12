import unittest
import datetime
from wextractor.extractors.excel import ExcelExtractor
from nose.tools import raises

class TestExcelExtractor(unittest.TestCase):
    def setUp(self):
        self.Extractor = ExcelExtractor('excel.xlsx', dtypes=[unicode, int, datetime.datetime])

    @raises(Exception)
    def test_header_matches_dtypes(self):
        '''
        If we have an ExcelExtractor and the number
        of headers doesn't match the number of columns
        specified in the dtypes, break
        '''
        ExcelExtractor(
            'excel.xlsx', header=['one', 'two'], dtypes=[unicode, int, datetime.datetime]
        )

    def test_convert_to_python_types(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()