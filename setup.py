#!/usr/bin/env python

import setuptools

with open('VERSION') as f:
    version = f.read().strip()

with open('README.md') as f:
    readme = f.read()

setuptools.setup(
    name='alerta',
    version=version,
    description='Alerta unified command-line tool and SDK',
    long_description=readme,
    url='http://github.com/alerta/python-alerta',
    license='MIT',
    author='Nick Satterly',
    author_email='nick.satterly@theguardian.com',
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'Click',
        'requests',
        'tabulate',
        'pytz',
        'six'
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
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Monitoring',
    ],
    python_requires='>=3.5'
)
