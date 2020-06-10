from setuptools import setup
setup(
    name='modot',
    version='0.1',
    description='Modular Overengineered Dotfile Organizer and Manager',
    url='https://github.com/miuon/modot',
    author='miuon',
    author_email='miuon@protonmail.com',

    install_requires=[
        'chevron',
        'Click',
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'modot=modot:modot',
        ],
    },
)
