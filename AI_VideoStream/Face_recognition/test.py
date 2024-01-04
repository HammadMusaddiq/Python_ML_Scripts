import sys
import os
from ftplib import FTP

# ftp = FTP(host="10.100.150.105",user="microcrawler",passwd="rapidev")

ftp = FTP()
ftp.connect(host="10.100.150.105",port=21)
# ftp.connect(host="10.100.103.114",port=21)
ftp.login(user="microcrawler",passwd="rapidev")
print(ftp.pwd())
