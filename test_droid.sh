rm -rf org.beerware.empty
ANDROID_HOME=/data/cross/pydk/android-sdk \
 PYDK=/data/cross/pydk \
 PYVER=3.9 \
 TEMPLATE=$(pwd)/pydk-template ./pydk-build-droid.sh org.beerware.empty
