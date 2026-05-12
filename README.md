# FC Zemst Sportief - Broodjes Stage Oostende 2026

Simpele webapplicatie waarmee spelers en staf hun broodjes + fruit kunnen bestellen voor de stage.

## Features

- **Speler-flow**: Zoek je naam → selecteer 3 broodjes + 1 fruit → voor zaterdag en zondag
- **Admin-paneel**: Overzicht van aantallen per type, wie nog niet besteld heeft, en volledige bestellijst

## Tech Stack

- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **Frontend**: HTML + Tailwind CSS
- **Deployment**: Docker

## Lokaal draaien

```bash
docker compose up --build
```

App beschikbaar op `http://localhost:8000`

## Easypanel Deployment

1. Maak een nieuw project aan in Easypanel
2. Voeg een PostgreSQL service toe:
   - Database naam: `broodjes`
   - User: `postgres`
   - Password: kies een sterk wachtwoord
3. Voeg een App service toe (Docker):
   - Verwijs naar je git repo of upload de code
   - Stel de environment variable in:
     ```
     DATABASE_URL=postgresql+asyncpg://postgres:JOUW_WACHTWOORD@POSTGRES_SERVICE_NAAM:5432/broodjes
     ```
   - Poort: `8000`
4. De app maakt automatisch de database tabellen aan en vult de spelerslijst in bij eerste opstart

## Broodjes-opties

| Type | Varianten |
|------|-----------|
| Pistolet | kaas, hesp, kip, salami |
| Sandwich | kaas, hesp, kip, salami |

## Fruit-opties

- Appel
- Banaan

## Regels

- 3 broodjes per dag per persoon
- 1 stuk fruit per dag per persoon
- Dezelfde keuze meerdere keren is toegestaan
