import asyncio
from contextlib import asynccontextmanager

from aiohttp import ClientSession
from cv2 import VideoCapture
from fastapi import FastAPI, status
from fastapi.responses import Response

from .camera import router as camera_router
from .settings import settings


async def get_lastest_frame(app: FastAPI) -> None:
    try:
        video_capture: VideoCapture = app.state.video_capture
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            app.state.latest_frame = frame
            await asyncio.sleep(0.0001)
    except asyncio.CancelledError:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Creates and manages the aiohttp ClientSession and background tasks for the application lifespan.
    """
    video_capture = VideoCapture(f"{settings.mediamtx_hls_url}/index.m3u8")
    app.state.video_capture = video_capture

    app.state.latest_frame = None
    get_latest_frame_task = asyncio.create_task(get_lastest_frame(app))

    async with ClientSession(raise_for_status=True) as session:
        app.state.client_session = session
        yield
        await session.close()
    app.state.video_capture.release()
    get_latest_frame_task.cancel()


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
