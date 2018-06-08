#!/bin/sh

script=`readlink -f $0`
WEBAPP_DIR=${script%/*}
HTDOC_DIR=${webAppDir%/*}

cd $WEBAPP_DIR

. /usr/local/virtualEnvs/captureQC/bin/activate
python manage.pyc $1
deactivate
