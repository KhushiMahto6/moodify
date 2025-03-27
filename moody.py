import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from textblob import TextBlob
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("17231becb04a4fb588f61930af7851e8"),  # ← Get from .env
    client_secret=os.getenv("ab5d7b18c19342758a78f5daf5051df9"),  # ← Get from .env
    redirect_uri="http://localhost:8888/callback",
    scope="playlist-modify-private"
))

print("CLIENT_ID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("CLIENT_SECRET:", os.getenv("SPOTIPY_CLIENT_SECRET"))

# Step 1: Get user mood
text = input("How are you feeling? ")
blob = TextBlob(text)
sentiment = blob.sentiment.polarity

# Step 2: Define mood keywords
if sentiment < -0.5:
    mood = "sad"
    keywords = ["melancholic", "heartbreak", "rainy day"]
elif sentiment < 0:
    mood = "mellow"
    keywords = ["chill", "calm", "lo-fi"]
elif sentiment < 0.5:
    mood = "happy"
    keywords = ["uplifting", "summer", "dance"]
else:
    mood = "hyped"
    keywords = ["energy", "workout", "party"]

# Step 3: Search Spotify for tracks
print(f"\n🔍 Searching Spotify for {mood} songs...")

track_list = []
for keyword in keywords:
    results = sp.search(q=keyword, type="track", limit=2)  # Get 2 tracks per keyword
    for track in results["tracks"]["items"]:
        track_list.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "url": track["external_urls"]["spotify"]
        })

# Step 4: Display the playlist
print(f"\n🎧 Here's your {mood} playlist:")
for i, track in enumerate(track_list[:6]):  # Show top 6 tracks
    print(f"{i+1}. '{track['name']}' by {track['artist']}")
    print(f"   Listen: {track['url']}\n")

# Step 5: Create a playlist in the user's account
user_id = sp.current_user()["id"]  # Get Spotify username
playlist_name = f"Moody: {mood.capitalize()} Vibes ({len(track_list)} Songs)"

# Create the playlist
playlist = sp.user_playlist_create(
    user=user_id,
    name=playlist_name,
    public=False,
    description=f"Auto-generated because you felt: '{text}'"
)
# Troll: Add Rick Astley if mood is super sad
if sentiment < -0.8:
    rick_roll = sp.search(q="Never Gonna Give You Up", type="track", limit=1)
    track_uris.insert(0, rick_roll["tracks"]["items"][0]["uri"])  # Add to start
    print("\n👀 Added a surprise song... trust me.")

# Add tracks to the playlist
track_uris = [track["url"].split("/")[-1] for track in track_list]  # Extract Spotify URIs
sp.playlist_add_items(playlist["id"], track_uris[:30])  # Max 30 tracks

# Share the playlist link
print(f"\n✅ Playlist created in your Spotify account!")
print(f"🔗 Open it here: {playlist['external_urls']['spotify']}")