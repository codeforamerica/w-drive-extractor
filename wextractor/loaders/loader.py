#!/usr/bin/env python

class Loader:
    def __init__(self, connection_params, schema=None):
        '''
        Initializes a new Loader. Loaders take a
        connection_params argument, which varies based on
        each implmenetation of the Loader subclasses
        and an optional schema argument that dictate
        how the extracted data should be loaded. If we have
        no schema, dump a denormalized data set from the data
        dictionary keys
        '''
        self.connection_params = connection_params
        self.schema = schema

    def connect(self):
        '''
        Each Loader must implement a connect method
        '''
        raise NotImplementedError

    def transform_to_schema(self, line):
        '''
        Each Loader must implement a transform_to_schema 
        method. This method should take the schema the
        class is initialized with and transform a single line
        of extracted data to that format.
        '''
        raise NotImplementedError

    def load(self, data, add_id=False):
        '''
        Each loader must implement a load method. Load takes an
        optional add_id variable that determines whether or not
        the tables need to add an id integer column
        '''
        raise NotImplementedError