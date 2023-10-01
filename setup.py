"""
setup.py for LeanIX Description Bot

This script is used to package and distribute the LeanIX Description Bot as a Python package.
It includes information such as the package name, version, dependencies, and entry points.

For usage instructions, please refer to the README.md file.

For more information about packaging Python projects, see the Python Packaging Authority:
https://packaging.python.org/
"""

from setuptools import setup, find_packages

setup(
    name='leanix_description',
    version='1.0.0',
    description='This is a Flask application designed to handle webhook from LeanIX. It includes rate limiting, user authentication, and security headers for enhanced security.',
    author='Björn',
    author_email='your@email.com',
    url='https://github.com/bc-bjoern/leanix_description',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'openai',
        'pandas',
        'requests',
        'python-decouple',
        'flask-limiter'
    ],
    entry_points={
        'console_scripts': [
            'leanix_description = leanix_description.ld:main'
        ]
    },
)
