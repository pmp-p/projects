#!/bin/sh

APK=$1
PYVER=${PYVER:-"3.8"}

export ROOT=$(pwd)

# TODO: replace by a download of pydk-min
export PYDK=${PYDK:-$(realpath $ROOT/..)}


if [ -f ${PYDK}/aosp/bin/activate ]
then
    echo " * Using HOST python from PyDK build"

    . ${PYDK}/aosp/bin/activate

    HOST=$(echo -n ${PYDK}/aosp)
    echo HOST=$HOST

    PYTHON=$(echo -n ${HOST}/bin/python3.?)
    export PIP="$PYTHON -u -B -m pip"
    export LD_LIBRARY_PATH="${HOST}/lib64:${HOST}/lib:$LD_LIBRARY_PATH"
    export PIPU=""
else

    for py in 9 8 7 6 5
    do
        if command -v python3.${py}
        then
            export PYTHON=$(command -v python3.${py})
            break
        fi
    done
    export PYTHON=${PYTHON:-$(command -v python3)}
    export PIP="$PYTHON -u -B -m pip"
    export PIPU="--user"
    export PATH=~/.local/bin:$PATH
    echo " * Using non PyDK-sdk cPython3 ${PYTHON}"
fi


if [ -f ${TEMPLATE:-${PYDK}/briefcase-android-gradle-template}/cookiecutter.json ]
then
    TEMPLATE=${TEMPLATE:-${PYDK}/briefcase-android-gradle-template}
else
    TEMPLATE="https://github.com/pmp-p/briefcase-android-gradle-template --checkout 3.8p"
fi



echo "

Build config
----------------------------
         APK : $APK
        PYDK : ${PYDK}
      EM SDK : ${PYDK}/emsdk
    projects : ${ROOT}
 pip install : $PIP install $PIPU
    TEMPLATE : $TEMPLATE
----------------------------

"




