FROM python:3.6

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD . ./schema_collector
WORKDIR schema_collector

ENV PYTHONPATH $PYTHONPATH:/schema_collector

ENTRYPOINT ["gunicorn"]
CMD ["-w", "4", "-b", "0.0.0.0:7500", "-t", "150", "-k", "aiohttp.worker.GunicornWebWorker", "schema_collector.app:app"]
