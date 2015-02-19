import unittest
from wextractor.loaders.loader import Loader

class TestLoader(unittest.TestCase):
    def test_loader_has_fields(self):
        '''
        Tests that an extractor has the proper fields
        '''
        test = Loader('dummy')

        self.assertEquals(test.connection_params, 'dummy')
        self.assertEquals(test.schema, None)
