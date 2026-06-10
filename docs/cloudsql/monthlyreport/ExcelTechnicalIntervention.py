import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta, datetime
from calendar import monthrange
import db
import tempfile
from dateutil.relativedelta import *
from monthlyreport.Functionutils import NewCalculTier
from monthlyreport.Functionutils import ListIntervention
from monthlyreport import Graph
from monthlyreport import ExcelSiteAnalysisTechnical

con = db.pool.connect()

'''
Pour info : 
colonne :
start = date de fin d'intervention => end_intervention
plan_date = date de début d'intervention => start_intervention 
interventionDate = date de signalement de l'intervention => problem_date
'''
def DashboardTechnical(Current_date,Date_janv,workbook):
	Name_worksheet = "Technicians"
	worksheet = workbook.add_worksheet(Name_worksheet)
	worksheet.freeze_panes(4, 0)
	worksheet.set_zoom(70)
	Site_format = workbook.add_format({'bg_color':"#DAEEF3",'bold': True,'valign':'vcenter','center_across':True})
	Data_format_YTD = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
	Data_format_month = workbook.add_format({'bg_color':"#00B050",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
	Title_format = workbook.add_format({'bold':True,"font_size":18,"center_across":True,'bg_color':'#FFFF00'})
	Percent_format = workbook.add_format({'num_format': '0%'})
##############EXTRACT DATA###############
	# Get the latest technician for each site based on the latest problem_date
	allSiteData = con.execute("""
		SELECT t.site, s.Platform, t.technician
		FROM technicals t
		JOIN Sites s ON s.Id_Site = t.site
		INNER JOIN (
			SELECT site, MAX(problem_date) AS max_problem_date
			FROM technicals
			GROUP BY site
		) latest ON latest.site = t.site AND latest.max_problem_date = t.problem_date
		WHERE s.Old_Platform <> 'Dead' AND s.Platform <> 'Dead'
		ORDER BY Left(t.site,1),LENGTH(t.site),t.site
	""").fetchall()
	# Get day without production for each site
	allDayNoProd = con.execute("""
		SELECT site, 
			SUM(
				CASE 
					WHEN problem_status = "Can Not Produce" 
					THEN DATEDIFF(end_intervention, start_intervention) 
					ELSE 0 
				END
			) AS day_without_production,
			DATE_FORMAT(problem_date, '%%Y-%%m-01') AS month
		FROM technicals
		WHERE start_intervention >= %s AND start_intervention < %s
		GROUP BY site
	""", (Date_janv, Current_date+relativedelta(months=+1))).fetchall()
	# Count alert levels for each site from samples table
	allAlertLevels = con.execute("""
		SELECT 
			site,
			SUM(CASE WHEN contamination_level_machine = 1 THEN 1 ELSE 0 END) AS level1_machine,
			SUM(CASE WHEN contamination_level_machine = 2 THEN 1 ELSE 0 END) AS level2_machine,
			SUM(CASE WHEN contamination_level_machine = 3 THEN 1 ELSE 0 END) AS level3_machine,
			SUM(CASE WHEN contamination_level_bottle = 1 THEN 1 ELSE 0 END) AS level1_bottle,
			SUM(CASE WHEN contamination_level_bottle = 2 THEN 1 ELSE 0 END) AS level2_bottle,
			SUM(CASE WHEN contamination_level_bottle = 3 THEN 1 ELSE 0 END) AS level3_bottle,
			SUM(CASE WHEN manganese > 0.05 THEN 1 ELSE 0 END) AS manganese_count,
			SUM(CASE WHEN aluminium > 0.2 THEN 1 ELSE 0 END) AS aluminium_count,
			SUM(CASE WHEN turbidity > 2 THEN 1 ELSE 0 END) AS turbidity_count,
			DATE_FORMAT(analysis_date, '%%Y-%%m-01') AS month
		FROM samples
		WHERE analysis_date >= %s AND analysis_date < %s AND type = "Monthly Test"
		GROUP BY site, month
	""", (Date_janv, Current_date+relativedelta(months=+1))).fetchall()

	# Build dynamic intervention list (same taxonomy as SiteAnalysis graph)
	all_interventions = [row[0] for row in con.execute(
		"""
		SELECT DISTINCT tp.problem_category
		FROM technical_problems tp
		JOIN technicals tt ON tt.id = tp.technical_id
		WHERE tt.start_intervention >= %s AND tt.start_intervention < %s
		  AND tp.problem_category IS NOT NULL
		ORDER BY tp.problem_category
		""",
		(Date_janv, Current_date+relativedelta(months=+1))
	).fetchall()]

	# Titles: static YTD block up to intervention families, then dynamic intervention columns, then static monthly block
	titles = [
		("Site", "site", False),
		("Platform", "site", False),
		("Technician", "site", False),
		("Tier", "site", False),
		("Day w/o prod", "ytd", False),
		("Ecoli-coliform TS", "ytd", False),
		("Lev 1 TS", "ytd", True),
		("Lev 2 TS", "ytd", True),
		("Lev 3 TS", "ytd", True),
		("Ecoli-coliform Bot", "ytd", False),
		("Lev 1 Bot", "ytd", True),
		("Lev 2 Bot", "ytd", True),
		("Lev 3 Bot", "ytd", True),
		("Alert chemical", "ytd", False),
		("Manganese", "ytd", True),
		("Aluminium", "ytd", True),
		("Turbidity", "ytd", True),
		("Routine intervention", "ytd", False),
			("Technical intervention", "ytd", False),
		("Tech <24h", "ytd", True),
		("% Tech <24h", "ytd", True),
			("WQ intervention", "ytd", False),
		("WQ <24h", "ytd", True),
		("% WQ <24h", "ytd", True),
	]
	# Precompute intervention counts per site by type for YTD (for dynamic columns)
	counts_ytd_rows = con.execute(
		"""
		SELECT tt.site, tp.problem_category, COUNT(*)
		FROM technical_problems tp
		JOIN technicals tt ON tt.id = tp.technical_id
		WHERE tt.start_intervention >= %s AND tt.start_intervention < %s
		GROUP BY tt.site, tp.problem_category
		""",
		(Date_janv, Current_date+relativedelta(months=+1))
	).fetchall()
	counts_ytd = {}
	totals_by_category = {}
	for site, cat, cnt in counts_ytd_rows:
		counts_ytd.setdefault(site, {})[cat] = cnt
		totals_by_category[cat] = totals_by_category.get(cat, 0) + cnt
	# Sort interventions by most interventions YTD (desc), fallback alphabetical
	interventions_sorted = sorted(all_interventions, key=lambda c: (-totals_by_category.get(c, 0), c))
	# Dynamic intervention columns (YTD counts per type) in sorted order
	ytd_dyn_start = len(titles)
	titles.extend([(intervention, "ytd", False) for intervention in interventions_sorted])
	ytd_dyn_end = len(titles) - 1
	# Monthly static block
	titles.extend([
		("Day w/o prod", "monthly", False),
		("Ecoli-coliform TS", "monthly", False),
		("Lev 1 TS", "monthly", True),
		("Lev 2 TS", "monthly", True),
		("Lev 3 TS", "monthly", True),
		("Ecoli-coliform Bot", "monthly", False),
		("Lev 1 Bot", "monthly", True),
		("Lev 2 Bot", "monthly", True),
		("Lev 3 Bot", "monthly", True),
		("Alert chemical", "monthly", False),
		("Manganese", "monthly", True),
		("Aluminium", "monthly", True),
		("Turbidity", "monthly", True),
		("Routine intervention", "monthly", False),
		("Technical intervention", "monthly", False),
		("Tech <24h", "monthly", True),
		("% Tech <24h", "monthly", True),
		("WQ intervention", "monthly", False),
		("WQ <24h", "monthly", True),
		("% WQ <24h", "monthly", True)
	])

	def find_col(col_title, fmt_type):
		for idx, (t, ft, _) in enumerate(titles):
			if t == col_title and ft == fmt_type:
				return idx
		return None

	# Column indexes used for writing Excel formulas in YTD % columns
	ytd_tech_total_col = find_col("Technical intervention", "ytd")
	ytd_tech_24h_col = find_col("Tech <24h", "ytd")
	ytd_tech_pct_col = find_col("% Tech <24h", "ytd")
	ytd_wq_total_col = find_col("WQ intervention", "ytd")
	ytd_wq_24h_col = find_col("WQ <24h", "ytd")
	ytd_wq_pct_col = find_col("% WQ <24h", "ytd")
	# Dynamic intervention columns (Monthly counts per type) in same sorted order
	monthly_dyn_start = len(titles)
	titles.extend([(intervention, "monthly", False) for intervention in interventions_sorted])
	monthly_dyn_end = len(titles) - 1
	for idx, (title, fmt_type, hidden) in enumerate(titles):
		if fmt_type == "ytd":
			fmt = Data_format_YTD
		elif fmt_type == "monthly":
			fmt = Data_format_month
		else:
			fmt = Site_format
		worksheet.write(3, idx, title, fmt)
		if hidden:
			worksheet.set_column(idx, idx, None, None, {'level':1,'hidden':True})
		else:
			worksheet.set_column(idx, idx, max(len(title), 15))
	worksheet.set_row(3, 30)  # Set row height for header row (index 3)
	ytd_columns = [i for i, (_, fmt_type, _) in enumerate(titles) if fmt_type == "ytd"]
	monthly_columns = [i for i, (_, fmt_type, _) in enumerate(titles) if fmt_type == "monthly"]
	ColumnENDYTD = ytd_columns[-1] if ytd_columns else 0
	ColumnENDMonthly = monthly_columns[-1] if monthly_columns else 0
	worksheet.merge_range(0, 4, 0, ColumnENDYTD, "YTD", Title_format)
	worksheet.merge_range(0, ColumnENDYTD + 1, 0, ColumnENDMonthly, "Monthly", Title_format)
	# Group/collapse dynamic columns by default
	if ytd_dyn_start <= ytd_dyn_end:
		for c in range(ytd_dyn_start, ytd_dyn_end + 1):
			width = max(len(titles[c][0]), 15)
			worksheet.set_column(c, c, width, None, {'level': 1, 'hidden': True})
	if monthly_dyn_start <= monthly_dyn_end:
		for c in range(monthly_dyn_start, monthly_dyn_end + 1):
			width = max(len(titles[c][0]), 15)
			worksheet.set_column(c, c, width, None, {'level': 1, 'hidden': True})

	# Build dictionaries
	day_no_prod_dict = {}
	for row in allDayNoProd:
		site = row[0]; day_wo_prod = row[1] or 0; month = row[2]
		day_no_prod_dict.setdefault(site, {})[month] = day_wo_prod

	def get_month_str(dt):
		return dt.strftime('%Y-%m-01')

	alert_level_dict = {}
	for row in allAlertLevels:
		site, *levels, month = row
		alert_level_dict.setdefault(site, {})[month] = {
			'level1_machine': levels[0] or 0,
			'level2_machine': levels[1] or 0,
			'level3_machine': levels[2] or 0,
			'level1_bottle': levels[3] or 0,
			'level2_bottle': levels[4] or 0,
			'level3_bottle': levels[5] or 0,
			'manganese_count': levels[6] or 0,
			'aluminium_count': levels[7] or 0,
			'turbidity_count': levels[8] or 0,
		}

	ytd_months = []
	tmp_date = Date_janv
	while tmp_date <= Current_date:
		ytd_months.append(get_month_str(tmp_date))
		tmp_date += relativedelta(months=1)
	current_month_str = get_month_str(Current_date)

	def sum_alerts(site, key):
		return sum(alert_level_dict.get(site, {}).get(m, {}).get(key, 0) for m in ytd_months)
	def alert_month(site, key):
		return alert_level_dict.get(site, {}).get(current_month_str, {}).get(key, 0)
	def alert_month_multi(site, keys):
		return sum(alert_month(site, k) for k in keys)
	def count_interventions(site, intervention_list, start_date, end_date):
		return sum(1 for s, cat, dt in con.execute("""SELECT site, tp.problem_category, start_intervention
		   FROM technical_problems tp JOIN technicals tt ON tp.technical_id = tt.id
		   WHERE tt.start_intervention >= %s AND tt.start_intervention < %s AND site = %s""",
		   (start_date, end_date, site)).fetchall() if s == site and cat in intervention_list)

	TechnicalInterventionPlanned, TechnicalInterventionUnplanned, QualityIntervention = ListIntervention()[3], ListIntervention()[4], ListIntervention()[1]

	# --- YTD % interventions completed within 24h (J or J+1) ---
	# Definition: DATE(start_intervention) is the intervention day; DATE(problem_date) is the incident start day.
	# Count as <24h if the intervention day is the same day (J) or the next day (J+1).
	def _in_clause(values):
		values = list(values)
		if not values:
			return "(NULL)", []
		return "(" + ",".join(["%s"] * len(values)) + ")", values

	tech_in, tech_params = _in_clause(TechnicalInterventionUnplanned)
	wq_in, wq_params = _in_clause(QualityIntervention)
	within_24h_rows = con.execute(
		f"""
		SELECT
			tt.site,
			SUM(CASE WHEN tp.problem_category IN {tech_in} THEN 1 ELSE 0 END) AS tech_total,
			SUM(CASE WHEN tp.problem_category IN {tech_in}
					  AND DATEDIFF(DATE(tt.start_intervention), DATE(tt.problem_date)) BETWEEN 0 AND 1
				 THEN 1 ELSE 0 END) AS tech_24h,
			SUM(CASE WHEN tp.problem_category IN {wq_in} THEN 1 ELSE 0 END) AS wq_total,
			SUM(CASE WHEN tp.problem_category IN {wq_in}
					  AND DATEDIFF(DATE(tt.start_intervention), DATE(tt.problem_date)) BETWEEN 0 AND 1
				 THEN 1 ELSE 0 END) AS wq_24h
		FROM technical_problems tp
		JOIN technicals tt ON tt.id = tp.technical_id
		WHERE tt.start_intervention >= %s AND tt.start_intervention < %s
		GROUP BY tt.site
		""",
		tech_params + tech_params + wq_params + wq_params + [Date_janv, Current_date + relativedelta(months=+1)]
	).fetchall()
	within_24h_by_site = {
		site: {
			'tech_total': tech_total or 0,
			'tech_24h': tech_24h or 0,
			'wq_total': wq_total or 0,
			'wq_24h': wq_24h or 0,
		}
		for site, tech_total, tech_24h, wq_total, wq_24h in within_24h_rows
	}

	# Precompute intervention counts per site by type for Monthly (for dynamic columns)
	counts_month_rows = con.execute(
		"""
		SELECT tt.site, tp.problem_category, COUNT(*)
		FROM technical_problems tp
		JOIN technicals tt ON tt.id = tp.technical_id
		WHERE tt.start_intervention >= %s AND tt.start_intervention < %s
		GROUP BY tt.site, tp.problem_category
		""",
		(Current_date, Current_date+relativedelta(months=+1))
	).fetchall()
	counts_month = {}
	for site, cat, cnt in counts_month_rows:
		counts_month.setdefault(site, {})[cat] = cnt
	Tier_List = NewCalculTier(Current_date)[0]

	FirstDataRow = 4
	for row_idx, row in enumerate(allSiteData):
		site, platform, technician = row
		data = []
		tier = next((t[1] for t in Tier_List if t[0] == site), "")
		data.extend([site, platform, technician, tier])
		ytd_total = sum(day_no_prod_dict.get(site, {}).get(m, 0) for m in ytd_months)
		data.append(ytd_total)
		level1_machine_ytd = sum_alerts(site, 'level1_machine'); level2_machine_ytd = sum_alerts(site, 'level2_machine'); level3_machine_ytd = sum_alerts(site, 'level3_machine')
		ecoli_coliform_ts_ytd = level1_machine_ytd + level2_machine_ytd + level3_machine_ytd
		data.extend([ecoli_coliform_ts_ytd, level1_machine_ytd, level2_machine_ytd, level3_machine_ytd])
		level1_bottle_ytd = sum_alerts(site, 'level1_bottle'); level2_bottle_ytd = sum_alerts(site, 'level2_bottle'); level3_bottle_ytd = sum_alerts(site, 'level3_bottle')
		ecoli_coliform_bot_ytd = level1_bottle_ytd + level2_bottle_ytd + level3_bottle_ytd
		data.extend([ecoli_coliform_bot_ytd, level1_bottle_ytd, level2_bottle_ytd, level3_bottle_ytd])
		manganese_ytd = sum_alerts(site, 'manganese_count'); aluminium_ytd = sum_alerts(site, 'aluminium_count'); turbidity_ytd = sum_alerts(site, 'turbidity_count')
		alert_chemical_ytd = manganese_ytd + aluminium_ytd + turbidity_ytd
		data.extend([alert_chemical_ytd, manganese_ytd, aluminium_ytd, turbidity_ytd])
		routine_ytd = count_interventions(site, TechnicalInterventionPlanned, Date_janv, Current_date+ relativedelta(months=+1))
		m = within_24h_by_site.get(site, {'tech_total': 0, 'tech_24h': 0, 'wq_total': 0, 'wq_24h': 0})
		# Use precomputed totals for unplanned technical and WQ to avoid per-site SQL loops.
		technical_ytd = m.get('tech_total', 0)
		quality_ytd = m.get('wq_total', 0)
		tech_24h_cnt = m.get('tech_24h', 0)
		wq_24h_cnt = m.get('wq_24h', 0)
		# Percent columns are written as Excel formulas so users can inspect the calculation.
		data.extend([routine_ytd, technical_ytd, tech_24h_cnt, "", quality_ytd, wq_24h_cnt, ""])
		# Dynamic YTD counts for each intervention type (sorted)
		for cat in interventions_sorted:
			data.append(counts_ytd.get(site, {}).get(cat, 0))
		monthly_val = day_no_prod_dict.get(site, {}).get(current_month_str, 0)
		data.append(monthly_val)
		ecoli_coliform_ts_month = alert_month_multi(site, ['level1_machine','level2_machine','level3_machine'])
		data.append(ecoli_coliform_ts_month)
		data.append(alert_month(site,'level1_machine'))
		data.append(alert_month(site,'level2_machine'))
		data.append(alert_month(site,'level3_machine'))
		ecoli_coliform_bot_month = alert_month_multi(site, ['level1_bottle','level2_bottle','level3_bottle'])
		data.append(ecoli_coliform_bot_month)
		data.append(alert_month(site,'level1_bottle'))
		data.append(alert_month(site,'level2_bottle'))
		data.append(alert_month(site,'level3_bottle'))
		alert_chemical_month = alert_month_multi(site, ['manganese_count','aluminium_count','turbidity_count'])
		data.append(alert_chemical_month)
		data.append(alert_month(site,'manganese_count'))
		data.append(alert_month(site,'aluminium_count'))
		data.append(alert_month(site,'turbidity_count'))
		routine_month = count_interventions(site, TechnicalInterventionPlanned, Current_date, Current_date+relativedelta(months=1))
		technical_month = count_interventions(site, TechnicalInterventionUnplanned, Current_date, Current_date+relativedelta(months=1))
		quality_month = count_interventions(site, QualityIntervention, Current_date, Current_date+relativedelta(months=1))
		# %<24h is only counted in YTD; keep monthly columns blank for consistent layout
		data.extend([routine_month, technical_month, "", "", quality_month, "", ""])
		# Dynamic Monthly counts for each intervention type (sorted)
		for cat in interventions_sorted:
			data.append(counts_month.get(site, {}).get(cat, 0))
		for i, val in enumerate(data):
			write_row = FirstDataRow + row_idx
			# Write YTD % columns as formulas: =IFERROR(numerator/denominator,"")
			if i == ytd_tech_pct_col and ytd_tech_24h_col is not None and ytd_tech_total_col is not None:
				num_cell = xl_rowcol_to_cell(write_row, ytd_tech_24h_col)
				den_cell = xl_rowcol_to_cell(write_row, ytd_tech_total_col)
				worksheet.write_formula(write_row, i, f"=IFERROR({num_cell}/{den_cell},\"\")", Percent_format)
				continue
			if i == ytd_wq_pct_col and ytd_wq_24h_col is not None and ytd_wq_total_col is not None:
				num_cell = xl_rowcol_to_cell(write_row, ytd_wq_24h_col)
				den_cell = xl_rowcol_to_cell(write_row, ytd_wq_total_col)
				worksheet.write_formula(write_row, i, f"=IFERROR({num_cell}/{den_cell},\"\")", Percent_format)
				continue
			# For monthly % columns we keep blank (metric is YTD only)
			if i < len(titles) and titles[i][1] == "monthly" and titles[i][0] in ("% Tech <24h", "% WQ <24h"):
				worksheet.write(write_row, i, "")
				continue
			worksheet.write(write_row, i, val)

	# --- Conditional formatting for alert columns ---
	red_bg_format = workbook.add_format({'bg_color': '#FCD5B4'})
	grey_bg_format = workbook.add_format({'bg_color': '#F2F2F2', 'font_color': '#F2F2F2'})

	# Define which columns to apply conditional formatting to, by title
	Title_column_to_format = (
		"Day w/o prod",
		"Ecoli-coliform TS",
		"Lev 1 TS",
		"Lev 2 TS",
		"Lev 3 TS",
		"Ecoli-coliform Bot",
		"Lev 1 Bot",
		"Lev 2 Bot",
		"Lev 3 Bot",
		"Alert chemical",
		"Manganese",
		"Aluminium",
		"Turbidity"
	)
	# Find column indexes for those titles (both YTD and monthly)
	column_to_format = [
		idx for idx, (title, _, _) in enumerate(titles)
		if title in Title_column_to_format
	]

	num_rows = len(allSiteData)
	start_row = FirstDataRow
	end_row = FirstDataRow + num_rows - 1

	# Apply conditional formatting: highlight cells > 0 in red, 0 in grey
	for col in column_to_format:
		cell_range = xl_range(start_row, col, end_row, col)
		worksheet.conditional_format(cell_range, {
			'type': 'cell',
			'criteria': '>',
			'value': 0,
			'format': red_bg_format
		})
		

	# --- Apply grey bg/font for ALL columns if value is 0 ---
	num_cols = len(titles)
	
	# Add SUM and AVERAGE formulas for each data column (after "Site", "Platform", "Technician", "Tier")
	Number_bold_format = workbook.add_format({'num_format': '#,##0', 'bold': True})
	Number_avg_format = workbook.add_format({'num_format': '#,##0.00', 'italic': True})
	Percent_avg_format = workbook.add_format({'num_format': '0%', 'italic': True})

	# Data columns start after the first 4 columns
	data_col_start = 4
	data_col_end = len(titles) - 1
	num_data_rows = len(allSiteData)
	first_data_row = FirstDataRow
	last_data_row = FirstDataRow + num_data_rows - 1

	for col in range(data_col_start, data_col_end + 1):
		is_percent_col = titles[col][0] in ("% Tech <24h", "% WQ <24h")
		# SUM in row 2 (index 1): not meaningful for percentages
		if not is_percent_col:
			worksheet.write_formula(1, col,
				"SUBTOTAL(9,{}:{})".format(
					xl_rowcol_to_cell(first_data_row, col),
					xl_rowcol_to_cell(last_data_row, col)
				),
				Number_bold_format
			)
		else:
			worksheet.write(1, col, "")
		# AVERAGE in row 3 (index 2)
		worksheet.write_formula(2, col,
			"SUBTOTAL(1,{}:{})".format(
				xl_rowcol_to_cell(first_data_row, col),
				xl_rowcol_to_cell(last_data_row, col)
			),
			Percent_avg_format if is_percent_col else Number_avg_format
		)

	# Optionally, add autofilter for all columns
	worksheet.autofilter(3, 0, last_data_row, data_col_end)

def EquipmentAge(Current_date,workbook):

	bold_format = workbook.add_format({'bold':True,'num_format':'# ##0','valign':'vcenter','center_across':True})
	yellow_bg_format = workbook.add_format({'bg_color':"#FFFF00",'num_format':'# ##0','valign':'vcenter','center_across':True})
	red_bg_format = workbook.add_format({'bg_color':"#C0504D",'num_format':'# ##0','valign':'vcenter','center_across':True})
	green_bg_format = workbook.add_format({'bg_color':"#92D050",'num_format':'# ##0','valign':'vcenter','center_across':True})
	
	
	ExtractDateEquipment = con.execute("""
		SELECT a.site, s.Platform,
		CASE WHEN YEAR(date_change_sand_filter_tank) < 2001 THEN MIN(Sales.Month) ELSE date_change_sand_filter_tank END AS sand_change,
		CASE WHEN YEAR(date_change_ac_filter_tank) < 2001 THEN MIN(Sales.Month) ELSE date_change_ac_filter_tank END AS ac_change,
		CASE 
        	WHEN uv_lamp = '' OR uv_lamp IS NULL THEN 'unknown'
        	ELSE uv_lamp 
    	END AS uv_lamp,
		CASE WHEN YEAR(date_change_uv_lamp) < 2001 OR date_change_uv_lamp = '' THEN MIN(Sales.Month) ELSE date_change_uv_lamp END AS uv_change,
		CASE WHEN YEAR(date_change_uv_controller) < 2001 OR date_change_uv_controller = '' THEN MIN(Sales.Month) ELSE date_change_uv_controller END AS controller_change,
		uv_controller, uv_controller_condition, stabilizer,
		CASE WHEN YEAR(last_change_stabilizer) < 2001 OR last_change_stabilizer = '' THEN MIN(Sales.Month) ELSE last_change_stabilizer END AS stabilizer_change,
		main_source_of_water
		FROM assessments a
		JOIN Sales ON a.site = Sales.Id_Site
		JOIN Sites s ON s.Id_Site = a.site
		WHERE s.Old_Platform <> 'Dead' AND s.Platform <> 'Dead'
		AND a.date_form = (
			SELECT MAX(date_form) FROM assessments WHERE site = a.site AND date_form <= %s
		)
		GROUP BY a.site
		ORDER BY a.site
	""", (Current_date + relativedelta(months=1),)).fetchall()

	# Normalize uv_lamp values to include a synthetic 'unknown' bucket (blank or NULL)
	UV_lamp_type = con.execute("""
		SELECT DISTINCT CASE WHEN uv_lamp IS NULL OR uv_lamp = '' THEN 'unknown' ELSE uv_lamp END AS uv_lamp
		FROM assessments
		ORDER BY uv_lamp
	""").fetchall()
	# Safety: ensure 'unknown' key exists even if no assessment currently maps (future-proof)
	# Water source categories (normalized like UV lamp)
	water_source_types = con.execute("""
		SELECT DISTINCT CASE WHEN main_source_of_water IS NULL OR main_source_of_water = '' THEN 'unknown' ELSE main_source_of_water END AS water_source
		FROM assessments
		ORDER BY water_source
	""").fetchall()

	Name_worksheet = "Equipment"
	worksheet = workbook.add_worksheet(Name_worksheet)
	worksheet.set_column(0,6,20)
	worksheet.write(0,0,"Equipement Age",workbook.add_format({'bold':True}))

	sand_media_dict = {'<5 years':[0,green_bg_format],'5-10 years':[0,yellow_bg_format],'>10 years':[0,red_bg_format],'Total':[0,bold_format]}
	AC_media_dict = {'<3 years':[0,green_bg_format],'3-4 years':[0,yellow_bg_format],'>4 years':[0,red_bg_format],'Total':[0,bold_format]}
	UV_lamp_type_dict = {t[0]: 0 for t in UV_lamp_type}
	if 'unknown' not in UV_lamp_type_dict:
		UV_lamp_type_dict['unknown'] = 0
	UV_lamp_type_dict['Total'] = 0
	water_source_dict = {t[0]: 0 for t in water_source_types}
	if 'unknown' not in water_source_dict:
		water_source_dict['unknown'] = 0
	water_source_dict['Total'] = 0
	
	UV_lamp_age_dict = {'<7500 hours':[0,green_bg_format],'7500-9000 hours':[0,yellow_bg_format],'>9000 hours':[0,red_bg_format],'Total':[0,bold_format]}
	Controller_dict = {'working correctly':[0,green_bg_format],'no_info':[0,yellow_bg_format],'not working correctly':[0,red_bg_format],'by-passed':[0,red_bg_format],'Total':[0,bold_format]}
	Stabilizer_dict = {'working correctly':[0,green_bg_format],'no_info':[0,yellow_bg_format],'not working correctly':[0,red_bg_format],'Total':[0,bold_format]}
	
	Current_date_eomonth = Current_date + relativedelta(months=1, days=-Current_date.day)
	for Site in ExtractDateEquipment:
		####SAND MEDIA####
		Site_date = Site[2]
		if isinstance(Site_date, datetime):
			Site_date = Site_date.date()
		if Site_date != None:
			Age = (Current_date_eomonth - Site_date).days / 365.25
			if Age < 5:
				sand_media_dict['<5 years'][0] += 1
			elif Age < 10:
				sand_media_dict['5-10 years'][0] += 1
			else:
				sand_media_dict['>10 years'][0] += 1
			sand_media_dict['Total'][0] += 1
		####AC MEDIA####
		Site_date = Site[3]
		if isinstance(Site_date, datetime):
			Site_date = Site_date.date()
		if Site_date is not None:
			Age = (Current_date_eomonth - Site_date).days / 365.25
			if Age < 3:
				AC_media_dict['<3 years'][0] += 1
			elif Age < 4:
				AC_media_dict['3-4 years'][0] += 1
			else:
				AC_media_dict['>4 years'][0] += 1
			AC_media_dict['Total'][0] += 1
		####UV LAMP Type####
		uv_type_val = Site[4]
		if uv_type_val is None or uv_type_val == '':
			uv_type_val = 'unknown'
		# Increment safely (key guaranteed)
		UV_lamp_type_dict[uv_type_val] += 1
		UV_lamp_type_dict['Total'] += 1
		####UV LAMP AGE####
		DefaultHoursUsedDailyUVLamp = 6
		
		Site_date = Site[5]
		if isinstance(Site_date, datetime):
			Site_date = Site_date.date()
		if Site_date is not None:
			Age = (Current_date_eomonth - Site_date).days
			Hours = Age * DefaultHoursUsedDailyUVLamp
			if Hours < 7500:
				UV_lamp_age_dict['<7500 hours'][0] += 1
			elif Hours < 9000:
				UV_lamp_age_dict['7500-9000 hours'][0] += 1
			else:
				UV_lamp_age_dict['>9000 hours'][0] += 1
			UV_lamp_age_dict['Total'][0] += 1

		####CONTROLLER####
		if Site[7] == None:
			continue
		if Site[8]=='does_not_work':
			Controller_dict['not working correctly'][0] += 1
		elif Site[7]=='By-passed':
			Controller_dict['by-passed'][0] += 1
		elif Site[7]=='':
			Controller_dict['no_info'][0] += 1
		else:
			Controller_dict['working correctly'][0] += 1
		Controller_dict['Total'][0] += 1

		####STABILIZER####
		if Site[9]=='no':
			Stabilizer_dict['not working correctly'][0] += 1
		elif Site[9]=='':
			Stabilizer_dict['no_info'][0] += 1
		else:
			Stabilizer_dict['working correctly'][0] += 1
		Stabilizer_dict['Total'][0] += 1

		####WATER SOURCE####
		water_source_val = Site[11] if len(Site) > 11 else None
		if water_source_val is None or water_source_val == '':
			water_source_val = 'unknown'
		if water_source_val not in water_source_dict:
			# In case a new unexpected category appears since we built distinct list
			water_source_dict[water_source_val] = 0
		water_source_dict[water_source_val] += 1
		water_source_dict['Total'] += 1
	
	####SAND MEDIA AGE####
	# Helper to find the max length among all dicts (for column alignment)
	def max_dict_len(*dicts):
		return max(len(d) for d in dicts)

	# Find the max column count among all dicts (for total column alignment)
	max_col = max_dict_len(sand_media_dict, AC_media_dict, UV_lamp_type_dict, UV_lamp_age_dict, Controller_dict, Stabilizer_dict, water_source_dict)+1 

	def write_dict_block(row_start, label, data_dict, fmt_label, fmt_key, value_fmt_map):
		worksheet.write(row_start, 0, label, fmt_label)
		# Exclude "Total" from keys for main table
		keys = [k for k in data_dict.keys() if k != "Total"]
		# Write keys
		for idx, key in enumerate(keys):
			worksheet.write(row_start - 1, idx + 1, key, fmt_key)
		# Write values
		for idx, key in enumerate(keys):
			val, fmt = data_dict[key] if isinstance(data_dict[key], (list, tuple)) else (data_dict[key], None)
			worksheet.write(row_start, idx + 1, val, fmt if fmt else value_fmt_map.get(key, None))
		# Write "Total" in the last column, regardless of position in dict
		if "Total" in data_dict:
			val, fmt = data_dict["Total"] if isinstance(data_dict["Total"], (list, tuple)) else (data_dict["Total"], None)
			worksheet.write(row_start - 1, max_col, "Total", fmt_key)
			worksheet.write(row_start, max_col, val, fmt if fmt else value_fmt_map.get("Total", None))

	# Sand Media
	write_dict_block(1, "Sand Media", sand_media_dict, workbook.add_format({'bold':True}),
					 workbook.add_format({'italic':True}), {k: sand_media_dict[k][1] for k in sand_media_dict})

	# AC Media
	write_dict_block(3, "AC Media", AC_media_dict, workbook.add_format({'bold':True}),
					 workbook.add_format({'italic':True}), {k: AC_media_dict[k][1] for k in AC_media_dict})

	# UV Lamp Type (no color format, just values)
	worksheet.write(5, 0, "UV Lamp Type", workbook.add_format({'bold':True}))
	keys = [k for k in UV_lamp_type_dict.keys() if k != "Total"]
	for idx, key in enumerate(keys):
		worksheet.write(4, idx + 1, key, workbook.add_format({'italic':True}))
		worksheet.write(5, idx + 1, UV_lamp_type_dict[key])
	# Total column for UV Lamp Type
	if "Total" in UV_lamp_type_dict:
		worksheet.write(4, max_col, "Total", workbook.add_format({'bold':True}))
		worksheet.write(5, max_col, UV_lamp_type_dict["Total"])

	# UV Lamp Age
	write_dict_block(7, "UV Lamp Hours", UV_lamp_age_dict, workbook.add_format({'bold':True}),
					 workbook.add_format({'italic':True}), {k: UV_lamp_age_dict[k][1] for k in UV_lamp_age_dict})

	# Controller
	write_dict_block(9, "Controller", Controller_dict, workbook.add_format({'bold':True}),
					 workbook.add_format({'italic':True}), {k: Controller_dict[k][1] for k in Controller_dict})

	# Stabilizer
	write_dict_block(11, "Stabilizer", Stabilizer_dict, workbook.add_format({'bold':True}),
					 workbook.add_format({'italic':True}), {k: Stabilizer_dict[k][1] for k in Stabilizer_dict})

	# Water Source (no color format, just values like UV Lamp Type)
	worksheet.write(13, 0, "Water Source", workbook.add_format({'bold':True}))
	ws_keys = [k for k in water_source_dict.keys() if k != 'Total']
	for idx, key in enumerate(ws_keys):
		worksheet.write(12, idx + 1, key, workbook.add_format({'italic':True}))
		worksheet.write(13, idx + 1, water_source_dict[key])
	if 'Total' in water_source_dict:
		worksheet.write(12, max_col, 'Total', workbook.add_format({'bold':True}))
		worksheet.write(13, max_col, water_source_dict['Total'])

	Graph.GraphWaterSource(workbook,worksheet,Name_worksheet,15,0,12,3,Current_date)
	Graph.GraphElectricitySource(workbook,worksheet,Name_worksheet,15,3,12,3,Current_date)
	Graph.GraphPump(workbook,worksheet,Name_worksheet,15,6,12,3,Current_date)
	Graph.UvLampPerYearGraph(workbook,worksheet,Name_worksheet,33,0,12,3,Current_date)

def EquipmentAgeDetail(Current_date,workbook):
	"""Dynamic per-site equipment age/status table with schema-driven columns.

	This refactor allows easy reordering / inserting of columns: just edit the
	`schema` list; formulas auto-adapt using key-based cell references.

	Ages and UV hours are now calculated directly in Excel with EOMONTH().
	"""
	worksheet = workbook.add_worksheet("Equipment Detail")
	worksheet.freeze_panes(1,3)
	worksheet.set_zoom(80)

	# Formats
	head_site_fmt = workbook.add_format({'bold': True, 'bg_color': '#DAEEF3', 'border':1, 'text_wrap': True, 'align':'center', 'valign':'vcenter'})
	head_data_fmt = workbook.add_format({'bold': True, 'bg_color': '#0070C0', 'border':1, 'text_wrap': True, 'align':'center', 'valign':'vcenter'})
	center_fmt = workbook.add_format({'align':'center','valign':'vcenter'})
	num_fmt = workbook.add_format({'align':'center','valign':'vcenter','num_format':'0.0'})
	date_fmt = workbook.add_format({'num_format': 'yyyy-mm-dd','align':'center','valign':'vcenter'})
	green_bg_format = workbook.add_format({'bg_color':"#92D050",'align':'center','valign':'vcenter'})
	yellow_bg_format = workbook.add_format({'bg_color':"#FFFF00",'align':'center','valign':'vcenter'})
	red_bg_format = workbook.add_format({'bg_color':"#C0504D",'align':'center','valign':'vcenter','font_color':'white'})

	Tier_List = NewCalculTier(Current_date)[0]

	# Pull latest assessment per site with relevant fields
	ExtractDateEquipment = con.execute("""
		SELECT a.site, s.Platform,
		CASE WHEN YEAR(date_change_sand_filter_tank) < 2001 THEN MIN(Sales.Month) ELSE date_change_sand_filter_tank END AS sand_change,
		CASE WHEN YEAR(date_change_ac_filter_tank) < 2001 THEN MIN(Sales.Month) ELSE date_change_ac_filter_tank END AS ac_change,
		uv_lamp,
		CASE WHEN YEAR(date_change_uv_lamp) < 2001 OR date_change_uv_lamp = '' THEN MIN(Sales.Month) ELSE date_change_uv_lamp END AS uv_change,
		CASE WHEN YEAR(date_change_uv_controller) < 2001 OR date_change_uv_controller = '' THEN MIN(Sales.Month) ELSE date_change_uv_controller END AS controller_change,
		uv_controller, uv_controller_condition, stabilizer,
		CASE WHEN YEAR(last_change_stabilizer) < 2001 OR last_change_stabilizer = '' THEN MIN(Sales.Month) ELSE last_change_stabilizer END AS stabilizer_change
		FROM assessments a
		JOIN Sales ON a.site = Sales.Id_Site
		JOIN Sites s ON s.Id_Site = a.site
		WHERE s.Old_Platform <> 'Dead' AND s.Platform <> 'Dead'
		AND a.date_form = (
			SELECT MAX(date_form) FROM assessments WHERE site = a.site AND date_form <= %s
		)
		GROUP BY a.site
		ORDER BY a.site
	""", (Current_date + relativedelta(months=1),)).fetchall()
	# Helper to convert python date to excel serial formula constant via DATE(y,m,d)
	y = Current_date.year; m = Current_date.month
	excel_current_eom = f"EOMONTH(DATE({y},{m},1),0)"  # end of current month

	# Define a schema: order = column order
	# type: value | date | formula | formula_text
	schema = [
		{'key':'site','header':'Site','type':'value','source':lambda row: row['site'],'head_fmt':head_site_fmt},
		{'key':'platform','header':'Platform','type':'value','source':lambda row: row['platform'],'head_fmt':head_site_fmt},
		{'key':'tier','header':'Tier','type':'value','source':lambda row,row_map=None: row['tier'],'head_fmt':head_site_fmt},
		{'key':'sand_change','header':'Sand media change date','type':'date','source':lambda row: row['sand_change']},
		{'key':'sand_age','header':'Sand media age (y)','type':'formula','number_fmt':num_fmt,
		 'formula':lambda cell, refs: f"=IF({refs['sand_change']}=\"\",\"\",({excel_current_eom}-{refs['sand_change']})/365.25)"},
		{'key':'sand_cat','header':'Sand media category','type':'formula_text',
		 'formula':lambda cell, refs: f"=IF({refs['sand_age']}=\"\",\"\",IF({refs['sand_age']}<5,\"<5y\",IF({refs['sand_age']}<10,\"5-10y\",\">10y\")))"},
		{'key':'ac_change','header':'AC media change date','type':'date','source':lambda row: row['ac_change']},
		{'key':'ac_age','header':'AC media age (y)','type':'formula','number_fmt':num_fmt,
		 'formula':lambda cell, refs: f"=IF({refs['ac_change']}=\"\",\"\",({excel_current_eom}-{refs['ac_change']})/365.25)"},
		{'key':'ac_cat','header':'AC media category','type':'formula_text',
		 'formula':lambda cell, refs: f"=IF({refs['ac_age']}=\"\",\"\",IF({refs['ac_age']}<3,\"<3y\",IF({refs['ac_age']}<4,\"3-4y\",\">4y\")))"},
		{'key':'uv_type','header':'UV lamp type','type':'value','source':lambda row: row['uv_lamp']},
		{'key':'uv_change','header':'UV lamp change date','type':'date','source':lambda row: row['uv_change']},
		{'key':'uv_hours','header':'UV lamp hours','type':'formula',
		 'formula':lambda cell, refs: f"=IF({refs['uv_change']}=\"\",\"\",({excel_current_eom}-{refs['uv_change']})*6)"},
		{'key':'uv_cat','header':'UV lamp category','type':'formula_text',
		 'formula':lambda cell, refs: f"=IF({refs['uv_hours']}=\"\",\"\",IF({refs['uv_hours']}<7500,\"<7500\",IF({refs['uv_hours']}<9000,\"7500-9000\",\">9000\")))"},
		{'key':'controller_change','header':'Controller change date','type':'date','source':lambda row: row['controller_change']},
		{'key':'controller','header':'Controller','type':'value','source':lambda row: row['uv_controller']},
		{'key':'controller_condition','header':'Controller condition','type':'value','source':lambda row: row['uv_controller_condition']},
		{'key':'controller_status','header':'Controller status','type':'formula_text',
		 'formula':lambda cell, refs: (
			f"=IF(AND({refs['controller']}=\"\",{refs['controller_condition']}=\"\"),\"no_info\","
			f"IF(LOWER({refs['controller_condition']})=\"does_not_work\",\"not working correctly\"," \
			f"IF(LOWER({refs['controller']})=\"by-passed\",\"by-passed\",\"working correctly\")))"
		 )},
		{'key':'stabilizer_change','header':'Stabilizer change date','type':'date','source':lambda row: row['stabilizer_change']},
		{'key':'stabilizer','header':'Stabilizer','type':'value','source':lambda row: row['stabilizer']},
	]

	# Write headers & build key->col map
	key_to_col = {}
	for col, col_def in enumerate(schema):
		key_to_col[col_def['key']] = col
		head_fmt = col_def.get('head_fmt', head_data_fmt if col_def['key'] not in ('site','platform','tier') else head_site_fmt)
		worksheet.write(0, col, col_def['header'], head_fmt)
		worksheet.set_column(col, col, max(15, len(col_def['header'])) + 1)

	# Helper to get a cell ref for a key for a given row r (0-based data row, header at 0)
	def cell_ref(key, r0):
		return xl_rowcol_to_cell(r0+1, key_to_col[key])  # +1 for header offset

	# Row processing
	for r, raw in enumerate(ExtractDateEquipment, start=0):
		(site_id, platform, sand_change, ac_change, uv_lamp, uv_change, controller_change, uv_controller, uv_controller_condition, stabilizer, stabilizer_change) = raw
		# Normalize dates to python date for writing (Excel will format); formulas will handle ages
		def to_date(v):
			if not v or v == '':
				return None
			if isinstance(v, datetime):
				return v.date()
			return v if isinstance(v, date) else None
		row_dict = {
			'site': site_id,
			'platform': platform,
			'tier': next((t[1] for t in Tier_List if t[0] == site_id), ""),
			'sand_change': to_date(sand_change),
			'ac_change': to_date(ac_change),
			'uv_lamp': uv_lamp,
			'uv_change': to_date(uv_change),
			'controller_change': to_date(controller_change),
			'uv_controller': uv_controller,
			'uv_controller_condition': uv_controller_condition,
			'stabilizer_change': to_date(stabilizer_change),
			'stabilizer': stabilizer,
		}
		# Pre-compute references for formulas in this row
		refs = {k: cell_ref(k, r) for k in key_to_col.keys()}
		for col, col_def in enumerate(schema):
			ctype = col_def['type']
			if ctype in ('value','date'):
				val = col_def['source'](row_dict)
				fmt = date_fmt if ctype == 'date' and val else center_fmt
				worksheet.write(r+1, col, val if val is not None else "", fmt)
			elif ctype == 'formula':
				formula = col_def['formula'](None, refs)
				fmt = col_def.get('number_fmt', center_fmt)
				worksheet.write_formula(r+1, col, formula, fmt)
			elif ctype == 'formula_text':
				formula = col_def['formula'](None, refs)
				worksheet.write_formula(r+1, col, formula, center_fmt)

	# Conditional formatting dynamically (based on keys existing)
	last_data_row_index = len(ExtractDateEquipment)
	if last_data_row_index > 0:
		# Helper apply text rules
		def text_rules(key, rules):
			if key not in key_to_col: return
			c = key_to_col[key]
			for rule in rules:
				cfg = {'type':'text','criteria':rule['criteria'],'value':rule['value'],'format':rule['format']}
				worksheet.conditional_format(1, c, last_data_row_index, c, cfg)
		text_rules('sand_cat', [
			{'criteria':'begins with','value':'<5y','format':green_bg_format},
			{'criteria':'begins with','value':'5-10y','format':yellow_bg_format},
			{'criteria':'begins with','value':'>10y','format':red_bg_format},
		])
		text_rules('ac_cat', [
			{'criteria':'begins with','value':'<3y','format':green_bg_format},
			{'criteria':'begins with','value':'3-4y','format':yellow_bg_format},
			{'criteria':'begins with','value':'>4y','format':red_bg_format},
		])
		text_rules('uv_cat', [
			{'criteria':'begins with','value':'<7500','format':green_bg_format},
			{'criteria':'begins with','value':'7500-9000','format':yellow_bg_format},
			{'criteria':'begins with','value':'>9000','format':red_bg_format},
		])
		text_rules('controller_status', [
			{'criteria':'begins with','value':'working correctly','format':green_bg_format},
			{'criteria':'begins with','value':'no_info','format':yellow_bg_format},
			{'criteria':'begins with','value':'not working correctly','format':red_bg_format},
			{'criteria':'begins with','value':'by-passed','format':yellow_bg_format},
		])
		# Stabilizer raw cell coloring
		if 'stabilizer' in key_to_col:
			c = key_to_col['stabilizer']
			worksheet.conditional_format(1,c,last_data_row_index,c,{'type':'text','criteria':'begins with','value':'works','format':green_bg_format})
			worksheet.conditional_format(1,c,last_data_row_index,c,{'type':'text','criteria':'begins with','value':'does_not_work','format':red_bg_format})
			worksheet.conditional_format(1,c,last_data_row_index,c,{'type':'text','criteria':'begins with','value':'no','format':red_bg_format})
			worksheet.conditional_format(1,c,last_data_row_index,c,{'type':'blanks','format':yellow_bg_format})

	worksheet.autofilter(0,0,max(0,last_data_row_index),len(schema)-1)
	return

def LaunchExcelCreationTechnical(Current_date,exchange_rate):
	Date_janv = date(Current_date.year,1,1)
	Month = Current_date.month
	if Month < 10:
		Month = '0' + str(Month)
	else:
		Month = str(Month)
	Year = str(Current_date.year)
	filepath = tempfile.gettempdir()+'/Technical Dashboard ' + Year + '-' + Month + '.xlsx'
	workbook = xlsxwriter.Workbook(filepath)
	DashboardTechnical(Current_date,Date_janv,workbook)
	EquipmentAge(Current_date,workbook)
	EquipmentAgeDetail(Current_date,workbook)
	ExcelSiteAnalysisTechnical.Technical_Site_Analysis(workbook, Current_date)
	workbook.close()

if __name__ == '__main__':
	Current_date = date(2023,8,1)
	LaunchExcelCreationTechnical(Current_date)
