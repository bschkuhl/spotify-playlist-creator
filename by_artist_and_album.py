import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Created originally for scraping theobelisk reviews and creating spotify playlists

# Load environment variables from the .env file
load_dotenv()

# Set up Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = 'playlist-modify-public'
LOG_DIR = './logs'

# Configure logging to log to a file
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
timestamp_short = datetime.now().strftime('%Y-%m-%d')
log_file = os.path.join(LOG_DIR, f'artist_and_album_search_{timestamp}.log')

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

# Function to scrape bandname, album, and title from a website
def scrape_website(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    dict = {}
    for tag in soup.select('div#content .post .entrytext h2'):  # Mention HTML tag names here. .entrytext h2
        child = tag.find('em')
        if child:
            dict[f"{tag.next.rstrip(', ').strip()}"] = child.text.strip()
    
    title = soup.title.string.strip()

    return dict, title

# Function to search Spotify and add to a playlist
def search_and_add_to_playlist(dict, playlist_name, url):
    user_id = sp.me()['id']
    playlist_id = playlist_exists(user_id, playlist_name)
    timestamp_short = datetime.now().strftime('%Y-%m-%d')
    if not playlist_id:
        logging.info(f"Creating new playlist: {playlist_name}")
        new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True, description=f'Generated automatically on {timestamp_short}. Source: {url}')
        playlist_id = new_playlist['id']
    else:
        logging.info(f"Playlist '{playlist_name}' already exists.")
    
    for bandname, album in dict.items():
        logging.info(f"Scraped data - Bandname: {bandname}, Album: {album}")
        query = f"album:{album} artist:{bandname}"
        results = sp.search(q=query, type='album', limit=1)
        if results['albums']['items']:
            album_id = results['albums']['items'][0]['id']
            tracks = sp.album_tracks(album_id)['items']
            track_uris = [track['uri'] for track in tracks]
            
            if track_uris:
                sp.playlist_add_items(playlist_id, track_uris)
        else:
            logging.warning(f"No album found for '{album}' by '{bandname}'.")

# Main logic to handle input
def main():
    input_mode = input("Enter 'manual' to provide bandname and album, or 'url' to scrape from a website: ").strip().lower()
    
    if input_mode == 'manual':
        user_input = input("Enter bandname and album (separated by a comma): ").strip()
        bandname, album = [x.strip() for x in user_input.split(',', 1)]
        playlist_name = input("Enter playlist name: ").strip()
        dict = {}
        dict[f"{bandname}"] = album

        search_and_add_to_playlist(dict, playlist_name, url)
    elif input_mode == 'url':
        url = input("Enter the URL to scrape: ").strip()
        try:
            dict, title = scrape_website(url)
            search_and_add_to_playlist(dict, title, url)
        except Exception as e:
            logging.error(f"Failed to scrape website: {e}")
    else:
        logging.error("Invalid input mode. Please enter 'manual' or 'url'.")

if __name__ == "__main__":
    main()
