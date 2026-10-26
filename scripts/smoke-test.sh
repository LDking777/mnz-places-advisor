#!/usr/bin/env bash
# Prueba de humo: verifica que el frontend y la API de un ambiente responden.
# Uso: ./scripts/smoke-test.sh <URL_FRONTEND> <URL_API>
set -euo pipefail

APP_URL="${1:?Falta la URL del frontend}"
API_URL="${2:?Falta la URL de la API}"
APP_URL="${APP_URL%/}"
API_URL="${API_URL%/}"

check() {
  local name="$1" url="$2" expected="$3"
  for attempt in 1 2 3 4 5; do
    code=$(curl -s -o /tmp/smoke_body -w '%{http_code}' --max-time 20 "$url" || echo 000)
    if [[ "$code" == "200" ]] && grep -q "$expected" /tmp/smoke_body; then
      echo "OK   $name -> $url (HTTP $code)"
      return 0
    fi
    echo "...  $name intento $attempt: HTTP $code, reintentando en 10 s"
    sleep 10
  done
  echo "FAIL $name -> $url"
  return 1
}

check "API /health"        "$API_URL/health" '"status":"ok"'
check "API recomendaciones" "$API_URL/api/v1/places/recommendations?limit=1" '"places"'
check "Frontend"           "$APP_URL/" '<div id="root">'
echo "Prueba de humo superada."
