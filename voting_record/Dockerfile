FROM python:3.9
RUN pip install google-cloud-pubsub psycopg2 psycopg
COPY *.json .
ADD main.py .
CMD ["python","-u", "./main.py"] 