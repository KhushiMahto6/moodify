import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mood configuration with track seeds and audio features
MOOD_SETTINGS = {
    "sad": {
        "keywords": ["sad", "depressed", "heartbroken", "lonely", "miserable"],
        "valence": 0.25,  # Low positivity
        "energy": 0.3,    # Low energy
        "seed_tracks": [
            "1tqHZCVFf6QUs6k0MK8Z4N",  # "Someone Like You" - Adele
            "6A6Z6imlQ46ZQFHhKzjqFZ"   # "Hurt" - Johnny Cash
        ],
        "search_terms": ["sad songs", "heartbreak music", "melancholic"]
    },
    "mellow": {
        "keywords": ["chill", "calm", "relaxed", "peaceful", "tired"],
        "valence": 0.5,   # Neutral positivity
        "energy": 0.4,    # Medium-low energy
        "seed_tracks": [
            "5Atp6XQ7Oppf6NCPyKqKkQ",  # "Sunflower" - Post Malone
            "3JvKfv6T31zOQini8f5Q4h"   # "Circles" - Post Malone
        ],
        "search_terms": ["chill music", "relaxing songs", "lo-fi"]
    },
    "happy": {
        "keywords": ["happy", "joyful", "cheerful", "good", "great"],
        "valence": 0.75,  # High positivity
        "energy": 0.65,   # Medium energy
        "seed_tracks": [
            "1mea3bSkSGXuIRvnydlB5b",  # "Can't Stop the Feeling" - Justin Timberlake
            "60nZcImufyMA1MKQY3dcCH"   # "Happy" - Pharrell Williams
        ],
        "search_terms": ["happy songs", "upbeat music", "joyful"]
    },
    "hyped": {
        "keywords": ["energetic", "pumped", "excited", "party", "ecstatic"],
        "valence": 0.85,  # Very high positivity
        "energy": 0.85,   # High energy
        "seed_tracks": [
            "7GhIk7Il098yCjg4BQjzvb",  # "Titanium" - David Guetta
            "0UaMYEvWZi0ZqiDOoHU3YI"   # "Don't Let Me Down" - The Chainsmokers
        ],
        "search_terms": ["party songs", "energetic music", "workout"]
    }
}

def analyze_mood(text):
    """Analyze text input to determine mood using keywords and sentiment analysis."""
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)["compound"]
    text_lower = text.lower()
    
    # Check for direct keyword matches first
    for mood, config in MOOD_SETTINGS.items():
        if any(keyword in text_lower for keyword in config["keywords"]):
            return mood, config
    
    # Fallback to sentiment analysis
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
            scope="playlist-modify-private",
            redirect_uri="http://localhost:8888/callback"
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
    
    # First try: Get recommendations using seed tracks
    try:
        recommendations = sp.recommendations(
            seed_tracks=mood_config["seed_tracks"][:2],
            limit=15,
            target_valence=mood_config["valence"],
            target_energy=mood_config["energy"],
            min_popularity=40
        )
        
        if recommendations and "tracks" in recommendations:
            for track in recommendations["tracks"]:
                track_list.append({
                    "name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "url": track["external_urls"]["spotify"],
                    "uri": track["uri"]
                })
    except Exception as e:
        print(f"⚠️ Recommendation API error: {e}")
    
    # Fallback: Search by mood keywords if no tracks found
    if not track_list:
        for term in mood_config["search_terms"][:2]:
            try:
                results = sp.search(
                    q=term,
                    type="track",
                    limit=5,
                    market="US"
                )
                if results and "tracks" in results and "items" in results["tracks"]:
                    for track in results["tracks"]["items"]:
                        track_list.append({
                            "name": track["name"],
                            "artist": track["artists"][0]["name"],
                            "url": track["external_urls"]["spotify"],
                            "uri": track["uri"]
                        })
            except Exception as e:
                print(f"⚠️ Search failed for '{term}': {e}")
    
    # Remove duplicate tracks
    unique_tracks = {}
    for track in track_list:
        if track["uri"] not in unique_tracks:
            unique_tracks[track["uri"]] = track
    return list(unique_tracks.values())

def create_playlist(sp, mood, text, tracks):
    """Create a Spotify playlist with the given tracks."""
    try:
        user_id = sp.current_user()["id"]
        playlist_name = f"Moody: {mood.capitalize()} Vibes"
        playlist_description = f"Auto-generated playlist for when you feel {mood} ({text})"
        
        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=playlist_description
        )
        
        if tracks:
            # Add tracks in batches of 100 (Spotify's limit)
            track_uris = [track["uri"] for track in tracks[:100]]
            sp.playlist_add_items(playlist["id"], track_uris)
            print(f"\n✅ Successfully created playlist with {len(track_uris)} tracks!")
            print(f"🔗 Open in Spotify: {playlist['external_urls']['spotify']}")
            return playlist
        else:
            print("⚠️ No tracks were found to add to the playlist.")
            return None
            
    except Exception as e:
        print(f"❌ Failed to create playlist: {e}")
        return None

def main():
    """Main function to run the Moody Playlist Generator."""
    # Initialize Spotify client
    sp = initialize_spotify_client()
    
    # Get user input
    text = input("\nHow are you feeling today? ")
    
    # Analyze mood
    mood, mood_config = analyze_mood(text)
    print(f"\n🎵 Detected mood: {mood.capitalize()}")
    
    # Get tracks for the detected mood
    print(f"\n🔍 Searching for {mood} songs...")
    tracks = get_tracks(sp, mood_config)
    
    # Display playlist preview
    if tracks:
        print(f"\n🎧 Here's your {mood} playlist preview:")
        for i, track in enumerate(tracks[:6]):
            print(f"{i+1}. {track['name']} by {track['artist']}")
            print(f"   {track['url']}\n")
    else:
        print("\n⚠️ Couldn't find any tracks for this mood.")
        return
    
    # Create playlist in Spotify
    create_playlist(sp, mood, text, tracks)

if __name__ == "__main__":
    main()