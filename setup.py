# -*- coding: utf-8 -*-

from setuptools import setup
import re

version = ''
with open('expenses/__init__.py', 'r') as f:
    version = re.search(r'__version__\s*=\s*\'([\d.]+)\'', f.read()).group(1)

with open('README.rst') as f:
    readme = f.read()

with open('HISTORY.rst') as f:
    history = f.read()

setup(
    name='expenses',
    version=version,
    author='Nick Frost',
    author_email='nickfrostatx@gmail.com',
    url='https://github.com/nickfrostatx/expenses',
    description='Roommate expense splitting.',
    long_description=readme + '\n\n' + history,
    packages=['expenses'],
    package_data={
        'expenses': [
            'static/*/*',
            'templates/*/*.html',
        ],
    },
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'bcrypt',
        'redis',
    ],
    extras_require={
        'testing': [
            'blinker',
            'fakeredis',
            'pytest',
            'pytest-cov',
            'pytest-pep8',
            'pytest-pep257',
        ],
    },
    license='MIT',
    keywords='expenses',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
