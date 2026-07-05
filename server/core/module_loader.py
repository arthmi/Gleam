# server/core/module_loader.py
import importlib.util
import json
from pathlib import Path

from server.core.clock import Clock


MODULES_DIR = Path(__file__).parent.parent / 'modules'

def discover_modules() -> dict:
    if not MODULES_DIR.exists():
        print(f'Modules directory {MODULES_DIR} does not exist. Creating it.')
        MODULES_DIR.mkdir()
    modules = {}
    for dir in MODULES_DIR.iterdir():
        if not dir.is_dir():
            continue
        for file in dir.iterdir():
            if file.name == 'module.json':
                with open(file) as f:
                    modules[dir.name] = json.load(f)
    return modules

def _import_module(module_path: Path, entry_file: str):
    spec = importlib.util.spec_from_file_location(module_path.stem, module_path / entry_file)
    if spec is None:
        raise ImportError(f'Could not load module from {module_path}')
    mod = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(f'No loader found for module {module_path}')
    spec.loader.exec_module(mod)
    return mod

def load_module(module_name: str, target, clock: Clock, params: dict={}):
    module_path = MODULES_DIR / module_name
    if not module_path.exists():
        raise ImportError(f'Module {module_name} not found')
    metadata = discover_modules()
    default_params = {
        param["name"]: param["default"]
        for param in metadata[module_name]["parameters"]
    }
    params = {**default_params, **params}
    if module_name not in metadata:
        raise ImportError(f'Metadata for module {module_name} not found')
    mod = _import_module(module_path, metadata[module_name]['entry'])
    module_class = getattr(mod, metadata[module_name]['class'])
    return module_class(target, clock, params)

def build_class_to_name(registry: dict | None = None) -> dict:
    registry = registry or discover_modules()
    return {meta['class']: name for name, meta in registry.items()}