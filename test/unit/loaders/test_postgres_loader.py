import unittest
from nose.tools import raises
from wextractor.loaders.postgres import PostgresLoader

class TestPostgresLoader(unittest.TestCase):
    def setUp(self):
        self.Loader = PostgresLoader({'database': 'dummy_db', 'user': 'dummy_user'})
        self.table_schema = {
            'table_name': 'test', 'pkey': 'id', 'columns': (('id', 'INTEGER'),)
        }
        self.table_schema_no_pkey = {
            'table_name': 'test', 'columns': (('id', 'INTEGER'),)
        }
        self.table_schema_cols_not_tuple = {
            'table_name': 'test', 'pkey': 'id', 'columns': (('id'),)
        }
        self.table_schema_no_col_types = {
            'table_name': 'test', 'pkey': 'id', 'columns': (('id',),)
        }
        self.table_schema_no_cols = {
            'table_name': 'test', 'pkey': 'id'
        }

    def test_generate_drop_table_query(self):
        '''
        Tests that the drop query is created properly
        '''
        drop_table_query = self.Loader.generate_drop_table_query(self.table_schema)
        self.assertEquals(drop_table_query, 'DROP TABLE IF EXISTS test')

    def test_generate_table_schema(self):
        '''
        Tests that the create query is created properly
        '''
        create_table_query = self.Loader.generate_create_table_query(self.table_schema)
        self.assertEquals(
            create_table_query,
            'CREATE TABLE IF NOT EXISTS test (row_id SERIAL,id INTEGER, PRIMARY KEY(id))'
        )

    def test_create_table_failures(self):
        '''
        Tests that having no pkey raises an Exception
        '''
        self.assertRaises(Exception, self.Loader.generate_create_table_query, self.table_schema_no_pkey)
        self.assertRaises(Exception, self.Loader.generate_create_table_query, self.table_schema_no_cols)
        self.assertRaises(Exception, self.Loader.generate_create_table_query, self.table_schema_cols_not_tuple)
        self.assertRaises(Exception, self.Loader.generate_create_table_query, self.table_schema_no_col_types)
