# 🎧 Moody Playlist Generator  
*"Because your music should match your meltdowns."*  

Automatically generates **Spotify playlists** based on your mood using:  
- **AI sentiment analysis** (TextBlob)  
- **Spotify API** (Spotipy)  
- **Pure chaos energy**  

![Demo GIF](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcW0yY2VkZGdlZ3BqY2R6N2JtY2VtbmV6Y2J6eGJlcW1kdmRxYmx5eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/l0HU7f8Rk7yX6i6A8/giphy.gif) *(Replace with your own GIF later!)*  

## ✨ Features  
- Detects **emotion** from text (e.g., *"I hate bugs"* → 😠 angry playlist).  
- Creates **real Spotify playlists** in your account.  
- Optional **troll mode** (adds Rick Astley if you’re too sad).  

## 🚀 Quick Start  
1. **Clone the repo**:  
   ```bash  
   git clone https://github.com/KhushiMahto6/moody-playlist.git  
   ```  
2. **Install dependencies**:  
   ```bash  
   pip install -r requirements.txt  
   ```  
3. **Add Spotify API keys**:  
   - Get keys from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).  
   - Create a `.env` file (copy `.env.example`).  
4. **Run it**:  
   ```bash  
   python moody.py  
   ```  

## 🔧 Tech Stack  
- **Python 3**  
- **Spotipy** (Spotify API wrapper)  
- **TextBlob** (NLP sentiment analysis)  

## 🌟 What’s Next?  
- [ ] Deploy as a **web app** (Flask/Next.js).  
- [ ] Add **Discord bot** integration.  
- [ ] Support for **Gen Z mood slang** (*"I'm ded 💀"* → emo playlist).  

---

Made with ❤️ + ☕ by **Your Name**  
*(Inspired by sleepless nights and bad playlists.)*  