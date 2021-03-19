#!/bin/bash

curl http://127.0.0.1:5000/getToken -d username=maxim -d password=foo -D headers -b cookie-jar -c cookie-jar > testout.log

curl http://127.0.0.1:5000/refreshToken  -D headers -b cookie-jar -c cookie-jar   >> testout.log



