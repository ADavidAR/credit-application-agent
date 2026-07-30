FROM python:3.12-slim

WORKDIR /credio

COPY pyproject.toml ./
COPY src ./src
COPY dataset ./dataset

RUN mkdir -p model db \
    && pip install --no-cache-dir -e ".[api]"

EXPOSE 8000

CMD ["python", "-m", "credio.api.main"]
