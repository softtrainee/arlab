
rm -f ./libcv.dylib

VERSION=1.0.0
ln -s ./libcv.$VERSION.dylib ./libcv.dylib

rm -f ./libcvaux.dylib
ln -s ./libcv.$VERSION.dylib ./libcvaux.dylib

