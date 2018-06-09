#!/usr/bin/env bash

set -e

if [ "${BITS}" = "32" ]; then
  curl -O https://kx.com/$X/3.5/linuxx86.zip
  unzip -d $CONDA_PREFIX linuxx86.zip
  rm -f $CONDA_PREFIX/q/q.q
else
  conda install -c kx kdb
  echo -n $QLIC_KC | base64 --decode > $CONDA_PREFIX/q/kc.lic
fi
