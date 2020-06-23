import configargparse
from datetime import datetime, timedelta, timezone
import time
import sqlite3
import sys
import os
import glob
import numpy as np
import re
import statistics
import traceback

def countdays(num_days, first_day,last_day):
    if first_day is None:
       if num_days is not None:
          return num_days
       else:
          return 2
    else:
       first_day_stamp=datetime(int(first_day[0:4]),int(first_day[4:6]),int(first_day[6:8]),0,tzinfo=timezone.utc).timestamp()
    if last_day is None:
       last_day_stamp=(datetime.utcnow()).timestamp()
    else:
       last_day_stamp=datetime(int(last_day[0:4]),int(last_day[4:6]),int(last_day[6:8]),0,tzinfo=timezone.utc).timestamp()
    if first_day_stamp > last_day_stamp:
       print("First day is after last day. Exiting.")
       sys.exit(1)
    return int((last_day_stamp-first_day_stamp)/3600/24+1)


def findpath(file1,storage_dir):
    for file2 in glob.glob(storage_dir+'/*/*.fits'):
      if samelink(file1,file2):
        return(file2)
    return 'None'

def timetonite(time):
    return (datetime.utcfromtimestamp(time)-timedelta(hours=12)).strftime('%Y-%m-%d')

def rec_listdir(dir):
    output=[]
    filelist=os.listdir(dir)
    for file in filelist:
        if os.path.isdir(dir+'/'+file):
           for file2 in os.listdir(dir+'/'+file):
               if file2[0] is not '.':
                  output.append(file+'/'+file2)
        else:
           if file[0] is not '.':
              output.append(file)
    return sorted(output)

def trimslash(DIRLIST):
    output = []
    for DIR in DIRLIST:
        if DIR[-1] == '/':
           output.append(DIR[:-1])
        else:
           output.append(DIR)
    return output

def dirisnite(dir):
    if not dir[:4].isdigit():
      return False
    if not dir[-2:].isdigit():
      return False
    if len(dir) == 10:
      if not (dir[4] == '-' and dir[7] == '-'):
        return False
      if dir[5:7].isdigit():
        return True
    if len(dir) == 8:
      if dir[4:6].isdigit():
        return True
    return False
    
def samelink(file1,file2):
    s1 = os.stat(file1)
    s2 = os.stat(file2)
    return (s1.st_ino, s1.st_dev) == (s2.st_ino, s2.st_dev)

def db_to_html(db, query, linkify=False):
    if isinstance(query,str):
      query=[query]
    conn = sqlite3.connect(db)
    html='<table style="width:100%">\n'
    c = conn.cursor()
    c.execute(query[0])
    columns= [description[0] for description in c.description]
    td='</td><td>'
    tdl='</td><td style="border-left:2px dashed silver;">'
    btd='</b></td><td><b>'
    hstring='<thead><tr style="border-top:3px solid black; border-bottom:3px solid black;"><td><b>'
    for column in columns:
        hstring+=column.replace('_',' ')+btd
    hstring += '</b></td></tr></thead>\n'
    html += hstring
    rows=c.fetchall()
    for num in range(1,len(query)):
        c.execute(query[num])
        rows.extend(c.fetchall())
        
    printhnum=20
    rownum=0
    for row in rows:
       if rownum == printhnum:
           html += hstring
           rownum=0
       rownum+=1
       html+='<tr style="border-bottom:2px dashed silver;"><td>'
       datanum=0
       for data in row:
           if (datanum == 0 ) & (linkify):
              html+='<a href="'+str(data)+'.html">'+str(data)+'</a>'+tdl
           else: 
              html+=str(data)+tdl
           datanum+=1
       html+='</tr>\n'
    html+='</table>\n'
    return html


def get_config():
    """Parse command line args, config file, environment variables to get configuration.
    Returns
    -------
    config: `dict`
        Configuration values for program.
    """
    parser = configargparse.ArgParser(config_file_parser_class=configargparse.YAMLConfigFileParser,
                                      auto_env_var_prefix="RSYMON_")
    parser.add('--input_dir', action='store', type=str, required=True,
               help='Path to input directory at NCSA. Must include storage and gen2repo subdirectories')
    parser.add('--first_day', action='store', type=str, required=False,
               help='Date in YYYYMMYY format for first. Must be before last day. Will override num_days')
    parser.add('--last_day', action='store', type=str, required=False,
               help='Date in YYYYMMYY format for last day if not today.')
    parser.add('--ingest_log', action='store', type=str, required=False,
               help="Location of ingest log (will default to today's log.")
    parser.add('--output_dir', action='store', type=str, required=True,
               help='Path to output directory where DB and webpage will live')
    parser.add('--query_links', action='store_true',
               help='Query repo for all links (for repos that do not organize by date; e.g. comCam and BOT).')
    parser.add('--num_days', action='store', type=int, required=False,
               help='Number of days before the last date.')
    config = vars(parser.parse_args())
    return config

class db_filler:
    def __init__(self,input_dir,output_dir,ingest_log,last_day=[]):
        self.now=datetime.utcnow()
        self.nowstr=self.now.strftime('%Y-%m-%d-%H:%M:%S')
        self.input_dir=input_dir
        self.output_dir=output_dir
        self.lock=output_dir+'/.monitor.lock'
        self.name=output_dir.split('/')[-1]
        if len(self.name) == 0:
           self.name=output_dir.split('/')[-2]
        self.check_input_dir()
        self.check_output_dir()
        self.check_lock()
        if last_day is None:
           self.last_day=self.now
        else:
           self.last_day=datetime(int(last_day[0:4]),int(last_day[4:6]),int(last_day[6:8]),0,tzinfo=timezone.utc)
        self.ingest_log = ingest_log
 
    def check_input_dir(self):
        self.repo_dir=self.input_dir+'/gen2repo/'
        self.raw_dir=self.repo_dir+'raw/'
        self.repo=self.repo_dir+'registry.sqlite3'
        self.storage=self.input_dir+'/storage/'
        if not os.path.exists(self.input_dir):
          print(self.input_dir+" does not exist. Exiting.")
          sys.exit(1)
        if not os.path.exists(self.repo):
          print(self.repo+" does not exist. Exiting.")
          sys.exit(1)
        if not os.path.exists(self.storage):
          print(self.storage+" does not exist. Exiting.")
          sys.exit(1)

    def check_output_dir(self):
        self.html=self.output_dir+'/index.html'
        self.db=self.output_dir+'/observing_monitor.sqlite3'  
        os.makedirs(self.output_dir,exist_ok=True)
        if not os.path.exists(self.output_dir):
          print("You do not have access to "+self.output_dir+". Exiting.")
          sys.exit(1)
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS FILE_COUNT (Nite_Obs TEXT PRIMARY KEY, Last_Update TEXT, N_Files INTEGER, Last_Transfer TEXT, N_Ingest INTEGER, Last_Ingest TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS TRANSFER_LIST (File_Name TEXT PRIMARY KEY, ST_DEV INTEGER, ST_INO INTEGER, FILENUM INTEGER,  Nite_Trans TEXT, Last_Update TEXT, Transfer_Path TEXT, Transfer_Time TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS INGEST_LIST (Ingest_Path TEXT PRIMARY KEY, File_Name TEXT, ST_DEV INTEGER, ST_INO INTEGER, FILENUM INTEGER, Nite_Obs TEXT, Last_Update TEXT, Transfer_Path TEXT, Ingest_Time TEXT)")
        conn.commit()
        conn.close()

    def check_lock(self):
        if os.path.exists(self.lock):
          print("The lock file, "+self.lock+" exists. This indicates that another process is running. Delete it if you think this is an error. Exiting.")
          sys.exit(1)
        open(self.lock, 'a').close() 

    def set_date(self,num):
        self.nite=(self.last_day-timedelta(days=num)).strftime('%Y-%m-%d')
        self.nite_no_hyphen=(self.last_day-timedelta(days=num)).strftime('%Y%m%d')
        self.next_nite=(self.last_day-timedelta(days=num-1)).strftime('%Y-%m-%d')
        self.next_nite_no_hyphen=(self.last_day-timedelta(days=num-1)).strftime('%Y%m%d')
        mintime=datetime(int(self.nite[0:4]),int(self.nite[5:7]),int(self.nite[8:10]),12, tzinfo=timezone.utc)
        self.mintime=mintime.timestamp()
        self.maxtime=(mintime+timedelta(days=1)).timestamp()

    def count_new_files(self,DIRLIST=[]):
        self.nfiles=0
        self.filenames=[]
        self.tdevs=[]
        self.tinos=[]
        self.tpaths=[]
        self.ttimes=[]
        self.ttimestrs=[]
        self.tnites=[]
        if DIRLIST == []:
            DIRLIST=[self.nite, self.nite_no_hyphen, self.next_nite, self.next_nite_no_hyphen]
        for DIR in DIRLIST:
            if DIR in [self.next_nite, self.next_nite_no_hyphen]:
                nite=self.next_nite
            else:
                nite=self.nite
            dirfile=0
            if os.path.exists(self.storage+DIR):
                 filelist=[DIR+'/'+fn for fn in sorted(rec_listdir(self.storage+DIR))]
                 for FILE in filelist:
                     PATH=self.storage+FILE
                     ttime=os.path.getmtime(PATH)
                     STAT = os.stat(PATH)
                     self.filenames.append(FILE)
                     self.tpaths.append(PATH)
                     self.tdevs.append(STAT.st_dev)
                     self.tinos.append(STAT.st_ino)
                     self.ttimes.append(ttime)
                     self.ttimestrs.append(datetime.utcfromtimestamp(ttime).strftime('%Y-%m-%d-%H:%M:%S'))
                     self.tnites.append(nite)
                     self.nfiles += 1
                     dirfile+=1

    def count_links_query(self):    
        self.ltimes=[]
        self.ltimestrs=[]
        self.lpaths=[]
        self.ldevs=[]
        self.linos=[]
        self.lfilepaths=[]
        self.lnites=[]
        self.nlinks=0
        conn = sqlite3.connect(self.repo)
        query="select run||'/'|| raftname||'/'||expId||'-'|| raftname ||'-'|| detectorName||'-det'||printf('%03d', detector)||'.fits' as FILENAME  from raw where dayObs = '"+self.nite+"' order by FILENAME"
        c = conn.cursor()
        c.execute(query)
        rows=c.fetchall()
        for FILENAME in [row[0] for row in rows]:
            FULLPATH = self.raw_dir+FILENAME
            if os.path.exists(FULLPATH):
                self.ltimes.append(os.lstat(FULLPATH).st_mtime)
                self.ltimestrs.append(datetime.utcfromtimestamp(self.ltimes[-1]).strftime('%Y-%m-%d-%H:%M:%S'))
                self.lpaths.append('raw/'+FILENAME)
                STAT=os.stat(FULLPATH)
                self.ldevs.append(STAT.st_dev)
                self.linos.append(STAT.st_ino)
                if os.path.islink(FULLPATH):
                    FILEPATH=os.readlink(FULLPATH)
                    self.lfilepaths.append(FILEPATH.split('storage/')[-1])
                else:
# Slow findpath replaced once we started writing down FILENUM (st_dev, st_iso combos) 
#                    FILEPATH=findpath(FULLPATH,self.storage)
                    self.lfilepaths.append('NONE')
                self.lnites.append(self.nite)
                self.nlinks += 1
            else:
                print(FULLPATH+' does not exist.')
        print(str(self.nlinks)+" found.")
        conn.close()

    def count_links(self,DIRLIST=[]):
        self.ltimes=[]
        self.ltimestrs=[]
        self.lpaths=[]
        self.ldevs=[]
        self.linos=[]
        self.lfilepaths=[]
        self.lnites=[]
        self.nlinks=0
        REPODIRS =  ['raw/']
        if DIRLIST == []:
           DIRLIST = [REPODIR+self.nite for REPODIR in REPODIRS]
        for DIR in trimslash(DIRLIST):
            NITEDIR=self.repo_dir+DIR
            if os.path.exists(NITEDIR):
                for FILE in sorted(rec_listdir(NITEDIR)):
                    FULLPATH=NITEDIR+'/'+FILE
                    self.ltimes.append(os.lstat(FULLPATH).st_mtime)
                    STAT=os.stat(FULLPATH)
                    self.ldevs.append(STAT.st_dev)
                    self.linos.append(STAT.st_ino)
                    self.ltimestrs.append(datetime.utcfromtimestamp(self.ltimes[-1]).strftime('%Y-%m-%d-%H:%M:%S'))
                    self.lpaths.append(DIR+'/'+FILE)
                    if os.path.islink(FULLPATH):
                        FILEPATH=os.readlink(FULLPATH)
                    else:
                        FILEPATH=findpath(FULLPATH,self.storage)
                    self.lfilepaths.append(FILEPATH.split('storage/')[-1])
                    if dirisnite(DIR.split('/')[-1]):
                        self.lnites.append(self.nite)
                    else:
                        self.lnites.append(timetonite(os.path.getmtime(FILEPATH)))
                    self.nlinks += 1
            else:
                print("Warning: "+NITEDIR+" does not exist.")


    def scan_log(self):
        if self.ingest_log is None:
           print("No ingest log. Not checking for ingestion errors.")
           return None
        if not os.path.exists(self.ingest_log): 
           print("No ingest log. Not checking for ingestion errors.")
           return None

    def update_transfer_link(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute("select count(Transfer_Path) from INGEST_LIST where Transfer_Path = 'NONE'")
        if c.fetchall()[0][0] == 0:
          conn.close()
          return None
        c.execute("update INGEST_LIST set (Transfer_Path, File_Name) = (select T.Transfer_Path, T.File_Name from INGEST_LIST I, TRANSFER_LIST T where T.FILENUM = I.FILENUM) where exists ( select 1 from INGEST_LIST WHERE Transfer_Path = 'NONE')")
        conn.commit()
        conn.close()

    def update_db_files(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        for num in range(len(self.filenames)):
            c.execute("INSERT OR REPLACE INTO TRANSFER_LIST (File_Name, ST_DEV, ST_INO, FILENUM, Nite_Trans, Last_Update, Transfer_Path, Transfer_Time) VALUES('"+self.filenames[num].split('/')[-1]+"', "+str(self.tdevs[num])+", "+str(self.tinos[num])+", "+str(self.tinos[num]*10000+self.tdevs[num])+", '"+self.tnites[num]+"', '"+self.nowstr+"', '"+self.filenames[num]+"', '"+self.ttimestrs[num]+"')")
        conn.commit()
        conn.close()
        if len(self.filenames) > 0:
             print("Inserted or replaced "+str(len(self.filenames))+" into TRANSFER_LIST.")

    def update_db_links(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        for num in range(len(self.lpaths)):
            c.execute("INSERT OR REPLACE INTO INGEST_LIST (Ingest_Path, File_Name, ST_DEV, ST_INO, FILENUM, Nite_Obs, Last_Update, Transfer_Path, Ingest_Time) VALUES('"+self.lpaths[num]+"', '"+self.lfilepaths[num].split('/')[-1]+"', "+str(self.ldevs[num])+", "+str(self.linos[num])+", "+str(self.tinos[num]*10000+self.tdevs[num])+", '"+self.lnites[num]+"', '"+self.nowstr+"', '"+self.lfilepaths[num]+"', '"+self.ltimestrs[num]+"')") 
        conn.commit()
        conn.close()
        if len(self.lpaths) > 0:
             print("Inserted or replaced "+str(len(self.lpaths))+" into INGEST_LIST.")
    

    def get_night_data(self):
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        c.execute('select count(i.File_Name), max(Transfer_Time), max(Ingest_Time) from INGEST_LIST i, Transfer_List t where i.FILENUM = t.FILENUM and Nite_Obs = "'+self.nite+'" group by Nite_Obs')
        rows=c.fetchall()
        if len(rows) > 0:
            [self.ningest,self.maxttime,self.maxitime]=rows[0]
        else:
            [self.ningest,self.maxttime,self.maxitime]=[0,'0000-00-00-00:00:00','0000-00-00-00:00:00' ]
        c.execute('select count(File_Name), max(Transfer_Time) from TRANSFER_LIST where FILENUM not in (select FILENUM from INGEST_LIST) and Nite_Trans = "'+self.nite+'" group by Nite_Trans')
        rows=c.fetchall()
        if len(rows) > 0:
            [ntransfer_unmatched, maxttime] = rows[0]
            self.ntransfer=self.ningest+ntransfer_unmatched
            self.maxttime=max(self.maxttime,maxttime)
        else:
            self.ntransfer=self.ningest
        c.execute("INSERT OR REPLACE INTO FILE_COUNT (Nite_Obs, Last_Update, N_Files, Last_Transfer, N_Ingest, Last_Ingest) VALUES('"+self.nite+"', '"+self.nowstr+"', "+str(self.ntransfer)+", '"+self.maxttime+"', "+str(self.ningest)+", '"+self.maxitime+"')")
        conn.commit()
        conn.close()

    def update_nite_html(self):
        outhtml=open(self.output_dir+'/'+self.nite+'.html','w')
        outhtml.write('<html>\n<head>\n<style>\n')
        outhtml.write('table, th, td {\nborder-collapse: collapse;\nfont-size: 20pt;\n }\n')
        outhtml.write('p {font-size: 20pt;\n }\n')
        outhtml.write('</style>\n')
        outhtml.write('</head>\n<body>\n')
        outhtml.write('<h1>'+self.name+' Transfer and Ingestion for Nite of '+self.nite+'</h1>') 
        outhtml.write('<p>Last updated: '+self.nowstr+'</p>\n')
        outhtml.write('<h2>Description</h2>\n')
        outhtml.write('<p>"File Name" is the name of the file transferred to NCSA.<br>\n')
        outhtml.write('"Transfer Path" is the path of the transferred file at NCSA with root '+self.storage+'.<br>\n')
        outhtml.write('"Transfer Time" is the UTC the file arrived at NCSA.<br>\n')
        outhtml.write('"Ingest Path" is the path of the transferred file at NCSA with root '+self.repo_dir+'.<br>\n')
        outhtml.write('"Ingest Time" is the UTC of the file ingestion at NCSA.<br><br>\n')
        outhtml.write(db_to_html(self.db, ['select File_Name, Transfer_Path, Transfer_Time, "None" as Ingest_Path, "None" as Ingest_Time from TRANSFER_LIST where FILENUM not in (select FILENUM from Ingest_list) and Nite_Trans = "'+self.nite+'" ORDER BY Transfer_Time', 'select i.File_Name as File_Name, i.Transfer_Path as Transfer_Path, Transfer_Time, Ingest_Path, Ingest_Time from Ingest_List i, Transfer_List t where i.FILENUM = t.FILENUM and Nite_Obs = "'+self.nite+'" ORDER BY Transfer_time']))
        outhtml.write('</body>\n</html>')
        outhtml.close()

    def update_main_html(self):
        outhtml=open(self.output_dir+'/index.html','w')
        outhtml.write('<html>\n<head>\n<style>\n')
        outhtml.write('table, th, td {\nborder-collapse: collapse;\nfont-size: 20pt;\n }\n')
        outhtml.write('p {font-size: 20pt;\n }\n')
        outhtml.write('</style>\n')
        outhtml.write('</head>\n<body>\n')
        outhtml.write('<h1>'+self.name+' Transfer and Ingestion</h1>') 
        outhtml.write('<p>Last updated: '+self.nowstr+'</p>\n')
        outhtml.write('<h2>Description</h2>\n')
        outhtml.write('<p>"Nite Obs" is the observing night (tied to UTC-12).<br>\n')
        outhtml.write('"Last Update" is the most recent UTC time that Nite Obs was checked.<br>\n')
        outhtml.write('"N Files" is the number of files received at NCSA.<br>\n')
        outhtml.write('"Last Transfer" is the UTC of the most recent file transfer.<br>\n')
        outhtml.write('"N Ingest" is the number of files successfully ingested at NCSA.<br>\n')
        outhtml.write('"Last Ingest" is the UTC of the most recently file ingest.<br><br>\n')
        outhtml.write(db_to_html(self.db, 'select * from FILE_COUNT ORDER by Nite_Obs DESC',linkify=True))
        outhtml.write('</body>\n</html>')
        outhtml.close()

def main():
    config = get_config()
    num_days=countdays(config['num_days'], config['first_day'],config['last_day'])
    db_lines=db_filler(config['input_dir'],config['output_dir'],config['ingest_log'],config['last_day'])
    for num in range(num_days):
        db_lines.set_date(num)
        db_lines.count_new_files()
        db_lines.update_db_files()
        if config['query_links']:
            db_lines.count_links_query()
        else:
            db_lines.count_links()
        db_lines.update_db_links()
        db_lines.update_transfer_link()
        db_lines.get_night_data()
        db_lines.update_nite_html() 
    db_lines.update_main_html()
    os.remove(db_lines.lock)
main()
