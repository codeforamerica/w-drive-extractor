import unittest
from nose.tools import raises
from wextractor.extractors.extractor import Extractor

class TestExtractor(unittest.TestCase):
    @raises(Exception)
    def test_header_matches_dtypes(self):
        '''
        If the number of headers doesn't match the number of columns
        specified in the dtypes, break
        '''
        Extractor(
            'dummy', header=['one', 'two'], dtypes=[unicode, int, datetime.datetime]
        )

if __name__ == '__main__':
    unittest.main()
