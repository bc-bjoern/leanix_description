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
