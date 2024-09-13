from typing import Annotated

from fastapi import APIRouter, Depends, Path
from schemas.film import Playlist
from api.v1.handlers import ExceptionHandlerRoute

from services.playlist import PlaylistService, get_playlist_service



router = APIRouter()
router.route_class = ExceptionHandlerRoute

@router.get(
    "/{film_id}/playlist",
    summary="Плэйлист фильма",
    response_model=Playlist,
)
async def playlist(
        film_id: Annotated[str, Path(description="ID фильма в формате UUID")],
        playlist_service: PlaylistService = Depends(get_playlist_service),
) -> Playlist:
    url = playlist_service.get_playlist_url(film_id)
    return Playlist(m3u8_url=url)
