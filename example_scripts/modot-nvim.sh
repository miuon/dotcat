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

nvimConfig=$HOME/.config/nvim
autoload=$HOME/.local/share/nvim/site/autoload

commonDir=`realpath $MODOT_COMMON`
hostDir=`realpath $MODOT_HOST`
themeDir=`realpath $MODOT_THEME`
isQuick=$MODOT_QUICK

mkdir -p $autoload
mkdir -p $nvimConfig
ln -sf $commonDir/autoload/plug.vim $autoload/plug.vim
ln -sf $commonDir/*.vim $nvimConfig

if [ "$isQuick" = true ]; then
	nvim +PlugUpdate +qall
else
	nvim +PlugUpdate +qall
fi
