FROM python:3.12-slim

RUN useradd -ms /bin/bash appuser
USER appuser
ENV PATH="/home/appuser/.local/bin:${PATH}"
ENV PATH="/home/appuser/.local/lib/python3.12/site-packages:${PATH}"
ENV PYTHONUNBUFFERED=1

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn

COPY app /app
WORKDIR /app

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
