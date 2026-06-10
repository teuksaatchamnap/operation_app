import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from datetime import date
from dateutil.relativedelta import relativedelta
import tempfile
import db
import calendar


def _first_of_month(d: date) -> date:
    return date(d.year, d.month, 1)


def SalesTeamPerformance(workbook, Current_date: date):
    con = db.pool.connect()

    # Formats (aligned with Technical dashboard look & feel)
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
    future_fmt = workbook.add_format({'bg_color': '#D9E1F2', 'num_format': '#,##0'})  # light blue for unreached future months
    m0_fmt = workbook.add_format({'bg_color': '#FFF2CC', 'bold': True, 'num_format': '#,##0'})
    date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd'})
    # Large yellow format for the global Units selector (value cell)
    unit_value_fmt = workbook.add_format({'bg_color': '#FFFF00', 'bold': True, 'font_size': 16, 'align': 'center', 'valign': 'vcenter'})
    unit_label_fmt = workbook.add_format({'bold': True, 'font_size': 12, 'align': 'right'})

    # 1) Interventions over last 12 months (rolling window)
    window_start = _first_of_month(Current_date) + relativedelta(months=-11)
    window_end = _first_of_month(Current_date) + relativedelta(months=+1)  # exclusive
    interventions = con.execute(
        """
        SELECT site, MIN(sale_date) AS m0_date
        FROM sale_team
        WHERE sale_date >= %s AND sale_date < %s AND sale_type = "sale_intervention"
          AND site IS NOT NULL AND site != ''
        GROUP BY site
        ORDER BY m0_date ASC, site ASC
        """,
        (window_start, window_end)
    ).fetchall()

    ws = workbook.add_worksheet('SalesTeam Sites')
    ws.set_zoom(90)

    if not interventions:
        ws.write(0, 0, 'No interventions recorded in the last 12 months', title_fmt)
        return

    # Fetch Tier and Platform for these sites
    site_ids = tuple(r[0] for r in interventions)
    tier_platform_map = {}
    try:
        rows_tp = con.execute("SELECT Id_Site, Last_Tier, Platform FROM Sites WHERE Id_Site IN %s", (site_ids,)).fetchall()
        tier_platform_map = {r[0]: (r[1], r[2]) for r in rows_tp}
    except Exception:
        # Fallback: query one by one if IN %s not supported
        for sid in site_ids:
            row = con.execute("SELECT Last_Tier, Platform FROM Sites WHERE Id_Site = %s", (sid,)).fetchone()
            if row:
                tier_platform_map[sid] = (row[0], row[1])
            else:
                tier_platform_map[sid] = (None, None)

    # 1b) Openings over last 12 months (rolling window), Option A: M0..M+12
    openings = con.execute(
        """
        SELECT site, MIN(sale_date) AS m0_date
        FROM sale_team
        WHERE sale_date >= %s AND sale_date < %s AND sale_type = "opening_site"
          AND site IS NOT NULL AND site != ''
        GROUP BY site
        ORDER BY m0_date ASC, site ASC
        """,
        (window_start, window_end)
    ).fetchall()

        # 1c) "Old" interventions: interventions that happened 12–24 months before Current_date
    old_window_start = _first_of_month(Current_date) + relativedelta(months=-24)
    old_window_end = _first_of_month(Current_date) + relativedelta(months=-12)  # exclusive
    old_interventions = con.execute(
                """
                SELECT site, MIN(sale_date) AS m0_date
                FROM sale_team
                WHERE sale_date >= %s AND sale_date < %s AND sale_type = "sale_intervention"
                    AND site IS NOT NULL AND site != ''
                GROUP BY site
                ORDER BY m0_date ASC, site ASC
                """,
                (old_window_start, old_window_end)
        ).fetchall()

        # 2) Fetch sales buckets: bottles per site per month for needed range (min/max across interventions, openings and old_interventions) and LY
    all_m0_dates = []
    if interventions:
        all_m0_dates.extend([(r[1] if isinstance(r[1], date) else date.fromisoformat(str(r[1]))) for r in interventions])
    if openings:
        all_m0_dates.extend([(r[1] if isinstance(r[1], date) else date.fromisoformat(str(r[1]))) for r in openings])
    if old_interventions:
        all_m0_dates.extend([(r[1] if isinstance(r[1], date) else date.fromisoformat(str(r[1]))) for r in old_interventions])

    # If there are openings but no interventions, ensure we still have dates
    if not all_m0_dates:
        all_m0_dates.append(_first_of_month(Current_date))

    # Interventions need -6..+6, openings need 0..+12, old interventions need -6..+18
    min_m = _first_of_month(min(all_m0_dates)) + relativedelta(months=-6)
    max_m = _first_of_month(max(all_m0_dates)) + relativedelta(months=+18)
    min_m_ly = min_m + relativedelta(years=-1)
    max_m_ly = max_m + relativedelta(years=-1)
    q_start = min(min_m, min_m_ly)
    q_end = max(max_m, max_m_ly) + relativedelta(months=+1)  # exclusive

    sales_rows = con.execute(
        """
        SELECT Sales.Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(Total_Sales,0) - IFNULL(Bottle_Sales,0)) AS bottles
        FROM Sales
        WHERE Month >= %s AND Month < %s
        GROUP BY Sales.Id_Site, m
        """,
        (q_start, q_end)
    ).fetchall()
    sales_map = {(r[0], r[1]): (r[2] or 0) for r in sales_rows}

    # Compute network average (across sites) per absolute calendar month in range
    month_sums = {}
    month_counts = {}
    for r in sales_rows:
        m = r[1]
        val = r[2] or 0
        month_sums[m] = month_sums.get(m, 0) + val
        month_counts[m] = month_counts.get(m, 0) + 1
    month_avg = {m: (month_sums[m] / month_counts[m]) if month_counts[m] > 0 else 0 for m in month_sums}

    # 3) Headers
    month_offsets = list(range(-6, 7))
    def label_for_offset(k: int) -> str:
        if k == 0:
            return 'M0'
        return f"M{k:+d}".replace('+0', '0')

    headers = ['Site', 'Platform', 'Tier', 'Intervention date'] + [label_for_offset(k) for k in month_offsets] + [
        'Avg M+1..M+3', 'LY Avg M+1..M+3', 'Prev Avg M-1..M-3', 'YoY vs LY (3m)', 'Vs Prev (3m)',
        'Avg M+1..M+6', 'LY Avg M+1..M+6', 'Prev Avg M-1..M-6', 'YoY vs LY (6m)', 'Vs Prev (6m)'
    ]

    # Column indices
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

    # Write headers (row 1), keep row 0 for top AVG row
    for c, h in enumerate(headers):
        if c < c_mstart:
            ws.write(1, c, h, head_site_fmt)
            ws.set_column(c, c, max(16, len(h) + 2))
        elif c_mstart <= c < c_mstart + len(month_offsets):
            # Green for M-6..M+6 (including M-6..M-4 and M-3..M+6)
            off = month_offsets[c - c_mstart]
            fmt = head_month_fmt if (-6 <= off <= 6) else head_fmt
            ws.write(1, c, h, fmt)
            ws.set_column(c, c, 9)
        else:
            # Darker green for Vs Prev columns as requested
            fmt = head_dark_green_fmt if c in (c_vs_prev3, c_vs_prev6) else head_fmt
            ws.write(1, c, h, fmt)
            ws.set_column(c, c, max(14, len(h) + 2))

    # Group columns for M-6..M-4 and M+4..M+6
    left_grp_start = c_mstart + month_offsets.index(-6)
    left_grp_end = c_mstart + month_offsets.index(-4)
    right_grp_start = c_mstart + month_offsets.index(4)
    right_grp_end = c_mstart + month_offsets.index(6)
    # Apply outline level and hide; no 'collapsed' flags per request
    for i in range(3):
        ws.set_column(left_grp_start+i, left_grp_start+i, None, None, {'level': 1, 'hidden': True})
        ws.set_column(right_grp_start+i, right_grp_start+i, None, None, {'level': 1, 'hidden': True})

    # Global Units selector on the SalesTeam Sites sheet (controls the whole workbook)
    # Place in C1 (row 0, col 2) with a big yellow background
    ws.write(0, 1, 'Units:', unit_label_fmt)
    ws.write(0, 2, 'Bot', unit_value_fmt)
    ws.data_validation(0, 2, 0, 2, {'validate': 'list', 'source': ['Bot', 'Bot/day']})
    ws.set_column(1, 2, 14)

    # 4) Data rows
    first_data_row = 2
    row = first_data_row
    current_month = _first_of_month(Current_date)

    for site, m0_real in interventions:
        # Normalize date
        m0_real = m0_real if isinstance(m0_real, date) else date.fromisoformat(str(m0_real))
        m0_first = _first_of_month(m0_real)

        ws.write(row, c_site, site)
        # Platform, Tier, Date
        tp = tier_platform_map.get(site, (None, None))
        ws.write(row, c_platform, '' if tp[1] is None else tp[1])
        ws.write(row, c_tier, '' if tp[0] is None else tp[0])
        ws.write_datetime(row, c_date, m0_real, date_fmt)

        # Write month window values (M-3..M+6), blank unreached future months, highlight M0
        # Collect for averages (current and LY)
        m_vals = {}
        for idx, off in enumerate(month_offsets):
            mm = m0_first + relativedelta(months=off)
            col = c_mstart + idx
            if mm > current_month:
                ws.write_blank(row, col, None, future_fmt)
                continue
            key = (site, mm.strftime('%Y-%m-01'))
            val = sales_map.get(key, 0)
            m_vals[off] = val
            # Unit-aware display: either raw bottles or per-day
            days_in_m = calendar.monthrange(mm.year, mm.month)[1]
            unit_cell = "'SalesTeam Sites'!$C$1"
            formula_val = f"IF({unit_cell}=\"Bot/day\",{val}/{days_in_m},{val})"
            cell_fmt = m0_fmt if off == 0 else num_fmt
            ws.write_formula(row, col, formula_val, cell_fmt)

        # Helper to sum/avg a list of month offsets, clamped to Current_date for current year
        def cur_sum_and_count(offsets):
            s = 0
            n = 0
            for off in offsets:
                mm = m0_first + relativedelta(months=off)
                if mm > current_month:
                    continue
                s += m_vals.get(off, 0)
                n += 1
            return s, n

        def ly_sum_and_count(offsets):
            s = 0
            n = 0
            for off in offsets:
                mm = (m0_first + relativedelta(months=off, years=-1)).strftime('%Y-%m-01')
                s += sales_map.get((site, mm), 0)
                n += 1
            return s, n
        # 3-month (M+1..M+3): current period average from visible month cells (unit-aware)
        offs3 = [1, 2, 3]
        cells3 = [xl_rowcol_to_cell(row, c_mstart + month_offsets.index(o)) for o in offs3]
        avg3_formula = f"IFERROR(AVERAGE({','.join(cells3)}),\"\")"
        ws.write_formula(row, c_avg3, avg3_formula, bold_num_fmt)
        # LY avg (3m): compute both per-month and per-day in Python, select by unit
        s3_ly, n3_ly = ly_sum_and_count(offs3)
        # per-day average across months
        s3_ly_pd_sum = 0
        for o in offs3:
            mm_ly = m0_first + relativedelta(months=o, years=-1)
            key_ly = (site, mm_ly.strftime('%Y-%m-01'))
            val_ly = sales_map.get(key_ly, 0)
            days_ly = calendar.monthrange(mm_ly.year, mm_ly.month)[1]
            s3_ly_pd_sum += (val_ly / days_ly) if days_ly else 0
        avg3_ly = (s3_ly / n3_ly) if n3_ly > 0 else 0
        avg3_ly_pd = (s3_ly_pd_sum / n3_ly) if n3_ly > 0 else 0
        unit_cell = "'SalesTeam Sites'!$C$1"
        ws.write_formula(row, c_avg3_ly, f"IF({unit_cell}=\"Bot/day\",{avg3_ly_pd},{avg3_ly})", bold_num_fmt)
        # Prev 3-month (M-1..M-3) and comparison
        offs3_prev = [-1, -2, -3]
        s3_prev = 0
        s3_prev_pd_sum = 0
        n3_prev = 0
        for o in offs3_prev:
            mm_prev = m0_first + relativedelta(months=o)
            if mm_prev > current_month:
                continue
            val_prev = m_vals.get(o, 0)
            s3_prev += val_prev
            days_prev = calendar.monthrange(mm_prev.year, mm_prev.month)[1]
            s3_prev_pd_sum += (val_prev / days_prev) if days_prev else 0
            n3_prev += 1
        avg3_prev = (s3_prev / n3_prev) if n3_prev > 0 else 0
        avg3_prev_pd = (s3_prev_pd_sum / n3_prev) if n3_prev > 0 else 0
        ws.write_formula(row, c_prev3, f"IF({unit_cell}=\"Bot/day\",{avg3_prev_pd},{avg3_prev})", bold_num_fmt)
        cur_cell3 = xl_rowcol_to_cell(row, c_avg3)
        ly_cell3 = xl_rowcol_to_cell(row, c_avg3_ly)
        ws.write_formula(row, c_yoy3, f"IF({ly_cell3}>0,{cur_cell3}/{ly_cell3}-1,\"\")", pct_fmt)
        prev3_cell = xl_rowcol_to_cell(row, c_prev3)
        ws.write_formula(row, c_vs_prev3, f"IF({prev3_cell}>0,{cur_cell3}/{prev3_cell}-1,\"\")", pct_fmt)

        # 6-month (M+1..M+6)
        offs6 = [1, 2, 3, 4, 5, 6]
        cells6 = [xl_rowcol_to_cell(row, c_mstart + month_offsets.index(o)) for o in offs6]
        avg6_formula = f"IFERROR(AVERAGE({','.join(cells6)}),\"\")"
        ws.write_formula(row, c_avg6, avg6_formula, bold_num_fmt)
        # LY 6m
        s6_ly, n6_ly = ly_sum_and_count(offs6)
        s6_ly_pd_sum = 0
        for o in offs6:
            mm_ly = m0_first + relativedelta(months=o, years=-1)
            key_ly = (site, mm_ly.strftime('%Y-%m-01'))
            val_ly = sales_map.get(key_ly, 0)
            days_ly = calendar.monthrange(mm_ly.year, mm_ly.month)[1]
            s6_ly_pd_sum += (val_ly / days_ly) if days_ly else 0
        avg6_ly = (s6_ly / n6_ly) if n6_ly > 0 else 0
        avg6_ly_pd = (s6_ly_pd_sum / n6_ly) if n6_ly > 0 else 0
        ws.write_formula(row, c_avg6_ly, f"IF({unit_cell}=\"Bot/day\",{avg6_ly_pd},{avg6_ly})", bold_num_fmt)
        # Prev 6-month (M-1..M-6) and comparison
        offs6_prev = [-1, -2, -3, -4, -5, -6]
        s6_prev = 0
        s6_prev_pd_sum = 0
        n6_prev = 0
        for o in offs6_prev:
            mm_prev = m0_first + relativedelta(months=o)
            if mm_prev > current_month:
                continue
            val_prev = m_vals.get(o, 0)
            s6_prev += val_prev
            days_prev = calendar.monthrange(mm_prev.year, mm_prev.month)[1]
            s6_prev_pd_sum += (val_prev / days_prev) if days_prev else 0
            n6_prev += 1
        avg6_prev = (s6_prev / n6_prev) if n6_prev > 0 else 0
        avg6_prev_pd = (s6_prev_pd_sum / n6_prev) if n6_prev > 0 else 0
        ws.write_formula(row, c_prev6, f"IF({unit_cell}=\"Bot/day\",{avg6_prev_pd},{avg6_prev})", bold_num_fmt)
        cur_cell6 = xl_rowcol_to_cell(row, c_avg6)
        ly_cell6 = xl_rowcol_to_cell(row, c_avg6_ly)
        ws.write_formula(row, c_yoy6, f"IF({ly_cell6}>0,{cur_cell6}/{ly_cell6}-1,\"\")", pct_fmt)
        prev6_cell = xl_rowcol_to_cell(row, c_prev6)
        ws.write_formula(row, c_vs_prev6, f"IF({prev6_cell}>0,{cur_cell6}/{prev6_cell}-1,\"\")", pct_fmt)

        row += 1

    last_data_row = row - 1

    # 5) Top AVG row with SUBTOTALs; YoY uses SUBTOTAL average of YoY values
    # Add a label in the Site column for validation source (includes 'Total Avg')
    ws.write(0, c_site, 'Total Avg', head_site_fmt)
    ws.write(0, c_mstart-1, 'AVG', head_right_fmt)
    # Non-YoY columns (include hidden prev averages too)
    for c in list(range(c_mstart + 1, c_after)) + [c_avg3, c_avg3_ly, c_prev3, c_avg6, c_avg6_ly, c_prev6]:
        start = xl_rowcol_to_cell(first_data_row, c)
        end = xl_rowcol_to_cell(last_data_row, c)
        ws.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

    # YoY (3m) - compute as (avg current 3m)/(avg LY 3m) - 1 for Total row
    cur3_start = xl_rowcol_to_cell(first_data_row, c_avg3)
    cur3_end = xl_rowcol_to_cell(last_data_row, c_avg3)
    ly3_start = xl_rowcol_to_cell(first_data_row, c_avg3_ly)
    ly3_end = xl_rowcol_to_cell(last_data_row, c_avg3_ly)
    ws.write_formula(0, c_yoy3, f"IF(SUBTOTAL(1,{ly3_start}:{ly3_end})>0,SUBTOTAL(1,{cur3_start}:{cur3_end})/SUBTOTAL(1,{ly3_start}:{ly3_end})-1,\"\")", bold_pct_fmt)

    # YoY (6m) - compute as (avg current 6m)/(avg LY 6m) - 1 for Total row
    cur6_start = xl_rowcol_to_cell(first_data_row, c_avg6)
    cur6_end = xl_rowcol_to_cell(last_data_row, c_avg6)
    ly6_start = xl_rowcol_to_cell(first_data_row, c_avg6_ly)
    ly6_end = xl_rowcol_to_cell(last_data_row, c_avg6_ly)
    ws.write_formula(0, c_yoy6, f"IF(SUBTOTAL(1,{ly6_start}:{ly6_end})>0,SUBTOTAL(1,{cur6_start}:{cur6_end})/SUBTOTAL(1,{ly6_start}:{ly6_end})-1,\"\")", bold_pct_fmt)

    # Vs Prev totals: compute as (avg current avg)/(avg prev avg) - 1 for Total row
    cur3_sum_start = xl_rowcol_to_cell(first_data_row, c_avg3)
    cur3_sum_end = xl_rowcol_to_cell(last_data_row, c_avg3)
    prev3_sum_start = xl_rowcol_to_cell(first_data_row, c_prev3)
    prev3_sum_end = xl_rowcol_to_cell(last_data_row, c_prev3)
    ws.write_formula(0, c_vs_prev3, f"IF(SUBTOTAL(1,{prev3_sum_start}:{prev3_sum_end})>0,SUBTOTAL(1,{cur3_sum_start}:{cur3_sum_end})/SUBTOTAL(1,{prev3_sum_start}:{prev3_sum_end})-1,\"\")", bold_pct_fmt)

    cur6_sum_start = xl_rowcol_to_cell(first_data_row, c_avg6)
    cur6_sum_end = xl_rowcol_to_cell(last_data_row, c_avg6)
    prev6_sum_start = xl_rowcol_to_cell(first_data_row, c_prev6)
    prev6_sum_end = xl_rowcol_to_cell(last_data_row, c_prev6)
    ws.write_formula(0, c_vs_prev6, f"IF(SUBTOTAL(1,{prev6_sum_start}:{prev6_sum_end})>0,SUBTOTAL(1,{cur6_sum_start}:{cur6_sum_end})/SUBTOTAL(1,{prev6_sum_start}:{prev6_sum_end})-1,\"\")", bold_pct_fmt)

    # 5b) Raw Data sheet: per-site network averages aligned to intervention M0 (M-6..M+6)
    ws_raw = workbook.add_worksheet('Raw Data')
    ws_raw.set_zoom(90)

    # Headers
    raw_headers = ['Site'] + [label_for_offset(k) for k in month_offsets]
    for c, h in enumerate(raw_headers): 
        if c == 0:
            ws_raw.write(1, c, h, head_site_fmt)
            ws_raw.set_column(c, c, max(16, len(h) + 2))
        else:
            ws_raw.write(1, c, h, head_month_fmt)
            ws_raw.set_column(c, c, 9)

    # Data rows
    first_data_row_raw = 2
    row_raw = first_data_row_raw
    for site, m0_real in interventions: 
        m0_real = m0_real if isinstance(m0_real, date) else date.fromisoformat(str(m0_real))
        m0_first = _first_of_month(m0_real)
        ws_raw.write(row_raw, 0, site)
        for idx, off in enumerate(month_offsets):
            mm = m0_first + relativedelta(months=off)
            col = 1 + idx
            if mm > current_month:
                ws_raw.write_blank(row_raw, col, None, future_fmt)
                continue
            keym = mm.strftime('%Y-%m-01')
            navg = month_avg.get(keym, 0)
            # Unit-aware network avg display
            days_in_m = calendar.monthrange(mm.year, mm.month)[1]
            unit_cell = "'SalesTeam Sites'!$C$1"
            formula_navg = f"IF({unit_cell}=\"Bot/day\",{navg}/{days_in_m},{navg})"
            ws_raw.write_formula(row_raw, col, formula_navg, num_fmt)
        row_raw += 1

    last_data_row_raw = row_raw - 1

    # Top AVG row in Raw Data (averages across sites for each offset)
    ws_raw.write(0, 0, 'Total Avg', head_site_fmt)
    for j in range(len(month_offsets)):
        c = 1 + j
        start = xl_rowcol_to_cell(first_data_row_raw, c)
        end = xl_rowcol_to_cell(last_data_row_raw, c)
        ws_raw.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

    # 5c) Sheet 2: Sales Evolution with dropdown and dynamic chart (extended with network avg)
    ws2 = workbook.add_worksheet('Sales Evolution')
    ws2.set_zoom(90)

    # UI: selection label and dropdown (source from 'SalesTeam Sites' column A incl. 'Total Avg')
    # Row 1: dropdown for recent interventions + explanation
    ws2.write(0, 0, 'Site interventions:', unit_label_fmt)
    ws2.write(0, 1, 'Total Avg', unit_value_fmt)  # default
    first_site_cell = xl_rowcol_to_cell(0, c_site, True, True)  # $A$1
    last_site_cell = xl_rowcol_to_cell(last_data_row, c_site, True, True)
    dv_source = f"='SalesTeam Sites'!{first_site_cell}:{last_site_cell}"
    ws2.data_validation(0, 1, 0, 1, {'validate': 'list', 'source': dv_source})

    # Second dropdown dedicated to old interventions (based on 'Old Interventions Sites')
    # Row 23 (index 22): dropdown for old interventions + explanation
    ws2.write(22, 0, 'Old site interventions:', unit_label_fmt)
    ws2.write(22, 1, 'Total Avg', unit_value_fmt)

    # Make column A wider so explanation fits in two rows
    ws2.set_column(0, 0, 40)

    # Explanation for recent interventions block in cell A2 (row 2)
    ws2.write(1, 0, 'Sites with interventions from M-12 to M-1', head_site_fmt)

    # X-axis labels M-6..M+6 in row 3; data in rows 4-6
    cat_row = 2   # row 3
    val_row = 3   # row 4 - selected site actual values
    val_row_net = 4  # row 5 - network average values
    for j, off in enumerate(month_offsets):
        ws2.write(cat_row, 1 + j, label_for_offset(off), head_month_fmt)

    # Build per-column formulas referencing sheet1 data
    first_row_idx = first_data_row  # numeric
    last_row_idx = last_data_row
    # Excel MATCH is 1-based row index within the sheet; we convert to index within our E3:E{last} area by subtracting (first_data_row-1)
    # Row labels matching chart series (blue bg to match chart legend)
    ws2.write(val_row, 0, 'Selected site', head_fmt)
    ws2.write(val_row_net, 0, 'Network avg', head_fmt)

    for j in range(len(month_offsets)):
        col_sheet1 = c_mstart + j
        start_addr = xl_rowcol_to_cell(first_row_idx, col_sheet1)
        end_addr = xl_rowcol_to_cell(last_row_idx, col_sheet1)
        range_addr = f"'SalesTeam Sites'!{start_addr}:{end_addr}"
        # Area for INDEX
        area_addr = range_addr
        # MATCH on site name column A
        match_col = "'SalesTeam Sites'!$A:$A"
        # OFFSET to convert absolute MATCH row to position in the area
        offset_val = first_row_idx
        formula = f"IF($B$1=\"Total Avg\",SUBTOTAL(1,{range_addr}),IFERROR(INDEX({area_addr},MATCH($B$1,{match_col},0)-{offset_val}),\"\"))"
        ws2.write_formula(val_row, 1 + j, formula, num_fmt)

        # Network average values from 'Raw Data'
        raw_start_addr = xl_rowcol_to_cell(first_data_row_raw, 1 + j)
        raw_end_addr = xl_rowcol_to_cell(last_data_row_raw, 1 + j)
        raw_range_addr = f"'Raw Data'!{raw_start_addr}:{raw_end_addr}"
        raw_area_addr = raw_range_addr
        raw_match_col = "'Raw Data'!$A:$A"
        raw_offset_val = first_data_row_raw
        formula_net = f"IF($B$1=\"Total Avg\",SUBTOTAL(1,{raw_range_addr}),IFERROR(INDEX({raw_area_addr},MATCH($B$1,{raw_match_col},0)-{raw_offset_val}),\"\"))"
        ws2.write_formula(val_row_net, 1 + j, formula_net, num_fmt)

    # Create line chart for recent interventions
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({
        'name':       'Selected site',
        'categories': ['Sales Evolution', cat_row, 1, cat_row, 1 + len(month_offsets) - 1],
        'values':     ['Sales Evolution', val_row, 1, val_row, 1 + len(month_offsets) - 1],
    })
    chart.add_series({
        'name':       'Network avg',
        'categories': ['Sales Evolution', cat_row, 1, cat_row, 1 + len(month_offsets) - 1],
        'values':     ['Sales Evolution', val_row_net, 1, val_row_net, 1 + len(month_offsets) - 1],
    })
    chart.set_title({'name': 'Sales Evolution (M-6 to M+6)'})
    chart.set_y_axis({'name': 'Bottles'})
    chart.set_x_axis({'name': 'Month relative to M0'})
    chart.set_legend({'position': 'bottom'})

    # Insert chart for recent interventions: rows 5 to 21 (approx.)
    ws2.insert_chart(5, 1, chart, {'x_scale': 1.4, 'y_scale': 1.2})

    # 5c-bis) Old interventions detailed sheet and evolution chart (M-6..M+18)
    if old_interventions:
        ws_old = workbook.add_worksheet('Old Interventions Sites')
        ws_old.set_zoom(90)

        # Ensure tier/platform map covers old intervention sites
        old_site_ids = tuple(r[0] for r in old_interventions)
        for sid in old_site_ids:
            if sid not in tier_platform_map:
                row_tp = con.execute("SELECT Last_Tier, Platform FROM Sites WHERE Id_Site = %s", (sid,)).fetchone()
                if row_tp:
                    tier_platform_map[sid] = (row_tp[0], row_tp[1])
                else:
                    tier_platform_map[sid] = (None, None)

        old_offsets = list(range(-6, 19))

        old_headers = ['Site', 'Platform', 'Tier', 'Intervention date'] + [label_for_offset(k) for k in old_offsets]

        for c, h in enumerate(old_headers):
            if c < 4:
                ws_old.write(1, c, h, head_site_fmt)
                ws_old.set_column(c, c, max(16, len(h) + 2))
            else:
                ws_old.write(1, c, h, head_month_fmt)
                ws_old.set_column(c, c, 9)

        first_data_row_old = 2
        row_old = first_data_row_old
        current_month = _first_of_month(Current_date)

        for site, m0_real in old_interventions:
            m0_real = m0_real if isinstance(m0_real, date) else date.fromisoformat(str(m0_real))
            m0_first = _first_of_month(m0_real)

            ws_old.write(row_old, 0, site)
            tp = tier_platform_map.get(site, (None, None))
            ws_old.write(row_old, 1, '' if tp[1] is None else tp[1])
            ws_old.write(row_old, 2, '' if tp[0] is None else tp[0])
            ws_old.write_datetime(row_old, 3, m0_real, date_fmt)

            for idx, off in enumerate(old_offsets):
                mm = m0_first + relativedelta(months=off)
                col = 4 + idx
                if mm > current_month:
                    ws_old.write_blank(row_old, col, None, future_fmt)
                    continue
                key = (site, mm.strftime('%Y-%m-01'))
                val = sales_map.get(key, 0)
                days_in_m = calendar.monthrange(mm.year, mm.month)[1]
                unit_cell = "'SalesTeam Sites'!$C$1"
                formula_val = f"IF({unit_cell}=\"Bot/day\",{val}/{days_in_m},{val})"
                cell_fmt = m0_fmt if off == 0 else num_fmt
                ws_old.write_formula(row_old, col, formula_val, cell_fmt)

            row_old += 1

        last_data_row_old = row_old - 1

        # Top AVG row for old interventions
        ws_old.write(0, 0, 'Total Avg', head_site_fmt)
        ws_old.write(0, 3, 'AVG', head_right_fmt)
        for c in range(4, 4 + len(old_offsets)):
            start = xl_rowcol_to_cell(first_data_row_old, c)
            end = xl_rowcol_to_cell(last_data_row_old, c)
            ws_old.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

        # Raw Data sheet for old interventions (network averages aligned to old intervention M0, M-6..M+18)
        ws_old_raw = workbook.add_worksheet('Raw Data Old')
        ws_old_raw.set_zoom(90)

        old_raw_headers = ['Site'] + [label_for_offset(k) for k in old_offsets]
        for c, h in enumerate(old_raw_headers):
            if c == 0:
                ws_old_raw.write(1, c, h, head_site_fmt)
                ws_old_raw.set_column(c, c, max(16, len(h) + 2))
            else:
                ws_old_raw.write(1, c, h, head_month_fmt)
                ws_old_raw.set_column(c, c, 9)

        first_data_row_old_raw = 2
        row_old_raw = first_data_row_old_raw
        for site, m0_real in old_interventions:
            m0_real = m0_real if isinstance(m0_real, date) else date.fromisoformat(str(m0_real))
            m0_first = _first_of_month(m0_real)
            ws_old_raw.write(row_old_raw, 0, site)
            for idx, off in enumerate(old_offsets):
                mm = m0_first + relativedelta(months=off)
                col = 1 + idx
                if mm > current_month:
                    ws_old_raw.write_blank(row_old_raw, col, None, future_fmt)
                    continue
                keym = mm.strftime('%Y-%m-01')
                navg = month_avg.get(keym, 0)
                days_in_m = calendar.monthrange(mm.year, mm.month)[1]
                unit_cell = "'SalesTeam Sites'!$C$1"
                formula_navg = f"IF({unit_cell}=\"Bot/day\",{navg}/{days_in_m},{navg})"
                ws_old_raw.write_formula(row_old_raw, col, formula_navg, num_fmt)
            row_old_raw += 1

        last_data_row_old_raw = row_old_raw - 1

        # Top AVG row in Raw Data Old
        ws_old_raw.write(0, 0, 'Total Avg', head_site_fmt)
        for j in range(len(old_offsets)):
            c = 1 + j
            start = xl_rowcol_to_cell(first_data_row_old_raw, c)
            end = xl_rowcol_to_cell(last_data_row_old_raw, c)
            ws_old_raw.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

        # Old interventions block on the same 'Sales Evolution' sheet, under the main chart
        # Reuse 'ws2' created earlier

        # Data validation for old interventions dropdown (based on 'Old Interventions Sites')
        first_old_site_cell = xl_rowcol_to_cell(0, 0, True, True)  # 'Old Interventions Sites'!$A$1
        last_old_site_cell = xl_rowcol_to_cell(last_data_row_old, 0, True, True)
        dv_source_old = f"='Old Interventions Sites'!{first_old_site_cell}:{last_old_site_cell}"
        ws2.data_validation(22, 1, 22, 1, {'validate': 'list', 'source': dv_source_old})

        # Explanation text for old interventions in cell A24 (row 24)
        ws2.write(23, 0, 'Sites with interventions from M-24 to M-12', head_site_fmt)

        # X-axis labels in row 25; data in rows 26-28
        old_cat_row = 24   # row 25
        old_val_row = 25   # row 26
        old_net_row = 26   # row 27

        for j, off in enumerate(old_offsets):
            ws2.write(old_cat_row, 1 + j, label_for_offset(off), head_month_fmt)

        first_row_idx_old = first_data_row_old
        last_row_idx_old = last_data_row_old
        first_row_idx_old_raw = first_data_row_old_raw
        last_row_idx_old_raw = last_data_row_old_raw

        # Row labels matching chart series (blue bg)
        ws2.write(old_val_row, 0, 'Selected site', head_fmt)
        ws2.write(old_net_row, 0, 'Network avg', head_fmt)

        for j in range(len(old_offsets)):
            # Selected site values from Old Interventions Sites
            col_sheet_old = 4 + j
            start_addr = xl_rowcol_to_cell(first_row_idx_old, col_sheet_old)
            end_addr = xl_rowcol_to_cell(last_row_idx_old, col_sheet_old)
            range_addr = f"'Old Interventions Sites'!{start_addr}:{end_addr}"
            area_addr = range_addr
            match_col = "'Old Interventions Sites'!$A:$A"
            offset_val = first_row_idx_old
            formula = f"IF($B$23=\"Total Avg\",SUBTOTAL(1,{range_addr}),IFERROR(INDEX({area_addr},MATCH($B$23,{match_col},0)-{offset_val}),\"\"))"
            ws2.write_formula(old_val_row, 1 + j, formula, num_fmt)

            # Network average values from Raw Data Old
            raw_start_addr = xl_rowcol_to_cell(first_row_idx_old_raw, 1 + j)
            raw_end_addr = xl_rowcol_to_cell(last_row_idx_old_raw, 1 + j)
            raw_range_addr = f"'Raw Data Old'!{raw_start_addr}:{raw_end_addr}"
            raw_area_addr = raw_range_addr
            raw_match_col = "'Raw Data Old'!$A:$A"
            raw_offset_val = first_row_idx_old_raw
            formula_net = f"IF($B$23=\"Total Avg\",SUBTOTAL(1,{raw_range_addr}),IFERROR(INDEX({raw_area_addr},MATCH($B$23,{raw_match_col},0)-{raw_offset_val}),\"\"))"
            ws2.write_formula(old_net_row, 1 + j, formula_net, num_fmt)

        chart_old = workbook.add_chart({'type': 'line'})
        chart_old.add_series({
            'name':       'Selected site',
            'categories': ['Sales Evolution', old_cat_row, 1, old_cat_row, 1 + len(old_offsets) - 1],
            'values':     ['Sales Evolution', old_val_row, 1, old_val_row, 1 + len(old_offsets) - 1],
        })
        chart_old.add_series({
            'name':       'Network avg',
            'categories': ['Sales Evolution', old_cat_row, 1, old_cat_row, 1 + len(old_offsets) - 1],
            'values':     ['Sales Evolution', old_net_row, 1, old_net_row, 1 + len(old_offsets) - 1],
        })
        chart_old.set_title({'name': 'Old interventions (M-6 to M+18)'})
        chart_old.set_y_axis({'name': 'Bottles'})
        chart_old.set_x_axis({'name': 'Month relative to M0'})
        chart_old.set_legend({'position': 'bottom'})

        # Insert old interventions chart: rows 27 to 43 (approx.)
        ws2.insert_chart(27, 1, chart_old, {'x_scale': 1.4, 'y_scale': 1.2})

        # Hide helper sheets for old interventions
        ws_old.hide()
        ws_old_raw.hide()

    # Hide Raw Data sheet by default
    ws_raw.hide()

    # Columns sizing
    ws2.set_column(1, 1, 12)

    # 5d) Openings sheet: similar layout but M0..M+12 window
    ws_open = workbook.add_worksheet('Openings Sites')
    ws_open.set_zoom(90)

    if openings:
        # Tier / Platform for openings sites (reuse map, extend if needed)
        opening_site_ids = tuple(r[0] for r in openings)
        for sid in opening_site_ids:
            if sid not in tier_platform_map:
                row_tp = con.execute("SELECT Last_Tier, Platform FROM Sites WHERE Id_Site = %s", (sid,)).fetchone()
                if row_tp:
                    tier_platform_map[sid] = (row_tp[0], row_tp[1])
                else:
                    tier_platform_map[sid] = (None, None)

        # Offsets for openings: M0..M+11
        open_offsets = list(range(0, 12))

        open_headers = ['Site', 'Platform', 'Tier', 'Opening date'] + [label_for_offset(k) for k in open_offsets]

        # Write headers (row 1), keep row 0 for top AVG row
        for c, h in enumerate(open_headers):
            if c < 4:
                ws_open.write(1, c, h, head_site_fmt)
                ws_open.set_column(c, c, max(16, len(h) + 2))
            else:
                ws_open.write(1, c, h, head_month_fmt)
                ws_open.set_column(c, c, 9)

        first_data_row_open = 2
        row_open = first_data_row_open
        current_month = _first_of_month(Current_date)

        for site, m0_real in openings:
            m0_real = m0_real if isinstance(m0_real, date) else date.fromisoformat(str(m0_real))
            m0_first = _first_of_month(m0_real)

            ws_open.write(row_open, 0, site)
            tp = tier_platform_map.get(site, (None, None))
            ws_open.write(row_open, 1, '' if tp[1] is None else tp[1])
            ws_open.write(row_open, 2, '' if tp[0] is None else tp[0])
            ws_open.write_datetime(row_open, 3, m0_real, date_fmt)

            for idx, off in enumerate(open_offsets):
                mm = m0_first + relativedelta(months=off)
                col = 4 + idx
                if mm > current_month:
                    ws_open.write_blank(row_open, col, None, future_fmt)
                    continue
                key = (site, mm.strftime('%Y-%m-01'))
                val = sales_map.get(key, 0)
                days_in_m = calendar.monthrange(mm.year, mm.month)[1]
                unit_cell = "'SalesTeam Sites'!$C$1"
                formula_val = f"IF({unit_cell}=\"Bot/day\",{val}/{days_in_m},{val})"
                cell_fmt = m0_fmt if off == 0 else num_fmt
                ws_open.write_formula(row_open, col, formula_val, cell_fmt)

            row_open += 1

        last_data_row_open = row_open - 1

        # Units dropdown on Openings Sites (same as SalesTeam Sites)
        ws_open.write(0, 1, 'Units:', unit_label_fmt)
        ws_open.write(0, 2, 'Bot', unit_value_fmt)
        ws_open.data_validation(0, 2, 0, 2, {'validate': 'list', 'source': ['Bot', 'Bot/day']})
        ws_open.set_column(1, 2, 14)

        # Top AVG row for openings
        ws_open.write(0, 0, 'Total Avg', head_site_fmt)
        ws_open.write(0, 3, 'AVG', head_right_fmt)
        for c in range(4, 4 + len(open_offsets)):
            start = xl_rowcol_to_cell(first_data_row_open, c)
            end = xl_rowcol_to_cell(last_data_row_open, c)
            ws_open.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

        # Raw Data sheet for openings (network averages aligned to opening M0, M0..M+12)
        ws_open_raw = workbook.add_worksheet('Raw Data Opening')
        ws_open_raw.set_zoom(90)

        open_raw_headers = ['Site'] + [label_for_offset(k) for k in open_offsets]
        for c, h in enumerate(open_raw_headers):
            if c == 0:
                ws_open_raw.write(1, c, h, head_site_fmt)
                ws_open_raw.set_column(c, c, max(16, len(h) + 2))
            else:
                ws_open_raw.write(1, c, h, head_month_fmt)
                ws_open_raw.set_column(c, c, 9)

        first_data_row_open_raw = 2
        row_open_raw = first_data_row_open_raw
        for site, m0_real in openings:
            m0_real = m0_real if isinstance(m0_real, date) else date.fromisoformat(str(m0_real))
            m0_first = _first_of_month(m0_real)
            ws_open_raw.write(row_open_raw, 0, site)
            for idx, off in enumerate(open_offsets):
                mm = m0_first + relativedelta(months=off)
                col = 1 + idx
                if mm > current_month:
                    ws_open_raw.write_blank(row_open_raw, col, None, future_fmt)
                    continue
                keym = mm.strftime('%Y-%m-01')
                navg = month_avg.get(keym, 0)
                days_in_m = calendar.monthrange(mm.year, mm.month)[1]
                unit_cell = "'SalesTeam Sites'!$C$1"
                formula_navg = f"IF({unit_cell}=\"Bot/day\",{navg}/{days_in_m},{navg})"
                ws_open_raw.write_formula(row_open_raw, col, formula_navg, num_fmt)
            row_open_raw += 1

        last_data_row_open_raw = row_open_raw - 1

        # Top AVG row in Raw Data Opening
        ws_open_raw.write(0, 0, 'Total Avg', head_site_fmt)
        for j in range(len(open_offsets)):
            c = 1 + j
            start = xl_rowcol_to_cell(first_data_row_open_raw, c)
            end = xl_rowcol_to_cell(last_data_row_open_raw, c)
            ws_open_raw.write_formula(0, c, f"SUBTOTAL(1,{start}:{end})", bold_num_fmt)

        # Simple evolution chart for openings (M0..M+12)
        ws_open2 = workbook.add_worksheet('Openings Evolution')
        ws_open2.set_zoom(90)

        ws_open2.write(1, 0, 'Site:', unit_label_fmt)
        ws_open2.write(1, 1, 'Total Avg', unit_value_fmt)
        first_open_site_cell = xl_rowcol_to_cell(0, 0, True, True)
        last_open_site_cell = xl_rowcol_to_cell(last_data_row_open, 0, True, True)
        dv_source_open = f"='Openings Sites'!{first_open_site_cell}:{last_open_site_cell}"
        ws_open2.data_validation(1, 1, 1, 1, {'validate': 'list', 'source': dv_source_open})

        cat_row_open = 4
        val_row_open = 5
        val_row_open_net = 6
        for j, off in enumerate(open_offsets):
            ws_open2.write(cat_row_open, 1 + j, label_for_offset(off), head_month_fmt)

        first_row_idx_open = first_data_row_open
        last_row_idx_open = last_data_row_open
        first_row_idx_open_raw = first_data_row_open_raw
        last_row_idx_open_raw = last_data_row_open_raw

        for j in range(len(open_offsets)):
            col_sheet_open = 4 + j
            start_addr = xl_rowcol_to_cell(first_row_idx_open, col_sheet_open)
            end_addr = xl_rowcol_to_cell(last_row_idx_open, col_sheet_open)
            range_addr = f"'Openings Sites'!{start_addr}:{end_addr}"
            area_addr = range_addr
            match_col = "'Openings Sites'!$A:$A"
            offset_val = first_row_idx_open
            formula = f"IF($B$2=\"Total Avg\",SUBTOTAL(1,{range_addr}),IFERROR(INDEX({area_addr},MATCH($B$2,{match_col},0)-{offset_val}),\"\"))"
            ws_open2.write_formula(val_row_open, 1 + j, formula, num_fmt)

            # Network average values from Raw Data Opening
            raw_start_addr = xl_rowcol_to_cell(first_row_idx_open_raw, 1 + j)
            raw_end_addr = xl_rowcol_to_cell(last_row_idx_open_raw, 1 + j)
            raw_range_addr = f"'Raw Data Opening'!{raw_start_addr}:{raw_end_addr}"
            raw_area_addr = raw_range_addr
            raw_match_col = "'Raw Data Opening'!$A:$A"
            raw_offset_val = first_row_idx_open_raw
            formula_net = f"IF($B$2=\"Total Avg\",SUBTOTAL(1,{raw_range_addr}),IFERROR(INDEX({raw_area_addr},MATCH($B$2,{raw_match_col},0)-{raw_offset_val}),\"\"))"
            ws_open2.write_formula(val_row_open_net, 1 + j, formula_net, num_fmt)

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

        ws_open2.set_column(0, 0, 10)
        ws_open2.set_column(1, 1, 12)

        # Hide helper sheet for openings raw data
        ws_open_raw.hide()

        # 5e) Salesman vs Site lending bottles matrix for interventions
        # Only create this tab for documents dated from May 2025 onwards, and
        # for those documents, only use data from 2025-05-01 and later.
        cutoff_date = date(2025, 5, 1)
        if Current_date >= cutoff_date:
            # Restrict data for this tab to interventions >= cutoff_date
            sales_start = cutoff_date
            sales_end = date(Current_date.year + 1, 1, 1)

            # Get all sites that had an intervention in the filtered window
            sites_this_year = con.execute(
                """
                SELECT DISTINCT site
                FROM sale_team
                WHERE sale_type = "sale_intervention"
                  AND sale_date >= %s AND sale_date < %s
                  AND site IS NOT NULL AND site != ''
                ORDER BY site
                """,
                (sales_start, sales_end)
            ).fetchall()

            # Get all distinct sales officers from sale_officer1 over the same period
            officers_this_year = con.execute(
                """
                SELECT DISTINCT sale_officer1
                FROM sale_team
                WHERE sale_type = "sale_intervention"
                  AND sale_date >= %s AND sale_date < %s
                  AND sale_officer1 IS NOT NULL AND sale_officer1 != ''
                ORDER BY sale_officer1
                """,
                (sales_start, sales_end)
            ).fetchall()

            if sites_this_year and officers_this_year:
                ws_salesman = workbook.add_worksheet('Salesman Lending')
                ws_salesman.set_zoom(90)

                # Fetch intervention dates per site for the Salesman Lending tab
                intervention_dates_rows = con.execute(
                    """
                    SELECT site, MIN(sale_date) AS first_date
                    FROM sale_team
                    WHERE sale_type = "sale_intervention"
                      AND sale_date >= %s AND sale_date < %s
                      AND site IS NOT NULL AND site != ''
                    GROUP BY site
                    ORDER BY site
                    """,
                    (sales_start, sales_end)
                ).fetchall()
                intervention_date_map = {}
                for r in intervention_dates_rows:
                    d = r[1] if isinstance(r[1], date) else date.fromisoformat(str(r[1]))
                    intervention_date_map[r[0]] = d

                # Header row for the main table: Site, Intervention date, then one column per officer, then Total
                header_row = 2  # row 3
                ws_salesman.write(header_row, 0, 'Site', head_site_fmt)
                ws_salesman.write(header_row, 1, 'Intervention date', head_site_fmt)
                ws_salesman.set_column(1, 1, 18)
                officer_col_start = 2  # officers start at column 2
                for idx, row_off in enumerate(officers_this_year):
                    officer = row_off[0]
                    col = officer_col_start + idx
                    ws_salesman.write(header_row, col, officer, head_site_fmt)
                    ws_salesman.set_column(col, col, max(14, len(str(officer)) + 2))
                # Total column after all officers
                total_col = officer_col_start + len(officers_this_year)
                ws_salesman.write(header_row, total_col, 'Total', head_fmt)
                ws_salesman.set_column(total_col, total_col, 14)

                # For performance, precompute sums in one query
                lending_rows = con.execute(
                    """
                    SELECT site, sale_officer1, SUM(IFNULL(lending_bottle,0)) AS lend_sum
                    FROM sale_team
                    WHERE sale_type = "sale_intervention"
                      AND sale_date >= %s AND sale_date < %s
                      AND site IS NOT NULL AND site != ''
                      AND sale_officer1 IS NOT NULL AND sale_officer1 != ''
                    GROUP BY site, sale_officer1
                    """,
                    (sales_start, sales_end)
                ).fetchall()

                lending_map = {(r[0], r[1]): (r[2] or 0) for r in lending_rows}

                # Write one row per site starting just under the header (row 4, index 3)
                first_data_row_salesman = header_row + 1
                for offset, row_site in enumerate(sites_this_year):
                    row_idx = first_data_row_salesman + offset
                    site_id = row_site[0]
                    ws_salesman.write(row_idx, 0, site_id, head_site_fmt)
                    ws_salesman.set_column(0, 0, max(16, len(str(site_id)) + 2))
                    # Intervention date
                    idate = intervention_date_map.get(site_id)
                    if idate:
                        ws_salesman.write_datetime(row_idx, 1, idate, date_fmt)
                    for col_idx, row_off in enumerate(officers_this_year):
                        officer = row_off[0]
                        col = officer_col_start + col_idx
                        val = lending_map.get((site_id, officer), 0)
                        if val:
                            ws_salesman.write_number(row_idx, col, val, num_fmt)
                    # Total per site (SUM across all officers for this row)
                    first_officer_cell = xl_rowcol_to_cell(row_idx, officer_col_start)
                    last_officer_cell = xl_rowcol_to_cell(row_idx, officer_col_start + len(officers_this_year) - 1)
                    ws_salesman.write_formula(row_idx, total_col, f"SUM({first_officer_cell}:{last_officer_cell})", bold_num_fmt)

                last_data_row_salesman = first_data_row_salesman + len(sites_this_year) - 1

                # Two summary rows above the table: Sum (SUBTOTAL 9) and Average (SUBTOTAL 1)
                sum_row = 0   # row 1
                avg_row = 1   # row 2
                ws_salesman.write(sum_row, 0, 'Sum', head_site_fmt)
                ws_salesman.write(avg_row, 0, 'Average', head_site_fmt)

                for col_idx in range(officer_col_start, officer_col_start + len(officers_this_year)):
                    start_addr = xl_rowcol_to_cell(first_data_row_salesman, col_idx)
                    end_addr = xl_rowcol_to_cell(last_data_row_salesman, col_idx)
                    ws_salesman.write_formula(sum_row, col_idx, f"SUBTOTAL(9,{start_addr}:{end_addr})", bold_num_fmt)
                    ws_salesman.write_formula(avg_row, col_idx, f"SUBTOTAL(1,{start_addr}:{end_addr})", bold_num_fmt)
                # Total column summary (Sum and Average)
                start_total = xl_rowcol_to_cell(first_data_row_salesman, total_col)
                end_total = xl_rowcol_to_cell(last_data_row_salesman, total_col)
                ws_salesman.write_formula(sum_row, total_col, f"SUBTOTAL(9,{start_total}:{end_total})", bold_num_fmt)
                ws_salesman.write_formula(avg_row, total_col, f"SUBTOTAL(1,{start_total}:{end_total})", bold_num_fmt)

                # Apply autofilter on the header row across all columns including Total
                ws_salesman.autofilter(header_row, 0, last_data_row_salesman, total_col)

    # 6) Hide/group LY and Prev avg columns
    ws.set_column(c_avg3_ly, c_avg3_ly, None, None, {'level': 1, 'hidden': True})
    ws.set_column(c_avg6_ly, c_avg6_ly, None, None, {'level': 1, 'hidden': True})
    ws.set_column(c_prev3, c_prev3, None, None, {'level': 1, 'hidden': True})
    ws.set_column(c_prev6, c_prev6, None, None, {'level': 1, 'hidden': True})

    # 7) Autofilter and freeze panes
    ws.autofilter(1, 0, last_data_row, c_vs_prev6)
    ws.freeze_panes(first_data_row, 4)  # freeze header + first 4 columns

    # 8) Conditional formatting: arrows in YoY columns based on +/-10%
    up_arrow_fmt = workbook.add_format({'font_color': '#00B050', 'bold': True, 'num_format': '+0.0% "↑"'})
    down_arrow_fmt = workbook.add_format({'font_color': '#C00000', 'bold': True, 'num_format': '-0.0% "↓"'})
    for col in (c_yoy3, c_yoy6, c_vs_prev3, c_vs_prev6):
        ws.conditional_format(first_data_row, col, last_data_row, col, {
            'type': 'cell', 'criteria': '>=', 'value': 0.1, 'format': up_arrow_fmt
        })
        ws.conditional_format(first_data_row, col, last_data_row, col, {
            'type': 'cell', 'criteria': '<=', 'value': -0.1, 'format': down_arrow_fmt
        })


def LaunchExcelSalesTeamPerformance(Current_date: date):
    # Write to temp folder like other reports
    Month = Current_date.month
    Month = ('0' + str(Month)) if Month < 10 else str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir() + '/SalesTeam Performance ' + Year + '-' + Month + '.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    SalesTeamPerformance(workbook, Current_date)
    workbook.close()
    return filepath


if __name__ == '__main__':
    # Simple manual run example
    LaunchExcelSalesTeamPerformance(date(2025, 10, 1))
