# projects

Various experiements using PyDK prebuilts

eg for creating an apk/zipweb application with a java class named org.beerware.empty

```
rm -rf org.beerware.empty

PYVER=3.9 PYDK=/data/cross/pydk TEMPLATE=/data/cross/pydk/projects/pydk-template ./pydk-build-droid.sh org.beerware.empty

PYVER=3.9 PYDK=/data/cross/pydk TEMPLATE=/data/cross/pydk/projects/pydk-template ./pydk-build-wasm.sh org.beerware.empty

```

soon the two scripts will be merged, but cpython-wasm is not able to init zip virtual filesystem,
 importlib is required to do that.
Panda3D will probably provide a C++ vfs to handle importlib bootstrap and maybe whole C file I/O.
