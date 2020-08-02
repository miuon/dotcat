from setuptools import setup
setup(
    name='modot',
    version='0.3',
    description='Modular Overengineered Dotfile Organizer and Manager',
    url='https://github.com/miuon/modot',
    author='miuon',
    author_email='miuon@protonmail.com',
    packages=['modot'],

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
