from flask import Flask
import os
import sys
import logging

# Silence default Flask/Werkzeug logs (200/304 GET logs)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Ensure backend dir is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from routes import api_blueprint

app = Flask(__name__)

import webbrowser
import threading

# Register Blueprint
app.register_blueprint(api_blueprint)

def open_browser():
    # Wait for server to start
    import time
    time.sleep(1.5)
    url = "http://127.0.0.1:5000"
    print(f"\n[*] AUTO-LAUNCHING: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    # Ensure we are in the backend directory context for relative paths
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(curr_dir)
    
    print("\n" + "="*50)
    print("   GRAND OAK ESTATES - AI ASSISTANT SERVER")
    print("   LOCAL API URL: http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    # Run browser launch in a separate thread so it doesn't block Flask
    threading.Thread(target=open_browser).start()
    
    app.run(debug=True, port=5000, use_reloader=False)
