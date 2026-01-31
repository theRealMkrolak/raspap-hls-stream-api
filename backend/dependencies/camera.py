from typing import Annotated

from cv2 import VideoCapture
from fastapi import Depends, Request


def get_video_capture(request: Request) -> VideoCapture | None:
    return request.app.state.video_capture


VideoCaptureDep = Annotated[VideoCapture | None, Depends(get_video_capture)]


def get_camera_last_frame(request: Request) -> bytes | None:
    return request.app.state.camera_last_frame


CameraLastFrameDep = Annotated[bytes | None, Depends(get_camera_last_frame)]
