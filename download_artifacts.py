import shutil
import urllib.request
from pathlib import Path

# Requer: pip install huggingface_hub
from huggingface_hub import snapshot_download

RAPIDOCR_VERSION = "v3.6.0"
RAPIDOCR_MODEL_BASE_URL = (
    f"https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/{RAPIDOCR_VERSION}"
)
RAPIDOCR_REQUIRED_ASSETS = {
    "torch/PP-OCRv4/det/ch_PP-OCRv4_det_infer.pth": [
        f"{RAPIDOCR_MODEL_BASE_URL}/torch/PP-OCRv4/det/ch_PP-OCRv4_det_infer.pth"
    ],
    "torch/PP-OCRv4/cls/ch_ptocr_mobile_v2.0_cls_infer.pth": [
        f"{RAPIDOCR_MODEL_BASE_URL}/torch/PP-OCRv4/cls/ch_ptocr_mobile_v2.0_cls_infer.pth"
    ],
    "torch/PP-OCRv4/rec/ch_PP-OCRv4_rec_infer.pth": [
        f"{RAPIDOCR_MODEL_BASE_URL}/torch/PP-OCRv4/rec/ch_PP-OCRv4_rec_infer.pth"
    ],
    "paddle/PP-OCRv4/rec/ch_PP-OCRv4_rec_infer/ppocr_keys_v1.txt": [
        f"{RAPIDOCR_MODEL_BASE_URL}/paddle/PP-OCRv4/rec/ch_PP-OCRv4_rec_infer/ppocr_keys_v1.txt"
    ],
    "fonts/FZYTK.TTF": [
        f"{RAPIDOCR_MODEL_BASE_URL}/resources/fonts/FZYTK.TTF",
        f"{RAPIDOCR_MODEL_BASE_URL}/fonts/FZYTK.TTF",
    ],
}


def copy_font_from_installed_rapidocr(target: Path) -> bool:
    """Try to copy FZYTK.TTF from installed rapidocr package resources."""
    try:
        import rapidocr  # type: ignore
    except Exception:
        return False

    package_root = Path(rapidocr.__file__).resolve().parent
    candidates = [
        package_root / "resources" / "fonts" / "FZYTK.TTF",
        package_root / "fonts" / "FZYTK.TTF",
        package_root / "ch_ppocr_rec" / "fonts" / "FZYTK.TTF",
    ]
    for candidate in candidates:
        if candidate.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidate, target)
            return True

    for candidate in package_root.rglob("FZYTK.TTF"):
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(candidate, target)
        return True

    return False


def download_with_fallback(urls: list[str], destination: Path) -> None:
    """Try a list of URLs until one succeeds."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    last_error = None

    for url in urls:
        try:
            with (
                urllib.request.urlopen(url, timeout=120) as response,
                destination.open("wb") as out_file,
            ):
                out_file.write(response.read())
            return
        except Exception as e:
            last_error = e
            continue

    raise RuntimeError(f"Falha ao baixar {destination.name}: {last_error}")


def ensure_root_model_safetensors(base_path: Path) -> Path:
    """Guarantee model.safetensors at artifacts root."""
    target = base_path / "model.safetensors"
    if target.exists() and target.stat().st_size > 0:
        return target

    candidates = sorted(p for p in base_path.rglob("*.safetensors") if p.is_file())
    if not candidates:
        raise RuntimeError(
            f"Nenhum arquivo .safetensors encontrado em {base_path}. "
            "Não foi possível criar model.safetensors."
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidates[0], target)
    return target


def ensure_root_artifact(
    base_path: Path,
    target_name: str,
    *,
    search_names: list[str] | None = None,
    required: bool = True,
) -> Path | None:
    """Guarantee an artifact file exists at artifacts root."""
    target = base_path / target_name
    if target.exists() and target.stat().st_size > 0:
        return target

    names = search_names or [target_name]
    candidates: list[Path] = []
    for name in names:
        candidates.extend(p for p in base_path.rglob(name) if p.is_file())

    if not candidates:
        if required:
            raise RuntimeError(
                f"Arquivo obrigatório ausente: {target_name} em {base_path}."
            )
        return None

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(candidates[0], target)
    return target


def download_docling_artifacts(base_path: Path | None = None):
    # Define o caminho de destino
    # Padrão alinhado ao notebook enhanced_summary_knowledge_tuning.
    if base_path is None:
        base_path = Path("examples/knowledge_tuning/docling_artifacts")
    base_path = base_path.resolve()
    base_path.mkdir(parents=True, exist_ok=True)

    print(f"Iniciando download dos artefatos para: {base_path.absolute()}")

    # 1. Baixar modelos de Layout do Docling (do Hugging Face)
    # Isso resolve o erro "Missing safe tensors file"
    print("\n--> Baixando modelos de Layout do Docling (ds4sd/docling-models)...")
    try:
        snapshot_download(repo_id="ds4sd/docling-models", local_dir=base_path)
        model_path = ensure_root_model_safetensors(base_path)
        preproc_path = ensure_root_artifact(
            base_path,
            "preprocessor_config.json",
            search_names=["preprocessor_config.json", "processor_config.json"],
            required=False,
        )
        if preproc_path is None:
            raise RuntimeError(
                "Arquivo obrigatório ausente: preprocessor_config.json "
                "(nem preprocessor_config.json nem processor_config.json foram encontrados)."
            )
        config_path = ensure_root_artifact(base_path, "config.json")
        # Optional tokenizer artifacts (copied when available)
        ensure_root_artifact(
            base_path,
            "tokenizer_config.json",
            required=False,
        )
        ensure_root_artifact(
            base_path,
            "tokenizer.json",
            required=False,
        )
        ensure_root_artifact(
            base_path,
            "special_tokens_map.json",
            required=False,
        )
        print("Modelos de Layout baixados com sucesso.")
        print(f"model.safetensors preparado em: {model_path}")
        print(f"preprocessor_config.json preparado em: {preproc_path}")
        print(f"config.json preparado em: {config_path}")
    except Exception as e:
        print(f"Erro ao baixar modelos do Docling: {e}")
        return

    # 2. Baixar modelos do RapidOCR (estrutura esperada pelo parser)
    rapidocr_path = base_path / "RapidOcr"
    rapidocr_path.mkdir(parents=True, exist_ok=True)

    print("\n--> Baixando modelos do RapidOCR (ModelScope)...")

    # Configurar User-Agent para evitar erros 403/401 em downloads diretos
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-agent", "Mozilla/5.0")]
    urllib.request.install_opener(opener)

    for relative_path, urls in RAPIDOCR_REQUIRED_ASSETS.items():
        filepath = rapidocr_path / relative_path
        print(f"   Baixando {relative_path}...")
        try:
            if filepath.exists() and filepath.stat().st_size > 0:
                print(f"   Já existe: {relative_path}")
                continue
            download_with_fallback(urls, filepath)
        except Exception as e:
            # Fallback local para fonte
            if relative_path.endswith(
                "fonts/FZYTK.TTF"
            ) and copy_font_from_installed_rapidocr(filepath):
                print("   Fonte FZYTK.TTF copiada do pacote rapidocr instalado.")
                continue
            print(f"   Erro ao baixar {relative_path}: {e}")

    # Verificação final obrigatória
    missing = []
    for relative_path in RAPIDOCR_REQUIRED_ASSETS:
        target = rapidocr_path / relative_path
        if not target.exists() or target.stat().st_size == 0:
            missing.append(relative_path)

    if missing:
        print("\nERRO: arquivos RapidOCR ausentes após download:")
        for item in missing:
            print(f" - {item}")
        raise RuntimeError("Falha ao preparar artefatos RapidOCR.")
    else:
        print("Modelos RapidOCR baixados com sucesso.")

    # Compatibilidade com resoluções sem ponto no nome da pasta
    compat_path = base_path.parent / "docling_artifacts"
    if compat_path.resolve() != base_path:
        shutil.copytree(base_path, compat_path, dirs_exist_ok=True)

    # Garante RAPIDOCR_MODEL_DIR explícito para debug no notebook
    print(f"DOCLING_ARTIFACTS_PATH={base_path}")
    print(f"RAPIDOCR_MODEL_DIR={rapidocr_path}")

    print("\nProcesso concluído! Agora você pode executar o 'Step 1' no notebook.")


if __name__ == "__main__":
    download_docling_artifacts()
