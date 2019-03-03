# from cgi import parse_qs, escape
import re, os
from flask import Flask
from flask import request, url_for, render_template
from flask_ini import FlaskIni

from functools import wraps
from flask import g, request, redirect, url_for, session, flash
import utils
from api_apps import spotify2youtube, youtube_helper, spotify_helper
# from flask.ext.login import current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)
app.iniconfig = FlaskIni()
with app.app_context():
    app.iniconfig.read('./configs/config.ini')
app.secret_key = app.iniconfig['FLASK']['APP_SECRET_KEY']
app.users = utils.load_users(app.iniconfig['FLASK']['USER_FILE'])
app.youtube_obj, app.spotify_obj = None, None


@app.before_request
def before_request():
    # Setup user
    if session.get('logged_in', None):
        g.user = {
            'username': session['username'],
            'secret_key': session['secret_key']
        }
    else:
        g.user = None

    # Setup query objects
    if not app.youtube_obj:
        app.youtube_obj = youtube_helper.build_youtube_object(app.iniconfig['YOUTUBE_API']['CLIENT_SECRET_LOCATION'],
                                                              app.iniconfig['YOUTUBE_API']['CLIENT_SECRETS_FILE'],
                                                              app.iniconfig['YOUTUBE_API']['CREDENTIALS_STORAGE'])
    if not app.spotify_obj:
        app.spotify_obj = spotify_helper.build_spotify_object(client_id=app.iniconfig['SPOTIFY_API']['CLIENT_ID'],
                                                      client_secret=app.iniconfig['SPOTIFY_API']['CLIENT_SECRET'])



def load_playlistmap(playlist_id):
    """ Loads the playlist map from the location "./data/<spotify_playlist_id>/map.txt"
	Each line of the data file i.e. "map.txt" looks like this: 
	
	spotify_song_id,youtube_song_URL

    """
    location = app.iniconfig['FLASK']["DATA_DIRECTORY"] + "/" + playlist_id
    file_name = location + "/" + "map.txt"
    if not os.path.isdir(location):
        os.makedirs(location)
    if not os.path.isfile(file_name):
	with open(file_name, "w") as f:
	    pass


    with open(file_name) as f:
	data = f.readlines()
    spotify_map = {}
    for line in data:
        [spotify_song_id, youtube_id] = line.strip().split(",")
	result = youtube_helper.videos_list_by_id(app.youtube_obj, youtube_id)
	spotify_map[spotify_song_id] = {
	  'video_id': result['items'][0]['id'],	
	  'video_title': result['items'][0]['snippet']['title'],	
	  'video_thumbnail': result['items'][0]['snippet']['thumbnails']['default']['url']
	}

    return spotify_map


def update_playlistmap(old_playlist_map, playlist_id, spotify_id, youtube_url):
    file_name = app.iniconfig["DATA_DIRECTORY"] + "/" + playlist_id + "/" + "map.txt"
    with open(file_name, "a+") as f:
	f.write(spotify_id + "," + youtube_url + "\n")
    old_playlist_map[spotify_id] = youtube_url
    return old_playlist_map

    
    



@app.route("/")
@login_required
def index():
    youtube_playlist = {
        'name': app.iniconfig['YOUTUBE_PLAYLIST']['NAME'],
        'id': app.iniconfig['YOUTUBE_PLAYLIST']['ID'],
        'songs': youtube_helper.list_playlist_videos(app.youtube_obj, app.iniconfig['YOUTUBE_PLAYLIST'])
    }
    spotify_playlist = {
        'name': app.iniconfig['SPOTIFY_PLAYLIST']['NAME'],
        'id': app.iniconfig['SPOTIFY_PLAYLIST']['ID'],
        'songs': spotify_helper.list_playlist_videos(app.spotify_obj, app.iniconfig['SPOTIFY_PLAYLIST'], sort_by='!added_at')
    }
    spotify2youtube_map = load_playlistmap(app.iniconfig['SPOTIFY_PLAYLIST']['ID'])

    # Fill with blank <td>'s so that we have extra rows for extra entries
    you_len, spo_len = len(youtube_playlist['songs']), len(spotify_playlist['songs'])
    if you_len != spo_len:
        if you_len < spo_len:
            youtube_playlist['songs'].extend([None]*(spo_len - you_len))
        else:
            spotify_playlist['songs'].extend([None]*(you_len - spo_len))
    zipped = zip(youtube_playlist['songs'], spotify_playlist['songs'])

    return render_template('index.html', youtube_playlist=youtube_playlist,
					 spotify_playlist=spotify_playlist,
                            		 zipped_songs=zipped,
					 spotify2youtube_map=spotify2youtube_map
			  )


# Use the secret_key in the request to authenticate it.
@app.route("/force_update")
def force_update_spotify2youtube():
    # Truncate the Youtube Playlist
    yt_videos = youtube_helper.list_playlist_videos(app.youtube_obj, app.iniconfig['YOUTUBE_PLAYLIST'])
    print "YT total videos: %d" %(len(yt_videos))
    for i, video in enumerate(yt_videos):
        youtube_helper.playlist_delete_video(app.youtube_obj, video['delete_id'])
        print "Delete - %d/%d" %(i+1, len(yt_videos))

    # Add videos from spotify playlist
    sp_videos = spotify_helper.list_playlist_videos(app.spotify_obj, app.iniconfig['SPOTIFY_PLAYLIST'], sort_by='!added_at')
    print "SP total videos: %d" %(len(sp_videos))
    for i, video in enumerate(reversed(sp_videos)):     # Add songs in the reverse direction to get the latest one on top
        song = video["artists"] + " - " + video["name"]     # Search format is "video_name - artist1, artist2 artist3"
        response = spotify2youtube.spotify2youtube(app.youtube_obj, app.iniconfig['YOUTUBE_PLAYLIST'], song)
        print "Added: %d/%d | %s" %(i+1, len(sp_videos), response["snippet"]["title"].encode("utf-8"))

    return "Success!"


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] not in app.users:
            error = 'Invalid username'
        elif request.form['password'] != app.users[request.form['username']]['password']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            session['secret_key'] = app.users[request.form['username']]['secret_key']
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('logged_in', None)
    session.pop('secret_key', None)
    flash('You were logged out')
    return redirect(url_for('index'))

# @app.route('/entries')
# def show_entries():
#     entries = ["a", "aa", "bb", "ccc"]
#     return render_template('show_entries.html', entries=entries)
#
#
# @app.route('/add', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     flash('New entry was successfully posted')
#     return redirect(url_for('show_entries'))

# def not_found(environ, start_response):
#     """Called if no URL matches."""
#     start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
#     return ['Not Found']
#
# def logs_main(environ, start_response):
#     """Called if no URL matches."""
#     start_response('200 OK', [('Content-Type', 'text/plain')])
#     file_name = "/var/log/upstart/api-listener.log"
#     with open(file_name) as f:
# 	data = f.readlines()
#     return data


@app.route('/spotify2youtube', methods=['GET'])
def spotify2youtube_main():
    """ Like the example above, but it uses the name specified in the URL.
    """
    data = request.args
    song = data.get("song", "")
    response = spotify2youtube.spotify2youtube(app.youtube_obj, app.iniconfig['YOUTUBE_PLAYLIST'], song)
    return song

# # map urls to functions
# urls = [
#     (r'^$', index),
#     (r'logs/?$', logs_main),
#     (r'logs/(.+)?$', logs_main),
#     (r'spotify2youtube/?$', spotify2youtube_main),
#     (r'spotify2youtube/(.+)$', spotify2youtube_main)
# ]

#
# def application(environ, start_response):
#     """
#     The main WSGI application. Dispatch the current request to
#     the functions from above and store the regular expression
#     captures in the WSGI environment as  `myapp.url_args` so that
#     the functions from above can access the url placeholders.
#
#     If nothing matches call the `not_found` function.
#     """
#     path = environ.get('PATH_INFO', '').lstrip('/')
#     for regex, callback in urls:
#         match = re.search(regex, path)
#         if match is not None:
#             environ['myapp.url_args'] = match.groups()
#             return callback(environ, start_response)
#     return not_found(environ, start_response)



if __name__=="__main__":
    # spotify2youtube("Eraser - Ed Sheeran")
    app.run(host='0.0.0.0')
