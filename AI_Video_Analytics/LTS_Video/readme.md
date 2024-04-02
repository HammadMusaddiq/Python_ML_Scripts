# Local-Video Trim Service - LTS

LTS is used to read video file from ftp server, trim that video file and upload again on the ftp server. It reads the topic "cryptix-video" and write the output in the topic "trimmed-videos".

## Virtual Environment Creation 



Change directory into 
```bash
cd /opt/Virtual_Environments
```
Create the Environment for LTS:

```bash
virtualenv --python=/usr/bin/python3.6 lts_env
```
Activate the virtual environment:

```bash
source lts_env/bin/activate
```
Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/LTS_Video/requirements.txt"
```
## Starting the microservice

Create a separate screen for LTS:

```bash
screen -S LTS
```
Activate the virtual environment:
```bash
source /opt/Virtual_Environments/lts_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/LTS_Video
```

Run Service

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5011 app:app 
```
Detach Screen 

```bash
CTR + A, D 
```
## Usage

```python
import requests

#send post request on ip and port for lts from config
response = requests.post(ip:port, json={"start": startime, "end":endtime, "url":videourl, "id":kafkaid})
print(response.json()["data"])
```
