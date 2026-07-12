# syntax=docker/dockerfile:1

FROM python:3.13-slim AS build

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.13-slim

RUN useradd -u 1000 -m neohub

COPY --from=build /install /usr/local

USER neohub

ENTRYPOINT ["neohub"]
CMD ["--help"]
