import calendar
import tempfile
from datetime import date
import db
import xlsxwriter
from monthlyreport.Functionutils import CategoryExpenses, exchange_rate_year
from dateutil.relativedelta import relativedelta
from xlsxwriter.utility import xl_rowcol_to_cell, xl_col_to_name


def _first_of_month(d: date) -> date:
    return date(d.year, d.month, 1)


def _iter_months(start_month: date, end_month: date):
    cur = _first_of_month(start_month)
    end = _first_of_month(end_month)
    while cur <= end:
        yield cur
        cur = cur + relativedelta(months=+1)


def _month_diff(a: date, b: date) -> int:
    """Month difference between first-of-month dates a and b (b - a) in whole months."""
    a = _first_of_month(a)
    b = _first_of_month(b)
    return (b.year - a.year) * 12 + (b.month - a.month)


def _label_for_offset(k: int) -> str:
    if k == 0:
        return 'M0'
    return f"M{k:+d}".replace('+', '+')


def _safe_div(numer: float | int | None, denom: float | int | None) -> float | None:
    if numer is None or denom is None:
        return None
    try:
        if denom == 0:
            return None
        return float(numer) / float(denom)
    except Exception:
        return None


def _normalize_vehicle_events(vehicle_events: list[tuple[str, date]]) -> dict[str, date]:
    """Normalize and deduplicate by site (keep earliest vehicle date if duplicates)."""
    vehicle_date_by_site: dict[str, date] = {}
    for site, d in vehicle_events:
        if not site:
            continue
        d = d if isinstance(d, date) else date.fromisoformat(str(d))
        if site not in vehicle_date_by_site or d < vehicle_date_by_site[site]:
            vehicle_date_by_site[site] = d
    return vehicle_date_by_site


def _in_clause(values: list[str]) -> tuple[str, list[str]]:
    values = list(values)
    if not values:
        return "(NULL)", []
    return "(" + ",".join(["%s"] * len(values)) + ")", values


def VehicleDeliveryImpact(
    workbook: xlsxwriter.Workbook,
    Current_date: date,
    *,
    vehicle_events: list[tuple[str, date]],
    vehicle_waves: list[list[tuple[str, date]]] | None = None,
):
    con = db.pool.connect()

    current_month = _first_of_month(Current_date)

    vehicle_date_by_site = _normalize_vehicle_events(vehicle_events)
    wave_labels = [f'Wave {i+1}' for i in range(len(vehicle_waves or []))]
    wave_maps = [_normalize_vehicle_events(w) for w in (vehicle_waves or [])]
    wave_sites_list = [sorted(m.keys()) for m in wave_maps]

    sites = sorted(vehicle_date_by_site.keys())
    if not sites:
        ws = workbook.add_worksheet('Dashboard')
        ws.write(0, 0, 'No vehicle sites provided')
        return

    m0_month_by_site = {s: _first_of_month(vehicle_date_by_site[s]) for s in sites}
    
    # Fixed offsets: M-12 to M+12
    offsets = list(range(-12, 13))

    # Formats
    title_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFFF00', 'center_across': True, 'font_size': 16})
    head_fmt = workbook.add_format({'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'center_across': True, 'text_wrap': True})
    head_site_fmt = workbook.add_format({'bold': True, 'bg_color': '#DAEEF3', 'center_across': True, 'text_wrap': True})
    head_month_fmt = workbook.add_format({'bold': True, 'bg_color': '#00B050', 'font_color': 'white', 'center_across': True, 'text_wrap': True})
    m0_head_fmt = workbook.add_format({'bold': True, 'bg_color': '#FFD966', 'center_across': True, 'align': 'center', 'text_wrap': True})
    num_fmt = workbook.add_format({'num_format': '#,##0'})
    bold_num_fmt = workbook.add_format({'num_format': '#,##0', 'bold': True})
    dollar_fmt = workbook.add_format({'num_format': '$#,##0'})
    bold_dollar_fmt = workbook.add_format({'num_format': '$#,##0', 'bold': True})
    dec_num_fmt = workbook.add_format({'num_format': '#,##0.0'})
    bold_dec_num_fmt = workbook.add_format({'num_format': '#,##0.0', 'bold': True})
    pct_fmt = workbook.add_format({'num_format': '0.0%'})
    bold_pct_fmt = workbook.add_format({'num_format': '0.0%', 'bold': True})
    italic_pct_plus_fmt = workbook.add_format({'num_format': '+0.0%;-0.0%;0.0%', 'italic': True})
    italic_dec_plus_fmt = workbook.add_format({'num_format': '+0.0;-0.0;0.0', 'italic': True})
    unit_label_fmt = workbook.add_format({'bold': True, 'font_size': 11, 'align': 'right'})
    selector_value_fmt = workbook.add_format({'bg_color': '#FFFF00', 'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter'})

    # Datas-sheet base formats (space-separated thousands: # ##0)
    space_num_fmt = workbook.add_format({'num_format': '# ##0'})
    bold_space_sub_fmt = workbook.add_format({'num_format': '# ##0', 'bold': True, 'bg_color': '#DAEEF3'})
    # Conditional formats applied via conditional_format (Profit → $, Over waste → %)
    cond_dollar_fmt = workbook.add_format({'num_format': '$# ##0'})
    cond_pct_fmt = workbook.add_format({'num_format': '0.0%'})
    cond_sub_dollar_fmt = workbook.add_format({'num_format': '$# ##0', 'bold': True, 'bg_color': '#DAEEF3'})
    cond_sub_pct_fmt = workbook.add_format({'num_format': '0.0%', 'bold': True, 'bg_color': '#DAEEF3'})

    # --- Fetch all data from DB ---
    min_m0 = min(m0_month_by_site.values())
    start_month = min_m0 + relativedelta(months=-12)
    q_start = start_month
    q_end = current_month + relativedelta(months=+13)  # for M+12

    # Sales data
    sales_rows = con.exec_driver_sql(
        """
        SELECT Sales.Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(Total_Sales,0) - IFNULL(Bottle_Sales,0)) AS bottles,
               AVG(Number_Open_Days) AS open_days,
               SUM(IFNULL(WiS_Sales,0)) AS wis_sales
        FROM Sales
        WHERE Month >=  %s AND Month < %s
        GROUP BY Sales.Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()

    sales_bottles = {(r[0], r[1]): (r[2] or 0) for r in sales_rows}  # inc. WinS
    sales_open_days = {(r[0], r[1]): (r[3] or 0) for r in sales_rows}
    sales_wis = {(r[0], r[1]): (r[4] or 0) for r in sales_rows}
    sales_bottles_exc_wins = {k: v - sales_wis.get(k, 0) for k, v in sales_bottles.items()}

    # Revenue for profit
    revenue_rows = con.exec_driver_sql(
        """
        SELECT Sales.Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(Total_Income,0)) AS income
        FROM Sales
        WHERE Month >= %s AND Month < %s
        GROUP BY Sales.Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()
    sales_income = {(r[0], r[1]): (r[2] or 0) for r in revenue_rows}

    # Expenses for profit
    category_expenses = CategoryExpenses()
    cat_clause, cat_params = _in_clause(category_expenses)
    expenses_rows = con.exec_driver_sql(
        f"""
        SELECT Expenses.Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(Amount_Expenses,0)) AS cost
        FROM Expenses
        WHERE Month >= %s AND Month < %s
            AND Category_expenses IN {cat_clause}
        GROUP BY Expenses.Id_Site, m
        """,
        tuple([q_start, q_end] + cat_params),
    ).fetchall()
    expenses_cost = {(r[0], r[1]): (r[2] or 0) for r in expenses_rows}

    # Indicators
    ind_rows = con.exec_driver_sql(
        """
        SELECT Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               AVG(Number_of_Vehicle) AS vehicles,
               AVG(Number_of_Operator) AS operators,
               SUM(Water_Consume) AS water_consume
        FROM Indicators
        WHERE Month >= %s AND Month < %s
        GROUP BY Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()

    ind_vehicles = {(r[0], r[1]): (r[2] if r[2] is not None else None) for r in ind_rows}
    ind_operators = {(r[0], r[1]): (r[3] if r[3] is not None else None) for r in ind_rows}
    ind_water = {(r[0], r[1]): (r[4] if r[4] is not None else None) for r in ind_rows}

    # Beneficiaries (AVG to handle duplicate rows — stock value, not a flow)
    benef_rows = con.exec_driver_sql(
        """
        SELECT Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               AVG(IFNULL(Beneficiaries,0)) AS benef
        FROM Beneficiaries
        WHERE Month >= %s AND Month < %s
        GROUP BY Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()
    benef_by_site = {(r[0], r[1]): (r[2] or 0) for r in benef_rows}

    # WinS income (for P&L revenue split)
    wins_inc_rows = con.exec_driver_sql(
        """
        SELECT Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(WiS_Income,0)) AS wins_income
        FROM Sales
        WHERE Month >= %s AND Month < %s
        GROUP BY Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()
    wins_income_by_site = {(r[0], r[1]): (r[2] or 0) for r in wins_inc_rows}

    # HOD Sales data (for HOD %)
    hod_rows = con.exec_driver_sql(
        """
        SELECT Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(Hod_Sales,0)) AS hod_sales,
               SUM(IFNULL(Total_Sales,0)) AS total_sales,
               SUM(IFNULL(WiS_Sales,0)) AS wis_sales,
               SUM(IFNULL(Bottle_Sales,0)) AS bottle_sales
        FROM Sales
        WHERE Month >= %s AND Month < %s
        GROUP BY Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()
    hod_sales_by_site = {(r[0], r[1]): (r[2] or 0) for r in hod_rows}
    total_sales_by_site = {(r[0], r[1]): (r[3] or 0) for r in hod_rows}
    wis_sales_by_site = {(r[0], r[1]): (r[4] or 0) for r in hod_rows}
    bottle_sales_by_site = {(r[0], r[1]): (r[5] or 0) for r in hod_rows}

    # Expenses by category (for P&L breakdown)
    exp_cat_rows = con.exec_driver_sql(
        f"""
        SELECT Expenses.Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               Category_expenses AS cat,
               SUM(IFNULL(Amount_Expenses,0)) AS cost
        FROM Expenses
        WHERE Month >= %s AND Month < %s
            AND Category_expenses IN {cat_clause}
        GROUP BY Expenses.Id_Site, m, Category_expenses
        """,
        tuple([q_start, q_end] + cat_params),
    ).fetchall()
    exp_by_cat: dict[str, dict[tuple, float]] = {}
    exp_rows_by_cat: dict[str, list] = {}
    for r in exp_cat_rows:
        cat = r[2]
        exp_by_cat.setdefault(cat, {})[(r[0], r[1])] = (r[3] or 0)
        exp_rows_by_cat.setdefault(cat, []).append((r[0], r[1], r[3] or 0))

    # Entrepreneur salary only (fix + variable)
    ent_sal_rows = con.exec_driver_sql(
        """
        SELECT Id_Site,
               DATE_FORMAT(Month, '%%Y-%%m-01') AS m,
               SUM(IFNULL(Amount_Expenses,0)) AS cost
        FROM Expenses
        WHERE Month >= %s AND Month < %s
            AND Ref_expenses IN ('fix_salary_entrepreneurs', 'variable_salary_entrepreneurs')
        GROUP BY Id_Site, m
        """,
        (q_start, q_end),
    ).fetchall()
    ent_salary_by_site = {(r[0], r[1]): (r[2] or 0) for r in ent_sal_rows}

    # Site metadata (Platform, Advisor)
    site_meta_rows = con.exec_driver_sql(
        "SELECT Id_Site, Platform, Advisor FROM Sites"
    ).fetchall()
    site_platform = {r[0]: (r[1] or '') for r in site_meta_rows}
    site_advisor = {r[0]: (r[2] or '') for r in site_meta_rows}

    # Network averages (calendar month basis)
    def _avg_by_month(rows, idx_value: int):
        sums, counts = {}, {}
        for rr in rows:
            m, v = rr[1], rr[idx_value]
            if v is None:
                continue
            sums[m] = sums.get(m, 0) + float(v)
            counts[m] = counts.get(m, 0) + 1
        return {m: (sums[m] / counts[m]) if counts[m] else 0 for m in sums}

    network_avg_sales = _avg_by_month(sales_rows, 2)  # inc. WinS
    network_avg_open_days = _avg_by_month(sales_rows, 3)
    network_avg_wis_sales = _avg_by_month(sales_rows, 4)
    network_avg_sales_exc_wins = {m: network_avg_sales[m] - network_avg_wis_sales.get(m, 0)
                                  for m in network_avg_sales}
    network_avg_vehicles = _avg_by_month(ind_rows, 2)
    network_avg_operators = _avg_by_month(ind_rows, 3)
    network_avg_water = _avg_by_month(ind_rows, 4)
    network_avg_benef = _avg_by_month(benef_rows, 2)

    # P&L network averages
    network_avg_total_income = _avg_by_month(revenue_rows, 2)
    network_avg_wins_income = _avg_by_month(wins_inc_rows, 2)
    network_avg_exp: dict[str, dict] = {}
    for cat, rows in exp_rows_by_cat.items():
        network_avg_exp[cat] = _avg_by_month(rows, 2)
    network_avg_ent_salary = _avg_by_month(ent_sal_rows, 2)

    # All sites that have data in the DB (for network-wide computed metrics)
    all_db_sites = sorted({r[0] for r in sales_rows})

    exchange_rate = exchange_rate_year(Current_date)

    def _profit_value(site: str, mm: date) -> float | None:
        key = (site, mm.strftime('%Y-%m-01'))
        revenue = sales_income.get(key)
        cost = expenses_cost.get(key)
        if revenue is None and cost is None:
            return None
        return ((revenue or 0) - (cost or 0)) / exchange_rate

    # Network avg profit (all sites in DB, not just vehicle sites)
    month_sums_profit, month_counts_profit = {}, {}
    months_list = list(_iter_months(start_month, current_month + relativedelta(months=+12)))
    for site in all_db_sites:
        for mm in months_list:
            mkey = mm.strftime('%Y-%m-01')
            pv = _profit_value(site, mm)
            if pv is not None:
                month_sums_profit[mkey] = month_sums_profit.get(mkey, 0) + float(pv)
                month_counts_profit[mkey] = month_counts_profit.get(mkey, 0) + 1
    network_avg_profit = {m: (month_sums_profit[m] / month_counts_profit[m]) if month_counts_profit[m] else 0 for m in month_sums_profit}

    # Helper functions for metrics
    def get_open_days(site: str, mm: date) -> float | None:
        return sales_open_days.get((site, mm.strftime('%Y-%m-01')))

    def get_closed_days(site: str, mm: date) -> float | None:
        od = get_open_days(site, mm)
        if od is None:
            return None
        return calendar.monthrange(mm.year, mm.month)[1] - od

    def get_overwaste(site: str, mm: date) -> float | None:
        water = ind_water.get((site, mm.strftime('%Y-%m-01')))
        sales = sales_bottles.get((site, mm.strftime('%Y-%m-01')))
        if water is None or water == 0 or sales is None:
            return None
        potential = water / 20
        if potential <= 0:
            return None
        val = 1 - (sales / potential)
        return max(0.0, min(1.0, val))

    def network_closed_days(mm: date) -> float | None:
        od = network_avg_open_days.get(mm.strftime('%Y-%m-01'))
        if od is None:
            return None
        return calendar.monthrange(mm.year, mm.month)[1] - od

    def get_beneficiaries(site: str, mm: date) -> float | None:
        return benef_by_site.get((site, mm.strftime('%Y-%m-01')))

    def network_beneficiaries(mm: date) -> float | None:
        return network_avg_benef.get(mm.strftime('%Y-%m-01'))

    def network_overwaste(mm: date  ) -> float | None:
        mkey = mm.strftime('%Y-%m-01')
        water = network_avg_water.get(mkey)
        sales = network_avg_sales.get(mkey)
        if water is None or water == 0 or sales is None:
            return None
        potential = water / 20
        if potential <= 0:
            return None
        val = 1 - (sales / potential)
        return max(0.0, min(1.0, val))

    # HOD Sales % metric
    def _hod_pct(site: str, mm: date) -> float | None:
        key = (site, mm.strftime('%Y-%m-01'))
        hod = hod_sales_by_site.get(key)
        total = total_sales_by_site.get(key)
        if hod is None or total is None:
            return None
        wis = wis_sales_by_site.get(key, 0)
        bottle = bottle_sales_by_site.get(key, 0)
        denom = total - wis - bottle
        if denom <= 0:
            return None
        return hod / denom

    # Network HOD % (all sites in DB, not just vehicle sites)
    _hod_month_sums: dict[str, float] = {}
    _hod_month_counts: dict[str, int] = {}
    for _site in all_db_sites:
        for _mm in months_list:
            _v = _hod_pct(_site, _mm)
            if _v is not None:
                _mk = _mm.strftime('%Y-%m-01')
                _hod_month_sums[_mk] = _hod_month_sums.get(_mk, 0) + _v
                _hod_month_counts[_mk] = _hod_month_counts.get(_mk, 0) + 1
    network_avg_hod_pct = {m: _hod_month_sums[m] / _hod_month_counts[m]
                           for m in _hod_month_sums if _hod_month_counts.get(m, 0) > 0}

    def _net_hod_pct(mm: date) -> float | None:
        return network_avg_hod_pct.get(mm.strftime('%Y-%m-01'))

    # Bottles / vehicle / day (inc. WinS)
    def _bottles_per_vehicle_day(site: str, mm: date) -> float | None:
        key = (site, mm.strftime('%Y-%m-01'))
        bottles = sales_bottles.get(key)  # inc. WinS
        vehicles = ind_vehicles.get(key)
        if bottles is None or vehicles is None or vehicles == 0:
            return None
        dim = calendar.monthrange(mm.year, mm.month)[1]
        return (float(bottles) / dim) / float(vehicles) if dim else None

    def _net_bottles_per_vehicle_day(mm: date) -> float | None:
        mkey = mm.strftime('%Y-%m-01')
        bottles = network_avg_sales.get(mkey)  # inc. WinS
        vehicles = network_avg_vehicles.get(mkey)
        if bottles is None or vehicles is None or vehicles == 0:
            return None
        dim = calendar.monthrange(mm.year, mm.month)[1]
        return (bottles / dim) / vehicles if dim else None

    # P&L metric functions
    def _pnl_income_sales(site: str, mm: date) -> float | None:
        total = sales_income.get((site, mm.strftime('%Y-%m-01')))
        if total is None:
            return None
        wins = wins_income_by_site.get((site, mm.strftime('%Y-%m-01')), 0)
        return (total - wins) / exchange_rate

    def _pnl_income_wins(site: str, mm: date) -> float | None:
        v = wins_income_by_site.get((site, mm.strftime('%Y-%m-01')))
        return v / exchange_rate if v else None

    def _pnl_exp(cat_name: str, site: str, mm: date) -> float | None:
        v = exp_by_cat.get(cat_name, {}).get((site, mm.strftime('%Y-%m-01')))
        return v / exchange_rate if v is not None else None

    def _pnl_exp_salary(site: str, mm: date) -> float | None:
        return _pnl_exp('salary', site, mm)

    def _pnl_exp_production(site: str, mm: date) -> float | None:
        return _pnl_exp('production', site, mm)

    def _pnl_exp_delivery(site: str, mm: date) -> float | None:
        return _pnl_exp('delivery', site, mm)

    def _pnl_exp_contribution(site: str, mm: date) -> float | None:
        return _pnl_exp('contribution', site, mm)

    def _pnl_exp_other(site: str, mm: date) -> float | None:
        key = (site, mm.strftime('%Y-%m-01'))
        inv = exp_by_cat.get('investment', {}).get(key)
        tech = exp_by_cat.get('technical', {}).get(key)
        if inv is None and tech is None:
            return None
        return ((inv or 0) + (tech or 0)) / exchange_rate

    # P&L network functions
    def _pnl_net_income_sales(mm: date) -> float | None:
        total = network_avg_total_income.get(mm.strftime('%Y-%m-01'))
        if total is None:
            return None
        wins = network_avg_wins_income.get(mm.strftime('%Y-%m-01'), 0)
        return (total - wins) / exchange_rate

    def _pnl_net_income_wins(mm: date) -> float | None:
        v = network_avg_wins_income.get(mm.strftime('%Y-%m-01'))
        return v / exchange_rate if v else None

    def _pnl_net_exp(cat_name: str, mm: date) -> float | None:
        v = network_avg_exp.get(cat_name, {}).get(mm.strftime('%Y-%m-01'))
        return v / exchange_rate if v is not None else None

    def _pnl_net_salary(mm: date) -> float | None:
        return _pnl_net_exp('salary', mm)

    def _pnl_net_production(mm: date) -> float | None:
        return _pnl_net_exp('production', mm)

    def _pnl_net_delivery(mm: date) -> float | None:
        return _pnl_net_exp('delivery', mm)

    def _pnl_net_contribution(mm: date) -> float | None:
        return _pnl_net_exp('contribution', mm)

    def _pnl_net_other(mm: date) -> float | None:
        inv = network_avg_exp.get('investment', {}).get(mm.strftime('%Y-%m-01'))
        tech = network_avg_exp.get('technical', {}).get(mm.strftime('%Y-%m-01'))
        if inv is None and tech is None:
            return None
        return ((inv or 0) + (tech or 0)) / exchange_rate

    # Entrepreneur salary metric (fix + variable only)
    def _pnl_ent_salary(site: str, mm: date) -> float | None:
        v = ent_salary_by_site.get((site, mm.strftime('%Y-%m-01')))
        return v / exchange_rate if v is not None else None

    def _pnl_net_ent_salary(mm: date) -> float | None:
        v = network_avg_ent_salary.get(mm.strftime('%Y-%m-01'))
        return v / exchange_rate if v is not None else None

    # Waves (dynamic — wave_labels / wave_maps / wave_sites_list already built above)

    # =====================================================================
    # Pre-create worksheets in desired tab order
    # =====================================================================
    ws_dash = workbook.add_worksheet('Dashboard')
    ws_graph = workbook.add_worksheet('Graphs')
    ws_datas = workbook.add_worksheet('Datas')
    ws_info = workbook.add_worksheet('Instructions')
    ws_events = workbook.add_worksheet('Vehicle events')
    ws_data_sel = workbook.add_worksheet('Raw Data')
    ws_data_net = workbook.add_worksheet('Network')
    ws_events.write(0, 0, 'All list', head_site_fmt)
    ws_events.write(1, 0, 'Total Avg')
    for wi, lbl in enumerate(wave_labels):
        ws_events.write(2 + wi, 0, lbl)
    for i, site in enumerate(sites, start=2 + len(wave_labels)):
        ws_events.write(i, 0, site)
    dv_site_source_all = f"='Vehicle events'!$A$2:$A${len(sites) + 2 + len(wave_labels)}"
    ws_events.hide()

    # =====================================================================
    # Helper: write a metric table
    # =====================================================================
    def _compute_aligned(site_list, vd_map, metric_func):
        """Returns list of values (one per offset) for a group of sites."""
        m0_grp = {s: _first_of_month(vd_map[s]) for s in site_list if s in vd_map}
        if not m0_grp:
            return [None] * len(offsets)
        result = []
        for off in offsets:
            vals = []
            for s, m0 in m0_grp.items():
                mm = m0 + relativedelta(months=off)
                if mm > current_month:
                    continue
                vals.append(metric_func(s, mm))
            # Average non-null
            vs = [v for v in vals if v is not None]
            result.append((sum(vs) / len(vs)) if vs else None)
        return result

    def _compute_network_aligned(metric_func_net, site_list_override=None):
        """Returns list of network avg values (one per offset), aligned to vehicle sites' M0.

        For each offset, resolve each vehicle site's M0+offset to an absolute
        calendar month, look up the network average for that month, then
        average the non-null results.  This ensures that if *some* sites
        already have data for a given offset the network value is present.
        If site_list_override is given, only those sites are considered.
        """
        s_list = site_list_override if site_list_override is not None else sites
        result = []
        for off in offsets:
            vals = []
            for s in s_list:
                m0 = m0_month_by_site.get(s)
                if m0 is None:
                    continue
                mm = m0 + relativedelta(months=off)
                if mm > current_month:
                    continue
                v = metric_func_net(mm)
                if v is not None:
                    vals.append(v)
            result.append((sum(vals) / len(vals)) if vals else None)
        return result

    def write_metric_table(ws, start_row, metric_name, sel_data_dict, fmt):
        """Write a metric table: header + Total Avg, wave groups, all sites."""
        ws.write(start_row, 0, metric_name, head_site_fmt)
        ws.write(start_row, 1, 'Site', head_site_fmt)
        for j, off in enumerate(offsets):
            col = 2 + j
            lbl = _label_for_offset(off)
            fmt_hdr = m0_head_fmt if off == 0 else head_month_fmt
            ws.write(start_row, col, lbl, fmt_hdr)

        row = start_row + 1
        # Total Avg
        ws.write(row, 1, 'Total Avg')
        for j, val in enumerate(sel_data_dict['Total Avg']):
            ws.write(row, 2 + j, val if val is not None else '', fmt)
        row += 1

        for wlbl in wave_labels:
            ws.write(row, 1, wlbl)
            for j, val in enumerate(sel_data_dict[wlbl]):
                ws.write(row, 2 + j, val if val is not None else '', fmt)
            row += 1

        # Individual sites
        for site in sites:
            ws.write(row, 1, site)
            for j, val in enumerate(sel_data_dict[site]):
                ws.write(row, 2 + j, val if val is not None else '', fmt)
            row += 1

        return row  # next available row

    def write_network_table(ws, start_row, metric_name, net_data_dict, fmt):
        """Write a network metric table with same layout as Raw Data."""
        ws.write(start_row, 0, metric_name, head_site_fmt)
        ws.write(start_row, 1, 'Site', head_site_fmt)
        for j, off in enumerate(offsets):
            col = 2 + j
            lbl = _label_for_offset(off)
            fmt_hdr = m0_head_fmt if off == 0 else head_month_fmt
            ws.write(start_row, col, lbl, fmt_hdr)

        row = start_row + 1
        # Total Avg
        ws.write(row, 1, 'Total Avg')
        for j, val in enumerate(net_data_dict['Total Avg']):
            ws.write(row, 2 + j, val if val is not None else '', fmt)
        row += 1

        for wlbl in wave_labels:
            ws.write(row, 1, wlbl)
            for j, val in enumerate(net_data_dict[wlbl]):
                ws.write(row, 2 + j, val if val is not None else '', fmt)
            row += 1

        # Individual sites
        for site in sites:
            ws.write(row, 1, site)
            for j, val in enumerate(net_data_dict[site]):
                ws.write(row, 2 + j, val if val is not None else '', fmt)
            row += 1

        return row

    # =====================================================================
    # Sheet 2: Raw Data (hidden) - All aligned data tables
    # =====================================================================
    ws_data_sel.set_zoom(85)

    next_row = 0

    # --- Helper for building network data dicts ---
    def _build_network_data(metric_func_net):
        data = {
            'Total Avg': _compute_network_aligned(metric_func_net),
            **{lbl: _compute_network_aligned(metric_func_net, wsites)
               for lbl, wsites in zip(wave_labels, wave_sites_list)},
        }
        for site in sites:
            data[site] = _compute_network_aligned(metric_func_net, [site])
        return data

    # 1. Sales (bottles/mo) – exc. WinS
    def _sales(site, mm):
        return sales_bottles_exc_wins.get((site, mm.strftime('%Y-%m-01')))

    sales_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, _sales),
        **{lbl: _compute_aligned(wsites, wmap, _sales) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        sales_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, _sales)

    def _net_sales(mm):
        return network_avg_sales_exc_wins.get(mm.strftime('%Y-%m-01'))

    sales_net_data = _build_network_data(_net_sales)

    next_row = write_metric_table(ws_data_sel, next_row, 'Sales exc. WinS (bottles/month)', sales_sel_data, num_fmt)
    next_row += 2

    # 2. Sales exc. WinS (bottles/day)
    def _sales_day(site, mm):
        s = sales_bottles_exc_wins.get((site, mm.strftime('%Y-%m-01')))
        if s is None:
            return None
        dim = calendar.monthrange(mm.year, mm.month)[1]
        return s / dim if dim else None

    sales_day_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, _sales_day),
        **{lbl: _compute_aligned(wsites, wmap, _sales_day) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        sales_day_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, _sales_day)

    def _net_sales_day(mm):
        s = network_avg_sales_exc_wins.get(mm.strftime('%Y-%m-01'))
        if s is None:
            return None
        dim = calendar.monthrange(mm.year, mm.month)[1]
        return s / dim if dim else None

    sales_day_net_data = _build_network_data(_net_sales_day)

    next_row = write_metric_table(ws_data_sel, next_row, 'Sales exc. WinS (bottles/day)', sales_day_sel_data, dec_num_fmt)
    next_row += 2

    # 3. Profit ($)
    profit_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, _profit_value),
        **{lbl: _compute_aligned(wsites, wmap, _profit_value) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        profit_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, _profit_value)

    def _net_profit(mm):
        return network_avg_profit.get(mm.strftime('%Y-%m-01'))

    profit_net_data = _build_network_data(_net_profit)

    next_row = write_metric_table(ws_data_sel, next_row, 'Profit ($)', profit_sel_data, dollar_fmt)
    next_row += 2

    # 4. Closed days
    closed_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, get_closed_days),
        **{lbl: _compute_aligned(wsites, wmap, get_closed_days) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        closed_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, get_closed_days)

    closed_net_data = _build_network_data(network_closed_days)

    next_row = write_metric_table(ws_data_sel, next_row, 'Closed days', closed_sel_data, dec_num_fmt)
    next_row += 2

    # 5. Vehicles
    def _vehicles(site, mm):
        return ind_vehicles.get((site, mm.strftime('%Y-%m-01')))

    vehicles_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, _vehicles),
        **{lbl: _compute_aligned(wsites, wmap, _vehicles) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        vehicles_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, _vehicles)

    def _net_vehicles(mm):
        return network_avg_vehicles.get(mm.strftime('%Y-%m-01'))

    vehicles_net_data = _build_network_data(_net_vehicles)

    next_row = write_metric_table(ws_data_sel, next_row, 'Vehicles', vehicles_sel_data, dec_num_fmt)
    next_row += 2

    # 6. Operators
    def _operators(site, mm):
        return ind_operators.get((site, mm.strftime('%Y-%m-01')))

    operators_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, _operators),
        **{lbl: _compute_aligned(wsites, wmap, _operators) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        operators_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, _operators)

    def _net_operators(mm):
        return network_avg_operators.get(mm.strftime('%Y-%m-01'))

    operators_net_data = _build_network_data(_net_operators)

    next_row = write_metric_table(ws_data_sel, next_row, 'Operators', operators_sel_data, dec_num_fmt)
    next_row += 2

    # 7. Over waste %
    overwaste_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, get_overwaste),
        **{lbl: _compute_aligned(wsites, wmap, get_overwaste) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        overwaste_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, get_overwaste)

    overwaste_net_data = _build_network_data(network_overwaste)

    next_row = write_metric_table(ws_data_sel, next_row, 'Over waste %', overwaste_sel_data, pct_fmt)
    next_row += 2

    # 8. Beneficiaries
    benef_sel_data = {
        'Total Avg': _compute_aligned(sites, vehicle_date_by_site, get_beneficiaries),
        **{lbl: _compute_aligned(wsites, wmap, get_beneficiaries) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
    }
    for site in sites:
        benef_sel_data[site] = _compute_aligned([site], vehicle_date_by_site, get_beneficiaries)

    benef_net_data = _build_network_data(network_beneficiaries)

    next_row = write_metric_table(ws_data_sel, next_row, 'Beneficiaries', benef_sel_data, num_fmt)
    next_row += 2

    # --- P&L aligned tables ---
    def _build_pnl_table(metric_func):
        data = {
            'Total Avg': _compute_aligned(sites, vehicle_date_by_site, metric_func),
            **{lbl: _compute_aligned(wsites, wmap, metric_func) for lbl, wsites, wmap in zip(wave_labels, wave_sites_list, wave_maps)},
        }
        for site in sites:
            data[site] = _compute_aligned([site], vehicle_date_by_site, metric_func)
        return data

    pnl_inc_sales_data = _build_pnl_table(_pnl_income_sales)
    pnl_inc_sales_net = _build_network_data(_pnl_net_income_sales)
    next_row = write_metric_table(ws_data_sel, next_row, 'Income Sales ($)', pnl_inc_sales_data, dollar_fmt)
    next_row += 2

    pnl_inc_wins_data = _build_pnl_table(_pnl_income_wins)
    pnl_inc_wins_net = _build_network_data(_pnl_net_income_wins)
    next_row = write_metric_table(ws_data_sel, next_row, 'Income WinS ($)', pnl_inc_wins_data, dollar_fmt)
    next_row += 2

    pnl_salary_data = _build_pnl_table(_pnl_exp_salary)
    pnl_salary_net = _build_network_data(_pnl_net_salary)
    next_row = write_metric_table(ws_data_sel, next_row, 'Salary ($)', pnl_salary_data, dollar_fmt)
    next_row += 2

    pnl_production_data = _build_pnl_table(_pnl_exp_production)
    pnl_production_net = _build_network_data(_pnl_net_production)
    next_row = write_metric_table(ws_data_sel, next_row, 'Production ($)', pnl_production_data, dollar_fmt)
    next_row += 2

    pnl_delivery_data = _build_pnl_table(_pnl_exp_delivery)
    pnl_delivery_net = _build_network_data(_pnl_net_delivery)
    next_row = write_metric_table(ws_data_sel, next_row, 'Delivery ($)', pnl_delivery_data, dollar_fmt)
    next_row += 2

    pnl_contribution_data = _build_pnl_table(_pnl_exp_contribution)
    pnl_contribution_net = _build_network_data(_pnl_net_contribution)
    next_row = write_metric_table(ws_data_sel, next_row, 'Contribution ($)', pnl_contribution_data, dollar_fmt)
    next_row += 2

    pnl_other_data = _build_pnl_table(_pnl_exp_other)
    pnl_other_net = _build_network_data(_pnl_net_other)
    next_row = write_metric_table(ws_data_sel, next_row, 'Other expenses ($)', pnl_other_data, dollar_fmt)
    next_row += 2

    # 16. HOD Sales (%)
    hod_pct_data = _build_pnl_table(_hod_pct)
    hod_pct_net = _build_network_data(_net_hod_pct)
    next_row = write_metric_table(ws_data_sel, next_row, 'HOD Sales (%)', hod_pct_data, pct_fmt)
    next_row += 2

    # 17. Entrepreneur Salary ($)
    ent_sal_data = _build_pnl_table(_pnl_ent_salary)
    ent_sal_net = _build_network_data(_pnl_net_ent_salary)
    next_row = write_metric_table(ws_data_sel, next_row, 'Entrepreneur Salary ($)', ent_sal_data, dollar_fmt)
    next_row += 2

    # 18. Bottles / vehicle / day (inc. WinS)
    bvd_data = _build_pnl_table(_bottles_per_vehicle_day)
    bvd_net = _build_network_data(_net_bottles_per_vehicle_day)
    next_row = write_metric_table(ws_data_sel, next_row, 'Bottles / vehicle / day', bvd_data, dec_num_fmt)

    ws_data_sel.hide()

    # =====================================================================
    # Sheet 3: Network (hidden) - Network aligned data
    # =====================================================================
    ws_data_net.set_zoom(85)

    next_row = 0
    next_row = write_network_table(ws_data_net, next_row, 'Sales exc. WinS (bottles/month)', sales_net_data, num_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Sales exc. WinS (bottles/day)', sales_day_net_data, dec_num_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Profit ($)', profit_net_data, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Closed days', closed_net_data, dec_num_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Vehicles', vehicles_net_data, dec_num_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Operators', operators_net_data, dec_num_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Over waste %', overwaste_net_data, pct_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Beneficiaries', benef_net_data, num_fmt)
    next_row += 2

    # P&L network tables
    next_row = write_network_table(ws_data_net, next_row, 'Income Sales ($)', pnl_inc_sales_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Income WinS ($)', pnl_inc_wins_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Salary ($)', pnl_salary_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Production ($)', pnl_production_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Delivery ($)', pnl_delivery_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Contribution ($)', pnl_contribution_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Other expenses ($)', pnl_other_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'HOD Sales (%)', hod_pct_net, pct_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Entrepreneur Salary ($)', ent_sal_net, dollar_fmt)
    next_row += 2
    next_row = write_network_table(ws_data_net, next_row, 'Bottles / vehicle / day', bvd_net, dec_num_fmt)

    ws_data_net.hide()

    # =====================================================================
    # Sheet 4: Datas (visible) - Dynamic single table driven by dropdown
    # =====================================================================
    ws_datas.set_zoom(85)

    # Metric names list (must match the header text used in write_metric_table)
    metric_names = [
        'Sales exc. WinS (bottles/month)',
        'Sales exc. WinS (bottles/day)',
        'Profit ($)',
        'Closed days',
        'Vehicles',
        'Operators',
        'Over waste %',
        'Beneficiaries',
        'HOD Sales (%)',
        'Bottles / vehicle / day',
    ]
    # Write metric names in a hidden helper column for dropdown source
    helper_base = 31  # column AF
    for mi, mname in enumerate(metric_names):
        ws_datas.write(mi, helper_base, mname)  # column AF (hidden later)
    dv_metric_source = f"='Datas'!${xl_col_to_name(helper_base)}$1:${xl_col_to_name(helper_base)}${len(metric_names)}"

    # Dropdown for metric selection
    ws_datas.write(0, 0, 'Indicator:', unit_label_fmt)
    ws_datas.write(0, 1, metric_names[0], selector_value_fmt)
    ws_datas.data_validation(0, 1, 0, 1, {'validate': 'list', 'source': dv_metric_source})
    ws_datas.merge_range(0, 1, 0, 3, metric_names[0], selector_value_fmt)

    # --- Helper cells for robust MATCH-based lookup ---
    # AG1: row number of the selected metric's header in Raw Data column A
    helper_match_col = helper_base + 1  # AG
    ws_datas.write_formula(0, helper_match_col,
        "=IFERROR(MATCH($B$1,'Raw Data'!$A:$A,0),1)", dec_num_fmt)
    ag_col = xl_col_to_name(helper_match_col)  # "AG"

    # Search window size for site lookup within a metric block
    rows_per_tbl = 1 + 1 + len(wave_labels) + len(sites)  # header + Total Avg + waves + individual sites

    # Build wave lookup for each site
    site_wave = {}
    for lbl, wsites in zip(wave_labels, wave_sites_list):
        for s in wsites:
            site_wave[s] = lbl

    # Info columns: A=Sites, B=Platform, C=Advisor, D=Wave, E=Date installation
    # Data columns start at F (col index 5)
    data_col_start = 5

    # Layout:
    # Row 0: Dropdown
    # Row 1: SUBTOTAL Average
    # Row 2: SUBTOTAL Sum
    # Row 3: Header (with autofilter)
    # Row 4+: Site data rows

    subtotal_avg_row = 1   # 0-based
    subtotal_sum_row = 2
    hdr_row = 3
    first_site_row = 4     # 0-based
    site_labels = sorted(sites, key=lambda s: vehicle_date_by_site.get(s, date.max))
    num_sites = len(site_labels)
    first_site_excel = first_site_row + 1  # 1-based = 5
    last_site_excel = first_site_excel + num_sites - 1
    last_data_col = data_col_start + len(offsets) - 1

    # --- Subtotal rows (above header) ---
    date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd', 'align': 'center'})
    bold_dec_sub_fmt = workbook.add_format({'num_format': '#,##0.0', 'bold': True, 'bg_color': '#DAEEF3'})
    bold_sub_label_fmt = workbook.add_format({'bold': True, 'bg_color': '#DAEEF3'})

    # Average row (SUBTOTAL 101 = average ignoring hidden rows)
    ws_datas.write(subtotal_avg_row, 0, 'Average', bold_sub_label_fmt)
    for c in range(1, data_col_start):
        ws_datas.write(subtotal_avg_row, c, '', bold_sub_label_fmt)
    for j in range(len(offsets)):
        col_letter = xl_col_to_name(data_col_start + j)
        formula = f"=IFERROR(SUBTOTAL(101,{col_letter}${first_site_excel}:{col_letter}${last_site_excel}),\"\")"
        ws_datas.write_formula(subtotal_avg_row, data_col_start + j, formula, bold_space_sub_fmt)

    # Sum row (SUBTOTAL 109 = sum ignoring hidden rows)
    ws_datas.write(subtotal_sum_row, 0, 'Sum', bold_sub_label_fmt)
    for c in range(1, data_col_start):
        ws_datas.write(subtotal_sum_row, c, '', bold_sub_label_fmt)
    for j in range(len(offsets)):
        col_letter = xl_col_to_name(data_col_start + j)
        formula = f"=IFERROR(SUBTOTAL(109,{col_letter}${first_site_excel}:{col_letter}${last_site_excel}),\"\")"
        ws_datas.write_formula(subtotal_sum_row, data_col_start + j, formula, bold_space_sub_fmt)

    # --- Header row ---
    ws_datas.write(hdr_row, 0, 'Sites', head_site_fmt)
    ws_datas.write(hdr_row, 1, 'Platform', head_site_fmt)
    ws_datas.write(hdr_row, 2, 'Advisor', head_site_fmt)
    ws_datas.write(hdr_row, 3, 'Wave', head_site_fmt)
    ws_datas.write(hdr_row, 4, 'Date installation', head_site_fmt)
    for j, off in enumerate(offsets):
        col = data_col_start + j
        lbl = _label_for_offset(off)
        fmt_hdr = m0_head_fmt if off == 0 else head_month_fmt
        ws_datas.write(hdr_row, col, lbl, fmt_hdr)

    # Autofilter on header row
    ws_datas.autofilter(hdr_row, 0, hdr_row + num_sites, last_data_col)

    # AH column for the MATCH helper per row
    helper_ae_col = helper_match_col + 1  # AH
    ah_col = xl_col_to_name(helper_ae_col)  # "AH"

    # --- Write site rows ---
    for i, label in enumerate(site_labels):
        r = first_site_row + i
        excel_r = r + 1
        # Col A: Site name
        ws_datas.write(r, 0, label)
        # Col B: Platform
        ws_datas.write(r, 1, site_platform.get(label, ''))
        # Col C: Advisor
        ws_datas.write(r, 2, site_advisor.get(label, ''))
        # Col D: Wave
        ws_datas.write(r, 3, site_wave.get(label, ''))
        # Col E: Date installation véhicule
        if label in vehicle_date_by_site:
            ws_datas.write_datetime(r, 4, vehicle_date_by_site[label], date_fmt)
        else:
            ws_datas.write(r, 4, '')

        # AH column: position of this site within the metric block in Raw Data
        ae_formula = (
            f'=IFERROR(MATCH($A{excel_r},'
            f"INDIRECT(\"'Raw Data'!$B$\"&${ag_col}$1&\":$B$\""
            f"&(${ag_col}$1+{rows_per_tbl})),0),\"\")"
        )
        ws_datas.write_formula(r, helper_ae_col, ae_formula, dec_num_fmt)

        # Data cells: INDEX on Raw Data at [header_row + site_offset - 1, column]
        col_offset = data_col_start - 2  # 5 - 2 = 3
        for j in range(len(offsets)):
            formula = (
                f"=IFERROR(INDEX('Raw Data'!$A:$AA,"
                f"${ag_col}$1+${ah_col}{excel_r}-1,COLUMN()-{col_offset}),\"\")"
            )
            ws_datas.write_formula(r, data_col_start + j, formula, space_num_fmt)

    # --- Conditional formatting: change unit based on selected metric ---
    # Data cell range
    dr_r1, dr_c1 = first_site_row, data_col_start
    dr_r2, dr_c2 = first_site_row + num_sites - 1, last_data_col
    # Subtotal range (avg + sum rows)
    sr_r1, sr_c1 = subtotal_avg_row, data_col_start
    sr_r2, sr_c2 = subtotal_sum_row, last_data_col

    # Profit ($) → dollar format
    ws_datas.conditional_format(dr_r1, dr_c1, dr_r2, dr_c2, {
        'type': 'formula', 'criteria': '=$B$1="Profit ($)"', 'format': cond_dollar_fmt})
    ws_datas.conditional_format(sr_r1, sr_c1, sr_r2, sr_c2, {
        'type': 'formula', 'criteria': '=$B$1="Profit ($)"', 'format': cond_sub_dollar_fmt})

    # Over waste % → percentage format
    ws_datas.conditional_format(dr_r1, dr_c1, dr_r2, dr_c2, {
        'type': 'formula', 'criteria': '=$B$1="Over waste %"', 'format': cond_pct_fmt})
    ws_datas.conditional_format(sr_r1, sr_c1, sr_r2, sr_c2, {
        'type': 'formula', 'criteria': '=$B$1="Over waste %"', 'format': cond_sub_pct_fmt})

    # HOD Sales (%) → percentage format
    ws_datas.conditional_format(dr_r1, dr_c1, dr_r2, dr_c2, {
        'type': 'formula', 'criteria': '=$B$1="HOD Sales (%)"', 'format': cond_pct_fmt})
    ws_datas.conditional_format(sr_r1, sr_c1, sr_r2, sr_c2, {
        'type': 'formula', 'criteria': '=$B$1="HOD Sales (%)"', 'format': cond_sub_pct_fmt})

    # Hide helper columns AF, AG, AH
    ws_datas.set_column(helper_base, helper_ae_col, None, None, {'hidden': True})
    ws_datas.set_column(0, 0, 12)  # Sites
    ws_datas.set_column(1, 1, 12)  # Platform
    ws_datas.set_column(2, 2, 12)  # Advisor
    ws_datas.set_column(3, 3, 10)  # Wave
    ws_datas.set_column(4, 4, 16)  # Date installation

    # =====================================================================
    # Sheet 5: Graphs (visible)
    # =====================================================================
    ws_graph.set_zoom(90)
    ws_graph.set_tab_color('#2E75B6')

    # ---- Graph-specific formats ----
    g_title_fmt = workbook.add_format({
        'bold': True, 'font_size': 14, 'font_color': 'white',
        'bg_color': '#1B3A5C', 'align': 'center', 'valign': 'vcenter',
    })
    g_label_fmt = workbook.add_format({
        'bold': True, 'font_size': 11, 'align': 'right', 'valign': 'vcenter',
    })
    g_selector_fmt = workbook.add_format({
        'bold': True, 'font_size': 12, 'bg_color': '#FFFF00',
        'align': 'center', 'valign': 'vcenter',
        'border': 1, 'border_color': '#4472C4',
    })
    g_head_fmt = workbook.add_format({
        'bold': True, 'font_size': 10, 'font_color': 'white',
        'bg_color': '#4472C4', 'align': 'center',
    })
    g_data_fmt = workbook.add_format({
        'num_format': '#,##0', 'align': 'center', 'bg_color': '#F2F2F2',
    })

    # ---- Title bar ----
    ws_graph.merge_range('A1:C1', 'EVOLUTION CHART', g_title_fmt)
    ws_graph.set_row(0, 28)

    # ---- Dropdowns: Site (row 2) + Indicator (row 3) ----
    ws_graph.write(1, 0, 'Site:', g_label_fmt)
    ws_graph.write(1, 1, 'Total Avg', g_selector_fmt)
    ws_graph.data_validation(1, 1, 1, 1, {'validate': 'list', 'source': dv_site_source_all})

    ws_graph.write(2, 0, 'Indicator:', g_label_fmt)
    ws_graph.write(2, 1, metric_names[0], g_selector_fmt)
    ws_graph.data_validation(2, 1, 2, 1, {'validate': 'list', 'source': dv_metric_source})

    # ---- Helper cells (hidden columns D-E) ----
    # D1: MATCH the selected indicator's header row in Raw Data column A
    g_helper_col = 3
    ws_graph.write_formula(0, g_helper_col,
        "=IFERROR(MATCH($B$3,'Raw Data'!$A:$A,0),1)", dec_num_fmt)
    g_hc = xl_col_to_name(g_helper_col)  # "D"

    # D2: MATCH the selected site within the metric block in Raw Data col B
    ws_graph.write_formula(1, g_helper_col,
        f'=IFERROR(MATCH($B$2,INDIRECT("\'Raw Data\'!$B$\"&${g_hc}$1&\":$B$\"&(${g_hc}$1+{rows_per_tbl})),0),"")',
        dec_num_fmt)

    # D3: MATCH the selected indicator's header row in Network column A
    ws_graph.write_formula(2, g_helper_col,
        "=IFERROR(MATCH($B$3,Network!$A:$A,0),1)", dec_num_fmt)

    # E1: MATCH the selected site within the Network metric block col B
    g_helper_col2 = 4
    g_hc2 = xl_col_to_name(g_helper_col2)  # "E"
    ws_graph.write_formula(0, g_helper_col2,
        f'=IFERROR(MATCH($B$2,INDIRECT("Network!$B$\"&${g_hc}$3&\":$B$\"&(${g_hc}$3+{rows_per_tbl})),0),"")',
        dec_num_fmt)

    # ---- Data table (row 4 = header, rows 5-29 = offsets) ----
    hdr_row_g = 4
    ws_graph.write(hdr_row_g, 0, 'Offset', g_head_fmt)
    ws_graph.write(hdr_row_g, 1, 'Selected', g_head_fmt)
    ws_graph.write(hdr_row_g, 2, 'Network', g_head_fmt)

    graph_sel_cell = "'Graphs'!$B$2"

    for j, off in enumerate(offsets):
        r = hdr_row_g + 1 + j
        ws_graph.write(r, 0, _label_for_offset(off), workbook.add_format({
            'align': 'center', 'bg_color': '#D6E4F0' if off == 0 else '#F2F2F2',
            'bold': off == 0,
        }))

        col_letter = xl_col_to_name(2 + j)

        # Selected site value: INDEX(Raw Data column, header_row + site_offset - 1)
        formula_sel = (
            f'=IFERROR(INDEX(\'Raw Data\'!{col_letter}:${col_letter},'
            f'${g_hc}$1+${g_hc}$2-1),"")'
        )
        ws_graph.write_formula(r, 1, formula_sel, g_data_fmt)

        # Network value: INDEX(Network column, header_row + site_offset - 1)
        formula_net = (
            f'=IFERROR(INDEX(Network!{col_letter}:${col_letter},'
            f'${g_hc}$3+${g_hc2}$1-1),"")'
        )
        ws_graph.write_formula(r, 2, formula_net, g_data_fmt)

    # ---- Chart ----
    last_data_row_g = hdr_row_g + len(offsets)  # 4 + 25 = 29

    evo_chart = workbook.add_chart({'type': 'line'})
    evo_chart.add_series({
        'name': '=Graphs!$B$2',
        'categories': ['Graphs', hdr_row_g + 1, 0, last_data_row_g, 0],
        'values': ['Graphs', hdr_row_g + 1, 1, last_data_row_g, 1],
        'line': {'color': '#4472C4', 'width': 2.5},
        'marker': {'type': 'circle', 'size': 4, 'fill': {'color': '#4472C4'}, 'border': {'color': '#4472C4'}},
    })
    evo_chart.add_series({
        'name': 'All Sites Average',
        'categories': ['Graphs', hdr_row_g + 1, 0, last_data_row_g, 0],
        'values': ['Graphs', hdr_row_g + 1, 2, last_data_row_g, 2],
        'line': {'color': '#ED7D31', 'width': 2, 'dash_type': 'dash'},
        'marker': {'type': 'diamond', 'size': 4, 'fill': {'color': '#ED7D31'}, 'border': {'color': '#ED7D31'}},
    })

    # Dynamic title referencing the indicator dropdown
    evo_chart.set_title({'name': '=Graphs!$B$3'})
    evo_chart.set_y_axis({
        'major_gridlines': {'visible': True, 'line': {'color': '#D9D9D9'}},
        'num_format': '#,##0',
    })
    evo_chart.set_x_axis({
        'label_position': 'low',
        'major_tick_mark': 'outside',
    })
    evo_chart.set_legend({'position': 'bottom', 'font': {'size': 10}})
    evo_chart.set_plotarea({'border': {'none': True}, 'fill': {'color': '#FAFAFA'}})
    evo_chart.set_chartarea({'border': {'color': '#D9D9D9'}})
    evo_chart.set_size({'width': 960, 'height': 480})

    ws_graph.insert_chart('E2', evo_chart)

    # ---- Column widths & hide helper ----
    ws_graph.set_column(0, 0, 12)
    ws_graph.set_column(1, 1, 22)
    ws_graph.set_column(2, 2, 14)
    ws_graph.set_column(g_helper_col, g_helper_col2, None, None, {'hidden': True})

    # =====================================================================
    # Sheet 6: Dashboard (visible)
    # =====================================================================
    ws_dash.set_zoom(95)
    ws_dash.set_tab_color('#1B3A5C')

    # ---- Dashboard-specific formats ----
    dash_title_fmt = workbook.add_format({
        'bold': True, 'font_size': 16, 'font_color': 'white',
        'bg_color': '#1B3A5C', 'align': 'center', 'valign': 'vcenter',
    })
    dash_section_fmt = workbook.add_format({
        'bold': True, 'font_size': 11, 'font_color': 'white',
        'bg_color': '#2E75B6', 'align': 'center', 'valign': 'vcenter',
    })
    dash_col_head_fmt = workbook.add_format({
        'bold': True, 'font_size': 10, 'font_color': 'white',
        'bg_color': '#4472C4', 'align': 'center', 'text_wrap': True,
    })
    dash_kpi_fmt = workbook.add_format({
        'bold': True, 'font_size': 10, 'bg_color': '#F2F2F2',
        'left': 2, 'left_color': '#4472C4',
    })
    dash_computed_fmt = workbook.add_format({
        'bold': True, 'font_size': 10, 'bg_color': '#D6E4F0',
        'left': 2, 'left_color': '#4472C4', 'italic': True,
    })
    dash_total_label = workbook.add_format({
        'bold': True, 'font_size': 10, 'bg_color': '#BDD7EE',
        'left': 2, 'left_color': '#2E75B6',
    })
    dash_result_label = workbook.add_format({
        'bold': True, 'font_size': 11, 'font_color': 'white',
        'bg_color': '#1B3A5C', 'left': 2, 'left_color': '#F4A300',
    })

    # Value formats (light gray bg for regular data cells)
    d_num = workbook.add_format({'num_format': '#,##0', 'bg_color': '#F2F2F2', 'align': 'center'})
    d_dec = workbook.add_format({'num_format': '#,##0.0', 'bg_color': '#F2F2F2', 'align': 'center'})
    d_dollar = workbook.add_format({'num_format': '$#,##0', 'bg_color': '#F2F2F2', 'align': 'center'})
    d_pct = workbook.add_format({'num_format': '0.0%', 'bg_color': '#F2F2F2', 'align': 'center'})
    d_evo_pct = workbook.add_format({'num_format': '+0.0%;-0.0%;0.0%', 'italic': True, 'bg_color': '#F2F2F2', 'align': 'center'})
    d_evo_abs = workbook.add_format({'num_format': '+0.0;-0.0;0.0', 'italic': True, 'bg_color': '#F2F2F2', 'align': 'center'})
    d_comp_dec = workbook.add_format({'num_format': '#,##0.0', 'bg_color': '#D6E4F0', 'italic': True, 'align': 'center'})
    d_comp_pct = workbook.add_format({'num_format': '+0.0%;-0.0%;0.0%', 'bg_color': '#D6E4F0', 'italic': True, 'align': 'center'})
    d_total_dollar = workbook.add_format({'num_format': '$#,##0', 'bold': True, 'bg_color': '#BDD7EE', 'align': 'center'})
    d_total_pct = workbook.add_format({'num_format': '+0.0%;-0.0%;0.0%', 'bold': True, 'italic': True, 'bg_color': '#BDD7EE', 'align': 'center'})
    d_result_dollar = workbook.add_format({'num_format': '$#,##0', 'bold': True, 'font_color': 'white', 'bg_color': '#1B3A5C', 'align': 'center'})
    d_result_pct = workbook.add_format({'num_format': '+0.0%;-0.0%;0.0%', 'bold': True, 'font_color': 'white', 'bg_color': '#1B3A5C', 'align': 'center'})

    # ---- Title ----
    ws_dash.merge_range('E1:J1', 'VEHICLE DELIVERY IMPACT', dash_title_fmt)

    # ---- Site selector ----
    ws_dash.write(2, 0, 'Site:', unit_label_fmt)
    ws_dash.write(2, 1, 'Total Avg', selector_value_fmt)
    ws_dash.data_validation(2, 1, 2, 1, {'validate': 'list', 'source': dv_site_source_all})

    dash_sel_cell = "'Dashboard'!$B$3"

    # Hidden helper columns start at K (col 10)
    helper_col_start = 10
    net_helper_col_start = helper_col_start + len(offsets)  # Network helpers right after Raw Data helpers

    # ---- Metric writer function ----
    def _write_dash_metric(row, metric_name, raw_start, val_fmt, vs_fmt='pct', lbl_fmt=None):
        """Write a dashboard metric row with hidden helpers, averages, evolution, and network comparison."""
        ws_dash.write(row, 4, metric_name, lbl_fmt or dash_kpi_fmt)
        data_row_start = raw_start + 2
        data_row_end = raw_start + rows_per_tbl
        # Hidden helper columns: pull each offset value from Raw Data for the selected site
        for j in range(len(offsets)):
            col = helper_col_start + j
            cd = xl_col_to_name(2 + j)
            formula = (
                f"=IFERROR(INDEX('Raw Data'!{cd}${data_row_start}:{cd}${data_row_end},"
                f"MATCH({dash_sel_cell},'Raw Data'!$B${data_row_start}:$B${data_row_end},0)),\"\")"
            )
            ws_dash.write_formula(row, col, formula, val_fmt)
        # Hidden helper columns: pull each offset value from Network for the selected site
        for j in range(len(offsets)):
            col = net_helper_col_start + j
            cd = xl_col_to_name(2 + j)
            formula = (
                f"=IFERROR(INDEX(Network!{cd}${data_row_start}:{cd}${data_row_end},"
                f"MATCH({dash_sel_cell},Network!$B${data_row_start}:$B${data_row_end},0)),\"\")"
            )
            ws_dash.write_formula(row, col, formula, val_fmt)
        pre_s = xl_rowcol_to_cell(row, helper_col_start)
        pre_e = xl_rowcol_to_cell(row, helper_col_start + 11)
        post_s = xl_rowcol_to_cell(row, helper_col_start + 12)
        post_e = xl_rowcol_to_cell(row, helper_col_start + 24)
        # 12M Avg Before Vehicle
        ws_dash.write_formula(row, 5, f'=AVERAGE({pre_s}:{pre_e})', val_fmt)
        # 12M Avg After Vehicle
        ws_dash.write_formula(row, 6, f'=AVERAGE({post_s}:{post_e})', val_fmt)
        # Evolution
        r1 = row + 1
        if vs_fmt == 'pct':
            ws_dash.write_formula(row, 7, f'=IF($F${r1}<>0,$G${r1}/$F${r1}-1,"")', d_evo_pct)
        else:
            ws_dash.write_formula(row, 7, f'=IF($F${r1}<>"",$G${r1}-$F${r1},"")', d_evo_abs)
        # All Sites Average (post-delivery period from Network helpers)
        net_post_s = xl_rowcol_to_cell(row, net_helper_col_start + 12)
        net_post_e = xl_rowcol_to_cell(row, net_helper_col_start + 24)
        ws_dash.write_formula(row, 8, f'=IFERROR(AVERAGE({net_post_s}:{net_post_e}),"")', val_fmt)
        # vs All Sites
        if vs_fmt == 'pct':
            ws_dash.write_formula(row, 9, f'=IF($I${r1}<>0,$G${r1}/$I${r1}-1,"")', d_evo_pct)
        else:
            ws_dash.write_formula(row, 9, f'=IF($I${r1}<>"",$G${r1}-$I${r1},"")', d_evo_abs)

    # ---- Table positions (Raw Data & Network — identical layout) ----
    rows_per_table = rows_per_tbl
    spacing = 2
    sales_mo_start = 0
    sales_day_start = sales_mo_start + rows_per_table + spacing
    profit_start = sales_day_start + rows_per_table + spacing
    closed_start = profit_start + rows_per_table + spacing
    vehicles_start = closed_start + rows_per_table + spacing
    operators_start = vehicles_start + rows_per_table + spacing
    overwaste_start = operators_start + rows_per_table + spacing
    benef_start = overwaste_start + rows_per_table + spacing
    pnl_inc_sales_start = benef_start + rows_per_table + spacing
    pnl_inc_wins_start = pnl_inc_sales_start + rows_per_table + spacing
    pnl_salary_start = pnl_inc_wins_start + rows_per_table + spacing
    pnl_production_start = pnl_salary_start + rows_per_table + spacing
    pnl_delivery_start = pnl_production_start + rows_per_table + spacing
    pnl_contribution_start = pnl_delivery_start + rows_per_table + spacing
    pnl_other_start = pnl_contribution_start + rows_per_table + spacing
    hod_pct_start = pnl_other_start + rows_per_table + spacing
    ent_salary_start = hod_pct_start + rows_per_table + spacing
    bvd_start = ent_salary_start + rows_per_table + spacing

    # ==================================================================================================================================
    # SECTION 1 – OPERATIONAL PERFORMANCE
    # ==================================================================
    ws_dash.merge_range(3, 4, 3, 9, 'OPERATIONAL PERFORMANCE', dash_section_fmt)

    ws_dash.write(4, 4, 'KPI', dash_col_head_fmt)
    ws_dash.write(4, 5, '12M Avg\nBefore Vehicle', dash_col_head_fmt)
    ws_dash.write(4, 6, '12M Avg\nAfter Vehicle', dash_col_head_fmt)
    ws_dash.write(4, 7, 'Evolution', dash_col_head_fmt)
    ws_dash.write(4, 8, 'All Sites Avg\n(M0 to M+12)', dash_col_head_fmt)
    ws_dash.write(4, 9, 'vs All Sites', dash_col_head_fmt)

    # Row 5: Sales exc. WinS (bottles/month)
    _write_dash_metric(5, 'Sales exc. WinS (bottles/month)', sales_mo_start, d_num)
    # Row 6: Sales exc. WinS (bottles/day)
    _write_dash_metric(6, 'Sales exc. WinS (bottles/day)', sales_day_start, d_dec)
    # Row 7: HOD Sales (%)
    _write_dash_metric(7, 'HOD Sales (%)', hod_pct_start, d_pct)
    # Row 8: Closed days / month
    _write_dash_metric(8, 'Closed days / month', closed_start, d_dec)
    # Row 9: Number of vehicles
    _write_dash_metric(9, 'Number of vehicles', vehicles_start, d_dec, 'abs')
    # Row 10: Number of operators
    _write_dash_metric(10, 'Number of operators', operators_start, d_dec, 'abs')

    # Row 11: Bottles / vehicle / day (inc. WinS, from dedicated table)
    _write_dash_metric(11, 'Bottles / vehicle / day', bvd_start, d_dec)

    # Row 12: Over waste (%)
    _write_dash_metric(12, 'Over waste (%)', overwaste_start, d_pct)
    # Row 13: Profit (USD)
    _write_dash_metric(13, 'Profit (USD)', profit_start, d_dollar)
    # Row 14: Beneficiaries
    _write_dash_metric(14, 'Beneficiaries', benef_start, d_num)

    # Row 15: Total Beneficiaries (SUM at M-1 pre / M+12 post, only sites with M+12 data)
    total_benef_pre = 0
    total_benef_post = 0
    for s in sites:
        m0 = m0_month_by_site[s]
        mm_post = m0 + relativedelta(months=12)
        b_post = get_beneficiaries(s, mm_post)
        if b_post is None:
            continue
        total_benef_post += b_post
        mm_pre = m0 + relativedelta(months=-1)
        b_pre = get_beneficiaries(s, mm_pre)
        if b_pre is not None:
            total_benef_pre += b_pre

    ws_dash.write(15, 4, 'Total Beneficiaries', dash_kpi_fmt)
    ws_dash.write(15, 5, total_benef_pre, d_num)       # M-1
    ws_dash.write(15, 6, total_benef_post, d_num)       # M+12
    if total_benef_pre:
        ws_dash.write(15, 7, total_benef_post / total_benef_pre - 1, d_evo_pct)
    else:
        ws_dash.write(15, 7, '', d_evo_pct)
    ws_dash.write(15, 8, '', d_num)      # No network
    ws_dash.write(15, 9, '', d_evo_pct)  # No network

    # ==================================================================
    # SECTION 2 – PROFIT & LOSS (USD)
    # ==================================================================
    ws_dash.merge_range(17, 4, 17, 9, 'PROFIT & LOSS (USD)', dash_section_fmt)

    ws_dash.write(18, 4, 'Category', dash_col_head_fmt)
    ws_dash.write(18, 5, '12M Avg\nBefore Vehicle', dash_col_head_fmt)
    ws_dash.write(18, 6, '12M Avg\nAfter Vehicle', dash_col_head_fmt)
    ws_dash.write(18, 7, 'Evolution', dash_col_head_fmt)
    ws_dash.write(18, 8, 'All Sites Avg\n(M0 to M+12)', dash_col_head_fmt)
    ws_dash.write(18, 9, 'vs All Sites', dash_col_head_fmt)

    # Revenue lines
    _write_dash_metric(19, 'Sales Revenue', pnl_inc_sales_start, d_dollar)
    _write_dash_metric(20, 'WinS Revenue', pnl_inc_wins_start, d_dollar)

    # Row 21: Total Revenue
    ws_dash.write(21, 4, 'Total Revenue', dash_total_label)
    ws_dash.write_formula(21, 5, '=$F$20+$F$21', d_total_dollar)
    ws_dash.write_formula(21, 6, '=$G$20+$G$21', d_total_dollar)
    ws_dash.write_formula(21, 7, '=IF($F$22<>0,$G$22/$F$22-1,"")', d_total_pct)
    ws_dash.write_formula(21, 8, '=$I$20+$I$21', d_total_dollar)
    ws_dash.write_formula(21, 9, '=IF($I$22<>0,$G$22/$I$22-1,"")', d_total_pct)

    # Expense lines
    _write_dash_metric(22, 'Salary', pnl_salary_start, d_dollar)
    _write_dash_metric(23, 'Production', pnl_production_start, d_dollar)
    _write_dash_metric(24, 'Delivery', pnl_delivery_start, d_dollar)
    _write_dash_metric(25, 'Contribution', pnl_contribution_start, d_dollar)
    _write_dash_metric(26, 'Other', pnl_other_start, d_dollar)

    # Row 27: Total Expenses
    ws_dash.write(27, 4, 'Total Expenses', dash_total_label)
    ws_dash.write_formula(27, 5, '=SUM($F$23:$F$27)', d_total_dollar)
    ws_dash.write_formula(27, 6, '=SUM($G$23:$G$27)', d_total_dollar)
    ws_dash.write_formula(27, 7, '=IF($F$28<>0,$G$28/$F$28-1,"")', d_total_pct)
    ws_dash.write_formula(27, 8, '=SUM($I$23:$I$27)', d_total_dollar)
    ws_dash.write_formula(27, 9, '=IF($I$28<>0,$G$28/$I$28-1,"")', d_total_pct)

    # Row 29: Net Result (Total Revenue − Total Expenses)
    ws_dash.write(29, 4, 'Net Result', dash_result_label)
    ws_dash.write_formula(29, 5, '=$F$22-$F$28', d_result_dollar)
    ws_dash.write_formula(29, 6, '=$G$22-$G$28', d_result_dollar)
    ws_dash.write_formula(29, 7, '=IF($F$30<>0,$G$30/$F$30-1,"")', d_result_pct)
    ws_dash.write_formula(29, 8, '=$I$22-$I$28', d_result_dollar)
    ws_dash.write_formula(29, 9, '=IF($I$30<>0,$G$30/$I$30-1,"")', d_result_pct)

    # Row 30: Entrepreneur Income (Net Result + Entrepreneur Salary)
    d_income_label = workbook.add_format({
        'bold': True, 'font_size': 11, 'font_color': 'white',
        'bg_color': '#2E75B6', 'left': 2, 'left_color': '#F4A300',
    })
    d_income_dollar = workbook.add_format({
        'num_format': '$#,##0', 'bold': True, 'font_color': 'white',
        'bg_color': '#2E75B6', 'align': 'center',
    })
    d_income_pct = workbook.add_format({
        'num_format': '+0.0%;-0.0%;0.0%', 'bold': True, 'font_color': 'white',
        'bg_color': '#2E75B6', 'align': 'center',
    })
    ws_dash.write(30, 4, 'Entrepreneur Income', d_income_label)
    # Income = Net Result + Entrepreneur Salary (row 32 = hidden entrepreneur salary)
    ws_dash.write_formula(30, 5, '=$F$30+$F$32', d_income_dollar)
    ws_dash.write_formula(30, 6, '=$G$30+$G$32', d_income_dollar)
    ws_dash.write_formula(30, 7, '=IF($F$31<>0,$G$31/$F$31-1,"")', d_income_pct)
    ws_dash.write_formula(30, 8, '=$I$30+$I$32', d_income_dollar)
    ws_dash.write_formula(30, 9, '=IF($I$31<>0,$G$31/$I$31-1,"")', d_income_pct)

    # Row 31 (hidden): Entrepreneur Salary helper – data from Ref_expenses entrepreneur only
    _write_dash_metric(31, 'Entrepreneur Salary', ent_salary_start, d_dollar)
    ws_dash.set_row(31, None, None, {'hidden': True})

    # ---- Conditional formatting: green / red for Evolution & vs All Sites ----
    green_evo = workbook.add_format({'font_color': '#006100'})
    red_evo = workbook.add_format({'font_color': '#9C0006'})

    for col_idx in (7, 9):  # H and J columns
        # Operations section (rows 5-15)
        ws_dash.conditional_format(5, col_idx, 15, col_idx, {
            'type': 'cell', 'criteria': '>', 'value': 0, 'format': green_evo})
        ws_dash.conditional_format(5, col_idx, 15, col_idx, {
            'type': 'cell', 'criteria': '<', 'value': 0, 'format': red_evo})
        # P&L section (rows 19-31)
        ws_dash.conditional_format(19, col_idx, 31, col_idx, {
            'type': 'cell', 'criteria': '>', 'value': 0, 'format': green_evo})
        ws_dash.conditional_format(19, col_idx, 31, col_idx, {
            'type': 'cell', 'criteria': '<', 'value': 0, 'format': red_evo})

    # ---- Hide helper columns & set widths ----
    ws_dash.set_column(helper_col_start, net_helper_col_start + len(offsets) - 1, None, None, {'hidden': True})

    ws_dash.set_column(0, 0, 12)
    ws_dash.set_column(1, 3, 14)
    ws_dash.set_column(4, 4, 26)
    ws_dash.set_column(5, 6, 17)
    ws_dash.set_column(7, 7, 13)
    ws_dash.set_column(8, 8, 15)
    ws_dash.set_column(9, 9, 13)

    ws_dash.set_row(0, 30)   # Title row
    ws_dash.set_row(3, 22)   # Section header
    ws_dash.set_row(4, 32)   # Column headers
    ws_dash.set_row(17, 22)  # P&L section header
    ws_dash.set_row(18, 32)  # P&L column headers

    # =====================================================================
    # Sheet 7: Instructions (visible, last tab)
    # =====================================================================
    ws_info.set_tab_color('#808080')
    ws_info.set_zoom(100)
    ws_info.set_column(0, 0, 4)
    ws_info.set_column(1, 1, 100)

    i_title = workbook.add_format({
        'bold': True, 'font_size': 16, 'font_color': 'white',
        'bg_color': '#1B3A5C', 'valign': 'vcenter',
    })
    i_h1 = workbook.add_format({
        'bold': True, 'font_size': 13, 'font_color': '#1B3A5C',
        'bottom': 2, 'bottom_color': '#4472C4',
    })
    i_h2 = workbook.add_format({
        'bold': True, 'font_size': 11, 'font_color': '#2E75B6',
    })
    i_txt = workbook.add_format({
        'font_size': 10, 'text_wrap': True, 'valign': 'top',
    })
    i_formula = workbook.add_format({
        'font_size': 10, 'text_wrap': True, 'valign': 'top',
        'bg_color': '#F2F2F2', 'font_name': 'Consolas', 'left': 4, 'left_color': '#4472C4',
    })
    i_bullet = workbook.add_format({
        'font_size': 10, 'text_wrap': True, 'valign': 'top', 'indent': 1,
    })

    r = 0
    ws_info.merge_range(r, 0, r, 1, '  HOW TO READ THIS REPORT', i_title)
    ws_info.set_row(r, 32)
    r += 2

    # --- General methodology ---
    ws_info.write(r, 1, 'General methodology', i_h1); r += 1
    ws_info.write(r, 1,
        'This report measures the impact of delivery vehicle deployment on site performance. '
        'Each site has a vehicle delivery date (M0). All data is aligned relative to that date: '
        'M-12 = 12 months before delivery, M0 = delivery month, M+12 = 12 months after delivery.', i_txt)
    ws_info.set_row(r, 48); r += 2

    ws_info.write(r, 1, 'Aligned data principle', i_h2); r += 1
    ws_info.write(r, 1,
        'Because sites received their vehicle on different calendar dates, we cannot compare raw calendar months. '
        'Instead, each site\'s data is re-indexed around its own M0 (vehicle delivery date). '
        'For example, if site A received a vehicle in Oct 2024, then Oct 2024 = M0, Sep 2024 = M-1, Nov 2024 = M+1. '
        'If site B received it in Dec 2025, then Dec 2025 = M0, Nov 2025 = M-1, Jan 2026 = M+1.', i_txt)
    ws_info.set_row(r, 64); r += 2

    ws_info.write(r, 1, 'Aggregation method: "Total Avg"', i_h2); r += 1
    ws_info.write(r, 1,
        'When "Total Avg" is selected, each offset column (M-12, M-11, ..., M+12) shows the average '
        'across all vehicle sites for that offset. Sites whose M0+offset falls in the future are excluded. '
        f'{", ".join(wave_labels)} show the average within each wave group only.', i_txt)
    ws_info.set_row(r, 48); r += 2

    ws_info.write(r, 1, 'Network average', i_h2); r += 1
    ws_info.write(r, 1,
        'The "All Sites Average" (or "Network") column is computed differently: for each offset, '
        'we resolve each vehicle site\'s M0+offset to an absolute calendar month, look up the network-wide '
        'average for that calendar month (across all sites in the database, not just vehicle sites), '
        'then average those values. This provides a fair comparison baseline.', i_txt)
    ws_info.set_row(r, 64); r += 2

    # --- Dashboard ---
    ws_info.write(r, 1, 'Dashboard tab', i_h1); r += 1
    ws_info.write(r, 1,
        'The Dashboard compares the 12 months before and after vehicle delivery for the selected site or group.', i_txt)
    ws_info.set_row(r, 30); r += 1
    ws_info.write(r, 1, '\u2022  12M Avg Before Delivery = average of values from M-12 to M-1 (12 months pre-vehicle)', i_bullet); r += 1
    ws_info.write(r, 1, '\u2022  12M Avg After Delivery = average of values from M0 to M+12 (13 months including delivery month)', i_bullet); r += 1
    ws_info.write(r, 1, '\u2022  Evolution = percentage change: (After \u00f7 Before) \u2212 1. Green = improvement, Red = degradation.', i_bullet); r += 1
    ws_info.write(r, 1, '\u2022  All Sites Average = network average over the post-delivery period (M0 to M+12)', i_bullet); r += 1
    ws_info.write(r, 1, '\u2022  vs All Sites = percentage difference: (Site After \u00f7 All Sites Avg) \u2212 1', i_bullet); r += 2

    # --- KPI definitions ---
    ws_info.write(r, 1, 'KPI definitions', i_h1); r += 1

    kpis = [
        ('Sales exc. WinS (bottles/month)',
         'Total monthly sales in bottles, excluding bottle-only sales and WinS sales.\nFormula: SUM(Total_Sales \u2212 Bottle_Sales \u2212 WiS_Sales) per site per month.'),
        ('Sales exc. WinS (bottles/day)',
         'Sales per calendar day in the month, excluding WinS.\nFormula: Sales exc. WinS (bottles/month) \u00f7 number of days in the month.'),
        ('HOD Sales (%)',
         'Proportion of sales delivered by Home Operated Delivery out of all non-WinS, non-bottle sales.\n'
         'Formula: Hod_Sales \u00f7 (Total_Sales \u2212 WiS_Sales \u2212 Bottle_Sales).\n'
         'Values range from 0% to 100%. A higher % means more deliveries are done via HOD.'),
        ('Closed days / month',
         'Number of days the site was closed in the month.\nFormula: calendar days in month \u2212 Number_Open_Days.'),
        ('Number of vehicles',
         'Average number of delivery vehicles available at the site for the month (from Indicators table).'),
        ('Number of operators',
         'Average number of delivery operators at the site for the month (from Indicators table).'),
        ('Bottles / vehicle / day',
         'Delivery efficiency per vehicle, including WinS sales (inc. WinS).\n'
         'Formula: (Total_Sales \u2212 Bottle_Sales) \u00f7 days in month \u00f7 Number of vehicles.\n'
         'Unlike Sales exc. WinS (bottles/day), this metric includes WinS to reflect the full delivery load per vehicle.'),
        ('Over waste (%)',
         'Percentage of treated water lost (not sold).\n'
         'Formula: 1 \u2212 (Sales in bottles \u00f7 (Water_Consume \u00f7 20)).\n'
         'Water_Consume is in liters; each bottle = 20L. Result is clamped between 0% and 100%.\n'
         'A lower % is better (less waste).'),
        ('Profit (USD)',
         'Monthly profit converted to USD.\nFormula: (Total_Income \u2212 Total_Expenses) \u00f7 exchange_rate.\n'
         'Expenses include: salary, production, delivery, contribution, investment, technical.'),
        ('Beneficiaries',
         'Number of people served by the site (from Beneficiaries table).\n'
         'Uses AVG aggregation to handle any duplicate records.'),
    ]

    for name, desc in kpis:
        ws_info.write(r, 1, name, i_h2); r += 1
        lines = desc.count('\n') + 1
        ws_info.write(r, 1, desc, i_formula)
        ws_info.set_row(r, max(30, lines * 16)); r += 1

    r += 1

    # --- P&L ---
    ws_info.write(r, 1, 'P&L section', i_h1); r += 1
    ws_info.write(r, 1,
        'All P&L amounts are monthly values converted to USD using the yearly exchange rate. '
        'The same Before/After/Evolution/Network columns apply.', i_txt)
    ws_info.set_row(r, 30); r += 1
    pnl_items = [
        ('Sales Revenue', 'Total_Income \u2212 WiS_Income, converted to USD.'),
        ('WinS Revenue', 'WiS_Income (Water in Schools program income), converted to USD.'),
        ('Total Revenue', 'Sales Revenue + WinS Revenue (computed formula).'),
        ('Salary / Production / Delivery / Contribution / Other',
         'Expenses by category from the Expenses table, converted to USD.\n"Other" = investment + technical categories combined.'),
        ('Total Expenses', 'Sum of all 5 expense categories (computed formula).'),
        ('Net Result', 'Total Revenue \u2212 Total Expenses.'),
        ('Entrepreneur Income', 'Net Result + Entrepreneur Salary (fix + variable salary of the entrepreneur only,\nexcluding operator salaries). Represents the entrepreneur\u2019s total personal income.'),
    ]
    for name, desc in pnl_items:
        ws_info.write(r, 1, name, i_h2); r += 1
        lines = desc.count('\n') + 1
        ws_info.write(r, 1, desc, i_formula)
        ws_info.set_row(r, max(26, lines * 16)); r += 1

    r += 1

    # --- Sheets guide ---
    ws_info.write(r, 1, 'Sheets overview', i_h1); r += 1
    sheets = [
        ('Dashboard', 'Summary view comparing 12 months Before vs After delivery. Select a site or wave from the dropdown.'),
        ('Graphs', 'Evolution chart (M-12 to M+12). Select a site/wave AND an indicator from the dropdowns. '
                   'Shows the selected site vs the network average.'),
        ('Datas', 'Detailed data table for one indicator at a time. Supports filtering by Platform, Advisor, Wave. '
                  'Subtotal rows (Average, Sum) above the header update based on visible rows (autofilter-aware). '
                  'Sites are sorted by vehicle installation date.'),
        ('Raw Data (hidden)', 'All aligned metric tables (16 indicators \u00d7 25 offsets). Used as data source by other sheets.'),
        ('Network (hidden)', 'Network average values for each indicator, used for comparison columns.'),
        ('Vehicle events (hidden)', 'Site list with wave assignments, used for dropdown sources.'),
    ]
    for name, desc in sheets:
        ws_info.write(r, 1, name, i_h2); r += 1
        lines = desc.count('\n') + 1
        ws_info.write(r, 1, desc, i_formula)
        ws_info.set_row(r, max(26, lines * 16)); r += 1


def LaunchExcelVehicleDeliveryImpact(Current_date: date):
    Month = Current_date.month
    Month = ('0' + str(Month)) if Month < 10 else str(Month)
    Year = str(Current_date.year)

    # Define vehicle rollout here: list of (site, vehicle_date)
    # Wave 1 (Oct 2024)
    vehicle_events_wave1 = [
        ('H9', date(2024, 10, 1)),
        ('I3', date(2024, 10, 1)),
        ('K17', date(2024, 10, 1)),
        ('F7', date(2024, 10, 1 )),
        ('M26', date(2024, 10, 1)),
        ('M28', date(2024, 10, 1)),
        ('L21', date(2024, 10, 1)),
        ('H2', date(2024, 10, 1)),
        ('P12', date(2024, 10, 1)),
        ('D4', date(2024, 10, 1)),
    ]
    # Wave 2 (Dec 2025)
    vehicle_events_wave2 = [
        ('M27', date(2025, 12, 1)),
        ('K29', date(2025, 12, 1)),
        ('H15', date(2025, 12, 1)),
        ('I21', date(2025, 12, 1)),
        ('H5', date(2025, 12, 1)),
    ]
    # Wave 3 (Mars 2026)
    vehicle_events_wave3 = [
        ('D6', date(2026, 3, 1)),
        ('O6', date(2026, 3, 1)),
        ('Q21', date(2026, 3, 1)),
        ('R8', date(2026, 3, 1)),
        ('T10', date(2026, 3, 1)),
        ('T8', date(2026, 3, 1)),
        ('O18', date(2026, 3, 1)),
        ('O23', date(2026, 3, 1)),
        ('I10', date(2026, 3, 1)),
        ('Q12', date(2026, 3, 1)),
        ('N18', date(2026, 3, 1)),
        ('J4', date(2026, 3, 1)),
        ('O20', date(2026, 3, 1)),
        ('H33', date(2026, 3, 1)),
        ('G14', date(2026, 3, 1)),
        ('E9', date(2026, 3, 1)),
        ('E19', date(2026, 3, 1)),
        ('R18', date(2026, 3, 1)),
        ('F8', date(2026, 3, 1)),
    ]
    vehicle_events = vehicle_events_wave1 + vehicle_events_wave2 + vehicle_events_wave3

    filepath = tempfile.gettempdir() + '/Vehicle Delivery Impact ' + Year + '-' + Month + '.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    VehicleDeliveryImpact(
        workbook,
        Current_date,
        vehicle_events=vehicle_events,
        vehicle_waves=[vehicle_events_wave1, vehicle_events_wave2, vehicle_events_wave3],
    )
    workbook.close()
    return filepath


if __name__ == '__main__':
    LaunchExcelVehicleDeliveryImpact(date(2026, 1, 1))
