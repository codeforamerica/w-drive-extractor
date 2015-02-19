import unittest
from nose.tools import raises
from wextractor.extractors.extractor import Extractor

class TestExtractor(unittest.TestCase):
    @raises(Exception)
    def test_header_matches_dtypes(self):
        '''
        Tests that mismatched lengths of headers and dtypes raises
        '''
        Extractor(
            'dummy', header=['one', 'two'], dtypes=[unicode, int, datetime.datetime]
        )

    def test_extractor_has_fields(self):
        '''
        Tests that an extractor has the proper fields
        '''
        test = Extractor('dummy')

        self.assertEquals(test.target, 'dummy')
        self.assertEquals(test.header, None)
        self.assertEquals(test.dtypes, None)

if __name__ == '__main__':
    unittest.main()
