from pathlib import Path
from io import BytesIO
from datetime import datetime

import pandas as pd
from flask import Blueprint, current_app, render_template, send_file
from flask_login import login_required

from .services import get_dashboard_data

bp = Blueprint("dashboard", __name__)


def _build_data():
    cache_dir = Path(current_app.config["CACHE_DIR"])
    charts_dir = Path(current_app.root_path) / "static" / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)

    return get_dashboard_data(
        cache_dir=cache_dir,
        static_charts_dir=charts_dir,
        max_age_hours=int(current_app.config["CACHE_MAX_AGE_HOURS"]),
        bdl_client_id=current_app.config.get("BDL_CLIENT_ID") or None,
        bdl_base_url=current_app.config.get("BDL_BASE_URL"),
    )


@bp.get("/dashboard")
@login_required
def dashboard():
    data = _build_data()
    return render_template(
        "dashboard.html",
        summary=data["summary"],
        tables=data["tables"],
        chart_paths=data["chart_paths"],
    )


@bp.get("/export/excel")
@login_required
def export_excel():
    data = _build_data()
    summary = data["summary"]
    tables = data["tables"]

    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        pd.DataFrame([{"Parametr": k, "Wartość": v} for k, v in summary.items()]).to_excel(
            writer, index=False, sheet_name="Podsumowanie"
        )
        tables["ranking"].to_excel(writer, index=False, sheet_name="Ranking")
        tables["top5"].to_excel(writer, index=False, sheet_name="Top5")
        tables["bottom5"].to_excel(writer, index=False, sheet_name="Bottom5")

    buf.seek(0)
    filename = f"bdl_raport_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    return send_file(
        buf,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# Uwaga: endpoint /report (alias do eksportu) został usunięty na życzenie.
# Zostawiamy tylko /export/excel oraz przycisk „Pobierz Excel”.
