from pydantic import BaseModel


class Playlist(BaseModel):
    """Output schema for playlist"""
    m3u8_url: str
