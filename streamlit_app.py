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

# --- 2. API SECRETS ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    THESPORTS_USER = st.secrets["THESPORTS_USER"]
    THESPORTS_SECRET = st.secrets["THESPORTS_SECRET"]
except Exception:
    st.error("CRITICAL: Secrets missing. Upewnij się, że na serwerze VPS masz plik .streamlit/secrets.toml")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# --- 3. HARDCORE DEBUG FUSION ENGINE ---

# CACHE: Zapamiętujemy nazwy lig i drużyn na 1 godzinę (3600 sekund), żeby nie zajechać limitów API
@st.cache_data(ttl=3600)
def fetch_dictionaries(sport_type, _params):
    base_url = f"https://api.thesports.com/v1/{sport_type}/match"
    try:
        diary_res = requests.get(f"{base_url}/diary", params=_params, timeout=10).json()
        teams = {t['id']: t['name'] for t in diary_res.get('results_extra', {}).get('team', [])}
        leagues = {c['id']: c['name'] for c in diary_res.get('results_extra', {}).get('competition', [])}
        return teams, leagues
    except:
        return {}, {}

def fetch_live_data(sport_type):
    base_url = f"https://api.thesports.com/v1/{sport_type}/match"
    params = {"user": THESPORTS_USER, "secret": THESPORTS_SECRET}
    
    try:
        # PING 1: Uderzamy o dane na żywo
        response = requests.get(f"{base_url}/detail_live", params=params, timeout=15)
        
        if response.status_code != 200:
            return [f"⚠️ HTTP FATAL {response.status_code}: {response.text}"]
            
        data = response.json()
        
        # DEMASKOWANIE API
        if isinstance(data, dict) and data.get('results') is None:
            return [f"🚨 API BLOCKED/ERROR. RAW SERVER MESSAGE: {str(data)}"]
            
        results = data.get('results', [])
        
        if len(results) == 0:
            return [f"📭 API IS EMPTY. Serwer TheSports twierdzi, że nie ma ANI JEDNEGO meczu {sport_type}. RAW: {str(data)[:100]}"]

        # PING 2: Bezpieczne pobieranie nazw z CACHE (Ultra szybkie!)
        teams, leagues = fetch_dictionaries(sport_type, params)

        active = []
        for m in results:
            c_name = leagues.get(m.get('competition_id'), f"League_{m.get('competition_id')}")
            h_name = teams.get(m.get('home_team_id'), f"Home_{m.get('home_team_id')}")
            a_name = teams.get(m.get('away_team_id'), f"Away_{m.get('away_team_id')}")
            status = m.get('status_id', 'N/A')
            
            active.append(f"🏆 [{c_name}] {h_name} vs {a_name} | Score: {m.get('score')} | Status_ID: {status}")
        
        return active
    except Exception as e:
        return [f"❌ PYTHON CRASH: {str(e)}"]

# --- 4. GLOBAL INTERFACE ---
st.title("📡 VANTAGE LIVE RADAR | VPS Edition")
st.caption(f"System: MAXIMUM OVERDRIVE | {datetime.now().strftime('%H:%M:%S')} UTC")

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
        if st.button(f"⚡ FORCE SCAN {label.upper()}", key=f"btn_{api_name}", use_container_width=True):
            with st.spinner(f"Hacking into {api_name} stream..."):
                matches = fetch_live_data(api_name)
            
            if matches and any(warn in matches[0] for warn in ["⚠️", "🚨", "📭", "❌"]):
                st.error(f"SYSTEM ALERT:\n{matches[0]}")
            elif not matches:
                st.warning("No matches found (Błąd krytyczny logiki).")
            else:
                st.success(f"Captured {len(matches)} raw signals!")
                for m in matches: st.write(m)
                
                st.divider()
                st.subheader("🤖 AI Rapid Scan")
                try:
                    # Model zaktualizowany do wariantu Pro zgodnie z Twoim zaleceniem
                    res = client.models.generate_content(model='gemini-2.5-pro', contents=f"Find the highest probability value in this data. Data: {matches}")
                    st.info(res.text)
                except Exception as e: st.error(f"AI Offline: {e}")

st.divider()
st.caption("© 2026 VANTAGE QUANT TECHNOLOGIES | V2.0 VPS Edition")
