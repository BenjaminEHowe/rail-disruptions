import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from flask import Flask
from hashlib import sha256
from io import BytesIO
from minio import Minio
from requests import get


def get_env(name, default=None):
  var = os.environ.get(name)
  if var is not None:
    return var
  if default is not None:
    return default
  raise RuntimeError(f"Environment variable {name} is required!")


bucket = get_env("S3_BUCKET")
client = Minio(
    get_env("S3_ENDPOINT"),
    access_key=get_env("S3_ACCESS_KEY"),
    secret_key=get_env("S3_SECRET_KEY"),
    region="unused",
    secure=bool(get_env("S3_SECURE", True)),
)
flask_app = Flask(__name__)
logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


@flask_app.route("/")
def status():
  return {
    "latest_data_hash": latest_hash,
    "latest_data_retrieved": latest_data_received,
  }


def get_latest_hash_from_storage():
  logger.info("Retrieving stored data from S3")
  objects = client.list_objects(bucket, recursive=True)
  filenames = sorted([obj.object_name for obj in objects], reverse=True)
  if filenames:
    return filenames[0].split(".")[0].split("_")[1]
  return None


def get_latest_data():
  global latest_data_received, latest_hash
  logger.info("Getting latest data")
  current_incidents = get("https://nrkbproxy.beh.uk/incidents.xml", headers={"user-agent": "not-requests"}).text
  current_hash = sha256(current_incidents.encode()).digest().hex()
  if latest_hash == current_hash:
    logger.info("Current data is up-to-date")
  else:
    logger.info("Updated data retrieved, storing...")
    now = datetime.now().strftime("%Y-%m-%dT%H%M%S")
    filename = f"{now}_{current_hash}.xml"
    data = current_incidents.encode("utf-8")
    client.put_object(
      bucket,
      filename,
      BytesIO(data),
      length=len(data),
      content_type="application/xml",
    )
    latest_data_received = now
    latest_hash = current_hash



logging.basicConfig(level=logging.INFO)
latest_data_received = None
latest_hash = get_latest_hash_from_storage()
get_latest_data()
scheduler.start()
scheduler.add_job(get_latest_data, "interval", minutes=1)

if __name__ == "__main__":
  flask_app.run()
