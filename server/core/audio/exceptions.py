# server/core/audio/exceptions.py
class AudioError(Exception):
    ...

class NoResultError(AudioError):
    def __init__(self, query: str, stderr: bytes) -> None:
        self.query = query
        self.stderr = stderr
        super().__init__(f'No result found for query: {query!r}\nerror:\t{stderr.decode(errors='ignore')}')


class DownloadError(AudioError):
    def __init__(self, video_id: str, stderr: bytes) -> None:
        self.video_id = video_id
        self.stderr = stderr
        super().__init__(f'Download failed for {video_id}: {stderr.decode(errors='ignore')}')