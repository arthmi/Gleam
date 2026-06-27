# server/api/websocket.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from server.api.dependencies import get_state
from server.api.models import ColorModel, ModuleTarget

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def broadcast(self, message: dict):   # notify all connected clients of an event (e.g., color change)
        for connection in self.connections:
            await self.send(connection, message)

    async def send(self, websocket: WebSocket, message: dict):
        await websocket.send_json(message)
manager = ConnectionManager()

@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, state=Depends(get_state)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await dispatch(data, state, websocket)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

def resolve_target(target: str, id: int, state):
    if target == 'strip':
        return state.strips.get(id)
    elif target == 'group':
        return state.groups.get(id)
    return None

async def dispatch(message: dict, state, websocket):
    target = message.get('target')
    id = message.get('id')
    data = message.get('data')
    if not target or not id or not data:
        await manager.send(websocket, {'status': 'error', 'message': 'Missing target, id or data'})
        return          
    match message.get('type'):
        case 'set_color':
            obj = resolve_target(target, id, state)
            if not obj:
                await manager.send(websocket, {'status': 'error', 'message': f'Target {target} not found'})
                return
            obj.set_color(ColorModel(**data))
            obj.show()
            await manager.broadcast({'status': 'success', 'message': f'{target.__class__.__name__.removeprefix('Led')} {id} color updated to ({data['r']}, {data['g']}, {data['b']}, {data['w']})'})
        case 'clear':
            obj = resolve_target(target, id, state)
            if not obj:
                await manager.send(websocket, {'status': 'error', 'message': f'Target {target} not found'})
                return
            obj.clear()
            obj.show()
            await manager.broadcast({'status': 'success', 'message': f'{target.__class__.__name__.removeprefix('Led')} {id} cleared'})
        case 'get_strips':
            await manager.send(websocket, {'status': 'success', 'data': {strip.id: strip for strip in state.strips.values()}})
        case 'get_groups':
            await manager.send(websocket, {'status': 'success', 'data': {group.id: group for group in state.groups.values()}})
        case 'start_module':
            module_name = data.get('module_name')
            params = data.get('params', {})
            if not module_name:
                await manager.send(websocket, {'status': 'error', 'message': 'Missing module_name in data'})
                return
            await state.start_module(module_name, ModuleTarget(target_type=target, target_id=id), params)
            await manager.broadcast({'status': 'success', 'message': f'Module {module_name} started on {target} {id}'})
        case 'stop_module':
            await state.stop_module(ModuleTarget(target_type=target, target_id=id))
            await manager.broadcast({'status': 'success', 'message': f'Module stopped on {target} {id}'})
        case 'list_modules':
            await manager.send(websocket, {'status': 'success', 'data': [
                {'name': module['name'], 'description': module['description'], 'parameters': module['parameters']}
                for module in state.db.get_modules()
            ]})
        case 'active_modules':
            await manager.send(websocket, {'status': 'success', 'data': state.active_modules})
        case _:
            await manager.send(websocket, {'status': 'error', 'message': f'Unknown message type `{message.get('type')}`'})