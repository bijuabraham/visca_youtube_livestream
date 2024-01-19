#!/usr/bin/python
__author__ = 'Biju Abraham'
__copyright__ = "Mar Thoma Church of San Francisco"
__credits__ = ["Google API Python Client Authors"]
#
# pip3 install oauth2client
# pip3 install google-auth-oauthlib
# pip3 install google-api-python-client
# pip3 install google-auth
# THis program will do the following
# - Check if the OAuth token exists if not create one
# - Refresh the token if it has expired

import os
import sys
import time
import datetime
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import logging
from logging.handlers import RotatingFileHandler

# Define the scopes required for YouTube API access
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

def get_authenticated_service():
    # Check if the OAuth token exists
    if os.path.exists('token.pickle'):
        # Load the existing token
        with open('token.pickle', 'rb') as token_file:
            credentials = pickle.load(token_file)
    else:
        # Create a new OAuth token
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', SCOPES)
        credentials = flow.run_local_server(port=0)
        log.warn("Pickle file was missing. Created a new one")
        # Save the token for future use
        with open('token.pickle', 'wb') as token_file:
            pickle.dump(credentials, token_file)

    # Refresh the token if it has expired
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        log.warn("Token Expired. Refreshed")
        # Save the refreshed token
        with open('token.pickle', 'wb') as token_file:
            pickle.dump(credentials, token_file)
    return

# Create a rotating log handler

log = logging.getLogger('status_logger')
log.setLevel(logging.INFO)
sthandler = RotatingFileHandler('/var/log/livestream/status.log', maxBytes=9000000, backupCount=2)
stformatter = logging.Formatter('%(asctime)s--%(levelname)s (%(threadName)-10s) %(message)s')
sthandler.setFormatter(stformatter)
log.addHandler(sthandler)

# Create a loop and call get_authenticated_service() every 20 minutes
while True:
    get_authenticated_service()
    log.info("Token Checked and updated")
    time.sleep(1200)


    

