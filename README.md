# FlyRank CRUD API

A small FastAPI CRUD service for tasks. It exposes a root endpoint with basic app info, a health check, and task endpoints for listing, reading, creating, updating, and deleting in-memory task records.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
fastapi dev main.py
```

The API starts at `http://127.0.0.1:8000` and Swagger UI is available at `http://127.0.0.1:8000/docs`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Returns basic API metadata, including the app name, version, and a short endpoint list. |
| GET | `/health` | Returns a simple health status payload. |
| GET | `/tasks` | Returns all tasks currently stored in memory. |
| GET | `/tasks/{task_id}` | Returns one task by ID, or `404` if it does not exist. |
| POST | `/tasks` | Creates a new task from a JSON body with `title` and optional `done`. |
| PUT | `/tasks/{task_id}` | Updates an existing task by ID. |
| DELETE | `/tasks/{task_id}` | Deletes a task by ID and returns `204 No Content`. |

## Example `curl -i`

```bash
curl -i http://127.0.0.1:8000/tasks
```

```text
HTTP/1.1 200 OK
date: Thu, 16 Jul 2026 10:04:48 GMT
server: uvicorn
content-length: 115
content-type: application/json

[{"id":1,"title":"Hello","done":false},{"id":2,"title":"Task","done":true},{"id":3,"title":"Backend","done":false}]
```

## Swagger Screenshot

![Swagger UI](swagger-ui.png)