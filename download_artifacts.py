import os
import urllib.request
from pathlib import Path

# Requer: pip install huggingface_hub
from huggingface_hub import snapshot_download, hf_hub_download


def download_docling_artifacts():
    # Define o caminho de destino
    # O notebook espera que os artefatos estejam em "examples/knowledge_tuning/docling_artifacts"
    # Ajuste este caminho base se você não estiver executando da raiz do projeto
    base_path = Path("examples/knowledge_tuning/docling_artifacts")
    base_path.mkdir(parents=True, exist_ok=True)

    print(f"Iniciando download dos artefatos para: {base_path.absolute()}")

    # 1. Baixar modelos de Layout do Docling (do Hugging Face)
    # Isso resolve o erro "Missing safe tensors file"
    print("\n--> Baixando modelos de Layout do Docling (ds4sd/docling-models)...")
    try:
        snapshot_download(repo_id="ds4sd/docling-models", local_dir=base_path)
        print("Modelos de Layout baixados com sucesso.")
    except Exception as e:
        print(f"Erro ao baixar modelos do Docling: {e}")
        return

    # 2. Baixar modelos do RapidOCR
    # O notebook configura RAPIDOCR_MODEL_DIR para apontar para rapidocr/models dentro dos artefatos
    rapidocr_path = base_path / "rapidocr" / "models"
    rapidocr_path.mkdir(parents=True, exist_ok=True)

    print("\n--> Baixando modelos do RapidOCR (via Hugging Face)...")
    # Usando Hugging Face (SWHL/RapidOCR) que é mais estável que releases do GitHub
    rapidocr_files = [
        "ch_PP-OCRv4_det_infer.onnx",
        "ch_PP-OCRv4_rec_infer.onnx",
        "ch_ppocr_mobile_v2.0_cls_infer.onnx",
    ]

    for filename in rapidocr_files:
        print(f"   Baixando {filename}...")
        try:
            hf_hub_download(repo_id="SWHL/RapidOCR", filename=filename, local_dir=rapidocr_path, local_dir_use_symlinks=False)
        except Exception as e:
            print(f"   Erro ao baixar {filename}: {e}")

    print("\nProcesso concluído! Agora você pode executar o 'Step 1' no notebook.")


if __name__ == "__main__":
    download_docling_artifacts()
