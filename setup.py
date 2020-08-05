'''Package configuraton for dotcat (DOTfile conCATenator)'''
from setuptools import setup
setup(
    name='dotcat',
    version='0.5',
    description='DOTfile conCATenator',
    url='https://github.com/miuon/dotcat',
    author='miuon',
    author_email='andrew@miuon.net',
    packages=['dotcat'],
    test_suite='tests',

    python_requires=">=3.5",
    install_requires=[
        'chevron',
        'Click',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'dotcat=dotcat.cli:cli',
        ],
    },
)
