#!/bin/sh

echo "Don't forget to activate the virtual env"
echo "  source /usr/local/virtualEnvs/captureQC/bin/activate"
echo

. /usr/local/virtualEnvs/captureQC/bin/activate
#PYTHONPATH=/var/webSites/captureQC.advanceQC.com/htdocs/aqc \
TNS_ADMIN=/usr/local/oracle/instantclient_11_2 \
     python \
     `pwd`/captureQC/manage.py runserver 0.0.0.0:8000
deactivate
