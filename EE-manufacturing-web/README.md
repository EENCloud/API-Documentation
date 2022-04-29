

## Eagle Eye Networks Application Note ##

### Detecting QR codes in a manufacturing environment ###

This is supporting code to go along with the published Application Note.  It is intended to show how QR codes can be detected using video security cameras.  This code runs in conjunction with the companion video analysis software *link* 

### Installation ###

This project uses Flask and Python3.  It is recommend to use Docker.

To build the docker container

`docker build -t webapp .`

to run it

`docker run -it -p 3000:3000 webapp`

If you choose not to use Docker, you can find all the steps required to install on a linux server inside the `Dockerfile`


### Questions, Comments, Suggestions ###

If you have questions, please feel free to reach out to us at api_support@een.com