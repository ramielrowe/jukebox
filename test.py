import os
import pprint

import spotipy
import spotipy.util as util

SCOPES = [
    'user-read-playback-state',
    'user-modify-playback-state',
    'playlist-modify-public',
]
SCOPE_STR = ' '.join(SCOPES)

USERNAME = os.environ.get('JUKEBOX_USERNAME')
DEVICE = os.environ.get('JUKEBOX_DEVICE')
PLAYLIST = os.environ.get('JUKEBOX_PLAYLIST')

token = util.prompt_for_user_token(USERNAME, SCOPE_STR)

if token:
    sp = spotipy.Spotify(auth=token)
    pprint.pprint(sp.current_playback()['context'])
