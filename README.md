# Led Controller

Personal smart lighting system for SK6812 RGBW LED strips. Controlled via a mobile web app on the local network.

Built for a Raspberry Pi 4B running a FastAPI server, with a React PWA as the interface.

---

## What it does

The system lets you control addressable LED strips installed throughout a room. Strips are split into named groups (e.g. "desk", "ceiling", "headboard"), each independently controllable. Modules can drive these groups with dynamic effects — reacting to audio, video, time of day, or whatever else.

Currently working:

- Strip and group management (define ranges, name them, persist to SQLite)
- Plugin-based module system, modules are isolated and independently activatable
- REST API via FastAPI
- React PWA frontend (offline-first, LAN only)