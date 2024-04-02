# Transcription

Transcription using Deeppavlov's pretrained model. This microservice is used by the audio_transcription and video_transcription processes.



## Virtual Environment Creation 

Change directory into 
```bash
cd /opt/Virtual_Environments
```


Create the Environment for Transcription:

```bash
virtualenv --python=/usr/bin/python3.6 transcription_env
```
Activate the virtual environment:

```bash
source transcription_env/bin/activate
```


Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/Transcription/requirements.txt"
```
Download and install models:

```bash
python -m deeppavlov install asr_tts

python -m deeppavlov download asr_tts
```

## Starting the microservice

Create a seperate screen for Transcription

```bash
screen -S Transcription
```

Activate the virtual environment:
```bash
source /opt/Virtual_Environments/transcription_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/Transcription
```

Run Service

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5006 app:app 
```

Detach Screen 

```bash
CTR + A, D 
```


## Usage

```python
import requests

#send post request on ip and port at the "diarization" route for Speaker Diarization from config
#audio_ftp_path is a single url sent as string
response = requests.post(ip:port+"/diarization", json={"url": audio_ftp_path})
print(response.json()["data"])


#send post request on ip and port at the "transcription" route for Audio Transcription from config
#chunk_ftp_path is a single url sent as string
response = requests.post(ip:port+"/transcription", json={"url": chunk_ftp_path})
print(response.json()["data"])
```

