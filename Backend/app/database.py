import sqlite3
from typing import List, Dict

def init_db():
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history 
                 (user_id TEXT, timestamp TEXT, message TEXT)''')
    conn.commit()
    conn.close()

def save_message(user_id: str, message: str):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id, timestamp, message) VALUES (?, datetime('now'), ?)", 
              (user_id, message))
    conn.commit()
    conn.close()

def get_chat_history(user_id: str) -> List[dict]:
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("SELECT timestamp, message FROM chat_history WHERE user_id = ? ORDER BY timestamp", (user_id,))
    history = [{"timestamp": row[0], "message": row[1]} for row in c.fetchall()]
    conn.close()
    return history

def clear_chat_history(user_id: str):
    conn = sqlite3.connect("chat_history.db")
    c = conn.cursor()
    c.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()