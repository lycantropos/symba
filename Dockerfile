ARG IMAGE_NAME
ARG IMAGE_VERSION

FROM ${IMAGE_NAME}:${IMAGE_VERSION}

WORKDIR /opt/symba

COPY pyproject.toml .
COPY README.md .
COPY setup.py .
COPY symba symba/
COPY src/ src/
COPY tests/ tests/

RUN pip install -e .[tests]
