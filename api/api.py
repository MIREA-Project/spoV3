from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from api_source_dir.db import async_session, init_models
from api_source_dir.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    async with async_session() as session:
        request.state.db = session
        response = await call_next(request)

        # If we got here without exceptions, commit any pending changes
        if hasattr(request.state, "db") and request.state.db.is_active:
            await request.state.db.commit()

        return response


if __name__ == '__main__':
    uvicorn.run("api:app", host="0.0.0.0", port=53474)