import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# --- MOOD DETECTION (From Step 2) ---
MOOD_KEYWORDS = {
    "sad": ["rough", "awful", "terrible", "depressed", "sad", "cry", "grumpy"],
    "mellow": ["meh", "okay", "fine", "chill", "relax", "peaceful", "tired"],
    "happy": ["joy", "happy", "awesome", "great", "good"],
    "hyped": ["excited", "pumped", "amazing", "best day", "wow"]
}

MOOD_SETTINGS = {
    "sad": {
        "keywords": ["melancholic", "sad", "heartbreak"],
        "valence_range": (0.0, 0.3),
        "energy_range": (0.1, 0.4),
        "seed_genres": ["blues", "sad"]
    },
    # ... (keep your other mood settings)
}

def analyze_mood(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)["compound"]
    text_lower = text.lower()
    
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return mood, MOOD_SETTINGS[mood]
    
    if sentiment < -0.5:
        return "sad", MOOD_SETTINGS["sad"]
    elif sentiment < -0.1:
        return "mellow", MOOD_SETTINGS["mellow"]
    elif sentiment < 0.6:
        return "happy", MOOD_SETTINGS["happy"]
    else:
        return "hyped", MOOD_SETTINGS["hyped"]

# --- SPOTIFY AUTHENTICATION ---
def get_spotify_client():
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri="http://localhost:8888/callback"
        ))
        return sp
    except Exception as e:
        st.error(f"❌ Spotify login failed: {e}")
        return None

# --- STREAMLIT UI ---
st.title("🎧 Moody Playlist Generator")
user_input = st.text_input("How are you feeling today?", "I'm feeling...")

if st.button("Create Playlist"):
    if not user_input or "I'm feeling..." in user_input:
        st.warning("Please share your mood!")
    else:
        mood, mood_config = analyze_mood(user_input)
        st.success(f"Detected mood: **{mood.upper()}**")
        
        sp = get_spotify_client()
        if sp:
            with st.spinner(f"🎵 Finding {mood} songs..."):
                try:
                    # --- PLAYLIST GENERATION (From Step 3) ---
                    recommendations = sp.recommendations(
                        seed_genres=mood_config["seed_genres"],
                        limit=15,
                        target_valence=sum(mood_config["valence_range"]) / 2,
                        target_energy=sum(mood_config["energy_range"]) / 2
                    )
                    
                    # Display songs
                    st.subheader(f"Your {mood} playlist:")
                    for i, track in enumerate(recommendations["tracks"][:6]):
                        st.write(f"{i+1}. [{track['name']}]({track['external_urls']['spotify']}) by {track['artists'][0]['name']}")
                    
                    # Create playlist in Spotify
                    playlist = sp.user_playlist_create(
                        user=sp.me()["id"],
                        name=f"Moody: {mood.capitalize()} Vibes",
                        public=False,
                        description=f"Auto-generated based on mood: '{user_input}'"
                    )
                    track_uris = [track["uri"] for track in recommendations["tracks"]]
                    sp.playlist_add_items(playlist["id"], track_uris[:30])
                    
                    st.success("✅ Playlist created in your Spotify account!")
                    st.markdown(f"[🔗 Open Playlist]({playlist['external_urls']['spotify']})")
                    
                except Exception as e:
                    st.error(f"❌ Failed to create playlist: {e}")