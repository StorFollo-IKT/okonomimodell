#!/usr/bin/env sh

BASEDIR=$(dirname "$0")

/usr/bin/python3 "$BASEDIR/manage.py" load_organisations all
/usr/bin/python3 "$BASEDIR/manage.py" load_resources all

/usr/bin/python3 "$BASEDIR/manage.py" load_users
/usr/bin/python3 "$BASEDIR/manage.py" match_users

/usr/bin/python3 "$BASEDIR/manage.py" load_workstations
/usr/bin/python3 "$BASEDIR/manage.py" load_servers