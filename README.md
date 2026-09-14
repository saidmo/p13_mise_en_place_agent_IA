# Agent IA – Ouvertures d'échecs (POC FFE)

POC d'un agent IA conversationnel aidant de jeunes joueurs à travailler
les ouvertures d'échecs.

## Stack
- Backend : FastAPI, LangGraph, Milvus, MongoDB
- Frontend : Angular
- Orchestration : Docker Compose

## Lancer le projet (dev)
1. `cp .env.example .env`
2. `docker compose up --build`
3. API : http://localhost:9000 — doc : http://localhost:9000/docs