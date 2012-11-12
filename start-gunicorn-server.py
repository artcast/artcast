#!/bin/sh

/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin/gunicorn --workers=2 -k gevent gunicorn-server:application
