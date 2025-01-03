import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
import json
import re

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

def scrape_track(url, dict):

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    if "bandcamp" in url:
        script_tag = soup.find('script', attrs={'data-player-data': True})
        if script_tag:
            data_player_data = script_tag['data-player-data']  # Extract the attribute content
            try:
                # Parse JSON content
                data = json.loads(data_player_data)
                artist = data.get('artist', None)
                album = data.get('album_title', None)
                if artist not in dict:
                    dict[f"{artist}"] = album
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
    elif "spotify" in url:
        if "album/" in url:
            get_album_and_artist(url.split("album/")[1].split("?")[0], dict)
    else:
        print("No 'data-player-data' script tag found.")  
    
    return dict

# Get artist and album information by album ID
def get_album_and_artist(album_id, dict):
    album_data = sp.album(album_id)
    artist = album_data['artists'][0]['name']
    album = album_data['name']
    dict[f"{artist}"] = album

    return dict

def scrape_iframes(url):
    """
    Scrape links from iframe tags on a given webpage.
    
    Args:
        url (str): The URL of the webpage to scrape.

    Returns:
        list: A list of links found in iframe tags.
    """
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all iframe tags
    iframe_tags = soup.find_all('iframe')
    
    # Extract links
    links = []
    for iframe in iframe_tags:
        src = iframe.get('src')
        if src and 'bandcamp.com' in src:
            links.append(src)
        elif src and 'open.spotify.com' in src:
            links.append(src)
    
    return links


# Function to scrape bandname, album, and title from a website
def scrape_website(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    dict = {}
    if "theobelisk" in url:
        for tag in soup.select('.entrytext h3'):  # Mention HTML tag names here. .entrytext h2
            child = tag.find('em')
            if child:
                key = tag.next.rstrip(', ').strip().replace('\u200b', '')
                key = re.sub(r"^\d+\.\s*", "", key)
                value = child.text.strip().replace('\u200b', '')
                dict[key] = value
        for tag in soup.select('.entrytext h2'):  # Mention HTML tag names here. .entrytext h2
            child = tag.find('em')
            if child:
                key = tag.next.rstrip(', ').strip().replace('\u200b', '')
                key = re.sub(r"^\d+\.\s*", "", key)
                value = child.text.strip().replace('\u200b', '')
                dict[key] = value
    elif "thedevilsmouth" in url:
        dict = {}
        links = scrape_iframes(url)
        for link in links:
            dict = scrape_track(link, dict)
    
    title = soup.title.string.strip().replace('\u200b', '')

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
    input_mode = input("Enter 'manual' to provide bandname and album, or 'url' to scrape from a website: ").strip().replace('\u200b', '').lower()
    
    if input_mode == 'manual':
        user_input = input("Enter bandname and album (separated by a comma): ").strip().replace('\u200b', '')
        bandname, album = [x.strip().replace('\u200b', '') for x in user_input.split(',', 1)]
        playlist_name = input("Enter playlist name: ").strip().replace('\u200b', '')
        dict = {}
        dict[f"{bandname}"] = album

        search_and_add_to_playlist(dict, playlist_name, url)
    elif input_mode == 'url':
        url = input("Enter the URL to scrape: ").strip().replace('\u200b', '')
        playlist_name = input("Enter playlist name: ").strip().replace('\u200b', '')

        try:
            dict, title = scrape_website(url)
            #Devils mouth: Top 30 2024
            #https://thedevilsmouth.substack.com/p/top-30-albums-2024-part-i-30-25
            if playlist_name != None:
                title = playlist_name
            search_and_add_to_playlist(dict, title, url)
        except Exception as e:
            logging.error(f"Failed to scrape website: {e}")
    else:
        logging.error("Invalid input mode. Please enter 'manual' or 'url'.")

if __name__ == "__main__":
    main()
