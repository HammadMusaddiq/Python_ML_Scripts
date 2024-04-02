from ftplib import FTP

class Ftp_Stream():
    def __init__(self, node_ip_ftp, node_port_ftp, node_path_ftp, auth_user_ftp, auth_pass_ftp):
        # self.node_ip_ftp = "10.100.160.105"
        # self.node_port_ftp = 21
        # self.node_path_ftp = ""
        # self.auth_user_ftp = "mulhimftp"
        # self.auth_pass_ftp = "Admin@ftp"

        self.node_ip_ftp = node_ip_ftp
        self.node_port_ftp = node_port_ftp
        self.node_path_ftp = node_path_ftp
        self.auth_user_ftp = auth_user_ftp
        self.auth_pass_ftp = auth_pass_ftp

        self.ftp = FTP(host=self.node_ip_ftp, user=self.auth_user_ftp, passwd = self.auth_pass_ftp)
        self.ftp_base_url = "http://"+self.node_ip_ftp + self.node_path_ftp
        self.ftp_base_path = self.ftp.pwd()

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
    
    def login(self):
        try:
            self.ftp.login(self.auth_user_ftp, self.auth_pass_ftp)
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
            self.chdir(pwd_path)
        except Exception as E:
            print("Error in changing ftp path: {}: {}, Error: {}".format(self.ftp_base_path, pwd_path, E))

    
    def directory_exists(self, dir):
        filelist = []
        self.ftp.retrlines('LIST', filelist.append)
        for f in filelist:
            if f.split()[-1] == dir and f.upper().startswith('D'):
                return True
        return False

    def chdir(self, pwd_path):
        try:
            self.ftp.cwd(pwd_path)
        except:
            self.ftp.cwd(self.ftp_base_path)
            if not self.is_connected():
                self.retry_ftp_connection()
            
            for dir in pwd_path.split('/'):
                if self.directory_exists(dir) is False:
                    self.ftp.mkd(dir)
                self.ftp.cwd(dir)
    
# ftp_class = Ftp_Stream()
# ftp_cursor = ftp_class.getFTP()
# print("FTP Basepath: " + str(ftp_cursor.pwd()) + '\n')

# base_url = ftp_class.getBaseURL()
# print("FTP Baseurl: " + str(base_url) + '\n')

# FTP_dir_path = "AIX/livestream_crops/"
# ftp_class.change_ftp_present_working_dir(FTP_dir_path)

# print("Success")