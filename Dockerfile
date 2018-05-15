FROM python:3.6

ENV PYTHONUNBUFFERED 1

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . ./schema_collector
WORKDIR schema_collector

ENV PYTHONPATH $PYTHONPATH:/schema_collector

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8900", "-t", "150", "-k", "aiohttp.worker.GunicornWebWorker", "schema_collector.app:app"]
