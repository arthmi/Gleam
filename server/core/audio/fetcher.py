# server/core/audio/fetcher
import asyncio
import json
from pathlib import Path

from server.core.audio.cache import AudioCache
from server.core.audio.exceptions import NoResultError, DownloadError

class AudioFetcher:
    def __init__(self, cache: AudioCache):
        self._cache_dir = Path('.cache/audio/files')
        self._cache = cache

    async def fetch_audio(self, query: str) -> Path:
        video_id, title = await self._resolve(query)

        cached_path = self._cache.get(video_id)
        if cached_path and cached_path.exists():
            self._cache.touch(video_id)
            return cached_path

        path = await self._download(video_id)
        self._cache.put(video_id, path, title=title, query=query)
        return path

    async def _resolve(self, query: str) -> tuple[str, str]:
        proc = await asyncio.create_subprocess_exec(
            'yt-dlp', f'ytsearch1:{query}', '--dump-json', '--no-download',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0 or not stdout:
            raise NoResultError(query, stderr)
        
        data = json.loads(stdout)
        return data['id'], data['title']

    async def _download(self, video_id: str) -> Path:
        path = f'{self._cache_dir}/{video_id}.wav'
        proc = await asyncio.create_subprocess_exec(
            'yt-dlp', f'https://www.youtube.com/watch?v={video_id}', '-x', '--audio-format', 'wav', '-o', path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise DownloadError(video_id, stderr)
        if Path(path).is_file():
            return Path(path)
        raise DownloadError(video_id, stderr)