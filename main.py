import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import json
import logging
from datetime import datetime
import unicodedata
import Levenshtein
import re

# Load environment variables from the .env file
load_dotenv()

# Set up Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID") 
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET") 
SPOTIFY_REDIRECT_URI = os.getenv("REDIRECT_URI") 
SCOPE = 'playlist-modify-public playlist-modify-private'
BATCH_SIZE = 100
LISTS_DIR = "./lists"
LIST_JSON = "test.json" # Replace with your own JSON file
LOG_DIR = './logs'
COUNTRY_PREFIXES_JSON = "country_prefixes.json" # Replace with your own JSON file
HELPER_DIR = './helpers'
# Configuration variable to decide whether to pick the higher popularity or skip on finding duplicate artists
PICK_HIGHER_POPULARITY = True 
# Configuration variable to decide whether to clear playlist before adding new songs
CLEAR_PLAYLIST = True 
# Configuration variable to allow approximate matches with distance of x
USE_LEV = False 
APPROX_MATCHES = 1 
# Configuration vairable to decide whether to pick the artist that is more similar in genre or skip on finding duplicate artists
PICK_GENRE_PROXIMITY = True # Only works with larger playlists, genre sometimes not available for smaller artists

os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging to log to a file
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
timestamp_short = datetime.now().strftime('%Y-%m-%d')
log_file = os.path.join(LOG_DIR, f'artist_search_{timestamp}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()  # Optional: Logs to console as well
    ]
)

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE
))

# Function to check if a playlist already exists
def playlist_exists(user_id, playlist_name):
    playlists = sp.current_user_playlists(limit=50)
    while playlists:
        for playlist in playlists['items']:
            if playlist['name'].lower() == playlist_name.lower():
                return playlist['id']  # Return existing playlist ID
        playlists = sp.next(playlists) if playlists['next'] else None
    return None

# Function to check if an artist's tracks already exist in a playlist
def get_existing_tracks(playlist_id):
    existing_tracks = set()
    results = sp.playlist_tracks(playlist_id, fields="items(track(uri)),next", limit=100)  # Include "next" explicitly
    while results:
        for item in results.get('items', []):  # Safely handle missing 'items'
            track = item.get('track')
            if track and 'uri' in track:
                existing_tracks.add(track['uri'])
        results = sp.next(results) if results and results.get('next') else None  # Safely handle 'next'
    return existing_tracks

def normalize_string(s):
    """Normalize string to remove special characters and accents."""
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower()

def normalize_genre(genres):
    normalized_genres = []
    # Create a regex pattern to match any of the country prefixes followed by a space
    pattern = re.compile(rf"^({'|'.join(re.escape(prefix) for prefix in country_prefix_file['country_prefixes'])})\s+", re.IGNORECASE)
    # Substitute the matched prefix with an empty string
    for genre in genres:
        normalized_genre = pattern.sub('', genre)
        normalized_genres.append(normalized_genre)
        if normalized_genre != genre:
            logging.info(f'Normalized genre "{genre}" to "{normalized_genre}".')
    return normalized_genres

# Load playlist data from file
file_path = os.path.join(LISTS_DIR, LIST_JSON)
with open(file_path, "r") as file:
    playlist_file = json.load(file)

# Load playlist data from file
c_prefix_path = os.path.join(HELPER_DIR, COUNTRY_PREFIXES_JSON)
with open(c_prefix_path, "r") as file:
    country_prefix_file = json.load(file)

# Access and process playlists
user_id = sp.me()['id']
for playlist in playlist_file["playlists"]:
    track_uris = []
    exact_matches_groups = []
    genre_list = []
    
    # Check if the playlist already exists
    existing_playlist_id = playlist_exists(user_id, playlist["playlistName"])
    if existing_playlist_id:
        logging.info(f"Playlist '{playlist['playlistName']}' already exists.")
        if CLEAR_PLAYLIST:
            # Clear the playlist
            logging.info("Clearing the playlist...")
            sp.playlist_change_details(existing_playlist_id, description=f'Generated automatically on {timestamp_short}. Learn more on GitHub: github.com/bschkuhl/spotify-playlist-creator')
            sp.playlist_replace_items(existing_playlist_id, [])  # This removes all existing tracks in the playlist
            logging.info("Playlist cleared.")
            existing_tracks = set()
        else:
            logging.info(f"Checking for missing tracks...")
            existing_tracks = get_existing_tracks(existing_playlist_id)
    else:
        logging.info(f"Creating new playlist: {playlist['playlistName']}")
        new_playlist = sp.user_playlist_create(user=user_id, name=playlist["playlistName"], public=True, description=f'Generated automatically on {timestamp_short}. Learn more on GitHub: github.com/bschkuhl/spotify-playlist-creator')
        existing_playlist_id = new_playlist['id']
        existing_tracks = set()

    # Process artists and their top tracks
    for artist in playlist["artists"]:
    # Perform search query with the artist name
        normalized_artistname = normalize_string(artist)
        results = sp.search(q=f'{artist}', type='artist', limit=50)  # Increase limit to handle multiple exact matches

        # Filter results for exact name matches (case-insensitive)
        exact_matches = [item for item in results['artists']['items'] if normalize_string(item['name']) == normalized_artistname]

        if not exact_matches and USE_LEV:
            approximate_matches = [
                item for item in results['artists']['items']
                if Levenshtein.distance(normalize_string(item['name']), normalized_artistname) == APPROX_MATCHES
            ]

            if approximate_matches:
                logging.info(f"Found approximate matches for artist '{artist}': {[item['name'] for item in approximate_matches]}")
                exact_matches = approximate_matches  # Treat approximate matches as exact matches for further processing
            else:
                logging.info(f"No matches (exact or approximate) found for artist '{artist}'")
        elif exact_matches:
            if len(exact_matches) > 1:
                # Log multiple exact matches
                logging.info(f"Multiple exact matches found for artist '{artist}': {[match['name'] for match in exact_matches]}")
                if PICK_GENRE_PROXIMITY:
                    exact_matches_groups.append(exact_matches)
                    continue
                elif not PICK_GENRE_PROXIMITY and PICK_HIGHER_POPULARITY:
                    # Choose the match with the highest popularity
                    best_match = max(exact_matches, key=lambda x: x['popularity'])
                    logging.info(f"Choosing the most popular match for artist '{artist}': {best_match['name']} with popularity {best_match['popularity']}")
                else:
                    # Skip processing if not picking the most popular match
                    logging.info(f"Skipping artist '{artist}' due to multiple matches and PICK_HIGHER_POPULARITY set to False")
                    continue
            else:
            # Single match
                best_match = exact_matches[0]
        
            # Process the best match
            artist_id = best_match['id']
            genre_list = genre_list + normalize_genre(best_match['genres'])
            top_tracks = sp.artist_top_tracks(artist_id)['tracks'][:3]
            
            # Extend track URIs if not already present
            track_uris.extend([track['uri'] for track in top_tracks if track['uri'] not in existing_tracks])
        else:
            logging.info(f"No exact match found for artist '{artist} in:'")
            logging.info(f"{[item['name'].lower() for item in results['artists']['items']]}")

    if PICK_GENRE_PROXIMITY:
        for group in exact_matches_groups:
            # check if per artist in match groups the genres and count how many matches. add to genre_matches list 
            # Find the item(s) with the highest number of matches
            max_matches = 0
            genre_matches = []
            for artist in group:
                if artist['name']  == 'Khan':
                    cool = 1
                matches = len(set(genre_list) & set( artist['genres']))
                if matches > max_matches:
                    max_matches = matches
                    genre_matches = [artist]  # Reset to this item
                elif matches == max_matches and matches > 0:
                    genre_matches.append(artist)  # Add to the list of best items
            
            if len(genre_matches) > 1: 
                best_match = max(genre_matches, key=lambda x: x['popularity'])
                logging.info(f"Choosing the most popular match for artist '{artist}': {best_match['name']} with popularity {best_match['popularity']}")
            elif len(genre_matches) == 1: 
                best_match = genre_matches[0]  # Take the first item if there's only one match
                logging.info(f"Choosing the best genre match for artist '{artist}': {best_match['name']} with genre match rating {max_matches}")
            elif PICK_HIGHER_POPULARITY:
                best_match = max(group, key=lambda x: x['popularity'])
                logging.info(f"Choosing the most popular match for artist '{artist}': {best_match['name']} with popularity {best_match['popularity']}")
            else: 
                continue

            # Process the best match
            artist_id = best_match['id']
            top_tracks = sp.artist_top_tracks(artist_id)['tracks'][:3]
            
            # Extend track URIs if not already present
            track_uris.extend([track['uri'] for track in top_tracks if track['uri'] not in existing_tracks])

    # Add new tracks to the playlist
    if track_uris:
        for i in range(0, len(track_uris), BATCH_SIZE):
            batch = track_uris[i:i + BATCH_SIZE]
            sp.playlist_add_items(existing_playlist_id, batch)
            logging.info(f"Added batch {i // BATCH_SIZE + 1} to the playlist '{playlist['playlistName']}'.")

    logging.info(f"Finished updating playlist: {playlist['playlistName']}\n\n")

logging.info(f"Finished updating playlists.")




