# audio_reactive/analysis.py
from dataclasses import dataclass

import numpy as np

@dataclass(frozen=True)
class AudioFeatures:
    level: float = 0.0

class Analyzer:
    def __init__(
            self,
            sample_rate: int,            # sample rate in Hz
            window_size: int = 1024,     # number of samples in the analysis window
            agc_release_s: float = 10.0, # AGC release time in seconds
            noise_floor: float = 0.01,   # noise floor level (0.0-1.0) below which the signal is considered silence
        ):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.agc_release_s = agc_release_s
        self.noise_floor = noise_floor

        self._buffer = np.zeros(window_size, dtype=np.float32) # preallocate ring buffer
        self._write_index = 0
        self._peak = 2 * noise_floor
        raise NotImplementedError

    def process(self, block: np.ndarray) -> AudioFeatures:
        if len(block) >= self.window_size:
            self._buffer[:] = block[-self.window_size:] # overwrite the buffer with the last `window_size`
            self._write_index = 0
        else:
            end_index = (self._write_index + len(block)) % self.window_size # compute the end index in the ring buffer
            if end_index < self._write_index:
                self._buffer[self._write_index:] = block[:self.window_size - self._write_index] # write the first part of the block to the end of the buffer
                self._buffer[:end_index] = block[self.window_size - self._write_index:]         # write the second part of the block to the beginning of the buffer
            else:
                self._buffer[self._write_index:end_index] = block # write the block to the buffer
            self._write_index = end_index

        rms = sqrt(mean(self._buffer ** 2))
        if rms > self._peak:
            self._peak = rms # instant attack
        else:
            block_duration = len(block) / self.sample_rate
            self._peak *= exp(-block_duration / self.agc_release_s) # exponential decay

        peak = max(self._peak, 2 * self.noise_floor)                   # avoid division by zero and ensure a minimum peak level
        level = clip((rms - noise_floor) / (peak - noise_floor), 0, 1) # Subtracting noise_floor acts as a simple noise gate
        return AudioFeatures(level=float(level))