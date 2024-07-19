import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collect_data import load_database


def plot_correlation_heatmap(tracks_df):
    """
    Generates a correlation heatmap for numeric features of tracks DataFrame.
    Args:
    - tracks_df (pd.DataFrame): DataFrame containing track data with numeric columns.
    Returns:
    - None
    """
    numeric_cols = ['popularity', 'duration_ms', 'danceability', 'energy', 'loudness', 'valence', 'tempo']
    numeric_df = tracks_df[numeric_cols]
    corr_matrix = numeric_df.corr()
    plt.figure(figsize=(12, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
    plt.title('Correlation Between Song Features')
    plt.savefig('correlation_heatmap.png')
    plt.show()


def plot_popularity_distribution(tracks_df):
    """
    Plots the distribution of song popularity indices.
    Args:
    - tracks_df (pd.DataFrame): DataFrame containing track data with 'popularity' column.
    - save_fig (bool, optional): Whether to save the plot as an image file. Default is False.
    Returns:
    - None
    """
    plt.figure(figsize=(12, 6))
    sns.histplot(tracks_df['popularity'], bins=20, kde=True)
    plt.title('Distribution of Song Popularity')
    plt.xlabel('Popularity Index')
    plt.ylabel('Number of Songs')
    plt.savefig('popularity_distribution.png')
    plt.show()


def plot_popularity_by_genre_count(artist_df):
    """
    Plots the average artist popularity based on the number of genres they are associated with.
    Args:
    - artist_df (pd.DataFrame): DataFrame containing artist data with 'genres' and 'popularity' columns.
    Returns:
    - None
    """
    artist_df['genre_count'] = artist_df['genres'].apply(len)
    popularity_by_count = artist_df.groupby('genre_count')['popularity'].mean().reset_index()
    plt.figure(figsize=(12, 6))
    sns.barplot(x='genre_count', y='popularity', data=popularity_by_count, palette='viridis')
    plt.title('Average Artist Popularity by Number of Genres')
    plt.xlabel('Number of Genres')
    plt.ylabel('Average Popularity Index')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True)
    plt.savefig('popularity_by_genre_count.png', bbox_inches='tight')
    plt.show()


def plot_duration_vs_popularity(tracks_df):
    """
    Plots the relationship between song duration and popularity.
    Args:
    - tracks_df (pd.DataFrame): DataFrame containing track data with 'duration_ms' and 'popularity' columns.
    Returns:
    - None
    """
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='duration_ms', y='popularity', data=tracks_df)
    plt.title('Relationship Between Song Duration and Popularity')
    plt.xlabel('Duration (ms)')
    plt.ylabel('Popularity Index')
    plt.savefig('duration_vs_popularity.png')
    plt.show()


def plot_audio_features_vs_popularity(tracks_df):
    """
    Plots scatter plots of various audio features against song popularity.
    Args:
    - tracks_df (pd.DataFrame): DataFrame containing track data with audio feature columns and 'popularity'.
    Returns:
    - None
    """
    audio_features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                      'valence', 'tempo']
    plt.figure(figsize=(14, 8))

    for i, feature in enumerate(audio_features):
        plt.subplot(3, 3, i + 1)
        sns.kdeplot(
            data=tracks_df, x=feature, y='popularity',
            fill=True, cmap="viridis", thresh=0, levels=100
        )
        plt.title(f'{feature.capitalize()} vs Popularity')
        plt.xlabel(feature.capitalize())
        plt.ylabel('Popularity Index')

    plt.tight_layout()
    plt.savefig('audio_features_vs_popularity_heatmap.png')
    plt.show()


def plot_popularity_by_album_type(tracks_df, artist_df, top_n_genres=20):
    """
    Plots the average song popularity by album type and genre based on artist associations.
    Args:
    - tracks_df (pd.DataFrame): DataFrame containing track data with 'album' and 'artists' columns.
    - artist_df (pd.DataFrame): DataFrame containing artist data with 'id', 'genres', and 'popularity' columns.
    - top_n_genres (int): Number of top genres to display in the plot. Others will be grouped into 'Other'.
    Returns:
    - None
    """
    artist_genres = {}
    for index, row in artist_df.iterrows():
        artist_genres[row['id']] = row['genres']

    def get_artist_genres(artist_ids):
        genres = set()
        for artist_id in artist_ids:
            if artist_id in artist_genres:
                genres.update(artist_genres[artist_id])
        return list(genres)

    tracks_df['artist_genres'] = tracks_df['artists'].apply(
        lambda artists: get_artist_genres([artist['id'] for artist in artists])
    )
    tracks_df['album_type'] = tracks_df['album'].apply(lambda x: x['album_type'] if 'album_type' in x else None)
    tracks_filtered = tracks_df.dropna(subset=['album_type', 'artist_genres'])

    genre_counts = {}
    for genres in tracks_filtered['artist_genres']:
        for genre in genres:
            if genre in genre_counts:
                genre_counts[genre] += 1
            else:
                genre_counts[genre] = 1

    top_genres = sorted(genre_counts.items(), key=lambda item: item[1], reverse=True)[:top_n_genres]
    top_genres_set = set([genre for genre, count in top_genres])

    def categorize_genre(genres):
        return [genre if genre in top_genres_set else 'Other' for genre in genres]

    tracks_filtered['categorized_genres'] = tracks_filtered['artist_genres'].apply(categorize_genre)

    popularity_by_album_genre = pd.DataFrame(columns=['album_type', 'genre', 'popularity'])
    for idx, row in tracks_filtered.iterrows():
        for genre in row['categorized_genres']:
            popularity_by_album_genre = pd.concat([popularity_by_album_genre, pd.DataFrame({
                'album_type': [row['album_type']],
                'genre': [genre],
                'popularity': [row['popularity']]
            })], ignore_index=True)

    popularity_by_album_genre = popularity_by_album_genre.groupby(['album_type', 'genre'])[
        'popularity'].mean().reset_index()

    plt.figure(figsize=(12, 8))
    sns.barplot(x='album_type', y='popularity', hue='genre', data=popularity_by_album_genre, palette='Set3')
    plt.title('Average Song Popularity by Album Type and Genre')
    plt.xlabel('Album Type')
    plt.ylabel('Average Popularity Index')
    plt.xticks(rotation=45)
    plt.legend(title='Genre', loc='upper right')
    plt.savefig('popularity_by_album_type_and_genre.png')
    plt.show()

    # Print the number of distinct genres being displayed
    displayed_genres = len(top_genres_set) + 1  # Including 'Other'
    print(f"Number of distinct genres being displayed: {displayed_genres}")



def plot_popularity_over_time(tracks_df):
    """
    Plots the average song popularity over time based on release years.
    Args:
    - tracks_df (pd.DataFrame): DataFrame containing track data with 'album' and 'release_date' columns.
    Returns:
    - None
    """
    tracks_with_album = tracks_df[tracks_df['album'].apply(lambda x: len(x) > 0)]
    tracks_with_album['release_year'] = pd.to_datetime(tracks_with_album['album'].apply(lambda x: x['release_date'])).dt.year
    popularity_over_time = tracks_with_album.groupby('release_year')['popularity'].mean().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='release_year', y='popularity', data=popularity_over_time)
    plt.title('Evolution of Average Song Popularity Over Time')
    plt.xlabel('Release Year')
    plt.ylabel('Average Popularity Index')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('popularity_over_ime.png')
    plt.show()
def find_documents_with_error_field(collection_name):
        cursor = collection_name.find({'audio': {'$exists': True}})
        print(len(cursor))
        # Print each document's _id that has the 'error' field
        # for document in cursor:
        #     print(f"Document _id with 'error' field: {document['id']}")


if __name__ == '__main__':
    milestone = load_database()
    # find_documents_with_error_field(milestone.tracks)

    print(milestone)
    print(milestone.list_collection_names())
    tracks_collection = milestone.tracks
    artists_collection = milestone.artists
    tracks_data = list(tracks_collection.find({}))
    tracks_df = pd.DataFrame(tracks_data)
    # Print all columns
    print("Columns in tracks_df:")
    print(tracks_df.columns)
    #
    # Print DataFrame shape
    print("\nShape of tracks_df:")
    print(tracks_df.shape)

    artists_data = list(artists_collection.find({}))
    artist_df = pd.DataFrame(artists_data)
    # Print all columns
    print("Columns in artist_df:")
    print(artist_df.columns)

    # Print DataFrame shape
    print("\nShape of artist_df:")
    print(artist_df.shape)

    required_columns = ['popularity', 'duration_ms', 'artist_id', 'danceability', 'energy', 'speechiness',
                        'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']
    for column in required_columns:
        if column not in tracks_df.columns:
            tracks_df[column] = None
    sns.set(style="whitegrid")
    # plot_correlation_heatmap(tracks_df)
    # plot_popularity_distribution(tracks_df)
    # plot_popularity_by_genre_count(artist_df)
    # plot_duration_vs_popularity(tracks_df)
    # plot_audio_features_vs_popularity(tracks_df)
    plot_popularity_by_album_type(tracks_df, artist_df)
    # plot_popularity_over_time(tracks_df)
    #
