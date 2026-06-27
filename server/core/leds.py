# server/core/leds.py
from server.core.types import ColorModel
from server.core.module_base import ModuleBase

class LedStrip:
    def __init__(self, id: int, name: str, num_leds: int):
        self.id = id
        self.name = name
        self.num_leds = num_leds
        self.groups: dict[int, LedGroup] = {}
        self.color_buffer: list[ColorModel]= [ColorModel(r=0, g=0, b=0)] * num_leds
        self.white_buffer: list[float]= [0.0] * num_leds
        self.intensity_buffer: list[float]= [1.0] * num_leds

    def set_color(self, color: ColorModel):
        self.color_buffer = [color] * self.num_leds

    def set_white(self, white: float):
        self.white_buffer = [white] * self.num_leds
    
    def set_intensity(self, intensity: float):
        self.intensity_buffer = [intensity] * self.num_leds

    def set_pixel(
            self,
            pixel: int,
            *,
            color: ColorModel|None=None,
            white: float|None=None,
            intensity: float|None=None
        ):
        if pixel < 0 or pixel >= self.num_leds:
            raise ValueError('Pixel index is out of bounds')
        if color is not None:
            self.color_buffer[pixel] = color
        if white is not None:
            self.white_buffer[pixel] = white
        if intensity is not None:
            self.intensity_buffer[pixel] = intensity
        

    def show(self, start: int=0, end: int=-1):
        string = ''
        for pixel, color in enumerate(self.color_buffer[start:end]):
            r, g, b = color.r, color.g, color.b
            intensity = self.intensity_buffer[pixel + start]
            w = self.white_buffer[pixel + start]
            final = (
                int(r * intensity),
                int(g * intensity),
                int(b * intensity),
                int(255 * w * intensity)
            )
            # string += f'\033[38;2;{final[0] + final[3]};{final[1] + final[3]};{final[2] + final[3]}m\u2588\033[0m'
            string += f'\n\033[38;2;{r};{g};{b}m\u2588\u2588\033[0m  '
            string += f'{r = }, {g = }, {b = }, {w = }, {intensity = }'
            print(string)

    def clear(self):
        self.color_buffer = [ColorModel(r=0, g=0, b=0)] * self.num_leds
        self.white_buffer = [0.0] * self.num_leds
        self.intensity_buffer = [1.0] * self.num_leds

class LedGroup:
    def __init__(self, id: int, name: str, strip: LedStrip, start: int, end: int):
        self.id = id
        self.name = name
        self.strip = strip
        self.start = start
        self.end = end
        self.num_leds = end - start

    def set_pixel(self, pixel: int, *, color=None, white=None, intensity=None):
        self.strip.set_pixel(pixel + self.start, color=color, white=white, intensity=intensity)

    def set_color(self, color: ColorModel):
        for pixel in range(self.end - self.start + 1):
            self.strip.set_pixel(pixel + self.start, color=color)

    def set_white(self, white: float):
        for pixel in range(self.end - self.start + 1):
            self.strip.set_pixel(pixel + self.start, white=white)

    def set_intensity(self, intensity: float):
        for pixel in range(self.end - self.start + 1):
            self.strip.set_pixel(pixel + self.start, intensity=intensity)


    def show(self):
        self.strip.show(self.start, self.end)

    def clear(self):
        for pixel in range(self.end - self.start):
            self.strip.set_pixel(pixel + self.start, color=ColorModel(r=0, g=0, b=0), white=0.0, intensity=1.0)