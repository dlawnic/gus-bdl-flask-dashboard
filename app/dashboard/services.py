from pathlib import Path
from ..data.pipeline import load_or_refresh_dataset
from ..data.analysis import build_analysis_outputs

def get_dashboard_data(cache_dir: Path, static_charts_dir: Path, max_age_hours: int, bdl_client_id: str | None, bdl_base_url: str):
    df = load_or_refresh_dataset(
        cache_dir=cache_dir,
        max_age_hours=max_age_hours,
        bdl_client_id=bdl_client_id,
        bdl_base_url=bdl_base_url,
    )
    summary, tables, chart_paths = build_analysis_outputs(df=df, charts_dir=static_charts_dir)
    return {"summary": summary, "tables": tables, "chart_paths": chart_paths}
