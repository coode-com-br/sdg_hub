# SDG HUB Seprol

## Inference server

- model = os.getenv("INFERENCE_MODEL", "RedHatAI/gpt-oss-20b")
- api_base = os.getenv("URL", "http://granite-ai-inference-server-ocp.apps.cluster-jzfpx.jzfpx.sandbox2518.opentlc.com/v1")
- api_key = os.getenv("API_KEY", "not")

## max_pages

- max_pages
  - input_dataset = prepare_dataset_from_pdf(pdf_path, "IBM 2024 Annual Report Summary", max_pages=6)

## Path Flows

- Path: `/opt/app-root/lib64/python3.12/site-packages/sdg_hub/flows/evaluation/rag_evaluation/prompts`
