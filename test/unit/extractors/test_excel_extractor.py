import unittest
import datetime
from wextractor.extractors.excel import ExcelExtractor
from nose.tools import raises

class TestExcelExtractor(unittest.TestCase):
    def setUp(self):
        self.Extractor = ExcelExtractor('excel.xlsx', dtypes=[unicode, int, datetime.datetime])

    def test_convert_to_python_types(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()