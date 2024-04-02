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
