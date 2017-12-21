import os

import flask
import spotipy
import spotipy.util as util

APP = flask.Flask(__name__)

SCOPES = [
    'user-read-playback-state',
    'user-modify-playback-state',
    'playlist-modify-public',
]
SCOPE_STR = ' '.join(SCOPES)

CACHE_PATH = os.environ.get('SPOTIPY_CACHE_PATH')

USERNAME = os.environ.get('JUKEBOX_USERNAME')
DEVICE = os.environ.get('JUKEBOX_DEVICE')
PLAYLIST = os.environ.get('JUKEBOX_PLAYLIST')

print USERNAME
print DEVICE
print PLAYLIST

if CACHE_PATH:
    TOKEN = util.prompt_for_user_token(USERNAME, SCOPE_STR,
                                       cache_path=CACHE_PATH)
else:
    TOKEN = util.prompt_for_user_token(USERNAME, SCOPE_STR)

SP = spotipy.Spotify(auth=TOKEN)


@APP.route('/jukebox', methods=['GET'])
def jukebox():
    sp_tracks = SP.user_playlist_tracks(SP.current_user()['id'],
                                        playlist_id=PLAYLIST)['items']
    tracks = [{'artist': t['track']['artists'][0]['name'],
               'name': t['track']['name'],
               'id': t['track']['id']}
              for t in sp_tracks]
    return flask.render_template('jukebox.html',
                                 tracks=tracks)


@APP.route('/jukebox/search', methods=['GET'])
def search():
    q = flask.request.args['q']

    sp_tracks = SP.search(q, type='track')['tracks']['items']
    tracks = [{'artist': t['artists'][0]['name'],
               'name': t['name'],
               'id': t['id']}
              for t in sp_tracks]

    return flask.render_template('search.html',
                                 tracks=tracks,
                                 q=q)


@APP.route('/jukebox/enqueue', methods=['POST'])
def enqueue():
    track_id = flask.request.form['track_id']
    location = flask.request.form['location']

    if location == 'next':
        sp_tracks = SP.user_playlist_tracks(SP.current_user()['id'],
                                            playlist_id=PLAYLIST)['items']
        current_track_id = SP.current_playback()['item']['id']
        cur_index = 0
        for track in sp_tracks:
            if track['track']['id'] == current_track_id:
                break
            cur_index += 1
        SP.user_playlist_add_tracks(SP.current_user()['id'],
                                    PLAYLIST, [track_id, ], cur_index + 1)
    else:
        SP.user_playlist_add_tracks(SP.current_user()['id'],
                                    PLAYLIST, [track_id, ])
    return flask.redirect('/jukebox')


@APP.route('/jukebox/remove', methods=['POST'])
def remove():
    track_id = flask.request.form['track_id']
    SP.user_playlist_remove_all_occurrences_of_tracks(
        SP.current_user()['id'], PLAYLIST, [track_id])
    return flask.redirect('/jukebox')


if __name__ == '__main__':
    APP.run(host='127.0.0.1', port=8080, debug=True)
