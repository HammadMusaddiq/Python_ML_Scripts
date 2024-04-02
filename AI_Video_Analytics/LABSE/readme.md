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
