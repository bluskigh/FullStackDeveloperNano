FROM python:stretch

copy . /app
WORKDIR /app

RUN apt-get update
RUN apt -y install python 
RUN apt -y install python-pip 
RUN pip install -r requirements.txt 

ENTRYPOINT ["gunicorn", "-b", ":8080", "main:APP"]
