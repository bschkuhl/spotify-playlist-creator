Here’s a detailed `README.md` for your Spotify Playlist Creator:

---

# **Spotify Playlist Creator**

This is a Python-based script that automates the creation of Spotify playlists based on artists and festivals. Using the Spotify Web API via the `spotipy` library, the script searches for artists, retrieves their top tracks, and adds them to a new playlist.

---

## **Features**
- **Artist Search**: Searches for artists using Spotify's search functionality.
- **Top Tracks Retrieval**: Fetches the top 3 tracks for each artist.
- **Playlist Creation**: Automatically creates a new playlist for each festival.
- **Batch Upload**: Handles Spotify's API limit of 100 tracks per request.

---

## **Prerequisites**
1. **Spotify Developer Account**: 
   - Sign up at [Spotify for Developers](https://developer.spotify.com/dashboard/).
   - Create a new app and obtain the `Client ID` and `Client Secret`.

2. **Python**:
   - Install Python 3.7 or later.

3. **Required Python Libraries**:
   - `spotipy`
   - `python-dotenv`

   Install them using:
   ```bash
   pip install spotipy python-dotenv
   ```

---

## **Setup**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/spotify-playlist-creator.git
cd spotify-playlist-creator
```

### **2. Create a `.env` File**
Create a `.env` file in the root directory and add the following:

```
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDIRECT_URI=http://localhost:8888/callback
```

Replace `your_client_id`, `your_client_secret`, and `http://localhost:8888/callback` with the credentials from your Spotify Developer account.

### **3. Update Festivals and Artists**
Modify the `festivals` object in the script to include your desired festivals and their artists:

```python
festivals = {
    "festivalList": [
        {
            "festivalName": "Rock Fest",
            "artists": ["Metallica", "Nirvana", "Pearl Jam"]
        },
        {
            "festivalName": "Pop Carnival",
            "artists": ["Taylor Swift", "Ed Sheeran", "Ariana Grande"]
        }
    ]
}
```

---

## **Usage**

### **Run the Script**
Execute the script to create playlists:
```bash
python spotify_playlist_creator.py
```

### **Output**
For each festival, a playlist will be created in your Spotify account, and the link to the playlist will be printed:

```
Playlist created: https://open.spotify.com/playlist/1234abcd5678efgh
```

---

## **Code Explanation**

### **Key Steps**
1. **Authentication**:
   The script authenticates the user using Spotify's OAuth 2.0. Ensure the scopes `playlist-modify-public` and/or `playlist-modify-private` are included.
   
2. **Artist Search**:
   Each artist is searched on Spotify to retrieve their `artist_id`.

3. **Top Tracks**:
   The top 3 tracks of each artist are fetched using the `artist_top_tracks` endpoint.

4. **Playlist Creation**:
   A new playlist is created for each festival using the `user_playlist_create` method.

5. **Batch Upload**:
   Tracks are added to the playlist in batches of 100 or fewer to comply with Spotify's API limits.

---

## **Error Handling**
- **Insufficient Scope**: Ensure the correct scopes are set in the OAuth configuration (`playlist-modify-public` or `playlist-modify-private`).
- **Too Many Tracks**: The script automatically splits track URIs into batches of 100 to avoid API errors.
- **Invalid Artist**: If an artist is not found, their tracks are skipped, and processing continues.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---
