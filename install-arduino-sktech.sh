#!/bin/bash
#
# Create directory structure for Arduino IDE 1.6 with symbolic links
# to this repository.

mkdir -p $HOME/Arduino/ZumoPdS
src=
ln -s $PWD/src/sketch.ino $HOME/Arduino/ZumoPdS/ZumoPdS.ino
ls -l --color $HOME/Arduino/ZumoPdS/ZumoPdS.ino

for src in $PWD/lib/Zumo*; do
    dst=$HOME/Arduino/libraries/$(basename $src)
    ln -s $src $dst 
    ls -l --color $dst
done
