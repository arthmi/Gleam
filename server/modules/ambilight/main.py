# main.py
import time
import numpy as np
from server.core.module_base import ModuleBase
from server.core.types import ColorModel, Layer
from server.modules.ambilight.capture import AmbilightCapture
from server.modules.ambilight.pipeline import extract_band, sample_led_colors, apply_saturation_boost, TemporalSmoother


class AmbilightModule(ModuleBase):
    def __init__(self, target, clock, params: dict):
        super().__init__(target, clock, params, layers=[Layer.COLOR])
        self._capture: AmbilightCapture = AmbilightCapture.get_instance(self.params['device_index'])
        self._smoother: TemporalSmoother = TemporalSmoother(
            num_leds=target.num_leds, tau=self.params['temporal_smoothing_tau']
        )
        self._last_frame_time: float|None = None

    async def run(self) -> None:
        self._capture.acquire()
        self._smoother.reset()
        try:
            while self.running:
                await self.clock.wait()
                raw_frame = self._capture.get_latest_frame()
                if raw_frame is None:
                    continue
                band = extract_band(raw_frame, self.params['edge'], self.params['band_depth_percent'])
                colors = sample_led_colors(
                    band, self.params['edge'], self.target.num_leds,
                    self.params['weight_exponent'], self.params['sample_overlap_percent'],
                )
                if self.params['reversed']:
                    colors = colors[::-1]
                colors = apply_saturation_boost(colors, self.params['saturation_boost'])

                now = time.time()
                dt = 0.0 if self._last_frame_time is None else now - self._last_frame_time
                self._last_frame_time = now
                colors = self._smoother.smooth(colors, dt)

                colors_uint8 = np.clip(colors, 0, 255).astype(np.uint8)
                colors_rgb = colors_uint8[:, ::-1]
                for i in range(self.target.num_leds):
                    self._set_pixel(i, color=ColorModel(r=colors_uint8[i][2], g=colors_uint8[i][1], b=colors_uint8[i][0]))
                self.target.show()
        finally:
            self._capture.release()