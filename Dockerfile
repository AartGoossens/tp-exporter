FROM python:3.8-slim

RUN apt update -y && apt install -y wget

WORKDIR /tmp
RUN apt-get update -y
RUN apt-get install -y software-properties-common
# RUN add-apt-repository -y ppa:canonical-chromium-builds/stage
# RUN apt-get update -y
RUN apt-get install -y chromium
RUN apt-get install -y chromium-driver

# RUN wget https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip -O chromedriver.zip
# RUN tar -xvzf chromedriver.zip
# RUN chmod +x chromedriver
# RUN mv ./chromedriver /usr/local/bin/

RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv

RUN mkdir /app
COPY Pipfile Pipfile.lock /app/

WORKDIR /app

RUN pipenv install --system

COPY . /app/

CMD python sync.py
