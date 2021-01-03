#!/bin/bash

. utils.sh

sudo mkdir -p "$HTML_ROOT/draw-resources"
update src/js "$HTML_ROOT/draw-resources"
update src/css "$HTML_ROOT/draw-resources"
update src/images "$HTML_ROOT/draw-resources"
update src/html/draw.html "$HTML_ROOT/draw.html"
