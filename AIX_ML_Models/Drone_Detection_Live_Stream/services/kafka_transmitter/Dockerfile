FROM python:3.8
WORKDIR /app

COPY kafka_transmitter/app/requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

COPY kafka_transmitter/app/main.py .

CMD ["python3", "main.py"]
