FROM python:3.12-slim

LABEL org.opencontainers.image.title="brutalizr" \
      org.opencontainers.image.description="Renames the identifiers in your code with swear words" \
      org.opencontainers.image.source="https://github.com/simonecosci/brutalizr" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /opt/brutalizr
COPY pyproject.toml README.md ./
COPY brutalizr ./brutalizr
RUN pip install . && rm -rf /opt/brutalizr

# mount the project to brutalize here
WORKDIR /work
ENTRYPOINT ["brutalizr"]
CMD ["--help"]
