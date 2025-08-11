# C:\AgentUr1\tools\config_adapter.py
from __future__ import annotations
from typing import Dict, Any

def adapt_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Нормализует структуру настроек для старого/нового формата."""
    # Если rag.vector_store не задан – подставим simple
    rag = cfg.setdefault("rag", {})
    rag.setdefault("vector_store", "simple")

    # Совместимость профилей
    profile = cfg.get("profile")
    profiles = cfg.get("profiles")
    if profile and profiles and profile in profiles:
        # Сливаем профиль поверх базовых ключей
        prof_cfg = profiles[profile] or {}
        # Простейший «глубокий» мердж
        def deep_merge(dst, src):
            for k, v in src.items():
                if isinstance(v, dict) and isinstance(dst.get(k), dict):
                    deep_merge(dst[k], v)
                else:
                    dst[k] = v
        deep_merge(cfg, prof_cfg)

    # Защита от мусорного значения коллекции "make_this_parameterizable_per_api_call"
    # Если в коде где-то захардкожено – лучше переопределить env/config на "documents"
    if "qdrant" in cfg and isinstance(cfg["qdrant"], dict):
        q = cfg["qdrant"]
        if q.get("collection_name") == "make_this_parameterizable_per_api_call":
            q["collection_name"] = "documents"

    return cfg

