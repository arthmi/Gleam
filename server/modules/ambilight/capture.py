# capture.py
import threading
import cv2
import numpy as np

class AmbilightCapture:
    _instances: dict[int, "AmbilightCapture"] = {}
    _instances_lock = threading.Lock()

    def __init__(self, device_index: int):
        self.device_index: int = device_index

        self._cap: cv2.VideoCapture | None = None
        self._thread: threading.Thread | None = None
        
        self._ref_count: int = 0
        self._lock = threading.Lock()
        self._latest_frame: np.ndarray | None = None
        self._frame_lock = threading.Lock()

        self._running: bool = False

    @classmethod
    def get_instance(cls, device_index: int) -> "AmbilightCapture":
        with cls._instances_lock:
            if device_index not in cls._instances:
                cls._instances[device_index] = cls(device_index)
            return cls._instances[device_index]

    def acquire(self) -> None:
        with self._lock:
            self._ref_count += 1
            if self._ref_count == 1:
                self._start()

    def release(self) -> None:
        with self._lock:
            if self._ref_count == 0:
                raise RuntimeError('No active')
            self._ref_count -= 1
            if self._ref_count == 0:
                self._stop()

    def _start(self) -> None:
        self._cap = cv2.VideoCapture(self.device_index)
        if not self._cap.isOpened():
            raise RuntimeError(f"Failed to open capture device at index {self.device_index}")
        # cv2.VideoWriter_fourcc(*'MJPG')     # "VideoWriter_fourcc" is not a known attribute of module cv2
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _stop(self) -> None:
        self._running = False
        if self._thread is None:
            raise RuntimeError("_stop() called but no capture thread was running")
        self._thread.join(timeout=5)
        if self._thread.is_alive():
            raise RuntimeError(f"Capture thread for device {self.device_index} did not stop within timeout")
        if self._cap is not None:
            self._cap.release()
        with self._frame_lock:
            self._cap = None
            self._thread = None
            self._latest_frame = None

    def _capture_loop(self) -> None:
        while self._running:
            if not self._cap:
                raise RuntimeError("_capture_loop running but self._cap is None")
            ret, frame = self._cap.read()
            if not ret:
                raise RuntimeError(f"Failed to read frame from device {self.device_index}")
            with self._frame_lock:
                self._latest_frame = frame
            cv2.imshow("Ambilight", frame)
            cv2.waitKey(1)
                

    def get_latest_frame(self) -> np.ndarray | None:
        with self._frame_lock:
            if self._latest_frame is None:
                return None
            else:
                return self._latest_frame.copy()