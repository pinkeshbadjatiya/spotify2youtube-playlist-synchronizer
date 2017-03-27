from cgi import parse_qs, escape
import re
import conf

conf.load_config()

# Import after loading the settings
from conf import settings
from api_apps.spotify2youtube import spotify2youtube


def index(environ, start_response):
    """This function will be mounted on "/" and display a link
    to the hello world page."""

    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''<pre>First, solve the problem. Then, write the code. 
								      -- John Johnson</pre>
	    ''']

def not_found(environ, start_response):
    """Called if no URL matches."""
    start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
    return ['Not Found']

def logs_main(environ, start_response):
    """Called if no URL matches."""
    start_response('200 OK', [('Content-Type', 'text/plain')])
    file_name = "/var/log/upstart/api-listener.log"
    with open(file_name) as f:
	data = f.readlines()
    return data


def spotify2youtube_main(environ, start_response):
    """ Like the example above, but it uses the name specified in the URL.
    """
    # get the name from the url if it was specified there.
    args = environ['myapp.url_args']
    # Parge the GET params
    data = parse_qs(environ["QUERY_STRING"])
    #print environ

    if args:
        path_param = escape(args[0])
    else:
        path_param = None

    song = data.get("song", "")[0]
    start_response('200 OK', [('Content-Type', 'text/html')])
    response = spotify2youtube(song)
    return [song]


# map urls to functions
urls = [
    (r'^$', index),
    (r'logs/?$', logs_main),
    (r'logs/(.+)?$', logs_main),
    (r'spotify2youtube/?$', spotify2youtube_main),
    (r'spotify2youtube/(.+)$', spotify2youtube_main)
]


def application(environ, start_response):
    """
    The main WSGI application. Dispatch the current request to
    the functions from above and store the regular expression
    captures in the WSGI environment as  `myapp.url_args` so that
    the functions from above can access the url placeholders.

    If nothing matches call the `not_found` function.
    """
    path = environ.get('PATH_INFO', '').lstrip('/')
    for regex, callback in urls:
        match = re.search(regex, path)
        if match is not None:
            environ['myapp.url_args'] = match.groups()
            return callback(environ, start_response)
    return not_found(environ, start_response)

if __name__=="__main__":
    spotify2youtube("Eraser - Ed Sheeran")
