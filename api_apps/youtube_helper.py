#!/usr/bin/python

from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json

import codecs

LANGUAGE = "en"


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



def playlist_add_video(youtube, video_id, playlist_id):
  playlist_insert_response = youtube.playlistItems().insert(
    part="snippet,status",
    body=dict(
      snippet=dict(
	playlistId=playlist_id,
	position=0,
	resourceId=dict(
	  videoId=video_id,
	  kind="youtube#video"
	)
      )
    )
  ).execute()
  return playlist_insert_response


if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="Google")
  args = argparser.parse_args()

  try:
    youtube_search(args.q)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
