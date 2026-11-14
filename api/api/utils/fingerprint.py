"""
Fingerprint de Dispositivo (Anti-Pirataria)
Gera hash único baseado em características do navegador/dispositivo
"""
import hashlib
import json
import re
from typing import Dict, Optional


def compute_fingerprint(client_data: Dict) -> str:
    """
    Computa fingerprint baseado em dados do cliente

    client_data esperado:
    {
        "userAgent": str,
        "screen": {width, height, colorDepth},
        "timezone": str,
        "language": str,
        "platform": str,
        "cookieEnabled": bool,
        "hardwareConcurrency": int,
        "deviceMemory": float,
        "canvas": str (hash de renderização),
        "webgl": str (vendor/renderer)
    }
    """
    # Normaliza dados
    normalized = {
        "ua": (client_data.get("userAgent") or "").strip(),
        "sw": client_data.get("screen", {}).get("width", 0),
        "sh": client_data.get("screen", {}).get("height", 0),
        "tz": client_data.get("timezone", ""),
        "lang": client_data.get("language", ""),
        "plat": client_data.get("platform", ""),
        "ce": bool(client_data.get("cookieEnabled", True)),
        "hc": client_data.get("hardwareConcurrency", 0),
        "dm": client_data.get("deviceMemory", 0),
        "cv": client_data.get("canvas", "")[:100],  # trunca
        "gl": client_data.get("webgl", "")[:100],
    }

    # Hash determinístico
    raw = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def extract_fingerprint_from_request(request_data: Dict) -> str:
    """
    Extrai fingerprint de uma requisição

    request_data esperado:
    {
        "user_agent": str,
        "screen": str (ex: "1920x1080"),
        "tz": str,
        "lang": str,
        "platform": str,
        "canvas": str,
        "webgl": str,
        "memory": int,
        "cores": int
    }
    """
    client_data = {
        "userAgent": request_data.get("user_agent", ""),
        "screen": _parse_screen(request_data.get("screen", "")),
        "timezone": request_data.get("tz", ""),
        "language": request_data.get("lang", ""),
        "platform": request_data.get("platform", ""),
        "cookieEnabled": request_data.get("cookies", True),
        "hardwareConcurrency": request_data.get("cores", 0),
        "deviceMemory": request_data.get("memory", 0),
        "canvas": request_data.get("canvas", ""),
        "webgl": request_data.get("webgl", ""),
    }
    return compute_fingerprint(client_data)


def _parse_screen(screen_str: str) -> Dict:
    """Parse '1920x1080' em dict"""
    if not screen_str or "x" not in screen_str:
        return {"width": 0, "height": 0}
    try:
        w, h = screen_str.split("x")[:2]
        return {"width": int(w), "height": int(h)}
    except (ValueError, IndexError):
        return {"width": 0, "height": 0}


def fuzzy_fingerprint_match(fp1: str, fp2: str) -> float:
    """
    Compara similaridade entre 2 fingerprints (0.0 a 1.0).
    Útil para detectar mudança de browser no mesmo dispositivo.
    """
    if not fp1 or not fp2:
        return 0.0
    if fp1 == fp2:
        return 1.0
    # Hash SHA-256 têm 64 chars. Compara primeiros 32 chars
    # (baixa precisão mas útil para fuzzy match)
    min_len = min(len(fp1), len(fp2))
    if min_len == 0:
        return 0.0
    matches = sum(1 for a, b in zip(fp1[:min_len], fp2[:min_len]) if a == b)
    return matches / min_len
