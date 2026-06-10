import calendar
import tempfile
from datetime import date

import db
import xlsxwriter
from dateutil.relativedelta import relativedelta
from xlsxwriter.utility import xl_rowcol_to_cell


# ═══════════════════════════════════════════════════════════════════════
# Utility functions (module-level, following VehicleDeliveryImpact pattern)
# ═══════════════════════════════════════════════════════════════════════

def _first_of_month(d: date) -> date:
    """Return the first day of the month for a given date."""
    return date(d.year, d.month, 1)


def _normalize_date(d) -> date:
    """Ensure *d* is a ``datetime.date``."""
    return d if isinstance(d, date) else date.fromisoformat(str(d))


def _label_for_offset(k: int) -> str:
    """Human-readable label for a month offset (M-6, M0, M+3, …)."""
    if k == 0:
        return 'M0'
    return f"M{k:+d}"


def _avg_by_month(rows, idx_value: int) -> dict[str, float]:
    """Compute the network average per calendar-month string from DB rows.

    Same logic as VehicleDeliveryImpact: for each calendar month, average
    across **all** sites that have data for that month.
    """
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for r in rows:
        m = r[1]
        v = r[idx_value]
        if v is None:
            continue
        sums[m] = sums.get(m, 0) + float(v)
        counts[m] = counts.get(m, 0) + 1
    return {m: sums[m] / counts[m] for m in sums if counts.get(m, 0) > 0}


def _ly_avg(sales_map: dict, site: str, m0_first: date, offsets_list: list[int]):
    """Compute Last-Year average (total and per-day) for *offsets_list* relative to *m0_first*."""
    total = 0
    total_pd = 0.0
    count = len(offsets_list)
    for o in offsets_list:
        mm_ly = m0_first + relativedelta(months=o, years=-1)
        val = sales_map.get((site, mm_ly.strftime('%Y-%m-01')), 0)
        total += val
        days = calendar.monthrange(mm_ly.year, mm_ly.month)[1]
        total_pd += (val / days) if days else 0
    avg = total / count if count > 0 else 0
    avg_pd = total_pd / count if count > 0 else 0
    return avg, avg_pd


def _prev_avg(m_vals: dict, m0_first: date, offsets_list: list[int], current_month: date):
    """Compute Previous-period average (total and per-day) for *offsets_list*, clamped to *current_month*."""
    total = 0
    total_pd = 0.0
    count = 0
    for o in offsets_list:
        mm = m0_first + relativedelta(months=o)
        if mm > current_month:
            continue
        val = m_vals.get(o, 0)
        total += val
        days = calendar.monthrange(mm.year, mm.month)[1]
        total_pd += (val / days) if days else 0
        count += 1
    avg = total / count if count > 0 else 0
    avg_pd = total_pd / count if count > 0 else 0
    return avg, avg_pd


def _fetch_site_metadata(con, site_ids: set) -> dict:
    """Fetch Tier and Platform for all given sites in a single query."""
    if not site_ids:
        return {}
    try:
        rows = con.execute(
            "SELECT Id_Site, Last_Tier, Platform FROM Sites WHERE Id_Site IN %s",
            (tuple(site_ids),),
        ).fetchall()
        return {r[0]: (r[1], r[2]) for r in rows}
    except Exception:
        result = {}
        for sid in site_ids:
            row = con.execute(
                "SELECT Last_Tier, Platform FROM Sites WHERE Id_Site = %s", (sid,)
            ).fetchone()
            result[sid] = (row[0], row[1]) if row else (None, None)
        return result


# ═══════════════════════════════════════════════════════════════════════
# Main function
# ═══════════════════════════════════════════════════════════════════════

def SalesTeamPerformance(workbook, Current_date: date):
    con = db.pool.connect()
    current_month = _first_of_month(Current_date)

    # ─── 1. Formats ──────────────────────────────────────────────────
    title_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFFF00', 'center_across': True, 'font_size': 18})
    head_fmt = workbook.add_format({'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'center_across': True, 'text_wrap': True})
    head_site_fmt = workbook.add_format({'bold': True, 'bg_color': '#DAEEF3', 'center_across': True, 'text_wrap': True})
    head_month_fmt = workbook.add_format({'bold': True, 'bg_color': '#00B050', 'font_color': 'white', 'center_across': True, 'text_wrap': True})
    head_right_fmt = workbook.add_format({'bold': True, 'bg_color': '#DAEEF3', 'align': 'right'})
    head_dark_green_fmt = workbook.add_format({'bold': True, 'bg_color': '#009900', 'font_color': 'white', 'center_across': True, 'text_wrap': True})
    num_fmt = workbook.add_format({'num_format': '#,##0'})
    pct_fmt = workbook.add_format({'num_format': '+0.0%;-0.0%'})
    bold_pct_fmt = workbook.add_format({'num_format': '+0.0%;-0.0%', 'bold': True})
    bold_num_fmt = workbook.add_format({'num_format': '#,##0', 'bold': True})
    future_fmt = workbook.add_format({'bg_color': '#D9E1F2', 'num_format': '#,##0'})
    m0_fmt = workbook.add_format({'bg_color': '#FFF2CC', 'bold': True, 'num_format': '#,##0'})
    date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    unit_value_fmt = workbook.add_format({'bg_color': '#FFFF00', 'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
    unit_label_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'right'})

    # ─── 2. Fetch event lists (all queries upfront) ──────────────────
    window_start = current_month + relativedelta(months=-11)
    window_end = current_month + relativedelta(months=+1)
    old_window_start = current_month + relativedelta(months=-24)
    old_window_end = current_month + relativedelta(months=-12)

    _event_query = """
        SELECT site, MIN(sale_date) AS m0_date
        FROM sale_team
        WHERE sale_date >= %s AND sale_date < %s
          AND sale_type = %s
          AND site IS NOT NULL AND site != ''
        GROUP BY site
        ORDER BY m0_date ASC, site ASC
    """
    interventions = con.execute(_event_query, (window_start, window_end, 'sale_intervention')).fetchall()
    openings = con.execute(_event_query, (window_start, window_end, 'opening_site')).fetchall()
    old_interventions = con.execute(_event_query, (old_window_start, old_window_end, 'sale_intervention')).fetchall()

    # ─── 3. Early exit ───────────────────────────────────────────────
    if not interventions:
        ws = workbook.add_worksheet('SalesTeam Sites')
        ws.set_zoom(90)
        ws.write(0, 0, 'No interventions recorded in the last 12 months', title_fmt)
        return

    # ─── 4. Normalize dates ──────────────────────────────────────────
    intervention_dates = [(r[0], _normalize_date(r[1])) for r in interventions]
    opening_dates = [(r[0], _normalize_date(r[1])) for r in openings]
    old_intervention_dates = [(r[0], _normalize_date(r[1])) for r in old_interventions]

    # ─── 5. Fetch site metadata (single query for all sites) ─────────
    all_site_ids = set()
    for event_list in (intervention_dates, opening_dates, old_intervention_dates):
        for site, _ in event_list:
            all_site_ids.add(site)
    tier_platform_map = _fetch_site_metadata(con, all_site_ids)

    # ─── 6. Fetch sales data (single query) ──────────────────────────
    all_m0 = [d for _, d in intervention_dates + opening_dates + old_intervention_dates]
    if not all_m0:
        all_m0 = [current_month]

    min_m = _first_of_month(min(all_m0)) + relativedelta(months=-6)
    max_m = _first_of_month(max(all_m0)) + relativedelta(months=+18)
    min_m_ly = min_m + relativedelta(years=-1)
    max_m_ly = max_m + relativedelta(years=-1)
    q_start = min(min_m, min_m_ly)
    q_end = max(max_m, max_m_ly) + relativedelta(months=+1)

    sales_rows = con.execute(
        """
        SELECT Sales.Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(Total_Sales,0) - IFNULL(Bottle_Sales,0)) AS bottles
        FROM Sales
        WHERE Month >= %s AND Month < %s
        GROUP BY Sales.Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()

    sales_map = {(r[0], r[1]): (r[2] or 0) for r in sales_rows}

    # ─── 7. Network averages (same logic as VehicleDeliveryImpact) ───
    network_avg = _avg_by_month(sales_rows, 2)

    # ─── 8. Define offsets ───────────────────────────────────────────
    month_offsets = list(range(-6, 7))    # M-6..M+6 for recent interventions
    old_offsets = list(range(-6, 19))      # M-6..M+18 for old interventions
    open_offsets = list(range(0, 12))      # M0..M+11 for openings

    # Unit cell reference (shared across sheets)
    unit_cell = "'SalesTeam Sites'!$C$1"

    # ─── Helper: write offset cells for a single site row ────────────
    def _write_offset_cells(ws, row, site, m0_first, offsets, col_start, unit_cell_ref=None):
        """Write month-offset value cells for one site row. Returns m_vals dict."""
        ref = unit_cell_ref or unit_cell
        m_vals = {}
        for idx, off in enumerate(offsets):
            mm = m0_first + relativedelta(months=off)
            col = col_start + idx
            if mm > current_month:
                ws.write_blank(row, col, None, future_fmt)
                continue
            val = sales_map.get((site, mm.strftime('%Y-%m-01')), 0)
            m_vals[off] = val
            days_in_m = calendar.monthrange(mm.year, mm.month)[1]
            formula_val = f"IF({ref}=\"Bot/day\",{val}/{days_in_m},{val})"
            cell_fmt = m0_fmt if off == 0 else num_fmt
            ws.write_formula(row, col, formula_val, cell_fmt)
        return m_vals

    # ─── Helper: write network-average Raw Data sheet ────────────────
    def _write_raw_data_sheet(ws, event_dates, offsets, unit_cell_ref=None):
        """Write a hidden Raw Data sheet with network averages aligned to each site's M0.
        Returns (first_data_row, last_data_row).
        """
        ref = unit_cell_ref or unit_cell
        ws.set_zoom(90)
        # Headers
        raw_headers = ['Site'] + [_label_for_offset(k) for k in offsets]
        for c, h in enumerate(raw_headers):
            if c == 0:
                ws.write(1, c, h, head_site_fmt)
                ws.set_column(c, c, max(16, len(h) + 2))
            else:
                ws.write(1, c, h, head_month_fmt)
                ws.set_column(c, c, 9)

        first_data_row = 2
        row = first_data_row
        for site, m0_real in event_dates:
            m0_first = _first_of_month(m0_real)
            ws.write(row, 0, site)
            for idx, off in enumerate(offsets):
                mm = m0_first + relativedelta(months=off)
                col = 1 + idx
                if mm > current_month:
                    ws.write_blank(row, col, None, future_fmt)
                    continue
                navg = network_avg.get(mm.strftime('%Y-%m-01'), 0)
                days_in_m = calendar.monthrange(mm.year, mm.month)[1]
                formula_navg = f"IF({ref}=\"Bot/day\",{navg}/{days_in_m},{navg})"
                ws.write_formula(row, col, formula_navg, num_fmt)
            row += 1

        last_data_row = row - 1

        # Top AVG row
        ws.write(0, 0, 'Total Avg', head_site_fmt)
        for j in range(len(offsets)):
            c = 1 + j
            start = xl_rowcol_to_cell(first_data_row, c)
            end = xl_rowcol_to_cell(last_data_row, c)
            ws.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

        return first_data_row, last_data_row

    # ─── Helper: write evolution chart block on ws2 ──────────────────
    def _write_evolution_block(ws2, block_row_start, dropdown_label, explanation,
                               event_dates, data_sheet_name, raw_sheet_name,
                               offsets, first_data_row_data, last_data_row_data,
                               first_data_row_raw, last_data_row_raw,
                               data_col_start, chart_title):
        """Write dropdown + data rows + chart for an evolution block.
        Returns the row after the chart.
        """
        # Dropdown
        ws2.write(block_row_start, 0, dropdown_label, unit_label_fmt)
        ws2.write(block_row_start, 1, 'Total Avg', unit_value_fmt)
        first_site_cell = xl_rowcol_to_cell(0, 0, True, True)
        last_site_cell = xl_rowcol_to_cell(last_data_row_data, 0, True, True)
        dv_source = f"='{data_sheet_name}'!{first_site_cell}:{last_site_cell}"
        ws2.data_validation(block_row_start, 1, block_row_start, 1, {'validate': 'list', 'source': dv_source})

        # Explanation
        ws2.write(block_row_start + 1, 0, explanation, head_site_fmt)

        # X-axis labels
        cat_row = block_row_start + 2
        val_row = block_row_start + 3
        val_row_net = block_row_start + 4

        for j, off in enumerate(offsets):
            ws2.write(cat_row, 1 + j, _label_for_offset(off), head_month_fmt)

        # Row labels matching chart series (blue bg)
        ws2.write(val_row, 0, 'Selected site', head_fmt)
        ws2.write(val_row_net, 0, 'Network avg', head_fmt)

        # Dropdown cell reference
        dd_cell = f"$B${block_row_start + 1}"

        # Per-column formulas
        for j in range(len(offsets)):
            # Selected site value from data sheet
            col_data = data_col_start + j
            start_addr = xl_rowcol_to_cell(first_data_row_data, col_data)
            end_addr = xl_rowcol_to_cell(last_data_row_data, col_data)
            range_addr = f"'{data_sheet_name}'!{start_addr}:{end_addr}"
            match_col = f"'{data_sheet_name}'!$A:$A"
            offset_val = first_data_row_data
            formula = (
                f"IF({dd_cell}=\"Total Avg\",SUBTOTAL(1,{range_addr}),"
                f"IFERROR(INDEX({range_addr},MATCH({dd_cell},{match_col},0)-{offset_val}),\"\"))"
            )
            ws2.write_formula(val_row, 1 + j, formula, num_fmt)

            # Network average values from raw data sheet
            raw_start = xl_rowcol_to_cell(first_data_row_raw, 1 + j)
            raw_end = xl_rowcol_to_cell(last_data_row_raw, 1 + j)
            raw_range = f"'{raw_sheet_name}'!{raw_start}:{raw_end}"
            raw_match = f"'{raw_sheet_name}'!$A:$A"
            raw_offset = first_data_row_raw
            formula_net = (
                f"IF({dd_cell}=\"Total Avg\",SUBTOTAL(1,{raw_range}),"
                f"IFERROR(INDEX({raw_range},MATCH({dd_cell},{raw_match},0)-{raw_offset}),\"\"))"
            )
            ws2.write_formula(val_row_net, 1 + j, formula_net, num_fmt)

        # Chart
        chart = workbook.add_chart({'type': 'line'})
        sheet_name = ws2.get_name()
        chart.add_series({
            'name':       'Selected site',
            'categories': [sheet_name, cat_row, 1, cat_row, 1 + len(offsets) - 1],
            'values':     [sheet_name, val_row, 1, val_row, 1 + len(offsets) - 1],
        })
        chart.add_series({
            'name':       'Network avg',
            'categories': [sheet_name, cat_row, 1, cat_row, 1 + len(offsets) - 1],
            'values':     [sheet_name, val_row_net, 1, val_row_net, 1 + len(offsets) - 1],
        })
        chart.set_title({'name': chart_title})
        chart.set_y_axis({'name': 'Bottles'})
        chart.set_x_axis({'name': 'Month relative to M0'})
        chart.set_legend({'position': 'bottom'})

        chart_row = val_row_net + 1
        ws2.insert_chart(chart_row, 1, chart, {'x_scale': 1.4, 'y_scale': 1.2})

        return chart_row + 16  # approximate height of chart in rows

    # ─── Helper: write a data sheet (Sites, Old, Openings) ───────────
    def _write_data_sheet(ws, event_dates, offsets, date_col_label,
                          col_start=4, *, write_comparison=False, unit_cell_ref=None):
        """Write a data sheet with site info + offset values.
        Returns (first_data_row, last_data_row).
        """
        ws.set_zoom(90)

        # Headers
        info_headers = ['Site', 'Platform', 'Tier', date_col_label]
        all_headers = info_headers + [_label_for_offset(k) for k in offsets]

        for c, h in enumerate(all_headers):
            if c < col_start:
                ws.write(1, c, h, head_site_fmt)
                ws.set_column(c, c, max(16, len(h) + 2))
            else:
                ws.write(1, c, h, head_month_fmt)
                ws.set_column(c, c, 9)

        first_data_row = 2
        row = first_data_row

        for site, m0_real in event_dates:
            m0_first = _first_of_month(m0_real)

            ws.write(row, 0, site)
            tp = tier_platform_map.get(site, (None, None))
            ws.write(row, 1, '' if tp[1] is None else tp[1])
            ws.write(row, 2, '' if tp[0] is None else tp[0])
            ws.write_datetime(row, 3, m0_real, date_fmt)

            _write_offset_cells(ws, row, site, m0_first, offsets, col_start, unit_cell_ref)
            row += 1

        last_data_row = row - 1

        # Top AVG row
        ws.write(0, 0, 'Total Avg', head_site_fmt)
        ws.write(0, col_start - 1, 'AVG', head_right_fmt)
        for c in range(col_start, col_start + len(offsets)):
            start = xl_rowcol_to_cell(first_data_row, c)
            end = xl_rowcol_to_cell(last_data_row, c)
            ws.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

        return first_data_row, last_data_row

    # ══════════════════════════════════════════════════════════════════
    # SHEET 1: SalesTeam Sites (main data with comparison columns)
    # ══════════════════════════════════════════════════════════════════
    ws = workbook.add_worksheet('SalesTeam Sites')
    ws.set_zoom(90)

    # Headers
    c_site = 0
    c_platform = 1
    c_tier = 2
    c_date = 3
    c_mstart = 4
    c_m0 = c_mstart + month_offsets.index(0)
    c_after = c_mstart + len(month_offsets)
    c_avg3 = c_after
    c_avg3_ly = c_after + 1
    c_prev3 = c_after + 2
    c_yoy3 = c_after + 3
    c_vs_prev3 = c_after + 4
    c_avg6 = c_after + 5
    c_avg6_ly = c_after + 6
    c_prev6 = c_after + 7
    c_yoy6 = c_after + 8
    c_vs_prev6 = c_after + 9

    headers = (
        ['Site', 'Platform', 'Tier', 'Intervention date']
        + [_label_for_offset(k) for k in month_offsets]
        + ['Avg M+1..M+3', 'LY Avg M+1..M+3', 'Prev Avg M-1..M-3', 'YoY vs LY (3m)', 'Vs Prev (3m)',
           'Avg M+1..M+6', 'LY Avg M+1..M+6', 'Prev Avg M-1..M-6', 'YoY vs LY (6m)', 'Vs Prev (6m)']
    )

    for c, h in enumerate(headers):
        if c < c_mstart:
            ws.write(1, c, h, head_site_fmt)
            ws.set_column(c, c, max(16, len(h) + 2))
        elif c_mstart <= c < c_after:
            ws.write(1, c, h, head_month_fmt)
            ws.set_column(c, c, 9)
        else:
            fmt = head_dark_green_fmt if c in (c_vs_prev3, c_vs_prev6) else head_fmt
            ws.write(1, c, h, fmt)
            ws.set_column(c, c, max(14, len(h) + 2))

    # Group columns M-6..M-4 and M+4..M+6 (hidden by default)
    for i in range(3):
        left_col = c_mstart + month_offsets.index(-6) + i
        right_col = c_mstart + month_offsets.index(4) + i
        ws.set_column(left_col, left_col, None, None, {'level': 1, 'hidden': True})
        ws.set_column(right_col, right_col, None, None, {'level': 1, 'hidden': True})

    # Units selector
    ws.write(0, 1, 'Units:', unit_label_fmt)
    ws.write(0, 2, 'Bot', unit_value_fmt)
    ws.data_validation(0, 2, 0, 2, {'validate': 'list', 'source': ['Bot', 'Bot/day']})
    ws.set_column(1, 2, 14)

    # Data rows
    first_data_row = 2
    row = first_data_row

    for site, m0_real in intervention_dates:
        m0_first = _first_of_month(m0_real)

        ws.write(row, c_site, site)
        tp = tier_platform_map.get(site, (None, None))
        ws.write(row, c_platform, '' if tp[1] is None else tp[1])
        ws.write(row, c_tier, '' if tp[0] is None else tp[0])
        ws.write_datetime(row, c_date, m0_real, date_fmt)

        # Month-offset values
        m_vals = _write_offset_cells(ws, row, site, m0_first, month_offsets, c_mstart)

        # ── 3-month comparison (M+1..M+3) ──
        offs3 = [1, 2, 3]
        cells3 = [xl_rowcol_to_cell(row, c_mstart + month_offsets.index(o)) for o in offs3]
        ws.write_formula(row, c_avg3, f"IFERROR(AVERAGE({','.join(cells3)}),\"\")", bold_num_fmt)

        avg3_ly, avg3_ly_pd = _ly_avg(sales_map, site, m0_first, offs3)
        ws.write_formula(row, c_avg3_ly, f"IF({unit_cell}=\"Bot/day\",{avg3_ly_pd},{avg3_ly})", bold_num_fmt)

        avg3_prev, avg3_prev_pd = _prev_avg(m_vals, m0_first, [-1, -2, -3], current_month)
        ws.write_formula(row, c_prev3, f"IF({unit_cell}=\"Bot/day\",{avg3_prev_pd},{avg3_prev})", bold_num_fmt)

        cur_cell3 = xl_rowcol_to_cell(row, c_avg3)
        ly_cell3 = xl_rowcol_to_cell(row, c_avg3_ly)
        prev3_cell = xl_rowcol_to_cell(row, c_prev3)
        ws.write_formula(row, c_yoy3, f"IF({ly_cell3}>0,{cur_cell3}/{ly_cell3}-1,\"\")", pct_fmt)
        ws.write_formula(row, c_vs_prev3, f"IF({prev3_cell}>0,{cur_cell3}/{prev3_cell}-1,\"\")", pct_fmt)

        # ── 6-month comparison (M+1..M+6) ──
        offs6 = [1, 2, 3, 4, 5, 6]
        cells6 = [xl_rowcol_to_cell(row, c_mstart + month_offsets.index(o)) for o in offs6]
        ws.write_formula(row, c_avg6, f"IFERROR(AVERAGE({','.join(cells6)}),\"\")", bold_num_fmt)

        avg6_ly, avg6_ly_pd = _ly_avg(sales_map, site, m0_first, offs6)
        ws.write_formula(row, c_avg6_ly, f"IF({unit_cell}=\"Bot/day\",{avg6_ly_pd},{avg6_ly})", bold_num_fmt)

        avg6_prev, avg6_prev_pd = _prev_avg(m_vals, m0_first, [-1, -2, -3, -4, -5, -6], current_month)
        ws.write_formula(row, c_prev6, f"IF({unit_cell}=\"Bot/day\",{avg6_prev_pd},{avg6_prev})", bold_num_fmt)

        cur_cell6 = xl_rowcol_to_cell(row, c_avg6)
        ly_cell6 = xl_rowcol_to_cell(row, c_avg6_ly)
        prev6_cell = xl_rowcol_to_cell(row, c_prev6)
        ws.write_formula(row, c_yoy6, f"IF({ly_cell6}>0,{cur_cell6}/{ly_cell6}-1,\"\")", pct_fmt)
        ws.write_formula(row, c_vs_prev6, f"IF({prev6_cell}>0,{cur_cell6}/{prev6_cell}-1,\"\")", pct_fmt)

        row += 1

    last_data_row = row - 1

    # Top AVG row
    ws.write(0, c_site, 'Total Avg', head_site_fmt)
    ws.write(0, c_mstart - 1, 'AVG', head_right_fmt)

    for c in list(range(c_mstart + 1, c_after)) + [c_avg3, c_avg3_ly, c_prev3, c_avg6, c_avg6_ly, c_prev6]:
        start = xl_rowcol_to_cell(first_data_row, c)
        end = xl_rowcol_to_cell(last_data_row, c)
        ws.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

    # YoY totals (ratio of averages, not average of ratios)
    for (c_cur, c_ly, c_yoy) in [(c_avg3, c_avg3_ly, c_yoy3), (c_avg6, c_avg6_ly, c_yoy6)]:
        cs = xl_rowcol_to_cell(first_data_row, c_cur)
        ce = xl_rowcol_to_cell(last_data_row, c_cur)
        ls = xl_rowcol_to_cell(first_data_row, c_ly)
        le = xl_rowcol_to_cell(last_data_row, c_ly)
        ws.write_formula(0, c_yoy,
            f"IF(SUBTOTAL(1,{ls}:{le})>0,SUBTOTAL(1,{cs}:{ce})/SUBTOTAL(1,{ls}:{le})-1,\"\")",
            bold_pct_fmt)

    # Vs Prev totals
    for (c_cur, c_prev, c_vs) in [(c_avg3, c_prev3, c_vs_prev3), (c_avg6, c_prev6, c_vs_prev6)]:
        cs = xl_rowcol_to_cell(first_data_row, c_cur)
        ce = xl_rowcol_to_cell(last_data_row, c_cur)
        ps = xl_rowcol_to_cell(first_data_row, c_prev)
        pe = xl_rowcol_to_cell(last_data_row, c_prev)
        ws.write_formula(0, c_vs,
            f"IF(SUBTOTAL(1,{ps}:{pe})>0,SUBTOTAL(1,{cs}:{ce})/SUBTOTAL(1,{ps}:{pe})-1,\"\")",
            bold_pct_fmt)

    # Hide/group LY and Prev columns
    for c in (c_avg3_ly, c_avg6_ly, c_prev3, c_prev6):
        ws.set_column(c, c, None, None, {'level': 1, 'hidden': True})

    # Autofilter and freeze panes
    ws.autofilter(1, 0, last_data_row, c_vs_prev6)
    ws.freeze_panes(first_data_row, 4)

    # Conditional formatting: arrows in YoY / Vs Prev columns
    up_arrow_fmt = workbook.add_format({'font_color': '#00B050', 'bold': True, 'num_format': '+0.0% "↑"'})
    down_arrow_fmt = workbook.add_format({'font_color': '#C00000', 'bold': True, 'num_format': '-0.0% "↓"'})
    for col in (c_yoy3, c_yoy6, c_vs_prev3, c_vs_prev6):
        ws.conditional_format(first_data_row, col, last_data_row, col, {
            'type': 'cell', 'criteria': '>=', 'value': 0.1, 'format': up_arrow_fmt})
        ws.conditional_format(first_data_row, col, last_data_row, col, {
            'type': 'cell', 'criteria': '<=', 'value': -0.1, 'format': down_arrow_fmt})

    # ══════════════════════════════════════════════════════════════════
    # SHEET 2: Raw Data (hidden) – network avg aligned to intervention M0
    # ══════════════════════════════════════════════════════════════════
    ws_raw = workbook.add_worksheet('Raw Data')
    first_data_row_raw, last_data_row_raw = _write_raw_data_sheet(ws_raw, intervention_dates, month_offsets)
    ws_raw.hide()

    # ══════════════════════════════════════════════════════════════════
    # SHEET 3: Sales Evolution (charts + dropdowns)
    # ══════════════════════════════════════════════════════════════════
    ws2 = workbook.add_worksheet('Sales Evolution')
    ws2.set_zoom(90)
    ws2.set_column(0, 0, 40)
    ws2.set_column(1, 1, 12)

    # Recent interventions block
    _write_evolution_block(
        ws2, block_row_start=0,
        dropdown_label='Site interventions:',
        explanation='Sales Evolution (M-6 to M+6)',
        event_dates=intervention_dates,
        data_sheet_name='SalesTeam Sites',
        raw_sheet_name='Raw Data',
        offsets=month_offsets,
        first_data_row_data=first_data_row,
        last_data_row_data=last_data_row,
        first_data_row_raw=first_data_row_raw,
        last_data_row_raw=last_data_row_raw,
        data_col_start=c_mstart,
        chart_title='Sales Evolution (M-6 to M+6)',
    )

    # ══════════════════════════════════════════════════════════════════
    # SHEETS 4-5: Old Interventions Sites + Raw Data Old (hidden)
    # ══════════════════════════════════════════════════════════════════
    if old_intervention_dates:
        ws_old = workbook.add_worksheet('Old Interventions Sites')
        first_data_row_old, last_data_row_old = _write_data_sheet(
            ws_old, old_intervention_dates, old_offsets, 'Intervention date')

        ws_old_raw = workbook.add_worksheet('Raw Data Old')
        first_data_row_old_raw, last_data_row_old_raw = _write_raw_data_sheet(
            ws_old_raw, old_intervention_dates, old_offsets)

        # Old interventions block on the Sales Evolution sheet
        _write_evolution_block(
            ws2, block_row_start=22,
            dropdown_label='Old site interventions:',
            explanation='Old interventions (M-6 to M+18)',
            event_dates=old_intervention_dates,
            data_sheet_name='Old Interventions Sites',
            raw_sheet_name='Raw Data Old',
            offsets=old_offsets,
            first_data_row_data=first_data_row_old,
            last_data_row_data=last_data_row_old,
            first_data_row_raw=first_data_row_old_raw,
            last_data_row_raw=last_data_row_old_raw,
            data_col_start=4,
            chart_title='Old interventions (M-6 to M+18)',
        )

        ws_old.hide()
        ws_old_raw.hide()

    # ══════════════════════════════════════════════════════════════════
    # SHEETS 6-8: Openings Sites + Raw Data Opening + Openings Evolution
    # ══════════════════════════════════════════════════════════════════
    ws_open = workbook.add_worksheet('Openings Sites')
    ws_open.set_zoom(90)

    if opening_dates:
        first_data_row_open, last_data_row_open = _write_data_sheet(
            ws_open, opening_dates, open_offsets, 'Opening date',
            unit_cell_ref="'Openings Sites'!$C$1")

        # Units dropdown on Openings Sites
        ws_open.write(0, 1, 'Units:', unit_label_fmt)
        ws_open.write(0, 2, 'Bot', unit_value_fmt)
        ws_open.data_validation(0, 2, 0, 2, {'validate': 'list', 'source': ['Bot', 'Bot/day']})
        ws_open.set_column(1, 2, 14)

        ws_open_raw = workbook.add_worksheet('Raw Data Opening')
        first_data_row_open_raw, last_data_row_open_raw = _write_raw_data_sheet(
            ws_open_raw, opening_dates, open_offsets,
            unit_cell_ref="'Openings Sites'!$C$1")

        # Openings Evolution chart sheet
        ws_open2 = workbook.add_worksheet('Openings Evolution')
        ws_open2.set_zoom(90)
        ws_open2.set_column(0, 0, 10)
        ws_open2.set_column(1, 1, 12)

        # Dropdown
        ws_open2.write(1, 0, 'Site:', unit_label_fmt)
        ws_open2.write(1, 1, 'Total Avg', unit_value_fmt)
        first_open_site = xl_rowcol_to_cell(0, 0, True, True)
        last_open_site = xl_rowcol_to_cell(last_data_row_open, 0, True, True)
        ws_open2.data_validation(1, 1, 1, 1, {
            'validate': 'list',
            'source': f"='Openings Sites'!{first_open_site}:{last_open_site}",
        })

        # Labels
        cat_row_open = 4
        val_row_open = 5
        val_row_open_net = 6

        for j, off in enumerate(open_offsets):
            ws_open2.write(cat_row_open, 1 + j, _label_for_offset(off), head_month_fmt)

        ws_open2.write(val_row_open, 0, 'Selected site', head_fmt)
        ws_open2.write(val_row_open_net, 0, 'Network avg', head_fmt)

        # Per-column formulas (same INDEX/MATCH pattern)
        for j in range(len(open_offsets)):
            col_data = 4 + j
            s = xl_rowcol_to_cell(first_data_row_open, col_data)
            e = xl_rowcol_to_cell(last_data_row_open, col_data)
            rng = f"'Openings Sites'!{s}:{e}"
            mcol = "'Openings Sites'!$A:$A"
            ov = first_data_row_open
            ws_open2.write_formula(val_row_open, 1 + j,
                f"IF($B$2=\"Total Avg\",SUBTOTAL(1,{rng}),IFERROR(INDEX({rng},MATCH($B$2,{mcol},0)-{ov}),\"\"))",
                num_fmt)

            rs = xl_rowcol_to_cell(first_data_row_open_raw, 1 + j)
            re = xl_rowcol_to_cell(last_data_row_open_raw, 1 + j)
            rrng = f"'Raw Data Opening'!{rs}:{re}"
            rmcol = "'Raw Data Opening'!$A:$A"
            rov = first_data_row_open_raw
            ws_open2.write_formula(val_row_open_net, 1 + j,
                f"IF($B$2=\"Total Avg\",SUBTOTAL(1,{rrng}),IFERROR(INDEX({rrng},MATCH($B$2,{rmcol},0)-{rov}),\"\"))",
                num_fmt)

        # Chart
        chart_open = workbook.add_chart({'type': 'line'})
        chart_open.add_series({
            'name':       'Selected site',
            'categories': ['Openings Evolution', cat_row_open, 1, cat_row_open, 1 + len(open_offsets) - 1],
            'values':     ['Openings Evolution', val_row_open, 1, val_row_open, 1 + len(open_offsets) - 1],
        })
        chart_open.add_series({
            'name':       'Network avg',
            'categories': ['Openings Evolution', cat_row_open, 1, cat_row_open, 1 + len(open_offsets) - 1],
            'values':     ['Openings Evolution', val_row_open_net, 1, val_row_open_net, 1 + len(open_offsets) - 1],
        })
        chart_open.set_title({'name': 'Sales Evolution after opening (M0 to M+11)'})
        chart_open.set_y_axis({'name': 'Bottles'})
        chart_open.set_x_axis({'name': 'Month relative to M0'})
        chart_open.set_legend({'position': 'bottom'})

        ws_open2.insert_chart(8, 1, chart_open, {'x_scale': 1.4, 'y_scale': 1.2})

        ws_open_raw.hide()

        # ══════════════════════════════════════════════════════════════
        # SHEET 9: Salesman Lending (matrix)
        # ══════════════════════════════════════════════════════════════
        cutoff_date = date(2025, 5, 1)
        if Current_date >= cutoff_date:
            _write_salesman_lending(con, workbook, ws_sheet_fmts={
                'head_site_fmt': head_site_fmt,
                'head_fmt': head_fmt,
                'num_fmt': num_fmt,
                'bold_num_fmt': bold_num_fmt,
                'date_fmt': date_fmt,
            }, cutoff_date=cutoff_date, Current_date=Current_date)


def _write_salesman_lending(con, workbook, *, ws_sheet_fmts, cutoff_date, Current_date):
    """Write the Salesman Lending pivot sheet."""
    head_site_fmt = ws_sheet_fmts['head_site_fmt']
    head_fmt = ws_sheet_fmts['head_fmt']
    num_fmt = ws_sheet_fmts['num_fmt']
    bold_num_fmt = ws_sheet_fmts['bold_num_fmt']
    date_fmt = ws_sheet_fmts['date_fmt']

    sales_start = cutoff_date
    sales_end = date(Current_date.year + 1, 1, 1)

    # Fetch sites, officers, intervention dates and lending sums in bulk
    sites_this_year = con.execute(
        """
        SELECT DISTINCT site
        FROM sale_team
        WHERE sale_type = 'sale_intervention'
          AND sale_date >= %s AND sale_date < %s
          AND site IS NOT NULL AND site != ''
        ORDER BY site
        """,
        (sales_start, sales_end),
    ).fetchall()

    officers_this_year = con.execute(
        """
        SELECT DISTINCT sale_officer1
        FROM sale_team
        WHERE sale_type = 'sale_intervention'
          AND sale_date >= %s AND sale_date < %s
          AND sale_officer1 IS NOT NULL AND sale_officer1 != ''
        ORDER BY sale_officer1
        """,
        (sales_start, sales_end),
    ).fetchall()

    if not sites_this_year or not officers_this_year:
        return

    intervention_dates_rows = con.execute(
        """
        SELECT site, MIN(sale_date) AS first_date
        FROM sale_team
        WHERE sale_type = 'sale_intervention'
          AND sale_date >= %s AND sale_date < %s
          AND site IS NOT NULL AND site != ''
        GROUP BY site
        ORDER BY site
        """,
        (sales_start, sales_end),
    ).fetchall()
    intervention_date_map = {
        r[0]: _normalize_date(r[1]) for r in intervention_dates_rows
    }

    lending_rows = con.execute(
        """
        SELECT site, sale_officer1, SUM(IFNULL(lending_bottle,0)) AS lend_sum
        FROM sale_team
        WHERE sale_type = 'sale_intervention'
          AND sale_date >= %s AND sale_date < %s
          AND site IS NOT NULL AND site != ''
          AND sale_officer1 IS NOT NULL AND sale_officer1 != ''
        GROUP BY site, sale_officer1
        """,
        (sales_start, sales_end),
    ).fetchall()
    lending_map = {(r[0], r[1]): (r[2] or 0) for r in lending_rows}

    # Fetch site metadata for Platform/Tier
    lending_site_ids = {r[0] for r in sites_this_year}
    lending_meta = _fetch_site_metadata(con, lending_site_ids)

    # ── Write sheet ──────────────────────────────────────────────────
    ws = workbook.add_worksheet('Salesman Lending')
    ws.set_zoom(90)

    header_row = 2
    officer_col_start = 4
    total_col = officer_col_start + len(officers_this_year)

    ws.write(header_row, 0, 'Site', head_site_fmt)
    ws.write(header_row, 1, 'Platform', head_site_fmt)
    ws.write(header_row, 2, 'Tier', head_site_fmt)
    ws.write(header_row, 3, 'Intervention date', head_site_fmt)
    ws.set_column(0, 0, 16)
    ws.set_column(1, 1, 14)
    ws.set_column(2, 2, 10)
    ws.set_column(3, 3, 18)
    for idx, row_off in enumerate(officers_this_year):
        officer = row_off[0]
        col = officer_col_start + idx
        ws.write(header_row, col, officer, head_site_fmt)
        ws.set_column(col, col, max(14, len(str(officer)) + 2))
    ws.write(header_row, total_col, 'Total', head_fmt)
    ws.set_column(total_col, total_col, 14)

    first_data_row = header_row + 1
    for offset, row_site in enumerate(sites_this_year):
        row_idx = first_data_row + offset
        site_id = row_site[0]
        ws.write(row_idx, 0, site_id, head_site_fmt)

        tp = lending_meta.get(site_id, (None, None))
        ws.write(row_idx, 1, '' if tp[1] is None else tp[1])
        ws.write(row_idx, 2, '' if tp[0] is None else tp[0])

        idate = intervention_date_map.get(site_id)
        if idate:
            ws.write_datetime(row_idx, 3, idate, date_fmt)

        for col_idx, row_off in enumerate(officers_this_year):
            val = lending_map.get((site_id, row_off[0]), 0)
            if val:
                ws.write_number(row_idx, officer_col_start + col_idx, val, num_fmt)

        # Total per site
        first_off = xl_rowcol_to_cell(row_idx, officer_col_start)
        last_off = xl_rowcol_to_cell(row_idx, officer_col_start + len(officers_this_year) - 1)
        ws.write_formula(row_idx, total_col, f"SUM({first_off}:{last_off})", bold_num_fmt)

    last_data_row = first_data_row + len(sites_this_year) - 1

    # Summary rows above
    ws.write(0, 0, 'Sum', head_site_fmt)
    ws.write(1, 0, 'Average', head_site_fmt)
    for col in range(officer_col_start, total_col + 1):
        s = xl_rowcol_to_cell(first_data_row, col)
        e = xl_rowcol_to_cell(last_data_row, col)
        ws.write_formula(0, col, f"SUBTOTAL(9,{s}:{e})", bold_num_fmt)
        ws.write_formula(1, col, f"SUBTOTAL(1,{s}:{e})", bold_num_fmt)

    ws.autofilter(header_row, 0, last_data_row, total_col)


# ═══════════════════════════════════════════════════════════════════════
# Launcher
# ═══════════════════════════════════════════════════════════════════════

def LaunchExcelSalesTeamPerformance(Current_date: date):
    Month = Current_date.month
    Month = ('0' + str(Month)) if Month < 10 else str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir() + '/SalesTeam Performance ' + Year + '-' + Month + '.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    SalesTeamPerformance(workbook, Current_date)
    workbook.close()
    return filepath


if __name__ == '__main__':
    LaunchExcelSalesTeamPerformance(date(2025, 10, 1))
