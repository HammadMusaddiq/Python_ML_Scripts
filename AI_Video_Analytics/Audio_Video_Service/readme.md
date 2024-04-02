# Audio Video Service
Basically used to write data in the kafka topic "videos-to-be-downloaded" for vidoe transcription, and "mp3-to-be-transcribed" for audio transcription. "videos-to-be-downloaded" topic will read by a trimming Stream (UTS) which is URL Trimming Services. "mp3-to-be-transcribed" topic will read by a trimming Stream (ADS) which is Audio Download Service.

Video transcription initiator

## Virtual Environment Creation 
Change directory into 
```bash
cd /opt/Virtual_Environments
```

Create the Environment for AVS:

```bash
virtualenv --python=/usr/bin/python3.6 avs_env
```
Activate the virtual environment:

```bash
source avs_env/bin/activate
```
Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/Audio_Video_Service/requirements.txt"
```
## Starting the microservice

Create a separate screen for AVS:

```bash
screen -S AVS
```
Activate the virtual environment:
```bash
source /opt/Virtual_Environments/avs_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/Audio_Video_Service
```

Run Service
```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5009 app:app 
```
Detach Screen 

```bash
CTR + A, D 
```

## Usage

```python
import requests

#send post request on ip and port for audio_video_service from config
response = requests.post(ip:port, json={"start": startime, "end":endtime, "url":videourl, "id":kafkaid})
print(response.json()["data"])
```
