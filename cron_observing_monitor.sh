source /home/emorgan2/.bashrc
WEBDIR=/lsstdata/user/staff/web_data/processing_monitor
/home/emorgan2/SOFTWARE/observing_monitor/break_locks.py $WEBDIR/auxTel $WEBDIR/NCSA_auxTel $WEBDIR/BOT $WEBDIR/comcam_ccs $WEBDIR/NCSA_comcam $WEBDIR/comcam_archiver
/home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/auxTel/L1Archiver --output $WEBDIR/auxTel
/home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/NCSA_auxTel --output $WEBDIR/NCSA_auxTel
/home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/BOT --output $WEBDIR/BOT --query_links
/home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/comcam/CCS/ --output $WEBDIR/comcam_ccs
/home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/NCSA_comcam/ --output $WEBDIR/NCSA_comcam --query_links
/home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/comcam/Archiver --output $WEBDIR/comcam_archiver
