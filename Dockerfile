FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY melodie_relay/ ./melodie_relay/

CMD ["kimini-relay", "chat"]