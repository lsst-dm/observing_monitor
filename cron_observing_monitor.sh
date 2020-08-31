source /home/emorgan2/.bashrc
WEBDIR=/lsstdata/user/staff/web_data/processing_monitor
PATH=/home/emorgan2/SOFTWARE/observing_monitor
REPO=/lsstdata/offline/teststand
$PATH/break_locks.py $WEBDIR/auxTel $WEBDIR/NCSA_auxTel $WEBDIR/BOT $WEBDIR/comcam_ccs $WEBDIR/NCSA_comcam $WEBDIR/comcam_archiver
$PATH/observing_monitor.py --input_dir $REPO/auxTel/L1Archiver --output $WEBDIR/auxTel
$PATH/observing_monitor.py --input_dir $REPO/NCSA_auxTel --output $WEBDIR/NCSA_auxTel
$PATH/observing_monitor.py --input_dir $REPO/BOT --output $WEBDIR/BOT
$PATH/observing_monitor.py --input_dir $REPO/comcam/CCS/ --output $WEBDIR/comcam_ccs
$PATH/observing_monitor.py --input_dir $REPO/NCSA_comcam/ --output $WEBDIR/NCSA_comcam
$PATH/observing_monitor.py --input_dir $REPO/comcam/Archiver --output $WEBDIR/comcam_archiver
$PATH/mainpage.py $WEBDIR auxTel BOT comcam_archiver comcam_ccs NCSA_auxTel  NCSA_comcam
