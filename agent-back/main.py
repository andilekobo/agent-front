import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

# Basic logging configuration for the application
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("careerops")

app = FastAPI(title="CareerOps API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "CareerOps backend is running"
    }


@app.on_event("startup")
async def on_startup():
    logger.info("CareerOps backend starting up")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("CareerOps backend shutting down")
