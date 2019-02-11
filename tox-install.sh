#!/usr/bin/env bash

qhome=${TOX_QHOME:-${HOME}/q}

# First, install q
if [ -f "${qhome}/q.k" ]
then
    QHOME=${VIRTUAL_ENV}/q
    if [ -f "${QHOME}/q.k" ]
    then
        echo "Q is already installed in ${QHOME}"
    else
        mkdir ${QHOME}
        cp ${qhome}/q.k ${QHOME}
        for q in ${qhome}/*/q
        do
            arch=$(basename $(dirname $q))
            echo "Found q in ${qhome}/${arch}"
            mkdir ${QHOME}/${arch}
            cp -p ${qhome}/${arch}/q ${QHOME}/${arch}/q
        done
    fi
elif [ -f "${QZIP}" ]; then
    QHOME=${VIRTUAL_ENV}/q
    unzip -q "${QZIP}" -d "${QHOME}"
elif [ -f "${HOME}/Downloads/m64.zip" ]; then
    QHOME=${VIRTUAL_ENV}/q
    unzip -q -n "${HOME}/Downloads/m64.zip" -d "${VIRTUAL_ENV}/q"
elif [ -f "${HOME}/Downloads/m32.zip" ]; then
    QHOME=${VIRTUAL_ENV}/q
    unzip -q -n "${HOME}/Downloads/m32.zip" -d "${VIRTUAL_ENV}/q"
else
    echo "Could not find q in ${qhome}, exiting"
    exit -1
fi
export QHOME

# Now call pip install
exec ${VIRTUAL_ENV}/bin/pip install --no-binary pyq $*
