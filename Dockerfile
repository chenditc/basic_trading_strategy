FROM tradingrepo.azurecr.io/vnpy:latest

MAINTAINER chendi chenditc@gmail.com 

# Install software
COPY strategies /strategies
COPY scripts /scripts
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm /requirements.txt

ENV PYTHONPATH=/strategies/

COPY start_notebook.sh /start_notebook.sh
CMD bash /start_notebook.sh
