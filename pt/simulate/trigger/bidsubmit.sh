#!/bin/bash
#! -a: account
#! -p: password 
#! -s: start_time
#! -e: end_time
#! -v: bidding value
#! -m: bidding price
#! -t: bidding type
BASEDIR=$(dirname "$0")
START=$(date +"%Y/%m/%d ")00
END=$(date +"%Y/%m/%d " --date="+1 days")00
cd $BASEDIR/../../../
/usr/local/bin/pipenv run python3 -m pt.simulate.bidsubmit -a $1 -p $2 -s "$START" -e "$END" -v $3 -m $4 -t $5 >> /tmp/bidsubmit-$1.log 2>&1
