from pymongo import MongoClient
from scrape_spotify import *

cluster = "mongodb+srv://milestone:RaphaelOryaDaniel2024@cluster0.avecywb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def load_database():
    try:
        client = MongoClient(cluster)
        milestone = client.MileStone
        applemusic = milestone.AppleMusic
        spotify = milestone.Spotify
        return milestone, applemusic, spotify
    except:
        return []


def update_playlists_for_categories(spotify, token_spotify, country):
    # Récupère les IDs de catégories pour le pays spécifié
    category_ids = spotify.find_one({}, {'category_ids.' + country: 1})['category_ids'][country]

    playlists = []
    # Pour chaque ID de catégorie, récupère les IDs de playlists
    for category_id in category_ids:
        playlist_ids = get_playlists_for_category(token_spotify, category_id, limit=50)
        if playlist_ids:
            playlists.extend(playlist_ids)

    # Met à jour la base de données MongoDB avec les playlists récupérées
    existing_country = spotify.find_one({"countries": country})
    playlists_dict = {playlist: True for playlist in playlists}

    if existing_country:
        existing_playlists = existing_country.get('playlists', {}).get(country, {})
        for playlist in playlists_dict:
            if playlist not in existing_playlists:
                existing_playlists[playlist] = True

        spotify.update_one(
            {"countries": country},
            {"$set": {f"playlists.{country}": existing_playlists}}
        )
    else:
        spotify.insert_one(
            {"countries": [country], "playlists": {country: playlists_dict}}
        )

    print(f"Updated playlists for country: {country}")


def update_countries_categories_ids(spotify, token_spotify,country):
    category_ids = get_categories(token_spotify, country=country, limit=50)
    new_categories_dict = {cid: True for cid in category_ids}
    existing_country = spotify.find_one({"countries": country})
    if existing_country:
        existing_categories = existing_country.get('category_ids', {}).get(country, {})
        for cid in new_categories_dict:
            if cid not in existing_categories:
                existing_categories[cid] = True
        spotify.update_one(
            {"countries": country},
            {"$set": {f"category_ids.{country}": existing_categories}}
        )
    else:
        spotify.insert_one(
            {"countries": [country], "category_ids": {country: new_categories_dict}}
        )
    print(f"Updated categories for country: {country}")


def update_tracks_and_artists_in_db(spotify, token_spotify, tracks):
    for track in tracks:
        track_id = track['track_id']
        artist_id = track['artist_id']
        existing_track = spotify.find_one({"tracks.track_id": track_id})
        if not existing_track:
            track_info = get_track_info_and_audio_features(token_spotify, track_id)
            spotify.update_one(
                {"tracks.track_id": {"$ne": track_id}},
                {"$push": {"tracks": track_info}},
                upsert=True
            )
        existing_artist = spotify.find_one({"artists.artist_id": artist_id})
        if not existing_artist:
            artist_info = get_artist_info(token_spotify, artist_id)
            spotify.update_one(
                {"artists.artist_id": {"$ne": artist_id}},
                {"$push": {"artists": artist_info}},
                upsert=True
            )

if __name__ == '__main__':
    milestone, applemusic, spotify = load_database()
    token_spotify = get_token_spotify(client_id, client_secret)
    countries = spotify.distinct('countries')
    for country in countries:
        update_countries_categories_ids(spotify, token_spotify,country)
        update_playlists_for_categories(spotify,token_spotify,country)
        playlists = spotify.find_one({"countries": country}, {'playlists.' + country: 1})['playlists'][country]
        for playlist_id in playlists.keys():
            playlist_details = get_playlist_details(token_spotify, playlist_id)
            if playlist_details != None:
                tracks = extract_tracks_from_playlist(playlist_details)
                time.sleep(3)
                if tracks != None:
                    update_tracks_and_artists_in_db(spotify, token_spotify, tracks)
                    time.sleep(4)
            time.sleep(10)
