import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Mood configuration with track seeds and audio features
MOOD_SETTINGS = {
    "sad": {
        "keywords": ["sad", "depressed", "heartbroken", "lonely", "miserable"],
        "valence": 0.25,
        "energy": 0.3,
        "seed_tracks": ["79OpcqzQvmqmy92saiWA4R"],
        "search_terms": ["sad songs", "heartbreak music", "melancholic"]
    },
    "mellow": {
        "keywords": ["chill", "calm", "relaxed", "peaceful", "tired"],
        "valence": 0.5,
        "energy": 0.4,
        "seed_tracks": ["5Atp6XQ7Oppf6NCPyKqKkQ", "3JvKfv6T31zOQini8f5Q4h"],
        "search_terms": ["chill music", "relaxing songs", "lo-fi"]
    },
    "happy": {
        "keywords": ["happy", "joyful", "cheerful", "good", "great"],
        "valence": 0.75,
        "energy": 0.65,
        "seed_tracks": ["1mea3bSkSGXuIRvnydlB5b", "60nZcImufyMA1MKQY3dcCH"],
        "search_terms": ["happy songs", "upbeat music", "joyful"]
    },
    "hyped": {
        "keywords": ["energetic", "pumped", "excited", "party", "ecstatic"],
        "valence": 0.85,
        "energy": 0.85,
        "seed_tracks": ["7GhIk7Il098yCjg4BQjzvb", "0UaMYEvWZi0ZqiDOoHU3YI"],
        "search_terms": ["party songs", "energetic music", "workout"]
    }
}

def analyze_mood(text):
    """Analyze text input to determine mood using keywords and sentiment analysis."""
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)["compound"]
    text_lower = text.lower()
    
    for mood, config in MOOD_SETTINGS.items():
        if any(keyword in text_lower for keyword in config["keywords"]):
            return mood, config
    
    if sentiment < -0.5:
        return "sad", MOOD_SETTINGS["sad"]
    elif sentiment < -0.1:
        return "mellow", MOOD_SETTINGS["mellow"]
    elif sentiment < 0.6:
        return "happy", MOOD_SETTINGS["happy"]
    else:
        return "hyped", MOOD_SETTINGS["hyped"]

def initialize_spotify_client():
    """Initialize and return authenticated Spotify client."""
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv("SPOTIPY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
            redirect_uri="http://localhost:8888/callback",
            scope="playlist-modify-private"
        ))
        print("✅ Authentication successful!")
        print(f"👤 Logged in as: {sp.me()['display_name']}")
        return sp
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        exit()

def get_tracks(sp, mood_config):
    """Get tracks based on mood configuration using recommendations or fallback search."""
    track_list = []
    
    try:
        recommendations = sp.recommendations(
            seed_tracks=mood_config["seed_tracks"],
            limit=15,
            target_valence=mood_config["valence"],
            target_energy=mood_config["energy"],
            min_popularity=40
        )
        track_list.extend([{ "name": t["name"], "artist": t["artists"][0]["name"], "url": t["external_urls"]["spotify"], "uri": t["uri"] } for t in recommendations["tracks"]])
    except Exception as e:
        print(f"⚠️ Recommendation API error: {e}")
        for term in mood_config["search_terms"]:
            try:
                results = sp.search(q=term, type="track", limit=5, market="US")
                track_list.extend([{ "name": t["name"], "artist": t["artists"][0]["name"], "url": t["external_urls"]["spotify"], "uri": t["uri"] } for t in results["tracks"]["items"]])
                time.sleep(0.2)
            except Exception as e:
                print(f"⚠️ Search failed for '{term}': {e}")
    return list({t["uri"]: t for t in track_list}.values())

def create_playlist(sp, mood, text, tracks):
    """Create a Spotify playlist with the given tracks."""
    try:
        user_id = sp.current_user()["id"]
        playlist = sp.user_playlist_create(
            user=user_id,
            name=f"Moody: {mood.capitalize()} Vibes",
            public=False,
            description=f"Auto-generated playlist for when you feel {mood} ({text})"
        )
        if tracks:
            sp.playlist_add_items(playlist["id"], [t["uri"] for t in tracks[:100]])
            print(f"\n✅ Playlist created: {playlist['external_urls']['spotify']}")
            return playlist
        print("⚠️ No tracks found.")
    except Exception as e:
        print(f"❌ Failed to create playlist: {e}")

def main():
    """Run the Moody Playlist Generator."""
    sp = initialize_spotify_client()
    text = input("\nHow are you feeling today? ")
    mood, mood_config = analyze_mood(text)
    print(f"\n🎵 Detected mood: {mood.capitalize()}")
    tracks = get_tracks(sp, mood_config)
    if tracks:
        print(f"\n🎧 Playlist preview:")
        for i, t in enumerate(tracks[:6]):
            print(f"{i+1}. {t['name']} by {t['artist']}\n   {t['url']}")
        create_playlist(sp, mood, text, tracks)
    else:
        print("⚠️ No suitable tracks found.")

if __name__ == "__main__":
    main()
