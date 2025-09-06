import apscheduler.schedulers.background
import flask
import logging
import os
import pprint

from datetime import datetime

import api


app = flask.Flask(__name__)
logger = logging.getLogger(__name__)
nrDisruptions = api.NRDisruptionsClient(
  base_url=os.environ.get("NR_KB_PROXY_URL") or "https://nrkbproxy.beh.uk",
)
scheduler = apscheduler.schedulers.background.BackgroundScheduler()

# TODO: migrate the below state into a database
incidentDetails = {}
serviceIndicators = []
updated_ts = datetime.now()


@app.route("/")
def all_operators():
  return flask.render_template(
    "all_operators.html",
    incidentDetails=incidentDetails,
    serviceIndicators=serviceIndicators,
  )


@app.route("/operator/<operator_code>")
def operator(operator_code: str):
  service_indicator = list(filter(lambda x: x.operator.code == operator_code, serviceIndicators))[0]
  title = f"{service_indicator.operator.name} ({operator_code})"
  relevant_incidents = []
  for incidentWithoutDetails in service_indicator.incidents:
    relevant_incidents.append(incidentDetails[incidentWithoutDetails.id])
  relevant_incidents.sort(key=lambda x: x.lastUpdatedTs)
  relevant_incidents.reverse()
  return flask.render_template(
    "operator.html",
    title=title,
    feedUrl=f"/operator/{operator_code}/feed",
    incidents=relevant_incidents,
    updatedTs=updated_ts,
  )


@app.route("/operator/<operator_code>/feed")
def operator_feed(operator_code: str):
  service_indicator = list(filter(lambda x: x.operator.code == operator_code, serviceIndicators))[0]
  title = f"{service_indicator.operator.name} ({operator_code})"
  relevant_incidents = []
  for incidentWithoutDetails in service_indicator.incidents:
    relevant_incidents.append(incidentDetails[incidentWithoutDetails.id])
  relevant_incidents.sort(key=lambda x: x.lastUpdatedTs)
  relevant_incidents.reverse()
  if relevant_incidents:
    feed_updated_ts = max(relevant_incidents, key=lambda x: x.lastUpdatedTs).lastUpdatedTs
  else:
    feed_updated_ts = updated_ts
  response = flask.make_response(flask.render_template(
    "operator_feed.xml",
    title=title,
    updated_ts=feed_updated_ts,
    operator_code=operator_code,
    incidents=relevant_incidents,
  ))
  response.headers["Content-type"] = "text/xml; charset=utf-8"
  return response


@app.route("/raw")
def raw_data():
  return flask.render_template(
    "raw.html",
    title="Raw Data",
    incidentDetails=pprint.pformat(list(incidentDetails.values()), indent=2, width=140),
    serviceIndicators=pprint.pformat(serviceIndicators, indent=2, width=140),
  )


def refresh_cached_data():
  global incidentDetails, serviceIndicators, updated_ts
  logger.info("Getting updated data from API")
  now = datetime.now().astimezone(api.TIMEZONE)

  # fetch service indicators
  serviceIndicators = nrDisruptions.get_toc_service_indicators()
  serviceIndicators.sort(key=lambda x: x.operator.name.lower())

  # fetch incidents
  incidentDetails = nrDisruptions.get_incident_details()

  updated_ts = now
  logger.info("Cached data updated successfully")


logging.basicConfig(level=logging.INFO)
refresh_cached_data()
scheduler.start()
scheduler.add_job(refresh_cached_data, "interval", minutes=5)
