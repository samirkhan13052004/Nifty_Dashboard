import streamlit as st
import random

# --- पेज सेटिंग (मोबाइल के लिए ऑप्टिमाइज्ड) ---
st.set_page_config(page_title="Nifty50 Algo", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .big-font { font-size:18px !important; font-weight: bold; }
    .signal-buy { color: #00C851; font-size: 26px; font-weight: bold; text-align: center; padding: 10px; border-radius: 10px; background-color: rgba(0, 200, 81, 0.1); }
    .signal-sell { color: #ff4444; font-size: 26px; font-weight: bold; text-align: center; padding: 10px; border-radius: 10px; background-color: rgba(255, 68, 68, 0.1); }
    .signal-wait { color: #ffbb33; font-size: 26px; font-weight: bold; text-align: center; padding: 10px; border-radius: 10px; background-color: rgba(255, 187, 51, 0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Nifty50 Auto-Setup")
st.markdown("12-Layer Institutional Filter Dashboard")
st.divider()

# --- लाइव डेटा (जब तक API नहीं लगती, यह सिस्टम को टेस्ट करने के लिए है) ---
def fetch_live_market_data():
    return {
        "Nifty_LTP": 21540.50,
        "BankNifty_Trend": random.choice(["Bullish", "Bearish"]),
        "India_VIX": round(random.uniform(10.5, 15.5), 2),
        "PCR": round(random.uniform(0.6, 1.4), 2),
        "Supertrend": random.choice(["Green", "Red"]),
        "RSI": random.randint(35, 75),
        "ADX": random.randint(15, 35),
        "Price_vs_VWAP": random.choice(["Above", "Below"]),
        "Price_vs_EMA200": "Above",
        "Wick_Rejection": "No",
        "Heavyweights_Green": random.randint(1, 5)
    }

data = fetch_live_market_data()

# --- टॉप पैनल (LTP, VIX, PCR) ---
c1, c2, c3 = st.columns(3)
with c1: st.metric("Nifty 50", f"₹{data['Nifty_LTP']}")
with c2: st.metric("India VIX", data['India_VIX'])
with c3: st.metric("PCR", data['PCR'])

st.divider()

# --- मास्टर सिग्नल लॉजिक ---
# यहाँ हम जानबूझकर डमी सिग्नल को ट्रिगर कर रहे हैं ताकि आप UI देख सकें 
# (लाइव में यह इंडिकेटर्स की वैल्यू पर काम करेगा)
if data['Supertrend'] == "Green" and data['RSI'] > 50 and data['PCR'] > 1.0:
    st.markdown('<p class="signal-buy">🟢 BUY CALL (CE)</p>', unsafe_allow_html=True)
    entry = data['Nifty_LTP']
    sl = entry - 25
    tgt = entry + 50
elif data['Supertrend'] == "Red" and data['RSI'] < 50 and data['PCR'] < 1.0:
    st.markdown('<p class="signal-sell">🔴 BUY PUT (PE)</p>', unsafe_allow_html=True)
    entry = data['Nifty_LTP']
    sl = entry + 25
    tgt = entry - 50
else:
    st.markdown('<p class="signal-wait">🟡 NO TRADE (Sideways)</p>', unsafe_allow_html=True)
    entry, sl, tgt = 0, 0, 0

# --- एंट्री, स्टॉप-लॉस और टारगेट प्राइस ---
if entry != 0:
    st.subheader("🎯 Trade Levels")
    tc1, tc2, tc3 = st.columns(3)
    tc1.success(f"**ENTRY:** ₹{entry}")
    tc2.error(f"**SL:** ₹{sl}")
    tc3.info(f"**TARGET:** ₹{tgt}")

st.divider()

# --- 12-Layer Filter Checklist (मोबाइल व्यू के लिए सेट किया गया) ---
st.subheader("🛡️ Live Filter Status")

def status(condition, good, bad):
    return f"✅ {good}" if condition else f"❌ {bad}"

with st.expander("📊 Technical Indicators", expanded=True):
    st.write(status(data['Supertrend'] == "Green", "Supertrend Green", "Supertrend Red"))
    st.write(status(data['Price_vs_VWAP'] == "Above", "Price > VWAP", "Price < VWAP"))
    st.write(status(data['Price_vs_EMA200'] == "Above", "Uptrend (EMA200)", "Downtrend"))
    st.write(status(data['RSI'] > 60 or data['RSI'] < 40, f"RSI Momentum ({data['RSI']})", f"RSI Choppy ({data['RSI']})"))

with st.expander("🛡️ Smart Money & Options", expanded=True):
    st.write(status(data['PCR'] > 1.0 or data['PCR'] < 0.8, f"PCR Directional ({data['PCR']})", f"PCR Neutral ({data['PCR']})"))
    st.write(status(data['ADX'] > 25, f"ADX Strong ({data['ADX']})", f"ADX Weak/Sideways ({data['ADX']})"))
    st.write(status(data['Wick_Rejection'] == "No", "No Wick Trap", "Candle Wick Trap!"))

with st.expander("🌐 Macro & Sync Filters", expanded=True):
    st.write(status(data['BankNifty_Trend'] == "Bullish", "BankNifty in Sync", "BankNifty Diverging"))
    st.write(status(data['India_VIX'] > 12, f"VIX OK ({data['India_VIX']})", f"VIX Low ({data['India_VIX']})"))
    st.write(status(data['Heavyweights_Green'] >= 3, f"{data['Heavyweights_Green']}/5 Heavyweights +ve", "Heavyweights Weak"))

st.divider()
if st.button("🔄 Refresh Data (Tap Here)", use_container_width=True):
    st.rerun()
