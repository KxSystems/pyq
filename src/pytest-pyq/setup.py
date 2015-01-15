from setuptools import setup

VERSION = '0.9'
setup(
    name="pytest-pyq",
    py_modules=['pytest_pyq'],
    version=VERSION,

    # the following makes a plugin available to py.test
    entry_points={
        'pytest11': [
            'pytest_pyq = pytest_pyq',
        ]
    },
)
