import spotipy
from spotipy.oauth2 import SpotifyOAuth
import itertools
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Set up Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("REDIRECT_URI")  # Adjust as needed
SCOPE = 'playlist-modify-public playlist-modify-private'
BATCH_SIZE = 100

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE
))

# Input list of artists
festivals = {
    "festivalList": [
        {
            "festivalPlaylistName": "Dyamo Metalfest 2025 Playlist",
            "artists": ["Charlotte Wessels", "Conjurer", "Dymytry", "Fear Factory", "Gojira", "I Prevail", "Kataklysm", "Kerry King", "Kublai Khan TX", "Mastodon", "Ministry", "Ne Obliviscaris", "Obituary", "Paradise Lost", "Phantom Elite", "Pothamus", "Sirenia", "Static-X", "Terrifier", "Thrown", "Wraith", "Within Temptation"]
        },
        {
            "festivalPlaylistName": "Alcatraz 2025 Playlist",
            "artists": ["3 Inches Of Blood", "Absu", "Alkerdeel", "Avulsed", "Baest", "Bark", "Between The Buried And Me", "Blaze Bayley", "Bloodclot", "Borknagar", "Briqueville", "Caliban", "Candlemass", "Clowns", "Cobracide", "Coffin Feeder", "Congress", "Conjurer", "Crypt Sermon", "Crystal Lake", "Cult Of Lina", "Cult Of Scarecrow", "D-A-D", "Dark Angel", "Devastation", "Devildriver", "Dimmu Borgir", "Dool", "Dope", "Doro", "Dvne", "Dying Fetus", "Earthless", "Emperor", "Evil Invaders", "Exhorder", "Feat Factory", "Fit For A King", "Flotsam And Jetsam", "Forbidden", "Fu Manchu", "Full Of Hell", "Gaerea", "Gutalax", "Holy Mother", "Hypocrist", "Il Nino", "In Aphelion", "Kerry King", "King Buffalo", "Knife", "Kreator", "Leprous", "Machine Head", "Magic Kingdom", "Majestica", "Mastodon", "Me And That Man", "Messa", "Michael Schenker", "Ministry", "Nalibomb", "Nasty Savage", "Ne Obliviscaris", "Obituary", "Overkill", "Pestilence", "Phil Campbell", "Phil Campbell And The Bastard Sons", "Pig Destroyer", "Primal Creation", "Promise Down", "Prong", "Psycroptic", "Rivers Of Nihil", "Rotting Christ", "Signs Of Algorithm", "Slaughter Messiah", "Splendidula", "Static-X", "Suffocation", "Tenside", "Terrifier", "Thabbath Doom Occulta", "The Belgian Quo Band", "The Black Dahlia Murder", "The Night Eternal", "Thrown", "Thy Catafalque", "Tsjuder", "Vader", "Violent Sin", "Vola", "Vulture", "W.A.S.P.", "Whatever It Takes", "Whiplash", "Winterfylleth", "Wytch Hazel", "Year Of No Light"]
        },
        {
            "festivalPlaylistName": "Roadburn 2025 Playlist",
            "artists": ["Altın Gün", "Bambara", "Big Brave", "Black Curse", "Blind Girls", "Buñuel", "Chat Pile", "Choke Chain", "CHVE", "Cinder Well", "Coilguns", "Concrete Winds", "Curses (Live)", "De Mannen Broeders", "Denisa", "Dødheimsgard", "Faetooth", "FIRE!", "Gillian Carter", "Glassing", "Gnod Drop Out With White Hills", "Great Falls", "Human Impact", "Kylesa", "Messa", "New Age Doom feat. Tuvaband", "One Leg One Eye", "Ora Cogan", "ØXN", "pageninetynine", "Ponte del Diavolo", "Pothamus", "Pygmy Lush", "Smote", "Stress Positions", "Sumac", "The HIRS Collective", "Thou", "Tristwch Y Fenywod", "Violent Magic Orchestra", "Vuur & Zijde", "Vyva Melinkolya", "Witch Club Satan", "Zombie Zombie"]
        },
        {
            "festivalPlaylistName": "Graspop 2025 Playlist",
            "artists": ["Airbourne", "Alien Ant Farm", "Amenra", "Amira Elfeky", "Angelus Apatrida", "Apocalyptica", "As Everything Unfolds", "Bad Wolves", "Beast In Black", "Beyond The Black", "Cattle Decapitation", "Charlotte Wessels", "Creeper", "Currents", "Dayseeker", "Dead Poet Society", "Deafheaven", "Death Angel", "Dragonforce", "Dream Theater", "Eagles of Death Metal", "Employed To Serve", "Epica", "Falling In Reverse", "Filter", "Fit For An Autopsy", "Fleshwater", "Flogging Molly", "From Ashes To New", "Gloryhammer", "Halocene", "Hardy", "Hatebreed", "Heaven Shall Burn", "Hot Milk", "House Of Protection", "Imminence", "In Flames", "Jerry Cantrell", "Jinjer", "Julie Christmas", "Katatonia", "Kim Dracula", "King Diamond", "Kittie", "Krokus", "Lagwagon", "Last Train", "Lorna Shore", "Mass Hysteria", "Motionless In White", "Municipal Waste", "Northlane", "Nothing More", "Nova Twins", "Novelists", "Orange Goblin", "Orbit Culture", "Paradise Lost", "Perturbator", "Peyton Parrish", "Primordial", "Psychonaut", "Rise Of The Northstar", "Sacred Reich", "Savatage", "Seven Hours After Violet", "Signs of the Swarm", "SiM", "Skillet", "Soen", "Spectral Wound", "Spiritbox", "Static Dress", "Stray From The Path", "Sun Dont Shine", "Sylosis", "Terror", "The Dead Daisies", "The Ghost Inside", "The Hu", "The Raven Age", "Thrice", "Trash Boat", "Triptykon", "Villagers Of Ioannina City", "Vowws", "Whitechapel"]
        },
        {
            "festivalPlaylistName": "Summer Breeze 2025 Playlist",
            "artists": ["3 Inches of Blood", "Abbie Falls", "Allt", "Angelmaker", "Angelus Apatrida", "Annisokay", "Asp", "August Burns Red", "Benighted", "Between the Buried and Me", "Counterparts", "Cult of Luna", "Dimmu Borgir", "Dominum", "Destruction", "Downset", "Elvenking", "Evil Invaders", "Fit for a King", "Fiddler’s Green", "Gaerea", "Gutalax", "Hammer King", "Hanabie", "Heavysaurus", "Iotunn", "Imperial Triumphant", "In Extremo", "Kublai Khan TX", "Kanonenfieber", "Kissin’ Dynamite", "League of Distortion", "Lik", "Machine Head", "Mr. Hurley & Die Pulveraffen", "Nytt Land", "Obituary", "Primordial", "Rivers of Nihil", "Royal Republic", "Saxon", "Septicflesh", "Slope", "Static-X", "Tarja & Marko Hietala", "Thrown", "Turbobier", "Within Temptation", "Wind Rose", "Warbringer", "Windrose"]
        },
        {
            "festivalPlaylistName": "Reload Festival 2025 Playlist",
            "artists": ["August Burns Red", "Annisokay", "Attila", "Bleed from Within", "Blood Command", "Celestial Sanctuary", "Conjurer", "Coldrain", "Counterparts", "Crystal Lake", "Drowning Pool", "Dope", "Downset", "Droput Kings", "Fear Factory", "Finntroll", "Frog Bog Dosenband", "Gojira", "Hanabie.", "I Prevail", "Kataklysm", "Kublai Khan TX", "Machine Head", "Mambo Kurt", "Ministry", "Obituary", "Prong", "Rise of the Northstar", "Rivers of Nihil", "Scythe Beast", "Shoreline", "Static-X", "The Browning", "The Butcher Sisters", "The Exploited", "The Halo Effect", "Trivium", "TurboBier", "While She Sleeps", "Wind Rose"]
        },
        {
            "festivalPlaylistName": "Desertfest 2025 Playlist",
            "artists": ["24/7 Diva Heaven", "Bismut", "Castle Rat", "Daufødt", "Elder", "Elephant Tree", "Eyehategod", "Frankie and the Witch Fingers", "Green Milk from the Planet Orange", "Kant", "Khan", "Lowrider", "Margaritas Podridas", "Rickshaw Billie’s Burger Patrol", "Skyjoggers", "Slomosa", "The Devil and the Almighty Blues", "The Hellacopters", "Turbo Moses", "Wine Lips"]
        },
        {
            "festivalPlaylistName": "STFU 2025 Playlist",
            "artists": []
        },
        {
            "festivalPlaylistName": "Hoflaerm 2025 Playlist",
            "artists": ["Annie Taylor", "Coltaine", "Elephant Tree", "Graveyard", "Khan", "Lurch", "Maidavale", "Monolord", "Piece", "Rezn", "Spirit Mother", "The Warlocks", "Vinnum Sabbathi", "Vug", "Elephant Tree"]
        },
    ]
}

# Accessing the object
for festival in festivals["festivalList"]:
    track_uris = []
    for artist in festival["artists"]:
     results = sp.search(q=f'artist:{artist}', type='artist', limit=1)
     if results['artists']['items']:
        artist_id = results['artists']['items'][0]['id']
        top_tracks = sp.artist_top_tracks(artist_id)['tracks'][:3]
        track_uris.extend([track['uri'] for track in top_tracks])   
            
    # Create a new playlist
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user=user_id, name=festival["festivalPlaylistName"], public=True)
    playlist_id = playlist['id']

    # Add tracks to the playlist
    if track_uris:
        for i in range(0, len(track_uris), BATCH_SIZE):
            batch = track_uris[i:i + BATCH_SIZE]
            sp.playlist_add_items(playlist_id, batch)
            print(f"Added batch {i // BATCH_SIZE + 1} to the playlist.")

    print(f'Playlist created: {playlist["external_urls"]["spotify"]}')



