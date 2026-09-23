# server/core/state.py
import asyncio

from server.database import Database
from server.core.leds import LedStrip, LedGroup
from server.core.module_loader import load_module
from server.core.types import Target, ColorModel, Layer
from server.core.clock import Clock

class AppState:
    def __init__(self, db: Database):
        self.db = db
        self.clock = Clock(fps=60)
        self.strips: dict[int, LedStrip]={}
        self.groups: dict[int, LedGroup]={}
        self.active_modules: dict={}

    async def startup(self):
        self._load_from_db()
        self._load_active_modules()
        asyncio.create_task(self.clock.run())


    def _load_from_db(self) -> None:
        strips = self.db.get_strips()
        self.strips = {
            strip[0]: LedStrip(strip[0], strip[1], strip[2])
            for strip in strips
        }
        groups = self.db.get_groups()
        for group in groups:
            self.groups[group[0]] = LedGroup(group[0], group[1], self.strips[group[2]], group[3], group[4])
            self.strips[group[2]].groups[group[0]] = self.groups[group[0]]

    def _load_active_modules(self) -> None:
        for strip_id in self.strips.keys():
            self.active_modules[strip_id] = {}
        for group in self.groups.values():
            self.active_modules[group.strip.id][group.id] = {
                Layer.COLOR: None,
                Layer.INTENSITY: None,
                Layer.WHITE: None
            }


    def add_strip(self, name: str, num_leds: int) -> LedStrip:
        strip_id = self.db.add_strip(name, num_leds)
        if not strip_id:
            raise RuntimeError(f'Failed to insert strip `{name}` into database')
        strip = LedStrip(strip_id, name, num_leds)
        self.strips[strip_id] = strip
        self.active_modules[strip_id] = {}
        return strip

    def update_strip(self, id: int, name: str, num_leds: int) -> LedStrip:
        self.db.update_strip(id, name, num_leds)
        strip = self.strips[id]
        strip.name = name
        if strip.num_leds != num_leds:
            strip.num_leds = num_leds
            strip.color_buffer = [ColorModel(r=0, g=0, b=0)] * num_leds
            strip.white_buffer = [0] * num_leds
            strip.intensity_buffer = [1.0] * num_leds
        return strip

    async def remove_strip(self, id: int) -> None:
        await self.stop_module(Target(type='strip', id=id))
        for group_id in list(self.strips[id].groups.keys()):
            del self.groups[group_id]
        self.db.delete_strip(id)
        del self.active_modules[id]
        del self.strips[id]


    def add_group(self, name: str, strip_id: int, start: int, end: int) -> LedGroup:
        group_id = self.db.add_group(name, strip_id, start, end)
        strip = self.strips[strip_id]
        if not group_id:
            raise RuntimeError(f'Failed to insert group `{name}` into database')
        group = LedGroup(group_id, name, strip, start, end)
        self.groups[group_id] = group
        strip.groups[group_id] = group
        self.active_modules[strip_id][group_id] = {
            Layer.COLOR: None,
            Layer.INTENSITY: None,
            Layer.WHITE: None
        }
        return group

    def update_group(self, id, name, start, end) -> LedGroup:
        self.db.update_group(id, name, start, end)
        group = self.groups[id]
        group.name = name
        group.start = start
        group.end = end        
        return group

    async def remove_group(self, group_id: int) -> None:
        await self.stop_module(Target(type='group', id=group_id))
        self.db.delete_group(group_id)
        del self.active_modules[self.groups[group_id].strip.id][group_id]
        del self.groups[group_id]

       

    async def start_module(self, module_name: str, target: Target, params: dict={}, layers: list[str]|None=None) -> None:
        match target.type:
            case 'strip':
                if target.id not in self.strips:
                    raise ValueError(f'Strip with id {target.id} does not exist')
                groups = self.active_modules[target.id]
                for group_id, _ in groups.items():
                    await self.start_module(
                        module_name,
                        Target(
                            type='group',
                            id=group_id
                        ),
                        params,
                        layers
                    )
            case 'group':
                obj = self.groups[target.id]
                module = load_module(module_name, obj, self.clock, params)
                if layers:
                    module.layers = layers
                group_layers = self.active_modules[self.groups[target.id].strip.id][target.id]
                modules_to_update = {}
                for layer in module.layers:
                    existing = group_layers.get(layer)
                    if existing:
                        existing_module, existing_task = existing
                        modules_to_update[id(existing_module)] = (existing_module, existing_task)
                        if layer in existing_module.layers:
                            existing_module.layers.remove(layer)
                for existing_module, existing_task in modules_to_update.values():
                    if not existing_module.layers:
                        await existing_module.stop()
                        existing_task.cancel()
                        try:
                            await existing_task
                        except asyncio.CancelledError:
                            pass
                task = asyncio.create_task(module.start())
                for layer in module.layers:
                    self.active_modules[self.groups[target.id].strip.id][target.id][layer] = (module, task)
            case _:
                raise ValueError(f'Invalid target type: {target.type}')

    async def stop_module(self, target: Target) -> None:
        match target.type:
            case 'strip':
                if target.id not in self.strips:
                    raise ValueError(f'Strip with id {target.id} does not exist')
                for group_id, _ in self.active_modules[target.id].items():
                    await self.stop_module(
                        Target(
                            type='group',
                            id=group_id
                        ),
                    )
                # tree[target.id] = {}
            case 'group':
                if target.id not in self.groups:
                    raise ValueError(f'Group with id {target.id} does not exist')
                strip_id = self.groups[target.id].strip.id
                layers = self.active_modules[strip_id][target.id]
                modules_to_stop = set()
                for layer, entry in layers.items():
                    if not entry:
                        continue
                    modules_to_stop.add(entry)
                    self.active_modules[strip_id][target.id][layer] = None
                for module, task in modules_to_stop:
                    await module.stop()
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            case _:
                raise ValueError(f'Invalid target type: {target.type}')
