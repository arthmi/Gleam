# ambilight/capture.py
import threading
import numpy as np
import cv2

class AmbilightCapture:
    _instance: 'AmbilightCapture|None' = None
    _instance_lock = threading.Lock()

    def __init__(self, device_index: int) -> None:
        self.device_index = device_index

        self.width: int|None = None
        self.height: int|None = None

        self._cap: cv2.VideoCapture|None = None
        self._thread: threading.Thread|None = None
        self._running = False

        self._latest_frame: np.ndarray|None = None
        self._frame_lock = threading.Lock()

    @classmethod
    def get_instance(cls, device_index: int=0) -> AmbilightCapture:
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls(device_index)
                    cls._instance.start()
        return cls._instance

    def start(self) -> None:
        self._cap = cv2.VideoCapture(self.device_index)
        if not self._cap or not self._cap.isOpened():
            raise RuntimeError(f'AmbilightCapture: unable to open video device index {self.device_index}')

        self.width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join()
        if self._cap is not None:
            self._cap.release()

    def get_latest_frame(self) -> np.ndarray|None:
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            return self._latest_frame.copy()

    def _capture_loop(self) -> None:
        while self._running:
            ret, frame = self._cap.read()    # type: ignore
            if not ret:
                # log : device disconected
                continue
            cv2.imshow("Ambilight", frame)
            cv2.waitKey(1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            with self._frame_lock:
                self._latest_frame = frame