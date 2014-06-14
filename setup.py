#!/usr/bin/env python

import os
import sys

from alerta import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name="alerta",
    version=__version__,
    description="Alerta unified command-line tool",
    long_description=readme,
    license="MIT",
    author="Nick Satterly",
    author_email="nick.satterly@theguardian.com",
    url="http://github.com/alerta/python-alerta-client",
    packages=['alerta'],
    install_requires=[
        'argparse',
        'requests',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'alerta = alerta.shell:main'
        ]
    },
    keywords="alerta client unified command line tool",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ]
)
