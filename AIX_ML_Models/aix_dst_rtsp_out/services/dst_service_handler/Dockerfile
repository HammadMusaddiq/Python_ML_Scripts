FROM python:3.8

WORKDIR /app
COPY dst_service_handler/app/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY dst_service_handler/app /app/