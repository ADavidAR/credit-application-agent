FROM ollama/ollama:latest

ENV OLLAMA_MODEL=llama3.1

COPY docker/ollama-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 11434

ENTRYPOINT ["/entrypoint.sh"]
