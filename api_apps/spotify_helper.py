# shows a user's playlists (need to be authenticated via oauth)

import sys
import spotipy
import spotipy.util as util
import pdb
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import time


def build_spotify_object(client_id, client_secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def convert_date_to_int(date_my_str):
    return time.mktime(datetime.strptime(date_my_str, "%Y-%m-%dT%H:%M:%SZ").timetuple())


def list_playlist_videos(spotify_obj, playlist_obj, sort_by=None):
    def add_tracks(playlist_tracks, results):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            playlist_tracks.append({
		'id': track['id'],
                'name': track['name'],
                'album': track['album']['name'],
                'artists': ", ".join([artist['name'] for artist in track['album']['artists']]),
                'thumbnail': track['album']['images'][0]['url'],
                'added_at': item['added_at']
            })
            # print item

    username, playlist_id = playlist_obj['ID'].split(':')[2], playlist_obj['ID'].split(':')[4]
    results = spotify_obj.user_playlist(username, playlist_id)

    all_playlist_tracks = []
    tracks = results['tracks']
    add_tracks(all_playlist_tracks, tracks)
    while tracks['next']:
        tracks = spotify_obj.next(tracks)
        add_tracks(all_playlist_tracks, tracks)
    for i, track in enumerate(all_playlist_tracks):
        track['index'] = i+1

    # for i, track in enumerate(all_playlist_tracks):
    #     print("   %d %32.32s %s" % (track['index'], track['artists'], track['name']))
    # pdb.set_trace()


    ## Add the sorting logic
    # SYNTAX:
    #          'added_at'  -> This will sort it using the timestamp in ASCENDING order
    #          '!added_at' -> This will sort using the timestamp in DESCENDING order
    if sort_by:
        is_descending_order = True if sort_by[0] == '!' else False
        sort_by = sort_by[1:] if sort_by[0] == "!" else sort_by
        print("\t\tSPOTIFY PLAYLIST: Sorting by '%s' in 'is_descending_order=%s'" %(sort_by, str(is_descending_order)))
        if sort_by == 'added_at':
            all_playlist_tracks.sort(key=lambda _item: convert_date_to_int(_item['added_at']), reverse=is_descending_order)
        else:
            print("UNKNOWN sort_by: %s" %(sort_by))

    return all_playlist_tracks


if __name__ == '__main__':
    sp = build_spotify_object(client_id="f6f53ad68e53447db3d0f445b17d14d6", client_secret="39fd4df534e84de6b37f9d5d8096ad09")
    list_playlist_videos(sp, "spotify:user:pinkeshbadjatiya:playlist:4IpU3hnDqV8KMZIHPo4LjD")
