#!/bin/bash

rm -f server/databases/frontend.db*
rm -rf migrations

flask db init
flask db migrate
flask db upgrade
