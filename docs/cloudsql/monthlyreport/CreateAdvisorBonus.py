"""Generate an Excel template for advisor bonus recap.

Creates an .xlsx file with:
- Sheet 1: raw data table (auto-filled from SQL)
- Sheet 2: recap by advisor/platform computed only with Excel formulas (SUMIFS)
- Sheet 3: recap by platform computed only with Excel formulas (SUMIFS)
- Sheet 4: "salaire advisor" mapping (manual input) used by recap formulas

Usage (from repo root):
    python -m monthlyreport.CreateAdvisorBonus

Optional:
    python -m monthlyreport.CreateAdvisorBonus --output monthlyreport/AdvisorBonus_2026-01.xlsx
    python -m monthlyreport.CreateAdvisorBonus --raw-rows 5000 --recap-rows 300
"""

from __future__ import annotations

import argparse
import calendar
from datetime import date, datetime
from pathlib import Path

from dateutil.relativedelta import relativedelta
import xlsxwriter
from xlsxwriter.exceptions import FileCreateError

import db
from monthlyreport.Functionutils import NewCalculTier


RAW_SHEET_NAME = "Raw data"
RECAP_SHEET_NAME = "Recap advisors"
RECAP_PLATFORM_SHEET_NAME = "Recap plateform"

SALARY_SHEET_NAME = "salaire"

RAW_TABLE_NAME = "tbl_raw"
RECAP_TABLE_NAME = "tbl_recap"
RECAP_PLATFORM_TABLE_NAME = "tbl_recap_platform"

SALARY_ADVISOR_RANGE_NAME = "rng_salaire_advisor"
SALARY_PLATFORM_RANGE_NAME = "rng_salaire_platform"

SALARY_ADVISOR_ADVISOR_COL_RANGE_NAME = "rng_salaire_advisor_advisor"
SALARY_ADVISOR_PLATFORM_COL_RANGE_NAME = "rng_salaire_advisor_platform"
SALARY_ADVISOR_SALARY_COL_RANGE_NAME = "rng_salaire_advisor_salaire"


STATIC_RAW_HEADERS: list[str] = [
    "Site",
    "Plateforme",
    "Advisor",
    "Tier",
]

RECAP_HEADERS: list[str] = [
    "Advisor",
    "Plateforme",
    "Total ventes Y",
    "Total ventes Y-1",
    "Total ventes Obj",
    "Obj increase",
    "% increase sales",
    "Diff",
    "salaire",
    "bonus",
]

RECAP_PLATFORM_HEADERS: list[str] = [
    "Plateforme",
    "Total ventes Y",
    "Total ventes Y-1",
    "Total ventes Obj",
    "Obj increase",
    "% increase sales",
    "Diff",
    "salaire",
    "bonus",
]

SALARY_HEADERS: list[str] = ["Advisor", "Plateforme", "salaire"]
SALARY_PLATFORM_HEADERS: list[str] = ["Plateforme", "salaire"]


def _build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an Excel template with a raw data sheet and a recap-by-advisor sheet "
            "using only Excel formulas (SUMIFS)."
        )
    )
    # Default month: previous month (last completed month).
    first_of_this_month = date.today().replace(day=1)
    default_month = (first_of_this_month - relativedelta(months=1)).strftime("%Y-%m")
    default_output = Path(__file__).resolve().parent / f"AdvisorBonus_{default_month}.xlsx"

    parser.add_argument(
        "--month",
        type=str,
        default=default_month,
        help="Reference month for Y/M in format YYYY-MM (default: previous month).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"Output .xlsx path (default: {default_output.as_posix()})",
    )
    parser.add_argument(
        "--raw-rows",
        type=int,
        default=5000,
        help="Number of empty data rows reserved in the raw table.",
    )
    parser.add_argument(
        "--recap-rows",
        type=int,
        default=200,
        help="Number of rows reserved for advisor/platform recap.",
    )

    return parser.parse_args()


def _parse_month(month_str: str) -> date:
    """Parse 'YYYY-MM' into a date at the 1st of the month."""
    try:
        return datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
    except Exception as exc:
        raise ValueError("--month must be in YYYY-MM format") from exc


def _month_label(month_date: date) -> str:
    abbr = calendar.month_abbr[month_date.month].lower()
    yy = str(month_date.year)[-2:]
    return f"{abbr}-{yy}"


def _raw_headers_for_month(reference_month: date) -> list[str]:
    m2 = reference_month - relativedelta(months=2)
    m1 = reference_month - relativedelta(months=1)
    m0 = reference_month
    lm2 = m2 - relativedelta(years=1)
    lm1 = m1 - relativedelta(years=1)
    lm0 = m0 - relativedelta(years=1)

    return [
        *STATIC_RAW_HEADERS,
        f"sales {_month_label(m2)}",
        f"sales {_month_label(m1)}",
        f"sales {_month_label(m0)}",
        f"sales {_month_label(lm2)}",
        f"sales {_month_label(lm1)}",
        f"sales {_month_label(lm0)}",
        f"obj {_month_label(m2)}",
        f"obj {_month_label(m1)}",
        f"obj {_month_label(m0)}",
    ]


def _in_clause(values: list[object]) -> str:
    if not values:
        raise ValueError("Empty IN clause values")
    return "(" + ",".join(["%s"] * len(values)) + ")"


def _fetch_raw_rows(reference_month: date) -> list[dict]:
    """Fetch site-level raw data from MySQL.

    Sales are computed as (Total_Sales - Bottle_Sales - WiS_Sales) which matches
    existing KPIs labeled as 'exc. WinS'.
    Objectives come from PrevisionsSales.PrevisionsSalesTot.
    """
    m2 = reference_month - relativedelta(months=2)
    m1 = reference_month - relativedelta(months=1)
    m0 = reference_month
    months_y = [m2, m1, m0]
    months_y1 = [d - relativedelta(years=1) for d in months_y]
    months_sales = months_y + months_y1
    months_obj = months_y

    # Tier for the reference month (one query batch).
    tier_map = dict(NewCalculTier(reference_month)[0])

    excluded_sites = ["X1", "X2", "A3", "A4", "A1", "C12"]
    excluded_sites_clause = _in_clause(excluded_sites)
    months_sales_clause = _in_clause(months_sales)
    months_obj_clause = _in_clause(months_obj)

    con = db.pool.connect()
    try:
        # Base site list with platform/advisor.
        query_sites = f"""
            SELECT DISTINCT
                s.Id_Site,
                COALESCE(NULLIF(s.Old_Platform,''), s.Platform) AS Plateforme,
                s.Advisor
            FROM Sites s
            LEFT JOIN Sales sa
                ON sa.Id_Site = s.Id_Site
                AND sa.Month IN {months_sales_clause}
            LEFT JOIN PrevisionsSales ps
                ON ps.Id_Site = s.Id_Site
                AND ps.Month IN {months_obj_clause}
            WHERE (sa.Id_Site IS NOT NULL OR ps.Id_Site IS NOT NULL)
              AND s.Id_Site NOT IN {excluded_sites_clause}
              AND s.Advisor IS NOT NULL AND s.Advisor <> '' AND s.Advisor <> 'Stop'
              AND COALESCE(NULLIF(s.Old_Platform,''), s.Platform) NOT IN ('Dead','Stop','STOP','')
            ORDER BY Left(s.Id_Site,1), LENGTH(s.Id_Site), s.Id_Site
        """
        site_rows = con.execute(query_sites, tuple(months_sales + months_obj + excluded_sites)).fetchall()

        sales_query = f"""
            SELECT
                Id_Site,
                Month,
                SUM(COALESCE(Total_Sales,0) - COALESCE(Bottle_Sales,0) - COALESCE(WiS_Sales,0)) AS sales_exc_wins
            FROM Sales
            WHERE Month IN {months_sales_clause}
            GROUP BY Id_Site, Month
        """
        sales_rows = con.execute(sales_query, tuple(months_sales)).fetchall()

        obj_query = f"""
            SELECT
                Id_Site,
                Month,
                SUM(COALESCE(PrevisionsSalesTot,0)) AS obj
            FROM PrevisionsSales
            WHERE Month IN {months_obj_clause}
            GROUP BY Id_Site, Month
        """
        obj_rows = con.execute(obj_query, tuple(months_obj)).fetchall()
    finally:
        try:
            con.close()
        except Exception:
            pass

    sales_map: dict[tuple[str, date], float] = {}
    for site_id, month, value in sales_rows:
        # MySQL returns Month as datetime; normalize to date for consistent dict keys.
        if isinstance(month, datetime):
            month = month.date()
        sales_map[(site_id, month)] = value

    obj_map: dict[tuple[str, date], float] = {}
    for site_id, month, value in obj_rows:
        if isinstance(month, datetime):
            month = month.date()
        obj_map[(site_id, month)] = value

    result: list[dict] = []
    for site_id, plateforme, advisor in site_rows:
        row = {
            "Site": site_id,
            "Plateforme": plateforme,
            "Advisor": advisor or "",
            "Tier": tier_map.get(site_id, ""),
            months_y[0]: sales_map.get((site_id, months_y[0])),
            months_y[1]: sales_map.get((site_id, months_y[1])),
            months_y[2]: sales_map.get((site_id, months_y[2])),
            months_y1[0]: sales_map.get((site_id, months_y1[0])),
            months_y1[1]: sales_map.get((site_id, months_y1[1])),
            months_y1[2]: sales_map.get((site_id, months_y1[2])),
            ("obj", months_y[0]): obj_map.get((site_id, months_y[0])),
            ("obj", months_y[1]): obj_map.get((site_id, months_y[1])),
            ("obj", months_y[2]): obj_map.get((site_id, months_y[2])),
        }
        result.append(row)

    return result


def create_template_excel(
    output_path: Path,
    reference_month: date,
    raw_rows: int = 5000,
    recap_rows: int = 200,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    workbook = xlsxwriter.Workbook(output_path.as_posix())

    fmt_header = workbook.add_format({"bold": True, "bg_color": "#DCE6F1", "border": 1})
    fmt_text = workbook.add_format({"border": 1})
    fmt_int = workbook.add_format({"num_format": "#,##0", "border": 1})
    fmt_percent = workbook.add_format({"num_format": "0.00%", "border": 1})
    fmt_percent_signed = workbook.add_format({"num_format": "+0.00%;-0.00%;0.00%", "border": 1})
    fmt_usd = workbook.add_format({"num_format": "$#,##0;-$#,##0;$0", "border": 1})

    fmt_diff_pos = workbook.add_format({"font_color": "#006100", "num_format": "+0.00%;-0.00%;0.00%", "border": 1})
    fmt_diff_neg = workbook.add_format({"font_color": "#9C0006", "num_format": "+0.00%;-0.00%;0.00%", "border": 1})

    ws_raw = workbook.add_worksheet(RAW_SHEET_NAME)
    ws_salary = workbook.add_worksheet(SALARY_SHEET_NAME)
    ws_recap = workbook.add_worksheet(RECAP_SHEET_NAME)
    ws_recap_platform = workbook.add_worksheet(RECAP_PLATFORM_SHEET_NAME)

    raw_headers = _raw_headers_for_month(reference_month)

    # Fetch data first so we can size/write tables.
    raw_data = _fetch_raw_rows(reference_month)
    raw_data_count = len(raw_data)

    # Build recap keys early so we can also populate the salary mapping sheet.
    pairs: list[tuple[str, str]] = []
    seen_pairs: set[tuple[str, str]] = set()
    advisors: list[str] = []
    seen_advisors: set[str] = set()
    platforms: list[str] = []
    seen_platforms: set[str] = set()
    for r in raw_data:
        adv = (r.get("Advisor") or "").strip()
        plat = (r.get("Plateforme") or "").strip()
        if not adv or not plat:
            continue

        if plat.lower() not in seen_platforms:
            seen_platforms.add(plat.lower())
            platforms.append(plat)

        if adv.lower() not in seen_advisors:
            seen_advisors.add(adv.lower())
            advisors.append(adv)

        key = (adv, plat)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        pairs.append(key)

    # Sort recap by Plateforme then Advisor
    pairs.sort(key=lambda x: (x[1].lower(), x[0].lower()))
    advisors.sort(key=str.lower)
    platforms.sort(key=str.lower)

    # --- Salaire sheet (manual input) - NOT an Excel Table on purpose.
    # Keeping this as a normal range avoids Excel's "calculated column" auto-fill behavior.
    ws_salary.freeze_panes(1, 0)
    ws_salary.set_column(0, 0, 22)  # Advisor
    ws_salary.set_column(1, 1, 14)  # Plateforme
    ws_salary.set_column(2, 2, 16)  # salaire

    # Separate platform salary block on the right.
    ws_salary.set_column(4, 4, 14)  # Plateforme
    ws_salary.set_column(5, 5, 16)  # salaire

    ws_salary.write_string(0, 0, SALARY_HEADERS[0], fmt_header)
    ws_salary.write_string(0, 1, SALARY_HEADERS[1], fmt_header)
    ws_salary.write_string(0, 2, SALARY_HEADERS[2], fmt_header)
    ws_salary.write_string(0, 4, SALARY_PLATFORM_HEADERS[0], fmt_header)
    ws_salary.write_string(0, 5, SALARY_PLATFORM_HEADERS[1], fmt_header)

    # Salary input for advisors is keyed by (Advisor, Plateforme), same granularity as recap.
    salary_advisor_reserved_rows = max(200, len(pairs) + 50)
    salary_platform_reserved_rows = max(300, len(platforms) + 30)

    # Named ranges used by VLOOKUP in recap sheets.
    workbook.define_name(
        SALARY_ADVISOR_RANGE_NAME,
        f"='{SALARY_SHEET_NAME}'!$A$2:$C${salary_advisor_reserved_rows + 1}",
    )
    workbook.define_name(
        SALARY_ADVISOR_ADVISOR_COL_RANGE_NAME,
        f"='{SALARY_SHEET_NAME}'!$A$2:$A${salary_advisor_reserved_rows + 1}",
    )
    workbook.define_name(
        SALARY_ADVISOR_PLATFORM_COL_RANGE_NAME,
        f"='{SALARY_SHEET_NAME}'!$B$2:$B${salary_advisor_reserved_rows + 1}",
    )
    workbook.define_name(
        SALARY_ADVISOR_SALARY_COL_RANGE_NAME,
        f"='{SALARY_SHEET_NAME}'!$C$2:$C${salary_advisor_reserved_rows + 1}",
    )
    workbook.define_name(
        SALARY_PLATFORM_RANGE_NAME,
        f"='{SALARY_SHEET_NAME}'!$E$2:$F${salary_platform_reserved_rows + 1}",
    )

    for idx, (adv, plat) in enumerate(pairs):
        excel_row = 1 + idx
        if excel_row > salary_advisor_reserved_rows:
            break
        ws_salary.write_string(excel_row, 0, adv, fmt_text)
        ws_salary.write_string(excel_row, 1, plat, fmt_text)

    for idx, plat in enumerate(platforms):
        excel_row = 1 + idx
        if excel_row > salary_platform_reserved_rows:
            break
        ws_salary.write_string(excel_row, 4, plat, fmt_text)

    # Pre-format the salary input column for a reasonable range.
    ws_salary.set_column(2, 2, 16, fmt_usd)
    ws_salary.set_column(5, 5, 16, fmt_usd)

    # --- Raw sheet
    ws_raw.freeze_panes(1, 0)
    ws_raw.set_column(0, 0, 18)  # Site
    ws_raw.set_column(1, 1, 14)  # Plateforme
    ws_raw.set_column(2, 2, 20)  # Advisor
    ws_raw.set_column(3, 3, 10)  # Tier
    ws_raw.set_column(4, len(raw_headers) - 1, 18)  # numeric columns

    raw_columns = []
    for idx, header in enumerate(raw_headers):
        col = {"header": header}
        if idx <= 3:
            col["format"] = fmt_text
        else:
            col["format"] = fmt_int
        raw_columns.append(col)

    # XlsxWriter tables require at least one data row in the range.
    raw_data_rows = max(1, int(raw_rows), raw_data_count)
    ws_raw.add_table(
        0,
        0,
        raw_data_rows,
        len(raw_headers) - 1,
        {
            "name": RAW_TABLE_NAME,
            "style": "Table Style Light 9",
            "columns": raw_columns,
            "header_row": True,
        },
    )

    # Fill raw data rows (starting at row 1 because row 0 is header).
    # Keep within the reserved table size.
    m2 = reference_month - relativedelta(months=2)
    m1 = reference_month - relativedelta(months=1)
    m0 = reference_month
    lm2 = m2 - relativedelta(years=1)
    lm1 = m1 - relativedelta(years=1)
    lm0 = m0 - relativedelta(years=1)
    month_keys = [m2, m1, m0, lm2, lm1, lm0]
    obj_keys = [("obj", m2), ("obj", m1), ("obj", m0)]

    for idx, row in enumerate(raw_data):
        excel_row = 1 + idx
        if excel_row > raw_data_rows:
            break
        ws_raw.write_string(excel_row, 0, str(row["Site"]), fmt_text)
        ws_raw.write_string(excel_row, 1, str(row["Plateforme"]), fmt_text)
        ws_raw.write_string(excel_row, 2, str(row["Advisor"]), fmt_text)
        ws_raw.write_string(excel_row, 3, str(row["Tier"]), fmt_text)

        for offset, key in enumerate(month_keys):
            value = row.get(key)
            if value is None:
                continue
            ws_raw.write_number(excel_row, 4 + offset, float(value), fmt_int)

        for offset, key in enumerate(obj_keys):
            value = row.get(key)
            if value is None:
                continue
            ws_raw.write_number(excel_row, 10 + offset, float(value), fmt_int)

    # --- Recap sheet
    ws_recap.freeze_panes(1, 0)
    ws_recap.set_column(0, 0, 22)  # Advisor
    ws_recap.set_column(1, 1, 14)  # Plateforme
    ws_recap.set_column(2, 4, 18)  # totals
    ws_recap.set_column(5, 7, 18)  # % columns
    ws_recap.set_column(8, 9, 16)  # salaire/bonus

    # Formulas using structured references.
    # They remain 100% Excel-side and update when raw table values change.
    sales_m2 = raw_headers[4]
    sales_m1 = raw_headers[5]
    sales_m0 = raw_headers[6]
    sales_lm2 = raw_headers[7]
    sales_lm1 = raw_headers[8]
    sales_lm0 = raw_headers[9]
    obj_m2 = raw_headers[10]
    obj_m1 = raw_headers[11]
    obj_m0 = raw_headers[12]

    sumifs_y = (
        f"SUMIFS({RAW_TABLE_NAME}[{sales_m2}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_m1}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_m0}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
    )
    sumifs_y1 = (
        f"SUMIFS({RAW_TABLE_NAME}[{sales_lm2}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_lm1}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_lm0}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
    )
    sumifs_obj = (
        f"SUMIFS({RAW_TABLE_NAME}[{obj_m2}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{obj_m1}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{obj_m0}],{RAW_TABLE_NAME}[Advisor],[@Advisor],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
    )

    # Guard against blank Advisor, and division by 0.
    f_total_y = f'=IF([@Advisor]="","",{sumifs_y})'
    f_total_y1 = f'=IF([@Advisor]="","",{sumifs_y1})'
    f_total_obj = f'=IF([@Advisor]="","",{sumifs_obj})'
    f_obj_increase = '=IF([@Advisor]="","",IFERROR([@[Total ventes Obj]]/[@[Total ventes Y-1]]-1,""))'
    f_sales_increase = '=IF([@Advisor]="","",IFERROR([@[Total ventes Y]]/[@[Total ventes Y-1]]-1,""))'
    f_diff = '=IF([@Advisor]="","",IFERROR([@[% increase sales]]-[@[Obj increase]],""))'
    f_salary_lookup = (
        f'=IF([@Advisor]="","",'
        f'IF(COUNTIFS({SALARY_ADVISOR_ADVISOR_COL_RANGE_NAME},[@Advisor],{SALARY_ADVISOR_PLATFORM_COL_RANGE_NAME},[@Plateforme])=0,"",'
        f'SUMIFS({SALARY_ADVISOR_SALARY_COL_RANGE_NAME},{SALARY_ADVISOR_ADVISOR_COL_RANGE_NAME},[@Advisor],{SALARY_ADVISOR_PLATFORM_COL_RANGE_NAME},[@Plateforme])'
        f'))'
    )
    f_bonus = '=IF([@Advisor]="","",IF([@[salaire]]="",0,IF([@[Diff]]>0,MIN([@[salaire]],[@[salaire]]*(0.5+[@[Diff]]*10)),0)))'

    recap_data_rows = max(1, int(recap_rows), len(pairs))
    ws_recap.add_table(
        0,
        0,
        recap_data_rows,
        len(RECAP_HEADERS) - 1,
        {
            "name": RECAP_TABLE_NAME,
            "style": "Table Style Light 9",
            "columns": [
                {"header": RECAP_HEADERS[0], "format": fmt_text},
                {"header": RECAP_HEADERS[1], "format": fmt_text},
                {"header": RECAP_HEADERS[2], "formula": f_total_y, "format": fmt_int},
                {"header": RECAP_HEADERS[3], "formula": f_total_y1, "format": fmt_int},
                {"header": RECAP_HEADERS[4], "formula": f_total_obj, "format": fmt_int},
                {"header": RECAP_HEADERS[5], "formula": f_obj_increase, "format": fmt_percent},
                {"header": RECAP_HEADERS[6], "formula": f_sales_increase, "format": fmt_percent},
                {"header": RECAP_HEADERS[7], "formula": f_diff, "format": fmt_percent_signed},
                {"header": RECAP_HEADERS[8], "formula": f_salary_lookup, "format": fmt_usd},
                {"header": RECAP_HEADERS[9], "formula": f_bonus, "format": fmt_usd},
            ],
            "header_row": True,
        },
    )

    # Conditional formatting for Diff: green with leading + if positive, red with - if negative.
    ws_recap.conditional_format(
        1,
        7,
        recap_data_rows,
        7,
        {"type": "cell", "criteria": ">", "value": 0, "format": fmt_diff_pos},
    )
    ws_recap.conditional_format(
        1,
        7,
        recap_data_rows,
        7,
        {"type": "cell", "criteria": "<", "value": 0, "format": fmt_diff_neg},
    )

    # Fill the first 2 columns (Advisor/Plateforme) for the recap.
    for idx, (adv, plat) in enumerate(pairs):
        excel_row = 1 + idx
        if excel_row > recap_data_rows:
            break
        ws_recap.write_string(excel_row, 0, adv, fmt_text)
        ws_recap.write_string(excel_row, 1, plat, fmt_text)


    # --- Recap plateforme sheet (aggregated by Plateforme only)
    ws_recap_platform.freeze_panes(1, 0)
    ws_recap_platform.set_column(0, 0, 14)  # Plateforme
    ws_recap_platform.set_column(1, 3, 18)  # totals
    ws_recap_platform.set_column(4, 6, 18)  # % columns
    ws_recap_platform.set_column(7, 8, 16)  # salaire/bonus

    sumifs_y_plat = (
        f"SUMIFS({RAW_TABLE_NAME}[{sales_m2}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_m1}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_m0}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
    )
    sumifs_y1_plat = (
        f"SUMIFS({RAW_TABLE_NAME}[{sales_lm2}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_lm1}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{sales_lm0}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
    )
    sumifs_obj_plat = (
        f"SUMIFS({RAW_TABLE_NAME}[{obj_m2}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{obj_m1}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
        f"+SUMIFS({RAW_TABLE_NAME}[{obj_m0}],{RAW_TABLE_NAME}[Plateforme],[@Plateforme])"
    )

    f_total_y_plat = f'=IF([@Plateforme]="","",{sumifs_y_plat})'
    f_total_y1_plat = f'=IF([@Plateforme]="","",{sumifs_y1_plat})'
    f_total_obj_plat = f'=IF([@Plateforme]="","",{sumifs_obj_plat})'
    f_obj_increase_plat = '=IF([@Plateforme]="","",IFERROR([@[Total ventes Obj]]/[@[Total ventes Y-1]]-1,""))'
    f_sales_increase_plat = '=IF([@Plateforme]="","",IFERROR([@[Total ventes Y]]/[@[Total ventes Y-1]]-1,""))'
    f_diff_plat = '=IF([@Plateforme]="","",IFERROR([@[% increase sales]]-[@[Obj increase]],""))'
    # Platform salary comes from the manual "salaire" sheet.
    f_salary_plat = f'=IF([@Plateforme]="","",IFERROR(VLOOKUP([@Plateforme],{SALARY_PLATFORM_RANGE_NAME},2,FALSE),""))'
    # Bonus formula must follow the exact same logic as the advisor recap.
    f_bonus_plat = '=IF([@Plateforme]="","",IF([@[salaire]]="",0,IF([@[Diff]]>0,MIN([@[salaire]],[@[salaire]]*(0.5+[@[Diff]]*10)),0)))'

    recap_platform_data_rows = max(1, int(recap_rows), len(platforms))
    ws_recap_platform.add_table(
        0,
        0,
        recap_platform_data_rows,
        len(RECAP_PLATFORM_HEADERS) - 1,
        {
            "name": RECAP_PLATFORM_TABLE_NAME,
            "style": "Table Style Light 9",
            "columns": [
                {"header": RECAP_PLATFORM_HEADERS[0], "format": fmt_text},
                {"header": RECAP_PLATFORM_HEADERS[1], "formula": f_total_y_plat, "format": fmt_int},
                {"header": RECAP_PLATFORM_HEADERS[2], "formula": f_total_y1_plat, "format": fmt_int},
                {"header": RECAP_PLATFORM_HEADERS[3], "formula": f_total_obj_plat, "format": fmt_int},
                {"header": RECAP_PLATFORM_HEADERS[4], "formula": f_obj_increase_plat, "format": fmt_percent},
                {"header": RECAP_PLATFORM_HEADERS[5], "formula": f_sales_increase_plat, "format": fmt_percent},
                {"header": RECAP_PLATFORM_HEADERS[6], "formula": f_diff_plat, "format": fmt_percent_signed},
                {"header": RECAP_PLATFORM_HEADERS[7], "formula": f_salary_plat, "format": fmt_usd},
                {"header": RECAP_PLATFORM_HEADERS[8], "formula": f_bonus_plat, "format": fmt_usd},
            ],
            "header_row": True,
        },
    )

    ws_recap_platform.conditional_format(
        1,
        6,
        recap_platform_data_rows,
        6,
        {"type": "cell", "criteria": ">", "value": 0, "format": fmt_diff_pos},
    )
    ws_recap_platform.conditional_format(
        1,
        6,
        recap_platform_data_rows,
        6,
        {"type": "cell", "criteria": "<", "value": 0, "format": fmt_diff_neg},
    )

    for idx, plat in enumerate(platforms):
        excel_row = 1 + idx
        if excel_row > recap_platform_data_rows:
            break
        ws_recap_platform.write_string(excel_row, 0, plat, fmt_text)

    try:
        workbook.close()
    except FileCreateError as exc:
        raise FileCreateError(
            f"{exc}. If the file is open in Excel, close it or provide a different --output path."
        )
    return output_path


def main() -> None:
    args = _build_args()
    ref_month = _parse_month(args.month)
    output = create_template_excel(
        args.output,
        reference_month=ref_month,
        raw_rows=args.raw_rows,
        recap_rows=args.recap_rows,
    )
    print(f"Created: {output}")


if __name__ == "__main__":
    main()
