import logging

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from hashlib import sha256
from requests import get

from model import RawData
from database import insert_raw_data
from database import select_latest_raw_data


flask_app = Flask(__name__)
logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


@flask_app.route("/")
def status():
  latest_raw_data = select_latest_raw_data()
  if latest_raw_data is not None:
    latest_raw_data_hash = latest_raw_data.hash
    latest_raw_data_retrieved = latest_raw_data.retrieved
  else:
    latest_raw_data_hash = None
    latest_raw_data_retrieved = None
  return {
    "latest_data_hash": latest_raw_data_hash,
    "latest_data_retrieved": latest_raw_data_retrieved,
  }


def get_latest_data():
  logger.info("Getting latest data")
  current_incidents = get("https://nrkbproxy.beh.uk/incidents.xml", headers={"user-agent": "not-requests"}).text
  current_hash = sha256(current_incidents.encode()).digest().hex()
  latest_raw_data = select_latest_raw_data()
  if latest_raw_data is not None and latest_raw_data.hash == current_hash:
    logger.info("Current data is up-to-date")
  else:
    logger.info("Updated data retrieved, storing...")
    insert_raw_data(RawData(
      hash=current_hash,
      data=current_incidents,
    ))


logging.basicConfig(level=logging.INFO)
get_latest_data()
scheduler.start()
scheduler.add_job(get_latest_data, "interval", minutes=1)

if __name__ == "__main__":
  flask_app.run()
