
#this script fixes Image not loaded error when "import pyopencv"
# run with sudo
# $ sudo ./pyopencv_fix.sh

SITE_PACKAGES=/Library/Frameworks/Python.framework/Versions/7.2/lib/python2.7/site-packages

NP=$SITE_PACKAGES/pyopencv-2.1.0.wr1.2.0-py2.7-macosx-10.5-i386.egg/pyopencv
echo changing $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib  
echo to 
echo $NP/libpyopencv_extras.dylib

echo 
echo

OUT=dl-cv_hpp_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cv_h_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cv_hpp_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cvaux_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cxcore_h_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cxcore_hpp_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cxcore_hpp_point_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cxcore_hpp_vec_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-cxtypes_h_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-highgui_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-ml_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT

OUT=dl-sdopencv_ext.so
echo changing $OUT
install_name_tool -change $SITE_PACKAGES/pyopencv/libpyopencv_extras.dylib $NP/libpyopencv_extras.dylib $NP/$OUT
