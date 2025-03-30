import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# --- MOOD CONFIGURATION ---
MOOD_KEYWORDS = {
    "sad": ["rough", "awful", "terrible", "depressed", "sad", "cry", "grumpy"],
    "mellow": ["meh", "okay", "fine", "chill", "relax", "peaceful", "tired"],
    "happy": ["joy", "happy", "awesome", "great", "good"],
    "hyped": ["excited", "pumped", "amazing", "best day", "wow"]
}

MOOD_SETTINGS = {
    "sad": {
        "keywords": ["melancholic", "sad", "heartbreak"],
        "valence_range": (0.0, 0.4),
        "energy_range": (0.1, 0.5),
        "seed_genres": ["blues", "acoustic"],
        "color": "#3498db",
        "emoji": "😢"
    },
    "mellow": {
        "keywords": ["chill", "lo-fi", "calm"],
        "valence_range": (0.3, 0.6),
        "energy_range": (0.3, 0.6),
        "seed_genres": ["chill", "ambient"],
        "color": "#2ecc71",
        "emoji": "😌"
    },
    "happy": {
        "keywords": ["happy", "uplifting", "joyful"],
        "valence_range": (0.6, 0.8),
        "energy_range": (0.5, 0.8),
        "seed_genres": ["pop", "indie"],
        "color": "#f1c40f",
        "emoji": "😊"
    },
    "hyped": {
        "keywords": ["energy", "workout", "party"],
        "valence_range": (0.8, 1.0),
        "energy_range": (0.7, 1.0),
        "seed_genres": ["edm", "dance"],
        "color": "#e74c3c",
        "emoji": "🤩"
    }
}

# --- CORE FUNCTIONS ---
def analyze_mood(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(text)["compound"]
    text_lower = text.lower()
    
    # Keyword matching first
    for mood, keywords in MOOD_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return mood, MOOD_SETTINGS[mood]
    
    # Sentiment fallback
    if sentiment < -0.5:
        return "sad", MOOD_SETTINGS["sad"]
    elif sentiment < -0.1:
        return "mellow", MOOD_SETTINGS["mellow"]
    elif sentiment < 0.6:
        return "happy", MOOD_SETTINGS["happy"]
    return "hyped", MOOD_SETTINGS["hyped"]

def get_spotify_client():
    try:
        return spotipy.Spotify(auth_manager=SpotifyOAuth(
            scope="playlist-modify-private",
            redirect_uri="http://localhost:8888/callback"
        ))
    except Exception as e:
        st.error(f"❌ Spotify login failed: {e}")
        return None

def apply_mood_theme(mood):
    """Apply dynamic styling based on mood"""
    st.markdown(f"""
        <style>
            .stTextInput input {{ border-color: {MOOD_SETTINGS[mood]['color']} }}
            .stButton>button {{ 
                background-color: {MOOD_SETTINGS[mood]['color']};
                color: white;
            }}
            .mood-header {{ color: {MOOD_SETTINGS[mood]['color']} }}
        </style>
    """, unsafe_allow_html=True)

# --- STREAMLIT UI ---
st.set_page_config(page_title="Moody Playlist Generator", page_icon="🎧")

# Sidebar for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Main app
st.title(f"{MOOD_SETTINGS['happy']['emoji']} Moody Playlist Generator")
user_input = st.text_input("How are you feeling today?", "I'm feeling...")

if st.button("Create Playlist"):
    if not user_input or "I'm feeling..." in user_input:
        st.warning("Please share your mood!")
    else:
        mood, mood_config = analyze_mood(user_input)
        st.session_state.history.append((mood, user_input))
        
        # Apply mood-specific styling
        apply_mood_theme(mood)
        st.success(f"Detected mood: **{mood_config['emoji']} {mood.upper()}**")
        
        sp = get_spotify_client()
        if sp:
            with st.spinner(f"🎵 Finding {mood} songs..."):
                try:
                    # Primary recommendation method
                    rec = sp.recommendations(
                        seed_genres=mood_config["seed_genres"][:2],
                        limit=15,
                        target_valence=sum(mood_config["valence_range"]) / 2,
                        target_energy=sum(mood_config["energy_range"]) / 2,
                        min_valence=mood_config["valence_range"][0],
                        max_valence=mood_config["valence_range"][1],
                        min_energy=mood_config["energy_range"][0],
                        max_energy=mood_config["energy_range"][1]
                    )
                    
                    # Display results
                    st.subheader(f"Your {mood} playlist {mood_config['emoji']}:")
                    cols = st.columns(2)
                    
                    for i, track in enumerate(rec["tracks"][:6]):
                        with cols[i % 2]:
                            st.write(f"#### {i+1}. {track['name']}")
                            st.write(f"**Artist**: {track['artists'][0]['name']}")
                            if track['preview_url']:
                                st.audio(track['preview_url'], format="audio/mp3")
                            st.markdown(f"[Open in Spotify]({track['external_urls']['spotify']})")
                            st.divider()
                    
                    # Save playlist
                    try:
                        playlist = sp.user_playlist_create(
                            user=sp.me()["id"],
                            name=f"{mood_config['emoji']} Moody: {mood.capitalize()} Vibes",
                            public=False,
                            description=f"Auto-generated based on mood: '{user_input}'"
                        )
                        sp.playlist_add_items(playlist["id"], [t["uri"] for t in rec["tracks"][:30]])
                        st.success(f"✅ Playlist saved to your Spotify!")
                        st.markdown(f"[🔗 Open Playlist]({playlist['external_urls']['spotify']})", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ Couldn't save playlist: {str(e)}")
                
                except Exception as e:
                    st.warning("⚠️ Using fallback search method...")
                    try:
                        results = sp.search(q=f"{mood} music", type="track", limit=15)
                        st.subheader(f"Your {mood} playlist (fallback):")
                        for i, track in enumerate(results["tracks"]["items"][:6]):
                            st.write(f"{i+1}. [{track['name']}]({track['external_urls']['spotify']}) by {track['artists'][0]['name']}")
                    except Exception as e:
                        st.error(f"❌ Fallback failed: {str(e)}")

# History sidebar
with st.sidebar:
    st.subheader("Your Mood History")
    for mood, text in reversed(st.session_state.history[-5:]):
        st.write(f"{MOOD_SETTINGS[mood]['emoji']} {text} → *{mood}*")