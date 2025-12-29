from aiohttp import ClientSession
from cv2 import VideoCapture, imencode
from fastapi import FastAPI, status
from fastapi.responses import Response, StreamingResponse

from .auth import APIKeyDep
from .settings import settings

tags_metadata = [
    {
        "name": "stream",
        "description": "Stream the camera",
    }
]


app = FastAPI(
    title="Watch Camera",
    description="A simple camera streaming service",
    version="0.1.0",
    tags_metadata=tags_metadata,
    licence_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

@app.get("/")
def ok() -> Response:
    return Response(status_code=status.HTTP_200_OK)

@app.get("/photo")
async def photo(
    api_key: str = APIKeyDep,
) -> Response:
    video_capture = VideoCapture(f"{settings.mediamtx_hls_url}/index.m3u8")
    success, frame = video_capture.read()
    if not success:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Failed to read frame from camera")
    _, encoded_frame = imencode('.jpg', frame)
    return Response(content=encoded_frame.tobytes(), media_type="image/jpeg")


@app.get("/stream")
@app.get("/{filename:path}")
async def hls_proxy(
    filename: str = "index.m3u8",
    api_key: str = APIKeyDep,
) -> Response:
    session = ClientSession()
    # Make request and get response (but don't enter context yet)
    response = await session.get(f"{settings.mediamtx_hls_url}/{filename}")
    
    # Get headers and status before streaming
    media_type = response.headers.get("Content-Type", "application/octet-stream")
    status_code = response.status
    

    async def stream_generator():
        async for chunk in response.content.iter_any():
            yield chunk

    return StreamingResponse(
        stream_generator(),
        media_type=media_type,
        status_code=status_code
    )