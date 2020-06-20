#!/bin/bash

i3confpath="$HOME/.config/i3/config"
i3confdir="$HOME/.config/i3"

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

commonDir=`realpath $MODOT_COMMON`
hostDir=`realpath $MODOT_HOST`
themeDir=`realpath $MODOT_THEME`
isQuick=$MODOT_QUICK

rm -r $i3confdir
mkdir $i3confdir
ln -sf $commonDir/common.i3config $i3confdir/common.i3config
ln -sf $hostDir/host.i3config $i3confdir/host.i3config
ln -sf $themeDir/theme.i3config $i3confdir/theme.i3config

touch $i3confpath
echo "#======================================================" >> $i3confpath
echo "#======!!!    GENERATED FILE, DO NOT EDIT   !!!========" >> $i3confpath
echo "#======================================================" >> $i3confpath
echo "" >> $i3confpath
cat $i3confdir/common.i3config >> $i3confpath
cat $i3confdir/host.i3config >> $i3confpath
cat $i3confdir/theme.i3config >> $i3confpath

if [ "$isQuick" = true ]; then
	echo "reloading i3"
	i3-msg reload >/dev/null
else
	echo "restarting i3"
	i3-msg restart >/dev/null
fi
