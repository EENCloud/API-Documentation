# EE-streaming #
Quick example project for using the Eagle Eye Networks API.  The goal is to show how a live camera stream can be embedded into a webpage.  This program handles logging into the API, and returns the `camera_id` and `auth_key`.

## Installation ##
`docker-compose up --build -d`

or you can run it locally on python3.

Make sure you have valid credentials in  `local_settings.py`


## Usage ##
This project includes two working demos.  For embedding live video in a webpage with needed to authorize please see:
`demo-live_video.html` 

For embedding live preview stream through websockets, please see:
`demo-live_preview.html`


## Troubleshooting ##
TODO:

