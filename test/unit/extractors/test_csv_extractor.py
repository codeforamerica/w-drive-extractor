import unittest
import datetime
from wextractor.extractors import CsvExtractor
from nose.tools import raises
from mock import patch

class TestCsvExtractor(unittest.TestCase):
    def setUp(self):
        '''
        file.csv is a csv file set up as follows:

        foo   | bar | baz
        ------|-----|-----
        qux   | 1   | 2
        quux  | 10  | 20
        quuux | 100 | 200
        '''
        self.extractor = CsvExtractor('./test/mock/csv/file.csv', url=False)

    @raises(TypeError)
    def test_bad_url_arg(self):
        '''
        Tests that passing a bad url arg raises a TypeError
        '''
        CsvExtractor('./test/mock/csv/file.csv', url='fails')

    def test_good_url_arg(self):
        '''
        Tests that passing a bool works as expected
        '''
        self.assertEquals(self.extractor.url, False)

    def test_detect_urls(self):
        '''
        Tests if self.url is assigned properly
        '''
        url1 = 'github.com/codeforamerica/w-drive-extractor'
        url2 = 'http://github.com/codeforamerica/w-drive-extractor'
        url3 = '/path/to/a/file.csv'

        self.assertTrue(CsvExtractor(url1).url)
        self.assertTrue(CsvExtractor(url2).url)
        self.assertFalse(CsvExtractor(url3).url)

    @patch('urllib2.urlopen')
    def test_urls_work(self, urlopen):
        '''
        Tests to see if using a url arg works as expected
        '''
        extractor = CsvExtractor('github.com/codeforamerica/w-drive-extractor')
        extractor.extract()
        assert urlopen.called

    def test_csv_extract(self):
        '''
        Tests that the extraction yields the proper data
        '''
        data = self.extractor.extract()
        self.assertEquals(len(data), 3)
        for row in data:
            self.assertEquals(
                sorted(row.keys()),
                ['bar', 'baz', 'foo']
            )

    def test_csv_headers_work(self):
        '''
        Tests that csv extractors work when you have headers
        '''
        extractor = CsvExtractor('./test/mock/csv/file.csv', header=['col1', 'col2', 'col3'], url=False)
        data = extractor.extract()
        self.assertEquals(len(data), 4)
        for row in data:
            self.assertEquals(
                sorted(row.keys()),
                ['col1', 'col2', 'col3']
            )
