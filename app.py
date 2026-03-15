import streamlit as st
import time
import os

RELAY_FILE = "relay.txt"
HB_FILE = "last_hb_time.txt"

# Create files if missing
if not os.path.exists(RELAY_FILE):
    with open(RELAY_FILE, "w") as f:
        f.write("RRRRRRRR")

if not os.path.exists(HB_FILE):
    with open(HB_FILE, "w") as f:
        f.write("0")

params = st.query_params

# Heartbeat from ESP - check for specific value to avoid false positives
if "heartbeat" in params and params["heartbeat"][0] == "1":
    with open(HB_FILE, "w") as f:
        f.write(str(time.time()))
    st.text("OK")
    st.stop()

# ESP reading relay state
if "read" in params and params["read"][0] == "1":
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
    relays = f.read()

# Read heartbeat
with open(HB_FILE, "r") as f:
    last = float(f.read())

age = time.time() - last

if age < 30:
    st.success("ONLINE")
else:
    st.error("OFFLINE")

st.write("Last heartbeat:", int(age), "seconds ago")
