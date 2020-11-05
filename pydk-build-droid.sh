#!/bin/sh
reset

. pydk-build-common.inc


export ANDROID_HOME=${ANDROID_HOME:-$(realpath ${PYDK}/android-sdk)}
export ANDROID_SDK_ROOT=$ANDROID_HOME

export ARCHITECTURES=${ARCHITECTURES:-"arm64-v8a armeabi-v7a x86 x86_64"}


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

