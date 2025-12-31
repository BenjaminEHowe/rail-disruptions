#!/bin/sh
exec gunicorn -b :5000 --error-logfile - ingester:flask_app
