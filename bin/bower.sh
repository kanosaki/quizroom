#!/bin/bash

cd $(dirname $0)/..

./manage.py bower $*
./manage.py collectstatic
