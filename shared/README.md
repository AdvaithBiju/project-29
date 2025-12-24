# Shared contracts

This directory holds shared artifacts like OpenAPI schemas or model notes. To regenerate the backend OpenAPI schema:

```bash
cd backend
uvicorn app.main:app --reload  # in one shell
curl http://localhost:8000/openapi.json -o ../shared/openapi.json
```

Clients (Flutter) can consume these schemas for validation or SDK generation as the project evolves.
