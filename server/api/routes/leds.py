# server/api/routes/leds.py
from fastapi import APIRouter, Depends, HTTPException

from server.api.models import ColorModel, StripResponse, GroupResponse, CreateStripRequest, UpdateStripRequest, CreateGroupRequest, UpdateGroupRequest
from server.api.dependencies import get_state

router = APIRouter(prefix='/leds', tags=['leds'])

@router.get('/list')
def get_list(state=Depends(get_state)):
    list = {}
    for strip in state.strips.values():
        list[strip.id] = {
            'name': strip.name,
            'num_leds': strip.num_leds,
            'groups': {}
        }
        for group in strip.groups.values():
            list[strip.id]['groups'][group.id] = {
                'name': group.name,
                'start': group.start,
                'end': group.end
            }
    return list


@router.post('/strip', response_model=StripResponse)
def add_strip(request: CreateStripRequest, state=Depends(get_state)):
    strip = state.add_strip(request.name, request.num_leds)
    return {'id': strip.id, 'name': strip.name, 'num_leds': strip.num_leds}

@router.put('/strip/{strip_id}', response_model=StripResponse)
def update_strip(strip_id: int, request: UpdateStripRequest, state=Depends(get_state)):
    if strip_id not in state.strips:
        raise HTTPException(status_code=404, detail=f'Strip {strip_id} not found')
    strip = state.update_strip(strip_id, request.name, request.num_leds)
    return {'id': strip.id, 'name': strip.name, 'num_leds': strip.num_leds}

@router.delete('/strip/{strip_id}', status_code=204)
async def remove_strip(strip_id: int, state=Depends(get_state)):
    if strip_id not in state.strips:
        raise HTTPException(status_code=404, detail=f'Strip {strip_id} not found')
    await state.remove_strip(strip_id)

@router.get('/strip/{strip_id}', response_model=StripResponse)
def get_strip(strip_id: int, state=Depends(get_state)):
    if strip_id not in state.strips:
        raise HTTPException(status_code=404, detail=f'Strip {strip_id} not found')
    return state.strips[strip_id]


@router.post('/strip/{strip_id}/color')
def set_strips_color(strip_id: int, color: ColorModel, state=Depends(get_state)):
    if strip_id not in state.strips:
        raise HTTPException(status_code=404, detail=f'Strip {strip_id} not found')
    strip = state.strips[strip_id]
    strip.set_color(color)
    strip.show()
    return {'status': 'success', 'message': f'Strip {strip_id} color updated to ({color.r}, {color.g}, {color.b})'}



@router.post('/group', response_model=GroupResponse)
def add_group(request: CreateGroupRequest, state=Depends(get_state)):
    group = state.add_group(request.name, request.strip_id, request.start, request.end)
    return {'id': group.id, 'name': group.name, 'strip_id': group.strip.id, 'start': group.start, 'end': group.end}

@router.put('/group/{group_id}', response_model=GroupResponse)
def update_group(group_id: int, request: UpdateGroupRequest, state=Depends(get_state)):
    if group_id not in state.groups:
        raise HTTPException(status_code=404, detail=f'Group {group_id} not found')
    group = state.update_group(group_id, request.name, request.start, request.end)
    return {'id': group.id, 'name': group.name, 'strip_id': group.strip.id, 'start': group.start, 'end': group.end}

@router.delete('/group/{group_id}', status_code=204)
async def remove_group(group_id: int, state=Depends(get_state)):
    if group_id not in state.groups:
        raise HTTPException(status_code=404, detail=f'Group {group_id} not found')
    await state.remove_group(group_id)

@router.get('/group/{group_id}', response_model=GroupResponse)
def get_group(group_id: int, state=Depends(get_state)):
    if group_id not in state.groups:
        raise HTTPException(status_code=404, detail=f'Group {group_id} not found')
    group = state.groups[group_id]
    return {
        'id': group.id,
        'name': group.name,
        'strip_id': group.strip.id,
        'start': group.start,
        'end': group.end,
    }


@router.post('/group/{group_id}/color')
def set_groups_color(group_id: int, color: ColorModel, state=Depends(get_state)):
    if group_id not in state.groups:
        raise HTTPException(status_code=404, detail=f'Group {group_id} not found')
    group = state.groups[group_id]
    group.set_color(color)
    group.show()
    return {'status': 'success', 'message': f'Group {group_id} color updated to ({color.r}, {color.g}, {color.b})'}
