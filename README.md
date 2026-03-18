# PDF Viewer + Event Tracker App

Este repositório contém uma aplicação completa com:

- Backend FastAPI (upload PDF, token, servir PDF, eventos)
- Frontend React + Vite (viewer PDF, track page views/events)

## Estrutura

- `backend/`: API FastAPI
- `frontend/`: app React

## Como rodar

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Acesse: `http://localhost:5173/?doc=<token>` (ou porta que o Vite escolher).

## Como testar rápido

1. Faça upload pelo backend:

```bash
curl -X POST "http://localhost:8000/api/upload" -F "file=@path/to/seu.pdf"
```

2. Use o token retornado no frontend:

`http://localhost:5173/?doc=<token>`

## Endpoints principais

- `POST /api/upload` (Upload de PDF)
- `GET /api/document/{token}` (Retorna URL do PDF)
- `GET /api/pdf/{token}` (Serve PDF)
- `POST /api/events` (Recebe eventos de tracking)

## O que NÃO subir no GitHub

- `backend/venv/`
- `frontend/node_modules/`
- `backend/storage/` (dados runtime)
- `.env`, chaves e credenciais

## Estrutura de eventos monitorados

- `document_open`
- `page_view`
- `page_time`
- `document_close`

## Notas

Se for integrar com outro dashboard, use a API do backend para gerar token/upload e buscar métricas.
