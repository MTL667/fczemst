from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

from app.database import engine, Base
from app.config import settings
from app.routers import api
from app.seed import seed_players

security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct = secrets.compare_digest(credentials.password, settings.admin_password)
    if not correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldig wachtwoord",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_players()
    yield


app = FastAPI(title="FC Zemst Sportief - Broodjes Stage", lifespan=lifespan)
app.include_router(api.router)

templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/bestelling/{player_id}", response_class=HTMLResponse)
async def order_page(request: Request, player_id: int):
    return templates.TemplateResponse("order.html", {"request": request, "player_id": player_id})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, _=Depends(verify_admin)):
    return templates.TemplateResponse("admin.html", {"request": request})
