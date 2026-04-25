from flask import Flask, render_template, jsonify, request
from database import (
    save_session,
    get_today_sessions,
    get_all_sessions,
    clear_all_sessions,
    get_last_session,
    ping_db
)
from analytics import show_graph, show_status_graph, show_daily_summary
from threading import Thread

app = Flask(__name__)

# ── DB connection check ──────────────────────────────────────────────────────
try:
    ping_db()
    print("MongoDB connected successfully.")
except Exception as e:
    print("MongoDB connection failed:", e)


# ── Dashboard ────────────────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    sessions       = get_today_sessions()
    completed      = [s for s in sessions if s.get("status") == "Completed"]
    failed         = [s for s in sessions if s.get("status") == "Failed"]
    total_focus    = sum(s.get("time", 0) for s in completed)
    total_sessions = len(sessions)
    success_rate   = round((len(completed) / total_sessions) * 100) if total_sessions else 0

    last = get_last_session()
    last_message = "No previous sessions yet."
    if last:
        if last.get("status") == "Failed" and last.get("ended_reason") == "closed":
            last_message = "Your previous session ended early because you closed the app."
        elif last.get("status") == "Failed":
            last_message = "Your previous session ended early."
        else:
            last_message = "Your previous session was completed."

    return render_template(
        "dashboard.html",
        sessions=sessions,
        completed_count=len(completed),
        failed_count=len(failed),
        total_focus_mins=total_focus // 60,
        success_rate=success_rate,
        last_message=last_message
    )


# ── Analytics page ───────────────────────────────────────────────────────────
@app.route("/analytics")
def analytics():
    sessions  = get_today_sessions()
    task_map  = {}
    for s in sessions:
        task = s.get("task", "Unknown")
        task_map[task] = task_map.get(task, 0) + int(s.get("time", 0))

    task_labels = list(task_map.keys())
    task_values = list(task_map.values())
    completed   = sum(1 for s in sessions if s.get("status") == "Completed")
    failed      = sum(1 for s in sessions if s.get("status") == "Failed")

    return render_template(
        "analytics.html",
        sessions=sessions,
        task_labels=task_labels,
        task_values=task_values,
        completed=completed,
        failed=failed
    )


# ── Start Tkinter focus window ───────────────────────────────────────────────
@app.route("/start-focus", methods=["POST"])
def start_focus():
    from tkinter_app import run_tkinter_window   # local import avoids circular import
    Thread(target=run_tkinter_window, daemon=True).start()
    return jsonify({"ok": True})


# ── Session API ──────────────────────────────────────────────────────────────
@app.route("/api/sessions/today")
def api_today():
    return jsonify(get_today_sessions())

@app.route("/api/sessions/all")
def api_all():
    return jsonify(get_all_sessions())

@app.route("/api/session/save", methods=["POST"])
def api_save():
    data = request.json
    save_session(
        data["task"],
        data["time"],
        data["status"],
        data.get("started_at"),
        data.get("ended_at"),
        data.get("ended_reason", "timer")
    )
    return jsonify({"ok": True})

@app.route("/api/sessions/clear", methods=["POST"])
def api_clear():
    clear_all_sessions()
    return jsonify({"ok": True})


# ── Matplotlib plot trigger (optional, opens in desktop window) ──────────────
@app.route("/plot/<name>", methods=["POST"])
def plot(name):
    try:
        if name == "graph":
            show_graph()
        elif name == "status":
            show_status_graph()
        elif name == "summary":
            show_daily_summary()
        else:
            return jsonify({"ok": False, "error": "Unknown plot name"}), 400
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(port=5000, debug=False, use_reloader=False)