from setuptools import setup

setup(
    name='bugmark',
    version='1.0',
    py_modules=['parser'],
    entry_points={
        'console_scripts': [
            'bugmark = parser:main',
        ],
    },
)