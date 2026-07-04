# server/api/models.py
from pydantic import BaseModel, Field

from server.core.types import Layer, Target, ColorModel

class StripResponse(BaseModel):
    id: int
    name: str
    num_leds: int

class GroupResponse(BaseModel):
    id: int
    name: str
    strip_id: int
    start: int
    end: int


class StartModuleRequest(BaseModel):
    target_type: str
    target_id: int
    layers: set[Layer]|None = None
    params: dict = {}

    def as_target(self) -> Target:
        return Target(type=self.target_type, id=self.target_id)


class CreateStripRequest(BaseModel):
    name: str
    num_leds: int

class UpdateStripRequest(BaseModel):
    name: str
    num_leds: int

class CreateGroupRequest(BaseModel):
    name: str
    strip_id: int
    start: int
    end: int

class UpdateGroupRequest(BaseModel):
    name: str
    start: int
    end: int

class FreezeRequest(BaseModel):
    layers: set[Layer] | None = None