# static/main.py
from server.core.module_base import ModuleBase
from server.api.models import ColorModel
from server.core.types import Layer

class StaticModule(ModuleBase):
    def __init__(self, target, params):
        super().__init__(target, params, layers=[Layer.COLOR, Layer.INTENSITY])


    async def run(self):
        self._set_color(ColorModel(**self.params['color']))
        self._set_intensity(self.params['intensity'])
        self.target.show()