import streamlit as st
import time
import os

# ------------------------------
# Files (temporary on Streamlit)
# ------------------------------
RELAY_FILE = "relay.txt"
HB_FILE = "last_hb_time.txt"

# ------------------------------
# Initialize files if missing
# ------------------------------
def init_files():
    if not os.path.exists(RELAY_FILE):
        with open(RELAY_FILE, "w") as f:
            f.write("RRRRRRRR")

    if not os.path.exists(HB_FILE):
        with open(HB_FILE, "w") as f:
            f.write("0")

init_files()

# ------------------------------
# Query parameters from ESP
# ------------------------------
params = st.query_params

# ESP heartbeat
if "heartbeat" in params:
    now = str(time.time())
    with open(HB_FILE, "w") as f:
        f.write(now)

    st.text("OK")
    st.stop()

# ESP reading relay states
if "read" in params:
    try:
        with open(RELAY_FILE, "r") as f:
            data = f.read().strip()
            if len(data) != 8:
                data = "RRRRRRRR"
    except:
        data = "RRRRRRRR"

    st.text(data)
    st.stop()

# ------------------------------
# Dashboard UI
# ------------------------------
st.set_page_config(page_title="ESP8266 Relay Control", layout="wide")

st.title("ESP8266 Relay Control Dashboard")

# ------------------------------
# Read relay state
# ------------------------------
try:
    with open(RELAY_FILE, "r") as f:
        relays = f.read().strip()
        if len(relays) != 8:
            relays = "RRRRRRRR"
except:
    relays = "RRRRRRRR"

# ------------------------------
# Read heartbeat
# ------------------------------
try:
    with open(HB_FILE, "r") as f:
        last_hb = float(f.read().strip())
except:
    last_hb = 0

age = time.time() - last_hb

is_online = age < 20

status_text = "ONLINE" if is_online else "OFFLINE"
status_color = "green" if is_online else "red"

# ------------------------------
# Status indicator
# ------------------------------
st.markdown(
    f"""
    <div style="
        width:140px;
        height:140px;
        border-radius:50%;
        background:{status_color};
        margin:auto;
    "></div>
    """,
    unsafe_allow_html=True
)

st.subheader(status_text)
st.caption(f"Last heartbeat {int(age)} sec ago")

st.markdown("---")

# ------------------------------
# Relay Controls
# ------------------------------
st.subheader("Relay Control")

cols = st.columns(4)

for i in range(8):

    col = cols[i % 4]

    with col:

        state = "ON" if relays[i] == "G" else "OFF"
        color = "green" if state == "ON" else "red"

        next_state = "R" if relays[i] == "G" else "G"

        st.markdown(f"### Relay {i+1}")
        st.markdown(
            f"<h4 style='color:{color}'>{state}</h4>",
            unsafe_allow_html=True
        )

        if st.button("Toggle", key=f"relay{i}"):

            relays_list = list(relays)
            relays_list[i] = next_state
            relays = "".join(relays_list)

            with open(RELAY_FILE, "w") as f:
                f.write(relays)

            st.rerun()

# ------------------------------
# Auto refresh every 5 sec
# ------------------------------
time.sleep(5)
st.rerun()
