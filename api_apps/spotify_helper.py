# shows a user's playlists (need to be authenticated via oauth)

import sys
import spotipy
import spotipy.util as util
import pdb
from spotipy.oauth2 import SpotifyClientCredentials



def build_spotify_object(client_id, client_secret):
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return sp

def list_playlist_videos(spotify_obj, playlist_obj):
    def add_tracks(playlist_tracks, results):
        for i, item in enumerate(tracks['items']):
            track = item['track']
            playlist_tracks.append({
                'name': track['name'],
                'album': track['album']['name'],
                'artists': ", ".join([artist['name'] for artist in track['album']['artists']]),
                'thumbnail': track['album']['images'][0]['url']
            })
            # print item
            # pdb.set_trace()

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
    return all_playlist_tracks


if __name__ == '__main__':
    sp = build_spotify_object(client_id="f6f53ad68e53447db3d0f445b17d14d6", client_secret="39fd4df534e84de6b37f9d5d8096ad09")
    list_playlist_videos(sp, "spotify:user:pinkeshbadjatiya:playlist:4IpU3hnDqV8KMZIHPo4LjD")
