import streamlit as st
import requests
from google import genai
from datetime import datetime

# --- 1. GLOBAL TERMINAL CONFIGURATION ---
st.set_page_config(page_title="VANTAGE GLOBAL RADAR", page_icon="🔴", layout="wide")

# --- 2. VIP SECURITY GATE (Priorytet: Bezpieczeństwo) ---
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
    st.stop()

# --- 3. SECURE API CONFIGURATION (Secrets Vault) ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    THESPORTS_USER = st.secrets["THESPORTS_USER"]
    THESPORTS_SECRET = st.secrets["THESPORTS_SECRET"]
except Exception:
    st.error("CRITICAL ERROR: API Secrets not found in Streamlit Cloud settings.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY) 

# --- 4. DATA FILTERS (Global Visibility Mode) ---
# Rozszerzone ID statusów dla Tenisa i Hokeja (1-4 to standard, 11-13 to często sety/tercje)
LIVE_STATUS_IDS = [1, 2, 3, 4, 11, 12, 13]

# --- 5. UNIVERSAL QUANT FUSION ENGINE (Bez filtrów ligowych dla testów) ---
def fetch_live_data(sport_type):
    base_url = f"https://api.thesports.com/v1/{sport_type}/match"
    params = {"user": THESPORTS_USER, "secret": THESPORTS_SECRET}
    active_matches = []
    
    try:
        # Pobieranie nazw drużyn i LIG (Diary API)
        res_diary = requests.get(f"{base_url}/diary", params=params, timeout=10).json()
        names = {t['id']: t['name'] for t in res_diary.get('results_extra', {}).get('team', [])}
        leagues = {c['id']: c['name'] for c in res_diary.get('results_extra', {}).get('competition', [])}
        
        # Pobieranie danych na żywo (Detail Live API)
        res_detail = requests.get(f"{base_url}/detail_live", params=params, timeout=10).json()
        
        for m in res_detail.get('results', []):
            if m.get('status_id') in LIVE_STATUS_IDS:
                c_name = leagues.get(m.get('competition_id'), "Global Tournament")
                h_name = names.get(m.get('home_team_id'), 'Player 1/Home')
                a_name = names.get(m.get('away_team_id'), 'Player 2/Away')
                
                # Budujemy pełny opis meczu dla AI
                match_desc = f"🏆 [{c_name}] {h_name} vs {a_name} | Score: {m.get('score')} | Stats: {m.get('stats')}"
                active_matches.append(match_desc)
        return active_matches
    except Exception as e:
        return []

# --- 6. GLOBAL USER INTERFACE ---
st.title("📡 VANTAGE LIVE RADAR | Predictive Alpha")
st.caption(f"Status: SYSTEM ONLINE | Time: {datetime.now().strftime('%H:%M:%S')} UTC")

tabs = st.tabs(["⚽ Football", "🎾 Tennis", "🏒 Ice Hockey", "🏀 Basketball"])
sports_map = [("football", "btn_f"), ("tennis", "btn_t"), ("ice_hockey", "btn_h"), ("basketball", "btn_b")]

for i, (sport, key) in enumerate(sports_map):
    with tabs[i]:
        st.subheader(f"{sport.capitalize()} Quant Scanner")
        if st.button(f"⚡ RUN {sport.upper()} SCANNER", type="primary", use_container_width=True, key=key):
            with st.spinner(f"Accessing global {sport} satellite feeds..."):
                matches = fetch_live_data(sport)
            
            if not matches:
                st.warning(f"No active {sport} matches detected globally at this moment.")
            else:
                st.success(f"Detected {len(matches)} matches. VIP AI Core analyzing value...")
                
                # Wyświetlamy listę wykrytych meczów pod przyciskiem
                for match in matches:
                    st.write(match)
                
                # Analiza AI Gemini 2.5 Pro
                st.divider()
                st.subheader("🤖 AI Green Ticket Analysis")
                prompt = f"Elite Quant Analysis: Analyze these live {sport} matches. Find mathematical value. Rule: No Unders. Focus: One 'Green Ticket' Safest Pick with highest momentum. \nData: {chr(10).join(matches)}"
                try:
                    res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.info(res.text)
                except Exception as e: 
                    st.error(f"AI Engine Offline: {e}")

st.divider()
st.caption("© 2026 VANTAGE QUANT TECHNOLOGIES | Global SaaS Model v1.3")
