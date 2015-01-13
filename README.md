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

##### Current Implemenations:

+ Postgres

##### TODO Implementations:

+ Simple key/value cache (Memcached/Redis)

##### TODO Features:

+ Allow schema input to specify relationships between tables