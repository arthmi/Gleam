# server/core/module_base.py
from abc import ABC, abstractmethod
from server.core.types import ColorModel, Layer
from server.core.clock import Clock

class ModuleBase(ABC):
    def __init__(self, target, clock: Clock, params: dict={}, layers: list[str]=[Layer.COLOR, Layer.INTENSITY, Layer.WHITE]):
        self.target = target
        self.params = params
        self.layers = layers
        self.clock = clock
        self.running = False

    @abstractmethod
    async def run(self):
        ...
    
    async def start(self):
        self.running = True
        await self.run()

    async def stop(self):
        self.running = False

    def _set_color(self, color: ColorModel):
        if Layer.COLOR in self.layers:
            self.target.set_color(color)

    def _set_intensity(self, intensity: float):
        if Layer.INTENSITY in self.layers:
            self.target.set_intensity(intensity)

    def _set_white(self, white: float):
        if Layer.WHITE in self.layers:
            self.target.set_white(white)

    def _set_pixel(
            self,
            pixel: int,
            *,
            color: ColorModel|None=None,
            white: int|None=None,
            intensity: float|None=None,
        ):
        if color is not None and Layer.COLOR in self.layers:
            self.target.set_pixel(pixel, color=color)
        if intensity is not None and Layer.INTENSITY in self.layers:
            self.target.set_pixel(pixel, intensity=intensity)
        if white is not None and Layer.WHITE in self.layers:
            self.target.set_pixel(pixel, white=white)