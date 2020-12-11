rm -rf org.beerware.empty
PYVER=3.9 \
 PYDK=/data/cross/pydk \
 TEMPLATE=$(pwd)/pydk-template ./pydk-build-wasm.sh org.beerware.empty
