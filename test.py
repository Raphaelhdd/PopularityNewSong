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
        playlist_ids = get_playlists_for_category(token_spotify, category_id, limit=10)
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


if __name__ == '__main__':
    milestone, applemusic, spotify = load_database()
    token_spotify = get_token_spotify(client_id, client_secret)
    countries = spotify.distinct('countries')
    for country in countries:
        update_countries_categories_ids(spotify, token_spotify,country)
        update_playlists_for_categories(spotify,token_spotify,country)

