# server/core/types.py
from pydantic import BaseModel, Field

class ModuleTarget(BaseModel):
    type: str    # 'strip' or 'group'
    id: int
    
    def as_key(self) -> tuple[str, int]:
        return (self.type, self.id)

class ColorModel(BaseModel):
    r: int = Field(..., ge=0, le=255)
    g: int = Field(..., ge=0, le=255)
    b: int = Field(..., ge=0, le=255)

class Layer:
    COLOR     = "color"
    INTENSITY = "intensity"
    WHITE     = "white"