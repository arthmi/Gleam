# rainbow/main.py
import colorsys
from server.core.module_base import ModuleBase
from server.core.types import Layer
from server.api.models import ColorModel

class RainbowModule(ModuleBase):
    def __init__(self, target, clock, params):
        super().__init__(target, clock, params, layers=[Layer.COLOR])
        self.every_n_frames = round(1 / params.get('fps', 60) * clock.fps)

    async def run(self):
        while self.running:
            await self.clock.wait()
            base_hue = (self.clock.frame * self.params['speed'] / self.clock.fps) % 1.0
            if self.clock.frame % self.every_n_frames == 0:
                for i in range(self.target.num_leds):
                    hue = (base_hue + i * self.params['spread'] / self.target.num_leds) % 1.0
                    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    self._set_color(ColorModel(r=int(r*255), g=int(g*255), b=int(b*255)))
                    self.target.show()