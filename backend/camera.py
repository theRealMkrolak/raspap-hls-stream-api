from aiohttp import ClientSession
from cv2 import imencode
from typing import AsyncGenerator
from fastapi import APIRouter, Request, status
from fastapi.responses import Response, StreamingResponse

from .auth import APIKeyDep
from .settings import settings

router = APIRouter(tags=["camera"])

@router.get("/photo")
async def photo(
    request: Request,
    api_key: str = APIKeyDep,
) -> Response:
    frame = request.app.state.latest_frame
    if frame is None:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Failed to read frame from camera")
    _, encoded_frame = imencode('.jpg', frame)
    return Response(content=encoded_frame.tobytes(), media_type="image/jpeg")


@router.get("/stream")
@router.get("/{filename:path}")
async def hls_proxy(
    request: Request,
    filename: str = "index.m3u8",
    api_key: str = APIKeyDep,
) -> StreamingResponse:
    session: ClientSession = request.app.state.client_session
    query_params_string = "&".join([f"{key}={value}" for key, value in request.query_params.items()])
    response = await session.get(f"{settings.mediamtx_hls_url}/{filename}?{query_params_string}")    
    status_code = response.status
    headers = response.headers
    async def get_chunk() -> AsyncGenerator[bytes, None]:
        while True:
            chunk = await response.content.read(65536)
            if not chunk:
                break
            yield chunk
    return StreamingResponse(content=get_chunk(), status_code=status_code, headers=headers)