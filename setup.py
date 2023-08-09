# -*- coding: utf-8 -*-

""" Setup v6_healthai_dashboard_py as a Python package
"""
from os import path
from codecs import open
from setuptools import setup, find_packages


# Get current directory
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Setup the package
setup(
    name='v6_healthai_dashboard_py',
    version='1.0.0',
    description='HealthAI: vantage6 algorithm to compute TNM statistics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/aiaragomes/v6-healthai-dashboard-py',
    license='MIT License',
    keywords=['Vantage6', 'Federated Algorithms'],
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'vantage6-client'
    ]
)
