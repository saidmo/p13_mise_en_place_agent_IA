# Assistant IA – Ouvertures d'échecs (POC)

Proof of Concept d'un agent IA conversationnel qui aide de jeunes joueurs à
travailler leurs **ouvertures d'échecs**. L'utilisateur manipule un échiquier
interactif ; l'agent analyse la position réelle et répond en s'appuyant sur des
**outils déterministes** (jamais sur ses seules connaissances) :

- **Lichess** — coups théoriques joués par les maîtres,
- **Stockfish** — évaluation moteur de la position,
- **RAG (Milvus)** — contexte explicatif des ouvertures,
- **YouTube** — vidéos pédagogiques pertinentes.

Le tout est orchestré par un graphe **LangGraph**, exposé via une API
**FastAPI**, avec persistance et cache dans **MongoDB**, et un front **Angular**.

---

## 1. Architecture

| Service         | Rôle                                                        | Port  |
|-----------------|------------------------------------------------------------|-------|
| `frontend`      | Interface Angular (échiquier + chat)                       | 4200  |
| `backend`       | API FastAPI + agent LangGraph + embeddings locaux          | 9000  |
| `milvus`        | Base vectorielle (RAG)                                     | 19530 |
| `etcd`          | Métadonnées de Milvus                                      | —     |
| `minio`         | Stockage objet de Milvus                                   | —     |
| `mongo`         | Persistance / cache (vidéos, données d'ouverture)          | 27017 |
| `ollama-tunnel` | Tunnel SSH vers le serveur GPU (LLM)                       | —     |

Le **modèle génératif** (`qwen3-vl:30b-a3b-instruct-q8_0`) tourne sur un serveur
GPU distant (**PGX**) et n'est **pas** embarqué dans la stack : le backend le
joint via un tunnel SSH (`ollama-tunnel`). Les **embeddings** du RAG, eux, sont
calculés localement dans le conteneur backend (`Qwen/Qwen3-Embedding-0.6B`).

```
Navigateur ──► frontend (Angular :4200)
                     │  HTTP /api/...
                     ▼
              backend (FastAPI :9000)
   ┌──────────┬──────────┬───────────────┬───────────┬──────────┬──────────────┐
   ▼          ▼          ▼               ▼           ▼          ▼              ▼
Lichess   Stockfish   Milvus(:19530)   YouTube    MongoDB   (embeddings   ollama-tunnel
 (API)    (binaire)   ├─ etcd          (API)     (:27017)    locaux)      └─SSH─► PGX
                      └─ minio                                              qwen3-vl:30b
```

MongoDB (base `chess_db`) sert de **couche de persistance et de cache** pour les
données externes : les vidéos pertinentes (YouTube) et les données d'ouverture de
référence (Lichess). Le cache est **tolérant aux pannes** : si MongoDB est
indisponible, l'agent continue de répondre en appelant directement les API.

---

## 2. Prérequis

- **Docker** et **Docker Compose** (v2) sur la machine hôte.
- **Accès au serveur GPU PGX** et **tunnel SSH configuré** : une clé privée
  `id_ed25519_ollama` et un fichier `known_hosts` doivent être présents dans le
  dossier pointé par `SSH_DIR` (voir la procédure dédiée du tunnel SSH).
  Sans le tunnel, l'agent ne peut pas répondre.
- **Clés API** :
  - **Lichess** — jeton personnel *sans aucun scope* :
    `https://lichess.org/account/oauth/token`
  - **YouTube Data API v3** — clé créée sur
    `https://console.cloud.google.com` (activer « YouTube Data API v3 »).

---

## 3. Configuration

1. Copier le modèle de configuration puis renseigner les valeurs :

   ```bash
   cp .env.example .env
   ```

2. Éditer `.env` :
   - `LICHESS_API_TOKEN` et `YOUTUBE_API_KEY` : vos clés,
   - `SSH_DIR` : le chemin réel du dossier contenant la clé SSH du tunnel,
   - `OLLAMA_MODEL` : le modèle disponible sur la PGX (par défaut
     `qwen3-vl:30b-a3b-instruct-q8_0`).

Le fichier `.env` **n'est pas versionné** (secrets). Seul `.env.example` l'est.
La connexion MongoDB utilise des valeurs par défaut (`mongodb://mongo:27017`,
base `chess_db`) ; aucun secret à renseigner.

---

## 4. Démarrage

> Séquence importante : la base vectorielle est **vide** après une installation
> fraîche. Il faut lancer l'ingestion (étape 3 ci-dessous) pour que le RAG
> fonctionne. Le cache MongoDB, lui, se remplit automatiquement à l'usage.

1. **Construire et lancer toute la stack**, depuis la racine du projet :

   ```bash
   docker compose up -d --build
   ```

2. **Attendre que Milvus soit prêt** (~1 à 2 min) :

   ```bash
   docker compose ps
   ```
   Le conteneur `milvus` doit être `healthy` avant de continuer.

3. **Ingérer le corpus RAG** (une seule fois, ou pour rafraîchir les données) :

   ```bash
   curl -X POST http://localhost:9000/api/v1/milvus/ingest
   ```
   La réponse indique le nombre de passages insérés (`total_chunks`).
   Vérification : `curl http://localhost:9000/api/v1/milvus/stats`
   doit renvoyer un `count` égal au nombre de passages.

4. **Accès à l'application** :
   - En local sur le serveur : `http://localhost:4200`
   - Depuis un autre poste du réseau : `http://<IP_DU_SERVEUR>:4200`

### Accès réseau (pare-feu)

Pour une démonstration depuis un autre poste, autoriser les ports entrants
**4200** (front) et **9000** (back) sur le serveur. Exemple Windows, restreint
au sous-réseau local (PowerShell administrateur) :

```powershell
New-NetFirewallRule -DisplayName "P13 Frontend 4200" -Direction Inbound -Protocol TCP -LocalPort 4200 -Action Allow -RemoteAddress 192.168.2.0/24
New-NetFirewallRule -DisplayName "P13 Backend 9000"  -Direction Inbound -Protocol TCP -LocalPort 9000 -Action Allow -RemoteAddress 192.168.2.0/24
```

---

## 5. Vérifier / explorer l'API

Documentation interactive (Swagger) : `http://localhost:9000/docs`

| Méthode | Endpoint                          | Rôle                                   |
|---------|-----------------------------------|----------------------------------------|
| GET     | `/api/v1/healthcheck`             | L'API répond                           |
| GET     | `/api/v1/moves/{fen}`             | Coups théoriques (Lichess)             |
| GET     | `/api/v1/evaluate/{fen}`          | Évaluation (Stockfish)                 |
| GET     | `/api/v1/vector-search?query=...` | Recherche RAG                          |
| GET     | `/api/v1/videos/{opening}`        | Vidéos YouTube                         |
| POST    | `/api/v1/milvus/ingest`           | (Re)construire le corpus RAG           |
| GET     | `/api/v1/mongo/stats`             | État du cache MongoDB (nb de documents)|
| POST    | `/api/v1/agent/chat`              | L'agent complet (question + FEN)       |

---

## 6. Dépannage

| Symptôme                                   | Cause probable / correctif                                             |
|--------------------------------------------|-----------------------------------------------------------------------|
| L'agent ne répond pas                      | Tunnel SSH tombé → `docker compose restart ollama-tunnel` ; PGX joignable ? |
| Le RAG ne renvoie rien                     | Corpus non ingéré → lancer `POST /api/v1/milvus/ingest`               |
| `/milvus/init` échoue au démarrage         | Milvus pas encore `healthy` → attendre puis réessayer                  |
| Site inaccessible depuis un autre poste    | Pare-feu → ouvrir 4200 et 9000 en entrée                              |
| Page blanche / « Invalid Host header »     | Serveur de dev Angular par IP → voir option `--allowed-hosts`          |
| `/mongo/stats` en erreur                   | MongoDB non démarré → `docker compose ps` ; l'agent fonctionne malgré tout (cache tolérant aux pannes) |

Vérifier la liaison LLM de bout en bout :

```bash
docker compose exec ollama-tunnel curl --max-time 10 http://127.0.0.1:11434/api/tags
```

---

## 7. Limites connues

- **Dépendance au serveur PGX + tunnel SSH** : le POC n'est pas 100 %
  autonome ; le LLM est distant.
- **Source du RAG** : le brief mentionne « Wikichess » ; la source nommée
  s'étant révélée inadaptée (site JS sans articles d'ouvertures), le corpus est
  constitué d'articles **Wikipédia FR**, ce que le brief autorise
  (« toutes sources pertinentes sont acceptées »).
- **Hallucination de liens** : un LLM peut inventer une URL dans son texte de
  synthèse ; atténué par le *system prompt*. Une garantie plus robuste (filtre
  déterministe en sortie n'autorisant que les URLs réellement renvoyées par
  l'outil) est identifiée comme évolution.
- **Librairie d'échiquier** : `ngx-chessground` a un packaging de dépendances
  imparfait (paquets à installer manuellement : `@angular/material`,
  `@angular/cdk`, `jszip`, `fzstd`, `chessops`).
- **Serveur de développement** : le front est servi par `ng serve` (adapté à un
  POC) ; une mise en production utiliserait un build statique derrière un serveur
  web / reverse proxy.

---

## 8. Test « installation fraîche »

Pour valider la reproductibilité, repartir de zéro :

```bash
docker compose down -v      # supprime conteneurs ET volumes (Milvus, Mongo, cache…)
docker compose up -d --build
# attendre milvus healthy, puis :
curl -X POST http://localhost:9000/api/v1/milvus/ingest
```

Puis suivre ce README sans rien deviner : si la démo fonctionne, la
documentation est complète.
