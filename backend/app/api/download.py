from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Game, GameFile

router = APIRouter()


@router.get("/{game_id}", summary="Download a game file")
async def download_game(
    game_id: int,
    file_id: int = Query(
        None,
        description="Optional GameFile id. Defaults to the first available file.",
    ),
    proxy: bool = Query(
        False,
        description="Proxy the file through this server instead of redirecting",
    ),
    session: AsyncSession = Depends(get_session),
):
    """Return the game file.

    By default this issues a 302 redirect to the stored file URL so the
    browser downloads directly from the source (no large binary passes through
    this API). With ?proxy=1 the server streams the file (only suitable for
    small/demo files).
    """
    game = await session.get(Game, game_id)
    if not game or not game.is_active:
        raise HTTPException(status_code=404, detail="Game not found")

    stmt = (
        select(GameFile)
        .where(GameFile.game_id == game.id)
        .order_by(
            case(
                (GameFile.label.ilike("%gofile%"), 1),
                (GameFile.label.ilike("%fileditch%"), 2),
                (GameFile.label.ilike("%mega%"), 3),
                else_=4,
            ),
            GameFile.id.asc(),
        )
        .limit(1)
    )
    if file_id is not None:
        stmt = select(GameFile).where(
            GameFile.id == file_id, GameFile.game_id == game.id
        )

    result = await session.execute(stmt)
    file_row = result.scalar_one_or_none()

    if file_id is not None and file_row is None:
        raise HTTPException(status_code=404, detail="File not found for this game")

    # CRITICAL: ensure we NEVER redirect to steamrip.com!
    url = file_row.url if file_row else game.direct_file_url
    if not url or "steamrip.com" in str(url).lower():
        # Check if there is any other non-steamrip game_file
        any_file_stmt = select(GameFile).where(
            GameFile.game_id == game.id,
            ~GameFile.url.ilike("%steamrip.com%"),
        ).limit(1)
        any_file = (await session.execute(any_file_stmt)).scalar_one_or_none()
        if any_file:
            url = any_file.url
        else:
            raise HTTPException(status_code=404, detail="Download mirrors are currently syncing. Please try again shortly.")

    if not url or "steamrip.com" in str(url).lower():
        raise HTTPException(status_code=404, detail="No direct mirror available for this game.")

    if proxy and url.startswith(("http://", "https://")):

        async def stream():
            import httpx

            async with httpx.AsyncClient() as client:
                async with client.stream("GET", url) as resp:
                    async for chunk in resp.aiter_bytes():
                        yield chunk

        return StreamingResponse(
            stream(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{game.slug}.bin"'},
        )

    return RedirectResponse(url, status_code=302)