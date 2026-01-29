#!/bin/sh
exec gunicorn -b :5000 --error-logfile - parser:flask_app
