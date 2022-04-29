#!/bin/bash

# keep the login credentials valid, run this script in crontab
# 0 * * * * /home/mcotton/dev/php-een/keep_alive.sh

wget --output-file=/dev/null https://een.cloud/php-een/page.html

