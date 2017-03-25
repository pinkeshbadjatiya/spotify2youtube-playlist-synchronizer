#!/usr/bin/python

import httplib2
import os
import sys
import pdb

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


from youtube_helper import youtube_search, playlist_add_video

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRET_LOCATION = os.path.join(os.path.dirname(__file__), "../configurations")
CLIENT_SECRETS_FILE = "client_secret_api-listener.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(CLIENT_SECRET_LOCATION ,
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

LAST_REDEMPTION_PLAYLIST = "PLY9u75QG8XbV8pZLq9WMBAgimogrmYiS_"



def build_youtube_object():
  # Run with the argument --noauth_local_webserver for the 1st time to store the credentiald
  flow = flow_from_clientsecrets(os.path.join(CLIENT_SECRET_LOCATION, CLIENT_SECRETS_FILE),
    message=MISSING_CLIENT_SECRETS_MESSAGE,
    scope=YOUTUBE_READ_WRITE_SCOPE)

  storage = Storage("googlecredentials-oauth2.json")
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, storage, flags)

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))
  return youtube


def _select_best_video(videos):
  # Time to show some intelligence!
  # Each video item is of the following format:
  # item = {
  #           "videoId":"OjGrcJ4lZCc",
  #           "videoTitle":"This is title",
  #           "channelId":"UC0C-w0YjGpqDXGB8IHb662A",
  #           "channelTitle":"This is channel name",
  #           "channelVerified":True
  #        }

  # Method: 1
  # Try to get video from the verified channel from the Top 5 results and choose the one with the max no of subs
  _videos = [vid for vid in videos[:5] if vid["channelVerified"]]               # Get verified channels from the Top 5 results
  _videos = sorted(_videos, key=lambda k: k["channelSubsCount"], reverse=True)  # Sort in descending order using the subsCount
  keywords_list = [
                    ["official", "music", "video"],
                    ["official", "video"],
                    ["official", "music", "audio"],
                    ["official", "lyric", "video"]
                  ]
  for keywords in keywords_list:
    for video in _videos:           # First match the 1st tuple across all the videos, then switch to the next set of keywords
      _video_name = video["videoTitle"].lower()
      if all(keyword in _video_name for keyword in keywords):     # Match all keywords in videoName
        return video
  if len(_videos):
    return _videos[0]

  # Method: 2
  # If heuristic fails, try to return video with max number of subscribers from the verified channel
  # Try this from the remaining results
  _videos = [vid for vid in videos[5:] if vid["channelVerified"]]         # Get top 5
  _videos = sorted(videos, key=lambda k: k["channelSubsCount"], reverse=True)   # Sort in descending order using the subsCount
  if len(_videos):
    return _videos[0]

  # Fallback:
  # If nothing works out, then FALLBACK to the 1st result
  return videos[0]


def spotify2youtube(query):
  youtube = build_youtube_object()
  print "##############################"
  print "Query: %s" %(query)
  print "##############################"
  videos = youtube_search(youtube, query)
  video = _select_best_video(videos)
  #print video
  response = playlist_add_video(youtube, video["id"], LAST_REDEMPTION_PLAYLIST)
  print response


if __name__=="__main__":
  print "Test!"
  print "Use  --noauth_local_webserver and run spotify2youtube.py to save the credentials"
  youtube = build_youtube_object()
  pdb.set_trace()
  #spotify2youtube("Google")
