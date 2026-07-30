import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "credio.api.routes:app",
        host=os.environ.get("API_HOST", "0.0.0.0"),
        port=int(os.environ.get("API_PORT", "8000")),
    )


if __name__ == "__main__":
    main()
