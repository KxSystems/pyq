#!/usr/bin/env bash

eval $(pyq -c 'import os;print("QHOME=%s;QBIN=%s" % (os.getenv("QHOME"), os.getenv("QBIN")))')
export QHOME
if [ $(uname) = "Linux" ]; then
  TS="taskset -c $CPUS"
else
  TS=''
fi
if [[ "${KDB_VER}" > "3.4" ]]; then
    $TS $QBIN $1 -q
else
    echo "Skipping tests for KDB_VER=${KDB_VER}"
fi
