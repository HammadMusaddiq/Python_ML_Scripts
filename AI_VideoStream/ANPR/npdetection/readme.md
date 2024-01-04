# LNPD (Licence Number Plate Detection)

## Virtual Environment Creation 

Create the Environment for LNPD:

```bash
virtualenv --python=/usr/bin/python3.6 lnpd_env
```

Activate the virtual environment:

```bash
source lnpd_env/bin/activate
```

Install the required packages from requirements.txt:

```bash
pip install -r requirements.txt
```

Install Tesseract:
```bash
sudo apt-get install libleptonica-dev tesseract-ocr libtesseract-dev python3-pil tesseract-ocr-eng tesseract-ocr-script-latn
```

Install flask:

```bash
pip install flask
```

Install gunicorn:

```bash
pip install gunicorn
```
## Usage

```python
import requests
#send post request on ip and port for LNPD from config
response = requests.post(ip:port, json={"imageUrl": Single_String_URL})

print(response.json()["data"])
```
