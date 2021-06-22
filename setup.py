from setuptools import setup

setup(
    name='large-file-generator',
    version='1.0.0',
    py_modules=['generator'],
    install_requires=[
        'Click', 'humanfriendly'
    ],
    entry_points={
        'console_scripts': [
            'large-file-generator = generator:cli',
        ],
    },
)
