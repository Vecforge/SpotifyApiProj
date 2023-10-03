import spotipy 
import time
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'
app.secret_key = 'Your Spotify secret key'
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('liked_songs', external = True))

@app.route('/likedSongs')
def liked_songs():
    try:
        token_info = get_token()
    except:
        print("User not logged in!")
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']
    test_id = None

    current_playlists = sp.current_user_playlists()['items']
    for playlist in current_playlists:
        if(playlist['name'] == "Liked"):
            liked_songs_id = playlist['id']
        if(playlist['name'] == "Test"): #test is  playlist
            test_id = playlist['id'] 
    
    if not liked_songs_id:
        return 'Liked songs not found'
    if not test_id:
        new_playlist = sp.user_playlist_create(user_id, 'Test', True)
        test_id = new_playlist['id']

    liked_songs_playlist = sp.playlist_items(liked_songs_id)
    song_uris = []
    for song in liked_songs_playlist['items']:
        song_uri = song['track']['uri']
        song_uris.append(song_uri)
    sp.user_playlist_add_tracks(user_id, test_id, song_uris, None)
    return ("SUCCESS!!!")

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external = False))

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = "99fe8762b7364540a115db49e80b3567", 
        client_secret = "1ae0f5d89bd24f76a525005276824698",
        redirect_uri = url_for('redirect_page', _external= True),
        scope = 'user-library-read playlist-modify-public playlist-modify-private')

app.run(debug = True)