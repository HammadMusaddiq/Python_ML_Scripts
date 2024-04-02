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

