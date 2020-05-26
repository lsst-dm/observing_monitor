source /home/emorgan2/.bashrc
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/auxTel/L1Archiver --output ~/public_html/auxTel 2
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/NCSA_auxTel --output ~/public_html/NCSA_auxTel 2
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/BOT --output ~/public_html/BOT 2 --query_links
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/comcam/CCS/ --output ~/public_html/comcam 2 --query_links
python /home/emorgan2/SOFTWARE/observing_monitor/observing_monitor.py --input_dir /lsstdata/offline/teststand/NCSA_comcam/ --output ~/public_html/NCSA_comcam 2 --query_links
