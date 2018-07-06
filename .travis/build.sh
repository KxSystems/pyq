#!/usr/bin/env bash

set -e

if [ -n "${CONDA_FORCE_32BIT}" ]; then
   arch="-m32 "
else
   arch=""
fi
if [[ "${TRAVIS_OS_NAME}" == "linux" ]]; then
    lgcov=" -lgcov";
fi
python setup.py config
python setup.py install_qlib
python setup.py install_scripts
LDFLAGS="${arch}--coverage${lgcov}"
CFLAGS="${arch}--coverage"
CC="gcc $LDFLAGS"
export CFLAGS LDFLAGS CC
python setup.py build_ext --build-temp .
python setup.py install_lib
python setup.py install_exe
python setup.py install_qext
unset CFLAGS LDFLAGS CC
