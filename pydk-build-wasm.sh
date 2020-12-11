#!/bin/bash
reset

export LIBEXT=a

. pydk-build-common.inc


export TOOLCHAIN_HOME=${TOOLCHAIN_HOME:-$(realpath ${PYDK}/emsdk)}

#p3webgldisplay.a  pandagles2.a
PANDA3D_CPP=""

for l in pandagles2.a p3openal_audio.a p3dtool.a p3dtoolconfig.a p3interrogatedb.a p3direct.a\
 pandabullet.a pandaexpress.a panda.a p3framework.a
do
    lib=${PYDK}/wasm/build-wasm/panda3d-wasm/lib/lib${l}
    if [ -f $lib ]
    then
        PANDA3D_CPP="$PANDA3D_CPP $lib"
    else
        echo " ERROR : missing link lib $lib"
        exit 1
    fi
done


PANDA3D_PY=""

for l in py.panda3d.interrogatedb.cpython-${LIBVER}-wasm.a py.panda3d.core.cpython-${LIBVER}-wasm.a \
 py.panda3d.bullet.cpython-${LIBVER}-wasm.a py.panda3d.direct.cpython-${LIBVER}-wasm.a
do
    lib=${PYDK}/wasm/build-wasm/panda3d-wasm/lib/lib${l}
    if [ -f $lib ]
    then
        PANDA3D_PY="$PANDA3D_PY $lib"
    else
        echo " ERROR : missing link lib $lib"
        exit 1
    fi
done


APKLIB=${PYDK}/wasm/apkroot-wasm/usr/lib

PYALL="$APKLIB/libpython${PYVER}.a $APKLIB/libssl.a $APKLIB/libcrypto.a"


export LIBDIR=${PYDK}/wasm/apkroot-wasm/usr/lib
export INCDIR=${PYDK}/wasm/apkroot-wasm/usr/include


reset
echo " Building $1 with ${TOOLCHAIN_HOME} and ${PYDK} from ${ROOT}"
echo "----------------------"


echo


function install_run
{
    APK_FILE=$1
    echo todo run view webserv + browser instance
    if [ -f python.wasm ]
    then
        echo "  * Running $APK_FILE press ctrl+c to terminate"

 PYTHONPATH=. \
 LD_LIBRARY_PATH=${PYDK}/host/lib:${PYDK}/host/lib64:${LD_LIBRARY_PATH} \
 ${PYDK}/host/bin/python${PYVER} -u -B -m pythons.js -d $(pwd) ${WEB:-"8000"}
        echo "bye"
    fi
}


function do_stdlib
{

    if [ -f python${PYVER}.zip ]
    then
        echo stdlib zip ready
    else
        echo " * prepare stdlib for zip archiving"

        rm -rf assets/python$PYVER
        mkdir -p assets/python$PYVER
        /bin/cp -Rfxpvu ${PYDK}/src/python3-wasm/Lib/. assets/python$PYVER/|egrep -v "test/|lib2to3" | wc -l
        rm -rf assets/python$PYVER/test assets/python$PYVER/unittest
        rm -rf assets/python$PYVER/lib2to3 assets/python$PYVER/site-packages

        echo " * overwriting with specific stdlib $PYVER platform support (zipimport)"

        # copy specific python platform support
        for ver in common 3.8 3.9
        do
            cp -Rfxp ${PYDK}/sources.py/cpython/wasm/${ver}/. assets/python$PYVER/
        done

        if true
        then
            WD=$(pwd)
            cd assets/python${PYVER}
            zip "${WD}/python${PYVER}.zip" -r .
            cd "${WD}"
            rm -rf assets/python$PYVER
        else
            echo " >>>>>>>>>>>>>>>>> stdlib not zipped <<<<<<<<<<<<<<<<<<"
        fi
    fi
}


function do_clean
{
    echo " * Removing old builds"

    # so install_run won't pick up last build in case of failure.
    echo todo remove webapk

    # cleanup potentially incompatible bytecode
    rm -rf $(find assets/ -type d|grep /__pycache__$)

}






if cd $APK 2>/dev/null
then
    echo "Project [${1}] found"
    cd ..
else

    echo "Initializing project [${1}] with TEMPLATE=$TEMPLATE
 press <enter> to continue"

    read

    $PIP install $PIPU --upgrade pip

    $PIP install $PIPU cookiecutter

    export COOKIECUTTER_CONFIG=cookiecutter.config
    mkdir -p templates replay

    cat > $COOKIECUTTER_CONFIG <<END
    cookiecutters_dir: templates
    replay_dir: replay
END


    cat > templates/cookiecutter.json <<END
    {
      "module_name": "pyweb",
      "bundle": "org.beerware",
      "app_name": "EmptyApp",
      "formal_name": "$1",
      "_copy_without_render": [
        "gradlew",
        "gradle.bat",
        "gradle/wrapper/gradle-wrapper.properties",
        "gradle/wrapper/gradle-wrapper.jar",
        ".gitignore",
        "*.png"
      ]
    }
END

    cookiecutter $TEMPLATE
fi



. ${TOOLCHAIN_HOME}/emsdk_env.sh


if cd $1
then
    if echo $@ |grep clean
    then
        do_clean

        # go deeper.
        echo "<ctrl+C> to abort, i WILL destroy : prebuilt" assets/python3.? assets/packages
        read cont
        rm -rf  prebuilt assets/python3.? assets/packages

    else
        echo " * syncing stdlib for $PYVER"

        mkdir -p assets/python$PYVER/ assets/packages/

        mkdir -p lib

        # copy generic python platform support
        cp -Rfxpvu ${PYDK}/sources.py/common/. assets/

# for wapy
        cp -Rfxpu ${PYDK}/wasm/build-wasm/panda3dffi-wasm/direct/ assets/packages/

# for cpy
        cp -Rfxpu ${PYDK}/wasm/build-wasm/panda3d-wasm/direct/ assets/packages/

        # copy specific python interpreter support
        cp -Rfxpv ${PYDK}/sources.py/cpython/packages/. assets/packages/

        # copy specific python platform support
        echo "FIXME use APK-ZIP as stdlib"

        # copy test framework
        cp -Rfxpvu ${PYDK}/wapy-lib/pythons ./assets/

        # copy readline support
        cp -fxpvu ${PYDK}/wapy-lib/readline/pyreadline.py ./assets/

        # todo move test folder with binary cmdline support into separate archive
        # until testsuite is fixed.
        echo " * Copy/Update prebuilt from ${PYDK}/prebuilt for local project"
        echo 'skipped'
        #/bin/cp -Rfxpvu ${PYDK}/prebuilt ./ |wc -l

        echo " * Copy/Update prebuilt from ${PYDK}/prebuilt.aosp for local project (pip+thirdparty modules)"
        echo 'skipped'
        #/bin/cp -Rfxpvu ${PYDK}/prebuilt.wasm/* ./prebuilt/ |wc -l

        for ARCH in "wasm"
        do
            echo " * Copy/Update include from $(echo ${PYDK}/*/apkroot-$ARCH/usr) for local project"
            /bin/cp -Rfxpvu ${PYDK}/*/apkroot-${ARCH}/usr/include ./prebuilt/$ARCH/ |wc -l

            echo " * Copy/Update prebuilt thirdparty libs from $(echo ${PYDK}/*/apkroot-$ARCH/usr) for local project"
            echo 'skipped NO DLOPEN yet'
            #/bin/cp -Rfxpvu ${PYDK}/*/apkroot-${ARCH}/usr/lib/lib*.so ./prebuilt/$ARCH/ |wc -l

        done

        do_stdlib ${APK}

        do_pip ${APK}


        # copy application files
        cp -aRfxp ../$1.app/assets/. ./assets/


        # **************  those patches should not apply to stdlib as it's better zipped (for now) *****************
        if [ -d ../$APK.app/patches ]
        then
            echo " Applying user patches"
            cp -Rfvpxu ../$APK.app/patches/. ./assets/
        fi



        # maybe stdlib not zipped ( testsuite case )

        if [ -f assets/python${PYVER}.zip ]
        then
            echo " * stdlib is packed assume patching done"
        else
            echo " * patching stdlib"
            #/bin/cp -aRfx ${PYDK}/sources.py/cpython/stdlib/python${PYVER}/. assets/python${PYVER}/
        fi

        do_clean ${APK}

        shift 1


EMOPTS="-s ERROR_ON_UNDEFINED_SYMBOLS=1 -s LLD_REPORT_UNDEFINED=1"
EMOPTS="$EMOPTS -s ENVIRONMENT=web -s USE_ZLIB=1 -s SOCKET_WEBRTC=0 -s SOCKET_DEBUG=1"
EMOPTS="$EMOPTS -s USE_ZLIB=1 -s NO_EXIT_RUNTIME=1"
EMOPTS="$EMOPTS -s EXPORT_ALL=1"

#black or white canvas ?
#EMOPTS="$EMOPTS -s OFFSCREENCANVAS_SUPPORT=1"

# NEEDED : emscripten_glReadBuffer
EMOPTS="$EMOPTS -s USE_WEBGL2=1"

# libgl-webgl2.a...
# EMOPTS="$EMOPTS -s USE_WEBGL2=1 -s FULL_ES2=1"

EMOPTS="$EMOPTS -s USE_ZLIB=1 -s USE_LIBPNG=1"

# RuntimeError: abort
# Assertion failed: Missing signature argument to addFunction: function _eglWaitGL()
# -s USE_SDL=2

#

# dups !
# -s USE_HARFBUZZ=1  -s USE_BULLET=1 -s USE_FREETYPE=1 -s USE_OGG=1


#EMOPTS="$EMOPTS -s USE_VORBIS=1"

# -s GL_DEBUG=1


#-s FULL_ES3=1 -s MIN_WEBGL_VERSION=2


DBG="-g1 -O2 -s LZ4=0 -s ASSERTIONS=1 -s DEMANGLE_SUPPORT=1 -s TOTAL_STACK=29360128 -s TOTAL_MEMORY=512MB"
# -s LLD_REPORT_UNDEFINED=1 --source-map-base http://localhost:8000/"
#DBG="-g4 -O0 -s LZ4=0 -s ASSERTIONS=2 -s DEMANGLE_SUPPORT=1 -s TOTAL_STACK=14680064 -s TOTAL_MEMORY=512MB --source-map-base http://localhost:8000"



echo "================================================================="
echo $EMOPTS
echo "          -------------------------------------------"
echo $DBG
echo "================================================================="

    PYLIB="$LIBDIR/libpython${PYVER}.a $LIBDIR/libssl.a $LIBDIR/libcrypto.a"
if false
then
    em++ $DBG -s ERROR_ON_UNDEFINED_SYMBOLS=1 -s LLD_REPORT_UNDEFINED=1 -s LINKABLE=1 -s EXPORT_ALL=1 \
 -fpic -shared -o libpp3d.so -L.\
 ${PYDK}/wasm/build-wasm/panda3d-wasm/lib/libp3*.a \
 ${PYDK}/wasm/build-wasm/panda3d-wasm/lib/libpa*.a \
 $PANDA3D_PY $PYLIB

fi
    #em++ -fpic   -shared -o libpp3d.so  $PYLIB

    #emcc $DBG $EMOPTS -fpic -static -r -o libpp3d.bc $PANDA3D_PY libp3d.bc

echo "
PYLIB=$PYLIB

PANDA3D_CPP=$PANDA3D_CPP

PANDA3D_PY=$PANDA3D_PY
=================================================================

"

    emcc -s MAIN_MODULE=1 --memory-init-file 0 $DBG $EMOPTS \
 -s 'EXTRA_EXPORTED_RUNTIME_METHODS=["ccall", "cwrap", "getValue", "stringToUTF8"]' \
 -I${INCDIR} -I${INCDIR}/python${PYVER} \
 --preload-file ./assets\
 --preload-file ./lib\
 --preload-file python${PYVER}.zip\
 -o python.html ./app/src/main/cpp/pythonsupport.c \
 $PANDA3D_CPP $PANDA3D_PY $PYLIB \
 -L. \
 -L${LIBDIR} -lbullet -logg -lvorbisfile -lvorbis -lfreetype -lharfbuzz

        if echo $@|grep -q build
        then
            echo "build-only terminated"
        else
            echo " * pushing and running apk $FILE"
            install_run $FILE
        fi
    fi
fi

