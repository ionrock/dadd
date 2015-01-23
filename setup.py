#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'Flask',
    'Flask-SQLAlchemy',
    'Flask-Admin',
    'Flask-Script',
    'Flask-Migrate',
    'python-daemon',
    'click',
    'psycopg2',
    'cherrypy',
    'erroremail>=0.1.6',
    'PyYAML',
    'requests',
    'wsgi-request-logger',
]

setup(
    name='dadd',
    version='0.2.4',
    description='Dadd administers daemons.',
    long_description=readme + '\n\n' + history,
    author='Eric Larson',
    author_email='eric@ionrock.org',
    url='https://github.com/ionrock/dadd',
    packages=[
        'dadd',
    ],
    package_dir={'dadd':
                 'dadd'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='dadd',
    entry_points={
        'console_scripts': [
            'dadd = dadd.cli:main',
            'dadd-admin = dadd.admin:manage',
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
