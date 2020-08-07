"""
Smartphoniker Shop
Copyright 2020, Leon Morten Richter
Author: Leon Morten Richter <leon.morten@gmail.com>
"""
import os

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

# Can't use 'from vigil_reporter import __version__' because
# setup.py imports from the package. This means that python
# will try importing the library while processing the setup.py
# (ie. before any of the dependencies get installed).
VERSION = None
with open(os.path.join('project', '__init__.py')) as f:
    for line in f:
        if line.strip().startswith('__version__'):
            VERSION = line.split('=')[1].strip()[1:-1].strip()
            break

REQS: list = []
with open(os.path.join('requirements', 'requirements_base.txt')) as f:
    [REQS.append(line) for line in f.readlines()]

with open(os.path.join('requirements', 'requirements_prod.txt')) as f:
    [REQS.append(line) for line in f.readlines()]

setup(
    name='smartphoniker-shop',
    version=VERSION,
    description='',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Leon Morten Richter',
    author_email='leon.morten@gmail.com',
    url='https://github.com/M0r13n/smartphoniker-shop',
    license="MIT",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=REQS
)
