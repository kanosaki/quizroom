#!/bin/bash
echo 'Booting server...'
cd $(dirname $0)/..

# Boot WebSocket server
python tornado_main.py &
TORNADO_PID=$!
trap "kill $TORNADO_PID" 1 2 3 15


# Boot Django Web app
python manage.py runserver
kill $TORNADO_PID
