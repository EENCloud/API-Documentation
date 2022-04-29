#!/bin/bash

#python3 -u server.py
gunicorn --bind 0.0.0.0:3000 --limit-request-line 0 --worker-class=gthread --threads=4 wsgi:app
