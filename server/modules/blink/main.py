# blink/main.py
from server.core.module_base import ModuleBase
from server.core.types import ColorModel, Layer

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
                        self._set_color(self.params['main_color'])
                        self._set_intensity(self.params['secondary_intensity'])
                        self._is_on = True
                    case 0:
                        self._set_color(self.params['secondary_color'])
                        self._set_intensity(self.params['main_intensity'])
                        self._is_on = False
                self.target.show()