# server/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from server.database import Database
from server.core.state import AppState
from server.api.routes.leds import router as leds_router
from server.api.routes.modules import router as modules_router
from server.api.models import ModuleTarget

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    db = Database('server/database/leds.db')
    state = AppState(db)
    app.state.app_state = state
    await state.startup()
    
    
    yield

    for strip_id in list(state.strips.keys()):
        await state.remove_strip(strip_id)
    db.close()

app = FastAPI(title='Led Controller', lifespan=lifespan)
app.include_router(leds_router)
app.include_router(modules_router)