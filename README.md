# Credio | Proyecto final Inteligencia Artificial IS-701

### Objetivo del proyecto

Integrar los conceptos de Machine Learning, FastAPI y agentes vistos en clase para construir un sistema funcional que evalúe solicitudes de crédito y tome decisiones automatizadas basadas en un modelo predictivo.

Credio combina un agente conversacional (LLM local vía Ollama) que recolecta los datos de la solicitud en español, con una API de predicción (FastAPI + scikit-learn) que calcula el nivel de riesgo crediticio real.

## Documentación

- **[Manual de usuario](docs/MANUAL_USUARIO.md)**: cómo usar el chat, qué datos pide, cómo interpretar el resultado.
- **[Documentación técnica](docs/DOCUMENTACION_TECNICA.md)**: arquitectura, estructura del proyecto, API, modelo, variables de entorno, cómo correrlo en local o con Docker.

## Inicio rápido

Con [Docker](https://www.docker.com/) instalado y corriendo:

```bash
docker compose up --build
```

Luego abrir `http://localhost:7860` para chatear con Credio. Ver [la documentación técnica](docs/DOCUMENTACION_TECNICA.md) para correrlo sin Docker.
