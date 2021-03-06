from setuptools import setup, find_packages
from os.path import join, dirname
from audience import __version__

setup(
    name='audience',
    version=__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'audience = audience.main:main',
            ]
        },
    install_requires = [
        'tweepy==2.2',
        'Flask==0.10.1'
        ],
)
