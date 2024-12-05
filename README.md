Spotify Playlist Creator

This is a Python-based script that automates the creation of Spotify playlists based on artists and festivals. Using the Spotify Web API via the spotipy library, the script searches for artists, retrieves their top tracks, and adds them to a new playlist.
Features

    Artist Search: Searches for artists using Spotify's search functionality.
    Top Tracks Retrieval: Fetches the top 3 tracks for each artist.
    Playlist Creation: Automatically creates a new playlist for each festival.
    Batch Upload: Handles Spotify's API limit of 100 tracks per request.

Prerequisites

    Spotify Developer Account:
        Sign up at Spotify for Developers.
        Create a new app and obtain the Client ID and Client Secret.

    Python:
        Install Python 3.7 or later.

    Required Python Libraries:
        spotipy
        python-dotenv

    Install them using:

pip install spotipy python-dotenv
