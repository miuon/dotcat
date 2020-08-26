'''Package configuraton for modot (MODular DOtfiles)'''
import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='modot',
    version='0.5.1',
    description='MOdular DOTfiles',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/miuon/modot',
    author='miuon',
    author_email='andrew@miuon.net',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],

    packages=['modot'],
    test_suite='tests',
    python_requires=">=3.7",
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
