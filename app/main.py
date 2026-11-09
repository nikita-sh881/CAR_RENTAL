import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.bootstrap import ensure_admin_exists
from app.routers import auth, cars, orders, users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("car_rental")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    try:
        ensure_admin_exists()
    except Exception:
        logger.exception("Bootstrap admin failed, continuing startup")
    yield


app = FastAPI(title="Car Rental API", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(cars.router)
app.include_router(orders.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")