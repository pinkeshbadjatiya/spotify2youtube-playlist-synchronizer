#!/usr/bin/python

import sys, pdb
from youtube_helper import build_youtube_object, youtube_search, playlist_add_video


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

  # TODO: Take views of video also into account
  # TODO: Give weightage to views more than subs

  # Method: 1
  # Try to get video from the verified channel from the Top 5 results and choose the one with the max no of subs
  _videos = [vid for vid in videos[:5] if vid["channelVerified"]]               # Get verified channels from the Top 5 results
  _videos = sorted(_videos, key=lambda k: k["channelSubsCount"], reverse=True)  # Sort in descending order using the subsCount
  keywords_list = [
                    ["official", "music", "video"],
                    ["official", "video"],
                    ["original", "version"],
                    ["!video", "!audio", "!lyrics"],
                    ["official", "lyric", "video"],
                    ["official", "music", "audio"],
                    ["official", "audio"],
                    ["audio", "only"]
                  ]
  for keywords in keywords_list:
    for video in _videos:           # First match the 1st tuple across all the videos, then switch to the next set of keywords
      _video_name = video["videoTitle"].lower()
      all_match = True
      for keyword in keywords:     # Match all keywords in videoName
          if keyword[0] == "!":
              all_match = all_match and (keyword[1:] not in _video_name)
          else:
              all_match = all_match and (keyword in _video_name)

      if all_match:
          return video

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


def spotify2youtube(youtube_obj, PLAYLIST, query):
  # youtube = build_youtube_object()
  print "##############################"
  print "Query: %s" %(query)
  print "##############################"
  videos = youtube_search(youtube_obj, query)
  video = _select_best_video(videos)
  #print video
  response = playlist_add_video(youtube_obj, video["videoId"], PLAYLIST)
  # print response
  return response


if __name__=="__main__":
  print "Test!"
  print "Use  --noauth_local_webserver and run spotify2youtube.py to save the credentials"
  youtube = build_youtube_object()
  pdb.set_trace()
  #spotify2youtube("Google")
