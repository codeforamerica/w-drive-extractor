## W-Drive Extractor

The W-Drive Extractor, named after the home of the shared list of contracts, is an attempt to extract and standardize data from spreadsheets, .csvs, and other files for a relational destination.

Current status: in development

### Getting Started

W-Drive Extractor has some external dependencies, which can be installed via pip. It is recommended that you use a virtualenv to manage these.

### Extractors

The Extractor base class is an interface for implementing data extraction from different sources. It requires taking in a `target` which can be a file or URL and two optional params. Headers is the title of the columns that will ultimately be extracted from your store, and dtypes is a list of native python types that each column should have.

##### Current Implementations:

+ Excel (.xls, .xlsx)

##### TODO implementations:

+ Textfile (.csv/.txt)
+ Postgres

### Loaders

The Loader base class is an interface for implementing data loading into new sources. It requires connection parameters (a python dictionary of connection params) and optional schema. The goal is for a single input source (spreadsheet, denormalized table, etc.) to be split into many tables.

##### Current Implementations:

+ Postgres [with relationships and simple deduplication!]

##### TODO Implementations:

+ Simple key/value cache (Memcached/Redis)
+ Other relational data stores

##### TODO Features:

+ Add tests

### Sample Usage

Below is an example of extracting data from Excel and loading it into a local [postgres database](http://postgresapp.com/) with defined relationships. NOTE: This implementation is still fragile and likely to be dependent on the fact that to_relations is the last table in the list below.

    import datetime

    from extractors.excel import ExcelExtractor
    from loaders.postgres import PostgresLoader

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
