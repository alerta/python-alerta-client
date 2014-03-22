#!/usr/bin/env python

import setuptools
from alertaclient import __version__

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name="alertaclient",
    version=__version__,
    description="Alerta client API for python",
    long_description=long_description,
    license="MIT",
    author="Nick Satterly",
    author_email="nick.satterly@theguardian.com",
    url="http://github.com/alerta/python-alertaclient",
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'requests'
    ],
    keywords="alerta library",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ],
    zip_safe=True
)