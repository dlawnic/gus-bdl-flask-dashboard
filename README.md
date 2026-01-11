# GUS BDL – raport rynku pracy (Flask)

Projekt zaliczeniowy: analiza danych statystycznych z GUS (Bank Danych Lokalnych) i prezentacja wyników w aplikacji webowej Flask dostępnej po zalogowaniu.

## Funkcje
- Rejestracja / logowanie / wylogowanie (baza SQLite)
- Pobieranie danych z **API BDL** (fetch) i cache lokalny (offline po pierwszym pobraniu)
- Wykresy (matplotlib) + tabele (pandas) w `/dashboard` oraz `/report`
- Testy (pytest)
- Docker (docker-compose)

## Uruchomienie lokalne (VS Code)
1) `python -m venv .venv`  
2) aktywuj venv i zainstaluj: `pip install -r requirements.txt`  
3) `cp .env.example .env` (Windows: `copy .env.example .env`) i ustaw `SECRET_KEY`  
4) Start: `python run.py` → `http://localhost:8000`

> Baza SQLite tworzy się automatycznie w `instance/app.sqlite3`.

> Uwaga: API BDL ma limity zapytań dla użytkowników anonimowych. Opcjonalnie ustaw `BDL_CLIENT_ID` w `.env`.

## Testy
`pytest -q`

## Docker
`cp .env.example .env` (Windows: `copy .env.example .env`)  
`docker compose up --build` → `http://localhost:8000`

## Struktura
- `app/` – aplikacja Flask
- `app/data/` – klient API BDL + cache + analiza
- `docs/report.md` – dokumentacja projektu
- `tests/` – testy
