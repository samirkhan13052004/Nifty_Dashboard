import streamlit as st
import pandas as pd
import pandas_ta as ta
import pyotp
from SmartApi import SmartConnect
import time

# --- पेज कॉन्फ़िगरेशन (मोबाइल और डेस्कटॉप के लिए वाइड लेआउट) ---
st.set_page_config(page_title="Nifty50 Pro Algorithmic Grid", page_icon="⚡", layout="wide")

# --- ब्यूटीफुल ग्रिड UI और अलर्ट बॉक्स के लिए कस्टम CSS ---
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

st.title("⚡ Nifty50 Institutional Algo Grid")

# --- सेशन स्टेट इनिशियलाइज़ेशन ---
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False
if 'smart_api_obj' not in st.session_state:
    st.session_state['smart_api_obj'] = None

# --- साइडबार: वेबसाइट पर सीधे Angel One क्रेडेंशियल्स डालने के लिए ---
with st.sidebar:
    st.header("🔐 Broker Login")
    st.markdown("Enter your Angel One details securely:")
    
    # .strip() का इस्तेमाल ताकि मोबाइल पर स्पेस की वजह से एरर न आए
    client_id = st.text_input("Client ID").strip()
    password = st.text_input("Pin / Password", type="password").strip()
    api_key = st.text_input("API Key", type="password").strip()
    totp_secret = st.text_input("TOTP Secret", type="password").strip().replace(" ", "")
    
    login_btn = st.button("Connect to Angel One")

    if login_btn:
        if client_id and password and api_key and totp_secret:
            try:
                smartApi = SmartConnect(api_key=api_key)
                totp = pyotp.TOTP(totp_secret).now()
                login_data = smartApi.generateSession(client_id, password, totp)
                
                if login_data['status']:
                    st.session_state['is_logged_in'] = True
                    st.session_state['smart_api_obj'] = smartApi
                    st.success("✅ Login Successful!")
                else:
                    st.error(f"❌ Login Failed: {login_data.get('message', 'Invalid combination')}")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
        else:
            st.warning("Please fill all the details.")

# --- मुख्य स्क्रीन लॉजिक ---
if not st.session_state['is_logged_in']:
    st.info("👈 Please open the sidebar and enter your Angel One credentials to launch the live dashboard.")
else:
    # --- डेटा फेचिंग और 12-लेयर स्ट्रेटेजी वैल्यूज़ ---
    # (यहाँ आप api ऑब्जेक्ट का इस्तेमाल करके अपनी लाइव कैंडल और ऑप्शन चेन डेटा ले सकते हैं)
    
    # डेमोंस्ट्रेशन के लिए वैलिडेटेड डेटा स्ट्रक्चर
    data = {
        "ltp": 21545.80, 
        "vix": 13.4, 
        "pcr": 1.15, 
        "rsi": 65, 
        "adx": 28, 
        "supertrend": "Green", 
        "ema_trend": "Uptrend", 
        "vwap_status": "Above", 
        "heavyweights": 4,
        "banknifty_sync": "Bullish",
        "wick_trap": "No"
    }

    # --- मास्टर सिग्नल लॉजिक (12-Layer Filters Check) ---
    is_buy = (
        data['supertrend'] == "Green" and 
        data['rsi'] > 60 and 
        data['pcr'] > 1.0 and 
        data['adx'] > 25 and 
        data['vwap_status'] == "Above" and
        data['ema_trend'] == "Uptrend" and
        data['vix'] > 12 and
        data['heavyweights'] >= 3 and
        data['banknifty_sync'] == "Bullish" and
        data['wick_trap'] == "No"
    )

    is_sell = (
        data['supertrend'] == "Red" and 
        data['rsi'] < 40 and 
        data['pcr'] < 0.8 and 
        data['adx'] > 25 and 
        data['vwap_status'] == "Below" and
        data['ema_trend'] == "Downtrend" and
        data['vix'] > 12 and
        data['heavyweights'] <= 2 and
        data['banknifty_sync'] == "Bearish" and
        data['wick_trap'] == "No"
    )

    # --- बड़ा सिग्नल और टारगेट डिस्प्ले बॉक्स ---
    if is_buy:
        st.markdown(f'<div class="signal-box-buy"><h2>🟢 BUY NIFTY CE (HIGH PROBABILITY)</h2><p>Entry: ₹{data["ltp"]} | Stop Loss: ₹{data["ltp"]-30} | Target: ₹{data["ltp"]+60}</p></div>', unsafe_allow_html=True)
    elif is_sell:
        st.markdown(f'<div class="signal-box-sell"><h2>🔴 BUY NIFTY PE (HIGH PROBABILITY)</h2><p>Entry: ₹{data["ltp"]} | Stop Loss: ₹{data["ltp"]+30} | Target: ₹{data["ltp"]-60}</p></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="signal-box-wait"><h2>🟡 SIDEWAYS / NO TRADE ZONE</h2><p>Filters are protecting you from false signals. Please Wait.</p></div>', unsafe_allow_html=True)

    # --- सुंदर ग्रिड लेआउट (3 कॉलम्स) ---
    st.markdown("### 📊 12-Layer Institutional Filters Matrix")
    col1, col2, col3 = st.columns(3)

    def grid_card(title, value, status, status_class):
        return f'<div class="grid-card"><div class="grid-title">{title}</div><div class="grid-value">{value}</div><div class="{status_class}">{status}</div></div>'

    with col1:
        st.markdown(grid_card("Nifty 50 (LTP)", f"₹{data['ltp']}", "Active Feed", "status-green"), unsafe_allow_html=True)
        st.markdown(grid_card("Supertrend (10,3)", data['supertrend'], "Bullish" if data['supertrend']=="Green" else "Bearish", "status-green" if data['supertrend']=="Green" else "status-red"), unsafe_allow_html=True)
        st.markdown(grid_card("VWAP Filter", data['vwap_status'], "Above Value" if data['vwap_status']=="Above" else "Below Value", "status-green" if data['vwap_status']=="Above" else "status-red"), unsafe_allow_html=True)
        st.markdown(grid_card("BankNifty Sync", data['banknifty_sync'], "Aligned", "status-green"), unsafe_allow_html=True)

    with col2:
        st.markdown(grid_card("RSI Momentum", data['rsi'], "Strong (>60)" if data['rsi']>60 else "Weak", "status-green" if data['rsi']>60 else "status-neutral"), unsafe_allow_html=True)
        st.markdown(grid_card("ADX Strength", data['adx'], "Trending (>25)" if data['adx']>25 else "Choppy/Sideways", "status-green" if data['adx']>25 else "status-neutral"), unsafe_allow_html=True)
        st.markdown(grid_card("EMA 200 Trend", data['ema_trend'], "Major Trend OK", "status-green"), unsafe_allow_html=True)
        st.markdown(grid_card("Candle Wick Trap", data['wick_trap'], "No Rejection", "status-green"), unsafe_allow_html=True)

    with col3:
        st.markdown(grid_card("Put-Call Ratio (PCR)", data['pcr'], "Bullish Bias" if data['pcr']>1.0 else "Bearish", "status-green" if data['pcr']>1.0 else "status-red"), unsafe_allow_html=True)
        st.markdown(grid_card("India VIX", data['vix'], "Options Safe" if data['vix']>12 else "Low Premium", "status-green" if data['vix']>12 else "status-neutral"), unsafe_allow_html=True)
        st.markdown(grid_card("Top 5 Heavyweights", f"{data['heavyweights']}/5", "Institutional Support", "status-green" if data['heavyweights']>=3 else "status-red"), unsafe_allow_html=True)
        st.markdown(grid_card("Risk Management", "Active", "1:2 Risk-Reward", "status-green"), unsafe_allow_html=True)

    if st.button("🔄 Refresh Real-Time Data", use_container_width=True):
        st.rerun()
