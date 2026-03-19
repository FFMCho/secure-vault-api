# Secure Vault API – Architektur & Umsetzungsplan

## 1. Projektanalyse

### Ausgangslage
- **Repository**: Fast leer (nur README, .gitignore)
- **Bisherige Ausrichtung**: Allgemeiner Secure-Backend-Service mit SQLite
- **Neues Ziel**: Cloud-Speicher-MVP mit klarem Scope

### Anforderungen im Überblick
| Bereich | Anforderungen |
|---------|---------------|
| **Auth** | Registrierung, Login, JWT, Rollen (user/admin), Passwort-Hashing |
| **Dateien** | Upload/Download über pre-signed URLs, Liste, Delete, Ownership |
| **Storage** | S3-kompatibel (R2/B2), Dateien NICHT über App-Server |
| **Datenbank** | PostgreSQL, Alembic-Migrationen |
| **Betrieb** | Docker Compose, .env, Healthcheck |
| **Sicherheit** | Audit-Logs, MIME/Size-Validierung, kurze JWT-/URL-Laufzeiten |

### Architektur-Regel: Pre-Signed URLs
Die App leitet Dateien **nicht** weiter. Sie prüft Rechte, validiert, erzeugt pre-signed URLs.  
Der Client tauscht Dateien **direkt** mit dem Object Storage aus. Das reduziert Last, Latenz und Speicherbedarf auf dem App-Server.

---

## 2. Vorgeschlagene Ordnerstruktur

```
secure-vault-api/
├── .env.example                 # Vorlage für Umgebungsvariablen
├── .env                         # (ignoriert, lokal)
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml               # UV/Poetry oder pip + requirements.txt
├── alembic.ini
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI-App, Lifespan
│   ├── config.py                # Pydantic Settings aus .env
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # FastAPI Depends (auth, current_user)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # Aggregiert alle V1-Router
│   │       ├── auth.py          # /auth/register, /auth/login
│   │       ├── users.py         # /users/me
│   │       ├── files.py         # /files/*
│   │       └── admin.py         # (optional) /admin/*
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py          # JWT, Passwort-Hashing
│   │   └── storage.py           # S3-Client, pre-signed URLs
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py           # AsyncSession, get_db
│   │   └── base.py              # DeclarativeBase
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── file.py
│   │   └── audit_log.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── file.py
│   │   └── audit.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── file_service.py
│   │   └── audit_service.py
│   │
│   └── migrations/              # (Alembic) → typisch: alembic/ außerhalb app/
│       └── versions/
│
├── alembic/                     # Alembic-Root (falls außerhalb app/)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures, Test-Client
│   ├── test_auth.py
│   ├── test_files.py
│   └── test_admin.py
│
└── docs/
    ├── ARCHITECTURE.md          # (diese Datei)
    └── API.md                   # (optional) API-Dokumentation
```

### Begründung der Struktur
- **`app/api/v1/`**: Versionierung von Anfang an, einfache Erweiterung auf v2
- **`app/core/`**: Technische Infrastruktur (Security, Storage) getrennt von Business-Logik
- **`app/services/`**: Business-Logik, die Router schlank hält
- **`app/models/` vs `app/schemas/`**: Klare Trennung DB-Modelle ↔ API-Kontrakte
- **`alembic/`**: Üblich, Alembic-Root auf Repo-Ebene zu halten (importiert `app.models`)

---

## 3. Umsetzungsplan in Phasen

### Phase 0: Projekt-Setup (Grundlagen)
**Ziel**: Repo lauffähig machen, ohne Business-Features.

| Schritt | Aktion |
|---------|--------|
| 0.1 | Abhängigkeiten (FastAPI, uvicorn, sqlalchemy, alembic, psycopg, boto3, python-jose, passlib, pydantic-settings) |
| 0.2 | `app/main.py` mit minimalem Healthcheck |
| 0.3 | `app/config.py` mit Pydantic Settings |
| 0.4 | `docker-compose.yml` (PostgreSQL, MinIO oder S3-kompatibel, App) |
| 0.5 | `Dockerfile` für die FastAPI-App |
| 0.6 | `.env.example` mit allen benötigten Variablen |
| 0.7 | Alembic initialisieren, `alembic.ini` anpassen |

**Ergebnis**: `docker compose up` startet App + DB, Healthcheck grün.

---

### Phase 1: Datenbank & Migrationen
**Ziel**: Schema steht, Migrationen laufen.

| Schritt | Aktion |
|---------|--------|
| 1.1 | SQLAlchemy-Modelle: `User`, `File`, `AuditLog` |
| 1.2 | Pydantic-Schemas für API |
| 1.3 | Erste Alembic-Migration (users, files, audit_logs) |
| 1.4 | DB-Session, Dependency `get_db` |

**Ergebnis**: Migration läuft, Tabellen existieren.

---

### Phase 2: Authentifizierung
**Ziel**: Registrierung, Login, JWT, Rollen.

| Schritt | Aktion |
|---------|--------|
| 2.1 | `core/security.py`: Passwort-Hashing (bcrypt), JWT-Erzeugung/-Validierung |
| 2.2 | `api/deps.py`: `get_current_user`, `require_role` |
| 2.3 | `POST /auth/register`, `POST /auth/login` |
| 2.4 | `GET /users/me` (geschützt) |
| 2.5 | `User.last_login_at` bei Login aktualisieren |

**Ergebnis**: User kann sich registrieren, einloggen, `/users/me` aufrufen.

---

### Phase 3: Object Storage & Dateien
**Ziel**: Pre-signed URLs, Datei-Metadaten in PostgreSQL.

| Schritt | Aktion |
|---------|--------|
| 3.1 | `core/storage.py`: S3-Client (boto3), Bucket-Check |
| 3.2 | `POST /files/upload-url`: Validierung (MIME, Größe), pre-signed PUT-URL erzeugen |
| 3.3 | Callback/Webhook ODER client-seitiger Flow: Nach Upload ruft Client `POST /files/confirm` (optional) – alternativ: nur Metadaten beim Request prüfen, pre-signed URL ausgeben |
| 3.4 | `GET /files`: Liste der Dateien des Users |
| 3.5 | `GET /files/{id}/download-url`: Ownership-Check, pre-signed GET-URL |
| 3.6 | `DELETE /files/{id}`: Ownership-Check, Soft-Delete (deleted_at) + optional Object-Storage-Löschung |

**Hinweis**: Beim pre-signed Upload muss der Client entweder:
- Metadaten (filename, content_type, size) mitsenden → Backend validiert und erzeugt URL; danach speichert Backend File-Eintrag (z.B. nach Bestätigung durch Client), **oder**
- Backend erzeugt URL mit erwarteten Metadaten; Client lädt hoch; Backend speichert Metadaten basierend auf Request (ohne Bestätigung).  
Für den MVP reicht: Request enthält filename, content_type, size → Backend validiert → erzeugt pre-signed PUT-URL → speichert File-Eintrag mit `object_key` (z.B. `{user_id}/{uuid}`). Client lädt hoch. Kein separater Confirm-Endpoint nötig.

**Ergebnis**: Upload/Download über pre-signed URLs, Liste, Delete mit Ownership.

---

### Phase 4: Audit & Sicherheit
**Ziel**: Audit-Logs, restliche Sicherheitsmaßnahmen.

| Schritt | Aktion |
|---------|--------|
| 4.1 | `AuditService`: `log(user_id, action, file_id?, ip, user_agent, status, detail)` |
| 4.2 | Middleware/Dependency: IP + User-Agent aus Request extrahieren |
| 4.3 | Audit bei: Login (erfolg/fehlgeschlagen), Datei-Upload-URL, Download-URL, Delete |
| 4.4 | Kurze JWT-Laufzeit (z.B. 15 Min) + Refresh (optional, oder erstmal ohne) |
| 4.5 | Kurze pre-signed URL-Laufzeit (z.B. 5 Min) |

**Ergebnis**: Sicherheitsrelevante Aktionen werden protokolliert.

---

### Phase 5: Admin & Feinschliff
**Ziel**: Admin-Endpunkte, Dokumentation, Tests.

| Schritt | Aktion |
|---------|--------|
| 5.1 | `GET /admin/stats`: Basis-Statistiken (User-Anzahl, Dateien, Speicher) |
| 5.2 | `GET /admin/audit-events`: Filterbare Audit-Logs (nur admin) |
| 5.3 | README aktualisieren, API-Übersicht |
| 5.4 | Unit-/Integration-Tests für Auth, Files, Admin |

**Ergebnis**: MVP vollständig, dokumentiert, getestet.

---

## 4. Erste Dateien im Repository (Reihenfolge)

Empfohlene Reihenfolge beim Anlegen:

| # | Datei | Zweck |
|---|-------|-------|
| 1 | `pyproject.toml` oder `requirements.txt` | Abhängigkeiten definieren |
| 2 | `app/__init__.py` | Package-Marker |
| 3 | `app/config.py` | Zentrale Konfiguration aus .env |
| 4 | `app/main.py` | FastAPI-App, Healthcheck |
| 5 | `.env.example` | Vorlage für Umgebungsvariablen |
| 6 | `docker-compose.yml` | PostgreSQL + MinIO (oder R2-Local) + App |
| 7 | `Dockerfile` | Container für die App |
| 8 | `alembic.ini` | Alembic-Konfiguration |
| 9 | `alembic/env.py` | Alembic mit Async-Support und app.models |
| 10 | `app/db/base.py`, `app/db/session.py` | SQLAlchemy-Setup |
| 11 | `app/models/*.py` | User, File, AuditLog |
| 12 | `app/schemas/*.py` | Pydantic-Schemas |
| 13 | `app/core/security.py` | JWT, Passwort |
| 14 | `app/core/storage.py` | S3-Pre-Signed-URLs |
| 15 | `app/api/deps.py` | Auth-Dependencies |
| 16 | `app/api/v1/auth.py`, `users.py`, `files.py` | Router |
| 17 | `app/services/*.py` | Business-Logik |
| 18 | `tests/conftest.py`, `test_*.py` | Tests |

---

## 5. Kurz-Begründungen

| Entscheidung | Begründung |
|--------------|------------|
| **Async SQLAlchemy** | Skalierbar, passt zu FastAPI |
| **Pydantic Settings** | Validierung und Typsicherheit für Config |
| **api/v1/** | API-Versionierung von Anfang an |
| **Services-Layer** | Router bleiben dünn, Logik testbar |
| **Soft-Delete bei Files** | Einfache Wiederherstellung, Audit-Trail |
| **MinIO in Docker** | Lokal S3-kompatibel ohne Cloud-Konto |
| **Alembic auf Repo-Root** | Standard, saubere Imports |

---

## Nächster Schritt

Sobald du grünes Licht gibst, starten wir mit **Phase 0** und legen die ersten Dateien (1–9) an.
