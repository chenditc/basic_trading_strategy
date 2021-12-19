FROM chenditc/vnpy:latest

MAINTAINER chendi chenditc@gmail.com 

# Install software
COPY strategies /strategies
COPY scripts /scripts
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt && rm /requirements.txt

ENV PYTHONPATH=/strategies/

CMD bash /scripts/start_notebook.sh
