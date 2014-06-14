#!/usr/bin/env python

import setuptools

with open('README.rst') as f:
    long_description = f.read()

execfile('alerta/version.py')

setuptools.setup(
    name="alerta",
    version=__version__,
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
