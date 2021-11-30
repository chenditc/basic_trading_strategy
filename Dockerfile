FROM tradingrepo.azurecr.io/vnpy:latest

MAINTAINER chendi chenditc@gmail.com 

# Install software
COPY strategies /strategies
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm /requirements.txt
