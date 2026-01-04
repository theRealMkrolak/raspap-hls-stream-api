import asyncio
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from cv2 import VideoCapture
from fastapi import FastAPI, status
from fastapi.responses import Response

from .camera import router as camera_router
from .settings import settings


async def background_task(app: FastAPI):
    """
    Background task that runs in the background.
    """
    while True:
        # We wrap the blocking read in a task and shield it.
        # This allows us to wait for the thread to finish even if we are cancelled.
        # This is CRITICAL to avoid a race condition where release() is called
        # while read() is still executing in a thread (causing a segfault).
        read_task = asyncio.create_task(asyncio.to_thread(app.state.video_capture.read))
        try:
            ret, frame = await asyncio.shield(read_task)
        except asyncio.CancelledError:
            await read_task
            raise

        if not ret and frame is None:
            break

        app.state.last_frame = frame
        await asyncio.sleep(0.01)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Creates and manages the aiohttp ClientSession and background tasks for the application lifespan.
    """
    app.state.video_capture = VideoCapture(f"{settings.mediamtx_hls_url}/index.m3u8")
    app.state.last_frame = None

    async with ClientSession(raise_for_status=True) as session:
        app.state.client_session = session
        app.state.background_task = asyncio.create_task(background_task(app))
        yield
        await session.close()

    app.state.background_task.cancel()
    try:
        await app.state.background_task
    except asyncio.CancelledError:
        pass
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
)

app.include_router(camera_router)


@app.get("/")
def ok() -> Response:
    return Response(status_code=status.HTTP_200_OK)
