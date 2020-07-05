#!/bin/bash

print_usage() {
	printf "Usage: no arguments\nShould be run from MODOT
Required environment variables:
\tMODOT_COMMON: directory of common files for this module
\tMODOT_HOST: directory of host files for this module
\tMODOT_THEME: directory of built theme files for this module
Optional environment variables:
\tMODOT_QUICK: true -- quick reload, false -- full restart\n"
}

if [ $# -gt 1 ] || [ -z $MODOT_COMMON ] || \
	[ -z $MODOT_HOST ] || [ -z $MODOT_THEME ] ; then
	print_usage ; exit 1 ;
fi

binDir=$HOME/bin

commonDir=`realpath $MODOT_COMMON`
hostDir=`realpath $MODOT_HOST`
themeDir=`realpath $MODOT_THEME`
isQuick=$MODOT_QUICK

mkdir -p $binDir
ln -sf $commonDir/bonsai $binDir
ln -sf $commonDir/bonsailoop $binDir
ln -sf $commonDir/colorscript/* $binDir

