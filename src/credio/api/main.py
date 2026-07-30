import os

import uvicorn


def main() -> None:
    """
    Punto de entrada de la API. Levanta el servidor uvicorn con la app de
    "credio.api.routes", usando host y puerto configurables por variable
    de entorno ("API_HOST", "API_PORT").
    """
    uvicorn.run(
        "credio.api.routes:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),
        port=int(os.environ.get("API_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
