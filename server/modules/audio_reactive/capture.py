# audio_reactive/capture.py
import threading

import numpy as np
import sounddevice as sd

from analysis import Analyzer, AudioFeatures


class AudioCapture:
    _instances: dict[str, 'AudioCapture'] = {}
    _lock = threading.Lock()

    def __init__(self, device: str):
        self._device = device
        self._refs = 0          # number of modules using this instance
        self._latest = AudioFeatures()
        self._stream: sd.InputStream | None = None
        self._analyzer: Analyzer | None = None

    @classmethod
    def acquire(cls, device: str = '') -> 'AudioCapture':
        with cls._lock:
            if device not in cls._instances:
                cls._instances[device] = AudioCapture(device)
            instance = cls._instances[device]
            instance._refs += 1
            if instance._refs == 1: # first user, start the stream
                instance._start()
                catch Exception as e:
                    instance._refs -= 1
                    del cls._instances[device]
                    raise RuntimeError(f'Failed to start audio capture for device '{device}': {e}') from e
            return instance

    def release(self) -> None:
        with cls._lock:
            self._refs -= 1
            if self._refs == 0:
                self._stop()
                del self._instances[self._device]

    def latest(self) -> AudioFeatures:
        return self._latest

    def _start(self) -> None:
        device = self._device or None
        info = sd.query_devices(device, 'input')      # get the device info
        sample_rate = int(info['default_samplerate']) # get the default sample rate for the device
        channels = min(2, info['max_input_channels']) # get the number of channels (max 2 for stereo)
        self._analyzer = Analyzer(sample_rate)
        self._stream = sd.InputStream(
            device=device,
            channels=channels,
            samplerate=sample_rate,
            blocksize=512,          # the number of frames per block
            dtype='float32',
            callback=self._on_audio
            )
        self._stream.start()

    def _stop(self) -> None:
        self._stream.stop()
        self._stream.close()
        self._stream = None

    def _on_audio(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        mono = indata.mean(axis=1) # convert to mono if stereo
        self._latest = self._analyzer.process(mono)