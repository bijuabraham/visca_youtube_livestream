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
#  1. Start the Broadcast with current time
#  2. Power off camera 
#  3. Power On camera
#  4. Position Camera

import os
import sys
import time
import datetime
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from visca_over_ip import Camera
from datetime import timedelta

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

        # Save the token for future use
        with open('token.pickle', 'wb') as token_file:
            pickle.dump(credentials, token_file)

    # Refresh the token if it has expired
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        # Save the refreshed token
        with open('token.pickle', 'wb') as token_file:
            pickle.dump(credentials, token_file)

    # Build the YouTube service
    service = build('youtube', 'v3', credentials=credentials)
    return service

# Get the authenticated YouTube service
youtube_service = get_authenticated_service()

# start a new broadcasting service
# Define the parameters needed for the API request

# Get the current time
current_time = datetime.datetime.utcnow()

# Set the scheduled start time to 5 minutes from the current time
scheduled_start_time = current_time + timedelta(minutes=5)

# Format the scheduled start time as an ISO 8601 string
scheduled_start_time_str = scheduled_start_time.isoformat() + 'Z'

# Set the scheduled end time to 3 hours (180 minutes) after the scheduled start time
scheduled_end_time = scheduled_start_time + timedelta(minutes=180)

# Format the scheduled end time as an ISO 8601 string
scheduled_end_time_str = scheduled_end_time.isoformat() + 'Z'

# Define the params dictionary with all settings including scheduling
params = {
    'part': 'snippet,status,contentDetails',
    'snippet': {
        'title': 'Mar Thoma Church Of San Francisco - Livestream',
        'scheduledStartTime': scheduled_start_time_str,
        'scheduledEndTime': scheduled_end_time_str
    },
    'status': {
        'privacyStatus': 'public',
        'selfDeclaredMadeForKids': False,  # Indicates if the stream is made for kids
        'liveChatStatus': 'disabled'       # Disables live chat for the stream
    },
    'contentDetails': {
        'enableAutoStart': True,           # Stream starts automatically when a valid signal is detected
        'enableAutoStop': True             # Stream stops automatically when the signal ends
    }
}

broadcast_response = youtube_service.liveBroadcasts().insert(
    part='snippet,status,contentDetails',
    body=params
).execute()
# Get the Broadcast ID
broadcast_id = broadcast_response['id']

print('Broadcast ID: %s' % broadcast_id)

print('Broadcast started successfully!')
print('Powering OFF Camera...')
cam = Camera('108.233.83.51')
cam.set_power(0)
time.sleep(10)
print('Powering ON Camera...')
cam.set_power(1)
time.sleep(45)
print('Panning Camera...')
cam.recall_preset(2)
cam.close_connection()
print('Camera started successfully!')
