#!/bin/sh
reset
APK=$1
PYVER=${PYVER:-"3.8"}


export ROOT=$(pwd)
PYDK=${PYDK:-"$ROOT/.."}
PYDK=$(realpath "$PYDK")
export PYDK

export ANDROID_HOME=${ANDROID_HOME:-$(realpath ${PYDK}/android-sdk)}
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PYTHONDONTWRITEBYTECODE=1
export ARCHITECTURES=${ARCHITECTURES:-"arm64-v8a armeabi-v7a x86 x86_64"}






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


export PYSET=true


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
 Android SDK : ${ANDROID_HOME}
        PYDK : ${PYDK}
    projects : ${ROOT}
 pip install : $PIP install $PIPU
    TEMPLATE : $TEMPLATE
----------------------------

"


FILE=./app/build/outputs/apk/release/app-release-unsigned.apk
FILE=./app/build/outputs/apk/debug/app-debug.apk
ADB=$ANDROID_HOME/platform-tools/adb
echo " * adb is $ADB"
echo " * un-installing any previous version on test device"
$ADB uninstall $APK

echo


function install_run
{
    APK_FILE=$1
    if [ -f $APK_FILE ]
    then
        echo "  * installing $APK_FILE"
        $ADB install $APK_FILE
        aapt=$(find $ANDROID_HOME/build-tools/|grep aapt$|sort|tail -n1)
        pkg=$($aapt dump badging "$APK_FILE"|awk -F" " '/package/ {print $2}'|awk -F"'" '/name=/ {print $2}')
        act=$($aapt dump badging "$APK_FILE"|awk -F" " '/launchable-activity/ {print $2}'|awk -F"'" '/name=/ {print $2}')
        echo "Running $pkg/$act"
        $ADB shell am start -n "$pkg/$act"
        echo
        echo " * adb is $ADB"
        echo "press <enter> to kill app '$APK'"
        read
        echo "$ADB shell am force-stop $APK"
        $ADB shell am force-stop $APK
    fi
}

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
        if find $req -type f|grep so$
        then
            echo " * can't add package : $(basename $req) not pure python"
        else
            echo " * adding pure-python pip package : $(basename $req)"
            cp -ru $req assets/packages/
        fi
    done

}

function do_stdlib
{
    /bin/cp -Rfxpvu ${PYDK}/src/python3-aosp/Lib/. assets/python$PYVER/|egrep -v "test/|lib2to3"
    rm -rf assets/python$PYVER/test assets/python$PYVER/unittest assets/python$PYVER/lib2to3 assets/python$PYVER/site-packages
}


function do_clean
{
    echo " * Removing old builds"

    # so install_run won't pick up last build in case of failure.
    rm ./app/build/outputs/apk/debug/app-debug.apk ./app/build/outputs/apk/release/app-release-unsigned.apk 2>/dev/null

    # cleanup potentially incompatible bytecode
    rm -rf $(find assets/ -type d|grep /__pycache__$)

    ./gradlew clean
}


# that trick is only valid is for rooted dev. It will partially reset device

if echo $@ |grep log
then
    $ADB root
    $ADB shell stop
    $ADB shell setprop log.redirect-stdio true
    $ADB shell setprop debug.ld.all dlerror,dlopen
    $ADB shell start
    exit
fi

if cd $APK 2>/dev/null
then
    echo "Project [${1}] found"
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
      "module_name": "empty",
      "bundle": "org.beerware",
      "app_name": "EmptyApp",
      "formal_name": "org.beerware.empty",
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

cd ${ROOT}

if cd $APK
then
    if echo $@ |grep clean
    then
        do_clean

        # go deeper.
        echo "<ctrl+C> to abort, i WILL destroy : prebuilt" assets/python3.? assets/packages
        read cont
        rm -rf app/build app/.externalNativeBuild prebuilt assets/python3.? assets/packages

    else
        echo " * Syncing stdlib for $PYVER"

        mkdir -p assets/python$PYVER/

        # cleanup


        # todo move test folder with binary cmdline support into separate archive
        # until testsuite is fixed.
        echo " * Copy/Update prebuilt from ${PYDK}/prebuilt for local project"

        mkdir -p prebuilt aosp
        for ARCH in ${ARCHITECTURES}
        do
            echo -n "  * Getting prebuilt for $ARCH : "
            /bin/cp -Rfxpvu ${PYDK}/pydk-min/prebuilt/${ARCH} ./prebuilt/ |wc -l
            /bin/cp -Rfxpvu ${PYDK}/pydk-min/aosp/apkroot-${ARCH} ./aosp/ |wc -l
        done

        #echo " * Copy/Update prebuilt from ${PYDK}/prebuilt.aosp for local project (pip+thirdparty modules)"
        #/bin/cp -Rfxpvu ${PYDK}/prebuilt.aosp/* ./prebuilt/ |wc -l

        for ARCH in ${ARCHITECTURES}
        do
            echo -n " * Copy/Update include from $(echo ${PYDK}/*/apkroot-$ARCH/usr) : "
            /bin/cp -Rfxpvu ${PYDK}/*/apkroot-${ARCH}/usr/include ./prebuilt/$ARCH/ |wc -l

            echo -n " * Copy/Update prebuilt thirdparty libs from $(echo ${PYDK}/*/apkroot-$ARCH/usr) : "
            /bin/cp -Rfxpvu ${PYDK}/*/apkroot-${ARCH}/usr/lib/lib*.so ./prebuilt/$ARCH/ |wc -l
        done

        do_pip ${APK}

        do_stdlib ${APK}


        cp -Rfvpxu ../$APK.app/assets/. ./assets/

        cp -Rfvpxu ${PYDK}/wapy-lib/pythons ./assets/

        if [ -d ../$APK.app/patches ]
        then
            echo " Applying user patches"
            cp -Rfvpxu ../$APK.app/patches/. ./assets/
        fi


        do_clean ${APK}

        shift 1
        ./gradlew --warning-mode all assembleDebug "$@"

        if echo $@|grep -q build
        then
            echo "build-only terminated"
        else
            echo " * pushing and running apk $FILE"
            install_run $FILE
        fi
    fi
fi

