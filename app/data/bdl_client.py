from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterable

import requests

@dataclass(frozen=True)
class BDLVariable:
    id: int
    name: str
    measure_unit: str | None = None
    level: int | None = None

class BDLClientError(RuntimeError):
    pass

class BDLClient:
    def __init__(self, base_url: str, client_id: str | None = None, timeout_s: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.client_id = (client_id or "").strip() or None
        self.timeout_s = timeout_s

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/json"}
        if self.client_id:
            h["X-ClientId"] = self.client_id
        return h

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            r = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout_s)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            raise BDLClientError(f"BDL request failed: {url} params={params} err={e}") from e

    def search_variables(self, phrase: str, page_size: int = 50) -> list[BDLVariable]:
        # BDL exposes /variables/search; depending on gateway it may accept name=... or search=...
        last_err: Exception | None = None
        for param_name in ("name", "search"):
            try:
                payload = self._get_json(
                    "/variables/search",
                    params={param_name: phrase, "page-size": page_size, "page": 0, "lang": "pl"},
                )
                results = []
                for item in payload.get("results", []):
                    results.append(
                        BDLVariable(
                            id=int(item.get("id")),
                            name=str(item.get("name") or ""),
                            measure_unit=item.get("measureUnitName"),
                            level=item.get("level"),
                        )
                    )
                return results
            except Exception as e:
                last_err = e
                continue
        raise BDLClientError(f"Could not search variables for '{phrase}'. Last error: {last_err}")

    def pick_best_variable(self, phrase: str, prefer_unit_contains: str | None = None) -> BDLVariable:
        candidates = self.search_variables(phrase)
        if not candidates:
            raise BDLClientError(f"No variables found for phrase: {phrase}")

        def score(v: BDLVariable) -> tuple[int, int, int]:
            unit_score = 1 if (prefer_unit_contains and v.measure_unit and prefer_unit_contains.lower() in v.measure_unit.lower()) else 0
            name_score = 1 if phrase.lower() in v.name.lower() else 0
            level_score = 0 if v.level is None else max(0, 10 - int(v.level))
            return (unit_score, name_score, level_score)

        return sorted(candidates, key=score, reverse=True)[0]

    def get_data_by_variable(
        self,
        var_id: int,
        years: Iterable[int],
        unit_level: int = 2,
        unit_parent_id: str | None = None,
        page_size: int = 100,
        sleep_between_pages_s: float = 0.05,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        page = 0
        years_list = list(years)

        while True:
            params: dict[str, Any] = {
                "format": "json",
                "unit-level": unit_level,
                "page-size": page_size,
                "page": page,
                "lang": "pl",
            }
            params["year"] = [int(y) for y in years_list]
            if unit_parent_id:
                params["unit-parent-id"] = unit_parent_id

            payload = self._get_json(f"/data/by-variable/{int(var_id)}", params=params)
            results = payload.get("results") or []
            if not results:
                break
            rows.extend(results)

            if not payload.get("links", {}).get("next"):
                break

            page += 1
            time.sleep(sleep_between_pages_s)

        return rows
