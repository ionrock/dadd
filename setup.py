#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'flask',
    'python-daemon',
    'click',
    'flask-sqlalchemy',
    'psycopg2',
    # I'd like to use these packages, but they don't seem to be
    # updated vs. core cherrypy.
    #
    # 'cheroot',
    # 'magicbus',
    'cherrypy',
]

setup(
    name='dad',
    version='0.1.0',
    description=('Dad is a remote worker hosts for '
                 'starting and forgetting processes.'),
    long_description=readme + '\n\n' + history,
    author='Eric Larson',
    author_email='eric@ionrock.org',
    url='https://github.com/ionrock/dad',
    packages=[
        'dad',
    ],
    package_dir={'dad':
                 'dad'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='dad',
    entry_points={
        'console_scripts': [
            'dad = dad.cli:run',
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
