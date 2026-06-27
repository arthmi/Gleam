# server/api/routes/modules.py
from fastapi import APIRouter, Depends, HTTPException

from server.api.dependencies import get_state
from server.core.module_loader import discover_modules
from server.api.models import ModuleTarget, StartModuleRequest

router = APIRouter(prefix='/modules', tags=['modules'])

@router.post('/{module_name}/start')
async def start_module(module_name: str, request: StartModuleRequest, state=Depends(get_state)):
    if not module_name in discover_modules():
        raise HTTPException(status_code=404, detail='Module not found')
    await state.start_module(module_name, request.as_target(), request.params, request.layers)
    return {'status': 'success', 'message': f'Module {module_name} started on {request.target_type} {request.target_id} with {request.layers} as layers'}

@router.post('/stop')
async def stop_module(target: ModuleTarget, state=Depends(get_state)):
    await state.stop_module(target)
    return {'status': 'success', 'message': f'Module stopped on {target.type} {target.id}'}

@router.get('/list')
def list_modules():
    return [
    {'name': module['name'], 'description': module['description'], 'parameters': module['parameters']}
        for module in discover_modules().values()
    ]

@router.get('/active')
def get_active_modules(state=Depends(get_state)):
    result = []
    for strip_id, groups in state.active_modules.items():
        for group_id, layers in groups.items():
            for layer, entry in layers.items():
                if entry:
                    module, _ = entry
                    result.append({
                        'strip_id': strip_id,
                        'group_id': group_id,
                        'layer': layer,
                        'module': module.__class__.__name__,
                        'params': module.params
                    })
    return result