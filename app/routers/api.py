from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import secrets

from app.database import get_db
from app.config import settings
from app.models import Player, Order, SANDWICH_OPTIONS, FRUIT_OPTIONS

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

router = APIRouter(prefix="/api")


class OrderCreate(BaseModel):
    player_id: int
    day: str
    sandwich_1: str
    sandwich_2: str
    sandwich_3: str
    fruit: str


class OrderResponse(BaseModel):
    id: int
    player_id: int
    player_name: str
    category: str
    day: str
    sandwich_1: str
    sandwich_2: str
    sandwich_3: str
    fruit: str


@router.get("/players")
async def get_players(q: str = "", db: AsyncSession = Depends(get_db)):
    query = select(Player).order_by(Player.category, Player.name)
    if q:
        query = query.where(Player.name.ilike(f"%{q}%"))
    result = await db.execute(query)
    players = result.scalars().all()
    return [{"id": p.id, "name": p.name, "category": p.category} for p in players]


@router.get("/players/{player_id}/orders")
async def get_player_orders(player_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.player_id == player_id))
    orders = result.scalars().all()
    return [
        {
            "id": o.id,
            "day": o.day,
            "sandwich_1": o.sandwich_1,
            "sandwich_2": o.sandwich_2,
            "sandwich_3": o.sandwich_3,
            "fruit": o.fruit,
        }
        for o in orders
    ]


@router.post("/orders")
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    sandwiches = [order.sandwich_1, order.sandwich_2, order.sandwich_3]
    for s in sandwiches:
        if s not in SANDWICH_OPTIONS:
            raise HTTPException(400, f"Ongeldig broodje: {s}")
    if order.fruit not in FRUIT_OPTIONS:
        raise HTTPException(400, f"Ongeldig fruit: {order.fruit}")
    if order.day not in ("zaterdag", "zondag"):
        raise HTTPException(400, "Dag moet 'zaterdag' of 'zondag' zijn")

    player = await db.get(Player, order.player_id)
    if not player:
        raise HTTPException(404, "Speler niet gevonden")

    existing = await db.execute(
        select(Order).where(Order.player_id == order.player_id, Order.day == order.day)
    )
    existing_order = existing.scalar_one_or_none()

    if existing_order:
        existing_order.sandwich_1 = order.sandwich_1
        existing_order.sandwich_2 = order.sandwich_2
        existing_order.sandwich_3 = order.sandwich_3
        existing_order.fruit = order.fruit
    else:
        existing_order = Order(
            player_id=order.player_id,
            day=order.day,
            sandwich_1=order.sandwich_1,
            sandwich_2=order.sandwich_2,
            sandwich_3=order.sandwich_3,
            fruit=order.fruit,
        )
        db.add(existing_order)

    await db.commit()
    return {"status": "ok", "message": "Bestelling opgeslagen!"}


@router.get("/admin/summary")
async def admin_summary(db: AsyncSession = Depends(get_db), _=Depends(verify_admin)):
    result = await db.execute(
        select(Order, Player).join(Player).order_by(Player.category, Player.name)
    )
    rows = result.all()

    summary = {"zaterdag": {}, "zondag": {}}
    orders_list = []

    for order, player in rows:
        orders_list.append(
            OrderResponse(
                id=order.id,
                player_id=player.id,
                player_name=player.name,
                category=player.category,
                day=order.day,
                sandwich_1=order.sandwich_1,
                sandwich_2=order.sandwich_2,
                sandwich_3=order.sandwich_3,
                fruit=order.fruit,
            )
        )
        day_summary = summary[order.day]
        for s in [order.sandwich_1, order.sandwich_2, order.sandwich_3]:
            day_summary[s] = day_summary.get(s, 0) + 1
        day_summary[order.fruit] = day_summary.get(order.fruit, 0) + 1

    all_players_result = await db.execute(select(Player).order_by(Player.category, Player.name))
    all_players = all_players_result.scalars().all()

    all_orders_result = await db.execute(select(Order.player_id, Order.day))
    players_ordered = {(row.player_id, row.day) for row in all_orders_result.all()}

    missing = []
    for p in all_players:
        for day in ("zaterdag", "zondag"):
            if (p.id, day) not in players_ordered:
                missing.append({"name": p.name, "category": p.category, "day": day})

    return {
        "summary": summary,
        "orders": [o.model_dump() for o in orders_list],
        "missing": missing,
        "total_players": len(all_players),
        "total_orders_saturday": sum(1 for o, _ in rows if o.day == "zaterdag"),
        "total_orders_sunday": sum(1 for o, _ in rows if o.day == "zondag"),
    }


class PlayerCreate(BaseModel):
    name: str
    category: str


@router.post("/admin/players")
async def add_player(player: PlayerCreate, db: AsyncSession = Depends(get_db), _=Depends(verify_admin)):
    name = player.name.strip()
    if not name:
        raise HTTPException(400, "Naam is verplicht")
    if player.category not in ("Trainer", "U13", "U15", "U16", "U17"):
        raise HTTPException(400, "Ongeldige categorie")

    new_player = Player(name=name, category=player.category)
    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)
    return {"status": "ok", "id": new_player.id, "name": new_player.name, "category": new_player.category}


@router.delete("/admin/players/{player_id}")
async def delete_player(player_id: int, db: AsyncSession = Depends(get_db), _=Depends(verify_admin)):
    player = await db.get(Player, player_id)
    if not player:
        raise HTTPException(404, "Speler niet gevonden")
    await db.delete(player)
    await db.commit()
    return {"status": "ok"}


@router.get("/options")
async def get_options():
    return {
        "sandwiches": SANDWICH_OPTIONS,
        "fruit": FRUIT_OPTIONS,
        "days": ["zaterdag", "zondag"],
    }
