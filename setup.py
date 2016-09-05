#!/usr/bin/env python

import setuptools

with open('VERSION') as f:
    version = f.read().strip()

with open('README.md') as f:
    readme = f.read()

setuptools.setup(
    name="alerta",
    version=version,
    description="Alerta unified command-line tool and SDK",
    long_description=readme,
    license="MIT",
    author="Nick Satterly",
    author_email="nick.satterly@theguardian.com",
    url="http://github.com/alerta/python-alerta",
    packages=['alertaclient'],
    install_requires=[
        'argparse',
        'requests',
        'pytz'
    ],
    entry_points={
        'console_scripts': [
            'alerta = alertaclient.shell:main'
        ]
    },
    keywords="alerta client unified command line tool sdk",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ]
)
