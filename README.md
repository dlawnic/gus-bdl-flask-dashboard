# GUS BDL – Labor Market Dashboard (Flask)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black)
![Docker](https://img.shields.io/badge/Docker-Compose-blue)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)
![pytest](https://img.shields.io/badge/Tests-pytest-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🇵🇱 Opis (PL)

Aplikacja webowa stworzona w Flask, służąca do pobierania, analizy oraz wizualizacji danych statystycznych rynku pracy z Banku Danych Lokalnych GUS (BDL). Projekt zrealizowany jako projekt zaliczeniowy oraz portfolio, z naciskiem na backend, analizę danych oraz dobre praktyki inżynierskie. Dostęp do aplikacji wymaga uwierzytelnienia użytkownika.

## 🇬🇧 Description (EN)

A Flask-based web application for fetching, analyzing, and visualizing labor market statistics from Poland’s GUS Local Data Bank (BDL). Developed as an academic and portfolio project, focusing on backend development, data processing, and clean application architecture. User authentication is required to access analytical views.

## 🎯 Zakres projektu / Project Scope

- integracja z zewnętrznym REST API (GUS BDL)
- przetwarzanie i agregacja danych statystycznych
- wizualizacja danych (wykresy i tabele)
- system uwierzytelniania użytkowników
- testy jednostkowe
- konteneryzacja aplikacji

## ⚙️ Funkcjonalności / Features

- rejestracja, logowanie i wylogowanie użytkowników
- baza danych SQLite (tworzona automatycznie)
- klient API GUS BDL
- lokalny cache danych (tryb offline po pierwszym pobraniu)
- wykresy (matplotlib)
- tabele danych (pandas)
- dashboard analityczny (/dashboard)
- widok raportu (/report)
- testy jednostkowe (pytest)
- Docker i docker-compose

## 🚀 Uruchomienie lokalne / Local Setup

1. Utworzenie środowiska wirtualnego
python -m venv .venv

2. Instalacja zależności
pip install -r requirements.txt

3. Konfiguracja środowiska
cp .env.example .env
Windows:
copy .env.example .env

Wymagana zmienna:
SECRET_KEY=your_secret_key

4. Uruchomienie aplikacji
python run.py

Aplikacja dostępna pod adresem:
http://localhost:8000

Baza danych SQLite tworzona jest automatycznie w:
instance/app.sqlite3

## 🧪 Testy / Tests

pytest -q

## 🐳 Docker

cp .env.example .env
docker compose up --build

http://localhost:8000

## 📁 Struktura projektu / Project Structure

app/
├── data/          # Klient API BDL, cache, analiza danych

├── templates/     # Szablony HTML

├── static/        # Pliki statyczne

docs/
├── report.md      # Dokumentacja projektu

tests/             # Testy jednostkowe

## ⚠️ Uwagi / Notes

API GUS BDL posiada limity zapytań dla użytkowników anonimowych.
Opcjonalna konfiguracja:
BDL_CLIENT_ID=your_client_id

## 🧠 Technologie (CV-ready)

Python, Flask, REST API, SQLite, pandas, matplotlib, pytest, Docker, Docker Compose, konfiguracja środowiskowa (.env)

## 📜 License

MIT License

## 👤 Autor / Author

Projekt edukacyjny i portfolio – Python / Flask / Data Analysis
