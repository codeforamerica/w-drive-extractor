#!/usr/bin/env python

class Extractor(object):
    def __init__(self, target, header=None, dtypes=None):
        '''
        Initializes a new Extractor. Extractors pull data
        out of different targets. The target (file, url, etc)
        is passed in as an argument, along with whether or
        not the first row of the target contains headers
        '''
        self.target = target
        self.header = header
        self.dtypes = dtypes

        # if we have a header and dtypes, make sure they are the
        # same length
        if self.header and self.dtypes:
            if len(self.header) != len(self.dtypes):
                raise Exception('Number of headers must match number of dtypes')

    def transform_row(self, header, row):
        if self.dtypes is None:
            return dict(zip(header, row))
        else:
            output = []
            for idx, cell in enumerate(row):
                try:
                    converted_val = self.dtypes[idx](cell)
                except:
                    converted_val = None
                output.append(
                    converted_val
                )
            return dict(zip(header, output))

    def simple_cleanup(self, field):
        '''
        Method to replace spaces with underscores, pound signs
        coerce to lowercase
        '''
        if type(field) in [str, unicode]:
            clean = field.lower().replace(' ', '_').replace('#', 'number')
        else:
            clean = field

        return clean

    def extract(self):
        '''
        Each Extractor implementation must implement an
        extract method. The method should return a
        list of dictionaries formatted as follows:
        [
            {field: value, ...},
            ...
        ]
        '''
        raise NotImplementedError