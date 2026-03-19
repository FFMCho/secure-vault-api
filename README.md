# Secure Vault API

Ein Cloud-Speicher-MVP als Portfolio- und Lernprojekt. Sichere Dateiablage mit pre-signed URLs – Dateitransfer läuft direkt zwischen Client und Object Storage, nicht über den App-Server.

## Tech Stack
- **Backend**: FastAPI
- **Datenbank**: PostgreSQL
- **Object Storage**: S3-kompatibel (MinIO lokal, Cloudflare R2 oder Backblaze B2 produktiv)
- **Auth**: JWT, Rollen (user/admin)
- **Migrationen**: Alembic
- **Betrieb**: Docker Compose

## MVP-Scope
- Registrierung, Login, JWT-Auth
- Upload/Download über pre-signed URLs (kein Dateidurchleitung über App)
- Datei-Liste, Delete, Ownership-Checks
- Audit-Logs für sicherheitsrelevante Aktionen
- MIME-Type- und Größenvalidierung

## Dokumentation
- **[Architektur & Umsetzungsplan](docs/ARCHITECTURE.md)** – Ordnerstruktur, Phasenplan, erste Dateien

## Schnellstart

### Mit Docker Compose (empfohlen)

```bash
# Optional: .env anpassen (Docker setzt eigene Werte)
cp .env.example .env

# Starten – Migrationen laufen automatisch
docker compose up --build

# API:          http://localhost:8000
# Healthcheck:  http://localhost:8000/health
# Swagger Docs: http://localhost:8000/docs
```

### Lokal ohne Docker

PostgreSQL muss laufen (z.B. per `docker compose up postgres -d`):

```bash
# .env anpassen: DATABASE_URL mit localhost statt postgres
cp .env.example .env

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Migrationen manuell

```bash
alembic upgrade head   # Ausführen
alembic revision -m "..."  # Neue Migration (nach Model-Änderung)
alembic autogenerate -m "..."  # Auto aus Models
```

## Projektstruktur

```
app/
├── api/v1/       # Router (health, auth, files, admin)
├── core/         # Security, S3-Storage
├── db/           # Session, Base
├── models/       # User, File, AuditLog
├── schemas/      # Pydantic Request/Response
└── services/     # Business-Logik
```

## API-Endpunkte (Phase 2)

| Methode | Endpunkt | Auth | Beschreibung |
|---------|----------|------|--------------|
| GET | `/health` | - | Healthcheck inkl. DB |
| GET | `/api/v1/health` | - | Wie oben |
| POST | `/api/v1/auth/register` | - | Registrierung |
| POST | `/api/v1/auth/login` | - | Login (JWT) |
| GET | `/api/v1/users/me` | Bearer | Aktueller User |

**Authentifizierung:** `Authorization: Bearer <token>`

## Status
- Phase 0: Projekt-Setup ✅
- Phase 1: DB, Models, Migrationen, API-Grundgerüst ✅
- Phase 2: Auth (Register, Login, JWT, /users/me) ✅
- Phase 3–5: Noch offen
