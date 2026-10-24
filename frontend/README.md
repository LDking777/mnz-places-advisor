# Frontend — Gestor de Recomendaciones Turísticas

SPA en React + Vite que consume el backend FastAPI.

## Entornos

| Modo | Archivo | Comando |
| --- | --- | --- |
| Desarrollo | `.env.development` | `npm run dev` |
| QA | `.env.qa` | `npm run dev:qa` / `npm run build:qa` |
| Producción | `.env.production` | `npm run build:prod` |

Todas las variables expuestas al navegador deben usar el prefijo `VITE_`. No coloque secretos
en estos archivos: la API key de Geoapify vive solo en el backend.

## Scripts

```bash
npm install
npm run dev
npm run build:qa
npm run lint
```

La URL del backend se configura con `VITE_API_BASE_URL` (ver `.env.example`).
