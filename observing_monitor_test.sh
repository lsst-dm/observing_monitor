#!/bin/bash
source /home/emorgan2/.bashrc
#Setting number of days that will be probed. We default to 2 to cover overnight transfer
NDAYS=2

#Options
# --last_night 20200501 (or some other 8 character date) will set the last night to be something other than tonight (e.g. to check data 
# from an earlier night)
# --query_links is set for repos that are not organized by date (necessitating a query). This incluess BOT and comcam.
OPTIONS=''

#INPUT is the directory 1 level up from the repo
#OUTPUT is where the html and a small db will be written
INPUT=/lsstdata/offline/teststand/auxTel/L1Archiver
OUTPUT=/home/emorgan2/public_html/auxTel

#INPUT=/lsstdata/offline/teststand/NCSA_auxtel
#OUTPUT=/home/emorgan2/public_html/NCSA_auxTel

#INPUT=/lsstdata/offline/teststand/BOT 
#OUTPUT=/home/emorgan2/public_html/BOT 
#OPTIONS=--query_links

#INPUT=/lsstdata/offline/teststand/comcam/CCS
#OUTPUT=/home/emorgan2/public_html/comcam 
#OPTIONS=--query_links

#INPUT=/lsstdata/offline/teststand/NCSA_comcam
#OUTPUT=/home/emorgan2/public_html/NCSA_comcam

python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir $INPUT --output $OUTPUT $NDAYS $OPTIONS
