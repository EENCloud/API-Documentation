# EE-monitor #
Quick monitor tool using the Eagle Eye Networks API.

## Installation ##
`docker-compose up --build -d`

or you can run it locally on python3.  Make sure to regenerate the secret_key in `settings.py`


## Usage ##
Start the Docker container, visit the URL in your browser, login with a valid Eagle Eye email/password combination that has access to cameras.

## Troubleshooting ##
 - Are you in the subaccount or the reseller account? You need to be in an account with devices
 - Do you have access cameras? You need cameras to choose from
 - Do you have proper permissions? You need permission to see the live streams
