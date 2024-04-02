from ftplib import FTP
import os
from dotenv import load_dotenv

load_dotenv()


class Ftp_Stream():
    def __init__(self):
        

        # self.node_ip_ftp = "10.100.160.105"
        # self.node_port_ftp = 21
        # self.node_path_ftp = ""
        # self.auth_user_ftp = "mulhimftp"
        # self.auth_pass_ftp = "Admin@ftp"
        
        self.node_ip_ftp = os.getenv("node_ip_ftp")
        self.node_port_ftp = os.getenv("node_port_ftp")
        self.node_path_ftp = os.getenv("node_path_ftp")
        self.auth_user_ftp = os.getenv("auth_user_ftp")
        self.auth_pass_ftp = os.getenv("auth_pass_ftp")




        self.ftp = FTP(host=self.node_ip_ftp, user=self.auth_user_ftp, passwd = self.auth_pass_ftp)
        self.ftp_base_url = "http://"+self.node_ip_ftp + self.node_path_ftp
        self.ftp_base_path = self.ftp.pwd()
        print(self.ftp_base_url)

    def getFTP(self):
        return self.ftp

    def getBaseURL(self):
        return self.ftp_base_url

    def connect(self):
        try:
            self.ftp.connect(host=self.node_ip_ftp)
            return True
        except Exception as E:
            return E
    
    def is_connected(self):
        try:
            self.ftp.pwd()
            return True
        except:
            return False

    def retry_ftp_connection(self):
        is_connected = False
        for i in range(5):
            if self.connect() == True:
                if self.login() == True:
                    is_connected = True
                    return is_connected
            else:
                error = "FTP Connection Error"
                E = self.ftp.connect()
        
        return is_connected

    def change_ftp_present_working_dir(self, pwd_path):
        try:
            self.ftp.cwd(self.ftp_base_path)
            # if self.ftp.pwd() != self.ftp_base_path:
            #     self.ftp.cwd(self.ftp_base_path)
            for folder in pwd_path.split('/')[1:]:
                self.chdir(folder)
        except Exception as E:
            print("Error in changing ftp path: {}: {}, Error: {}".format(self.ftp.pwd(), pwd_path, E))


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
    
