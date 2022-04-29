

# webservice that is tracking the found QR coodes
TRACKER_HOST = "http://localhost:3000"

# setting up some parameters for posting annotations

# minimum time to wait between updating the current annotationo
MIN_DELAY_BETWEEN_ANNT = 7

# maimum value between the last annotationo for the current QR code,
# try to update the current annotation if it can be updated, 
# if it exceeds this time a new annotation will be created 
# instead of updating the current annotationo
MAX_DELAY_BETWEEN_ANNT = 10
