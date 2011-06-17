#!/bin/sh

WORKON_HOME=/home/turan.no/
PROJECT_ROOT=/home/turan.no/turansite

# activate virtual environment
. $WORKON_HOME/bin/activate

cd $PROJECT_ROOT
python manage.py send_mail >> $PROJECT_ROOT/logs/cron_mail.log 2>&1
