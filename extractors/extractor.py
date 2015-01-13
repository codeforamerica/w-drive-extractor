#!/usr/bin/env python

class Extractor:
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
        dictionary formatted as follows:
        {
            sheet name: [{field: value, ...}],
            ...
        }
        '''
        raise NotImplementedError