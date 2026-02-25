FROM quay.io/opendatahub/workbench-images:cuda-jupyter-minimal-ubi9-python-3.12-2025a_20250903

USER 0

COPY requirements.txt /tmp/requirements.txt

ENV DOCLING_ARTIFACTS_PATH=/docling_artifacts
ENV RAPIDOCR_MODEL_DIR=/docling_artifacts/RapidOcr

RUN mkdir -p "${RAPIDOCR_MODEL_DIR}" "${DOCLING_ARTIFACTS_PATH}" \
  && python -m pip install --no-cache-dir sdg-hub \
  && python -m pip install --no-cache-dir -r /tmp/requirements.txt \
  && rm -rf /root/.cache/pip /tmp/requirements.txt \
  && chown -R 1001:0 "${RAPIDOCR_MODEL_DIR}" "${DOCLING_ARTIFACTS_PATH}" \
  && chmod -R a+rwx "${RAPIDOCR_MODEL_DIR}" "${DOCLING_ARTIFACTS_PATH}"

USER 1001
