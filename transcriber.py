#!/usr/bin/env python3
"""
Servico automatico de transcricao de notas faladas no Obsidian.
Roda a cada 30 minutos via Windows Task Scheduler (sem janela).
"""

import os
import re
import json
import shutil
import logging
from pathlib import Path

# ── Config ───────────────────────────────────────────────────────────────────────
_cfg_path = Path(__file__).parent / "config.json"
if not _cfg_path.exists():
    raise FileNotFoundError(f"config.json nao encontrado em {_cfg_path}")
_cfg = json.loads(_cfg_path.read_text(encoding="utf-8"))

VAULT_DIR           = Path(_cfg["vault_dir"])
NOTAS_FALADAS       = VAULT_DIR / _cfg["notas_faladas_file"]
AUDIOS_TRANSCRITOS  = VAULT_DIR / _cfg["audios_transcritos_dir"]
LOG_FILE            = Path(_cfg["log_file"]) if _cfg.get("log_file") else Path(__file__).parent / "transcriber.log"
_WHISPER_MODEL      = _cfg.get("whisper_model", "large-v3")
_LANGUAGE           = _cfg.get("language", "pt")
_BEAM_SIZE          = _cfg.get("beam_size", 5)
_CPU_THREADS        = _cfg.get("cpu_threads") or os.cpu_count() or 4

# Obsidian embed: ![[arquivo.m4a]] ou ![[pasta/arquivo.m4a]]
EMBED_RE = re.compile(
    r'!\[\[([^\]]+\.(?:mp3|wav|m4a|ogg|opus|flac|aac|wma))\]\]',
    re.IGNORECASE,
)

# ── Logging ──────────────────────────────────────────────────────────────────────
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# Silencia logs HTTP do huggingface_hub
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("huggingface_hub").setLevel(logging.WARNING)

_model = None
_GPU_ERROR_KEYWORDS = ("cublas", "cudnn", "cuda", ".dll", "library", "cufft", "out of memory")


def _is_gpu_error(e: Exception) -> bool:
    return any(k in str(e).lower() for k in _GPU_ERROR_KEYWORDS)


def _prep_cuda():
    if os.name != "nt":
        return
    try:
        import nvidia
        for root in nvidia.__path__:
            for bin_dir in Path(root).glob("*/bin"):
                try:
                    os.add_dll_directory(str(bin_dir))
                except Exception:
                    pass
    except Exception:
        pass


def _load_cpu_model():
    from faster_whisper import WhisperModel
    m = WhisperModel(_WHISPER_MODEL, device="cpu", compute_type="int8",
                     cpu_threads=_CPU_THREADS)
    logging.info("Modelo carregado na CPU.")
    return m


def _get_model():
    global _model
    if _model:
        return _model
    _prep_cuda()
    from faster_whisper import WhisperModel
    try:
        _model = WhisperModel(_WHISPER_MODEL, device="cuda", compute_type="int8_float16")
        logging.info("Modelo carregado na GPU.")
    except Exception as e:
        if _is_gpu_error(e):
            logging.warning(f"GPU indisponivel ({e}), usando CPU.")
        _model = _load_cpu_model()
    return _model


def _run_transcription(audio_path: Path, model) -> str:
    segs, _ = model.transcribe(
        str(audio_path),
        language=_LANGUAGE,
        beam_size=_BEAM_SIZE,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    result = " ".join(s.text.strip() for s in segs).strip()
    return result if result else "(transcricao vazia)"


def transcribe(audio_path: Path) -> str:
    global _model
    model = _get_model()
    try:
        return _run_transcription(audio_path, model)
    except Exception as e:
        if _is_gpu_error(e):
            logging.warning(f"GPU falhou durante transcricao ({e}), recarregando na CPU.")
            _model = _load_cpu_model()
            return _run_transcription(audio_path, _model)
        raise


def find_audio(name: str) -> "Path | None":
    for p in VAULT_DIR.rglob(name):
        try:
            if AUDIOS_TRANSCRITOS.resolve() not in p.resolve().parents:
                return p
        except Exception:
            pass
    return None


def process():
    if not NOTAS_FALADAS.exists():
        logging.warning("notas faladas.md nao encontrado.")
        return

    content = NOTAS_FALADAS.read_text(encoding="utf-8")
    matches = EMBED_RE.findall(content)

    if not matches:
        logging.info("Nenhum embed de audio pendente.")
        return

    AUDIOS_TRANSCRITOS.mkdir(exist_ok=True)
    changed = False

    for audio_ref in matches:
        audio_name = Path(audio_ref).name

        # Ja foi processado?
        if (AUDIOS_TRANSCRITOS / audio_name).exists():
            continue

        audio_path = find_audio(audio_name)
        if not audio_path:
            logging.warning(f"Arquivo nao encontrado no vault: {audio_name}")
            continue

        logging.info(f"Transcrevendo: {audio_name}")
        try:
            transcript = transcribe(audio_path)

            embed = f"![[{audio_ref}]]"
            replacement = f"**{audio_name}**\n\n{transcript}"
            content = content.replace(embed, replacement, 1)

            shutil.move(str(audio_path), str(AUDIOS_TRANSCRITOS / audio_name))
            logging.info("  Movido para Audios-Transcritos/")
            changed = True

        except Exception as e:
            logging.error(f"  Erro em {audio_name}: {e}")

    if changed:
        NOTAS_FALADAS.write_text(content, encoding="utf-8")
        logging.info("notas faladas.md atualizado.")


if __name__ == "__main__":
    logging.info("=== Verificacao iniciada ===")
    try:
        process()
    except Exception as e:
        logging.error(f"Erro fatal: {e}")
    logging.info("=== Concluido ===")
