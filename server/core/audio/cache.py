# server/core/audio/cache.py
from pathlib import Path
import time
from server.database import Database


class AudioCache:
    def __init__(self, db: Database, files_dir: Path, max_size_bytes: int):
        self.db = db
        self._files_dir = files_dir
        self._max_size_bytes = max_size_bytes

        self._files_dir.mkdir(parents=True, exist_ok=True)
        self._init_audio_cache()

    def _init_audio_cache(self) -> None:
        self.db.cursor.execute('''
            CREATE TABLE IF NOT EXISTS audio_cache (
                video_id TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                title TEXT NOT NULL,
                query TEXT NOT NULL,
                last_used_at REAL NOT NULL,
                size_bytes INTEGER NOT NULL
            )
        ''')
        self.db.conn.commit()

    def get(self, video_id: str) -> Path | None:
        self.db.cursor.execute("SELECT path FROM audio_cache WHERE video_id = ?", (video_id,))
        row = self.db.cursor.fetchone()
        if not row:
            return None
        return Path(row[0])
        

    def touch(self, video_id: str) -> None:
        self.db.cursor.execute('UPDATE audio_cache SET last_used_at = ? WHERE video_id = ?', (time.time(), video_id,))
        self.db.conn.commit()

    def put(self, video_id: str, path: Path, *, title: str, query: str) -> None:
        size = path.stat().st_size
        self.db.cursor.execute('INSERT INTO audio_cache VALUES (?, ?, ?, ?, ?, ?)', (video_id, str(path), title, query, time.time(), size,))
        self.db.conn.commit()
        self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        while self._total_size() > self._max_size_bytes:
            self.db.cursor.execute('SELECT video_id, path FROM audio_cache ORDER BY last_used_at ASC LIMIT 1')
            video_id, path = self.db.cursor.fetchone()
            Path(path).unlink(missing_ok=True)
            self.db.cursor.execute('DELETE FROM audio_cache WHERE video_id = ?', (video_id,))
            self.db.conn.commit()

    def _total_size(self) -> int:
        self.db.cursor.execute('SELECT COALESCE(SUM(size_bytes), 0) FROM audio_cache')
        return self.db.cursor.fetchone()[0]