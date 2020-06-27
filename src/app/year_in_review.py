# Descriptions for the Features?
# Mobile friendly

import requests
import json
import base64


SPOTIFY_CLIENT_ID = '01618aba78f146599240d0625c6956d0'
SPOTIFY_CLIENT_SECRET = 'd79f9af180e54d939771540d888aa58f'

PLAYLIST_ID = '720360kMd4LiSAVzyA8Ft4'

BASE_REQUEST_URI = 'https://api.spotify.com/v1/'
BASE_AUTHZ_URI = 'https://accounts.spotify.com/api/token'


def get_spotify_auth_token():
  resp = requests.post(
    BASE_AUTHZ_URI,
    headers={
      'Authorization': 'Basic %s' % base64.b64encode((CLIENT_ID + ':' + CLIENT_SECRET).encode('utf-8')).decode('utf-8')
    },
    data={
      'grant_type': 'client_credentials'
    })
  if resp.status_code != 200:
    return None
  return resp.json()['access_token']

# fetch data from Spotify API and build the playlist json data structure
def playlist_info(token):
  overview_data = _get_playlist_overview(token)

  playlist_tracks_data = _get_playlist_tracks(token)
  track_dict = _build_track_dict(playlist_tracks_data)
  track_features = _get_track_features(
    list(track_dict.keys()),
    token
  )
  for each in track_features:
    id = each['id']
    track_dict[id]['features'] = each
  overview_dict = {}
  overview_dict = {k: v for k, v in overview_data.items()}
  overview_dict['playlist_count'] = len(track_dict.keys())
  overview_dict['track_breakdown'] = track_dict

  with open('./src/app/offline_data/playlist.json', 'w+', encoding='utf-8') as f:
    json.dump(overview_dict, f, ensure_ascii=False, indent=4)
  return overview_dict


# get metadata about the playlist
def _get_playlist_overview(token):
  overview_params = 'name,description,followers,owner(display_name),external_urls(spotify)'

  resp = requests.get(
    BASE_REQUEST_URI + f'playlists/{PLAYLIST_ID}',
    headers={
      'Authorization': f'Bearer {token}'
    },
    params={
      'fields': overview_params
    }
  )
  if resp.status_code != 200:
    return 'error fetching playlist overview'
  return resp.json()


# get paginated data for all tracks
def _get_playlist_tracks(token):
  album_params = 'album(name,release_date,images,album_type)'
  artist_params = 'artists(name)'
  track_params = 'limit,next,offset,total,href,items(added_at,' \
  'track(%s,%s,name,release_date,duration_ms,explicit,external_urls,popularity,id))' % (album_params, artist_params)

  track_list = []
  resp = requests.get(
    BASE_REQUEST_URI + f'playlists/{PLAYLIST_ID}/tracks',
    headers={
      'Authorization': f'Bearer {token}'
    },
    params={
      'fields': track_params
    }
  )

  if resp.status_code == 200:
    track_dict = resp.json()
    track_list.extend(track_dict['items'])
    while track_dict['next']:
      resp = requests.get(
        track_dict['next'],
        headers={
          'Authorization': f'Bearer {token}'
        },
        params={
          'fields': track_params
        }
      )
      if resp.status_code == 200:
        track_dict = resp.json()
        track_list.extend(track_dict['items'])

  return track_list

# get feature info for list of tracks
def _get_track_features(song_ids, token):

  pagination_list = [song_ids[i:i+100] for i in range(0,len(song_ids), 100)]
  feature_list = []
  for songs in pagination_list:
    song_string = ','.join(songs)

    resp = requests.get(
      BASE_REQUEST_URI + 'audio-features',
      headers={
        'Authorization': 'Bearer %s' % token
      },
      params={
        'ids': song_string
      }
    )
    feature_list.extend(resp.json()['audio_features'])
  
  return feature_list
  #
  # Example response
  # {
  # "audio_features": [
  #   {
  #     "acousticness": 0.135, 
  #     "analysis_url": "https://api.spotify.com/v1/audio-analysis/1PR1JQmuOmI3eD4isHeLlI", 
  #     "danceability": 0.722, 
  #     "duration_ms": 158276, 
  #     "energy": 0.574, 
  #     "id": "1PR1JQmuOmI3eD4isHeLlI", 
  #     "instrumentalness": 0.000865, 
  #     "key": 10, 
  #     "liveness": 0.163, 
  #     "loudness": -5.72, 
  #     "mode": 0, 
  #     "speechiness": 0.179, 
  #     "tempo": 104.983, 
  #     "time_signature": 4, 
  #     "track_href": "https://api.spotify.com/v1/tracks/1PR1JQmuOmI3eD4isHeLlI", 
  #     "type": "audio_features", 
  #     "uri": "spotify:track:1PR1JQmuOmI3eD4isHeLlI", 
  #     "valence": 0.337
  #   }, 
  # }


def _build_track_dict(playlist_arr):
  track_dict = {}
  for track in playlist_arr:
    id = track['track']['id']
    track_dict[id] = track['track']
  return track_dict
