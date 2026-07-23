# ambilight/main.py
from server.core.module_base import ModuleBase
from server.core.clock import Clock
from server.core.types import ColorModel, Layer
from server.modules.ambilight.capture import AmbilightCapture
from server.modules.ambilight.edges import Edge, get_edge_colors


class AmbilightModule(ModuleBase):
    def __init__(self, target, clock: Clock, params: dict = {}, layers=[Layer.COLOR]) -> None:
        super().__init__(target, clock, params, layers)
        self.capture = AmbilightCapture.get_instance(
            device_index=self.params.get("device_index", 0),
        )

    async def run(self):
        while self.running:
            await self.clock.wait()
            frame = self.capture.get_latest_frame()
            if frame is None:
                continue
            edge = get_edge_colors(
                frame,
                Edge(self.params['edge']),
                self.params['band_depth_percent'],
                self.target.num_leds,
                self.params['reversed'],
                self.params['weight_exponent'],
                self.params['blur_sigma']
            )
            for pixel, color in enumerate(edge):
                self._set_pixel(pixel=pixel, color=ColorModel(r=round(color[0]), g=round(color[1]), b=round(color[2])))
            self.target.show()