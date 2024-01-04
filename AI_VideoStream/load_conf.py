import configparser
from pywebhdfs.webhdfs import PyWebHdfsClient
import io


class Load_Config():

    def __init__(self):
        # Parsing Local Config File ./config.ini to get ip & port for HDFS
        self.local_config_parses = configparser.ConfigParser()
        self.local_config_parses.read("./config.ini")
        #self.local_config_parses.read("config.ini")
        self.host_hdfs = str(self.local_config_parses.get('HDFS', 'ip')).strip()
        self.port_hdfs = str(self.local_config_parses.get('HDFS', 'port'))
        self.hdfs = PyWebHdfsClient(host=self.host_hdfs,port=self.port_hdfs, user_name='hdfs')
        
        
        # Remote config.ini file path located on HDFS
        self.conf_file = '/user/config/config.ini'
        
        self.node_ip_smoke_detection = None
        self.node_port_smoke_detection = None
        
        self.auth_ip_weapon_detection  = None
        self.auth_port_weapon_detection  = None

        # Remote HDFS config.ini parser
        self.parse_str = configparser.ConfigParser()

        # Reading in Bytes, decode to String
        self.conf_read = self.hdfs.read_file(self.conf_file).decode("utf-8") 
        self.buf = io.StringIO(self.conf_read)
        self.parse_str.readfp(self.buf)
        
        # self.node_ip_smoke_detection = str(self.parse_str.get('FTP', 'host')).strip()
        # self.node_port_smoke_detection = int(self.parse_str.get('FTP', 'port'))

        self.node_ip_smoke_detection = '10.100.103.201'
        self.node_port_smoke_detection = 6002
        self.node_path_smoke_detection = 'insert'
        
        # self.node_ip_weapon_detection = str(self.parse_str.get('FTP', 'username')).strip()
        # self.node_port_weapon_detection = str(self.parse_str.get('FTP', 'password')).strip()

        self.node_ip_weapon_detection = '10.100.103.201'
        self.node_port_weapon_detection = 6001
        self.node_path_weapon_detection = 'insert'
        

    def getSmokeDetection(self):
        return self.node_ip_smoke_detection, self.node_port_smoke_detection, self.node_path_smoke_detection

    def getWeaponDetection(self):
        return self.node_ip_weapon_detection, self.node_port_weapon_detection, self.node_path_weapon_detection