# Spotify Playlist Creator

This Python script automates the creation and updating of Spotify playlists based on a JSON configuration file. It uses the Spotify Web API via the `spotipy` library to check for existing playlists and tracks, add missing tracks, and create new playlists as needed.

---

## **Features**
- **Playlist Management**:
  - Checks if a playlist already exists before creating a new one.
  - Updates existing playlists by adding only missing tracks.
- **Track Management**:
  - Avoids duplicate tracks in playlists.
  - Fetches the top 3 tracks for each artist and adds them to the playlist.
- **Batch Upload**:
  - Handles Spotify's API limit of 100 tracks per request by batching track additions.
- **Website Scraping**:
  - Scrapes band and album information from websites. 
  - Automatically creates a playlist with the scraped data. 
  - Playlist name is dynamically set to the website's title.
---

## **Prerequisites**
1. **Spotify Developer Account**:
   - Sign up at [Spotify for Developers](https://developer.spotify.com/dashboard/).
   - Create a new app and obtain the `Client ID` and `Client Secret`.

2. **Python 3.7+**:
   - Install Python if not already installed. You can download it from [Python.org](https://www.python.org/).

3. **Required Python Libraries**:
   Install the dependencies:
   ```bash
   pip install -r requirements.txt  
   ```

4. **Environment Variables**:
   - Create a `.env` file in the project root and add the following:
     ```
     CLIENT_ID=your_client_id
     CLIENT_SECRET=your_client_secret
     REDIRECT_URI=http://localhost:8888/callback
     ```

5. **JSON Playlist Configuration**:
   - Place your playlist JSON files in the `/lists` directory.
   - Ensure the JSON file structure matches the following example:
     ```json
     {
       "playlists": [
         {
           "playlistName": "My Playlist 1",
           "artists": ["Artist 1", "Artist 2", "Artist 3"]
         },
         {
           "playlistName": "My Playlist 2",
           "artists": ["Artist A", "Artist B"]
         }
       ]
     }
     ```

---

## **Setup and Usage**

### **1. Clone the Repository**
```bash
git clone https://github.com/your-username/spotify-playlist-creator.git
cd spotify-playlist-creator
```

### **2. Prepare Your JSON Files**
- Add your playlist JSON files to the `/lists` directory.
- Update the `LIST_JSON` variable in the script to point to your desired JSON file:
  ```python
  LIST_JSON = "example.json"
  ```

### **3. Run the Script**
Execute the script to create and update playlists:
```bash
python by_artist.py
```
Execute the script to scrape a website like theobelisk.net and update playlists:
```bash
python by_artist_and_album.py
```

## **Error Handling**
- **Invalid JSON**: The script will raise an error if the JSON file structure is incorrect.
- **Rate Limits**: Spotify API rate limits are managed, but delays may occur with large numbers of tracks or artists.
- **Missing Tracks**: If an artist has no top tracks, they are skipped without stopping the script.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---
