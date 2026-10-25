# Gestor de Recomendaciones Turísticas — Manizales

Monorepo con dos capas independientes:

```
.
├── backend/    FastAPI + asyncpg + PostgreSQL/PostGIS + Groq
└── frontend/   React + Vite (SPA)
```

No hay dependencias ni configuraciones compartidas entre capas.

## 1. Crear la estructura desde cero

```powershell
mkdir manizales-tours
cd manizales-tours
mkdir backend, frontend

# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
Copy-Item .env.example .env
cd ..

# Frontend
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

## 2. Base de datos

Requisitos: PostgreSQL con la extensión PostGIS disponible.

```powershell
createdb manizales_tours
psql -d manizales_tours -f backend/db/seed_places.sql
```

El esquema crea la tabla `places` con geometría `GEOGRAPHY(POINT, 4326)`,
categorías jerárquicas e índices GIST/GIN para búsquedas espaciales.

## 3. Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env    # edite DATABASE_URL y GROQ_API_KEY
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Variables soportadas (solo por entorno / `.env`, nunca en código):

| Variable | Obligatoria | Default |
| --- | --- | --- |
| `DATABASE_URL` | Sí | — |
| `GROQ_API_KEY` | No | — (si falta, responde sin enriquecimiento IA) |
| `GROQ_MODEL` | No | `openai/gpt-oss-20b` |
| `GROQ_BASE_URL` | No | `https://api.groq.com/openai/v1` |
| `GROQ_TIMEOUT_SECONDS` | No | `12` |
| `FRONTEND_ORIGINS` | No | `http://localhost:5173` (lista separada por comas) |

La consulta de lugares usa `ST_DWithin` para el radio y el operador KNN
`geom <-> point` para ordenar por distancia. El pool de `asyncpg` se crea al iniciar
la aplicación y se cierra al apagarla.

### Endpoints

#### `GET /api/v1/places/recommendations`

| Query | Default | Límites |
| --- | --- | --- |
| `category` | `tourism.sights` | patrón `^[a-z0-9._]+$` |
| `latitude` | `5.068` | -90 a 90 |
| `longitude` | `-75.517` | -180 a 180 |
| `radius_m` | `5000` | 100 a 50000 |
| `limit` | `20` | 1 a 50 |
| `preferences` | — | texto para Groq (ordena y justifica) |

Respuesta (DTO simplificado, enriquecido opcionalmente con Groq):

```json
{
  "city": "Manizales",
  "count": 1,
  "places": [
    {
      "name": "Catedral Basílica de Manizales",
      "category": "tourism.sights",
      "latitude": 5.0675,
      "longitude": -75.5167,
      "reason": "Icono histórico y arquitectónico de Manizales..."
    }
  ],
  "ai_enriched": true,
  "ai_model": "openai/gpt-oss-20b",
  "fallback_reason": null
}
```

#### `POST /api/v1/chat/assistant`

Recibe `question`, `category`, `latitude`, `longitude`, `radius_m`, `limit` y
`preferences`. Devuelve `answer`, `suggested_places`, `places_count`, `ai_enriched`,
`ai_model` y `fallback_reason`.

Errores: `503` base de datos/configuración no disponible, `504` timeout del servicio
externo, `502` respuesta inválida de Groq, `422` parámetros inválidos.

### Pruebas (deterministas, sin red ni base de datos real)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

Las pruebas usan un fake de `PlaceSource` y reemplazan el pool de `asyncpg`, por lo que
no requieren PostgreSQL ni consumen servicios externos.

## 4. Frontend

```powershell
cd frontend
npm install
npm run dev          # DEV  -> .env.development
npm run dev:qa       # QA   -> .env.qa
npm run build:prod   # PROD -> .env.production
```

`VITE_API_BASE_URL` define el backend por entorno. Solo variables `VITE_*` llegan al
navegador; jamás incluya credenciales allí.

## 5. Seguridad

- `.env` está en `.gitignore`; solo se versiona `.env.example` sin valores reales.
- Inyectar `DATABASE_URL` y `GROQ_API_KEY` con el gestor de secretos del proveedor cloud
  (SSM, Secrets Manager, Vault) en lugar de un archivo `.env` en producción.
- CORS restringido a los orígenes definidos en `FRONTEND_ORIGINS`.
- Timeouts explícitos y mapeo de errores a códigos HTTP propios.

## 6. Próximos pasos (CI/CD)

```yaml
# ejemplo de pipeline
backend: pip install -r requirements-dev.txt && pytest
frontend: npm ci && npm run lint && npm run build:qa
```
