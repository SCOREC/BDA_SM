#!/bin/bash

rm -f authServer.db
rm -rf migrations

flask db init
flask db migrate
flask db upgrade
