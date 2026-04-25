import pandas as pd
import matplotlib.pyplot as plt
from database import get_today_sessions

def _today_df():
    data = get_today_sessions()
    if not data:
        return None
    df = pd.DataFrame(data)
    if df.empty:
        return None
    df["time"] = pd.to_numeric(df.get("time", 0), errors="coerce").fillna(0)
    return df

def show_graph():
    df = _today_df()
    if df is None or "task" not in df.columns:
        print("No data available")
        return

    task_time = df.groupby("task")["time"].sum().sort_values(ascending=False)
    if task_time.empty:
        print("No task data to plot")
        return

    plt.figure(figsize=(8, 5))
    task_time.plot(kind="bar", color="skyblue")
    plt.title("Time Spent per Task Today")
    plt.xlabel("Task")
    plt.ylabel("Time (seconds)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def show_status_graph():
    df = _today_df()
    if df is None or "status" not in df.columns:
        print("No data available")
        return

    counts = df["status"].value_counts()
    if counts.empty:
        print("No status data to plot")
        return

    plt.figure(figsize=(6, 4))
    counts.plot(kind="bar", color=["green", "red", "orange"])
    plt.title("Completed vs Failed Sessions")
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

def show_daily_summary():
    df = _today_df()
    if df is None or "status" not in df.columns:
        print("No data available")
        return

    completed = df[df["status"] == "Completed"]["time"].sum()
    failed = df[df["status"] == "Failed"]["time"].sum()

    if completed == 0 and failed == 0:
        print("No productive data yet")
        return

    plt.figure(figsize=(6, 6))
    plt.pie(
        [completed, failed],
        labels=["Completed", "Failed"],
        autopct="%1.1f%%",
        colors=["#66cc66", "#ff6666"]
    )
    plt.title("Today’s Productivity Split")
    plt.tight_layout()
    plt.show()