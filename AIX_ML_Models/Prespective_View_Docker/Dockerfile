FROM python:3.8

WORKDIR /app/

COPY . /app/

EXPOSE 8001

RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip3 install -r requirements.txt

CMD gunicorn -w 2 -t 10000 --bind 0.0.0.0:8001 app:app 

