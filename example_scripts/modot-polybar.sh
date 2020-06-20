#!/bin/bash

polybarConf=$HOME/.config/polybar

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

mkdir -p $polybarConf >/dev/null
mkdir -p $polybarConf/scripts >/dev/null
ln -sf $commonDir/config $polybarConf/config
ln -sf $commonDir/scripts/* $polybarConf/scripts
ln -sf $hostDir/host.ini $polybarConf/host.ini
ln -sf $hostDir/polybar-launch $HOME/bin/polybar-launch
chmod a+x $hostDir/polybar-launch
ln -sf $themeDir/theme.ini $polybarConf/theme.ini
ln -sf $themeDir/modules.ini $polybarConf/modules.ini
ln -sf $themeDir/user_modules.ini $polybarConf/user_modules.ini

if [ "$isQuick" = true ]; then
	echo "quick reload polybar"
	touch -m $polybarConf/config
else
	echo "full reload polybar"
	touch -m $polybarConf/config
	$HOME/bin/polybar-launch >/dev/null 2>/dev/null
fi
