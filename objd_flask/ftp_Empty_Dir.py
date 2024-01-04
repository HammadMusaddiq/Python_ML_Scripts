from ftplib import FTP
import configparser
import io
from pyspark.sql import SparkSession

# For access path, on cluster user this ("hdfs:///user/config/config.ini"). on System user this ("hdfs://192.168.18.182/user/config/config.ini")
conf_path = "hdfs://192.168.18.185/user/config/config.ini"

# configuration for FTP
node_ip_ftp = None
node_port_ftp = None
auth_user_ftp  = None
auth_pass_ftp  = None

# configuration for OBJD_FLASK
node_ip_objd = None
node_port_objd = None

def initialize_config(spark):
    global node_ip_ftp 
    global node_port_ftp 
    global auth_user_ftp 
    global auth_pass_ftp 

    parse_str = configparser.ConfigParser()
    c = spark.sparkContext.textFile(conf_path).collect()
    buf = io.StringIO("\n".join(c))
    x = parse_str.readfp(buf)
    node_ip_ftp = str(parse_str.get('FTP', 'host')).strip()
    node_port_ftp = str(parse_str.get('FTP', 'port')).strip()
    auth_user_ftp = str(parse_str.get('FTP', 'username')).strip()
    auth_pass_ftp = str(parse_str.get('FTP', 'password')).strip()

    node_ip_objd = str(parse_str.get('OBJD_FLASK', 'ip')).strip()
    node_port_objd = str(parse_str.get('OBJD_FLASK', 'port')).strip()

spark = SparkSession.builder.getOrCreate()

initialize_config(spark)

print(node_ip_ftp)
print(node_port_ftp)
print(auth_user_ftp)
print(auth_pass_ftp)

# FTP Server Connection
ftp = None
def connect():
    global ftp
    ftp = FTP()
    try:
        ftp.connect(node_ip_ftp, int(node_port_ftp))
        return True
    except Exception as e:
        print(e)
        return False

def login():
    global ftp
    try:
        ftp.login(auth_user_ftp, auth_pass_ftp)
        return True
    except Exception as e:
        print(e)
        return False

def directory_exists(dir):
    global ftp
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    #print(filelist)
    for f in filelist:
        if f.split()[-1] == dir and f.upper().startswith('D'):
            return True
    return False

def chdir(dir):
    global ftp
    if directory_exists(dir) is False:
        ftp.mkd(dir)
    ftp.cwd(dir)

def emptyFTPDir():
    dirname = 'Object_Detection_Video/Frames'
    try: 
        connect()
        try: 
            login()
            #chdir("Object_Detection_Video")
            #chdir("Frames")
            ftp.cwd(dirname)
            try:
                # print(ftp.nlst())
                for file in ftp.nlst():
                    try:
                        ftp.delete(file) # Delete Files
                    except Exception:
                        ftp.rmd(file) # Delete Folder
                ftp.quit()
            except Exception as E:
                print(E)
        except Exception as E:
            print(E)
    except Exception as E:
        print(E)

emptyFTPDir()