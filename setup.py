#!/usr/bin/env python

import os

import setuptools


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setuptools.setup(
    name='alerta',
    version=read('VERSION'),
    description='Alerta unified command-line tool and SDK',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/guardian/python-alerta',
    license='Apache License 2.0',
    author='Nick Satterly',
    author_email='nfsatterly@gmail.com',
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'Click',
        'requests',
        'requests_hawk',
        'tabulate',
        'pytz'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'alerta = alertaclient.cli:cli'
        ]
    },
    keywords='alerta client unified command line tool sdk',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Monitoring',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    python_requires='>=3.8'
)
