from __future__ import annotations

import argparse
import calendar
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import sys
import tempfile
from typing import Iterable, Optional

from dateutil.relativedelta import relativedelta

# Allow running this module directly (e.g. `python monthlyreport/TeukSaatIndicatorsEmail.py`)
# without breaking imports.
if __name__ == "__main__" and __package__ is None:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

import db
import mail
from monthlyreport.Functionutils import NewCalculTier


# Manual objectives (optional)
# Set these values once here so cron runs use them automatically.
# Example:
#   DEFAULT_CONSUMERS_OBJECTIVE = 120000
#   DEFAULT_SITES_GT3_OBJECTIVE = 45
DEFAULT_CONSUMERS_OBJECTIVE: Optional[int] = 1_100_000
DEFAULT_SITES_GT3_OBJECTIVE: Optional[int] = None


@dataclass(frozen=True)
class TeukSaatIndicators:
    report_month: date

    active_kiosks: int
    active_kiosks_last_month: Optional[int]
    active_kiosks_last_year: Optional[int]
    active_kiosks_objective: Optional[int]

    consumers: int
    consumers_last_year: Optional[int]
    consumers_objective: Optional[int]

    beneficiaries_wins: int

    bot_day_exc_wins: Optional[float]
    bot_day_inc_wins: Optional[float]
    bot_day_exc_wins_last_year: Optional[float]
    bot_day_inc_wins_last_year: Optional[float]
    bot_day_exc_wins_objective: Optional[float]

    ytd_bot_exc_wins: int
    ytd_bot_inc_wins: int
    ytd_bot_exc_wins_last_year: Optional[int]
    ytd_bot_inc_wins_last_year: Optional[int]
    ytd_objective_exc_wins: int

    st1_count: int
    st1_count_last_year: Optional[int]
    st1_pct: Optional[float]
    st1_pct_last_year: Optional[float]

    # New additions
    lfl_ytd_bot_exc_wins: int
    lfl_ytd_bot_exc_wins_last_year: Optional[int]
    lfl_ytd_objective_exc_wins: Optional[int]
    lfl_site_count: int

    sites_gt_3_operators: int
    sites_gt_3_operators_last_year: Optional[int]
    sites_gt_3_operators_objective: Optional[int]


def _safe_int(value) -> int:
    if value is None:
        return 0
    try:
        return int(value)
    except Exception:
        return 0


def _safe_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except Exception:
        return None


def _fmt_int(value: Optional[int]) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}".replace(",", " ")


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.0f}%"


def _fmt_signed_int(delta: Optional[int], suffix: str = "") -> str:
    if delta is None:
        return "—"
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta:,}".replace(",", " ") + suffix


def _fmt_signed_pct(delta: Optional[float]) -> str:
    if delta is None:
        return "—"
    sign = "+" if delta > 0 else ""
    return f"{sign}{delta * 100:.0f}%"


def _pct_change(curr: Optional[float], prev: Optional[float]) -> Optional[float]:
    if curr is None or prev is None:
        return None
    if prev == 0:
        return None
    return (curr / prev) - 1.0


def _delta(curr: Optional[int], prev: Optional[int]) -> Optional[int]:
    if curr is None or prev is None:
        return None
    return int(curr) - int(prev)


def _html_badge(text: str) -> str:
    return (
        "<span style=\"display:inline-block;padding:4px 10px;border-radius:999px;"
        "background:#EEF2FF;color:#3730A3;font-weight:600;font-size:12px;\">"
        f"{text}</span>"
    )


def _sql_in_placeholders(values: list) -> str:
    # Returns a string like "%s,%s,%s" to safely build `IN (...)` clauses.
    # Some DB drivers do not support binding a tuple directly to a single `%s`.
    if not values:
        return "%s"
    return ",".join(["%s"] * len(values))


def _html_card(title: str, subtitle_html: str, rows_html: str) -> str:
    return (
        "<div style=\"margin:18px 0;padding:16px 16px 6px;border:1px solid #E5E7EB;"
        "border-radius:14px;background:#FFFFFF;\">"
        f"<div style=\"display:flex;align-items:baseline;justify-content:space-between;gap:12px;\">"
        f"<div style=\"font-size:16px;font-weight:700;color:#111827;\">{title}</div>"
        f"<div style=\"font-size:12px;color:#6B7280;\">{subtitle_html}</div>"
        "</div>"
        "<div style=\"margin-top:10px;overflow-x:auto;\">"
        "<table cellpadding=\"0\" cellspacing=\"0\" style=\"width:100%;border-collapse:collapse;min-width:540px;\">"
        "<thead>"
        "<tr>"
        "<th style=\"text-align:left;padding:10px 10px;border-bottom:1px solid #E5E7EB;color:#6B7280;font-size:12px;\">Metric</th>"
        "<th style=\"text-align:right;padding:10px 10px;border-bottom:1px solid #E5E7EB;color:#6B7280;font-size:12px;\">Value</th>"
        "<th style=\"text-align:right;padding:10px 10px;border-bottom:1px solid #E5E7EB;color:#6B7280;font-size:12px;\">Δ vs N-1</th>"
        "<th style=\"text-align:right;padding:10px 10px;border-bottom:1px solid #E5E7EB;color:#6B7280;font-size:12px;\">Δ vs M-1</th>"
        "<th style=\"text-align:left;padding:10px 10px;border-bottom:1px solid #E5E7EB;color:#6B7280;font-size:12px;\">Notes</th>"
        "</tr>"
        "</thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
        "</div>"
        "</div>"
    )


def _row(metric: str, value: str, delta_n1: str = "—", delta_m1: str = "—", notes: str = "") -> str:
    return (
        "<tr>"
        f"<td style=\"padding:10px;border-bottom:1px solid #F3F4F6;color:#111827;\">{metric}</td>"
        f"<td style=\"padding:10px;border-bottom:1px solid #F3F4F6;text-align:right;font-variant-numeric:tabular-nums;color:#111827;font-weight:600;\">{value}</td>"
        f"<td style=\"padding:10px;border-bottom:1px solid #F3F4F6;text-align:right;font-variant-numeric:tabular-nums;\">{delta_n1}</td>"
        f"<td style=\"padding:10px;border-bottom:1px solid #F3F4F6;text-align:right;font-variant-numeric:tabular-nums;\">{delta_m1}</td>"
        f"<td style=\"padding:10px;border-bottom:1px solid #F3F4F6;color:#6B7280;\">{notes}</td>"
        "</tr>"
    )


def _colorize_delta(text: str, is_positive: Optional[bool]) -> str:
    if is_positive is None:
        return f"<span style=\"color:#6B7280\">{text}</span>"
    return (
        f"<span style=\"color:{'#047857' if is_positive else '#B91C1C'};font-weight:700\">{text}</span>"
    )


def _beneficiaries_wins_default(report_month: date) -> int:
    # Same default values as in IndicatorsTeukSaat (Excel tab).
    if report_month.year == 2022:
        return 315_000
    if report_month.year == 2023:
        return 350_000
    if report_month.year == 2024:
        return 376_000
    return 388_000


def compute_teuksaat_indicators(
    report_month: date,
    beneficiaries_wins: Optional[int] = None,
    consumers_objective: Optional[int] = None,
    sites_gt_3_operators_objective: Optional[int] = None,
) -> TeukSaatIndicators:
    con = db.pool.connect()

    date_n_1 = date(report_month.year - 1, report_month.month, 1)
    date_m_1 = report_month - relativedelta(months=+1)
    date_janv = date(report_month.year - 1, 12, 1)
    date_last_janv = date(report_month.year - 2, 12, 1)

    # --- Active kiosks (same SQL as IndicatorsTeukSaat) ---
    active_rows = con.execute(
        "SELECT COUNT(Sales.Id_Site), Month "
        "FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site "
        "WHERE (Month = %s OR Month = %s OR Month = %s) AND Platform <> 'Dead' "
        "GROUP BY Month ORDER BY Month DESC",
        (report_month, date_m_1, date_n_1),
    ).fetchall()

    def _month_key(value) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            # Accept 'YYYY-MM-01' (or full timestamp); only keep the date part.
            return date.fromisoformat(value[:10])
        raise TypeError(f"Unexpected Month type: {type(value)}")

    active_by_month = {_month_key(row[1]): _safe_int(row[0]) for row in active_rows}
    active_kiosks = active_by_month.get(report_month, 0)
    active_kiosks_last_month = active_by_month.get(date_m_1)
    active_kiosks_last_year = active_by_month.get(date_n_1)

    # Objective: count number of sites with forecasted sales this month (PrevisionsSales).
    active_obj_row = con.execute(
        """
        SELECT COUNT(DISTINCT ps.Id_Site)
        FROM PrevisionsSales ps
        INNER JOIN Sites s ON s.Id_Site = ps.Id_Site
        WHERE ps.Month = %s AND ps.PrevisionsSalesTot > 0 AND s.Platform <> 'Dead'
        """,
        (report_month,),
    ).fetchone()
    active_kiosks_objective = (
        _safe_int(active_obj_row[0]) if active_obj_row and active_obj_row[0] is not None else None
    )

    # --- Consumers ---
    consumers_row = con.execute(
        """SELECT IFNULL(SUM(Beneficiaries), 0) FROM Beneficiaries 
            INNER JOIN Sites ON Sites.Id_Site = Beneficiaries.Id_Site 
            WHERE Month = %s AND Platform <> 'Dead'""",
        (report_month,),
    ).fetchone()
    consumers = _safe_int(consumers_row[0] if consumers_row else 0)

    consumers_ly_row = con.execute(
        """SELECT SUM(Beneficiaries) FROM Beneficiaries 
            INNER JOIN Sites ON Sites.Id_Site = Beneficiaries.Id_Site 
            WHERE Month = %s AND Platform <> 'Dead'""",
        (date_n_1,),
    ).fetchone()
    consumers_last_year = _safe_int(consumers_ly_row[0]) if consumers_ly_row and consumers_ly_row[0] is not None else None

    # --- Beneficiaries WinS ---
    # Use the school table (same logic as in Activity Indicator): academy year depends on month.
    # Months 1..10 map to previous calendar year; months 11..12 map to current calendar year.
    if beneficiaries_wins is not None:
        wins_value = int(beneficiaries_wins)
    else:
        academy_year = report_month.year - 1 if report_month.month in {1, 2, 3, 4, 5, 6, 7, 8, 9, 10} else report_month.year
        wins_row = con.execute(
            """
            SELECT IFNULL(SUM(sp.number_of_children), 0)
            FROM school_programs sp
            INNER JOIN Sites s ON s.Id_Site = sp.Id_Site
            WHERE sp.academy_year = %s AND s.Platform <> 'Dead'
            """,
            (academy_year,),
        ).fetchone()
        wins_value = _safe_int(wins_row[0] if wins_row else 0)

    # --- B/day (average B/day/site) ---
    # We want the mean of per-site daily performance (not a global weighted average).
    bot_day_row = con.execute(
        """
        SELECT
            AVG((Total_Sales - WiS_Sales - Bottle_Sales) / NULLIF(Number_Open_Days, 0)) AS bot_exc_avg,
            AVG((Total_Sales - Bottle_Sales) / NULLIF(Number_Open_Days, 0)) AS bot_inc_avg
        FROM Sales
        INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site
        WHERE Platform <> 'Dead' AND Month = %s
        """,
        (report_month,),
    ).fetchone()

    bot_day_last_row = con.execute(
        """
        SELECT
            AVG((Total_Sales - WiS_Sales - Bottle_Sales) / NULLIF(Number_Open_Days, 0)) AS bot_exc_avg,
            AVG((Total_Sales - Bottle_Sales) / NULLIF(Number_Open_Days, 0)) AS bot_inc_avg
        FROM Sales
        INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site
        WHERE Platform <> 'Dead' AND Month = %s
        """,
        (date_n_1,),
    ).fetchone()

    bot_exc = _safe_float(bot_day_row[0]) if bot_day_row else None
    bot_inc = _safe_float(bot_day_row[1]) if bot_day_row else None
    bot_exc_ly = _safe_float(bot_day_last_row[0]) if bot_day_last_row else None
    bot_inc_ly = _safe_float(bot_day_last_row[1]) if bot_day_last_row else None

    # Objective: average objective B/day/site = AVG(PrevisionsSalesTot / (days_in_month - 1)) across sites.
    days_in_month = calendar.monthrange(report_month.year, report_month.month)[1]
    denom = max(days_in_month - 1, 1)
    month_obj_row = con.execute(
        """
        SELECT AVG(ps.PrevisionsSalesTot / %s)
        FROM PrevisionsSales ps
        INNER JOIN Sites s ON s.Id_Site = ps.Id_Site
        WHERE ps.Month = %s AND ps.PrevisionsSalesTot > 0 AND s.Platform <> 'Dead'
        """,
        (denom, report_month),
    ).fetchone()
    bot_day_exc_wins_objective = _safe_float(month_obj_row[0]) if month_obj_row else None

    # --- YTD bottle sold ---
    ytd_row = con.execute(
        "SELECT SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(Total_Sales-Bottle_Sales) "
        "FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site "
        "WHERE Month <= %s AND Month > %s AND Platform <> 'Dead'",
        (report_month, date_janv),
    ).fetchone()
    ytd_ly_row = con.execute(
        "SELECT SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(Total_Sales-Bottle_Sales) "
        "FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site "
        "WHERE Month <= %s AND Month > %s AND Platform <> 'Dead'",
        (date_n_1, date_last_janv),
    ).fetchone()

    ytd_exc = _safe_int(ytd_row[0] if ytd_row else 0)
    ytd_inc = _safe_int(ytd_row[1] if ytd_row else 0)
    ytd_exc_ly = _safe_int(ytd_ly_row[0]) if ytd_ly_row and ytd_ly_row[0] is not None else None
    ytd_inc_ly = _safe_int(ytd_ly_row[1]) if ytd_ly_row and ytd_ly_row[1] is not None else None

    objective_row = con.execute(
        "SELECT SUM(ps.PrevisionsSalesTot) FROM PrevisionsSales ps "
        "INNER JOIN Sites s ON s.Id_Site = ps.Id_Site "
        "WHERE ps.Month <= %s AND ps.Month > %s AND s.Platform <> 'Dead'",
        (report_month, date_janv),
    ).fetchone()
    ytd_objective = _safe_int(objective_row[0] if objective_row else 0)

    # --- ST1 ---
    st1_count = len(NewCalculTier(report_month)[1][0])
    st1_count_last_year = len(NewCalculTier(date_n_1)[1][0])

    st1_pct = (st1_count / active_kiosks) if active_kiosks else None
    st1_pct_last_year = (st1_count_last_year / active_kiosks_last_year) if active_kiosks_last_year else None

    # --- Like-for-Like (YTD, exc. WinS) ---
    analyzed_year = report_month.year - 1
    reference_month = date(analyzed_year, 1, 1)
    lfl_sites = con.execute(
        "SELECT DISTINCT Sales.Id_Site FROM Sales "
        "INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site "
        "WHERE Month = %s AND Total_Sales IS NOT NULL AND Platform <> 'Dead'",
        (reference_month,),
    ).fetchall()
    lfl_site_ids = [row[0] for row in lfl_sites]
    if not lfl_site_ids:
        lfl_site_ids = ["EBM"]

    in_clause = _sql_in_placeholders(lfl_site_ids)

    lfl_ytd_row = con.execute(
        "SELECT SUM(Total_Sales - Bottle_sales - WiS_Sales) FROM Sales "
        "INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site "
        f"WHERE Month <= %s AND Month > %s AND Sales.Id_Site IN ({in_clause}) AND Sites.Platform <> 'Dead'",
        (report_month, date_janv, *lfl_site_ids),
    ).fetchone()
    lfl_ytd = _safe_int(lfl_ytd_row[0] if lfl_ytd_row else 0)

    lfl_ytd_ly_row = con.execute(
        "SELECT SUM(Total_Sales - Bottle_sales - WiS_Sales) FROM Sales "
        "INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site "
        f"WHERE Month <= %s AND Month > %s AND Sales.Id_Site IN ({in_clause}) AND Sites.Platform <> 'Dead'",
        (date_n_1, date_last_janv, *lfl_site_ids),
    ).fetchone()
    lfl_ytd_ly = _safe_int(lfl_ytd_ly_row[0]) if lfl_ytd_ly_row and lfl_ytd_ly_row[0] is not None else None

    lfl_obj_row = con.execute(
        "SELECT SUM(ps.PrevisionsSalesTot) FROM PrevisionsSales ps "
        "INNER JOIN Sites s ON s.Id_Site = ps.Id_Site "
        f"WHERE ps.Month <= %s AND ps.Month > %s AND ps.Id_Site IN ({in_clause}) AND s.Platform <> 'Dead'",
        (report_month, date_janv, *lfl_site_ids),
    ).fetchone()
    lfl_ytd_objective = _safe_int(lfl_obj_row[0]) if lfl_obj_row and lfl_obj_row[0] is not None else None

    # --- Sites with >= 3 operators (this month) ---
    gt3_row = con.execute(
        "SELECT COUNT(DISTINCT Indicators.Id_Site) "
        "FROM Indicators JOIN Sites ON Sites.Id_Site = Indicators.Id_Site "
        "WHERE Month = %s AND Number_of_Operator >= 3 AND Sites.Platform <> 'Dead'",
        (report_month,),
    ).fetchone()
    sites_gt_3 = _safe_int(gt3_row[0] if gt3_row else 0)

    gt3_ly_row = con.execute(
        "SELECT COUNT(DISTINCT Indicators.Id_Site) "
        "FROM Indicators JOIN Sites ON Sites.Id_Site = Indicators.Id_Site "
        "WHERE Month = %s AND Number_of_Operator >= 3 AND Sites.Platform <> 'Dead'",
        (date_n_1,),
    ).fetchone()
    sites_gt_3_ly = _safe_int(gt3_ly_row[0] if gt3_ly_row else 0)

    # Objective for this KPI: reach the number of active sites.
    sites_gt_3_operators_objective = active_kiosks

    return TeukSaatIndicators(
        report_month=report_month,
        active_kiosks=active_kiosks,
        active_kiosks_last_month=active_kiosks_last_month,
        active_kiosks_last_year=active_kiosks_last_year,
        active_kiosks_objective=active_kiosks_objective,
        consumers=consumers,
        consumers_last_year=consumers_last_year,
        consumers_objective=consumers_objective,
        beneficiaries_wins=wins_value,
        bot_day_exc_wins=bot_exc,
        bot_day_inc_wins=bot_inc,
        bot_day_exc_wins_last_year=bot_exc_ly,
        bot_day_inc_wins_last_year=bot_inc_ly,
        bot_day_exc_wins_objective=bot_day_exc_wins_objective,
        ytd_bot_exc_wins=ytd_exc,
        ytd_bot_inc_wins=ytd_inc,
        ytd_bot_exc_wins_last_year=ytd_exc_ly,
        ytd_bot_inc_wins_last_year=ytd_inc_ly,
        ytd_objective_exc_wins=ytd_objective,
        st1_count=st1_count,
        st1_count_last_year=st1_count_last_year,
        st1_pct=st1_pct,
        st1_pct_last_year=st1_pct_last_year,
        lfl_ytd_bot_exc_wins=lfl_ytd,
        lfl_ytd_bot_exc_wins_last_year=lfl_ytd_ly,
        lfl_ytd_objective_exc_wins=lfl_ytd_objective,
        lfl_site_count=len([s for s in lfl_site_ids if s != "EBM"]),
        sites_gt_3_operators=sites_gt_3,
        sites_gt_3_operators_last_year=sites_gt_3_ly,
        sites_gt_3_operators_objective=sites_gt_3_operators_objective,
    )


def render_teuksaat_indicators_email(ind: TeukSaatIndicators) -> str:
    # Excel-like rendering: mimic the IndicatorsTeukSaat worksheet layout (A–E grid, colors, fonts).
    month_label_excel = ind.report_month.strftime("%B-%Y")

    active_delta_ly = _delta(ind.active_kiosks, ind.active_kiosks_last_year)
    active_delta_lm = _delta(ind.active_kiosks, ind.active_kiosks_last_month)

    consumers_growth = _pct_change(
        float(ind.consumers),
        float(ind.consumers_last_year) if ind.consumers_last_year else None,
    )

    bot_exc_growth = _pct_change(ind.bot_day_exc_wins, ind.bot_day_exc_wins_last_year)
    bot_inc_growth = _pct_change(ind.bot_day_inc_wins, ind.bot_day_inc_wins_last_year)

    ytd_exc_growth = _pct_change(
        float(ind.ytd_bot_exc_wins),
        float(ind.ytd_bot_exc_wins_last_year) if ind.ytd_bot_exc_wins_last_year else None,
    )
    ytd_inc_growth = _pct_change(
        float(ind.ytd_bot_inc_wins),
        float(ind.ytd_bot_inc_wins_last_year) if ind.ytd_bot_inc_wins_last_year else None,
    )

    st1_delta = _delta(ind.st1_count, ind.st1_count_last_year)
    st1_pct_delta = None
    if ind.st1_pct is not None and ind.st1_pct_last_year is not None:
        st1_pct_delta = ind.st1_pct - ind.st1_pct_last_year

    lfl_growth = _pct_change(
        float(ind.lfl_ytd_bot_exc_wins),
        float(ind.lfl_ytd_bot_exc_wins_last_year) if ind.lfl_ytd_bot_exc_wins_last_year else None,
    )

    gt3_delta_ly = _delta(ind.sites_gt_3_operators, ind.sites_gt_3_operators_last_year)

    def _delta_cell_int(delta: Optional[int]) -> str:
        if delta is None:
            return ""
        return _colorize_delta(_fmt_signed_int(delta, suffix=" kiosks" if False else ""), delta > 0)

    def _delta_cell_pct(delta: Optional[float]) -> str:
        if delta is None:
            return ""
        return _colorize_delta(_fmt_signed_pct(delta), delta > 0)

    def _cell(text: str, style: str, cls: str = "") -> str:
        cls_attr = f" class=\"{cls}\"" if cls else ""
        return f"<td{cls_attr} style=\"{style}\">{text}</td>"

    # Lighter palette for email readability (keeps Excel vibe without the harsh yellow).
    bg_even = "background:#F3F6FC;"
    bg_odd = "background:#EDF3FE;"
    grid = "border:1px solid #D6DEEA;"
    base = f"{grid}padding:5px 8px;font-family:Calibri,Arial,sans-serif;line-height:1.25;"
    base_center = base + "text-align:center;vertical-align:middle;"
    base_left = base + "text-align:left;vertical-align:middle;"
    base_right = base + "text-align:right;vertical-align:middle;"

    title_style = (
        base_center
        + "font-size:16px;font-weight:800;color:#0F172A;background:#EAF0FB;"
        + "padding:12px 10px;letter-spacing:0.2px;"
    )
    section_style = (
        "background:#DDEAFB;border:1px solid #B6C8E6;"
        "padding:6px 10px;font-family:Calibri,Arial,sans-serif;"
        "font-size:13px;font-weight:700;text-align:center;vertical-align:middle;color:#1F4E78;"
    )
    metric_style = base_left + "font-size:13px;font-weight:700;color:#1F4E78;"
    sub_metric_style = base_left + "font-size:11px;font-style:italic;color:#0F172A;"
    value_style = base_right + "font-size:13px;font-weight:700;color:#0F172A;font-variant-numeric:tabular-nums;white-space:nowrap;"
    value_sub_style = base_right + "font-size:11px;font-style:italic;color:#0F172A;font-variant-numeric:tabular-nums;white-space:nowrap;"
    note_style = base_left + "font-size:11px;font-style:italic;color:#334155;"
    note_obj_style = base_left + "font-size:11px;font-style:italic;color:#7C2D12;"
    colhdr_style = base_center + "font-size:12px;font-weight:700;color:#1F4E78;background:#EAF0FB;"
    vs_style = base_left + "font-size:11px;color:#0F172A;"
    vs_obj_style = base_left + "font-size:11px;color:#7C2D12;"

    def fmt_int_or_blank(v: Optional[int]) -> str:
        return "" if v is None else _fmt_int(v)

    def fmt_pct_or_blank(v: Optional[float]) -> str:
        return "" if v is None else _fmt_pct(v)

    def fmt_round_int_or_blank(v: Optional[float]) -> str:
        if v is None:
            return ""
        return _fmt_int(int(round(v)))

    def _small_block(lines: list[str]) -> str:
        clean = [l for l in lines if l]
        if not clean:
            return ""
        return '<div style="font-size:11px;line-height:1.25">' + "<br>".join(clean) + "</div>"

    def _fmt_signed_pp(delta: Optional[float]) -> str:
        if delta is None:
            return "—"
        sign = "+" if delta > 0 else ""
        return f"{sign}{delta * 100:.0f} pp"

    def _vs_int(curr: int, prev: Optional[int], label: str) -> str:
        if prev is None:
            return ""
        d = _delta(curr, prev)
        p = _pct_change(float(curr), float(prev))
        d_txt = _colorize_delta(_fmt_signed_int(d), None if d is None else d > 0)
        p_txt = _colorize_delta(_fmt_signed_pct(p), None if p is None else p > 0)
        return _small_block([f"{label}: {_fmt_int(prev)}", f"Δ: {d_txt} ({p_txt})"])

    def _vs_round_int(curr: Optional[float], prev: Optional[float], label: str) -> str:
        if curr is None or prev is None:
            return ""
        curr_i = int(round(curr))
        prev_i = int(round(prev))
        return _vs_int(curr_i, prev_i, label)

    def _vs_pct_pp(curr: Optional[float], prev: Optional[float], label: str) -> str:
        if curr is None or prev is None:
            return ""
        d = curr - prev
        d_txt = _colorize_delta(_fmt_signed_pp(d), None if d is None else d > 0)
        return _small_block([f"{label}: {_fmt_pct(prev)}", f"Δ: {d_txt}"])

    def _vs_objective_int(curr: int, objective: Optional[int]) -> str:
        if objective is None:
            return ""
        d = curr - int(objective)
        p = _pct_change(float(curr), float(objective))
        d_txt = _colorize_delta(_fmt_signed_int(d), d >= 0)
        p_txt = _colorize_delta(_fmt_signed_pct(p), None if p is None else p > 0)
        return _small_block([f"Objective: {_fmt_int(objective)}", f"Δ: {d_txt} ({p_txt})"])

    def _vs_objective_round_int(curr: Optional[float], objective: Optional[float]) -> str:
        if curr is None or objective is None:
            return ""
        return _vs_objective_int(int(round(curr)), int(round(objective)))

    def _vs_int_lines(curr: int, prev: Optional[int], label: str) -> list[str]:
        if prev is None:
            return []
        d = _delta(curr, prev)
        p = _pct_change(float(curr), float(prev))
        d_txt = _colorize_delta(_fmt_signed_int(d), None if d is None else d > 0)
        p_txt = _colorize_delta(_fmt_signed_pct(p), None if p is None else p > 0)
        return [f"{label}: {_fmt_int(prev)}", f"Δ: {d_txt} ({p_txt})"]

    # Build rows to mimic the sheet starting around row 6 (we don't keep row numbers in HTML).
    rows: list[str] = []
    zebra_alt = False

    def _zebra_bg() -> str:
        return bg_odd if zebra_alt else bg_even

    def add_row(c1: str, c2: str, c3: str, c4: str, s1: str, s2: str, s3: str, s4: str) -> None:
        nonlocal zebra_alt
        bg = _zebra_bg()
        rows.append(
            "<tr>"
            + f"<td style=\"{bg}{s1}\">{c1}</td>"
            + f"<td style=\"{bg}{s2}\">{c2}</td>"
            + f"<td style=\"{bg}{s3}\">{c3}</td>"
            + f"<td style=\"{bg}{s4}\">{c4}</td>"
            + "</tr>"
        )
        zebra_alt = not zebra_alt

    # Header row (B6..E6 equivalent) - 4 visible columns (metric/value/delta/notes)
    rows.append(
        "<tr>" + f"<td class=\"ts-title\" colspan=\"4\" style=\"{title_style}\">Teuk Saat 1001 Indicators</td>" + "</tr>"
    )

    def _period_row(label: str) -> str:
        nonlocal zebra_alt
        zebra_alt = False
        return f"<tr><td colspan=\"4\" style=\"{section_style}\">{label}</td></tr>"

    # Column headers (clear 4-column layout)
    rows.append(
        "<tr>"
        + _cell("Indicator", colhdr_style)
        + _cell("Current", colhdr_style)
        + _cell("vs last year / month", colhdr_style)
        + _cell("vs objective", colhdr_style)
        + "</tr>"
    )

    # Order requested: Monthly -> YTD -> 12 Months
    rows.append(_period_row("Monthly"))

    # Monthly: Active kiosks (single readable row)
    add_row(
        "Number of active kiosks",
        _fmt_int(ind.active_kiosks),
        _small_block(
            _vs_int_lines(ind.active_kiosks, ind.active_kiosks_last_month, "Last month")
            + ["<span style=\"color:#94A3B8\">—</span>"]
            + _vs_int_lines(ind.active_kiosks, ind.active_kiosks_last_year, "Last year")
        ),
        _vs_objective_int(ind.active_kiosks, ind.active_kiosks_objective),
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )

    # Monthly: Sites > 3 operators
    add_row(
        "Nb Sites \u2265 3 Workers",
        _fmt_int(ind.sites_gt_3_operators),
        _vs_int(ind.sites_gt_3_operators, ind.sites_gt_3_operators_last_year, "Last year"),
        _vs_objective_int(ind.sites_gt_3_operators, ind.sites_gt_3_operators_objective),
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )

    # Monthly: B/day (no empty filler rows)
    add_row(
        "B/day exc. WinS",
        fmt_round_int_or_blank(ind.bot_day_exc_wins),
        _vs_round_int(ind.bot_day_exc_wins, ind.bot_day_exc_wins_last_year, "Last year"),
        _vs_objective_round_int(ind.bot_day_exc_wins, ind.bot_day_exc_wins_objective),
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )
    add_row(
        "B/day inc. WinS",
        fmt_round_int_or_blank(ind.bot_day_inc_wins),
        _vs_round_int(ind.bot_day_inc_wins, ind.bot_day_inc_wins_last_year, "Last year"),
        "",
        sub_metric_style,
        value_sub_style,
        vs_style,
        vs_obj_style,
    )

    rows.append(_period_row("YTD"))

    add_row(
        "Total bottle sold exc. WinS",
        _fmt_int(ind.ytd_bot_exc_wins),
        _vs_int(ind.ytd_bot_exc_wins, ind.ytd_bot_exc_wins_last_year, "Last year"),
        _vs_objective_int(ind.ytd_bot_exc_wins, ind.ytd_objective_exc_wins),
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )
    add_row(
        "Total bottle sold inc. WinS",
        _fmt_int(ind.ytd_bot_inc_wins),
        _vs_int(ind.ytd_bot_inc_wins, ind.ytd_bot_inc_wins_last_year, "Last year"),
        "",
        sub_metric_style,
        value_sub_style,
        vs_style,
        vs_obj_style,
    )

    # Added: Like-for-Like (YTD)
    add_row(
        "Total Sales (Bot) LFL exc. WinS (YTD)",
        _fmt_int(ind.lfl_ytd_bot_exc_wins),
        _vs_int(ind.lfl_ytd_bot_exc_wins, ind.lfl_ytd_bot_exc_wins_last_year, "Last year"),
        _vs_objective_int(ind.lfl_ytd_bot_exc_wins, ind.lfl_ytd_objective_exc_wins),
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )

    rows.append(_period_row("12 Months"))

    # 12 Months: Consumers + Beneficiaries WinS
    add_row(
        "Consumers",
        _fmt_int(ind.consumers),
        _vs_int(ind.consumers, ind.consumers_last_year, "Last year"),
        _vs_objective_int(ind.consumers, ind.consumers_objective),
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )
    add_row(
        "Beneficiaries WinS",
        _fmt_int(ind.beneficiaries_wins),
        "",
        "",
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )

    # 12 Months: ST1
    add_row(
        "Number of ST1",
        _fmt_int(ind.st1_count),
        _vs_int(ind.st1_count, ind.st1_count_last_year, "Last year"),
        _vs_objective_int(ind.st1_count, 125),
        metric_style,
        value_style,
        vs_style,
        vs_obj_style,
    )
    # % ST1 row
    # Excel compares ratio difference; represent as signed percentage points.
    st1_pp_delta = None
    if st1_pct_delta is not None:
        st1_pp_delta = st1_pct_delta
    add_row(
        "% of ST1",
        fmt_pct_or_blank(ind.st1_pct),
        _vs_pct_pp(ind.st1_pct, ind.st1_pct_last_year, "Last year"),
        "",
        sub_metric_style,
        value_sub_style,
        vs_style,
        vs_obj_style,
    )

    # Render a 4-col grid (metric/value/delta/notes) with Excel-like styling.
    html_parts = [
        "<!doctype html>",
        "<html><head><meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        "<style>",
        "@media only screen and (max-width:600px){",
        "  .ts-title{font-size:15px !important;}",
        "  .ts-wrapper{padding:6px !important;}",
        "  .ts-table td{padding:4px 6px !important;font-size:11px !important;line-height:1.15 !important;}",
        "  .ts-table{table-layout:fixed !important;width:100% !important;}",
        "}",
        "</style>",
        "</head>",
        "<body style=\"margin:0;background:#FFFFFF;font-family:Calibri,Arial,sans-serif;\">",
        "<div class=\"ts-wrapper\" style=\"padding:12px;\">",
        "<div style=\"max-width:860px;margin:0 auto;border:1px solid #E2E8F0;border-radius:10px;overflow:hidden;\">",
        "<div style=\"overflow-x:auto;-webkit-overflow-scrolling:touch;\">",
        "<table class=\"ts-table\" cellpadding=\"0\" cellspacing=\"0\" style=\"border-collapse:collapse;table-layout:fixed;width:100%;\">",
        "<colgroup>",
        "<col style=\"width:42%\">",
        "<col style=\"width:16%\">",
        "<col style=\"width:22%\">",
        "<col style=\"width:20%\">",
        "</colgroup>",
        "".join(rows),
        "</table>",
        "</div>",
        "</div>",
        "</div>",
        "</body></html>",
    ]
    html = "".join(html_parts)

    return html


def _get_recipients_from_permissions(permission_like: str) -> list[str]:
    con = db.pool.connect()
    rows = con.execute(
        "SELECT email from users WHERE permissions like %s",
        (f"%{permission_like}%",),
    ).fetchall()
    return [r[0] for r in rows if r and r[0]]


def send_teuksaat_indicators_email(
    report_month: Optional[date] = None,
    to_emails: Optional[Iterable[str]] = None,
    dry_run: bool = False,
    beneficiaries_wins: Optional[int] = None,
    consumers_objective: Optional[int] = None,
    sites_gt_3_operators_objective: Optional[int] = None,
    output_html_path: Optional[str] = None,
) -> str:
    if report_month is None:
        today = datetime.today().date()
        report_month = date(today.year, today.month, 1) - relativedelta(months=+1)

    if consumers_objective is None:
        consumers_objective = DEFAULT_CONSUMERS_OBJECTIVE

    ind = compute_teuksaat_indicators(
        report_month,
        beneficiaries_wins=beneficiaries_wins,
        consumers_objective=consumers_objective,
        sites_gt_3_operators_objective=sites_gt_3_operators_objective,
    )
    html = render_teuksaat_indicators_email(ind)

    if output_html_path:
        path = Path(output_html_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    if dry_run:
        return html

    recipients: list[str]
    if to_emails is not None:
        recipients = list(to_emails)
    else:
        recipients = ["amandine.chaussinand@teuksaat1001.com","axel.liber@1001fontaines.com",
                      "linemanagement@teuksaat1001.com","q.pelletier@1001fontaines.com"]

    if not recipients:
        raise RuntimeError(
            "No recipients found. Add users with 'receive_teuksaat_indicators_email' permission (preferred) "
            "or pass --to explicitly."
        )

    subject = f"TS1001 Indicators - {calendar.month_name[report_month.month]} {report_month.year}"
    mail.send_email(to_emails=recipients, subject=subject, html_content=html)
    return html


def _parse_month(value: str) -> date:
    # Accept YYYY-MM or YYYY-MM-01
    try:
        if len(value) == 7:
            dt = datetime.strptime(value, "%Y-%m")
            return date(dt.year, dt.month, 1)
        dt = datetime.strptime(value, "%Y-%m-%d")
        return date(dt.year, dt.month, 1)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Send TS1001 Indicators email.")
    parser.add_argument("--month", type=_parse_month, help="Report month (YYYY-MM). Defaults to previous month.")
    parser.add_argument("--to", action="append", help="Recipient email (repeatable).")
    parser.add_argument("--dry-run", action="store_true", help="Do not send; just render HTML.")
    parser.add_argument(
        "--output-html",
        help=(
            "Write rendered HTML to this file path (no send required). "
            "Example: --output-html preview_teuksaat_indicators.html"
        ),
    )
    parser.add_argument(
        "--print-html",
        action="store_true",
        help="Print rendered HTML to stdout (no send required).",
    )
    parser.add_argument(
        "--output-html-temp",
        action="store_true",
        help="Write rendered HTML to a temp file and print the path (no send required).",
    )
    parser.add_argument(
        "--wins-beneficiaries",
        type=int,
        default=None,
        help="Override Beneficiaries WinS value (otherwise uses the Excel default rule).",
    )

    parser.add_argument(
        "--objective-consumers",
        type=int,
        default=None,
        help="Manual objective for Consumers (optional).",
    )
    parser.add_argument(
        "--objective-sites-gt3",
        type=int,
        default=None,
        help="Deprecated/ignored: objective for 'Nb Sites \u2265 3 Workers' is the number of active sites.",
    )

    args = parser.parse_args(argv)

    output_path = args.output_html
    if args.output_html_temp:
        month = args.month
        if month is None:
            today = datetime.today().date()
            month = date(today.year, today.month, 1) - relativedelta(months=+1)
        fname = f"teuksaat_indicators_email_{month.year}-{month.month:02d}.html"
        output_path = str(Path(tempfile.gettempdir()) / fname)

    preview_only = args.dry_run or args.print_html or bool(output_path)

    html = send_teuksaat_indicators_email(
        report_month=args.month,
        to_emails=args.to,
        dry_run=preview_only,
        beneficiaries_wins=args.wins_beneficiaries,
        consumers_objective=args.objective_consumers,
        sites_gt_3_operators_objective=args.objective_sites_gt3,
        output_html_path=output_path,
    )

    if args.print_html:
        print(html)
    elif output_path:
        print(f"Wrote HTML to: {output_path}")
    elif args.dry_run:
        print(f"Rendered HTML length: {len(html)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
