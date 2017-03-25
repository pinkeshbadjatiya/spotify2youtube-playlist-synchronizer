#!/usr/bin/python

from apiclient.errors import HttpError
from oauth2client.tools import argparser

import codecs


def youtube_search(youtube, query):
  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=query,
    type="video",
    part="id,snippet",
    order='relevance'
  ).execute()

  search_videos = []
  for item in search_response.get("items", []):
    print item
    video = {}
    video["id"] = item["id"]["videoId"]
    video["title"] = codecs.encode(item["snippet"]["title"], "utf-8")
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
