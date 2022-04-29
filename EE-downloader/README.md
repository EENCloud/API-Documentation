## EE-downloader ##

This sample webapp uses the Eagle Eye prefetch API.  It handles making requests from videos from the previous 24 hours.  It also handles receiving the webhooks and storing their status in redis.  Because this is using webhooks you'll want to have a way to expose these to the internet.  The webhook receiving URL should be accessable by *.eagleeyenetworks.com


 - this is using python 3.7
 - you'll need to have requests, flask, redis installed
 - set debug to `False `
 - `pip3 install -r requirements.txt`
 - `export FLASK_ENV=production`
 - `chomod +x startup.sh`

 then run it 
 - `./startup.sh`

 or you can use docker

  - `docker build -t ee-downloader .`
  - `docker run -d -p 4000:4000 ee-downloader`
