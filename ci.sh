#!/usr/bin/env bash

set -ex

export QHOME="/root/q"

echo "* Installing PyQ"

python setup.py install_exe
python setup.py install_qlib
python setup.py install_qext
python setup.py install_scripts
LDFLAGS='--coverage -lgcov'
CFLAGS='--coverage'
export CFLAGS LDFLAGS
python setup.py install_lib
unset CFLAGS LDFLAGS

pyq --versions

echo "* Running tests"
pyq -mpytest --pyargs pyq
taskset -c "$CPUS" "${QHOME}/l${BITS}/q" src/pyq/tests/test.p

echo "* Running lcov"
gcov_path="$(find . -type f -name "*.gcno" -o -name "*.gcda"  -exec dirname {} \; -quit)"
lcov --capture \
     --directory "${gcov_path}" \
     --output-file pyq.info \
     --rc lcov_branch_coverage=1 \
     --base-directory $(pwd)/src/pyq \
     --no-external \
     --derive-func-data
ls -la ${gcov_path}/*{gcno,gcda}
gcov -f -b -c -o "${gcov_path}" src/pyq/_k.c
find . -name \*gcov
