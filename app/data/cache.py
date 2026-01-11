from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import pandas as pd

@dataclass(frozen=True)
class CacheMeta:
    created_at_iso: str
    source: str

def _meta_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}.meta.json"

def _data_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}.csv.gz"

def is_cache_fresh(cache_dir: Path, key: str, max_age_hours: int) -> bool:
    mp = _meta_path(cache_dir, key)
    if not mp.exists():
        return False
    try:
        meta = json.loads(mp.read_text(encoding="utf-8"))
        created = datetime.fromisoformat(meta["created_at_iso"]).astimezone(timezone.utc)
        return datetime.now(timezone.utc) - created <= timedelta(hours=max_age_hours)
    except Exception:
        return False

def save_cache(cache_dir: Path, key: str, df: pd.DataFrame, source: str) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(_data_path(cache_dir, key), index=False, compression="gzip")
    meta = CacheMeta(created_at_iso=datetime.now(timezone.utc).isoformat(), source=source)
    _meta_path(cache_dir, key).write_text(json.dumps(meta.__dict__, ensure_ascii=False, indent=2), encoding="utf-8")

def load_cache(cache_dir: Path, key: str) -> pd.DataFrame:
    return pd.read_csv(_data_path(cache_dir, key), compression="gzip")
