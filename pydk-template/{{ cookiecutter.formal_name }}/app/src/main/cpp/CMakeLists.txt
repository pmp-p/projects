# https://boringssl.googlesource.com/boringssl/+/version_for_cocoapods_6.0/third_party/android-cmake/README.md

# -DANDROID_ABI="armeabi-v7a with NEON" ?


project(app)
cmake_minimum_required(VERSION 3.4.1)

set(PYVER {{ cookiecutter.pyver }})
set(PYTHON python${PYVER})
set(ANDROID_STL "c++_shared")

set(ROOT  ${CMAKE_SOURCE_DIR}/../../../..)

set(ASSETS ${ROOT}/assets)
set(PREBUILT ${ROOT}/prebuilt/${ANDROID_NDK_ABI_NAME})
#set(PREINC ${ROOT}/prebuilt/${ANDROID_NDK_ABI_NAME}/include)
set(PREINC ${ROOT}/aosp/apkroot-${ANDROID_NDK_ABI_NAME}/usr/include)


# copy arch dependant libs
#execute_process(COMMAND sh -c "mkdir -p ${PREBUILT};/bin/cp ${BUILT}/*.so ${PREBUILT}/")
#execute_process(COMMAND sh -c "mkdir -p ${PREBUILT};/bin/cp ${BUILT}-extra/*.so ${PREBUILT}/")
# copy sysconfig data
#execute_process(COMMAND sh -c "/bin/cp ${ASSETS}/python${PYVER}/_sysconfig*.py ${ASSETS}/python${PYVER}/")

message(">>>>>>>>>> ${PREINC}/${PYTHON} <<<<<<<<<<<<<")

include_directories(${PREINC} ${PREINC}/${PYTHON} ${CMAKE_SOURCE_DIR} ${CMAKE_SOURCE_DIR}/include)

file(GLOB ${CMAKE_SOURCE_DIR}/*/*.c)

add_library(rmipython SHARED rmipython.c cpy-aosp/mod_egl.cpp)

add_library(ssl SHARED IMPORTED )
set_target_properties(ssl PROPERTIES IMPORTED_LOCATION ${PREBUILT}/libsslpython.so)

add_library(crypto SHARED IMPORTED )
set_target_properties(crypto PROPERTIES IMPORTED_LOCATION ${PREBUILT}/libcryptopython.so)

add_library(lzma SHARED IMPORTED )
set_target_properties(lzma PROPERTIES IMPORTED_LOCATION ${PREBUILT}/liblzma.so)

add_library(BZ2 SHARED IMPORTED )
set_target_properties(BZ2 PROPERTIES IMPORTED_LOCATION ${PREBUILT}/libbz2.so)

add_library(ffi SHARED IMPORTED )
set_target_properties(ffi PROPERTIES IMPORTED_LOCATION ${PREBUILT}/libffi.so)

add_library(brokenthings SHARED IMPORTED )
set_target_properties(brokenthings PROPERTIES IMPORTED_LOCATION ${PREBUILT}/libbrokenthings.so)

add_library(python3 SHARED IMPORTED )
set_target_properties(python3 PROPERTIES IMPORTED_LOCATION ${PREBUILT}/lib${PYTHON}.so)
set_target_properties(python3 PROPERTIES IMPORTED_NO_SONAME ON)


# Include libraries needed for rmipython lib
target_link_libraries(rmipython
                    android
                    log
                    z
                    lzma
                    BZ2
                    ffi
                    ssl
                    c++_shared
                    crypto
                    brokenthings
                    python3
                    GLESv2
                    GLESv1_CM
                    EGL
)

#include(${BUILT}.include)
#                     -Wl,-whole-archive
#                     ${PREBUILT}/lib/libpython3.7.a
#                      -Wl,--no-whole-archive)
