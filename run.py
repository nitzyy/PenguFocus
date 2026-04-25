import threading, subprocess, time, webbrowser

def start_flask():
    subprocess.Popen(["python", "app.py"])

t = threading.Thread(target=start_flask, daemon=True)
t.start()
time.sleep(1.5)          # wait for Flask to boot
webbrowser.open("http://localhost:5000")

import tkinter_app      # blocks here until window closes