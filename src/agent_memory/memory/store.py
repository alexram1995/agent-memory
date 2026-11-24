from pathlib import Path
import sqlite3

class Store:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
        self.db.executescript(schema)

    def ensure_project(self, project_id: str, name: str | None = None):
        self.db.execute("INSERT OR IGNORE INTO projects(id,name) VALUES(?,?)", (project_id, name or project_id))
        self.db.commit()

    def start_session(self, project_id: str, session_id: str):
        self.ensure_project(project_id)
        self.db.execute("INSERT OR IGNORE INTO sessions(id,project_id) VALUES(?,?)", (session_id, project_id))
        self.db.commit()

    def save_state(self, project_id: str, session_id: str, content: str):
        self.db.execute("INSERT INTO active_states(project_id,session_id,content,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP) "
                        "ON CONFLICT(project_id) DO UPDATE SET session_id=excluded.session_id,content=excluded.content,updated_at=CURRENT_TIMESTAMP",
                        (project_id, session_id, content))
        self.db.commit()

    def get_state(self, project_id: str):
        row = self.db.execute("SELECT content FROM active_states WHERE project_id=?", (project_id,)).fetchone()
        return row["content"] if row else None

    def add_memory(self, project_id: str, kind: str, content: str, session_id=None, importance=3, source=None):
        cur = self.db.execute("INSERT INTO memories(project_id,session_id,kind,content,importance,source) VALUES(?,?,?,?,?,?)",
                              (project_id, session_id, kind, content, importance, source))
        mid = cur.lastrowid
        self.db.execute("INSERT INTO memories_fts(rowid,content,kind,project_id) VALUES(?,?,?,?)", (mid, content, kind, project_id))
        self.db.commit()
        return mid

    def add_event(self, project_id: str, event_type: str, content: str, session_id=None, task_id=None, verified=False):
        self.db.execute("INSERT INTO events(project_id,session_id,task_id,event_type,content,verified) VALUES(?,?,?,?,?,?)",
                        (project_id,session_id,task_id,event_type,content,int(verified)))
        self.db.commit()

    def search(self, project_id: str, query: str, limit=8):
        # FTS5 query syntax can reject punctuation-heavy inputs; fall back to LIKE.
        try:
            rows = self.db.execute("SELECT m.id,m.kind,m.content,m.importance,m.created_at FROM memories m "
                "JOIN memories_fts f ON f.rowid=m.id WHERE f.project_id=? AND memories_fts MATCH ? "
                "ORDER BY m.importance DESC,m.id DESC LIMIT ?", (project_id, query, limit)).fetchall()
        except sqlite3.OperationalError:
            rows = self.db.execute("SELECT id,kind,content,importance,created_at FROM memories WHERE project_id=? AND content LIKE ? "
                "ORDER BY importance DESC,id DESC LIMIT ?", (project_id, f"%{query}%", limit)).fetchall()
        return [dict(r) for r in rows]

    def recent_events(self, project_id: str, limit=12):
        rows = self.db.execute("SELECT event_type,content,verified,created_at FROM events WHERE project_id=? ORDER BY id DESC LIMIT ?",(project_id,limit)).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        self.db.close()
