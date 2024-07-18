import base64
import time

import requests
import json
# Milestone
client_id = 'bbf867f24ccc4a659958c0143a01fe2d'
client_secret = 'e0c45a79155b4c4f96c3c949857d6ec1'


#Raph huji
# client_id = '8a8016324af74789b439da9f7203a463'
# client_secret = '7164149f6adc4e8e9b68b719228785ec'

# Raph 2
# client_id = "af47d6abadc24951be9d427ce7674fff"
# client_secret = "a6ad80c487004559a1d1ef4c73712a10"

# Raph 3
# client_id = '9bbb858b7f274d7bac53ca44b0288f86'
# client_secret = 'b7a52c2a83004efc80cd78fd38efa051'

# raph 4
# client_id = '984d68df30b74765a9391dc75da0dd77'
# client_secret = 'afb1170f0ea444bd970aa76625246310'

# raph 5
# client_id = '37c700485f504ca49cdb7ecc15f259f5'
# client_secret = '1d331b53a20649f1b85dedf3b1ac2d8e'

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


def get_track_info(token, track_id):
    """
    This function takes the access token and a track ID, retrieves information
    about the track from Spotify, and returns the track info as a JSON object.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("404")
            return None
        elif response.status_code != 200:
            print("STOP TRACK INFO")
            time.sleep(5000)
            return None
        track_info = response.json()
        return track_info
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def get_audio_features(token, track_id):
    """
    This function takes the access token and a track ID, retrieves the audio
    features of the track from Spotify, and returns the features as a JSON object.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("404")
            return {"audio":"No information"}
        elif response.status_code != 200:
            print("STOP AUDIO FEATURE")
            time.sleep(5000)
            return None
        audio_features = response.json()
        return audio_features
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def get_artist_info(token, artist_id):
    """
    This function takes the access token and an artist ID, retrieves information
    about the artist from Spotify, and returns the artist info as a JSON object.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("404")
            return None
        elif response.status_code != 200:
            print("STOP ARTIST INFO")
            time.sleep(5000)
            return None
        artist_info = response.json()
        return artist_info
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def get_categories(token, country='US', limit=50):
    """
    This function takes the access token and country code, retrieves the playlist categories,
    and returns a list of dictionaries with category IDs and names.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/browse/categories?country={country}&limit={limit}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("404")
            return None
        elif response.status_code != 200:
            print("STOP CATEGORIES")
            time.sleep(5000)
            return None
        categories = response.json()
        category_list = [{'id': category['id'], 'name': category['name']} for category in categories['categories']['items']]
        return category_list
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def get_playlists_for_category(token, category_id, limit=50):
    """
    This function takes the access token, category ID, and limit, retrieves
    playlists for the specified category, and returns a list of playlist IDs.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists?limit={limit}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("404")
            return None
        elif response.status_code != 200:
            print("STOP PLAYLIST")
            time.sleep(5000)
            return None
        playlists = response.json()
        playlist_ids = [{'id': playlist['id'], 'name': playlist['name']} for playlist in playlists['playlists']['items']]
        return playlist_ids
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


def get_all_playlist_ids(playlists_collection):
    """
    This function retrieves all playlist IDs from the playlists_collection
    and returns them as a list.
    """
    playlists = playlists_collection.find({}, {'id': 1, '_id': 0})
    playlist_ids = [playlist['id'] for playlist in playlists]
    return playlist_ids


def get_playlist_details(token, playlist_id):
    """
    This function takes the access token and a playlist ID, retrieves detailed information
    about the playlist from Spotify, and returns the playlist details.
    """
    headers = get_auth_headers(token)
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 404:
            print("404")
            return None
        elif response.status_code != 200:
            print("STOP PLAYLIST DETAIL")
            time.sleep(5000)
            return None
        playlist_details = response.json()
        return playlist_details
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


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
    if track_info != None:
        audio_features = get_audio_features(token, track_id)
        if audio_features != None:
            return {**track_info, **audio_features}
    return None




