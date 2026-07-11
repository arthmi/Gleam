# server/api/routes/leds.py
from fastapi import APIRouter, Depends

from server.core.state import AppState
from server.core.types import ColorModel
from server.api.models import FreezeRequest, DimRequest
from server.api.dependencies import get_target, get_state

router = APIRouter(prefix='/leds', tags=['leds'])


@router.post('/color')
async def set_color(color: ColorModel, target=Depends(get_target)):
    target.set_color(color)
    target.show()
    return {'status': 'success', 'message': f'Strip {target.id} color updated to ({color.r}, {color.g}, {color.b})'}
        
@router.post('/white')
async def set_white(brightness: int, target=Depends(get_target)):
    target.set_white(brightness)
    target.show()
    return {'status': 'success', 'message': f'Strip {target.id} white updated to ({brightness})'}

@router.post('/intensity')
async def set_intensity(intensity: int, target=Depends(get_target)):
    target.set_intensity(intensity)
    target.show()
    return {'status': 'success', 'message': f'Strip {target.id} intensity updated to ({intensity})'}

@router.post('/dim')
async def set_dim(request: DimRequest, state: AppState = Depends(get_state)):
    if not request.targets:
        for t in state.strips.values():
            t.set_dim(request.dim)
            t.show()
    else:
        for t in request.targets:
            get_target(t, state).set_dim(request.dim)
            get_target(t, state).show()


@router.post('/freeze')
async def freeze(body: FreezeRequest, target=Depends(get_target)):
    target.freeze(body.layers)
    return {'status': 'success', 'message': f'Strip {target.id} frozen with layers {body.layers}'}

@router.post('/unfreeze')
async def unfreeze(body: FreezeRequest, target=Depends(get_target)):
    target.unfreeze(body.layers)
    return {'status': 'success', 'message': f'Strip {target.id} unfrozen with layers {body.layers}'}