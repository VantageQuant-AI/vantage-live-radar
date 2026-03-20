import streamlit as st
import requests
from google import genai
from datetime import datetime

# --- 1. GLOBAL TERMINAL CONFIGURATION ---
st.set_page_config(page_title="VANTAGE GLOBAL RADAR", page_icon="🔴", layout="wide")

# --- 2. VIP SECURITY GATE (Security Priority) ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🔴 VANTAGE QUANT AI</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Enter VIP Access Code:", type="password")
        if st.button("Unlock Terminal 🔓", use_container_width=True):
            if password == "VANTAGE-VIP":
                st.session_state['authenticated'] = True
                st.rerun()
            else: st.error("ACCESS DENIED.")
    st.stop()

# --- 3. SECURE API CONFIGURATION (Secrets Vault) ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    THESPORTS_USER = st.secrets["THESPORTS_USER"]
    THESPORTS_SECRET = st.secrets["THESPORTS_SECRET"]
except Exception:
    st.error("CRITICAL ERROR: API Secrets missing.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY) 

# --- 4. UNIVERSAL OPEN ENGINE (No Filters Mode) ---
def fetch_all_live_data(sport_type):
    base_url = f"https://api.thesports.com/v1/{sport_type}/match"
    params = {"user": THESPORTS_USER, "secret": THESPORTS_SECRET}
    
    try:
        # 1. Pobieramy nazwy (Diary)
        res_diary = requests.get(f"{base_url}/diary", params=params, timeout=10).json()
        teams = {t['id']: t['name'] for t in res_diary.get('results_extra', {}).get('team', [])}
        competitions = {c['id']: c['name'] for c in res_diary.get('results_extra', {}).get('competition', [])}
        
        # 2. Pobieramy dane LIVE
        res_live = requests.get(f"{base_url}/detail_live", params=params, timeout=10).json()
        
        found_matches = []
        for m in res_live.get('results', []):
            # Akceptujemy KAŻDY status, który nie jest końcem meczu (Statusy 1-13)
            if m.get('status_id') in [1, 2, 3, 4, 11, 12, 13]:
                c_name = competitions.get(m.get('competition_id'), "Global League")
                h_name = teams.get(m.get('home_team_id'), f"Team_{m.get('home_team_id')}")
                a_name = teams.get(m.get('away_team_id'), f"Team_{m.get('away_team_id')}")
                score = m.get('score', '0-0')
                
                # Budujemy opis dla AI i użytkownika
                match_entry = f"🏆 [{c_name}] {h_name} vs {a_name} | Score: {score} | Stats: {m.get('stats')}"
                found_matches.append(match_entry)
        
        return found_matches
    except: return []

# --- 5. GLOBAL USER INTERFACE ---
st.title("📡 VANTAGE LIVE RADAR | Open Satellite Feed")
st.caption(f"Status: GLOBAL SCAN MODE | {datetime.now().strftime('%H:%M:%S')} UTC")

# Poprawione etykiety (Hokej bez podkreślnika!)
tabs = st.tabs(["⚽ Football", "🎾 Tennis", "🏒 Ice Hockey", "🏀 Basketball"])
sports_config = [
    ("football", "btn_f", 0), 
    ("tennis", "btn_t", 1), 
    ("ice_hockey", "btn_h", 2), 
    ("basketball", "btn_b", 3)
]

for api_name, btn_key, tab_idx in sports_config:
    with tabs[tab_idx]:
        # Naprawa napisu dla hokeja
        display_name = api_name.replace("_", " ").capitalize()
        st.subheader(f"{display_name} Quant Scanner")
        
        if st.button(f"⚡ RUN {display_name.upper()} SCANNER", type="primary", use_container_width=True, key=btn_key):
            with st.spinner(f"Intercepting {api_name} data streams..."):
                matches = fetch_all_live_data(api_name)
            
            if not matches:
                st.warning(f"No active {display_name} matches found in the entire global API.")
            else:
                st.success(f"Captured {len(matches)} live matches! Analyzing for VIP Value...")
                
                # Lista meczów pod przyciskiem
                for match in matches:
                    st.write(match)
                
                # Analiza AI
                st.divider()
                st.subheader("🤖 AI Value Analysis (Green Ticket)")
                prompt = f"Analyze these {display_name} live matches. Rule: No Unders. Rule: Find ONE Safest Pick (Green Ticket) based on momentum. Data: {chr(10).join(matches)}"
                try:
                    res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.info(res.text)
                except Exception as e: st.error(f"AI Core Error: {e}")

st.divider()
st.caption("© 2026 VANTAGE QUANT TECHNOLOGIES | Version: OPEN_RADAR_v1.3")
