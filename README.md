[![Build Status](https://travis-ci.org/codeforamerica/w-drive-extractor.svg?branch=master)](https://travis-ci.org/codeforamerica/w-drive-extractor)

# W-Drive Extractor (wextractor)

The W-Drive Extractor (or the wextractor), named after the home of the shared list of contracts in the City of Pittsburgh, is an attempt to extract and standardize data from spreadsheets, .csvs, and other files for a relational destination.

## Using the W-Drive-Extractor

### Getting Started

#### Installation

W-Drive Extractor is available as a pre-release package via pypi. You can install via pip:

    pip install wextractor --pre

#### Usage

Here's a simple example of extracting data from the Pittsburgh Police blotter:

    >>> from wextractor.extractors import CsvExtractor
    >>> extractor = CsvExtractor('http://apps.pittsburghpa.gov/police/arrest_blotter/arrest_blotter_Monday.csv')
    >>> data = extractor.extract()
    >>> print data
    >>> [{u'NEIGHBORHOOD': u'Spring Garden', u'DESCRIPTION': u'Flight to Avoid Apprehension  Tri...

For a more complex example of usage, please see the bottom of this file.

##### TODO Features:

+ Add cli support
+ Change `loader` and `extractor` methods to use kwargs
+ Add better exception messaging for the `load` and `extract` methods

## Developing W-Drive-Extractor

### Getting Started

W-Drive Extractor has some external dependencies, which can be installed via pip. It is recommended that you use a [virtualenv](https://github.com/codeforamerica/howto/blob/master/Python-Virtualenv.md) to manage these.

The W-Drive-Extractor is an object-oriented application. In order to use it, you must first *extract* data from its original source using an `Extractor`'s `extract` method (the `ExcelExtractor` is currently the only supported example). Once the data is extracted, it can then be *loaded* back into some other datasource using a `Loader`'s `load` method. (only `PostgresLoader` has been implemented thus far). For a more detailed example on how this works, check out the sample usage at the bottom of this file.

### Extractors

The Extractor base class is an interface for implementing data extraction from different sources. It requires taking in a `target` which can be a file or URL and two optional params. Headers is the title of the columns that will ultimately be extracted from your store, and dtypes is a list of native python types that each column should have.

##### Current Implementations:

+ Excel (.xls, .xlsx)
+ Comma-Separated Values (.csv)

##### TODO implementations:

+ Generic Text Files (.txt)
+ Postgres
+ MS Access

### Loaders

The Loader base class is an interface for implementing data loading into new sources. It requires connection parameters (a python dictionary of connection params) and optional schema. The goal is for a single input source (spreadsheet, denormalized table, etc.) to be split into many tables.

##### Current Implementations:

+ Postgres [with relationships and simple deduplication!]

##### TODO Implementations:

+ Simple key/value cache (Memcached/Redis)
+ Other relational data stores

### Tests

Tests are located in the `test` directory. To run the tests, run

    PYTHONPATH=. nosetests test/

from inside the root directory. For more coverage information, run

    PYTHONPATH=. nosetests test/ -vs --with-coverage --cover-package=wextractor --cover-erase

### Detailed Sample Usage

Below is an example of extracting data from Excel and loading it into a local [postgres database](http://postgresapp.com/) with defined relationships. NOTE: This implementation is still fragile and likely to be dependent on the fact that to_relations is the last table in the list below.

    import datetime

    from wextractor.extractors import ExcelExtractor
    from wextractor.loaders import PostgresLoader

    one_sheet = ExcelExtractor(
        'files/one sheet contract list.xlsx',
        dtypes=[
            unicode, unicode, unicode, int, unicode,
            unicode, datetime.datetime, int, unicode, unicode,
            unicode, unicode, unicode, unicode, unicode,
            unicode, unicode, unicode, unicode
        ]
    )
    data = one_sheet.extract()

    loader = PostgresLoader(
        {'database': 'w_drive', 'user': 'bensmithgall', 'host': 'localhost'},
        [{
            'table_name': 'contract',
            'to_relations': [],
            'from_relations': ['company'],
            'pkey': None,
            'columns': (
                ('description', 'TEXT'),
                ('notes', 'TEXT'),
                ('contract_number', 'VARCHAR(255)'),
                ('county', 'VARCHAR(255)'),
                ('type_of_contract', 'VARCHAR(255)'),
                ('pa', 'VARCHAR(255)'),
                ('expiration', 'TIMESTAMP'),
                ('spec_number', 'VARCHAR(255)'),
                ('controller_number', 'INTEGER'),
                ('commcode', 'INTEGER')
            )
        },
        {
            'table_name': 'company_contact',
            'to_relations': [],
            'from_relations': ['company'],
            'pkey': None,
            'columns': (
                ('contact_name', 'VARCHAR(255)'),
                ('address_1', 'VARCHAR(255)'),
                ('address_2', 'VARCHAR(255)'),
                ('phone_number', 'VARCHAR(255)'),
                ('email', 'VARCHAR(255)'),
                ('fax_number', 'VARCHAR(255)'),
                ('fin', 'VARCHAR(255)'),
            )
        },
        {
            'table_name': 'company',
            'to_relations': ['company_contact', 'contract'],
            'from_relations': [],
            'pkey': None,
            'columns': (
                ('company', 'VARCHAR(255)'),
                ('bus_type', 'VARCHAR(255)'),
            )
        }]
    )

    loader.load(data, True)
