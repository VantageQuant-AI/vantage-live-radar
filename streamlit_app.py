import streamlit as st
import requests
from google import genai
from datetime import datetime

# --- 1. CONFIG & SECURITY ---
st.set_page_config(page_title="VANTAGE GLOBAL RADAR", page_icon="🔴", layout="wide")

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

# --- 2. API KEYS ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    THESPORTS_USER = st.secrets["THESPORTS_USER"]
    THESPORTS_SECRET = st.secrets["THESPORTS_SECRET"]
except:
    st.error("CRITICAL: Secrets missing in Streamlit Cloud.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# --- 3. UNIVERSAL ENGINE WITH ERROR REPORTING ---
def fetch_live_data(sport_type):
    base_url = f"https://api.thesports.com/v1/{sport_type}/match"
    params = {"user": THESPORTS_USER, "secret": THESPORTS_SECRET}
    
    try:
        # Sprawdzamy połączenie - jeśli tu wywali błąd, zobaczymy go na ekranie!
        response = requests.get(f"{base_url}/detail_live", params=params, timeout=15)
        
        if response.status_code != 200:
            return [f"⚠️ API Error {response.status_code}: {response.text[:100]}"]
            
        data = response.json()
        results = data.get('results', [])
        
        if not results:
            return []

        # Pobieramy nazwy drużyn z Diary, żeby nie było "Team_ID"
        diary_res = requests.get(f"{base_url}/diary", params=params, timeout=15).json()
        teams = {t['id']: t['name'] for t in diary_res.get('results_extra', {}).get('team', [])}
        leagues = {c['id']: c['name'] for c in diary_res.get('results_extra', {}).get('competition', [])}

        active = []
        # Rozszerzone statusy: 1-9 (Piłka), 10-20 (Tenis/Inne)
        for m in results:
            if m.get('status_id') in range(1, 30): 
                c_name = leagues.get(m.get('competition_id'), "Global League")
                h_name = teams.get(m.get('home_team_id'), f"Home_{m.get('home_team_id')}")
                a_name = teams.get(m.get('away_team_id'), f"Away_{m.get('away_team_id')}")
                active.append(f"🏆 [{c_name}] {h_name} vs {a_name} | Score: {m.get('score')}")
        
        return active
    except Exception as e:
        return [f"❌ Connection Error: {str(e)}"]

# --- 4. INTERFACE ---
st.title("📡 VANTAGE LIVE RADAR | Open Satellite Feed")
st.caption(f"System: DEBUG MODE | {datetime.now().strftime('%H:%M:%S')} UTC")

# Poprawiony napis Hokej (bez podkreślnika)
sports_data = {
    "⚽ Football": "football",
    "🎾 Tennis": "tennis",
    "🏒 Ice Hockey": "ice_hockey",
    "🏀 Basketball": "basketball"
}

tabs = st.tabs(list(sports_data.keys()))

for i, (label, api_name) in enumerate(sports_data.items()):
    with tabs[i]:
        st.subheader(f"{label} Quant Scanner")
        if st.button(f"⚡ SCAN {label.upper()}", key=f"btn_{api_name}", use_container_width=True):
            with st.spinner(f"Intercepting {api_name} stream..."):
                matches = fetch_live_data(api_name)
            
            if not matches:
                st.warning(f"No active {label} matches detected globally.")
            elif "⚠️" in matches[0] or "❌" in matches[0]:
                st.error(matches[0]) # Pokazuje DOKŁADNY błąd API (np. zły adres IP)
            else:
                st.success(f"Captured {len(matches)} matches!")
                for m in matches: st.write(m)
                
                # Szybka analiza AI
                prompt = f"Elite Analysis: Find ONE best value bet from these matches. Data: {matches}"
                try:
                    res = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                    st.info(res.text)
                except Exception as e: st.error(f"AI Error: {e}")

st.divider()
st.caption("© 2026 VANTAGE QUANT TECHNOLOGIES")
