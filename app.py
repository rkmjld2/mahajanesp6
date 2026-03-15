from flask import Flask, request
import time
import os

app = Flask(__name__)

RELAY_FILE = "relay.txt"
HB_FILE = "last_hb_time.txt"

# Create files
open(RELAY_FILE, 'a').close()
open(HB_FILE, 'a').close()

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    with open(HB_FILE, 'w') as f:
        f.write(str(time.time()))
    return "OK"

@app.route('/read', methods=['GET'])
def read_relay():
    with open(RELAY_FILE, 'r') as f:
        return f.read()

@app.route('/')
def dashboard():
    with open(RELAY_FILE, 'r') as f:
        relays = f.read()[:8].ljust(8, 'R')
    
    with open(HB_FILE, 'r') as f:
        last = float(f.read())
    
    age = time.time() - last
    
    status = "🟢 ONLINE" if age < 30 else "🔴 OFFLINE"
    
    html = f"""
    <h1>ESP8266 Relay Control</h1>
    <h2>{status}</h2>
    <p>Last heartbeat: {int(age)}s ago</p>
    <h3>Relays: {relays}</h3>
    <form method="POST">
        <input name="relays" value="{relays}" maxlength="8">
        <button>Update</button>
    </form>
    """
    return html

@app.route('/', methods=['POST'])
def update_relays():
    relays = request.form['relays'][:8].upper()
    with open(RELAY_FILE, 'w') as f:
        f.write(relays)
    return dashboard()

if __name__ == '__main__':
    app.run()
