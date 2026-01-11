from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .bdl_client import BDLClient, BDLVariable
from .cache import is_cache_fresh, save_cache, load_cache

CACHE_KEY = "bdl_labour_market_v2"  # nowy klucz -> nie miesza się ze starym cache


def _years_range(start: int = 2015, end: int | None = None) -> list[int]:
    end_year = end or date.today().year
    return list(range(start, end_year + 1))


def _pick_variable_strict(
    client: BDLClient,
    phrase: str,
    must_unit_contains_any: list[str],
    must_name_contains_any: list[str],
    reject_name_contains_any: list[str],
) -> BDLVariable:
    candidates = client.search_variables(phrase, page_size=100)

    def ok(v: BDLVariable) -> bool:
        name = (v.name or "").lower()
        unit = (v.measure_unit or "").lower()

        if must_unit_contains_any:
            if not any(u.lower() in unit for u in must_unit_contains_any):
                return False

        if must_name_contains_any:
            if not any(n.lower() in name for n in must_name_contains_any):
                return False

        if reject_name_contains_any:
            if any(r.lower() in name for r in reject_name_contains_any):
                return False

        return True

    filtered = [v for v in candidates if ok(v)]
    if filtered:
        # prefer niższy level (woj/typ danych), a potem „ładniejsze” dopasowanie nazwy
        def score(v: BDLVariable) -> tuple[int, int]:
            level_score = 0 if v.level is None else max(0, 10 - int(v.level))
            name_score = 1 if phrase.lower() in (v.name or "").lower() else 0
            return (level_score, name_score)

        return sorted(filtered, key=score, reverse=True)[0]

    # fallback: stara logika (jak nic nie spełni filtrów)
    return client.pick_best_variable(phrase, prefer_unit_contains=must_unit_contains_any[0] if must_unit_contains_any else None)


def load_or_refresh_dataset(
    cache_dir: Path,
    max_age_hours: int,
    bdl_client_id: str | None,
    bdl_base_url: str,
) -> pd.DataFrame:
    cache_dir.mkdir(parents=True, exist_ok=True)

    if is_cache_fresh(cache_dir, CACHE_KEY, max_age_hours):
        cached = load_cache(cache_dir, CACHE_KEY)
        if isinstance(cached, pd.DataFrame) and not cached.empty:
            return cached

    client = BDLClient(base_url=bdl_base_url, client_id=bdl_client_id)

    # 1) Bezrobocie – chcemy % i „stopa bezrobocia”
    v_unemp = _pick_variable_strict(
        client=client,
        phrase="stopa bezrobocia rejestrowanego",
        must_unit_contains_any=["%"],
        must_name_contains_any=["bezrobocia", "stopa"],
        reject_name_contains_any=["dynamika", "indeks", "rok poprzedni", "2015=100", "100=rok"],
    )

    # 2) Płace – chcemy zł/PLN i „wynagrodzenie”
    v_wages = _pick_variable_strict(
        client=client,
        phrase="przeciętne miesięczne wynagrodzenia brutto",
        must_unit_contains_any=["zł", "pln"],
        must_name_contains_any=["wynagrod", "miesięcz"],
        reject_name_contains_any=["dynamika", "indeks", "rok poprzedni", "2015=100", "100=rok"],
    )

    years = _years_range(2015)

    rows_unemp = client.get_data_by_variable(var_id=v_unemp.id, years=years, unit_level=2)
    rows_wages = client.get_data_by_variable(var_id=v_wages.id, years=years, unit_level=2)

    df_unemp = _normalize(rows_unemp, metric="unemployment_rate")
    df_wages = _normalize(rows_wages, metric="avg_wage")

    df = (
        pd.merge(df_unemp, df_wages, on=["year", "unitId", "unitName"], how="outer")
        .sort_values(["year", "unitName"])
        .reset_index(drop=True)
    )

    save_cache(cache_dir, CACHE_KEY, df, source=f"BDL vars: unemp={v_unemp.id}, wage={v_wages.id}")
    return df


def _normalize(rows: list[dict[str, Any]], metric: str) -> pd.DataFrame:
    """
    Obsługuje dwa formaty, które realnie pojawiają się w BDL:
    A) płaski: { unitId, unitName, year, val }
    B) zagnieżdżony: { id/unitId, name/unitName, values: [{year,val}, ...] }
    """
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["year", "unitId", "unitName", metric])

    # ------- helpers: unitId/unitName mogą się nazywać różnie -------
    def series_or_empty(colnames: list[str]) -> pd.Series:
        for c in colnames:
            if c in df.columns:
                s = df[c]
                if isinstance(s, pd.Series):
                    return s
        return pd.Series([""] * len(df), index=df.index)

    unit_id_raw = series_or_empty(["unitId", "unit_id", "id"])
    unit_name_raw = series_or_empty(["unitName", "unit_name", "name"])

    unit_id = unit_id_raw.fillna("").astype(str).replace("nan", "").str.strip()
    unit_name = unit_name_raw.fillna("").astype(str).replace("nan", "").str.strip()

    # ------- CASE A: płaski -------
    if "year" in df.columns and "val" in df.columns:
        val_s = df["val"].fillna("").astype(str).str.replace(" ", "", regex=False).str.replace(",", ".", regex=False)
        out = pd.DataFrame(
            {
                "year": pd.to_numeric(df["year"], errors="coerce").astype("Int64"),
                "unitId": unit_id,
                "unitName": unit_name,
                metric: pd.to_numeric(val_s, errors="coerce"),
            }
        )
        return out.dropna(subset=["year"]).reset_index(drop=True)

    # ------- CASE B: values list -------
    if "values" in df.columns:
        base = df.copy()
        base["unitId"] = unit_id
        base["unitName"] = unit_name

        exploded = base.explode("values", ignore_index=True)
        exploded = exploded[exploded["values"].notna()].copy()
        if exploded.empty:
            return pd.DataFrame(columns=["year", "unitId", "unitName", metric])

        vals = pd.json_normalize(exploded["values"])
        if "year" not in vals.columns or "val" not in vals.columns:
            return pd.DataFrame(columns=["year", "unitId", "unitName", metric])

        val_s = vals["val"].fillna("").astype(str).str.replace(" ", "", regex=False).str.replace(",", ".", regex=False)

        out = pd.DataFrame(
            {
                "year": pd.to_numeric(vals["year"], errors="coerce").astype("Int64"),
                "unitId": exploded["unitId"].reset_index(drop=True),
                "unitName": exploded["unitName"].reset_index(drop=True),
                metric: pd.to_numeric(val_s, errors="coerce"),
            }
        )
        return out.dropna(subset=["year"]).reset_index(drop=True)

    # nieznany format
    return pd.DataFrame(columns=["year", "unitId", "unitName", metric])
