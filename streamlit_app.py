import streamlit as st
import requests
from google import genai
import time
from datetime import datetime

# --- 1. GLOBAL TERMINAL CONFIGURATION ---
st.set_page_config(
    page_title="VANTAGE QUANT AI | Live Radar", 
    page_icon="🔴", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. VIP SECURITY GATE (Full English) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🔴 VANTAGE QUANT AI</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #ffffff;'>Restricted Access Terminal</h3>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Enter VIP Access Code:", type="password")
        if st.button("Unlock Terminal 🔓", use_container_width=True):
            if password == "VANTAGE-VIP":
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED. Invalid credentials.")
    st.stop() #

# --- 3. SECURE API CONFIGURATION (Secrets Vault) ---
try:
    GEMINI_API_KEY = st.secrets["AIzaSyAnIn8rijiJqEdR3FrweiLwbaLY1uZ6Lts"]
    THESPORTS_USER = st.secrets["theyzhaso"]
    THESPORTS_SECRET = st.secrets["4e8d37d123ec79adbf295e3f98b8dffd"]
except Exception:
    st.error("CRITICAL ERROR: API Secrets not found in Streamlit Cloud settings.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY) 

# --- 4. DATA FILTERS (Bug Fix for Yesterday's matches) ---
# Status IDs 1-4: 1st Half, HT, 2nd Half, ET. Everything else is ignored.
LIVE_STATUS_IDS = [1, 2, 3, 4]

ALLOWED_LEAGUE_KEYWORDS = [
    "UEFA", "Champions", "Europa", "Premier League", "LaLiga", "Serie A", "Bundesliga", "Ligue 1", "Ekstraklasa"
]

# --- 5. QUANT FUSION ENGINES (Merged Logic from VANTAGE QUANT AI.py) ---

def fetch_live_data(sport_type):
    """Universal fusion engine for Football, Tennis, Hockey, and Basketball."""
    base_url = f"https://api.thesports.com/v1/{sport_type}/match"
    params = {"user": THESPORTS_USER, "secret": THESPORTS_SECRET}
    active_matches = []
    
    try:
        # Fetch team/player names
        res_diary = requests.get(f"{base_url}/diary", params=params, timeout=10).json()
        names = {t['id']: t['name'] for t in res_diary.get('results_extra', {}).get('team', [])}
        
        # Fetch live data and apply Status Filter
        res_detail = requests.get(f"{base_url}/detail_live", params=params, timeout=10).json()
        for m in res_detail.get('results', []):
            if m.get('status_id') in LIVE_STATUS_IDS:
                h_name = names.get(m.get('home_team_id'), 'Home')
                a_name = names.get(m.get('away_team_id'), 'Away')
                active_matches.append(f"{h_name} vs {a_name} | Score: {m.get('score')} | Stats: {m.get('stats')}")
        return active_matches
    except: return []

# --- 6. GLOBAL USER INTERFACE (Full English) ---
st.title("📡 VANTAGE LIVE RADAR | Predictive Alpha")
st.caption(f"Status: SYSTEM ONLINE | Boot Time: {datetime.now().strftime('%H:%M:%S')} UTC")
st.success("✅ VIP Verification Successful. Welcome to VANTAGE Terminal.")

tabs = st.tabs(["⚽ Football", "🎾 Tennis", "🏒 Ice Hockey", "🏀 Basketball"])

# Logic for all tabs
sports = [("football", "btn_f"), ("tennis", "btn_t"), ("ice_hockey", "btn_h"), ("basketball", "btn_b")]

for i, (sport, key) in enumerate(sports):
    with tabs[i]:
        st.subheader(f"{sport.capitalize()} Quant Scanner")
        if st.button(f"⚡ RUN {sport.upper()} SCANNER", type="primary", use_container_width=True, key=key):
            with st.spinner(f"Connecting to live {sport} databases..."):
                matches = fetch_live_data(sport)
            
            if not matches:
                st.warning(f"No active {sport} matches found in tracked leagues.")
            else:
                st.success(f"Analyzed {len(matches)} matches. VIP AI Core taking control...")
                prompt = f"Elite Quant Analysis Request: Analyze these {sport} matches for mathematical value. Rule: No Unders. Focus: Green Ticket Safest Pick. \nData: {chr(10).join(matches)}"
                try:
                    res = client.models.generate_content(model='gemini-2.5-pro', contents=prompt)
                    st.markdown(res.text)
                except Exception as e: st.error(f"AI Engine Offline: {e}")

st.divider()
st.caption("© 2026 VANTAGE QUANT TECHNOLOGIES | Global SaaS Model v1.2")
