#!/bin/bash

module=gl.py
temp=.gl-symbols
rm -f $module $temp

echo "from pyglet.gl import (" > $module
ack -ho "gl[A-Z]\w+"    | sort | uniq | sed "s/gl\(.*\)/gl\1 as \1/" >> $temp
ack -ho "GL[a-z]+"      | sort | uniq >> $temp
ack -ho "GL_[A-Z_0-9]+" | sort | uniq >> $temp

echo "Total symbols: " $(cat .gl-symbols | wc -l)

cat $temp | sed "s/$/,/g" >> $module
echo ")" >> $module

rm  -f .gl-symbols

