from pytubefix import YouTube
from pytubefix.exceptions import PytubeFixError
import logging

logger = logging.getLogger(__name__)

def get_youtube_streams(youtube_url: str) -> list:
    """
    Returns list of progressive mp4 streams as dicts {"quality": ..., "url": ...}.
    Raises PytubeFixError on failure.
    """
    try:
        yt = YouTube(youtube_url)
        streams = yt.streams.filter(file_extension="mp4", progressive=True).order_by('resolution').desc()
        return [{"quality": s.resolution, "url": s.url} for s in streams]
    except PytubeFixError as e:
        logger.exception("pytubefix error fetching %s", youtube_url)
        raise
    except Exception as e:
        logger.exception("Unexpected error fetching youtube streams for %s", youtube_url)
        raise PytubeFixError(str(e)) from e
