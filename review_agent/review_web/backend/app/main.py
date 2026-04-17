from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import router
from .paths import get_workspace_paths


def create_app() -> FastAPI:
    app = FastAPI(title="Review Web (Survey/Tutorial)")
    app.include_router(router)

    # Same-origin by default; allow localhost dev variations.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://localhost:5173", "http://127.0.0.1", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    paths = get_workspace_paths()
    if paths.frontend_dist_root.exists():
        app.mount("/", StaticFiles(directory=str(paths.frontend_dist_root), html=True), name="frontend")
    return app


app = create_app()

