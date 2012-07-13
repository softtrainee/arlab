#!/bin/bash
mline="==================================================================================="
marea="+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo $mline
echo Starting Test Bot
echo $mline
echo

echo Testing Launch system
echo
echo $marea
src_dir=~/Programming/mercurial/pychron_test
python $src_dir/launchers/test.py
echo $marea
echo

echo Launching RemoteHardwareServer...
python $src_dir/launchers/remote_hardware_server.py &
echo

echo Launching Pychron...
echo Using Pychrondata_test, and pychron_test

python $src_dir/launchers/pychron.py

