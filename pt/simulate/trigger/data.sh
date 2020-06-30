#!/bin/bash
BASEDIR=$(dirname "$0")
cd $BASEDIR/../../
/usr/local/bin/pipenv run python3 -m pt.simulate.data -b $1 -p $2 >> /tmp/data-$1.log 2>&1
