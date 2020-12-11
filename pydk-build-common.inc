#!/bin/bash sourced

APK=$1
PYVER=${PYVER:-"3.8"}


export ROOT=$(pwd)

export LIBVER=$(echo  $PYVER|cut -c1,3)

# TODO: replace by a download of pydk-min
export PYDK=${PYDK:-$(realpath $ROOT/..)}


export PYTHONDONTWRITEBYTECODE=1



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




function do_pip
{
    echo " * processing pip requirement for application [$1]"
    # pip install -r requirements.txt
    # pip download --dest ../*/src/pip --no-binary :all: -r requirements-jni.txt
    mkdir -p assets/packages
    /bin/cp -Rfxpvu ${PYDK}/assets/python$PYVER/* assets/python$PYVER/
    echo "==========================================================="
    echo "${APKUSR}/lib/python${PYVER}/site-packages/ *filtered* => assets/packages/ "
    echo "==========================================================="

    for req in $(find ${PYDK}/assets/packages/ -maxdepth 1  | egrep -v 'info$|egg$|pth$|txt$|/$')
    do
        if find $req -type f|grep ${LIBEXT}$
        then
            echo " * can't add package : $(basename $req) not pure python"
        else
            echo " * adding pure-python pip package : $(basename $req)"
            cp -ru $req assets/packages/
        fi
    done

}



