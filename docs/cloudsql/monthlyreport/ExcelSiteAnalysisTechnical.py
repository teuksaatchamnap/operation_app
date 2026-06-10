from os import write
import xlsxwriter
from monthlyreport.Functionutils import listSiteStillActive
from datetime import date
import db
from dateutil.relativedelta import *
from xlsxwriter.utility import xl_col_to_name
from collections import defaultdict

def Technical_Site_Analysis(workbook, Current_date):
    
    # Create the worksheets
    def add_worksheet():
        worksheet_site_analysis = add_ws("Site Analysis")
        worksheet_site_analysis.hide_gridlines(2)
        worksheet_site_analysis.print_area('A1:H60')
        worksheet_site_analysis.fit_to_pages(1, 1)  # Fit to 1 page wide by 1 page tall
        #worksheet_site_analysis.set_print_scale(100)  # 100% scaling (optional, can adjust as needed)
        worksheet_data_months = add_ws("Data Month Site Analysis", True)
        worksheet_date_contamination_bottle = add_ws("Contamination Bottle", True)
        worksheet_date_contamination_machine = add_ws("Contamination Machine", True)
        worksheet_list_intervention = add_ws("List Intervention", True)
        worksheet_site_intervention = add_ws("Site Intervention", True)
        worksheet_alu = add_ws("Aluminium", True)
        worksheet_turb = add_ws("Turbidity", True)
        worksheet_water_consumption = add_ws("Water Consumption",True)
        return worksheet_site_analysis, worksheet_data_months, worksheet_date_contamination_bottle, worksheet_date_contamination_machine, worksheet_list_intervention, worksheet_site_intervention,worksheet_alu, worksheet_turb, worksheet_water_consumption
    
    def add_ws(name, hidden=False):
        ws = workbook.add_worksheet(name)
        if hidden:
            ws.hide()
        return ws

    def format_factory(workbook):
        fmt = {}
        fmt['normal_num'] = workbook.add_format({'num_format': '#,###,##0'})
        fmt['number'] = workbook.add_format({'num_format': '#,###,##0', 'align': 'right'})
        fmt['date'] = workbook.add_format({'num_format': 'mmm-yy', 'align': 'right'})
        fmt['small_text'] = workbook.add_format({'num_format': '#,###,##0', 'align': 'right','font_size': 7})
        fmt['decimal'] = workbook.add_format({'num_format': '#,##0.00', 'align': 'right'})
        fmt['percentage'] = workbook.add_format({'num_format': '0.0%'})
        fmt['merge'] = workbook.add_format({'font_color': 'red', 'center_across': True, 'bold': True, 'font_size': 16, 'underline': True})
        fmt['bold'] = workbook.add_format({'font_size': '12', 'bold': True})
        fmt['bg_red'] = workbook.add_format({'bg_color': '#FFC7CE', 'bold': True})
        fmt['Green_header'] = workbook.add_format({'bg_color': '#76933C', 'font_color':'#FFFFFF','bold': True, 'align': 'center', 'valign': 'vcenter'})
        fmt['Green_subheader'] = workbook.add_format({'bg_color': '#D8E4BC','italic': True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['Green_subheader_date'] = workbook.add_format({'bg_color': '#D8E4BC','italic': True, 'align': 'center', 'valign': 'vcenter','font_size':10,'num_format':'mmm-yy'})
        fmt['PandL_header'] = workbook.add_format({'bg_color': '#203764', 'font_color':'#FFFFFF','bold': True, 'align': 'center', 'valign': 'vcenter'})
        fmt['PandL_subheader'] = workbook.add_format({'bg_color': '#DCE6F1','italic': True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['PandL_subheader_bold'] = workbook.add_format({'num_format':'#,###,##0','bg_color': '#DCE6F1','bold': True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['PandL_number']= workbook.add_format({"num_format" : '#,###,##0','italic':True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['Select_format'] = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
        fmt['blank_light'] = workbook.add_format({'bg_color':'#F2F2F2','font_color':'#666666'})
        return fmt

    def col_letter_from_header(header):
        header_monthly_data = headers_month_tab
        col = xl_col_to_name(header_monthly_data.index(header))
        return col
    
    def fetch_query(query, *args):
        con = db.pool.connect()
        return con.execute(query, args if args else ()).fetchall()

    def fetch_dict(data):
        return {row[0]: row for row in data}

    def query(Current_date):
        query_map = {
            'Sites': ("""
                SELECT s.Id_Site, s.Platform, s.Advisor, s.Entrepreneur_English_Name, s.Date_start_working, r.technician
                FROM Sites s
                LEFT JOIN (
                    SELECT site, technician, date
                    FROM routines
                    WHERE date <= %s
                    AND date = (
                        SELECT MAX(date) FROM routines r2 WHERE r2.site = routines.site AND r2.date <= %s
                    )
                ) r ON s.Id_Site = r.site
            """, Current_date, Current_date),

            'Sales_Monthly': ("SELECT Id_Site, (Total_Sales - Bottle_Sales)/Number_Open_Days FROM Sales WHERE Month = %s", Current_date),

            'Sales_YTD': ("SELECT Id_Site, SUM(Total_Sales - Bottle_Sales)/SUM(Number_Open_Days) FROM Sales "
            "WHERE Month <= %s AND Month > %s GROUP BY Id_Site", Current_date+relativedelta(months=1), date(Current_date.year,1,1)),

            'Technical_Monthly': ("SELECT site,COUNT(id) FROM technicals WHERE reporting <> 'ON-SITE(Routine)'"
                            "AND problem_date <= %s AND problem_date > %s GROUP BY site", Current_date + relativedelta(months=1), Current_date),

            'Technical_ytd': ("SELECT site,COUNT(id) FROM technicals WHERE reporting <> 'ON-SITE(Routine)'"
                            "AND problem_date < %s AND problem_date >= %s GROUP BY site", Current_date+relativedelta(months=1), date(Current_date.year,1,1)),
            
            'Assessment': ("""
            WITH latest_per_site AS (SELECT *,
                ROW_NUMBER() OVER (PARTITION BY site ORDER BY date_form DESC) AS row_num FROM assessments
                WHERE date_form < %s)
            SELECT site, date_form, main_source_of_electricity, main_source_of_water, second_source_of_water, 
                flocculation_and_coagulation_process, reverse_osmose, ultrafiltration, uv_lamp, uv_lamp_condition,
                uv_controller, uv_ballast, raw_water_pump, back_wash_pump, micro_filter_pump
            FROM latest_per_site WHERE row_num = 1 """, Current_date+relativedelta(months=1)),
            
            'Routine': ("""
            WITH latest_per_site AS (SELECT *,
                ROW_NUMBER() OVER (PARTITION BY site ORDER BY date DESC) AS row_num FROM routines
                WHERE date < %s)
            SELECT site, date, pH_raw_water, Turbidity_raw_water, Conductivity_raw_water, TDS_raw_water,
                        maximum_flow_of_the_micro_filtration_pump, condition_of_sand_filter_tank, condition_of_ac_filter_tank, technician
            FROM latest_per_site WHERE row_num = 1 """, Current_date+relativedelta(months=1)),

            'Quality_Monthly': ("""
            SELECT site, 
                COUNT(CASE WHEN escherichia > 0 THEN 1 END) AS escherichia_count, 
                COUNT(CASE WHEN total_coliform > 0 THEN 1 END) AS total_coliform_count,
                pH, turbidity, conductivity, TDS
            FROM samples WHERE analysis_date <= %s AND analysis_date > %s
            AND type = "Monthly Test" GROUP BY site""",
            Current_date + relativedelta(months=1), Current_date),

            'Quality_YTD': ("""
            SELECT site,
                COUNT(CASE WHEN escherichia > 0 THEN 1 END) AS escherichia_count, 
                COUNT(CASE WHEN total_coliform > 0 THEN 1 END) AS total_coliform_count 
            FROM samples WHERE analysis_date < %s AND analysis_date >= %s 
            AND type = "Monthly Test" GROUP BY site""",
            Current_date+relativedelta(months=1), date(Current_date.year,1,1)),

            'HistoricAlert' : ("""
            SELECT site, DATE(DATE_FORMAT(analysis_date, '%%Y-%%m-01')) AS analysis_date, COALESCE(contamination_level_bottle, 0) AS contamination_level_bottle, 
            COALESCE(contamination_level_machine, 0) AS contamination_level_machine FROM samples
            WHERE analysis_date < %s AND analysis_date >= %s AND type = "Monthly Test" """,
            Current_date+relativedelta(months=1), date(Current_date.year,1,1)),

            'HistoricIntervention' : ("""SELECT site, tp.problem_category, DATE(DATE_FORMAT(start_intervention, '%%Y-%%m-01'))
							   FROM technical_problems tp
							   JOIN technicals tt ON tp.technical_id = tt.id
							   WHERE tt.start_intervention >= %s AND tt.start_intervention < %s
							   ORDER BY site""",
            date(Current_date.year,1,1),Current_date+relativedelta(months=1)),

            'HistoricAluTurb' : ("""
            SELECT site, DATE(DATE_FORMAT(analysis_date, '%%Y-%%m-01')) AS analysis_date, aluminium,turbidity
            FROM samples WHERE analysis_date < %s AND analysis_date >= %s AND type = "Monthly Test"
            """,
            Current_date+relativedelta(months=1), date(Current_date.year,1,1)),

            'InterventionList': ("""SELECT DISTINCT problem_category FROM technical_problems 
                                JOIN technicals ON technical_problems.technical_id = technicals.id
                                WHERE start_intervention >= %s and problem_category IS NOT NULL
                                ORDER BY problem_category ASC""",date(Current_date.year,1,1)),

            'WaterConsume':("""SELECT Id_Site, DATE(DATE_FORMAT(month, '%%Y-%%m-01')) AS month,Water_Consume 
                            FROM Indicators WHERE Month <= %s AND Month >= %s""",
                            Current_date,date(Current_date.year,1,1)),

            'Pre_treatment': ("""
            WITH latest_per_site AS (SELECT *,
                ROW_NUMBER() OVER (PARTITION BY site ORDER BY date_form DESC) AS row_num FROM assessments
                WHERE date_form < %s)
            SELECT site, pre_treatment_process_1, pre_treatment_process_2, pre_treatment_process_3,
                    pre_treatment_process_4, pre_treatment_process_5, pre_treatment_process_6, pre_treatment_process_7
            FROM latest_per_site WHERE row_num = 1 """, Current_date+relativedelta(months=1)),

            'Pre_treatment_info': ("""
            WITH latest_per_site AS (SELECT *,
                ROW_NUMBER() OVER (PARTITION BY site ORDER BY date_form DESC) AS row_num FROM assessments
                WHERE date_form < %s)
            SELECT site, type_of_raw_water_tank as rwt_type, raw_water_tank_v_liter as rwt_vol,
                    type_of_sand_filter_tank as sft_type, sand_filter_tank_v_liter as sft_vol,
                    type_of_ac_filter_tank as act_type, ac_filter_tank_v_liter as act_vol,
                    type_of_resin_filter_tank as rft_type, resin_filter_tank_v_liter as rft_vol,
                    type_of_clear_water_tank as cwt_type, clear_water_tank_v_liter as cwt_vol,
                    type_of_afm as afm_type, afm_v_iter as afm_vol,
                    type_of_zmag as zmag_type, zmag_v_iter as zmag_vol,
                    type_of_sand_filter_and_Zmag_tank as sfz_type, sand_filter_and_zmag_v_iter as sfz_vol
            FROM latest_per_site WHERE row_num = 1 """, Current_date+relativedelta(months=1)),
            }   

        fetched = {k: fetch_dict(fetch_query(*v)) if (k != 'HistoricAlert' or k!= 'WaterConsume') and isinstance(v, tuple) else fetch_dict(fetch_query(v))
                for k, v in query_map.items() if (k != 'HistoricAlert' or k != 'WaterConsume') }
        
        return fetched, query_map

    def write_raw_data_month(ws, row_index, site_id):

        site_info = fetched['Sites'].get(site_id, (site_id, '', '', '','',''))
        Sales_monthly = fetched['Sales_Monthly'].get(site_id, (site_id, 0))
        Sales_ytd = fetched['Sales_YTD'].get(site_id, (site_id, 0))
        Technical_monthly = fetched['Technical_Monthly'].get(site_id, (site_id, 0))
        Technical_ytd = fetched['Technical_ytd'].get(site_id, (site_id, 0))
        Assessment = fetched['Assessment'].get(site_id, (site_id, '', '', '', '', '', '', '', '', '', '', '','','',''))
        Routine = fetched['Routine'].get(site_id, (site_id, '', '', '', '', '', '', '', '', '', '', ''))
        Quality_monthly = fetched['Quality_Monthly'].get(site_id, (site_id, 0, 0, "", "", "", ""))
        Quality_ytd = fetched['Quality_YTD'].get(site_id, (site_id, 0, 0))


        ws.write_row(row_index, 0, [
            site_info[0], site_info[1], site_info[5], site_info[3], site_info[4],
            Sales_monthly[1], Sales_ytd[1], Assessment[1], Assessment[2], Assessment[3], Assessment[4], Assessment[5],
            Assessment[6], Assessment[7], Assessment[8], Assessment[9], Assessment[10],
            Assessment[11],Assessment[12], Assessment[13], Assessment[14], Quality_monthly[1], Quality_monthly[2], Quality_ytd[1], Quality_ytd[2],
            Quality_monthly[3], Quality_monthly[4], Quality_monthly[5], Quality_monthly[6], Routine[2], Routine[3], 
            Routine[4], Routine[5], Technical_monthly[1], Technical_ytd[1], Routine[1], Routine[6],
            Routine[7], Routine[8]])

    def raw_data_month_header():
        column = [
            'Site', 'Platform', 'Technician', 'Entrepreneur Name', 'Starting Date', 'Bottle day Month', 'Bottle day YTD',
            'Date Assessment', 'Main source of electricity', 'Main source of water', 'Second source of water',
            'Flocculation and coagulation process', 'Reverse osmosis', 'Ultrafiltration', 'UV lamp', 'UV lamp condition',
            'UV controller', 'UV ballast', 'Raw water pump', 'Back wash pump', 'Micro filter pump', 
            '#E.coli Monthly', '#Coliform Monthly', '#E.coli YTD', '#Coliform YTD', 'Drink. water pH',
            'Drink. water turbidity', 'Drink. water conductivity', 'Drink. water TDS', 'Raw water pH', 'Raw water turbidity',
            'Raw water conductivity', 'Raw water TDS', "Unplanned int. Monthly", "Unplanned int. YTD",
            'Last check', 'Flow measured', 'Sand filter', 'AC filter'
        ]
        return column

    def pretreatement_processes():
        pretreatment_map = {
            'ចម្រោះខ្សាច់/Sand filter': ['sft_type', 'sft_vol'],
            'ចម្រោះធ្យូង/Activated Carbon filter': ['act_type', 'act_vol'],
            'ចម្រោះ R.O/Reverse Osmose' : ['Yes'],
            'ធុងទទេ/Empty tank' : ['Yes'],
            'AFM Filter' : ['afm_type', 'afm_vol'],
            'ចម្រោះ UF/Ultrafiltration' : ['Yes'],
            'ប្រភេទនៃធុងចម្រោះខ្សាច់ & zmax/ type_of_sand_and_zmax' : ['sfz_type', 'sfz_vol'],
            'ធុងទឹកឆៅ/Raw water tank' : ['rwt_type', 'rwt_vol'],
            'ធុងស្មាច់/FRP tank' : ['Yes'],
            'ធុងទឹកថ្លា/Clear water tank' : ['cwt_type', 'cwt_vol'],
            'ចម្ររ៉េស៊ីន/Resin filter' : ['rft_type', 'rft_vol'],
            'ZMag zeolite' : ['zmag_type', 'zmag_vol'],
            'ចម្រោះសេរ៉ាម៉ិច/Ceramic filter' : ['Yes']
        }
        return pretreatment_map

    def write_data_pretreatment():
        """Create hidden raw pretreatment sheet (if absent) and populate it.

        New format (one row per site):
        Site | S1_Process | S1_Type | S1_Vol | S2_Process | S2_Type | S2_Vol | ... | S7_Process | S7_Type | S7_Vol

        Returns
        -------
        raw_sheet_name : str
            Name of the hidden sheet.
        col_map : dict
            Mapping: step -> {'process': col_letter, 'type': col_letter, 'vol': col_letter}
        """
        raw_sheet_name = 'raw pretreatment info'
        raw_ws = None
        if hasattr(workbook, 'get_worksheet_by_name'):
            try:
                raw_ws = workbook.get_worksheet_by_name(raw_sheet_name)
            except Exception:
                raw_ws = None
        if raw_ws:
            # Build column map from known structure (Site then 7 * 3 columns)
            col_map = {}
            for step in range(1,8):
                base_idx = 1 + (step-1)*3  # zero-based after Site
                col_map[step] = {
                    'process': xl_col_to_name(base_idx),
                    'type': xl_col_to_name(base_idx+1),
                    'vol': xl_col_to_name(base_idx+2)
                }
            return raw_sheet_name, col_map

        raw_ws = workbook.add_worksheet(raw_sheet_name)
        raw_ws.hide()
        # Headers
        headers = ['Site']
        for step in range(1,8):
            headers.extend([f'S{step}_Process', f'S{step}_Type', f'S{step}_Vol'])
        raw_ws.write_row(0,0,headers)

        # Prepare mapping from process name to attribute field names
        pmap = pretreatement_processes()
        pre_info_order = ['site','rwt_type','rwt_vol','sft_type','sft_vol','act_type','act_vol','rft_type','rft_vol','cwt_type','cwt_vol','afm_type','afm_vol','zmag_type','zmag_vol','sfz_type','sfz_vol']
        index_map = {name:i for i,name in enumerate(pre_info_order)}

        for site_id, data in fetched['Pre_treatment'].items():
            row_tuple = tuple(data)
            processes = list(row_tuple[1:])  # p1..p7
            info_rec = fetched['Pre_treatment_info'].get(site_id)
            row_vals = [site_id]
            for step_no, proc in enumerate(processes, start=1):
                if proc:
                    # Determine attribute fields for this process
                    attr_list = pmap.get(proc, [])
                    if len(attr_list) >= 2:
                        type_field, vol_field = attr_list[0], attr_list[1]
                        type_val = info_rec[index_map[type_field]] if info_rec and type_field in index_map and len(info_rec) > index_map[type_field] else ''
                        vol_val = info_rec[index_map[vol_field]] if info_rec and vol_field in index_map and len(info_rec) > index_map[vol_field] else ''
                    else:
                        type_val = ''
                        vol_val = ''
                    row_vals.extend([proc, type_val, vol_val])
                else:
                    row_vals.extend(['','',''])
            # Ensure exactly 7 steps * 3 columns appended
            current_steps = (len(row_vals)-1)//3
            if current_steps < 7:
                missing = 7 - current_steps
                row_vals.extend(['','','']*missing)
            raw_ws.write_row(raw_ws.dim_rowmax+1, 0, row_vals)

        # Build column map for later formula generation
        col_map = {}
        for step in range(1,8):
            base_idx = 1 + (step-1)*3  # zero-based after Site
            col_map[step] = {
                'process': xl_col_to_name(base_idx),
                'type': xl_col_to_name(base_idx+1),
                'vol': xl_col_to_name(base_idx+2)
            }
        return raw_sheet_name, col_map

    def write_data_water_consumption(ws):
        ws.write(0, 0, "Site")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        water_consume = fetch_query(*query_map['WaterConsume'])
        consumption_cache = defaultdict(dict)
        for site_id, month, consumption in water_consume:
            consumption_cache[site_id][month] = consumption
        while Jan_date <= Current_date:
            ws.write(0, col, Jan_date.strftime('%b'))
            col += 1
            Jan_date += relativedelta(months=1)
        
        # Add a row to select data for the site from 'Site Analysis!O2'
        ws.write(1, 0, "Selected Site")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        while Jan_date <= Current_date:
            ws.write_formula(1, col, 
            f"=INDEX({xl_col_to_name(col)}3:{xl_col_to_name(col)}{len(ListSiteActive) + 2}, MATCH('Site Analysis'!{cell_site}, A3:A{len(ListSiteActive) + 2}, 0))*1", 
            fmt['number']
            )
            col += 1
            Jan_date += relativedelta(months=1)
        
        for row_idx, site_row in enumerate(ListSiteActive, start=2):
            site_id = site_row[0]
            ws.write(row_idx, 0, site_id)
            Jan_date = date(Current_date.year, 1, 1)
            col = 1
            while Jan_date <= Current_date:
                values = consumption_cache.get(site_id, {}).get(Jan_date)
                if values:
                    ws.write(row_idx, col, values)
                col += 1
                Jan_date += relativedelta(months=1)

    def write_data_contamination(ws,number_value):
        ws.write(0, 0, "Site")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        all_historic_alert = fetch_query(*query_map['HistoricAlert'])
        alert_cache = defaultdict(dict)
        for site_id, month, sales, days in all_historic_alert:
            alert_cache[site_id][month] = (sales, days)
        
        while Jan_date <= Current_date:
            ws.write(0, col, Jan_date.strftime('%b'))
            col += 1
            Jan_date += relativedelta(months=1)
        
        # Add a row to select data for the site from 'Site Analysis!O2'
        ws.write(1, 0, "Selected Site")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        while Jan_date <= Current_date:
            ws.write_formula(1, col, 
            f"=INDEX({xl_col_to_name(col)}3:{xl_col_to_name(col)}{len(ListSiteActive) + 2}, MATCH('Site Analysis'!{cell_site}, A3:A{len(ListSiteActive) + 2}, 0))*1", 
            fmt['number']
            )
            col += 1
            Jan_date += relativedelta(months=1)
        
        for row_idx, site_row in enumerate(ListSiteActive, start=2):
            site_id = site_row[0]
            ws.write(row_idx, 0, site_id)
            Jan_date = date(Current_date.year, 1, 1)
            col = 1
            while Jan_date <= Current_date:
                values = alert_cache.get(site_id, {}).get(Jan_date)
                if values:
                    ws.write(row_idx, col, values[number_value])
                col += 1
                Jan_date += relativedelta(months=1)

    def write_data_aluturb(ws,number_value):
        ws.write(0, 0, "Site")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        all_historic_aluturb = fetch_query(*query_map['HistoricAluTurb'])
        alert_cache = defaultdict(dict)
        for site_id, month, sales, days in all_historic_aluturb:
            alert_cache[site_id][month] = (sales, days)
        
        while Jan_date <= Current_date:
            ws.write(0, col, Jan_date.strftime('%b'))
            col += 1
            Jan_date += relativedelta(months=1)
        
        # Add a row to select data for the site from 'Site Analysis!O2'
        ws.write(1, 0, "Selected Site")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        while Jan_date <= Current_date:
            ws.write_formula(1, col, 
            f"=INDEX({xl_col_to_name(col)}3:{xl_col_to_name(col)}{len(ListSiteActive) + 2}, MATCH('Site Analysis'!{cell_site}, A3:A{len(ListSiteActive) + 2}, 0))*1", 
            fmt['decimal']
            )
            col += 1
            Jan_date += relativedelta(months=1)
        
        for row_idx, site_row in enumerate(ListSiteActive, start=2):
            site_id = site_row[0]
            ws.write(row_idx, 0, site_id)
            Jan_date = date(Current_date.year, 1, 1)
            col = 1
            while Jan_date <= Current_date:
                values = alert_cache.get(site_id, {}).get(Jan_date)
                if values:
                    ws.write(row_idx, col, values[number_value])
                col += 1
                Jan_date += relativedelta(months=1)
    
    def write_intervention_type(ws):
        ws.write(0, 0, "Site")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        all_historic_intervention = fetch_query(*query_map['HistoricIntervention'])
        # print(all_historic_intervention)
        intervention_cache = defaultdict(lambda: defaultdict(list))

        # Organize data into a cache
        for site_id, problem_category, month in all_historic_intervention:
            intervention_cache[site_id][month].append(problem_category)

        # Write month headers
        while Jan_date <= Current_date:
            ws.write(0, col, Jan_date.strftime('%b'))
            col += 1
            Jan_date += relativedelta(months=1)

        # Write data for each site
        for row_idx, site_row in enumerate(ListSiteActive, start=1):
            site_id = site_row[0]
            ws.write(row_idx, 0, site_id)
            Jan_date = date(Current_date.year, 1, 1)
            col = 1
            while Jan_date <= Current_date:
                problems = intervention_cache.get(site_id, {}).get(Jan_date, [])
                ws.write(row_idx, col, "-".join(filter(None, problems)))
                col += 1
                Jan_date += relativedelta(months=1)

    def write_intervention_summary(ws_summary, ws_source):
        # Write the formula to gather data for each month from the source tab
        col = 1
        Jan_date = date(Current_date.year, 1, 1)
        while Jan_date <= Current_date:
            ws_summary.write_formula(
                0, col,
                f"=INDEX('{ws_source.get_name()}'!{xl_col_to_name(col)}2:{xl_col_to_name(col)}{len(ListSiteActive) + 1}, "
                f"MATCH('Site Analysis'!O2, '{ws_source.get_name()}'!A2:A{len(ListSiteActive) + 1}, 0))"
            )
            col += 1
            Jan_date += relativedelta(months=1)
        
        # Write the header row with month names
        ws_summary.write(0, 0, "Intervention Type")
        Jan_date = date(Current_date.year, 1, 1)
        col = 1
        while Jan_date <= Current_date:
            ws_summary.write(1, col, Jan_date.strftime('%b'))
            col += 1
            Jan_date += relativedelta(months=1)

        # Write the list of all possible interventions in the first column, split Khmer/English for formula
        all_interventions = [row[0] for row in fetch_query(*query_map['InterventionList'])]
        for row_idx, intervention in enumerate(all_interventions, start=2):
            if "/" in intervention:
                khmer, english = intervention.split("/", 1)
                formula = f'=IF(\'Site Analysis\'!D2="Khmer","{khmer.strip()}","{english.strip()}")'
                ws_summary.write_formula(row_idx, 0, formula)
            else:
                ws_summary.write(row_idx, 0, intervention)

            # Write the formula to count occurrences of each intervention type for each month
            col = 1
            Jan_date = date(Current_date.year, 1, 1)
            while Jan_date <= Current_date:
                ws_summary.write_formula(
                    row_idx, col,
                    f"=(LEN({xl_col_to_name(col)}1) - "
                    f"LEN(SUBSTITUTE({xl_col_to_name(col)}1, A{row_idx+1}, \"\"))) / LEN(A{row_idx+1})"
                )
                col += 1
                Jan_date += relativedelta(months=1)

    def title_language(ws,cell_language_name,cell_language,cell_site,cell_platform_title,cell_platform,cell_technician_title,cell_technician,fmt):
        site_count = len(ListSiteActive) + 2
        ws.merge_range('A1:H1', 'Technical Site Analysis', fmt['merge'])
        ws.data_validation(cell_site, {'validate': 'list', 'source': f"'Data Month Site Analysis'!A2:A{site_count}"})
        try:
            ws.write(cell_site, ListSiteActive[0][0],fmt['Select_format'])
        except:
            ws.write(cell_site,"CHOOSE SITE",fmt['Select_format'])
        ws.write(cell_language_name, 'Select Language/ជ្រើសរើស​ភាសា', fmt['bold'])
        ws.data_validation(cell_language, {'validate': 'list', 'source': ['Khmer', 'English']})
        ws.write(cell_language, "English", fmt['bold'])
        ws.write_formula(cell_platform_title, f'=IF({cell_language}="Khmer","តំបន់","Platform")', fmt['bold'])
        ws.write(cell_platform, f"=INDEX('Data Month Site Analysis'!B2:B{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['normal_num'])
        ws.write_formula(cell_technician_title, f'=IF({cell_language}="Khmer","អ្នកបច្ចេកទេស","Technician")', fmt['bold'])
        ws.write(cell_technician, f"=INDEX('Data Month Site Analysis'!C2:C{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['normal_num'])

    def write_site_analysis_header(ws, fmt):
        site_count = len(ListSiteActive) + 2
        col_ent = col_letter_from_header('Entrepreneur Name')
        col_start_date = col_letter_from_header('Starting Date')
        headers = {
            'A3': 'កូដស្ថានីយ|Site code',
            'C3': 'ខែ|Month',
            'E3': 'ឈ្មោះសហគ្រិន|Ent. name',
            'G3': 'ថ្ងៃចាប់ផ្តើម|Starting date'
        }
        value = {
            'B3': ('=O2', fmt['Green_subheader']),
            'D3': (f'{Current_date}', fmt['Green_subheader_date']),
            'F3': (f"=INDEX('Data Month Site Analysis'!{col_ent}2:{col_ent}{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['Green_subheader']),
            'H3': (f"=INDEX('Data Month Site Analysis'!{col_start_date}2:{col_start_date}{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['Green_subheader_date'])
        }
        for cell, val in headers.items():
            kh, en = val.split('|')
            ws.write_formula(cell, f'=IF(D2="Khmer","{kh}","{en}")',fmt['Green_header'])
        for cell, (val, format_type) in value.items():
            ws.write(cell, val, format_type)
        # Slightly increase column G (Starting date label/value area) for better readability
        try:
            current_width = ws.col_sizes.get(6) if hasattr(ws, 'col_sizes') else None  # 0-based index
        except Exception:
            current_width = None
        # Set to a modest wider value; if already larger this will be harmless
        ws.set_column('G:G', 15)

    def write_quality_technical_performance(ws, fmt,start_row=4):
        site_count = len(ListSiteActive) + 2
        base = "'Data Month Site Analysis'!"
        match = f"MATCH('Site Analysis'!O2,{base}A2:A{site_count},0)"
        blocks = [
            {
            'title': ('A', 'ព័ត៌មានប្រចាំខែ|Monthly info', 'PandL_header', 24),
            'rows': [
            ('ដប/ថ្ងៃ|Bot/day', 'PandL_subheader',["Bottle day Month"], 'number', 8),
            ('មេរោគអេកូលី|E. Coli Alert', 'PandL_subheader',["#E.coli Monthly"], 'number', 8),
            ('មេរោគកូលីហ្វម|Coliform Alert', 'PandL_subheader',["#Coliform Monthly"], 'number', 8),
            ('អន្តរាគមន៍មិនគ្រោងទុក|Unplanned int.', 'PandL_subheader',["Unplanned int. Monthly"], 'number', 8)
            ]
            },
            {
            'title': ('C', 'ព័ត៌មានប្រចាំឆ្នាំ|YTD info', 'PandL_header', 24),
            'rows': [
            ('ដប/ថ្ងៃ|Bot/day', 'PandL_subheader',["Bottle day YTD"], 'number', 8),
            ('មេរោគអេកូលី|E. Coli Alert', 'PandL_subheader',["#E.coli YTD"], 'number', 8),
            ('មេរោគកូលីហ្វម|Coliform Alert', 'PandL_subheader', ["#Coliform YTD"], 'number', 8),
            ('អន្តរាគមន៍មិនគ្រោងទុក|Unplanned int.', 'PandL_subheader',["Unplanned int. YTD"], 'number', 8)
            ]
            },
            {
            'title': ('E', 'គុណភាពទឹកឆៅ|Raw water qual.', 'PandL_header', 24),
            'rows': [
            ('pH|pH', 'PandL_subheader',["Raw water pH"], 'number', 8),
            ('ភាពល្អក់|Turbidity', 'PandL_subheader',["Raw water turbidity"], 'number', 8),
            ('ភាពចម្លងអគ្គិសនី|Conductivity', 'PandL_subheader',["Raw water conductivity"], 'number', 8),
            ('សារធាតុរឹងរលាយ|TDS', 'PandL_subheader',["Raw water TDS"], 'number', 8)
            ]
            },
            {
            'title': ('G', 'គុណភាពទឹកផឹក|Drinking water qual.', 'PandL_header', 28),
            'rows': [
            ('pH|pH', 'PandL_subheader',["Drink. water pH"], 'number', 8),
            ('ភាពល្អក់|Turbidity', 'PandL_subheader',["Drink. water turbidity"], 'number', 8),
            ('ភាពចម្លងអគ្គិសនី|Conductivity', 'PandL_subheader',["Drink. water conductivity"], 'number', 8),
            ('សារធាតុរឹងរលាយ|TDS', 'PandL_subheader',["Drink. water TDS"], 'number', 8)
            ]
            }
        ]

        for block in blocks:
            title_col, title_text, format_header, size_header = block['title']
            kh_title, en_title = title_text.split('|')
            value_col = chr(ord(title_col) + 1)
            ws.merge_range(f"{title_col}{start_row}:{value_col}{start_row}", f'=IF({cell_language}="Khmer","{kh_title}","{en_title}")', fmt[format_header])
            ws.set_column(f'{title_col}:{title_col}', size_header / 2)
            # Set the next column (value_col) to size_header / 2
            ws.set_column(f'{value_col}:{value_col}', size_header / 2)
            row_num = start_row
            for label_text, format_subheader,matching_header, format_formula, size_formula in block['rows']:
                row_num += 1
                kh, en = label_text.split('|') if '|' in label_text else (label_text, label_text)
                label_cell = f"{title_col}{row_num}"
                
                value_cell = f"{value_col}{row_num}"

                # Convert matching_header to column letters
                matching_columns = [col_letter_from_header(header) for header in matching_header]
                if len(matching_columns) > 1:
                    formula = " / ".join(f"INDEX({base}{col}2:{col}{site_count},{match})" for col in matching_columns)
                else:
                    formula = f"=INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count},{match})"

                ws.write_formula(label_cell, f'=IF({cell_language}="Khmer","{kh}","{en}")', fmt[format_subheader])
                

                ws.write_formula(value_cell, formula, fmt[format_formula])

    def write_assessment_routine(ws, fmt, start_row=9, start_col=6):
        site_count = len(ListSiteActive) + 2
        base = "'Data Month Site Analysis'!"
        match = f"MATCH('Site Analysis'!O2,{base}A2:A{site_count},0)"
        blocks = [
            {
                'title': ('ព័ត៌មានបច្ចេកទេស|Site assessment', 'PandL_header'),
                'rows': [
                    ('ការវាយតម្លៃទីតាំងចុងក្រោយ|Last assessment', 'PandL_subheader', ['Date Assessment'], 'date', 8, False),
                    ('ប្រភពអគ្គិសនី|Electricity source', 'PandL_subheader', ["Main source of electricity"], 'small_text', 8, False),
                    ('ប្រភពទឹក|Water source', 'PandL_subheader', ["Main source of water"], 'small_text', 8, True),
                    ('ប្រភពទឹកទី២|2nd water source', 'PandL_subheader', ["Second source of water"], 'small_text', 8, True),
                    ('ការកូទឹក|Flocculation', 'PandL_subheader', ["Flocculation and coagulation process"], 'small_text', 8, False),
                    ('RO|RO', 'PandL_subheader', ["Reverse osmosis"], 'small_text', 8, False),
                    ('UF|UF', 'PandL_subheader', ["Ultrafiltration"], 'small_text', 8, False),
                    ('អំពូលយូវី|UV lamp', 'PandL_subheader', ["UV lamp"], 'small_text', 8, False),
                    ('ស្ថានភាពអំពុលយូវី|UV lamp condition', 'PandL_subheader', ['UV lamp condition'], 'small_text', 8, False),
                    ('ប្រព័ន្ធបញ្ជារយូវី|UV controller', 'PandL_subheader', ['UV controller'], 'small_text', 8, True),
                    ('បាឡាសយូវី|UV ballast', 'PandL_subheader', ['UV ballast'], 'small_text', 8, True),
                    ('ម៉ូទ័រទឹកឆៅ|Raw water pump', 'PandL_subheader', ['Raw water pump'], 'small_text', 8, False),
                    ('ម៉ូទ័រទឹកស្អាត|Back wash pump', 'PandL_subheader', ['Back wash pump'], 'small_text', 8, False),
                    ('ម៉ូទ័រចម្រោះសីតុណ្ហភាពតូច|Micro filter pump', 'PandL_subheader', ['Micro filter pump'], 'small_text', 8, False)
                ]
            },
            {
                'title': ('Routine Check|Routine Check', 'PandL_header'),
                'rows': [
                    ('ត្រួតពិនិត្យចុងក្រោយ|Last check', 'PandL_subheader', ['Last check'], 'date', 8, False),
                    ('ការវាស់លំហូរទឹក|Flow measured', 'PandL_subheader', ['Flow measured'], 'small_text', 8, False),
                    ('ចម្រោះខ្សាច់|Sand filter', 'PandL_subheader', ['Sand filter'], 'small_text', 8, True),
                    ('ចម្រោះធ្យូង|AC filter', 'PandL_subheader', ['AC filter'], 'small_text', 8, True)
                ]
            }
        ]

        for block_idx, block in enumerate(blocks):
            title_text, format_header = block['title']
            kh_title, en_title = title_text.split('|')
            # Offset each block by block_height rows to stack vertically
            block_col = start_col
            row_num = start_row
            title_col = xl_col_to_name(block_col)
            value_col = chr(ord(title_col) + 1)
            ws.merge_range(f"{title_col}{row_num}:{value_col}{row_num}", f'=IF({cell_language}="Khmer","{kh_title}","{en_title}")', fmt[format_header])
            for label_text, format_subheader, matching_header, format_formula, size_formula, split in block['rows']:
                row_num += 1
                kh, en = label_text.split('|') if '|' in label_text else (label_text, label_text)
                label_cell = f"{title_col}{row_num}"
                value_cell = f"{value_col}{row_num}"

                # Convert matching_header to column letters
                matching_columns = [col_letter_from_header(header) for header in matching_header]
                if split == True:
                    formula = (
                        f'=IFERROR('
                        f'IF(D2="English", '
                        f'RIGHT(INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count}, '
                        f'MATCH(O2, {base}A2:A{site_count}, 0)), '
                        f'LEN(INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count}, '
                        f'MATCH(O2, {base}A2:A{site_count}, 0))) - FIND("/", INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count}, '
                        f'MATCH(O2, {base}A2:A{site_count}, 0)))), '
                        f'LEFT(INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count}, '
                        f'MATCH(O2, {base}A2:A{site_count}, 0)), '
                        f'FIND("/", INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count}, '
                        f'MATCH(O2, {base}A2:A{site_count}, 0))) - 1)),"")'
                    )
                else:
                    formula = f"=INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count},{match})"

                ws.write_formula(label_cell, f'=IF({cell_language}="Khmer","{kh}","{en}")', fmt[format_subheader])
                ws.write_formula(value_cell, formula, fmt[format_formula])
                
            block_height = len(block['rows']) + 1
            start_row += (block_idx+1) * block_height

    def write_pretreatment_dynamic(ws, fmt, start_row=8, raw_sheet_name='raw pretreatment info', col_map=None):
        """Render dynamic pretreatment chain from the one-row-per-site raw sheet.

        Displayed layout:
        Step | Process | Type | Volume (for steps 1..7)

        Process & Type values may contain a bilingual "Khmer/English" pattern.
        We show LEFT part if language = Khmer else RIGHT part when a slash is present.
        """
        if col_map is None:
            # Reconstruct assuming standard layout
            col_map = {}
            for step in range(1,8):
                base_idx = 1 + (step-1)*3
                col_map[step] = {
                    'process': xl_col_to_name(base_idx),
                    'type': xl_col_to_name(base_idx+1),
                    'vol': xl_col_to_name(base_idx+2)
                }
        # Title bilingual
        ws.merge_range(start_row, 0, start_row,5, f"=IF({cell_language}=\"Khmer\",\"ខ្សែសង្វាក់មុនព្យាបាល\",\"Pretreatment Chain\")", fmt['Green_header'])
        # Headers bilingual
        header_row = start_row + 1
        headers = [
            ("ជំហាន","Step"),
            ("ដំណើរការ","Process"),
            ("ប្រភេទ","Type"),
            ("មាឌ (L)","Volume (L)"),
            ("","Height (cm)"),
            ("","Diameter (cm)")
        ]
        for c,(kh,en) in enumerate(headers):
            ws.write_formula(header_row,c, f"=IF({cell_language}=\"Khmer\",\"{kh}\",\"{en}\")", fmt['Green_subheader'])
        cell_site_sel = cell_site
        for step in range(1,8):
            row_out = start_row + 1 + step
            ws.write(row_out,0,step,fmt['small_text'])
            proc_col = col_map[step]['process']
            type_col = col_map[step]['type']
            vol_col = col_map[step]['vol']
            proc_index = f"INDEX('{raw_sheet_name}'!${proc_col}:${proc_col},MATCH('Site Analysis'!{cell_site_sel},'{raw_sheet_name}'!$A:$A,0))"
            type_index = f"INDEX('{raw_sheet_name}'!${type_col}:${type_col},MATCH('Site Analysis'!{cell_site_sel},'{raw_sheet_name}'!$A:$A,0))"
            vol_index = f"INDEX('{raw_sheet_name}'!${vol_col}:${vol_col},MATCH('Site Analysis'!{cell_site_sel},'{raw_sheet_name}'!$A:$A,0))"
            # Process: blank if empty/0; split Khmer/English when slash present
            proc_formula = (
                f"=IFERROR(IF({proc_index}=\"\" ,\"\",IF(OR({proc_index}=0,{proc_index}=\"\"),\"\",IF(ISNUMBER(SEARCH(\"/\",{proc_index})),"
                f"IF({cell_language}=\"Khmer\",LEFT({proc_index},FIND(\"/\",{proc_index})-1),RIGHT({proc_index},LEN({proc_index})-FIND(\"/\",{proc_index}))),{proc_index}))),\"\")"
            )
            # Type: only if process cell (col B) not blank
            type_formula = (
                f"=IF($B{row_out+1}=\"\",\"\",IFERROR(IF({type_index}=\"\",\"\",IF(OR({type_index}=0,{type_index}=\"\"),\"\",IF(ISNUMBER(SEARCH(\"/\",{type_index})),"
                f"IF({cell_language}=\"Khmer\",LEFT({type_index},FIND(\"/\",{type_index})-1),RIGHT({type_index},LEN({type_index})-FIND(\"/\",{type_index}))),{type_index}))),\"\"))"
            )
            # Volume: show blank if 0 or empty
            vol_formula = (
                f"=IF($B{row_out+1}=\"\",\"\",IFERROR(IF(OR({vol_index}=\"\",{vol_index}=0),\"\",{vol_index}),\"\"))"
            )
            ws.write_formula(row_out,1,proc_formula,fmt['small_text'])
            ws.write_formula(row_out,2,type_formula,fmt['small_text'])
            ws.write_formula(row_out,3,vol_formula,fmt['small_text'])
        # Conditional formatting: light grey fill for blanks in Process/Type/Volume
        first_data_row = start_row + 2
        last_data_row = start_row + 8
        ws.conditional_format(first_data_row,1,last_data_row,3,{
            'type':'blanks',
            'format': fmt['blank_light']
        })
 
    def create_graph_contamination(workbook, sheet_name1, sheet_name2):
        chart = workbook.add_chart({'type': 'column'})

        Color = ["#D0E4F7", "#91C3EB", "#519FD9", "#1F78B4", "#0A4C8A"]
        col_start = 1
        col_end = col_start + Current_date.month - 1 
        col_range = (xl_col_to_name(col_start), xl_col_to_name(col_end))
        
        # Add series for data from sheet_name1
        chart.add_series({
            'name': f"Bottle",
            'categories': f"='{sheet_name1}'!{col_range[0]}1:{col_range[1]}1",
            'values': f"='{sheet_name1}'!{col_range[0]}2:{col_range[1]}2",
            'fill': {'color': Color[0]},
            'border': {'none': True},
            'gap': 30
        })
        
        # Add series for data from sheet_name2
        chart.add_series({
            'name': f"Machine",
            'categories': f"='{sheet_name2}'!{col_range[0]}1:{col_range[1]}1",
            'values': f"='{sheet_name2}'!{col_range[0]}2:{col_range[1]}2",
            'fill': {'color': Color[1]},
            'border': {'none': True},
            'gap': 30
        })
        chart.set_legend({'position': 'right', 'font': {'name': 'Arial Unicode MS','size':6}})
        chart.set_y_axis({'name': 'Contamination Level', 'major_unit': 1})  # Set Y axis interval to 1
        chart.set_size({'width': 741, 'height': 220})
        return chart
    
    def create_graph_aluturb(workbook, sheet_name1, sheet_name2): 
    # Base chart (column type for Aluminium)
        chart = workbook.add_chart({'type': 'column'})

        # Second chart (line type for Turbidity)
        line_chart = workbook.add_chart({'type': 'line'})

        # Define colors
        Color_Aluminium = "#1F78B4"  # Blue
        Color_Turbidity = "#FF0000"  # Red

        col_start = 1
        col_end = col_start + Current_date.month - 1 
        col_range = (xl_col_to_name(col_start), xl_col_to_name(col_end))

        # Aluminium series (on primary Y-axis)
        chart.add_series({
            'name': f"Aluminium",
            'categories': f"='{sheet_name1}'!{col_range[0]}1:{col_range[1]}1",
            'values': f"='{sheet_name1}'!{col_range[0]}2:{col_range[1]}2",
            'fill': {'color': Color_Aluminium},
            'border': {'none': True},
            'y2_axis': False,
            'gap': 30 
        })

        # Turbidity series (on secondary Y-axis, line chart)
        line_chart.add_series({
            'name': f"Turbidity",
            'categories': f"='{sheet_name2}'!{col_range[0]}1:{col_range[1]}1",
            'values': f"='{sheet_name2}'!{col_range[0]}2:{col_range[1]}2",
            'y2_axis': True,
            'line': {'color': Color_Turbidity},
            'marker': {
                'type': 'circle',
                'size': 5,
                'border': {'color': Color_Turbidity},
                'fill': {'color': Color_Turbidity}
            }
        })

        # Combine the charts
        chart.combine(line_chart)

        chart.set_legend({'position': 'right', 'font': {'name': 'Arial Unicode MS','size':6}})

        # Set axes
        chart.set_y_axis({'name': 'Aluminium', 'major_gridlines': {'visible': False}, 'num_font': {'size': 9}})
        chart.set_y2_axis({
                        'name': 'Turbidity',
                        'major_gridlines': {'visible': False},
                        'visible': True
                    })


        # Set size
        chart.set_size({'width': 533, 'height': 220})

        return chart
    
    def create_graph_water_production(workbook, sheet_name1):
        chart = workbook.add_chart({'type': 'line'})

        col_start = 1
        col_end = col_start + Current_date.month - 1 
        col_range = (xl_col_to_name(col_start), xl_col_to_name(col_end))
        
        # Add series for data from sheet_name1
        chart.add_series({
            'name': f"Water production (L)",
            'categories': f"='{sheet_name1}'!{col_range[0]}1:{col_range[1]}1",
            'values': f"='{sheet_name1}'!{col_range[0]}2:{col_range[1]}2",
        })

        chart.set_legend({'position': 'right'})
        chart.set_title({'none': True})  # Remove the title

        chart.set_size({'width': 741, 'height': 220})
        return chart
    
    def create_graph_intervention(workbook, ws_summary):
        # Create a stacked column chart
        chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})

        # Define the range for the months
        col_start = 1
        col_end = col_start + Current_date.month - 1
        col_range = (xl_col_to_name(col_start), xl_col_to_name(col_end))

        # Fetch all intervention types
        all_interventions = [row[0] for row in fetch_query(*query_map['InterventionList'])]

        # Dynamically generate unique patterns for any number of intervention types
        # Start with a set of base patterns, then generate new ones if needed
        base_patterns = [
            {'pattern': 1, 'fg_color': '#000000'},  # Solid black
            {'pattern': 1, 'fg_color': '#FFFFFF'},  # Solid white
            {'pattern': 2, 'fg_color': '#C0C0C0'},  # Medium gray
            {'pattern': 3, 'fg_color': '#808080'},  # Dark gray
            {'pattern': 4, 'fg_color': '#E0E0E0'},  # Light gray
            {'pattern': 5, 'fg_color': '#000000'},  # Dark horizontal
            {'pattern': 6, 'fg_color': '#000000'},  # Dark vertical
            {'pattern': 7, 'fg_color': '#000000'},  # Dark down
            {'pattern': 8, 'fg_color': '#000000'},  # Dark up
            {'pattern': 9, 'fg_color': '#000000'},  # Dark grid
            {'pattern': 10, 'fg_color': '#000000'}, # Dark trellis
            {'pattern': 11, 'fg_color': '#000000'}, # Light horizontal
        ]
        patterns = []
        for i in range(len(all_interventions)):
            if i < len(base_patterns):
                patterns.append(base_patterns[i])
            else:
                # Generate a new pattern by cycling through available pattern numbers and generating a new gray shade
                pattern_num = (i % 18) + 1  # Excel supports pattern 1-18
                # Generate a gray color based on the index
                gray = 32 + (i * 32) % 224
                hex_gray = f"#{gray:02X}{gray:02X}{gray:02X}"
                patterns.append({'pattern': pattern_num, 'fg_color': hex_gray})

        # Add a series for each intervention type
        for row_idx, intervention in enumerate(all_interventions, start=2):
            pattern = patterns[(row_idx - 2) % len(patterns)]
            chart.add_series({
            'name': f"='{ws_summary.get_name()}'!A{row_idx + 1}",
            'categories': f"='{ws_summary.get_name()}'!{col_range[0]}2:{col_range[1]}2",
            'values': f"='{ws_summary.get_name()}'!{col_range[0]}{row_idx + 1}:{col_range[1]}{row_idx + 1}",
            'fill': pattern,
            'border': {'none': True},
            'gap': 30  # Reduce gap width to 30%
            })

        chart.set_legend({
            'position': 'right',
            'font': {'size': 8},  # Slightly larger font for readability
        })
        chart.set_y_axis({
            'name': 'Number of Interventions',
            'major_unit': 1,  # Set Y axis interval to 1
        })
        chart.set_x_axis({'name': 'Months'})
        chart.set_size({'width': 741, 'height': 278})
        chart.set_title({'name': 'Intervention Types by Month'})

        return chart

    # Add worksheets for different sections of the report
    (   worksheet_site_analysis, 
        worksheet_data_months, 
        worksheet_contamination_bottle, 
        worksheet_contamination_machine, 
        worksheet_list_intervention, 
        worksheet_site_intervention,
        worksheet_alu,
        worksheet_turb,
        worksheet_water_consumption
    ) = add_worksheet()
    fmt = format_factory(workbook)
    fetched, query_map = query(Current_date)
    cell_language = "D2"
    cell_site = "O2"
    cell_platform_title = "E2"
    cell_platform = "F2"
    cell_technician_title = "G2"
    cell_technician = "H2"

    ListSiteActive = listSiteStillActive(Current_date,Current_date-relativedelta(months=12))
    #Monthly Data tab
    headers_month_tab = raw_data_month_header()
    worksheet_data_months.write_row(0, 0, headers_month_tab)
    for i, site_row in enumerate(ListSiteActive):
        site_id = site_row[0]
        write_raw_data_month(worksheet_data_months, i + 1, site_id)

    #Write water consumption tab
    write_data_water_consumption(worksheet_water_consumption)

    #Write contamination tabs
    write_data_contamination(worksheet_contamination_bottle,0)
    write_data_contamination(worksheet_contamination_machine,1)

    #Write technical intervention tabs
    write_intervention_type(worksheet_list_intervention)
    write_intervention_summary(worksheet_site_intervention, worksheet_list_intervention)

    #Write Alu Turbidity tabs
    write_data_aluturb(worksheet_alu,0)
    write_data_aluturb(worksheet_turb,1)

    #Write Site Analysis
    title_language(worksheet_site_analysis,"A2",cell_language,cell_site,cell_platform_title,cell_platform,cell_technician_title,cell_technician,fmt)
    write_site_analysis_header(worksheet_site_analysis, fmt)
    write_quality_technical_performance(worksheet_site_analysis, fmt)
    write_assessment_routine(worksheet_site_analysis, fmt)
    # Build raw pretreatment data sheet then render dynamic view
    _raw_sheet_name, _col_map = write_data_pretreatment()
    write_pretreatment_dynamic(worksheet_site_analysis, fmt, start_row=8, raw_sheet_name=_raw_sheet_name, col_map=_col_map)
    chart_contamination = create_graph_contamination(workbook, worksheet_contamination_bottle.get_name(), worksheet_contamination_machine.get_name())
    worksheet_site_analysis.insert_chart('A29', chart_contamination)
    chart_aluturb = create_graph_aluturb(workbook, worksheet_alu.get_name(), worksheet_turb.get_name())
    worksheet_site_analysis.insert_chart('A18', chart_aluturb)
    chart_intervention = create_graph_intervention(workbook, worksheet_site_intervention)
    worksheet_site_analysis.insert_chart('A40', chart_intervention)
    
    #create_chart_data(workbook, worksheet_site_analysis)

    

