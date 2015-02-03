import unittest
from wextractor.loaders.postgres import PostgresLoader

class TestPostgresLoader(unittest.TestCase):
	def setUp(self):
		self.Loader = PostgresLoader('dummy_connection')
		self.table_schema = {'table_name': 'test'}

	def test_generate_drop_table_query(self):
		drop_table_query = self.Loader.generate_drop_table_query(self.table_schema)
		self.assertEquals(drop_table_query, 'DROP TABLE IF EXISTS test')

	def test_generate_table_schema(self):

		self.assertTrue(True)