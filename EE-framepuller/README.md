# EE-framepuller ##

Wrapper to pull a single frame out of video


 - `docker build -t ee-framepuller .`
 - `docker run -d -p 4000:4000 ee-framepuller`

Or you can launch it using docker-compose:

 - `docker-compose up`

If you are going run this in production you might want to:

 - set debug to `False`
 - `export FLASK_ENV=production`

