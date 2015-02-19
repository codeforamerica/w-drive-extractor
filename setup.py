from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# convert .md to .rst; from here: http://stackoverflow.com/questions/10718767/have-the-same-readme-both-in-markdown-and-restructuredtext
try:
    from pypandoc import convert
    long_description = convert(path.join(here, 'README.md'), 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    long_description = ''

with open('requirements/pkg.txt') as f:
    required = f.read().splitlines()

setup(
    name='wextractor',
    url='https://github.com/codeforamerica/w-drive-extractor',
    license='MIT',
    version='0.1.0',
    author='Ben Smithgall',
    author_email='bsmithgall@codeforamerica.org',

    description='Extract flat data and load it as relational data',
    long_description=long_description,

    packages=find_packages(),
    install_requires=required,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
