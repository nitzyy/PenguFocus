import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import requests

from timer import Timer
from validator import valid_task_name

FLASK_URL = "http://127.0.0.1:5000"

timer = Timer()

session_data = {
    "started_at": None,
    "saved": False,
    "task": "",
    "ended_reason": "timer"
}

def post_session(status, ended_reason):
    if session_data["saved"]:
        return

    if not session_data["started_at"]:
        return

    payload = {
        "task": session_data["task"],
        "time": timer.elapsed,
        "status": status,
        "started_at": session_data["started_at"].strftime("%Y-%m-%d %H:%M:%S"),
        "ended_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ended_reason": ended_reason
    }

    r = requests.post(f"{FLASK_URL}/api/session/save", json=payload, timeout=3)
    r.raise_for_status()
    session_data["saved"] = True

def load_image(path, size=(180, 180)):
    img = Image.open(path).resize(size)
    return ImageTk.PhotoImage(img)

def run_tkinter_window():
    root = tk.Tk()
    root.title("PenguFocus Focus Mode")
    root.geometry("420x620")
    root.resizable(False, False)

    neutral_img = load_image("images/neutral.png")
    happy_img = load_image("images/happy.png")
    sad_img = load_image("images/sad.png")

    task_var = tk.StringVar()
    status_var = tk.StringVar(value="Enter a task and start focusing.")

    title = tk.Label(root, text="PenguFocus 🐧", font=("Arial", 20, "bold"))
    title.pack(pady=10)

    entry = tk.Entry(root, textvariable=task_var, font=("Arial", 12), width=28)
    entry.pack(pady=8)

    penguin_label = tk.Label(root, image=neutral_img)
    penguin_label.pack(pady=10)

    timer_label = tk.Label(root, text="25:00", font=("Arial", 24, "bold"))
    timer_label.pack(pady=5)

    status_label = tk.Label(root, textvariable=status_var, font=("Arial", 11), wraplength=350)
    status_label.pack(pady=5)

    def update_ui(state):
        if state == "neutral":
            penguin_label.config(image=neutral_img)
        elif state == "happy":
            penguin_label.config(image=happy_img)
        else:
            penguin_label.config(image=sad_img)

    def cancel_after():
        if timer.after_id is not None:
            try:
                root.after_cancel(timer.after_id)
            except:
                pass
            timer.after_id = None

    def update_timer():
        if not timer.running:
            return

        remaining = timer.tick()
        timer_label.config(text=f"{remaining//60:02}:{remaining%60:02}")

        if remaining > 0:
            update_ui("neutral")
            timer.after_id = root.after(1000, update_timer)
        else:
            complete_session()

    def start_session():
        task = task_var.get().strip()

        try:
            assert task != "", "Task cannot be empty"
            if not valid_task_name(task):
                raise ValueError("Task name contains invalid characters")
        except (AssertionError, ValueError) as e:
            messagebox.showerror("Validation Error", str(e))
            return

        if timer.running:
            return

        timer.reset()
        timer.start()
        session_data["started_at"] = datetime.now()
        session_data["saved"] = False
        session_data["task"] = task
        session_data["ended_reason"] = "timer"

        update_ui("neutral")
        status_var.set(f"Working on: {task}")
        update_timer()

    def stop_session():
        if not timer.running:
            return

        cancel_after()
        timer.stop()
        update_ui("sad")
        status_var.set("Session failed. Penguin is sad.")

        try:
            post_session("Failed", "stop")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def complete_session():
        cancel_after()
        timer.stop()
        timer_label.config(text="00:00")
        update_ui("happy")
        status_var.set("Session completed. Penguin is happy.")

        try:
            post_session("Completed", "timer")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def on_close():
        if timer.running and not session_data["saved"]:
            cancel_after()
            timer.stop()
            update_ui("sad")
            try:
                post_session("Failed", "closed")
            except:
                pass
        root.destroy()

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Start", command=start_session, width=14).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(button_frame, text="Stop", command=stop_session, width=14).grid(row=0, column=1, padx=5, pady=5)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()