source /home/emorgan2/.bashrc
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/auxTel/L1Archiver --output /lsstdata/user/staff/web_data/processing_monitor/auxTel
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/NCSA_auxTel --output /lsstdata/user/staff/web_data/processing_monitor/NCSA_auxTel
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/BOT --output /lsstdata/user/staff/web_data/processing_monitor/BOT --query_links
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/comcam/CCS/ --output /lsstdata/user/staff/web_data/processing_monitor/comcam_ccs --query_links
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/NCSA_comcam/ --output /lsstdata/user/staff/web_data/processing_monitor/NCSA_comcam --query_links
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/comcam/Archiver --output /lsstdata/user/staff/web_data/processing_monitor/comcam_archiver --query_links
