#!/bin/sh

script=`readlink -f $0`
WEBAPP_DIR=${script%/*}
HTDOC_DIR=${WEBAPP_DIR%/*}

cd $HTDOC_DIR

uid=`ls -ld . | awk '{print $3}'`
gid=`ls -ld . | awk '{print $4}'`

chown -R $uid:$gid .
find $WEBAPP_DIR -type d              -exec chmod 2755  {} \;
find $WEBAPP_DIR -type f              -exec chmod 0644  {} \;
find $WEBAPP_DIR -type f -name '*.sh' -exec chmod +x    {} \;

chmod -R g+w $WEBAPP_DIR/media
chmod    g+w $WEBAPP_DIR/root
chmod    g+w $WEBAPP_DIR/root/db.sqlite3
chmod    g+w $WEBAPP_DIR/root/wsgi.py

touch $WEBAPP_DIR/root/wsgi.py
