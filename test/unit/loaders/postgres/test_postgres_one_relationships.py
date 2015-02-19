import unittest
import json
from mock import Mock

from wextractor.loaders.postgres import PostgresLoader

class TestPostgresLoaderOneRelationships(unittest.TestCase):
    def setUp(self):

        self.schema = [
                {
                    'table_name': 'foo',
                    'pkey': None,
                    'columns': (
                        ('foo', 'INTEGER'),
                        ('bar', 'INTEGER')
                    ),
                    'to_relations': [],
                    'from_relations': ['baz'],
                },
                {
                    'table_name': 'baz',
                    'pkey': None,
                    'columns': (
                        ('baz', 'VARCHAR'),
                    ),
                    'to_relations': ['foo'],
                    'from_relations': []
                }
            ]

        self.loader = PostgresLoader({'database': 'dummy_db', 'user': 'dummy_user'}, schema=self.schema)

        self.data = json.loads(open('./test/mock/json/one_relation.json', 'r').read())

    def test_foreign_key_statement_generator(self):
        '''
        Tests that the alter table statements are properly generated
        '''
        self.assertEquals(
            'ALTER TABLE foo ADD FOREIGN KEY (baz_id) REFERENCES baz',
            self.loader.generate_foreign_key_query(self.schema[0])
        )

    def test_simple_dedupe(self):
        '''
        Tests that both of our tables were properly deduped
        '''
        tables = self.loader.transform_to_schema(self.data, True)
        self.assertEquals(len(tables[0]), 4)
        self.assertEquals(len(tables[1]), 3)

    def test_transform_to_proper_schema(self):
        '''
        Tests to make sure the schema was properly transformed
        '''
        transformed = self.loader.transform_to_schema(self.data, True)

        # ensure that the proper fields ended up in the right tables
        self.assertEquals(
            sorted(transformed[0][0].keys()),
            ['bar', 'baz_id', 'foo', 'foo_id']
        )

        self.assertEquals(
            sorted(transformed[1][0].keys()),
            ['baz', 'baz_id']
        )

    def test_generate_tempfile(self):
        '''
        Tests to make sure that the files have the right fields, row_id
        '''

        transformed = self.loader.transform_to_schema(self.data, True)
        for ix, table in enumerate(transformed):
            tmpfile, col_headers = self.loader.generate_data_tempfile(table)

            self.assertTrue('row_id' in col_headers)
            self.assertTrue(len(tmpfile.read().split('\n')), len(table))