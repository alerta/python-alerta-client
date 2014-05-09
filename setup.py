#!/usr/bin/env python

import setuptools

with open('README.rst') as f:
    long_description = f.read()

setuptools.setup(
    name="alerta",
    version='3.1.0',
    description="Alerta unified command-line tool",
    long_description=long_description,
    license="MIT",
    author="Nick Satterly",
    author_email="nick.satterly@theguardian.com",
    url="http://github.com/alerta/python-alerta-client",
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'argparse',
        'requests',
        'pytz'
    ],
    keywords="alerta command line",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ],
    entry_points={
        'console_scripts': [ 'alerta = alerta.shell:main']
    }
)
