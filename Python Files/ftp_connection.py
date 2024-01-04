import io
import configparser
from ftplib import FTP
from pywebhdfs.webhdfs import PyWebHdfsClient 


class Ftp_Stream():
    def __init__(self):
        # self.local_config_parses = configparser.ConfigParser()
        
        # self.local_config_parses.read("config.ini")
        # # self.host_hdfs = str(self.local_config_parses.get('HDFS', 'ip')).strip()
        # self.host_hdfs = '10.100.103.101'
        # self.port_hdfs=50070

        # # self.port_hdfs = str(self.local_config_parses.get('HDFS', 'port'))
        # self.hdfs = PyWebHdfsClient(host=self.host_hdfs,port=self.port_hdfs, user_name='hdfs')
        
        # # Remote config.ini file path located on HDFS
        # self.conf_file = '/user/config/config.ini'
        
        self.node_ip_ftp = "10.100.150.105"
        self.node_port_ftp = 21
        self.node_path_ftp = "/microcrawler"
        self.auth_user_ftp  = "microcrawler"
        self.auth_pass_ftp  = "rapidev"

        # # Remote HDFS config.ini parser
        # self.parse_str = configparser.ConfigParser()

        # # Reading in Bytes, decode to String
        # self.conf_read = self.hdfs.read_file(self.conf_file).decode("utf-8") 
        # self.buf = io.StringIO(self.conf_read)
        # self.parse_str.readfp(self.buf)
        # self.node_ip_ftp = str(self.parse_str.get('FTP', 'host')).strip()
        # self.node_port_ftp = int(self.parse_str.get('FTP', 'port'))
        # self.auth_user_ftp = str(self.parse_str.get('FTP', 'username')).strip()
        # self.auth_pass_ftp = str(self.parse_str.get('FTP', 'password')).strip()

        self.ftp = FTP(host=self.node_ip_ftp,user=self.auth_user_ftp,passwd=self.auth_pass_ftp)
        self.base_url = "http://"+self.node_ip_ftp + self.node_path_ftp
        self.ftp_base_path = self.ftp.pwd()

    def change_ftp_present_working_dir(self, pwd_path):
        try:
            self.ftp.cwd(self.ftp_base_path)
            # if self.ftp.pwd() != self.ftp_base_path:
            #     self.ftp.cwd(self.ftp_base_path)
            for folder in pwd_path.split('/')[1:]:
                self.chdir(folder)
        except Exception as E:
            print("Error in changing ftp path: {}: {}, Error: {}".format(self.ftp.pwd(), pwd_path, E))
            # logger.error("An Exception occured in while changing directory in FTP : {}".format(E))        
        # try:
        #     if self.ftp.pwd() != pwd_path:
        #         self.ftp.cwd(pwd_path) #if error on changing cwd then make in exception
        # except:
        #     try:
        #         for folder in pwd_path.split('/')[1:]:
        #             self.chdir(folder)
        #     except Exception as E:
        #         print(E)
        #         # logger.error("An Exception occured in while changing directory in FTP : {}".format(E)) 


    def getFTP(self):
        return self.ftp

    def getBaseURL(self):
        return self.base_url

    def retry_ftp_connection(self):
        is_connected = False
        for i in range(5): # 5 retries
            if self.connect() == True:
                # logger.info("Connection established with FTP")
                if self.login() == True:
                    # logger.info("Login with FTP successful")
                    is_connected = True
                    return is_connected
            else:
                error = "FTP Connection Error"
                E = self.ftp.connect()
                # logger.error("{} Reason: {}".format(error,E))
        
        return is_connected


    def is_connected(self):
        try:
            self.ftp.pwd()
            return True
        except:
            return False
        
        
    def connect(self):
        try:
            # logger.info("Trying FTP Connection ({}:{})".format(self.node_ip_ftp,self.node_port_ftp))
            self.ftp.connect(host=self.node_ip_ftp)
            return True
        except Exception as E:
            # logger.error("FTP Connect Error {}".format(E))
            return E

    def login(self):
        try:
            self.ftp.login(self.auth_user_ftp, self.auth_pass_ftp)
            return True
        except Exception as E:
            return E

    def directory_exists(self, dir):
        filelist = []
        self.ftp.retrlines('LIST', filelist.append)
        for f in filelist:
            if f.split()[-1] == dir and f.upper().startswith('D'):
                return True
        return False

    def chdir(self, dir):
        if self.directory_exists(dir) is False:
            self.ftp.mkd(dir)
        self.ftp.cwd(dir)
