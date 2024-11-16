from setuptools import setup, find_packages
from os import path
working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='geo_measurements',
    version='0.0.1',
    url='https://github.com/b3n3c/geo_measurements',
    author='b3n3c',
    description='This Python project delivers a suite of geospatial utility functions for precise geographic coordinate measurements.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "utm>=0.7.0",
        "geographiclib>=2.0",
        "shapely>=2.0",
        "pyproj>=3.7.0",
        "geopandas>=1.0.0",
    ]
)