cd /Library/Frameworks/Python.framework/Versions/7.2/lib/python2.7/site-packages/pyopencv-2.1.0.wr1.2.0-py2.7-macosx-10.5-i386.egg/pyopencv
rm -f ./libcv.dylib

VERSION=2.1.0
ln -s ./libcv.$VERSION.dylib ./libcv.dylib

rm -f ./libcvaux.dylib
ln -s ./libcvaux.$VERSION.dylib ./libcvaux.dylib

