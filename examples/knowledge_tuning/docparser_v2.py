#!/usr/bin/env python3
"""
PDF Document Processing and Export Tool

This script processes PDF documents using the docling library, performing OCR,
table detection, and exporting to multiple formats. Configuration is handled
through a YAML file, allowing flexible control over processing options.

Example Usage:
    # Using defaults
    python docparser_v2.py -i ./pdfs -o ./output

    # Using custom config
    python docparser_v2.py -i ./pdfs -o ./output -c config.yaml

See README.md for detailed configuration options and examples.
"""

# Standard
import importlib
from pathlib import Path
import logging
import json
import os
import shutil
import time
from typing import Dict, Optional
from urllib.error import URLError
from urllib.request import urlopen
import yaml

# Third Party
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorDevice,
    AcceleratorOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
import click

# `logger_config.py` is not colocated with examples in all environments.
# Prefer the package logger and fall back to stdlib logging for standalone runs.
try:
    from sdg_hub.core.utils.logger_config import setup_logger
except ImportError:
    def setup_logger(name: str) -> logging.Logger:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
        return logging.getLogger(name)

logger = setup_logger(__name__)

# Constants and type definitions
EXPORT_FORMATS = {
    "json": ("json", "export_to_dict"),  # Deep Search JSON format
    "text": ("txt", "export_to_text"),  # Plain text
    "markdown": ("md", "export_to_markdown"),  # Markdown with structure
    "html": ("html", "export_to_html"),  # HTML with styling
    "doctags": ("doctags", "export_to_document_tokens"),  # Document tokens
}

DEFAULT_CONFIG = {
    "pipeline": {
        "ocr": {
            "enabled": True,  # Enable/disable OCR processing
            "languages": ["es"],  # List of language codes (e.g., eng, fra, deu)
        },
        "tables": {
            "enabled": True,  # Enable/disable table detection
            "cell_matching": True,  # Enable/disable cell matching in tables
        },
        "performance": {
            "threads": 4,  # Number of processing threads
            "device": "auto",  # Device selection (auto, cpu, gpu)
        },
    },
    "export": {
        "formats": {
            "json": True,  # Deep Search JSON format
            "text": True,  # Plain text
            "markdown": True,  # Markdown with structure
            "html": True,  # HTML with styling
            "doctags": True,  # Document tokens
        }
    },
}

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


def load_config(config_path: Optional[Path] = None) -> dict:
    """Load configuration from file or return defaults."""
    if not config_path:
        return DEFAULT_CONFIG

    try:
        with config_path.open("r") as f:
            user_config = yaml.safe_load(f)
            # Merge with defaults to ensure all required fields exist
            return {**DEFAULT_CONFIG, **user_config}
    except Exception as e:
        logger.warning(f"Failed to load config file: {e}. Using defaults.")
        return DEFAULT_CONFIG


def setup_pipeline_options(config: dict) -> PdfPipelineOptions:
    """Configure pipeline options from config dictionary."""
    pipeline_config = config["pipeline"]

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = pipeline_config["ocr"]["enabled"]
    pipeline_options.do_table_structure = pipeline_config["tables"]["enabled"]
    pipeline_options.table_structure_options.do_cell_matching = pipeline_config[
        "tables"
    ]["cell_matching"]
    pipeline_options.ocr_options.lang = pipeline_config["ocr"]["languages"]
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=pipeline_config["performance"]["threads"],
        device=getattr(
            AcceleratorDevice, pipeline_config["performance"]["device"].upper()
        ),
    )
    return pipeline_options


def resolve_artifacts_dir(output_dir: Path) -> Path:
    """Resolve a writable Docling artifacts directory for OCR/model downloads."""
    configured = os.getenv("DOCLING_ARTIFACTS_PATH")
    artifacts_dir = (
        Path(configured).expanduser()
        if configured
        else output_dir / ".docling_artifacts"
    ).resolve()
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    os.environ["DOCLING_ARTIFACTS_PATH"] = str(artifacts_dir)
    return artifacts_dir


def configure_rapidocr_model_dir(output_dir: Path, artifacts_dir: Path) -> Path:
    """Force RapidOCR model cache to align with Docling artifacts directory."""
    model_root = (artifacts_dir / "RapidOcr").resolve()
    configured = os.getenv("RAPIDOCR_MODEL_DIR")
    model_root.mkdir(parents=True, exist_ok=True)
    os.environ["RAPIDOCR_MODEL_DIR"] = str(model_root)

    # Migrate models from legacy locations when present.
    legacy_dirs = [
        (output_dir / "rapidocr_models").resolve(),
        (output_dir / ".rapidocr_models").resolve(),
    ]
    if configured:
        configured_path = Path(configured).expanduser().resolve()
        if configured_path != model_root:
            legacy_dirs.insert(0, configured_path)

    for legacy_dir in legacy_dirs:
        if legacy_dir.exists() and legacy_dir != model_root:
            logger.warning(
                "Migrating RapidOCR assets from legacy path %s to %s",
                legacy_dir,
                model_root,
            )
            shutil.copytree(legacy_dir, model_root, dirs_exist_ok=True)

    # RapidOCR 3.x defaults to package-relative cache paths.
    # Patch known module globals so downloads go to a writable location.
    modules_to_patch = [
        "rapidocr.inference_engine.base",
        "rapidocr.ch_ppocr_rec.main",
        "rapidocr.inference_engine.onnxruntime",
        "rapidocr.inference_engine.openvino",
        "rapidocr.inference_engine.paddle",
        "rapidocr.inference_engine.torch",
    ]
    for module_name in modules_to_patch:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "DEFAULT_MODEL_PATH"):
                setattr(module, "DEFAULT_MODEL_PATH", model_root)
        except Exception:
            # Keep processing even if a module is absent for current backend.
            continue

    return model_root


def download_to_path(url: str, destination: Path) -> None:
    """Download a file to destination using stdlib urllib."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=120) as response, destination.open("wb") as out_file:
        out_file.write(response.read())


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


def ensure_docling_models(artifacts_dir: Path) -> None:
    """Ensure Docling core models are available in the selected artifacts directory."""
    logger.info(f"Ensuring Docling core models in {artifacts_dir}")
    try:
        downloaded_path = Path(DocumentConverter.download_models_hf()).expanduser().resolve()
    except Exception as e:
        logger.error("Failed to download Docling models: %s", str(e))
        raise RuntimeError(
            "Docling model bootstrap failed (download_models_hf). "
            "Cannot continue."
        ) from e

    if downloaded_path != artifacts_dir:
        shutil.copytree(downloaded_path, artifacts_dir, dirs_exist_ok=True)

    # Some docling builds expect model.safetensors at artifacts root.
    model_file = artifacts_dir / "model.safetensors"
    if not model_file.exists() or model_file.stat().st_size == 0:
        candidates = list(artifacts_dir.rglob("model.safetensors"))
        if not candidates and downloaded_path.exists():
            candidates = list(downloaded_path.rglob("model.safetensors"))
        if candidates:
            model_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(candidates[0], model_file)

    if not model_file.exists() or model_file.stat().st_size == 0:
        raise RuntimeError(
            f"Missing safe tensors file: {model_file}. "
            "Cannot continue with current Docling setup."
        )

    # Compatibility alias for environments/libraries that resolve without leading dot.
    compat_dir = (artifacts_dir.parent / "docling_artifacts").resolve()
    if compat_dir != artifacts_dir:
        compat_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(artifacts_dir, compat_dir, dirs_exist_ok=True)


def ensure_rapidocr_models(model_root: Path) -> None:
    """Ensure required RapidOCR assets exist locally, downloading when needed."""
    logger.info(f"Ensuring RapidOCR assets in {model_root}")
    for relative_path, source_urls in RAPIDOCR_REQUIRED_ASSETS.items():
        target = model_root / relative_path
        if target.exists() and target.stat().st_size > 0:
            continue
        last_error: Exception | None = None
        for source_url in source_urls:
            logger.info(f"Downloading RapidOCR asset: {relative_path} from {source_url}")
            try:
                download_to_path(source_url, target)
                last_error = None
                break
            except (OSError, URLError, TimeoutError) as e:
                last_error = e
                continue

        if target.exists() and target.stat().st_size > 0:
            continue

        if relative_path.endswith("fonts/FZYTK.TTF") and copy_font_from_installed_rapidocr(target):
            logger.info("Using FZYTK.TTF from installed rapidocr package resources.")
            continue

        if last_error is None:
            last_error = RuntimeError("all download sources failed")

        logger.error(
            "Failed to download RapidOCR asset %s from all sources: %s",
            relative_path,
            str(last_error),
        )
        raise RuntimeError(
            f"RapidOCR model download failed for {relative_path}. "
            "Cannot continue with OCR enabled."
        ) from last_error

    missing = [
        relative_path
        for relative_path in RAPIDOCR_REQUIRED_ASSETS
        if not (model_root / relative_path).exists()
        or (model_root / relative_path).stat().st_size == 0
    ]
    if missing:
        logger.error("Missing RapidOCR assets after download attempt: %s", missing)
        raise RuntimeError(
            "RapidOCR model assets are missing after download attempt. "
            "Cannot continue with OCR enabled."
        )


def export_document(
    conv_result, doc_filename: str, output_dir: Path, config: dict
) -> None:
    """Export document in configured formats."""
    enabled_formats = {
        k: v
        for k, v in EXPORT_FORMATS.items()
        if config["export"]["formats"].get(k, True)
    }

    for format_name, (extension, export_method) in enabled_formats.items():
        try:
            content = getattr(conv_result.document, export_method)()
            output_path = output_dir / f"{doc_filename}.{extension}"

            with output_path.open("w", encoding="utf-8") as fp:
                if isinstance(content, (dict, list)):
                    json.dump(content, fp, ensure_ascii=False, indent=2)
                else:
                    fp.write(content)

            logger.debug(f"Successfully exported {format_name} format to {output_path}")

        except Exception as e:
            logger.error(f"Failed to export {format_name} format: {str(e)}")
            raise


@click.command()
@click.option(
    "--input-dir",
    "-i",
    type=click.Path(path_type=Path),
    help="Directory containing the documents to convert",
    required=True,
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    help="Directory to save the converted documents",
    required=True,
)
@click.option(
    "--config",
    "-c",
    type=click.Path(path_type=Path),
    help="Path to YAML configuration file",
    default=None,
)
def export_document_new_docling(
    input_dir: Path,
    output_dir: Path,
    config: Optional[Path],
):
    """Convert PDF documents and export them in multiple formats."""
    config_data = load_config(config)

    file_paths = list(input_dir.glob("*.pdf"))
    if not file_paths:
        logger.warning(f"No PDF files found in {input_dir}")
        return

    logger.info(f"Found {len(file_paths)} PDF files to process")

    pipeline_options = setup_pipeline_options(config_data)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir = resolve_artifacts_dir(output_dir)
    rapidocr_model_dir = configure_rapidocr_model_dir(output_dir, artifacts_dir)
    logger.info(f"Using DOCLING_ARTIFACTS_PATH={artifacts_dir}")
    logger.info(f"Using RAPIDOCR_MODEL_DIR={rapidocr_model_dir}")
    ensure_docling_models(artifacts_dir)
    if pipeline_options.do_ocr:
        ensure_rapidocr_models(rapidocr_model_dir)
    else:
        logger.info("OCR disabled by configuration; skipping RapidOCR model download.")

    def build_converter(with_ocr: bool) -> DocumentConverter:
        pipeline_options.do_ocr = with_ocr
        # Newer Docling builds accept artifacts_path directly.
        # Keep a fallback for older versions while preserving the env var override.
        try:
            return DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                },
                artifacts_path=artifacts_dir,
            )
        except TypeError:
            return DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )

    doc_converter = build_converter(with_ocr=pipeline_options.do_ocr)

    def is_missing_rapidocr_model_error(error_text: str) -> bool:
        text = error_text.lower()
        return (
            "rapido cr" in text
            or "rapidocr" in text
            or "pp-ocrv4" in text
            or "/rapidocr/" in text
        ) and (
            "does not exists" in text
            or "is not found" in text
            or "provided model path" in text
        )

    success_count = failure_count = 0
    start_time = time.time()

    for file_path in file_paths:
        logger.info(f"Processing {file_path}")
        try:
            conv_result = doc_converter.convert(file_path)
            doc_filename = conv_result.input.file.stem

            export_document(conv_result, doc_filename, output_dir, config_data)
            success_count += 1
            logger.info(f"Successfully processed {file_path}")

        except Exception as e:
            error_text = str(e)
            if pipeline_options.do_ocr and is_missing_rapidocr_model_error(error_text):
                logger.error(
                    "RapidOCR model missing during conversion for %s: %s",
                    file_path,
                    error_text,
                )
                raise RuntimeError(
                    "RapidOCR model missing after bootstrap. "
                    "Please check network/access to model source and retry."
                ) from e

            failure_count += 1
            logger.error(f"Failed to process {file_path}: {error_text}")
            continue

    processing_time = time.time() - start_time

    logger.info(
        f"Processed {success_count + failure_count} docs in {processing_time:.2f} seconds"
        f"\n  Successful: {success_count}"
        f"\n  Failed: {failure_count}"
    )


if __name__ == "__main__":
    try:
        export_document_new_docling()
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        raise
