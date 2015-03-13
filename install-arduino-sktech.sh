#!/bin/bash
#
# Create directory structure for Arduino IDE 1.6 with symbolic links
# to this repository.

mkdir -p $HOME/Arduino/ZumoPdS
src=$PWD/arduino/src/sketch.ino
dst=$HOME/Arduino/ZumoPdS/ZumoPdS.ino

[[ -e $dst ]] || ln -s $src $dst
ls -l --color $HOME/Arduino/ZumoPdS/ZumoPdS.ino

for src in $PWD/arduino/lib/Zumo* $PWD/arduino/lib/QTRSensors; do
    dst=$HOME/Arduino/libraries/$(basename $src)
    [[ -e $dst ]] || ln -s $src $dst 
    ls -l --color $dst
done
