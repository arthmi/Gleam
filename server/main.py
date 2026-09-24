# server/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from server.core.types import Target
from server.database import Database
from server.core.state import AppState

from server.api.routes.leds import router as leds_router
from server.api.routes.targets import router as targets_router
from server.api.routes.modules import router as modules_router
from server.api.routes.scenes import router as screnes_router

if os.environ.get("VERCEL"):
    DB_PATH = '/tmp/gleam.db'
else:
    DB_PATH = 'server/storage/database.db'

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    db = Database(DB_PATH)
    state = AppState(db)
    app.state.app_state = state
    await state.startup()
    
    
    yield

    for strip_id in list(state.strips.keys()):
        await state.stop_module(Target(type='strip', id=strip_id))
    db.close()

app = FastAPI(title='Gleam', lifespan=lifespan)
app.include_router(targets_router)
app.include_router(leds_router)
app.include_router(modules_router)
app.include_router(screnes_router)