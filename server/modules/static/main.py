# static/main.py
from server.core.module_base import ModuleBase
from server.api.models import ColorModel
from server.core.types import Layer

class StaticModule(ModuleBase):
    def __init__(self, target, clock, params):
        super().__init__(target, clock, params, layers=[Layer.COLOR, Layer.INTENSITY])


    async def run(self):
        if self.params['color']:
            self._set_color(ColorModel(**self.params['color']))
        if self.params['intensity']:
            self._set_intensity(self.params['intensity'])
        if self.params['white']:
            self._set_white(self.params['white'])
        self.target.show()