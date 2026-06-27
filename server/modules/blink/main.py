# blink/main.py
from server.core.module_base import ModuleBase
from server.api.models import ColorModel
from server.core.types import Layer

class BlinkModule(ModuleBase):
    def __init__(self, target, clock, params):
        super().__init__(target, clock, params, layers=[Layer.COLOR, Layer.INTENSITY])
        self.every_n_frames = round(params['delay'] * clock.fps)


    async def run(self):
        while self.running:
            await self.clock.wait()
            is_on = (self.clock.frame // self.every_n_frames) % 2 == 0
            if self.clock.frame % self.every_n_frames == 0:
                match is_on:
                    case 1:
                        self._set_color(ColorModel(r=255, g=255, b=255))
                        self._set_intensity(1.0)
                        self._is_on = True
                    case 0:
                        self._set_color(ColorModel(r=0, g=0, b=0))
                        self._set_intensity(0.0)
                        self._is_on = False
                self.target.show()