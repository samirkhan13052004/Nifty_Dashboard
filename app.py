import streamlit as st
import pyotp
from SmartApi import SmartConnect
import time

# --- पेज कॉन्फ़िगरेशन ---
st.set_page_config(page_title="Nifty50 Pro Setup", page_icon="⚡", layout="wide")

# --- ब्यूटीफुल ग्रिड UI के लिए कस्टम CSS ---
st.markdown("""
    <style>
    .grid-card { background-color: #1E1E2E; border-radius: 12px; padding: 15px; margin-bottom: 15px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2); color: white; }
    .grid-title { font-size: 14px; color: #A6ACCD; text-transform: uppercase; font-weight: bold; }
    .grid-value { font-size: 24px; font-weight: bold; margin: 5px 0; }
    .status-green { color: #00E676; font-size: 16px; font-weight: bold; }
    .status-red { color: #FF1744; font-size: 16px; font-weight: bold; }
    .status-neutral { color: #FFC400; font-size: 16px; font-weight: bold; }
    .signal-box-buy { background: linear-gradient(135deg, #00C851, #007E33); padding: 20px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px;}
    .signal-box-sell { background: linear-gradient(135deg, #ff4444, #CC0000); padding: 20px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px;}
    .signal-box-wait { background: linear-gradient(135deg, #33b5e5, #0099CC); padding: 20px; border-radius: 15px; text-align: center; color: white; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Nifty50 Pro Algorithmic Grid")

# --- सेशन स्टेट इनिशियलाइज़ेशन ---
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False

# --- साइडबार: Angel One लॉगिन फॉर्म ---
with st.sidebar:
    st.header("🔐 API Login")
    st.markdown("Enter your Angel One credentials:")
    
    # UI इनपुट्स (पासवर्ड और कीज़ को सुरक्षित रखने के लिए type="password" लगा है)
    client_id = st.text_input("Client ID")
    password = st.text_input("Pin / Password", type="password")
    api_key = st.text_input("API Key", type="password")
    totp_secret = st.text_input("TOTP Secret", type="password")
    
    login_btn = st.button("Connect to Broker")

    if login_btn:
        if client_id and password and api_key and totp_secret:
            try:
                # एंजल वन लॉगिन प्रोसेस
                smartApi = SmartConnect(api_key=api_key)
                totp = pyotp.TOTP(totp_secret).now()
                login_data = smartApi.generateSession(client_id, password, totp)
                
                if login_data['status']:
                    st.session_state['is_logged_in'] = True
                    st.success("✅ Login Successful!")
                else:
                    st.error(f"❌ Login Failed: {login_data['message']}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
        else:
            st.warning("Please fill all the details.")

# --- मुख्य स्क्रीन लॉजिक ---
if not st.session_state['is_logged_in']:
    st.info("👈 Please enter your API details in the sidebar to view the live dashboard.")
else:
    # --- डमी डेटा (इसे आप API डेटा फेच करने वाले फंक्शन से रिप्लेस करेंगे) ---
    data = {
        "ltp": 21545.80, "vix": 13.4, "pcr": 1.15, "rsi": 65, "adx": 28, 
        "supertrend": "Green", "ema_trend": "Uptrend", "vwap_status": "Above", "heavyweights": 4
    }

    # --- मास्टर सिग्नल (बड़ा अलर्ट बॉक्स) ---
    if data['supertrend'] == "Green" and data['rsi'] > 60 and data['pcr'] > 1.0:
        st.markdown(f'<div class="signal-box-buy"><h2>🟢 BUY NIFTY CE</h2><p>Entry: ₹{data["ltp"]} | SL: ₹{data["ltp"]-30} | TGT: ₹{data["ltp"]+60}</p></div>', unsafe_allow_html=True)
    elif data['supertrend'] == "Red" and data['rsi'] < 40 and data['pcr'] < 0.8:
        st.markdown(f'<div class="signal-box-sell"><h2>🔴 BUY NIFTY PE</h2><p>Entry: ₹{data["ltp"]} | SL: ₹{data["ltp"]+30} | TGT: ₹{data["ltp"]-60}</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-box-wait"><h2>🟡 SIDEWAYS MARKET</h2><p>Wait for High Probability Setup</p></div>', unsafe_allow_html=True)

    # --- सुंदर ग्रिड लेआउट (3 कॉलम्स) ---
    st.markdown("### 📊 Live Matrix")
    col1, col2, col3 = st.columns(3)

    def grid_card(title, value, status, status_class):
        return f'<div class="grid-card"><div class="grid-title">{title}</div><div class="grid-value">{value}</div><div class="{status_class}">{status}</div></div>'

    with col1:
        st.markdown(grid_card("Nifty 50 (LTP)", f"₹{data['ltp']}", "Active", "status-green"), unsafe_allow_html=True)
        st.markdown(grid_card("Supertrend", data['supertrend'], "Bullish" if data['supertrend']=="Green" else "Bearish", "status-green" if data['supertrend']=="Green" else "status-red"), unsafe_allow_html=True)
        st.markdown(grid_card("VWAP Filter", data['vwap_status'], "Price > VWAP", "status-green" if data['vwap_status']=="Above" else "status-red"), unsafe_allow_html=True)

    with col2:
        st.markdown(grid_card("RSI Momentum", data['rsi'], "Strong" if data['rsi']>60 else "Weak", "status-green" if data['rsi']>60 else "status-neutral"), unsafe_allow_html=True)
        st.markdown(grid_card("ADX Strength", data['adx'], "Trending Market" if data['adx']>25 else "Choppy", "status-green" if data['adx']>25 else "status-neutral"), unsafe_allow_html=True)
        st.markdown(grid_card("EMA 200", data['ema_trend'], "Major Trend", "status-green" if data['ema_trend']=="Uptrend" else "status-red"), unsafe_allow_html=True)

    with col3:
        st.markdown(grid_card("Put-Call Ratio (PCR)", data['pcr'], "Bullish" if data['pcr']>1.0 else "Bearish", "status-green" if data['pcr']>1.0 else "status-red"), unsafe_allow_html=True)
        st.markdown(grid_card("India VIX", data['vix'], "Options Safe" if data['vix']>12 else "Premium Decay", "status-green" if data['vix']>12 else "status-neutral"), unsafe_allow_html=True)
        st.markdown(grid_card("Heavyweights", f"{data['heavyweights']}/5", "In Sync", "status-green" if data['heavyweights']>=3 else "status-red"), unsafe_allow_html=True)

    if st.button("🔄 Refresh API Data", use_container_width=True):
        st.rerun()
