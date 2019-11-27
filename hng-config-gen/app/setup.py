#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name="gen-rgw",
    version="1.0",
    description="Generates RGW configurations based on YAML files",
    author="Jose Nuñez",
    author_email="jose.nunezmartinez@telefonica.com",
    license="",
    keywords = "rgw hng generator jinja netacad packettracer \
    pythonscript scripts yaml",
    url="https://pdihub.hi.inet/condor/hng_scalation/tree/master/gen-hng",
    packages=find_packages(),
    long_description=long_description,
    scripts=['gen-rgw.py'],
    install_requires=['Jinja2', 'click', 'pyyaml'],
    project_urls={
        'Source': 'https://pdihub.hi.inet/condor/hng_scalation/tree/master/gen-hng',
        'Tracker': 'https://pdihub.hi.inet/condor/hng_scalation/tree/master/gen-hng',
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Utilities",
    ],
)
