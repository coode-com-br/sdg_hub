FROM quay.io/opendatahub/workbench-images:cuda-jupyter-minimal-ubi9-python-3.12

USER 0

ENV UV_PROJECT_ENVIRONMENT=/opt/app-root/sdg_hub_venv
ENV PATH="/opt/app-root/sdg_hub_venv/bin:${PATH}"

WORKDIR /tmp/sdg_hub_notebook
COPY container/pyproject.toml ./pyproject.toml

RUN python -m pip install --no-cache-dir --upgrade pip uv \
 && uv sync --no-dev --no-install-project \
 && uv sync --no-dev --no-install-project --extra examples \
 && rm -rf /root/.cache/pip /root/.cache/uv /tmp/sdg_hub_notebook

WORKDIR /opt/app-root/src

USER 1001
