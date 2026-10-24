# Gestor de Recomendaciones Turísticas — Manizales

Monorepo con dos capas independientes:

```
.
├── backend/    FastAPI + httpx + python-dotenv (integración Geoapify)
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
Copy-Item .env.example .env   # complete GEOAPIFY_API_KEY
cd ..

# Frontend
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

## 2. Backend

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env    # edite GEOAPIFY_API_KEY y GROQ_API_KEY
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Variables soportadas (solo por entorno / `.env`, nunca en código):

| Variable | Obligatoria | Default |
| --- | --- | --- |
| `GEOAPIFY_API_KEY` | Sí | — |
| `GROQ_API_KEY` | No | — (si falta, usa solo Geoapify con orden original) |
| `GROQ_MODEL` | No | `openai/gpt-oss-20b` |
| `GROQ_BASE_URL` | No | `https://api.groq.com/openai/v1` |
| `GROQ_TIMEOUT_SECONDS` | No | `12` |
| `GEOAPIFY_BASE_URL` | No | `https://api.geoapify.com` |
| `GEOAPIFY_TIMEOUT_SECONDS` | No | `8` |
| `GEOAPIFY_CONNECT_TIMEOUT_SECONDS` | No | `3` |
| `GEOAPIFY_LANGUAGE` | No | `es` |
| `FRONTEND_ORIGINS` | No | `http://localhost:5173` (lista separada por comas) |

### Endpoint

`GET /api/v1/places/recommendations`

| Query | Default | Límites |
| --- | --- | --- |
| `category` | `tourism.sights` | patrón `^[a-z0-9._]+$` |
| `latitude` | `5.068` | -90 a 90 |
| `longitude` | `-75.517` | -180 a 180 |
| `radius_m` | `5000` | 100 a 50000 |
| `limit` | `20` | 1 a 50 |
| `preferences` | — | texto para Groq (ordena y justifica) |

La consulta a Geoapify usa `filter=circle:{lon},{lat},{radius}` y `categories={category}`.
La API key viaja como `apiKey` en la petición saliente y nunca se registra en logs ni se
devuelve al cliente.

Respuesta (DTO simplificado, enriquecido opcionalmente con Groq):

```json
{
  "city": "Manizales",
  "count": 3,
  "places": [
    {
      "name": "Edificio Alejandro Gutiérrez",
      "category": "tourism.sights",
      "latitude": 5.06788343940026,
      "longitude": -75.51691905581364,
      "reason": "Icono histórico y arquitectónico de Manizales..."
    }
  ],
  "ai_enriched": true,
  "ai_model": "openai/gpt-oss-20b",
  "fallback_reason": null
}
```

  "city": "Manizales",
  "count": 2,
  "places": [
    {
      "name": "Catedral Basílica de Manizales",
      "category": "tourism.sights",
      "latitude": 5.0675,
      "longitude": -75.5167
    }
  ]
}
```

Errores: `502` payload/estado inválido del proveedor, `504` timeout, `503` configuración
faltante, `422` parámetros inválidos.

### Pruebas (deterministas, sin red)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```

`unittest.mock` reemplaza `httpx.AsyncClient.get` y la dependencia del cliente en los tests de
API. Ninguna prueba consume la cuota de Geoapify ni requiere conectividad.

## 3. Frontend

```powershell
cd frontend
npm install
npm run dev          # DEV  -> .env.development
npm run dev:qa       # QA   -> .env.qa
npm run build:prod   # PROD -> .env.production
```

`VITE_API_BASE_URL` define el backend por entorno. Solo variables `VITE_*` llegan al
navegador; jamás incluya la API key allí.

## 4. Seguridad

- `.env` está en `.gitignore`; solo se versiona `.env.example` sin valores reales.
- Rotar `GEOAPIFY_API_KEY` ante cualquier sospecha de exposición.
- En despliegue, inyectar la clave con el gestor de secretos del proveedor cloud (SSM,
  Secrets Manager, Vault) en lugar de un archivo `.env`.
- CORS restringido a los orígenes definidos en `FRONTEND_ORIGINS`.
- Timeouts explícitos y mapeo de errores del proveedor a códigos HTTP propios.

## 5. Próximos pasos (CI/CD)

```yaml
# ejemplo de pipeline
backend: pip install -r requirements-dev.txt && pytest
frontend: npm ci && npm run lint && npm run build:qa
```
