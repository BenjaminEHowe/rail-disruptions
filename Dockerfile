FROM python:3.12-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app /app
WORKDIR /app
RUN chmod a+x boot.sh

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
