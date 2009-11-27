#!/bin/sh

WORKON_HOME=/home/turan.lart.no/
PROJECT_ROOT=/home/turan.lart.no/pinax-env/turansite

# activate virtual environment
. $WORKON_HOME/pinax-env/bin/activate

cd $PROJECT_ROOT
python manage.py send_mail >> $PROJECT_ROOT/logs/cron_mail.log 2>&1
