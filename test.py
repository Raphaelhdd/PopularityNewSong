from pymongo import MongoClient
from scrape_spotify import *

cluster = "mongodb+srv://milestone:RaphaelOryaDaniel2024@cluster0.avecywb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def load_database():
    try:
        client = MongoClient(cluster)
        milestone = client.MileStone
        return milestone
    except:
        return []


def update_playlists_globally(milestone, token_spotify):
    category_ids = milestone.category_ids.distinct('id')
    if category_ids is not None:
        for category_id in category_ids:
            playlist_ids = get_playlists_for_category(token_spotify, category_id, limit=50)
            if playlist_ids:
                for playlist in playlist_ids:
                    existing_playlist = milestone.playlists_ids.find_one({"id": playlist['id']})
                    if existing_playlist:
                        if existing_playlist['name'] != playlist['name']:
                            milestone.playlists_ids.update_one(
                                {"id": playlist['id']},
                                {"$set": {"name": playlist['name']}}
                            )
                    else:
                        milestone.playlists_ids.insert_one({"id": playlist['id'], "name": playlist['name']})
        print(f"Updated playlists globally")



def update_categories_ids_globally(category_ids_collection, token_spotify, country):
    categories = get_categories(token_spotify, country=country, limit=50)
    if categories is not None:
        for category in categories:
            existing_category = category_ids_collection.find_one({"id": category['id']})
            if existing_category:
                if existing_category['name'] != category['name']:
                    category_ids_collection.update_one(
                        {"id": category['id']},
                        {"$set": {"name": category['name']}}
                    )
            else:
                category_ids_collection.insert_one({"id": category['id'], "name": category['name']})
        print(f"Updated categories globally")

def update_tracks_and_artists_in_db(tracks_db,artists_db, token_spotify, tracks):
    for track in tracks:
        track_id = track['track_id']
        artist_id = track['artist_id']
        existing_track = tracks_db.find_one({"track_id": track_id})
        if not existing_track:
            track_info = get_track_info_and_audio_features(token_spotify, track_id)
            if track_info != None:
                tracks_db.insert_one(track_info)
                # print(f"Inserted new track: {track_id}")
        existing_artist = artists_db.find_one({"artist_id": artist_id})
        if not existing_artist:
            artist_info = get_artist_info(token_spotify, artist_id)
            if artist_info != None:
                artists_db.insert_one(artist_info)
                # print(f"Inserted new artist: {artist_id}")


if __name__ == '__main__':
    milestone = load_database()
    token_spotify = get_token_spotify(client_id, client_secret)
    countries = milestone.countries.distinct('countries')

    for country in countries:
        # update_categories_ids_globally(milestone.category_ids, token_spotify, country)
        # update_playlists_globally(milestone, token_spotify)
        playlist_ids = get_all_playlist_ids(milestone.playlists_ids)
        for playlist_id in playlist_ids:
            if not milestone.playlist_id_seen.find_one({"playlist_id": playlist_id}):
                try:
                    playlist_details = get_playlist_details(token_spotify, playlist_id)
                    if playlist_details:
                        tracks = extract_tracks_from_playlist(playlist_details)
                        if tracks:
                            update_tracks_and_artists_in_db(milestone.tracks, milestone.artists, token_spotify, tracks)
                    milestone.playlist_id_seen.insert_one({"playlist_id": playlist_id})
                except Exception as e:
                    print(f"Error processing playlist ID {playlist_id}: {str(e)}")
                    continue

    print("Global updates completed successfully.")
