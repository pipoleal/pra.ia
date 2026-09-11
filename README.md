# praIA

Base de API em FastAPI com PostgreSQL, pronta para executar em containers.

## Executar

```powershell
docker compose up --build
```

A API fica disponível em `http://localhost:8001`.

Endpoints disponíveis:

- `GET /` confirma que a API está online.
- `GET /health` verifica a conexão com o PostgreSQL.
