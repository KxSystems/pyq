#!/usr/bin/env bash

set -e

export QHOME="/root/q"

echo "* Installing PyQ"
python setup.py install_exe
python setup.py install_qlib
python setup.py install_qext
python setup.py install_scripts
LDFLAGS='--coverage'
CFLAGS='-fno-strict-aliasing -g -O2 --coverage -fprofile-arcs -ftest-coverage'
export CFLAGS LDFLAGS
python setup.py install_lib
unset CFLAGS LDFLAGS

pyq --versions

echo "* Running tests"
pyq -mpytest --pyargs pyq
taskset -c "$CPUS" "${QHOME}/l${BITS}/q" src/pyq/tests/test.p
gcov_path=$(ls -1d build/temp*/src/pyq)
ls -la ${gcov_path}/*{gcno,gcda}
lcov --capture \
     --directory "${gcov_path}" \
     --output-file pyq.info \
     --rc lcov_branch_coverage=1 \
     --base-directory $(pwd)/src/pyq \
     --no-external \
     --derive-func-data
