# URL-Video Trim Service - UTS

UTS is used to download video from url, trim that video file and upload it on the ftp server. It reads the topic "videos-to-be-downloaded" and write the output in the topic "trimmed-videos".

## Virtual Environment Creation 

Change directory into 
```bash
cd /opt/Virtual_Environments
```
Create the Environment for UTS:

```bash
virtualenv --python=/usr/bin/python3.6 uts_env
```
Activate the virtual environment:

```bash
source uts_env/bin/activate
```
Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/UTS_Video/requirements.txt"
```
## Starting the microservice

Create a separate screen for UTS:

```bash
screen -S UTS
```
Activate the virtual environment:
```bash
source /opt/Virtual_Environments/uts_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/UTS_Video
```

Run Service

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5010 app:app 
```
Detach Screen 

```bash
CTR + A, D 
```

## Usage

```python
import requests

#send post request on ip and port for uts from config
response = requests.post(ip:port, json={"start": startime, "end":endtime, "url":videourl, "id":kafkaid})
print(response.json()["data"])
```

