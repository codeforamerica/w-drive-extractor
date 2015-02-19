#!/usr/bin/env python

import datetime
import urllib2
import httplib
import urlparse

from wextractor.extractors.extractor import Extractor

class CsvExtractor(Extractor):
    def __init__(self, target, header=None, dtypes=None, url=None):
        '''
        CsvExtractor initializes with an optional url flag that tells
        the extractor whether or not the resource is local or remote so
        that it can be loaded accordingly
        '''
        super(CsvExtractor, self).__init__(target, header, dtypes)

        if url is None:
            self.url = self.detect_url(target)
        elif type(url) != bool:
            raise TypeError('url kwarg must be of type bool')
        else:
            self.url = url

    def detect_url(target):
        # see: http://stackoverflow.com/questions/2924422/how-do-i-determine-if-a-web-page-exists-with-shell-scripting
        # and http://stackoverflow.com/questions/1140661/python-get-http-response-code-from-a-url
        # for additional information
        good_codes = [httplib.OK, httplib.FOUND, httplib.MOVED_PERMANENTLY]
        # check to see if we have a scheme in the url, and append one if not
        parsed_target = urlparse(target)
        if bool(parsed_target.scheme) is False:
            target = 'http://' + target
        host, path = urlparse(target)[1:3]
        try:
            conn = httplib.HTTPConnection(host)
            conn.request("HEAD", path)
            status = conn.getresponse().status
        except StandardError:
            status = None

        return status in good_codes

    def extract(self):
        if self.url:
            raw_data = urllib2.urlopen(target).read().decode('utf-8-sig').rstrip()
        else:
            with open(target, 'r') as f:
                raw_data = f.read().decode('utf-8-sig').rstrip()

        # standardize the file endings
        raw_data = raw_data.replace('\r\n', '\n').replace('\r', '\n')

        if not self.header:
            # use first line if self.header not defined
            current_headers = raw_data.split('\n')[0].split(',')
            raw_data = raw_data[1:]
        else:
            current_headers = self.header

        output = []

        for row in raw_data.split('\n'):
            output.append(
                dict(zip(current_headers, row.split(',')))
            )

        return output