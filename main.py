import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import json

# Load environment variables from the .env file
load_dotenv()

# Set up Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID") 
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET") 
SPOTIFY_REDIRECT_URI = os.getenv("REDIRECT_URI") 
SCOPE = 'playlist-modify-public playlist-modify-private'
BATCH_SIZE = 100
LISTS_DIR = "./lists"
LIST_JSON = "example.json" # Replace with your own JSON file

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

# Load playlist data from file
file_path = os.path.join(LISTS_DIR, LIST_JSON)
with open(file_path, "r") as file:
    playlist_file = json.load(file)

# Access and process playlists
user_id = sp.me()['id']
for playlist in playlist_file["playlists"]:
    track_uris = []

    # Check if the playlist already exists
    existing_playlist_id = playlist_exists(user_id, playlist["playlistName"])
    if existing_playlist_id:
        print(f"Playlist '{playlist['playlistName']}' already exists. Checking for missing tracks...")
        existing_tracks = get_existing_tracks(existing_playlist_id)
    else:
        print(f"Creating new playlist: {playlist['playlistName']}")
        new_playlist = sp.user_playlist_create(user=user_id, name=playlist["playlistName"], public=True)
        existing_playlist_id = new_playlist['id']
        existing_tracks = set()

    # Process artists and their top tracks
    for artist in playlist["artists"]:
        results = sp.search(q=f'artist:{artist}', type='artist', limit=1)
        if results['artists']['items']:
            artist_id = results['artists']['items'][0]['id']
            top_tracks = sp.artist_top_tracks(artist_id)['tracks'][:3]
            track_uris.extend([track['uri'] for track in top_tracks if track['uri'] not in existing_tracks])

    # Add new tracks to the playlist
    if track_uris:
        for i in range(0, len(track_uris), BATCH_SIZE):
            batch = track_uris[i:i + BATCH_SIZE]
            sp.playlist_add_items(existing_playlist_id, batch)
            print(f"Added batch {i // BATCH_SIZE + 1} to the playlist '{playlist['playlistName']}'.")

    print(f"Finished updating playlist: {playlist['playlistName']}")



