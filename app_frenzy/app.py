from fastapi import FastAPI

from app_frenzy import api

app = FastAPI()

app.include_router(api.router, prefix="/api", tags=["api"])


@app.get("/health")
async def health():
    return {"message": "Alive!"}
