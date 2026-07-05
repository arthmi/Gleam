# server/api/routes/scenes.py
from fastapi import APIRouter, Depends, HTTPException
import json

from server.api.dependencies import get_state
from server.core.module_loader import build_class_to_name
from server.api.models import SceneRequest, StartModuleRequest
from server.core.types import Target, Layer

router = APIRouter(prefix='/scenes', tags=['scenes'])

@router.get('')
def get_scenes(state=Depends(get_state)):
    scenes = state.db.get_scenes()
    return [{'id': scene[0], 'name': scene[1]} for scene in scenes]

@router.get('/{scene_id}')
def get_scene(scene_id: str, state=Depends(get_state)):
    modules = state.db.get_scene_modules(scene_id)
    if not modules:
        raise HTTPException(status_code=404, detail=f'Scene {scene_id} not found')
    return [
        {'id': module[0], 'scene_id': module[1], 'strip_id': module[2], 'group_id': module[3], 'layer': module[4], 'module_name': module[5], 'params': json.loads(module[6])}
        for module in modules
        ]

@router.post('/{scene_id}/start')
async def start_scene(scene_id: str, state=Depends(get_state)):
    modules = state.db.get_scene_modules(scene_id)
    if not modules:
        raise HTTPException(status_code=404, detail=f'Scene {scene_id} not found')
    class_to_name = build_class_to_name()
    for module in modules:
        params = json.loads(module[6])
        module_name = class_to_name[module[5]]
        request = StartModuleRequest(target_type='group', target_id=module[3], layers=module[4], params=params)
        await state.start_module(module_name, request.as_target(), request.params, request.layers)
    return {'status': 'success', 'message': f'Scene {scene_id} started successfully'}


@router.post('')
def create_scene(scene_name: str, state=Depends(get_state)):
    modules = state.active_modules
    scene_id = state.db.add_scene(scene_name, modules)
    return {'status': 'success', 'message': f'Scene {scene_id} created successfully'}

@router.put('/{scene_id}')
def update_scene(scene_id: str, request: SceneRequest, state=Depends(get_state)):
    state.db.update_scene(scene_id, request.name, request.module_name, request.params)
    return {'status': 'success', 'message': f'Scene {scene_id} updated successfully'}

@router.delete('/{scene_id}')
def delete_scene(scene_id: int, state=Depends(get_state)):
    state.db.delete_scene(scene_id)
    return {'status': 'success', 'message': f'Scene {scene_id} deleted successfully'}