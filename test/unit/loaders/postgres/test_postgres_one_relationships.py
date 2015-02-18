import unittest
import json
from mock import Mock

from wextractor.loaders.postgres import PostgresLoader

class TestPostgresLoaderOneRelationships(unittest.TestCase):
    def setUp(self):
        self.loader = PostgresLoader(
            {'database': 'dummy_db', 'user': 'dummy_user'},
            schema=[
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
        )

        self.data = json.loads(open('./test/mock/json/one_relation.json', 'r').read())

    def test_simple_dedupe(self):
        '''
        Test that both of our tables were properly deduped
        '''
        tables = self.loader.transform_to_schema(self.data, True)
        self.assertEquals(len(tables[0]), 4)
        self.assertEquals(len(tables[1]), 3)