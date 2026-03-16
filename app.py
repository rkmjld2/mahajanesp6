from flask import Flask, request
import time
import os

app = Flask(__name__)

RELAY_FILE = "relay.txt"
HB_FILE = "last_hb_time.txt"

# Create files if missing
open(RELAY_FILE, 'a').close()
open(HB_FILE, 'a').close()

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    with open(HB_FILE, 'w') as f:
        f.write(str(time.time()))
    return "OK"

@app.route('/read', methods=['GET'])
def read_relay():
    try:
        with open(RELAY_FILE, 'r') as f:
            return f.read()
    except:
        return "RRRRRRRR"

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    relays = "RRRRRRRR"
    try:
        with open(RELAY_FILE, 'r') as f:
            relays = f.read()[:8].ljust(8, 'R')
    except:
        pass
    
    try:
        with open(HB_FILE, 'r') as f:
            last = float(f.read())
            age = time.time() - last
            status = "🟢 ONLINE" if age < 30 else "🔴 OFFLINE"
            age_text = f"{int(age)}s ago"
    except:
        status = "🔴 OFFLINE"
        age_text = "Never"
    
    if request.method == 'POST':
        new_relays = request.form.get('relays', relays)[:8].upper()
        with open(RELAY_FILE, 'w') as f:
            f.write(new_relays)
        return dashboard()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>ESP8266 Control</title>
    <meta http-equiv="refresh" content="5">
    <style>
    body {{ font-family: Arial; margin: 40px; }}
    .status {{ font-size: 24px; font-weight: bold; padding: 10px; }}
    .online {{ background: #d4edda; color: #155724; }}
    .offline {{ background: #f8d7da; color: #721c24; }}
    .relay {{ display: inline-block; width: 80px; margin: 5px; padding: 10px; text-align: center; border-radius: 5px; }}
    .on {{ background: #d4edda; color: #155724; }}
    .off {{ background: #f8d7da; color: #721c24; }}
    input {{ width: 200px; padding: 8px; }}
    button {{ padding: 8px 20px; background: #007bff; color: white; border: none; border-radius: 5px; }}
    </style>
    </head>
    <body>
        <h1>ESP8266 Relay Control</h1>
        <div class="status {'online' if 'ONLINE' in status else 'offline'}">{status}</div>
        <p>Last heartbeat: {age_text}</p>
        
        <h2>Relay Status: {relays}</h2>
        <div>
        """
    for i in range(8):
        status = "ON" if relays[i] == 'G' else "OFF"
        cls = "on" if relays[i] == 'G' else "off"
        html += f'<div class="relay {cls}">R{i+1}: {status}</div>'
    
    html += f"""
        </div>
        <form method="POST">
            <p>Relay state: <input name="relays" value="{relays}" maxlength="8">
            <button>Update</button></p>
        </form>
    </body>
    </html>
    """
    return html

if __name__ == '__main__':
    app.run()
