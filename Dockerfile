FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY melodie_kimini/ ./melodie_kimini/
COPY melodie_relay/ ./melodie_relay/

RUN pip install --no-cache-dir .[relay]

CMD ["kimini-relay", "chat"]
