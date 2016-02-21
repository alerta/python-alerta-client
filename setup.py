#!/usr/bin/env python

import setuptools

with open('VERSION') as f:
    version = f.read().strip()

with open('README.md') as f:
    readme = f.read()

setuptools.setup(
    name="alerta",
    namespace_packages=['alerta'],
    version=version,
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Monitoring',
    ]
)
