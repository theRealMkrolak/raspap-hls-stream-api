import asyncio
import contextlib
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from cv2 import VideoCapture
from fastapi import FastAPI, status
from fastapi.responses import Response

from .administrative import router as administrative_router
from .camera import router as camera_router
from .settings import settings


async def background_task(app: FastAPI):
    """
    Background task that captures frames from the stream with automatic reconnection.
    """
    video_capture: VideoCapture = app.state.video_capture
    stream_url = f"{settings.mediamtx_hls_url}/index.m3u8"

    while True:
        # 1. Check if the capture is valid; if not, try to reconnect
        if video_capture is None or not video_capture.isOpened():
            if video_capture is not None:
                video_capture.release()

            video_capture = VideoCapture(stream_url)
            app.state.video_capture = video_capture

            if not video_capture.isOpened():
                await asyncio.sleep(5)
                continue

        # 2. Try to read a frame
        read_task = asyncio.create_task(asyncio.to_thread(video_capture.read))
        try:
            ret, frame = await read_task

            if not ret:
                video_capture.release()
                await asyncio.sleep(5)
                continue

            app.state.last_frame = frame
            await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            if video_capture is not None:
                video_capture.release()
            raise
        except Exception:
            if video_capture is not None:
                video_capture.release()
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Creates and manages the aiohttp ClientSession and
    background tasks for the application lifespan.
    """
    # Initialize with None to let background_task handle the first connection
    app.state.video_capture = None
    app.state.last_frame = None

    async with ClientSession(raise_for_status=True) as session:
        app.state.client_session = session
        app.state.background_task = asyncio.create_task(background_task(app))
        yield
        await session.close()

    # Cancel the background task and wait for it to clean up
    app.state.background_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await app.state.background_task

    # Final cleanup check
    if app.state.video_capture is not None:
        app.state.video_capture.release()


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
    },
    lifespan=lifespan,
    debug=True,
)

app.include_router(camera_router)
app.include_router(administrative_router)


@app.get("/")
def ok() -> Response:
    return Response(status_code=status.HTTP_200_OK)
