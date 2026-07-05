# server/api/routes/leds.py
from fastapi import APIRouter, Depends

from server.core.types import ColorModel
from server.api.models import FreezeRequest
from server.api.dependencies import get_state, get_target

router = APIRouter(prefix='/leds', tags=['leds'])


@router.post('/color')
async def set_color(color: ColorModel, state=Depends(get_state), target=Depends(get_target)):
    target.set_color(color)
    target.show()
    return {'status': 'success', 'message': f'Strip {target.id} color updated to ({color.r}, {color.g}, {color.b})'}
        
@router.post('/white')
async def set_white(brightness: int, state=Depends(get_state), target=Depends(get_target)):
    target.set_white(brightness)
    target.show()
    return {'status': 'success', 'message': f'Strip {target.id} white updated to ({brightness})'}

@router.post('/intensity')
async def set_intensity(intensity: int, state=Depends(get_state), target=Depends(get_target)):
    target.set_intensity(intensity)
    target.show()
    return {'status': 'success', 'message': f'Strip {target.id} intensity updated to ({intensity})'}

@router.post('/freeze')
async def freeze(body: FreezeRequest, state=Depends(get_state), target=Depends(get_target)):
    target.freeze(body.layers)
    return {'status': 'success', 'message': f'Strip {target.id} frozen with layers {body.layers}'}

@router.post('/unfreeze')
async def unfreeze(body: FreezeRequest, state=Depends(get_state), target=Depends(get_target)):
    target.unfreeze(body.layers)
    return {'status': 'success', 'message': f'Strip {target.id} unfrozen with layers {body.layers}'}