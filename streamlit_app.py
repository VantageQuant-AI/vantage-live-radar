import streamlit as st
import requests
from google import genai
import time
from datetime import datetime

# --- 1. TERMINAL CONFIGURATION ---
st.set_page_config(
    page_title="VANTAGE QUANT AI | Global Live Radar", 
    page_icon="🔴", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. VIP SECURITY GATE (Authentication) ---
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
                st.error("ACCESS DENIED. Invalid Credentials.")
    st.stop()

# --- 3. SECURE API CONFIGURATION (Using Secrets) ---
# Ensure these are set in Streamlit Cloud Dashboard -> Settings -> Secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    THESPORTS_USER = st.secrets["THESPORTS_USER"]
    THESPORTS_SECRET = st.secrets["THESPORTS_SECRET"]
except Exception:
    st.error("CRITICAL ERROR: API Secrets not found. Please configure Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY) 

# --- 4. LIVE STATUS FILTER (Bug Fix for "Yesterday's Matches") ---
# Status IDs 1-4 typically represent: 1: 1st Half, 2: HT, 3: 2nd Half, 4: ET
LIVE_STATUS_IDS = [1, 2, 3, 4]

# --- 5. DATA FUSION ENGINES ---

def fetch_football_data():
    url_diary = "https://api.thesports.com/v1/football/match/diary"
    url_detail = "https://api.thesports.com/v1/football/match/detail_live"
    params = {"user": THESPORTS_USER, "secret": THESPORTS_SECRET}
    
    active_matches = []
    try:
        # Fetch names from diary
        res_diary = requests.get(url_diary, params=params, timeout=10).json()
        teams = {t['id']: t['name'] for t in res_diary.get('results_extra', {}).get('team', [])}
        
        # Fetch live data and filter strictly by status
        res_detail = requests.get(url_detail, params=params, timeout=10).json()
        for m in res_detail.get('results', []):
            if m.get('status_id') in LIVE_STATUS_IDS:
                name = f"{teams.get(m.get('home_team_id'), 'Home')} vs {teams.get(m.get('away_team_id'), 'Away')}"
                active_matches.append(f"⚽ {name} | Score: {m.get('score')} | Stats: {m.get('stats')}")
        return active_matches
    except: return []

# (Functions for Tennis, Hockey, and Basketball would follow the same status-filtering logic)

# --- 6. GLOBAL USER INTERFACE ---
st.title("📡 VANTAGE LIVE RADAR | Predictive Alpha")
st.caption(f"Status: SYSTEM ONLINE | Boot Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
st.success("✅ VIP Verification Successful. Welcome to VANTAGE Terminal.")

tab_f, tab_t, tab_h, tab_b = st.tabs(["⚽ Football", "🎾 Tennis", "🏒 Ice Hockey", "🏀 Basketball"])

with tab_f:
    st.subheader("⚽ Football Scanner (Quant AI Core 2.5 Pro)")
    if st.button("⚡ RUN LIVE FOOTBALL SCAN", type="primary", use_container_width=True):
        with st.spinner("Aggregating live momentum and market asymmetries..."):
            matches = fetch_football_data()
        
        if not matches:
            st.warning("No active matches found. System is monitoring for the next kick-off.")
        else:
            prompt = f"Elite Quant Analysis Request: Filter these matches for mathematical value. Rule: No Unders. Focus: Green Ticket Safest Pick. \nData: {chr(10).join(matches)}"
            try:
                response = client.models.generate_content(model='gemini-2.5-pro', contents=prompt)
                st.markdown(response.text)
            except Exception as e: st.error(f"AI Engine Offline: {e}")

st.divider()
st.caption("© 2026 VANTAGE QUANT TECHNOLOGIES | Global SaaS Model v1.2")
