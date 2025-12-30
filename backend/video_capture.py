from cv2 import VideoCapture
from queue import Queue
from cv2.typing import MatLike
from threading import Thread


class VideoCaptureBufferless:

    cap: VideoCapture
    queue: Queue[MatLike]

    def __init__(self, videoCapture: VideoCapture) -> None:
        self.cap = videoCapture
        self.queue = Queue()
        t = Thread(target=self._reader)
        t.daemon = True
        t.start()

    def _reader(self) -> None:
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.queue.empty():
                self.queue.get_nowait()   # discard previous (unprocessed) frame
            self.queue.put_nowait(frame)

    def read(self) -> MatLike:
        """Async read - returns the most recent frame."""
        return self.queue.get()