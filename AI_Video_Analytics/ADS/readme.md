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
