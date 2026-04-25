import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

from timer import Timer
from database import save_session, clear_all_sessions, get_last_session
from file_utils import write_log, ensure_dirs
from validator import valid_task_name
from analytics import show_graph, show_status_graph, show_daily_summary

ensure_dirs()

root = tk.Tk()
root.title("PenguFocus 🐧")
root.geometry("420x660")
root.resizable(False, False)

timer = Timer()
session_data = {
    "started_at": None,
    "saved": False,
    "task": "",
    "ended_reason": "timer"
}

def load_image(path, size=(180, 180)):
    img = Image.open(path)
    img = img.resize(size)
    return ImageTk.PhotoImage(img)

neutral_img = load_image("images/neutral.png")
happy_img = load_image("images/happy.png")
sad_img = load_image("images/sad.png")

task_var = tk.StringVar()
status_var = tk.StringVar(value="Enter a task and start a focus session.")

def update_status_from_last_session():
    last = get_last_session()
    if not last:
        status_var.set("Enter a task and start a focus session.")
        return

    if last.get("status") == "Failed" and last.get("ended_reason") == "closed":
        status_var.set("Previous session ended early because the app was closed.")
    elif last.get("status") == "Failed":
        status_var.set("Previous session ended early.")
    else:
        status_var.set("Welcome back! Your previous session was completed.")

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

def update_ui_state(state):
    if state == "neutral":
        penguin_label.config(image=neutral_img)
    elif state == "happy":
        penguin_label.config(image=happy_img)
    elif state == "sad":
        penguin_label.config(image=sad_img)

def update_timer():
    if not timer.running:
        return

    time_left = timer.tick()
    timer_label.config(text=f"{time_left//60:02}:{time_left%60:02}")

    if time_left > 0:
        update_ui_state("neutral")
        timer.after_id = root.after(1000, update_timer)
    else:
        complete_session()

def save_current_session(status, ended_reason):
    if session_data["saved"]:
        return

    try:
        save_session(
            session_data["task"],
            timer.elapsed,
            status,
            session_data["started_at"].strftime("%Y-%m-%d %H:%M:%S") if session_data["started_at"] else None,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ended_reason=ended_reason
        )
        session_data["saved"] = True
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def start_session():
    if timer.running:
        return

    task = task_var.get().strip()
    try:
        assert task != "", "Task cannot be empty"
        if not valid_task_name(task):
            raise ValueError("Task name contains invalid characters")
    except AssertionError as e:
        messagebox.showerror("Validation Error", str(e))
        return
    except ValueError as e:
        messagebox.showerror("Validation Error", str(e))
        return

    timer.reset()
    timer.start()
    session_data["started_at"] = datetime.now()
    session_data["saved"] = False
    session_data["task"] = task
    session_data["ended_reason"] = "timer"

    update_ui_state("neutral")
    status_var.set(f"Working on: {task}")
    write_log(f"STARTED session for task: {task}")
    update_timer()

def stop_session():
    if not timer.running:
        return

    if timer.after_id is not None:
        try:
            root.after_cancel(timer.after_id)
        except:
            pass
        timer.after_id = None

    timer.stop()
    update_ui_state("sad")
    status_var.set(f"Session failed. Penguin is sad! Task: {session_data['task']}")
    write_log(f"FAILED session for task: {session_data['task']} after {timer.elapsed} seconds")
    save_current_session("Failed", "stop")

def complete_session():
    if timer.after_id is not None:
        try:
            root.after_cancel(timer.after_id)
        except:
            pass
        timer.after_id = None

    timer.stop()
    timer_label.config(text="00:00")
    update_ui_state("happy")
    status_var.set(f"Session completed. Penguin is happy! Task: {session_data['task']}")
    write_log(f"COMPLETED session for task: {session_data['task']} in {timer.elapsed} seconds")
    save_current_session("Completed", "timer")

def on_close():
    if timer.running and not session_data["saved"]:
        if timer.after_id is not None:
            try:
                root.after_cancel(timer.after_id)
            except:
                pass
            timer.after_id = None

        timer.stop()
        update_ui_state("sad")
        status_var.set(f"Session failed because app was closed. Task: {session_data['task']}")
        write_log(f"FAILED session for task: {session_data['task']} after {timer.elapsed} seconds due to close")
        save_current_session("Failed", "closed")
    root.destroy()

def start_fresh():
    if messagebox.askyesno("Warning", "This will clear ALL previous data permanently. Continue?"):
        clear_all_sessions()
        timer.reset()
        session_data["started_at"] = None
        session_data["saved"] = False
        session_data["task"] = ""
        session_data["ended_reason"] = "timer"
        task_var.set("")
        timer_label.config(text="25:00")
        status_var.set("All data cleared. Start a fresh session.")
        update_ui_state("neutral")

def open_graph_safe():
    try:
        show_graph()
    except Exception as e:
        messagebox.showerror("Graph Error", str(e))

def open_status_graph_safe():
    try:
        show_status_graph()
    except Exception as e:
        messagebox.showerror("Graph Error", str(e))

def open_daily_summary_safe():
    try:
        show_daily_summary()
    except Exception as e:
        messagebox.showerror("Graph Error", str(e))

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Start", command=start_session, width=14).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Stop", command=stop_session, width=14).grid(row=0, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Show Graph", command=open_graph_safe, width=14).grid(row=1, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Status Graph", command=open_status_graph_safe, width=14).grid(row=1, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Daily Summary", command=open_daily_summary_safe, width=30).grid(row=2, column=0, columnspan=2, padx=5, pady=5)
tk.Button(button_frame, text="Start Fresh", command=start_fresh, width=30).grid(row=3, column=0, columnspan=2, padx=5, pady=5)

update_status_from_last_session()
root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()