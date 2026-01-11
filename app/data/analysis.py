from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

import matplotlib
matplotlib.use("Agg")  # ważne na Windows/Flask debug
import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.colors import Normalize

FIGSIZE = (10, 5.5)

# Kolory wykresów (jasne, czytelne, spójne z UI)
COLOR_UNEMP = "#2563eb"   # blue-600
COLOR_WAGE = "#f59e0b"    # amber-500
COLOR_GRID = "#e2e8f0"    # slate-200


def _apply_chart_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#cbd5e1",
            "axes.labelcolor": "#0f172a",
            "xtick.color": "#0f172a",
            "ytick.color": "#0f172a",
            "text.color": "#0f172a",
            "grid.color": COLOR_GRID,
            "grid.linewidth": 0.8,
            "grid.alpha": 0.8,
            "font.size": 11,
        }
    )


def _auto_fix_scales(data: pd.DataFrame) -> pd.DataFrame:
    
    d = data.copy()

    if "unemployment_rate" in d.columns and d["unemployment_rate"].notna().any():
        med = float(d["unemployment_rate"].dropna().median())
        if 0 < med <= 1.0:
            d["unemployment_rate"] = d["unemployment_rate"] * 100.0

    if "avg_wage" in d.columns and d["avg_wage"].notna().any():
        med = float(d["avg_wage"].dropna().median())
        # 95 -> 9500; 120 -> 12000 itp.
        if 1.0 < med < 500.0:
            d["avg_wage"] = d["avg_wage"] * 100.0

    return d


def build_analysis_outputs(
    df: pd.DataFrame, charts_dir: Path
) -> tuple[dict[str, Any], dict[str, pd.DataFrame], dict[str, str]]:
    charts_dir.mkdir(parents=True, exist_ok=True)

    data = df.copy()

    # typy
    data["year"] = pd.to_numeric(data.get("year"), errors="coerce").astype("Int64")
    data["unemployment_rate"] = pd.to_numeric(data.get("unemployment_rate"), errors="coerce")
    data["avg_wage"] = pd.to_numeric(data.get("avg_wage"), errors="coerce")

    # nazwy/ID (bez "nan")
    if "unitId" not in data.columns:
        data["unitId"] = ""
    if "unitName" not in data.columns:
        data["unitName"] = ""

    data["unitId"] = data["unitId"].fillna("").astype(str).replace("nan", "").str.strip()
    data["unitName"] = data["unitName"].fillna("").astype(str).replace("nan", "").str.strip()

    # skale
    data = _auto_fix_scales(data)

    # Guard: brak danych
    if data.empty or data["year"].dropna().empty:
        summary = {
            "latest_unemp_year": None,
            "latest_wage_year": None,
            "latest_both_year": None,
            "avg_unemployment_latest": None,
            "avg_wage_latest": None,
            "corr_unemp_vs_wage_latest": None,
        }
        empty_rank = pd.DataFrame(columns=["Województwo", "Stopa bezrobocia (%)", "Przeciętne wynagrodzenie (zł)"])
        tables = {"ranking": empty_rank, "top5": empty_rank, "bottom5": empty_rank}
        chart_paths = {
            "trend": f"charts/{Path(_plot_empty(charts_dir / 'trend.png', 'Brak danych')).name}",
            "bar_unemp": f"charts/{Path(_plot_empty(charts_dir / 'bar_unemp.png', 'Brak danych')).name}",
            "scatter": f"charts/{Path(_plot_empty(charts_dir / 'scatter.png', 'Brak danych')).name}",
        }
        return summary, tables, chart_paths

    # lata dostępności osobno
    unemp_years = data.dropna(subset=["unemployment_rate", "year"])["year"]
    wage_years = data.dropna(subset=["avg_wage", "year"])["year"]
    both_years = data.dropna(subset=["unemployment_rate", "avg_wage", "year"])["year"]

    latest_unemp_year = int(unemp_years.max()) if not unemp_years.empty else None
    latest_wage_year = int(wage_years.max()) if not wage_years.empty else None
    latest_both_year = int(both_years.max()) if not both_years.empty else None

    latest_unemp = data[data["year"] == latest_unemp_year].copy() if latest_unemp_year else pd.DataFrame()
    latest_wage = data[data["year"] == latest_wage_year].copy() if latest_wage_year else pd.DataFrame()
    latest_both = data[data["year"] == latest_both_year].copy() if latest_both_year else pd.DataFrame()

    both = latest_both.dropna(subset=["unemployment_rate", "avg_wage"]).copy()

    # korelacja tylko jeśli ma sens
    corr = None
    if len(both) >= 3:
        if both["avg_wage"].nunique(dropna=True) >= 2 and both["unemployment_rate"].nunique(dropna=True) >= 2:
            c = both["unemployment_rate"].corr(both["avg_wage"])
            if pd.notna(c):
                corr = float(c)

    summary = {
        "latest_unemp_year": latest_unemp_year,
        "latest_wage_year": latest_wage_year,
        "latest_both_year": latest_both_year,
        "avg_unemployment_latest": float(latest_unemp["unemployment_rate"].dropna().mean()) if not latest_unemp.empty else None,
        "avg_wage_latest": float(latest_wage["avg_wage"].dropna().mean()) if not latest_wage.empty else None,
        "corr_unemp_vs_wage_latest": corr,
    }


    rank_src = latest_unemp.dropna(subset=["unemployment_rate"])[["unitId", "unitName", "unemployment_rate"]].copy()

    if latest_wage_year is not None and not latest_wage.empty:
        wage_for_ranking = latest_wage[["unitId", "avg_wage"]].copy()
    else:
        wage_for_ranking = pd.DataFrame(columns=["unitId", "avg_wage"])

    rank_src = rank_src.merge(wage_for_ranking, on="unitId", how="left")

    # displayName: unitName jeśli jest, inaczej "ID: <unitId>"
    rank_src["displayName"] = rank_src["unitName"].where(
        rank_src["unitName"].astype(str).str.len() > 0,
        "ID: " + rank_src["unitId"].astype(str),
    )

    ranking = (
        rank_src.sort_values("unemployment_rate", ascending=False)[["displayName", "unemployment_rate", "avg_wage"]]
        .rename(
            columns={
                "displayName": "Województwo",
                "unemployment_rate": "Stopa bezrobocia (%)",
                "avg_wage": "Przeciętne wynagrodzenie (zł)",
            }
        )
        .reset_index(drop=True)
    )

    tables = {
        "ranking": ranking,
        "top5": ranking.head(5),
        "bottom5": ranking.tail(5).sort_values("Stopa bezrobocia (%)", ascending=True) if not ranking.empty else ranking,
    }

    # Charts
    chart_paths: dict[str, str] = {}

    yearly = (
        data.groupby("year", dropna=True)[["unemployment_rate", "avg_wage"]]
        .mean(numeric_only=True)
        .reset_index()
        .dropna(subset=["year"])
        .sort_values("year")
    )

    chart_paths["trend"] = _plot_trend(yearly, charts_dir / "trend.png")

    if latest_unemp.empty or latest_unemp_year is None:
        chart_paths["bar_unemp"] = _plot_empty(
            charts_dir / "bar_unemp.png",
            "Brak danych bezrobocia dla najnowszego roku",
        )
    else:
        chart_paths["bar_unemp"] = _plot_bar(
            latest_unemp.dropna(subset=["unemployment_rate"]),
            charts_dir / "bar_unemp.png",
            latest_unemp_year,
        )

    if both.empty or latest_both_year is None:
        chart_paths["scatter"] = _plot_empty(
            charts_dir / "scatter.png",
            "Brak danych wspólnych (płace + bezrobocie) dla najnowszego wspólnego roku",
        )
    else:
        chart_paths["scatter"] = _plot_scatter(
            both,
            charts_dir / "scatter.png",
            latest_both_year,
        )

    # Return relative paths from /static
    chart_paths = {k: f"charts/{Path(v).name}" for k, v in chart_paths.items()}
    return summary, tables, chart_paths


def _plot_trend(yearly: pd.DataFrame, out_path: Path) -> str:
    if yearly.empty:
        return _plot_empty(out_path, "Brak danych do trendu")

    _apply_chart_style()

    fig, ax1 = plt.subplots(figsize=FIGSIZE)
    x = yearly["year"].astype(int)

    # lewa oś: bezrobocie
    line1 = None
    if yearly["unemployment_rate"].notna().any():
        line1 = ax1.plot(
            x,
            yearly["unemployment_rate"],
            color=COLOR_UNEMP,
            linewidth=2.6,
            marker="o",
            markersize=5,
            label="Bezrobocie (%)",
        )[0]
        ax1.set_ylabel("Bezrobocie (%)")
        ax1.grid(True, axis="y")

    # prawa oś: płace
    ax2 = ax1.twinx()
    line2 = None
    if yearly["avg_wage"].notna().any():
        line2 = ax2.plot(
            x,
            yearly["avg_wage"],
            color=COLOR_WAGE,
            linewidth=2.6,
            marker="s",
            markersize=5,
            label="Płace (zł)",
        )[0]
        ax2.set_ylabel("Płace (zł)")

    ax1.set_xlabel("Rok")
    ax1.set_title("Trend: bezrobocie i płace (średnia po województwach)")

    # legenda wspólna
    handles = [h for h in [line1, line2] if h is not None]
    if handles:
        labels = [h.get_label() for h in handles]
        ax1.legend(handles, labels, loc="upper left", frameon=True, framealpha=0.95)

    # lepsza czytelność osi X
    ax1.set_xticks(list(x))
    for tick in ax1.get_xticklabels():
        tick.set_rotation(0)
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, facecolor="white")
    plt.close(fig)
    return str(out_path)


def _plot_bar(latest_unemp: pd.DataFrame, out_path: Path, year: int) -> str:
    _apply_chart_style()
    plt.figure(figsize=FIGSIZE)
    if latest_unemp.empty:
        return _plot_empty(out_path, "Brak danych do wykresu")

    d = latest_unemp.sort_values("unemployment_rate", ascending=True).copy()
    labels = d["unitName"].where(d["unitName"].astype(str).str.len() > 0, d["unitId"].astype(str))

    # kolory per słupek (im wyższe bezrobocie, tym „cieplejszy” kolor)
    vals = d["unemployment_rate"].astype(float)
    norm = Normalize(vmin=float(vals.min()), vmax=float(vals.max())) if len(vals) else Normalize(vmin=0, vmax=1)
    colors = cm.get_cmap("YlOrRd")(norm(vals))

    bars = plt.barh(labels, vals, color=colors, edgecolor="white", linewidth=0.8)
    plt.title(f"Stopa bezrobocia – województwa ({year})")
    plt.xlabel("Stopa bezrobocia (%)")
    plt.grid(True, axis="x")

    # wartości na końcu słupków
    for b in bars:
        v = b.get_width()
        plt.text(v + 0.05, b.get_y() + b.get_height() / 2, f"{v:.2f}%", va="center", fontsize=9)
    plt.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, facecolor="white")
    plt.close()
    return str(out_path)


def _plot_scatter(both: pd.DataFrame, out_path: Path, year: int) -> str:
    _apply_chart_style()
    plt.figure(figsize=FIGSIZE)
    if both.empty:
        return _plot_empty(out_path, "Brak danych do wykresu zależności")

    x = both["avg_wage"].astype(float)
    y = both["unemployment_rate"].astype(float)

    # kolor punktu = bezrobocie (czytelniej widać „gorące” regiony)
    norm = Normalize(vmin=float(y.min()), vmax=float(y.max())) if len(y) else Normalize(vmin=0, vmax=1)
    sc = plt.scatter(
        x,
        y,
        c=y,
        cmap="viridis",
        norm=norm,
        s=90,
        alpha=0.9,
        edgecolors="white",
        linewidth=0.7,
    )
    plt.title(f"Zależność: wynagrodzenie vs bezrobocie ({year})")
    plt.xlabel("Przeciętne wynagrodzenie (zł)")
    plt.ylabel("Stopa bezrobocia (%)")
    plt.grid(True)

    cbar = plt.colorbar(sc)
    cbar.set_label("Bezrobocie (%)")
    plt.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, facecolor="white")
    plt.close()
    return str(out_path)


def _plot_empty(out_path: Path, message: str) -> str:
    _apply_chart_style()
    plt.figure(figsize=FIGSIZE)
    plt.text(0.5, 0.5, message, ha="center", va="center", wrap=True, fontsize=14, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, facecolor="white")
    plt.close()
    return str(out_path)
