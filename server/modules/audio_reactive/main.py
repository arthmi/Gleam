# audio_reactive/main.py
import math
import time

from server.core.module_base import ModuleBase
from server.core.types import ColorModel, Layer

from server.modules.audio_reactive.capture import AudioCapture

GAMMA = 2.0

class AudioReactiveModule(ModuleBase):
    def __init__(self, target, clock, params):
        super().__init__(target, clock, params, layers=[Layer.COLOR, Layer.INTENSITY])
        self._capture: AudioCapture | None = None
        self._smoothed = 0.0

    async def run(self):
        self._capture = AudioCapture.acquire(self.params['device'])
        try:
            last = time.monotonic()
            while self.running:
                await self.clock.wait()
                dt = 1 / self.clock.fps                               # time since last frame
                level = self._capture.latest().level                  # get the latest audio level 
                target = min(1.0, level * self.params['sensitivity']) # scale the level by sensitivity
                
                tau = self.params['attack']/1000 if target > self._smoothed else self.params['release']/1000 # choose attack or release smoothing
                alpha = 1.0 if tau <= 0 else 1 - math.exp(-dt / tau)                                         # calculate the smoothing factor
                self._smoothed += (target - self._smoothed) * alpha                                          # move the level toward the target

                shaped = self._smoothed ** GAMMA                                                                                  # apply gamma shaping to the smoothed level
                intensity = self.params['min_intensity'] + (self.params['max_intensity'] - self.params['min_intensity']) * shaped # map the shaped level to the intensity range
                
                self._set_intensity(intensity)
                self.target.show()
                
        finally:
            self._capture.release()
            self._capture = None