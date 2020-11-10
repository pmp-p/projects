#!/bin/sh
clear

export PYDK=${PYDK:-/data/cross/pydk}
APK=${1:-org.beerware.empty}

/bin/cp -aRfvxpu $APK.app/{assets,__main__.py} $APK/
/bin/cp -aRfvxpu $APK.app/patches/. ${APK}/assets/


mv -vf $APK/assets/packages/panda3d/__init__.py ${PYDK}/host/lib/python3.9/site-packages/panda3d/__init__.py
cp -aRfvxpu ${PYDK}/wapy-lib/pythons ${APK}/assets/

python3.9 -i -u -B $APK
stty sane
