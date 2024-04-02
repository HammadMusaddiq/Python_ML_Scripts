



# List of Contents
1. [Getting Started](#getting-started)
2.  [IP and PORT Table](#ip-and-port-table)
3. [NER](#ner)
4. [LABSE](#labse)
5. [Transcription](#transcription)
6.  [Audio Video Service](#audio-video-service)
7. [URL-Video Trim Service (UTS)](#url-video-trim-service---uts)
8. [Local-Video Trim Service (LTS)](#local-video-trim-service---lts)
9. [Text Categorization](#text-categorization)
10. [Audio Download Service (ADS)](#audio-download-service---ads)
11. [Updating the Virtual Environments](#updating-the-virtual-environments) 
12.  [Important Notes](#important-notes)
 


# Getting Started
SSH into the remote VM/Droplet/Server

Update `/etc/hosts`
```bash
sudo nano /etc/hosts
```

Add the following ambari hosts ips in `/etc/hosts` 


For V4 Staging Server
```bash
10.100.103.101 master.rapidev.ae
10.100.103.102 snamenode.rapidev.ae
10.100.103.103 worker1.rapidev.ae
10.100.103.104 worker2.rapidev.ae
10.100.103.105 worker3.rapidev.ae
10.100.103.106 worker4.rapidev.ae
```

ssh key setup for repository secure access

```bash
ssh-keygen # set up your public/private key
cat ~/.ssh/id_rsa.pub # copy ssh public key
```
Add the copied ssh into your account settings
```
1. From Bitbucket, choose Personal settings from your avatar in the lower left.

2. Click SSH keys. If you've already added keys, you'll see them on this page.

3. From Bitbucket, click Add key.

4. Enter a Label for your new key, for example, Default public key.

5. Paste the copied public key into the SSH Key field.

6. Click Save.
```


Update ubuntu distribution

```bash
sudo add-apt-repository ppa:deadsnakes/ppa

sudo apt-get update
sudo apt-get install git
cd /home
git clone -b development git@bitbucket.org:rapidevosinteam/owlsense_microservices.git

sudo apt-get install python3.6
sudo apt-get update -y
sudo apt-get install python3.6-dev
sudo apt install python3.6-distutils
sudo apt-get install ffmpeg
sudo apt update && sudo apt install supervisor
sudo systemctl status supervisor

sudo update-alternatives  --set python /usr/bin/python3.6
```
screen is used to open multiple sessions.When the user exits terminal while using ssh, the processes/services will still be running in the background

```bash
sudo apt-get install screen
```

```
Supervisor is a process manager which provides a singular interface for managing and monitoring a number of long-running programs. We will be using multiple rq workers
```


Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the virtualenv package:

```bash
pip3 install virtualenv
```


We use gunicorn for management of frequently occuring exceptions of server base architecture and to use more than 1 threads ( workers )

```bash
pip3 install gunicorn
```

Install Pacakge for Milvus

```bash
python3 -m pip install pymilvus==2.0.0rc9
```

Install Git
```bash
sudo apt-get install git
```



Clone the repo in ```/opt``` directiry
```bash
git clone git@bitbucket.org:rapidevosinteam/bds_microservices.git 
```
change directory into 
```bash
cd /opt/bds_microservices
```
For the Virtual Environments, create a separate folder in  ```/opt```
```bash
cd /opt
mkdir Virtual_Environments
```


# IP and PORT Table
In this case, the ip for microservices are:

| SERVER| IP |
|:---:|:---:|
| Staging V4 | 10.100.103.123 (to be updated for cryptix)|

The list of Microservices and their respective ports are the following:

| SERVICE | PORT |
|:---:|:---:|
| NER | 5001 |
| LABSE | 5004 |
| TRANSCRIPTION | 5006 |
| VDI | 5009 |
| UTS_VIDEO | 5010 |
| LTS_VIDEO | 5011 |
| CATEGORIZATION | 5012 |
| ADS | 5013 |




# NER

Named Entity Recognition (NER) using Deeppavlov Multi BERT.  Microservice is used only by the NER stream.
Output is shown on front end in the "Talks About" section in Profile Info.

## Virtual Environment Creation 
Change directory into 
```bash
cd /opt/Virtual_Environments
```
Create the Environment for NER:

```bash
virtualenv --python=/usr/bin/python3.6 ner_env
```
Activate the virtual environment:

```bash
source ner_env/bin/activate
```
Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/NER/requirements.txt"
```



## Starting the microservice

Create a seperate screen for NER

```bash
screen -S NER
```
Activate the virtual environment:
```bash
source /opt/Virtual_Environments/ner_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/NER
```
Run Service

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5001 app:app 
```

Detach Screen 

```bash
CTR + A, D 
```

## Usage

```python
import requests

#send post request on ip and port for NER from config
response = requests.post(ip:port, json={"text": list_of_strings})

print(response.json()["data"])
```


# LABSE

LABSE is a multilingual embedding model that is a powerful tool which encodes text from different languages into a shared embedding space, enabling it to be applied to a range of downstream tasks, like text classification, clustering, and others, while also leveraging semantic information for language understanding. This microservice is currently being used for Emotion and Sentiment Analysis.

## Virtual Environment Creation 

Change directory into 
```bash
cd /opt/Virtual_Environments
```


Create the Environment for LABSE:

```bash
virtualenv --python=/usr/bin/python3.6 labse_env
```
Activate the virtual environment:

```bash
source labse_env/bin/activate
```

Install CMake:

```bash
pip install cmake==3.18.4.post1
```


Install **Sentence Transformer** packages:

```bash
pip install sentence_transformers
```


Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/LABSE/requirements.txt"
```

## Starting the microservice

Create a seperate screen for LABSE

```bash
screen -S LABSE
```

Activate the virtual environment:
```bash
source /opt/Virtual_Environments/labse_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/LABSE
```

Run Service

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5004 app:app 
```

Detach Screen 

```bash
CTR + A, D 
```



## Usage

```python
import requests

#send post request on ip and port for Labse from config
response = requests.post(ip:port, json={"text": list_of_strings})
print(response.json()["data"])
```

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
# Text Categorization

Text Categorization using zero shot detection

## Virtual Environment Creation 

Change directory into 
```bash
cd /opt/Virtual_Environments
```
Create the Environment for Text Categorization:

```bash
virtualenv --python=/usr/bin/python3.6 cat_env
```
Activate the virtual environment:

```bash
source cat_env/bin/activate
```
Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/Text_Categorization/requirements.txt"
```
## Starting the microservice

Create a seperate screen for Text Categotization

```bash
screen -S Categorization
```
Activate the virtual environment:
```bash
source /opt/Virtual_Environments/cat_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/Text_Categorization
```

Run Service

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5012 app:app 
```

Detach Screen 
```bash
CTR + A, D 
```
## Usage

```python
import requests

#send post request on ip and port for Text Categorization from config
response = requests.post("http://127.0.0.1:5000/",json={"text":target_text})

print(response.json())

#The categories are:
#1. Anti-State
#2. Pro-State
#3. Sexual-Abusive
#4. Non Abusive
#5. Ofence
#6. Peaceful
#7. Supports Judiciary
#8. Against Judiciary
#9. Supports Islam
#10. Against Islam
#Output will show confidence and predictions in a dictionary for example:
#{'confidence': [0.9797252416610718, 0.776104211807251, 0.7757889628410339, 0.7357200980186462, 0.7220778465270996], 'predictions': #['Pro-State', 'Non Abusive', 'Peaceful', 'Against Judiciary', 'Supports Islam']}

```

# Audio Download Service - ADS
ADS is used to download audio from (.mp3) url and store it on the FTP Server. It reads the topic "mp3-to-be-transcribed" and write the output in the topic "cryptix-audio".


Change directory into 
```bash
cd /opt/Virtual_Environments
```
Create the Environment for Audio Download Service

```bash
virtualenv --python=/usr/bin/python3.6 ads_env
```
Activate the virtual environment:

```bash
source ads_env/bin/activate
```
Install the required packages from requirements.txt:

```bash
pip install -r "../cryptrix_microservices/ADS/requirements.txt"
```
## Starting the microservice

Create a separate screen for ADS

```bash
screen -S ADS
```
Activate the virtual environment:
```bash
source /opt/Virtual_Environments/ads_env/bin/activate
```
Change directory into 
```bash
cd /opt/cryptrix_microservices/ADS
```

Run Service

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5013 app:app 
```

Detach Screen 
```bash
CTR + A, D 
```

## Usage

```python
#send post request on ip and port for ADS from config
response = requests.post(ip:port, json={"audio_url": audio_url})

print(response.json()["data"])
```

# Updating the Virtual Environments
If the Virtual Environment of a microservice needs to be changed due to the change in some requirements, following instructions can be used.

Change directory to the git repository:
```bash
cd /opt/owlsense_microservices
```
Fetch and pull any updates to the microservices and their requirement files:
```bash
git fetch
git pull
```
Activate the virtual environment that needs to be updated:

```bash
source /opt/Virtual_Environments/<ENV_NAME>/bin/activate
```
Install the New requirements:
```bash
pip install -r "/opt/owlsense_microservices/<MICROSERVICE_FOLDER>/requirements.txt"
```

# Important Notes

- Do NOT change the folder names of the Virtual Environment folders or any other folder that might be in its path. If changed, the environments will no longer work properly and have to be created again.







