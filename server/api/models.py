# server/api/models.py
from pydantic import BaseModel, Field

from server.core.types import Layer, Target

class StripResponse(BaseModel):
    id: int
    name: str
    num_leds: int = Field(..., gt=0)

class GroupResponse(BaseModel):
    id: int
    name: str
    strip_id: int
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)


class StartModuleRequest(BaseModel):
    target_type: str
    target_id: int
    layers: set[Layer]|None = None
    params: dict = {}

    def as_target(self) -> Target:
        return Target(type=self.target_type, id=self.target_id)


class StripRequest(BaseModel):
    name: str
    num_leds: int = Field(..., gt=0)


class GroupRequest(BaseModel):
    name: str
    strip_id: int
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)

class FreezeRequest(BaseModel):
    layers: set[Layer] | None = None