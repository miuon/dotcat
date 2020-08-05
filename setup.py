'''Package configuraton for modot (MODular DOtfiles)'''
from setuptools import setup
setup(
    name='modot',
    version='0.4',
    description='MOdular DOTfiles',
    url='https://github.com/miuon/modot',
    author='miuon',
    author_email='andrew@miuon.net',
    packages=['modot'],
    test_suite='tests',

    python_requires=">=3.5",
    install_requires=[
        'chevron',
        'Click',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'modot=modot.cli:cli',
        ],
    },
)
