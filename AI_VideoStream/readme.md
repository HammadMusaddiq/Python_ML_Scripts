# FRS (Facial Recognition System) with Milvus 

FRS is using here to extract embeddings from the images and store it on the milvus database. 

## Virtual Environment Creation 

Make FRS Screen:

```bash
screen -S FRS
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the virtualenv package:

```bash
pip3 install virtualenv
```

Create the Environment for Facenet:

```bash
virtualenv --python=/usr/bin/python3.6 frs_env
```

Activate the virtual environment:

```bash
source frs_env/bin/activate
```

Install CMake:

```bash
pip install cmake==3.18.4.post1
```

Install torch, torchvision and torch audio:

```bash
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cpu
```

Install the required packages from requirements.txt:

```bash
pip install -r requirements.txt
```

Run Milvus Docker:

```bash
sudo docker-compose up -d
```

Run Service:

```bash
gunicorn -w 4 -t 10000 --bind 0.0.0.0:5003 app:app 
```

## Extra (Milvus Docker) 

<b>Note:</b> Only use these commands to run/test Milvus docker image in separate screen. Run these commands carefully. Start Docker Image in the same frs_milvus path.  

To Run Milvus Service in New Screen:

```bash
screen -S FRS_Milvus
```

To Start Milvus:

```bash
sudo docker-compose up -d
```

To Check the status of the container:

```bash
sudo docker-compose ps
```

To Stop Milvus:

```bash
sudo docker-compose down
```

To delete after stoping milvus:

```bash
sudo rm -rf volumes
```

To disply list of all running docker images on the system:

```bash
sudo docker container ls
```

## Usage

```python
import requests

# To Extract Image Embeddings and save it on the Milvus Database
response = requests.post(ip:port, json={"imageUrl": single_image_url_string})
print(response.json()["data"])

# To Search for Similar Images, we are using Milvus Search
response = requests.post(ip:port+"/milvus/search", json={"imageUrl": single_image_url_string})
print(response.json()["data"])
```

