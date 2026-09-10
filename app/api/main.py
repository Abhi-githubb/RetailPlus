"""
RetailPulse REST API Main Application.
Production-grade FastAPI analytics backend exposing transactional data,
aggregated metrics, and executive KPIs.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from src.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("RetailPulse Analytics REST API initialized and ready to serve traffic.")
    yield
    logger.info("RetailPulse Analytics REST API shutting down.")


app = FastAPI(
    title="RetailPulse E-Commerce Analytics API",
    description="""
    Production-grade analytical REST API for RetailPulse.
    Provides low-latency queries for executive KPIs, sales trajectories, customer cohorts,
    product performance, regional penetration, and data quality metrics.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for Streamlit frontend and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    from src.utils.config import API_HOST, API_PORT
    uvicorn.run("app.api.main:app", host=API_HOST, port=API_PORT, reload=True)
