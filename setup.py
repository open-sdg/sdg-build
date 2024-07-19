# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

setup(name='sdg',
      version='2.3.0',
      description='Build SDG data and metadata into output formats',
      url='https://github.com/open-sdg/sdg-build',
      author='Doug Ashton',
      author_email='douglas.j.ashton@gmail.com',
      license='MIT',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'check', 'reset']),
      zip_safe=False,
      package_data={'sdg': [
        os.path.join('outputs', 'sdmx_global_content_constraints.csv'),
      ]},
      include_package_data=True,
      python_requires='>=3.7',
      install_requires=[
        'rfc3986<2',
        'pyyaml',
        'gitpython',
        'numpy<2',
        'pandas>=1,<2',
        'yamlmd',
        'jsonschema',
        'requests',
        'humanize',
        'unicode-slugify',
        'sdmx1>=2.6.1',
        'frictionless>=4,<5',
        'csvw',
        'mammoth',
        'pyquery',
        'pyjstat',
        'Jinja2',
        'natsort',
        'openpyxl==3.1.0',
        'pydantic>=1,<2',
        'typer==0.11.0',
      ],
      dependency_links=[
        "git+https://github.com/dougmet/yamlmd",
    ])
