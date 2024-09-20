import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collect_data import load_database
from scipy.stats import pearsonr
from sklearn.preprocessing import MinMaxScaler
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
    tracks_df['duration_s'] = tracks_df['duration_ms'] / 1000

    # Filter the relevant range
    filtered_df = tracks_df[(tracks_df['duration_s'] >= 0) & (tracks_df['duration_s'] <= 800)]

    # Normalize the duration
    scaler = MinMaxScaler()
    filtered_df['duration_s_scaled'] = scaler.fit_transform(filtered_df[['duration_s']])

    # Create duration bins
    duration_bins = pd.cut(filtered_df['duration_s_scaled'], bins=20)  # 20 bins for normalized duration

    # Calculate average popularity for each bin
    avg_popularity_by_bin = filtered_df.groupby(duration_bins)['popularity'].mean().reset_index()

    # Plotting
    plt.figure(figsize=(12, 6))
    sns.lineplot(x=avg_popularity_by_bin['duration_s_scaled'].apply(lambda x: x.mid), y=avg_popularity_by_bin['popularity'])
    plt.title('Average Song Popularity by Normalized Duration Range')
    plt.xlabel('Normalized Duration Range (0 to 1)')
    plt.ylabel('Average Popularity Index')
    plt.grid(True)
    plt.savefig('avg_popularity_by_normalized_duration_range.png')
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
    for feature in audio_features:
        plt.figure(figsize=(8, 6))

        # Create bins for the feature
        if feature == 'tempo':
            bins = pd.cut(tracks_df[feature], bins=range(0, 250, 10))
        else:
            bins = pd.cut(tracks_df[feature], bins=20)  # 20 bins for features between 0 and 1

        # Calculate the average popularity for each bin
        avg_popularity_by_bin = tracks_df.groupby(bins)['popularity'].mean().reset_index()

        # Plotting
        sns.lineplot(x=avg_popularity_by_bin[feature].apply(lambda x: x.mid), y=avg_popularity_by_bin['popularity'])

        plt.title(f'{feature.capitalize()} vs Average Popularity')
        plt.xlabel(feature.capitalize())
        plt.ylabel('Average Popularity Index')

        # Save each plot as a separate image file
        plt.savefig(f'{feature}_vs_avg_popularity.png')
        plt.show()

def plot_popularity_by_album_type(tracks_df, artist_df, top_n_genres=10):
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

    plt.figure(figsize=(14, 10))
    sns.barplot(x='album_type', y='popularity', hue='genre', data=popularity_by_album_genre, palette='Set3')
    plt.title('Average Song Popularity by Album Type and Genre')
    plt.xlabel('Album Type')
    plt.ylabel('Average Popularity Index')
    plt.xticks(rotation=45)
    plt.legend(title='Genre', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('popularity_by_album_type_and_genre.png')
    plt.show()

    # Print the number of distinct genres being displayed
    displayed_genres = len(top_genres_set) + 1  # Including 'Other'
    print(f"Number of distinct genres being displayed: {displayed_genres}")

    # Calculate and print the average popularity for each album type
    avg_popularity_by_album_type = popularity_by_album_genre.groupby('album_type')['popularity'].mean()
    print("\nAverage Popularity by Album Type:")
    print(avg_popularity_by_album_type)



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


def plot_genre_popularity_over_time(tracks_df, artist_df, genres_to_plot):
    """
    Plots the average song popularity over time for specified genres.
    Args:
    - tracks_df (pd.DataFrame): DataFrame containing track data with 'album', 'artists', 'popularity', and 'release_date' columns.
    - artist_df (pd.DataFrame): DataFrame containing artist data with 'id', 'genres' columns.
    - genres_to_plot (list): List of genres to plot.
    Returns:
    - None
    """
    # Map artist IDs to their genres
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

    # Filter tracks by genres of interest
    def filter_genres(genres):
        return [genre for genre in genres if genre in genres_to_plot]

    tracks_df['filtered_genres'] = tracks_df['artist_genres'].apply(filter_genres)
    tracks_filtered = tracks_df[
        tracks_df['filtered_genres'].apply(len) > 0].copy()  # Create a copy to avoid SettingWithCopyWarning

    # Convert release date to datetime
    tracks_filtered.loc[:, 'release_date'] = pd.to_datetime(tracks_filtered['album'].apply(lambda x: x['release_date']))
    tracks_filtered.loc[:, 'year'] = tracks_filtered['release_date'].dt.year

    # Explode genres to have one row per genre
    tracks_exploded = tracks_filtered.explode('filtered_genres')

    # Group by year and genre to calculate average popularity
    popularity_over_time = tracks_exploded.groupby(['year', 'filtered_genres'])['popularity'].mean().reset_index()

    # Plotting
    plt.figure(figsize=(12, 8))
    sns.lineplot(x='year', y='popularity', hue='filtered_genres', data=popularity_over_time, marker='o')
    plt.title('Average Song Popularity Over Time by Genre')
    plt.xlabel('Year')
    plt.ylabel('Average Popularity Index')
    plt.legend(title='Genre')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('genre_popularity_over_time.png')
    plt.show()



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
    plot_duration_vs_popularity(tracks_df)
    # plot_audio_features_vs_popularity(tracks_df)
    # plot_popularity_by_album_type(tracks_df, artist_df)
    # plot_popularity_over_time(tracks_df)
    #
    # genres_to_plot = ['pop', 'rock', 'rap', 'r&b']
    # plot_genre_popularity_over_time(tracks_df, artist_df, genres_to_plot)
