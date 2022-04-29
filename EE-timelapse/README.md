## EE-timelapse ##

You need to do some stuff to get this up and running.  If you are not using Docker than you will also need FFmpeg installed.

 - this is using python 3, should be minor work on convert backwards to python 2
 - `pip install -r requirements.txt`

 then run it 
 - `./startup.sh`

 or you can use docker

  - `docker build -t ee-timelapse .`
  - `docker run -d -p 4000:4000 ee-timelapse`

or docker-compose

 - `docker-compose up --build`
