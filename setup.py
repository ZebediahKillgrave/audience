from setuptools import setup, find_packages
from os.path import join, dirname
import audience

setup(
    name='audience',
    version=audience.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'audience = aacc.main:main',
            ]
        },
    install_requires = [
        'tweepy==2.2'
        ],
)
