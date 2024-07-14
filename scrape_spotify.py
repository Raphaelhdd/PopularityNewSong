import base64
import time

import requests
import json
# Milestone
# client_id = 'f6ef862497644b69a7c3fd7c02917ffb'
# client_secret = 'c57a91b370cb4b03a606a57cd1c057eb'


#Raph huji
client_id = '8a8016324af74789b439da9f7203a463'
client_secret = '7164149f6adc4e8e9b68b719228785ec'
def get_token_spotify(client_id, client_secret):
    """
    This function takes the client_id and client_secret, encodes them in base64,
    and requests an access token from Spotify.
    """
    auth_string = f"{client_id}:{client_secret}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        "Authorization": "Basic " + auth_base64,  # Note the space after "Basic"
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    # Make POST request to get the access token
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        json_result = response.json()
        token = json_result['access_token']
        return token
    else:
        print(f"Error requesting access token: {response.status_code}, {response.text}")
        return None


def get_auth_headers(token):
    """
    This function takes the access token and returns the headers required for
    authenticated requests to the Spotify API.
    """
    return {"Authorization": "Bearer " + token}


def search_for_an_artist(token, artist_name):
    """
    This function takes the access token and an artist's name, searches for the
    artist on Spotify, and prints the result.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    response = requests.get(url, headers=headers)
    json_result = json.loads(response.content)
    if 'artists' in json_result and 'items' in json_result['artists'] and len(json_result['artists']['items']) > 0:
        artist = json_result['artists']['items'][0]
        artist_info = {
            'name': artist['name'],
            'id': artist['id'],
            'followers': artist['followers']['total'],
            'popularity': artist['popularity'],
            'genres': artist['genres']
        }
        return artist_info
    else:
        print("Artist not found")
        return None


def get_track_info(token, track_id):
    """
    This function takes the access token and a track ID, retrieves information
    about the track from Spotify, and returns the track info as a JSON object.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    response = requests.get(url, headers=headers)
    retry_after = int(response.headers.get('Retry-After',1))
    print(retry_after)
    time.sleep(retry_after)
    try:
        track_info = response.json()
    except:
        return None
    return track_info

def get_audio_features(token, track_id):
    """
    This function takes the access token and a track ID, retrieves the audio
    features of the track from Spotify, and returns the features as a JSON object.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        time.sleep(20)
    audio_features = response.json()
    return audio_features

def get_artist_info(token, artist_id):
    """
    This function takes the access token and an artist ID, retrieves information
    about the artist from Spotify, and returns the artist info as a JSON object.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        time.sleep(20)
    artist_info = response.json()
    return artist_info

def get_multiple_artists_info(token, artist_names):
    """
    This function takes the access token and a list of artist names, retrieves
    information about each artist from Spotify, and returns a list of artist info
    JSON objects.
    """
    artist_infos = []
    for name in artist_names:
        search_result = search_for_an_artist(token, name)
        artist_id = search_result['artists']['items'][0]['id']
        artist_info = get_artist_info(token, artist_id)
        artist_infos.append(artist_info)
    return artist_infos

def get_categories(token, country='US', limit=50):
    """
    This function takes the access token and country code, retrieves the playlist categories,
    and returns a list of category IDs.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/browse/categories?country={country}&limit={limit}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        time.sleep(20)
    else:
        categories = response.json()
        category_ids = [category['id'] for category in categories['categories']['items']]
        return category_ids


def get_playlists_for_category(token, category_id, limit=10):
    """
    This function takes the access token, category ID, and limit, retrieves
    playlists for the specified category, and returns a list of playlist IDs.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists?limit={limit}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        time.sleep(20)
    else:
        playlists = response.json()
        playlist_ids = [playlist['id'] for playlist in playlists['playlists']['items']]
        return playlist_ids


def get_playlist_tracks(token, playlist_id):
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        time.sleep(20)
    else:
        playlist_tracks = response.json()
        return playlist_tracks


def get_artists_from_playlists(token, playlist_ids):
    """
    This function takes the access token and a list of playlist IDs, retrieves the tracks in the playlists,
    and returns a list of unique artist names.
    """
    artist_names = set()
    for playlist_id in playlist_ids:
        playlist_tracks = get_playlist_tracks(token, playlist_id)
        for item in playlist_tracks['items']:
            track = item['track']
            if track != None:
                for artist in track['artists']:
                    artist_names.add(artist['name'])
    return list(artist_names)




def analyze_artist_popularity(artists_info):
    sorted_artists = sorted(artists_info, key=lambda x: x['popularity'], reverse=True)
    return sorted_artists



def get_playlist_details(token, playlist_id):
    """
    This function takes the access token and a playlist ID, retrieves detailed information
    about the playlist from Spotify, and returns the playlist details.
    """
    print(playlist_id)
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        time.sleep(20)
    else:
        playlist_details = response.json()
        return playlist_details

def extract_tracks_from_playlist(playlist_details):
    tracks = []
    for item in playlist_details['tracks']['items']:
        track = item['track']
        if track:
            tracks.append({
                'track_id': track['id'],
                'track_name': track['name'],
                'artist_id': track['artists'][0]['id'],
                'artist_name': track['artists'][0]['name'],
                'album_id': track['album']['id'],
                'album_name': track['album']['name'],
                'popularity': track['popularity']
            })
    return tracks


def get_track_info_and_audio_features(token, track_id):
    track_info = get_track_info(token, track_id)
    audio_features = get_audio_features(token, track_id)
    return {**track_info, **audio_features}
# token = get_token_spotify(client_id, client_secret)
# category_ids = get_categories(token, country='IL', limit=50)
# all_playlist_ids = []
# for category_id in category_ids:
#     playlist_ids = get_playlists_for_category(token, category_id, limit=10)
#     all_playlist_ids.extend(playlist_ids)
#
# artist_names = get_artists_from_playlists(token, all_playlist_ids)
# artists_info = get_multiple_artists_info(token, artist_names)
# sorted_artists = analyze_artist_popularity(artists_info)
#
# for artist in sorted_artists:
#     print(f"Artist: {artist['name']}, ID: {artist['id']}, Followers: {artist['followers']}, Popularity: {artist['popularity']}, Genres: {artist['genres']}")
