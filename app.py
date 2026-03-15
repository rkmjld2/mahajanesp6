import streamlit as st
import time
import os

RELAY_FILE = "relay.txt"
HB_FILE = "last_hb_time.txt"
PING_FILE = "ping.txt"  # ESP creates this file

# Create files if missing
for f in [RELAY_FILE, HB_FILE, PING_FILE]:
    if not os.path.exists(f):
        with open(f, "w") as file:
            if f == RELAY_FILE:
                file.write("RRRRRRRR")
            elif f == HB_FILE:
                file.write("0")
            else:
                file.write("")

params = st.query_params

# Simple ping detection - ESP just needs to create a file
if os.path.exists(PING_FILE) and os.path.getmtime(PING_FILE) > time.time() - 1:
    os.remove(PING_FILE)
    with open(HB_FILE, "w") as f:
        f.write(str(time.time()))
    st.text("OK")
    st.stop()

# ESP reading relay state
if "read" in params:
    try:
        with open(RELAY_FILE, "r") as f:
            data = f.read()
    except:
        data = "RRRRRRRR"
    st.text(data)
    st.stop()

# Dashboard
st.title("ESP8266 Relay Control")

# Read relay state
with open(RELAY_FILE, "r") as f:
    relays = f.read().ljust(8)[:8]

# Read heartbeat
with open(HB_FILE, "r") as f:
    last = float(f.read())

age = time.time() - last

if age < 30:
    st.success("🟢 ONLINE")
else:
    st.error("🔴 OFFLINE")

st.write(f"**Last heartbeat:** {int(age)} seconds ago")

# Relay display
cols = st.columns(8)
for i in range(8):
    status = "ON" if relays[i] == 'G' else "OFF"
    with cols[i]:
        st.metric(f"R{i+1}", status)

# Manual control
new_state = st.text_input("Relay state (RRRRRRRR/G mix)", value=relays)
if st.button("Update"):
    with open(RELAY_FILE, "w") as f:
        f.write(new_state[:8].upper())
    st.success("Updated!")
    st.rerun()
