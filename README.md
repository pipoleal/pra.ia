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

## Deploy do frontend

Na Vercel, configure `frontend` como o **Root Directory**. Esse diretório contém
o `package.json` e a pasta `app` do Next.js. Defina `NEXT_PUBLIC_API_URL` com a
URL pública do backend hospedado no Render.
