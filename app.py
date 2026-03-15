import streamlit as st
import time
import os
from streamlit.runtime.scriptrunner import get_script_run_ctx

RELAY_FILE = "relay.txt"
HB_FILE = "last_hb_time.txt"

# Create files if missing
if not os.path.exists(RELAY_FILE):
    with open(RELAY_FILE, "w") as f:
        f.write("RRRRRRRR")

if not os.path.exists(HB_FILE):
    with open(HB_FILE, "w") as f:
        f.write("0")

# Get request headers to detect ESP requests
ctx = get_script_run_ctx()
is_esp_request = False
request_type = ""

if ctx and hasattr(ctx.session_state, '_session_info') and ctx.session_state._session_info.ws:
    try:
        headers = dict(ctx.session_state._session_info.ws.request.headers)
        user_agent = headers.get('user-agent', '').lower()
        
        if 'esp-heartbeat' in user_agent:
            is_esp_request = True
            request_type = "heartbeat"
        elif 'esp-read' in user_agent:
            is_esp_request = True
            request_type = "read"
    except:
        pass

# Handle ESP heartbeat
if is_esp_request and request_type == "heartbeat":
    with open(HB_FILE, "w") as f:
        f.write(str(time.time()))
    st.text("OK")
    st.stop()

# Handle ESP reading relay state
if is_esp_request and request_type == "read":
    try:
        with open(RELAY_FILE, "r") as f:
            data = f.read()
    except:
        data = "RRRRRRRR"
    st.text(data)
    st.stop()

# Dashboard UI (only shown for browser requests)
st.title("ESP8266 Relay Control")

# Read relay state
with open(RELAY_FILE, "r") as f:
    relays = f.read().ljust(8)[:8]  # Ensure exactly 8 chars

# Read heartbeat
with open(HB_FILE, "r") as f:
    last = float(f.read())

age = time.time() - last

if age < 30:
    st.success("🟢 ONLINE")
else:
    st.error("🔴 OFFLINE")

st.write(f"**Last heartbeat:** {int(age)} seconds ago")

# Relay status display
st.subheader("Relay Status")
cols = st.columns(8)
for i in range(8):
    status = "ON" if relays[i] == 'G' else "OFF"
    color = "green" if relays[i] == 'G' else "red"
    with cols[i]:
        st.metric(f"R{i+1}", status, delta=None, delta_color=color)

# Manual relay control (optional)
st.subheader("Manual Control")
new_relays = st.text_input("Relay state (8 chars, G=ON, R=OFF)", value=relays)
if st.button("Update Relays"):
    with open(RELAY_FILE, "w") as f:
        f.write(new_relays[:8].upper())
    st.success("Relay state updated!")
    st.rerun()
