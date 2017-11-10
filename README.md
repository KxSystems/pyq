# PyQ - Python for kdb+
[![Build Status](https://travis-ci.org/abalkin/pyq.svg?branch=travis)](https://travis-ci.org/abalkin/pyq)
[![Documentation Status](https://readthedocs.org/projects/pyq/badge/?version=latest)](http://pyq.readthedocs.io/en/latest/?badge=latest)
[![PyPI Version](https://img.shields.io/pypi/v/pyq.svg)](https://pypi.python.org/pypi/pyq)
[![LGTM](https://img.shields.io/badge/lgtm-review-blue.svg)](https://lgtm.com/projects/g/enlnt/pyq)

[PyQ][2] brings the [Python programming language][4] to the [kdb+ database][5]. It allows
developers to integrate Python and q codes seamlessly in one application.
This is achieved by bringing the Python and q interpreters into the same process
so that code written in either of the languages operates on the same data.
In PyQ, Python and q objects live in the same memory space and share the same
data.

## Installation

```bash
pip install pyq
```

For detailed installation instructions see [installation instructions][1].

## Usage

For Python programmers:

```bash
$ pyq
```
```python
>>> from pyq import q
>>> 1 + q.til(10)
k('1 2 3 4 5 6 7 8 9 10')
```

or run your Python script as

```bash
pyq [python options] python-script
```

For q programmers:

```bash
$ q
```
```q
q)p)from math import hypot  / prefix python code with p)
q)p)q.h = hypot             / import a python function
q)h 3 4                     / call the python function from q
5f
```

## Documentation

Documentation is available on the [PyQ homepage][2].

## Testing

Use [tox][3] to run tests.

```bash
cd path/to/pyq/source
tox
```

[1]: https://code.kx.com/q/interfaces/pyq/install/
[2]: https://code.kx.com/q/interfaces/pyq
[3]: https://tox.readthedocs.io/en/latest
[4]: https://www.python.org/about
[5]: https://kx.com
