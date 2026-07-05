# server/api/dependencies.py
from fastapi import Depends, HTTPException, Request

from server.core.leds import LedGroup, LedStrip
from server.core.types import Target

def get_state(request: Request):
    return request.app.state.app_state

def get_target(target: Target, state=Depends(get_state)) -> LedStrip | LedGroup:
    match target.type:
        case 'strip':
            if target.id not in state.strips:
                raise HTTPException(status_code=404, detail=f'Strip {target.id} not found')
            return state.strips[target.id]
        case 'group':
            if target.id not in state.groups:
                raise HTTPException(status_code=404, detail=f'Group {target.id} not found')
            return state.groups[target.id]
        case _:
            raise HTTPException(status_code=400, detail=f'Invalid target type {target.type}')