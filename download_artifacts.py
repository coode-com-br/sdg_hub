import os
import urllib.request
from pathlib import Path

# Requer: pip install huggingface_hub
from huggingface_hub import snapshot_download


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

    print("\n--> Baixando modelos do RapidOCR...")
    # URLs para os modelos ONNX padrão (versão v4 é comum para docling)
    rapidocr_urls = [
        "https://github.com/RapidAI/RapidOCR/releases/download/v1.1.0/ch_PP-OCRv4_det_infer.onnx",
        "https://github.com/RapidAI/RapidOCR/releases/download/v1.1.0/ch_PP-OCRv4_rec_infer.onnx",
        "https://github.com/RapidAI/RapidOCR/releases/download/v1.1.0/ch_PP-OCRv4_cls_infer.onnx",
    ]

    for url in rapidocr_urls:
        filename = url.split("/")[-1]
        filepath = rapidocr_path / filename

        if not filepath.exists():
            print(f"   Baixando {filename}...")
            try:
                urllib.request.urlretrieve(url, filepath)
            except Exception as e:
                print(f"   Erro ao baixar {filename}: {e}")
        else:
            print(f"   {filename} já existe.")

    print("\nProcesso concluído! Agora você pode executar o 'Step 1' no notebook.")


if __name__ == "__main__":
    download_docling_artifacts()
