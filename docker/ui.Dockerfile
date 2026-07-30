FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /credio

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir -e ".[ui]"

EXPOSE 7860

CMD ["python", "-m", "credio.ui.main"]
