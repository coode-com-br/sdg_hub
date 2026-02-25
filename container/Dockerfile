FROM quay.io/opendatahub/workbench-images:cuda-jupyter-minimal-ubi9-python-3.12-2025a_20250903

USER 0

COPY requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir sdg-hub \
  && python -m pip install --no-cache-dir -r /tmp/requirements.txt \
  && rm -rf /root/.cache/pip /tmp/requirements.txt

USER 1001
