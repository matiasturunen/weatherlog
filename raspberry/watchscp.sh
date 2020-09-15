#!/bin/bash
#UPLOAD=$1
UPLOAD="pi@192.168.0.227:~/weatherlog/"
fswatch -0 . | xargs -0 -I {} sh -c 'p="{}"; f="${p/$(pwd)\/}"; scp $p '"$UPLOAD"'"${f}"'