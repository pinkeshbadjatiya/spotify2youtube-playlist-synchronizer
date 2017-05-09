#!/usr/bin/python

import httplib2
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json, os, codecs

LANGUAGE = "en"


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
#CLIENT_SECRET_LOCATION = os.path.join(os.path.dirname(__file__), "../configurations")

#CLIENT_SECRET_LOCATION = current_app.iniconfig['YOUTUBE_API']['CLIENT_SECRET_LOCATION']
#CLIENT_SECRETS_FILE = current_app.iniconfig['YOUTUBE_CLIENT_SECRETS_FILE']

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# PLAYLIST = current_app.iniconfig['PLAYLIST_ID']



def build_youtube_object(client_secret_location, client_secrets_file, credentials_storage):
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
  """ % os.path.abspath(os.path.join(client_secret_location ,
                                     client_secrets_file))

  # Run with the argument --noauth_local_webserver for the 1st time to store the credentiald
  flow = flow_from_clientsecrets(os.path.join(client_secret_location, client_secrets_file), message=MISSING_CLIENT_SECRETS_MESSAGE,
        scope=YOUTUBE_READ_WRITE_SCOPE)

  storage = Storage(credentials_storage)
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, storage, flags)

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))
  return youtube



def check_channel_verification_status(youtube, channelId):
  # Since we cannot have direct check, we check is subs_count >= 100,000
  # Input: channelId
  # Output: True if verified, False if not + SubscriberCount

  SUBS_COUNT_LIMIT = 100000

  search_response = youtube.channels().list(
    part="statistics",
    id=channelId,
    hl=LANGUAGE
  ).execute()

  for item in search_response.get("items", []):
    if not item["statistics"]["hiddenSubscriberCount"]:     # Subs counts not hidden
      if int(item["statistics"]["subscriberCount"]) >= SUBS_COUNT_LIMIT:
        return True, int(item["statistics"]["subscriberCount"])
  return False, int(item["statistics"]["subscriberCount"])



def youtube_search(youtube, query):
  # Call the search.list method to retrieve results matching the specified
  # query term.

  MAX_RESULTS = 10 # youtube.com shows 20 results per page

  search_response = youtube.search().list(
    q=query,
    type="video",
    part="id,snippet",
    order='relevance',
    relevanceLanguage=LANGUAGE,
    maxResults=MAX_RESULTS
  ).execute()

  search_videos = []
  for i, item in enumerate(search_response.get("items", [])):
    #if not i:
    #  print json.dumps(item, sort_keys=True, indent=4)

    if item["id"]["kind"] == "youtube#video":
      video = {}
      video["videoId"], video["channelId"] = item["id"]["videoId"], item["snippet"]["channelId"]
      video["videoTitle"], video["channelTitle"] = codecs.encode(item["snippet"]["title"], "utf-8"), codecs.encode(item["snippet"]["channelTitle"], "utf-8")
      video["channelVerified"], video["channelSubsCount"] = check_channel_verification_status(youtube, video["channelId"])
      search_videos.append(video)

  return search_videos

#  Call the videos.list method to retrieve location details for each video.
#  video_response = youtube.videos().list(
#    id=video_ids,
#    part='snippet, recordingDetails'
#  ).execute()
#


def list_playlist_videos(youtube, playlist_obj):
  # Retrieve the list of videos uploaded to the authenticated user's channel.
  playlistitems_list_request = youtube.playlistItems().list(
    playlistId=playlist_obj['ID'],
    part="snippet",
    maxResults=50
  )

  videos = []
  while playlistitems_list_request:
    playlistitems_list_response = playlistitems_list_request.execute()

    # Print information about each video.
    for playlist_item in playlistitems_list_response["items"]:
      id = playlist_item["id"]
      title = playlist_item["snippet"]["title"]
      index = playlist_item["snippet"]["position"]
      video_id = playlist_item["snippet"]["resourceId"]["videoId"]
      thumbnail = playlist_item["snippet"]["thumbnails"]["default"]['url']

    #   print "%s (%s)\n %s\n" % (title, video_id, thumbnail)
      videos.append({
        'delete_id': id,    # Useful only when we delete video from playlist
        'video_index': index + 1,
        'video_title': title,
        'video_id': video_id,
        'video_thumbnail': thumbnail
      })
    playlistitems_list_request = youtube.playlistItems().list_next(
      playlistitems_list_request, playlistitems_list_response)
  return videos


def playlist_add_video(youtube, video_id, playlist_obj):
  playlist_insert_response = youtube.playlistItems().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
	playlistId=playlist_obj['ID'],
	position=0,
	resourceId=dict(
	  videoId=video_id,
	  kind="youtube#video"
	)
      )
    )
  ).execute()
  return playlist_insert_response


def playlist_delete_video(youtube, video_delete_id):
  playlist_delete_response = youtube.playlistItems().delete(
    id=video_delete_id,
  ).execute()
  return playlist_delete_response


if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="Google")
  args = argparser.parse_args()

  try:
    youtube_search(args.q)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
