# server/core/types.py
from pydantic import BaseModel, Field
from enum import Enum

class Target(BaseModel):
    type: str    # 'strip' or 'group'
    id: int
    
    def as_key(self) -> tuple[str, int]:
        return (self.type, self.id)

class ColorModel(BaseModel):
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)

class Layer(str, Enum):
    COLOR     = "color"
    INTENSITY = "intensity"
    WHITE     = "white"