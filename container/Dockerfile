FROM quay.io/opendatahub/workbench-images:cuda-jupyter-minimal-ubi9-python-3.12-2025a_20250903

USER 0

WORKDIR /opt/app-root/src

COPY requirements.txt requirements.txt

RUN python -m pip install --no-cache-dir sdg-hub \
  && python -m pip install --no-cache-dir -r requirements.txt \
  && rm -rf /root/.cache/pip requirements.txt \
  && chown -R 1001:0 "/opt/app-root/lib/python3.12/site-packages" \
  && chmod -R g+rwX "/opt/app-root/lib/python3.12/site-packages"

USER 1001
