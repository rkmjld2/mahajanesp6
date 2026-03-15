import streamlit as st
import time
import os
from datetime import datetime

# Files (will NOT persist long-term on Streamlit Cloud!)
RELAY_FILE = "relay.txt"
HB_FILE    = "last_hb_time.txt"

# Initialize files if missing
if not os.path.exists(RELAY_FILE):
    with open(RELAY_FILE, "w") as f:
        f.write("RRRRRRRR")

if not os.path.exists(HB_FILE):
    with open(HB_FILE, "w") as f:
        f.write("0")

# ────────────────────────────────────────────────
# Handle ESP8266 requests via query params
# ESP calls:   your-app-url/?heartbeat=1
#          or: your-app-url/?read=1
# ────────────────────────────────────────────────
query_params = st.query_params

if "heartbeat" in query_params:
    now_str = str(time.time())
    with open(HB_FILE, "w") as f:
        f.write(now_str)
    # Optional: log (visible in Streamlit logs)
    print(f"Heartbeat received at {now_str} from UA: {st.context.headers.get('User-Agent', 'unknown')}")
    st.write("OK")  # ESP sees this response
    st.stop()       # End execution early

if "read" in query_params:
    try:
        with open(RELAY_FILE, "r") as f:
            content = f.read().strip()
        st.write(content)
    except:
        st.write("RRRRRRRR")
    st.stop()

# ────────────────────────────────────────────────
# Normal dashboard (browser view)
# ────────────────────────────────────────────────

st.set_page_config(page_title="ESP8266 Relay Control", layout="wide")

st.title("ESP8266 Relay Control Dashboard")

# Read current relays
try:
    with open(RELAY_FILE, "r") as f:
        relays = f.read().strip()
    if len(relays) != 8:
        relays = "RRRRRRRR"
except:
    relays = "RRRRRRRR"

# Read last heartbeat
try:
    with open(HB_FILE, "r") as f:
        last_hb_str = f.read().strip()
        last_hb = float(last_hb_str) if last_hb_str else 0.0
except:
    last_hb = 0.0

now = time.time()
age = now - last_hb
is_online = age < 15

status_text = "ONLINE" if is_online else "OFFLINE"
status_color = "green" if is_online else "red"

last_seen = f"Last seen {age:.0f} sec ago" if age >= 0 else "Never seen"

# Status indicator
st.markdown(
    f"""
    <div style="
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: {status_color};
        margin: 20px auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    "></div>
    """,
    unsafe_allow_html=True
)

st.subheader(status_text)
st.caption(last_seen)

st.markdown("---")

st.subheader("Relay Control")

# Horizontal layout with columns
cols = st.columns(4)  # 4 columns → 2 rows of 4 relays

for i in range(8):
    col = cols[i % 4]
    with col:
        state = "ON" if relays[i] == "G" else "OFF"
        state_color = "green" if state == "ON" else "red"
        
        next_s = "R" if state == "ON" else "G"
        button_text = "Turn ON" if next_s == "G" else "Turn OFF"
        
        st.markdown(f"**Relay {i+1}**")
        st.markdown(f"<span style='color:{state_color}; font-weight:bold;'>{state}</span>", unsafe_allow_html=True)
        
        if st.button(button_text, key=f"btn_{i}"):
            # Toggle
            relays_list = list(relays)
            relays_list[i] = next_s
            new_relays = "".join(relays_list)
            with open(RELAY_FILE, "w") as f:
                f.write(new_relays)
            st.success(f"Relay {i+1} set to { 'ON' if next_s=='G' else 'OFF' }")
            time.sleep(0.5)
            st.rerun()

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
