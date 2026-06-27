# server/api/dependencies.py
from fastapi import Request

def get_state(request: Request):
    return request.app.state.app_state