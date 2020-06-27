import json

FEATURE_SET = set([
  'acousticness',
  'danceability',
  'duration_ms',
  'energy',
  'instrumentalness',
  'liveness',
  'loudness',
  'tempo',
  'popularity',
  'valence'
])


def generate_per_feature_metrics():
  playlist_data = get_latest_data('playlist')
  
  # Figure out how to get min/max feature for each feature
  start_key = next(iter(playlist_data['track_breakdown']))
  default_track = playlist_data['track_breakdown'].get(start_key)

  feature_map = dict.fromkeys(FEATURE_SET)
  for k,v in feature_map.items():
    feature_map[k] = {
    'min': default_track,
    'max': default_track,
    'sum': 0,
    'avg': 0
  }

  # find the min,max,avg for each feature
  for k,v in playlist_data['track_breakdown'].items():
    for feature_key, feature_val in feature_map.items():
      if feature_key == 'popularity':
        curr_feature = v[feature_key]
        if curr_feature < feature_map[feature_key]['min'][feature_key]:
          feature_map[feature_key]['min'] = v
        if curr_feature > feature_map[feature_key]['max'][feature_key]:
          feature_map[feature_key]['max'] = v
        feature_map[feature_key]['sum'] += curr_feature
      else:
        curr_feature = v['features'][feature_key]
        if curr_feature < feature_map[feature_key]['min']['features'][feature_key]:
          feature_map[feature_key]['min'] = v
        if curr_feature > feature_map[feature_key]['max']['features'][feature_key]:
          feature_map[feature_key]['max'] = v
        feature_map[feature_key]['sum'] += curr_feature
        
  for k,v in feature_map.items():
    feature_map[k]['avg'] = round(feature_map[k]['sum'] / len(playlist_data['track_breakdown'].keys()), 2)

  with open('./src/app/offline_data/metrics.json', 'w+', encoding='utf-8') as f:
    json.dump(feature_map, f, ensure_ascii=False, indent=4)


def get_latest_data(file_name):
  try:
    with open(f'./src/app/offline_data/{file_name}.json') as f:
      return json.load(f)
  except Exception:
    return None
