import unittest
import json
from mock import Mock

from wextractor.loaders.postgres import PostgresLoader

class TestPostgresLoaderNoRelationships(unittest.TestCase):
    def setUp(self):
        self.loader = PostgresLoader(
            {'database': 'dummy_db', 'user': 'dummy_user'},
            schema=[{
                'table_name': 'test',
                'pkey': None,
                'columns': (
                    ('foo', 'TEXT'),
                    ('bar', 'TEXT')
                )
            }]
        )

        self.data = json.loads(open('./test/mock/json/no_relations.json', 'r').read())

    def test_simple_dedupe(self):
        '''
        Tests to make sure that the duplicate rows are knocked out
        '''
        self.assertEquals(len(self.data), 4)
        self.assertEquals(len(self.loader.transform_to_schema(self.data, True)[0]), 3)
        # Should still work if add_pkey is set to False, given that the value of pkey in the schema is None
        self.assertEquals(len(self.loader.transform_to_schema(self.data, False)[0]), 3)
        # Assert that we have the proper column names

    def test_transform_to_proper_schema(self):
        '''
        Tests to make sure that the schema is transformed properly
        '''
        self.assertEquals(
            sorted(self.loader.transform_to_schema(self.data, True)[0][0].keys()),
            ['bar', 'foo', 'test_id']
        )
        # it should still work when add_pkey is set to false
        self.assertEquals(
            sorted(self.loader.transform_to_schema(self.data, False)[0][0].keys()),
            ['bar', 'foo', 'test_id']
        )

    def test_generate_tmpfile(self):
        '''
        Make sure that the column headers include the rowid and the file has the right number of rows
        '''
        transformed = self.loader.transform_to_schema(self.data, True)
        tmpfile, col_headers = self.loader.generate_data_tempfile(transformed[0])

        self.assertTrue('row_id' in col_headers)
        self.assertTrue(len(tmpfile.read().split('\n')), 3)

