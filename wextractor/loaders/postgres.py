#!/usr/bin/env python

import os
import tempfile
import psycopg2
import simplejson as json
from hashlib import md5
from copy import deepcopy

from collections import defaultdict

from wextractor.loaders.loader import Loader

class PostgresLoader(Loader):
    def __init__(self, connection_params, schema=None):
        super(PostgresLoader, self).__init__(connection_params, schema)

        if self.schema is None:
            self.schema = []

        for table_schema in self.schema:
            if table_schema.get('columns', None) is None:
                raise Exception('Tables must contain columns')
            elif not isinstance(table_schema['columns'][0], tuple):
                raise Exception('Table columns must be tuples')
            elif len(table_schema['columns'][0]) == 1:
                raise Exception('Column Types are not specified')

    def connect(self):
        '''
        The connect method implements the logic behind
        the psycopg2 connection. Try/catch/finally
        logic should be implemented outside this method
        to ensure that the database connection always
        closes when appropriate.

        For PostgresLoader, the connection_params
        must include at least a database and user.
        It can also optionally include a hostname, port,
        and password
        '''
        database = self.connection_params.get('database', None)
        user = self.connection_params.get('user', None)

        if not database or not user:
            raise Exception('PostgresLoader must contain "database" and "user" keys')

        conn = psycopg2.connect(**self.connection_params)
        return conn

    def generate_drop_table_query(self, table_schema):
        '''
        Generates a cascanding drop table query that will drop
        all tables and their relations
        '''
        drop_query = '''DROP TABLE IF EXISTS {table} CASCADE'''.format(
            table=table_schema['table_name']
        )

        return drop_query

    def generate_create_table_query(self, table_schema):
        '''
        Geneates a create table query and raises exceptions
        if the table schema generation is malformed
        '''
        if len(table_schema['columns'][0]) == 2:
            coldefs = 'row_id SERIAL,'

            coldefs += ','.join(
                    '{name} {dtype}'.format(name=name, dtype=dtype) for name, dtype in table_schema['columns']
                )

            create_query = '''CREATE TABLE IF NOT EXISTS {table} ({coldefs}, PRIMARY KEY({pkey}))'''.format(
                table=table_schema['table_name'],
                coldefs=coldefs,
                pkey=table_schema['pkey']
            )

            return create_query

    def generate_foreign_key_query(self, table, i=0):
        '''
        Generates alter table statements that add formal
        foreign key relationships. Takes in a schema and
        an optional index (defaults to 0) of the positon
        of the relationship in the schema

        NOTE: This must be called AFTER data is already
        loaded. Otherwise, a psycopg2 error will be thrown.
        '''
        if table.get('from_relations', None) is None:
            return
        return '''ALTER TABLE {table} ADD FOREIGN KEY ({id}) REFERENCES {relationship}'''.format(
            table=table['table_name'],
            id=table['from_relations'][i] + '_id',
            relationship=table['from_relations'][i]
        )

    def null_replace(self, field):
        '''
        Replaces empty string, None with 'NULL' for Postgres loading
        '''
        if type(field) in [str, unicode]:
            if field == '':
                return 'NULL'
        elif field is None:
            return 'NULL'

        return field

    def hash_row(self, row):
        '''
        Return an md5 hash of a row's contents (minus its index). This hash
        will turn into the table's new primary key.
        '''
        return md5(json.dumps(row, sort_keys=True)).hexdigest()

    def simple_dedupe(self, idx, table):
        '''
        Takes in a table that has been transformed by the
        transform_to_schema method but not been deduplicated.
        This method simply attempts to determine if the row
        is an exact replica (minus fkeys). If it is, it checks to
        make sure the fkeys are the same and handles the event that
        the relationships are to different places and thus should
        be different rows (by modifying the primary key). Returns
        a deduplicated list.
        '''
        checker, output, pkey, fkey = {}, [], {}, {}

        pkey_name = self.schema[idx]['table_name'] + '_id'
        fkeys_name = [i + '_id' for i in self.schema[idx].get('from_relations', [])]

        for row in table:
            # store the value of the primary key
            pkey[pkey_name] = row.pop(pkey_name, None)
            for key in fkeys_name:
                # store the values of the primary key
                fkey[key] = row.pop(key, None)

            row_as_tuple = tuple(row.items())

            # Use try/except because it's faster than checking if
            # the key is in the dictionary keys
            try:
                row_with_fkey = dict(row.items() + fkey.items())

                checker[row_as_tuple]['pkey'].add(
                    (pkey_name, self.hash_row(row_with_fkey))
                )

                checker[row_as_tuple]['fkey'].add(tuple(fkey.items()))

            except KeyError:
                # make a deep copy because calling .pop() will update
                # every single one of these otherwise
                fkey_copy = deepcopy(fkey)
                # create a tuple of tuples for proper extraction later
                pkey_tuple = ((pkey_name, self.hash_row(row)),)
                checker[row_as_tuple] = {
                    'pkey': set(pkey_tuple),
                    'fkey': set(tuple(fkey_copy.items()))
                }

        # We should now have deduplicated everything, so we just
        # reshape the checker dictionary into the list of dict format
        # that the remainder should expect
        for checker_row, table_keys in checker.items():

            if len(table_keys['fkey']) == 0 or len(fkeys_name) == 0:
                final_output = dict(checker_row)
                final_output.update(dict(table_keys['pkey']))

            elif len(table_keys['pkey']) == 1 and len(table_keys['fkey']) == 1:
                final_output = dict(checker_row)
                final_output.update(dict(table_keys['pkey']))
                final_output.update(dict(table_keys['fkey']))

            elif len(table_keys['pkey']) == len(table_keys['fkey']):
                for fkey in table_keys['fkey']:
                    new_pkey = self.hash_row(checker_row + fkey)

                    final_output = dict(checker_row)
                    final_output.update({pkey_name: new_pkey})
                    try:
                        final_output.update(dict((fkey,)))
                    except:
                        final_output.update(dict(fkey))

            else:
                # TODO: Implement something to handle this
                raise Exception('pkey/fkey mismatch.')

            output.append(final_output)

        return output

    def transform_to_schema(self, data, add_pkey):
        '''
        Schema for postgres must take the following form:

        [
            {
            'table_name': '',
            'pkey': '',
            'index': '',
            'to_relations': ['table_name', ...],
            'from_relations': ['table_name', ...],
            'columns': ( ('col_name', col_type), ... ),
            }, ...
        ]

        Input data will come in as a list of dictionaries, with
        the keys being the column names and the values being the
        values. The transformed data will return a list of
        dictionaries where each dictionary is a table to write
        to the final data store.

        Additionally, this method holds a dictionary of like items
        and their ids to allow for very simple deduplication.
        '''
        # start by generating the output list of lists
        output = [list() for i in range(len(self.schema))]
        holder = [defaultdict(list) for i in range(len(self.schema))]

        # initialize a dictionary to hold potential duplicates
        deduper = {}

        for ix, line in enumerate(data):
            for table_idx, table in enumerate(self.schema):

                col_names = zip(*table['columns'])[0]

                # initialize the new row to add to the final loaded data
                new_row = dict()

                for cell in line.iteritems():

                    if cell[0] in col_names:
                        # extend the new row with the value of the cell
                        new_row[cell[0]] = str(self.null_replace(cell[1]))
                    else:
                        continue

                row_id = self.hash_row(new_row)
                if add_pkey or table.get('pkey', None) is None:
                    new_row[table['table_name'] + '_id'] = row_id
                else:
                    new_row[table['pkey']] = row_id

                # once we have added all of the data fields, add the relationships
                for relationship in table.get('to_relations', []):
                    # find the index of the matching relationship table
                    rel_index = next(index for (index, d) in enumerate(self.schema) if d['table_name'] == relationship)
                    output[rel_index][ix][self.schema[table_idx]['table_name'] + '_id'] = row_id

                output[table_idx].extend([new_row])

        final_output = []
        for table_ix, table in enumerate(output):
            final_output.append(self.simple_dedupe(table_ix, table))

        return final_output

    def generate_data_tempfile(self, data):
        '''
        Takes in a list and generates a temporary tab-separated
        file. This file can then be consumed by the Postgres \COPY
        function
        '''

        tmp_file = tempfile.TemporaryFile(dir=os.getcwd())

        if len(data) == 0:
            return tmp_file, None

        n = 0

        for row in data:
            row = sorted(row.items())

            n += 1
            if n % 10000 == 0:
                print 'Wrote {n} lines'.format(n=n)

            rowstr = '\t'.join([str(n)] + [i[1] for i in row]) + '\n'

            tmp_file.write(rowstr)

        tmp_file.seek(0)

        return tmp_file, ['row_id'] + sorted(data[0].keys())

    def load(self, data, add_pkey=True):
        '''
        Main method for final Postgres loading.

        Takes in data and a flag for adding a primary key and
        transforms the input data to the proper schema, generates
        relationships, does simple deduplcation on exact matches,
        writes a tempfile with all of the data, boots up a
         connection to Postgres, and loads everything in
        '''
        conn = None

        try:
            conn = self.connect()
            cursor = conn.cursor()

            if not self.schema:
                raise Exception('Schemaless loading is not supported by PostgresLoader')

            tables = self.transform_to_schema(data, add_pkey)

            for ix, table in enumerate(self.schema):
                table['columns'] = ( (table['table_name'] + '_id', 'VARCHAR(32)'), ) + table['columns']

                if add_pkey or table.get('pkey', None) is None:
                    table['pkey'] = table['table_name'] + '_id'

                if table.get('from_relations', None):
                    for relationship in table['from_relations']:
                        table['columns'] += ( ( relationship + '_id', 'VARCHAR(32)' ), )

                drop_table = self.generate_drop_table_query(table)
                cursor.execute(drop_table)

                create_table = self.generate_create_table_query(table)
                cursor.execute(create_table)
                tmp_file, column_names = self.generate_data_tempfile(tables[ix])

                cursor.copy_from(tmp_file, table['table_name'], null='NULL', sep='\t', columns=column_names)

            for table in self.schema:
                for ix, relationship in enumerate(table.get('from_relations', [])):
                    fk_query = self.generate_foreign_key_query(table, ix)
                    cursor.execute(fk_query)

            conn.commit()

        except psycopg2.Error, e:
            if conn:
                conn.rollback()
            raise e

        finally:
            if conn:
                conn.close()
