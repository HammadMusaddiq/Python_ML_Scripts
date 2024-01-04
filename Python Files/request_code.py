import requests

url = "http://10.100.160.103:8096/run_realtime?camera_url=rtsp://admin:Rapidev321@192.168.23.166:554/cam/realmonitor?channel=1%26subtype=0&camera_ip=192.168.23.199&kafka_ip=10.100.160.100:9092&out_port=8082&threats='{ '1': 2,  '2': 1 }'"

# url = {'camera_url': 'rtsp://admin:Admin12345@192.168.18.166:554/cam/realmonitor?channel=1&subtype=0', 'camera_ip': '192.168.18.166', 'kafka_ip': '10.100.160.100:9092', 'threats': "{'1': 2, '2': 1, '3': 3, '4': 3, '5': 3, '6': 3, '7': 3, '8': 3}", 'out_port': 9296}

# url = "http://10.100.160.103:8096/run_realtime?camera_url=rtsp://admin:Admin12345@192.168.18.166:554/cam/realmonitor?channel=1&subtype=0&camera_ip=192.168.18.166&kafka_ip=10.100.160.100:9092&out_port=9296&threats={'1': 2, '2': 1, '3': 3, '4': 3, '5': 3, '6': 3, '7': 3, '8': 3}"

payload={}
files={}
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)

print(response.text)

import ast
threats = "{ '1': 2,  '2': 1 }"
str1 = "{ 'name': 2, 'id': 1 }"
my_dict = ast.literal_eval(threats)
my_dict1 = ast.literal_eval(str1)


import json
val = json.loads(threats)
print(val)
