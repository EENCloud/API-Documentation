#!/bin/bash

# delete files older than 1 day old
find ./flv/* -mtime +1 -type f -delete
find ./tmp/* -mtime +1 -type f -delete


