symba
=====

[![](https://dev.azure.com/lycantropos/symba/_apis/build/status/lycantropos.symba?branchName=master)](https://dev.azure.com/lycantropos/symba/_build/latest?definitionId=34&branchName=master)
[![](https://readthedocs.org/projects/symba/badge/?version=latest)](https://symba.readthedocs.io/en/latest "Documentation")
[![](https://codecov.io/gh/lycantropos/symba/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/symba "Codecov")
[![](https://img.shields.io/github/license/lycantropos/symba.svg)](https://github.com/lycantropos/symba/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/symba.svg)](https://badge.fury.io/py/symba "PyPI")

In what follows `python` is an alias for `python3.5` or `pypy3.5`
or any later version (`python3.6`, `pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions
```bash
python -m pip install --upgrade pip setuptools
```

### User

Download and install the latest stable version from `PyPI` repository
```bash
python -m pip install --upgrade symba
```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/symba.git
cd symba
```

Install dependencies
```bash
python -m pip install -r requirements.txt
```

Install
```bash
python setup.py install
```

Usage
-----
```python
>>> from symba.base import Expression, sqrt
>>> golden_ratio = (1 + sqrt(5)) / 2
>>> isinstance(golden_ratio, Expression)
True
>>> golden_ratio * golden_ratio == golden_ratio + 1
True
>>> 1 / golden_ratio == golden_ratio - 1
True
>>> def fibonacci(index: int) -> Expression:
...     """
...     Based on:
...     https://en.wikipedia.org/wiki/Golden_ratio#Relationship_to_Fibonacci_sequence
...     """
...     golden_ratio_power = golden_ratio ** index
...     return ((golden_ratio_power - (-1) ** index / golden_ratio_power)
...             / sqrt(5))
>>> fibonacci(0) == 0
True
>>> fibonacci(1) == 1
True
>>> fibonacci(100) == 354224848179261915075
True

```

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose release
```

Bump version
```bash
bump2version --verbose release
```

This will set version to `major.minor.patch`.

### Running tests

Install dependencies
```bash
python -m pip install -r requirements-tests.txt
```

Plain
```bash
pytest
```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
