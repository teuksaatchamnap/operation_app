
import xlsxwriter
from monthlyreport.Functionutils import CategoryExpenses,exchange_rate_year,ConsumableType
from datetime import date
import tempfile
import db
from dateutil.relativedelta import *
from xlsxwriter.utility import xl_col_to_name,xl_rowcol_to_cell
import flask
from collections import defaultdict

def CreateworkbookSiteAnalysis():
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir()+'/Site Analysis '+Year+'-'+Month+'.xlsm'
    workbook = xlsxwriter.Workbook(filepath)
    return(workbook)

def SiteAnalysis(ListTier, ListSiteActive, workbook, Current_date, F2F):

    con = db.pool.connect()

    # Set formatting styles
    def format_factory(workbook):
        fmt = {}
        fmt['empty'] = workbook.add_format({'bg_color': '#D9D9D9'})
        fmt['empty_with_line'] = workbook.add_format({'bg_color': '#D9D9D9', 'left': 12})
        fmt['normal_num'] = workbook.add_format({'num_format': '#,###,##0'})
        fmt['dollar'] = workbook.add_format({'num_format': '$#,###,##0'})
        fmt['riel'] = workbook.add_format({'num_format': '៛#,###,##0'})
        fmt['number'] = workbook.add_format({'bg_color': '#DCE6F1', 'num_format': '#,###,##0', 'align': 'right'})
        fmt['percentage'] = workbook.add_format({'bg_color': '#DCE6F1', 'num_format': '0.0%'})
        fmt['merge'] = workbook.add_format({'font_color': 'red', 'center_across': True, 'bold': True, 'font_size': 16, 'underline': True})
        fmt['bold'] = workbook.add_format({'font_size': '12', 'bold': True})
        fmt['bg_red'] = workbook.add_format({'bg_color': '#FFC7CE', 'bold': True})
        fmt['Green_header'] = workbook.add_format({'bg_color': '#76933C', 'font_color':'#FFFFFF','bold': True, 'align': 'center', 'valign': 'vcenter'})
        fmt['Green_header_line'] = workbook.add_format({'bg_color': '#76933C', 'font_color':'#FFFFFF','bold': True, 'align': 'center', 'valign': 'vcenter', 'left': 12})
        fmt['Green_subheader'] = workbook.add_format({'bg_color': '#D8E4BC','italic': True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['Green_subheader_line'] = workbook.add_format({'bg_color': '#D8E4BC', 'italic': True, 'align': 'center', 'valign': 'vcenter','font_size': 10, 'left': 12 })
        fmt['Green_subheader_date'] = workbook.add_format({'bg_color': '#D8E4BC','italic': True, 'align': 'center', 'valign': 'vcenter','font_size':10,'num_format':'mmm-yy'})
        fmt['PandL_header'] = workbook.add_format({'bg_color': '#203764', 'font_color':'#FFFFFF','bold': True, 'align': 'center', 'valign': 'vcenter'})
        fmt['PandL_subheader'] = workbook.add_format({'bg_color': '#DCE6F1','italic': True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['PandL_subheader_bold'] = workbook.add_format({'num_format':'#,###,##0','bg_color': '#DCE6F1','bold': True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['PandL_number']= workbook.add_format({"num_format" : '#,###,##0','italic':True, 'align': 'center', 'valign': 'vcenter','font_size':10})
        fmt['Select_format'] = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
        return fmt
    
    def add_worksheet():
        worksheet_site_analysis = add_ws("Site Analysis")
        worksheet_site_analysis.hide_gridlines(2)
        worksheet_site_analysis.print_area('A1:H45')
        worksheet_site_analysis.set_margins(left=0.25, right=0.25, top=0.5, bottom=0.5)
        worksheet_data_months = add_ws("Data Month Site Analysis", True)
        worksheet_data_historic = add_ws("Data Lday Site Analysis", True)
        worksheet_expenses = add_ws("Expenses", True)
        worksheet_mix = add_ws("Mix", True)
        return worksheet_site_analysis, worksheet_data_months, worksheet_data_historic, worksheet_expenses,worksheet_mix

    def add_ws(name, hidden=False):
        ws = workbook.add_worksheet(name)
        if hidden:
            ws.hide()
        return ws

    def query():
        Bottle_code = ConsumableType()[1]
        query_map = {
            'Sites': "SELECT Id_Site, Platform, Advisor, Number_Population, Number_Households, Entrepreneur_English_Name, Date_start_working"
            " FROM Sites",
            'SchoolBudget': "SELECT Id_Site, SchoolSalesBudget FROM Sites",
            'Sales': ("SELECT Id_Site, Total_income, Total_sales - Bottle_Sales, Hod_Sales, Hod_Price, "
                "Shopkeeper_Sales, Shopkeeper_Price, WiS_Sales, WiS_Price, Onsite_Sales, Onsite_Price, "
                "Free_Sales, Number_open_days, WiS_Income,"
                "(Total_Sales- Bottle_Sales)/Number_open_days,"
                "(Total_Sales - Bottle_Sales - WiS_Sales)/Number_open_days FROM Sales WHERE Month = %s", Current_date),
            'Sales_M_1': ("SELECT Id_Site, SUM(Total_sales - Bottle_Sales - WiS_Sales), SUM(Total_Income-WiS_Income), SUM(WiS_Income) "
                "FROM Sales WHERE Month = %s GROUP BY Id_Site", Current_date-relativedelta(months=+1)),
            'SalesYTD': ("SELECT Id_Site, SUM(Total_sales - Bottle_Sales - WiS_Sales), SUM(Total_Income-WiS_Income), SUM(WiS_Income), "
                "SUM(Total_sales - Bottle_Sales - WiS_Sales)/SUM(Number_open_days) FROM Sales WHERE Month <= %s AND Month >= %s "
                "GROUP BY Id_Site", Current_date, date(Current_date.year, 1, 1)),
            'SalesYTD_N_1': ("SELECT Id_Site, SUM(Total_sales - Bottle_Sales - WiS_Sales), SUM(Total_Income-WiS_Income), SUM(WiS_Income) "
                "FROM Sales WHERE Month <= %s AND Month >= %s GROUP BY Id_Site", Current_date-relativedelta(months=+12), date(Current_date.year-1, 1, 1)),
            'Beneficiaries': ("SELECT Id_Site, Beneficiaries FROM Beneficiaries WHERE Month = %s GROUP BY Id_Site", Current_date),
            'IndicatorsOp': ("SELECT Id_Site, Number_of_operator FROM Indicators WHERE Month = %s", Current_date),
            'IndicatorsWater': ("SELECT Id_Site, Water_consume FROM Indicators WHERE Month = %s", Current_date),
            'WinSAvg': ("SELECT Id_Site, AVG(WiS_Sales) FROM DailySales WHERE Month >= %s AND Month < %s GROUP BY Id_Site", Current_date, Current_date + relativedelta(months=+1)),
            'HistoricSales': (
            "SELECT Id_Site, Month, Total_Sales - Bottle_Sales - WiS_Sales, Number_open_days "
            "FROM Sales WHERE Month >= %s AND Month <= %s",
            date_start_historic, Current_date
            ),
            'Debt': ("SELECT Id_Site, - Amount_Expenses FROM Expenses "
            "WHERE Month = %s AND Ref_expenses = 'debt' GROUP BY Id_Site", Current_date),
            'BottlesYTD':("SELECT Id_Site, SUM(Number_Item) FROM Consumable "
                "WHERE Month <=%s AND Month >= %s AND Item in %s "
                "GROUP BY Id_Site",Current_date, date(Current_date.year,1,1),Bottle_code),
            'BottlesN_1':("SELECT Id_Site, SUM(Number_Item) FROM Consumable "
                "WHERE Month <=%s AND Month >= %s AND Item in %s "
                "GROUP BY Id_Site",Current_date-relativedelta(months=12), date(Current_date.year-1,1,1),Bottle_code),
            'EntrepreneurProfile': ("SELECT ep.Id_Site, ep.Entrepreneur_English_name, ep.Working_Date "
                "FROM entrepreneur_profiles ep "
                "INNER JOIN ( "
                    "SELECT Id_Site, MAX(Submitted_Date) AS Max_Submitted_Date "
                    "FROM entrepreneur_profiles "
                    "WHERE Status = 'new_entrepreneur_coming' AND Submitted_Date <= %s "
                    "GROUP BY Id_Site "
                ") latest ON ep.Id_Site = latest.Id_Site AND ep.Submitted_Date = latest.Max_Submitted_Date "
                "WHERE ep.Status = 'new_entrepreneur_coming'", Current_date),
            'Expenses': ("SELECT Id_Site, SUM(Amount_expenses), "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END AS Category_expenses "
                "FROM Expenses WHERE Month = %s AND Category_expenses IN %s "
                "GROUP BY Id_Site, "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END "
                "ORDER BY Id_Site, Category_expenses", 
                Current_date, Category_expenses
            ),
            'Expenses_M_1': ("SELECT Id_Site, SUM(Amount_expenses), "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END AS Category_expenses "
                "FROM Expenses WHERE Month = %s AND Category_expenses IN %s "
                "GROUP BY Id_Site, "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END "
                "ORDER BY Id_Site, Category_expenses", 
                Current_date-relativedelta(months=+1), Category_expenses
            ),
            'Expenses_YTD': ("SELECT Id_Site, SUM(Amount_expenses), "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END AS Category_expenses "
                "FROM Expenses WHERE Month <= %s AND Month >= %s AND Category_expenses IN %s "
                "GROUP BY Id_Site, "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END "
                "ORDER BY Id_Site, Category_expenses", 
                Current_date,date(Current_date.year,1,1),Category_expenses
            ),
            'Expenses_YTD_N_1': ("SELECT Id_Site, SUM(Amount_expenses), "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END AS Category_expenses "
                "FROM Expenses WHERE Month <= %s AND Month >= %s AND Category_expenses IN %s "
                "GROUP BY Id_Site, "
                "CASE "
                "WHEN Ref_expenses = 'fix_salary_entrepreneurs' OR Ref_expenses = 'variable_salary_entrepreneurs' THEN 'salary entrepreneur' "
                "WHEN Ref_expenses = 'fix_salary_operators' OR Ref_expenses = 'variable_salary_operators' THEN 'salary operator' "
                "ELSE Category_expenses "
                "END "
                "ORDER BY Id_Site, Category_expenses", 
                Current_date-relativedelta(months=+12), date(Current_date.year-1,1,1), Category_expenses
            ) 
        }
        print(Current_date,Current_date-relativedelta(months=+12))

        fetched = {k: fetch_dict(fetch_query(*v)) if (k != 'HistoricSales') and isinstance(v, tuple) else fetch_dict(fetch_query(v))
                for k, v in query_map.items() if (k != 'HistoricSales') }
        
        def process_expenses(raw_data):
            processed = {}
            for site_id, amount, category in raw_data:
                if site_id not in processed:
                    processed[site_id] = {}
                processed[site_id][category] = amount
            return processed
        
        expenses_raw = fetch_query(*query_map['Expenses'])
        expenses_m_1_raw = fetch_query(*query_map['Expenses_M_1'])
        expenses_ytd_raw = fetch_query(*query_map['Expenses_YTD'])
        expenses_ytd_n_1_raw = fetch_query(*query_map['Expenses_YTD_N_1'])

        fetched['Expenses'] = process_expenses(expenses_raw)
        fetched['Expenses_M_1'] = process_expenses(expenses_m_1_raw)
        fetched['Expenses_YTD'] = process_expenses(expenses_ytd_raw)
        fetched['Expenses_YTD_N_1'] = process_expenses(expenses_ytd_n_1_raw)

        return fetched, query_map

    def add_button(ws, cell, macro, caption):
        ws.insert_button(cell, {'macro': macro, 'caption': caption, 'width': 80, 'height': 30})
    
    def add_vba(ws):
        workbook.add_vba_project(flask.current_app.root_path + '/static/VBA/vbaProject.bin')
        buttons = [("L4", "ThisWorkbook.BoutonAll", "Print All"),
                    ("L6", "ThisWorkbook.BoutonBTB", "Print BTB"),
                    ("L8", "ThisWorkbook.BoutonPP", "Print PP"),
                    ("L10", "ThisWorkbook.BoutonKC", "Print KC"),
                    ("L12", "ThisWorkbook.BoutonSR", "Print SR")]
        for cell, macro, caption in buttons:
            add_button(ws, cell, macro, caption)

    def fetch_query(query, *args):
        return con.execute(query, args if args else ()).fetchall()

    def fetch_dict(data):
        return {row[0]: row for row in data}

    def write_data_monthly_data(ws, row_index, site_id):
        site_info = fetched['Sites'].get(site_id, (site_id, '', '', 0, 0, '', ''))
        sales_info = fetched['Sales'].get(site_id)
        sales_info_m_1 = fetched['Sales_M_1'].get(site_id)
        sales_ytd = fetched['SalesYTD'].get(site_id)
        sales_ytd_n_1 = fetched['SalesYTD_N_1'].get(site_id)
        beneficiaries = fetched['Beneficiaries'].get(site_id)
        operator = fetched['IndicatorsOp'].get(site_id)
        water = fetched['IndicatorsWater'].get(site_id)
        school_budget = fetched['SchoolBudget'].get(site_id)
        wins_avg = fetched['WinSAvg'].get(site_id)
        debt = fetched['Debt'].get(site_id, (site_id))
        bottle_bought_ytd = fetched['BottlesYTD'].get(site_id,{})
        bottle_bought_N_1 = fetched['BottlesN_1'].get(site_id,{})
        expense_data = fetched['Expenses'].get(site_id, {})
        expense_data_m_1 = fetched['Expenses_M_1'].get(site_id, {})
        expense_data_ytd = fetched['Expenses_YTD'].get(site_id, {})
        expense_data_ytd_n_1 = fetched['Expenses_YTD_N_1'].get(site_id, {})
        entrepreneur_profile = fetched['EntrepreneurProfile'].get(site_id)
        tier = next((t[1] for t in ListTier if t[0] == site_id), '')

        expense_categories = ["production", "salary entrepreneur", "salary operator", "delivery", "contribution", "investment", "technical"]
        expense_values = [expense_data.get(category, '') for category in expense_categories]
        expense_values_m_1 = [expense_data_m_1.get(category, '') for category in expense_categories]
        expense_values_ytd = [expense_data_ytd.get(category, '') for category in expense_categories]
        expense_values_ytd_n_1 = [expense_data_ytd_n_1.get(category, '') for category in expense_categories]

        ws.write_row(row_index + 1, 0, [
            site_info[0],  # Site
            site_info[1],  # Platform
            site_info[2],  # Advisor
            tier,  # Tier
            (entrepreneur_profile[1] if entrepreneur_profile else site_info[5]),  # Entrepreneur Name
            (entrepreneur_profile[2] if entrepreneur_profile else site_info[6]),  # Starting Date
            (sales_info[14] if sales_info else ''), # Bot Day
            (sales_info[15] if sales_info else ''), # Bot Day No WinS
            (sales_ytd[4] if sales_ytd else ''),    # Bot Day No WinS YTD
            (sales_info[2] if sales_info else ''),  # Total Sales
            (sales_info[3] if sales_info else ''),  # Hod Sales
            (sales_info[4] if sales_info else ''),  # Hod Price
            (sales_info[5] if sales_info else ''),  # Shopkeeper Sales
            (sales_info[6] if sales_info else ''),  # Shopkeeper Price
            (sales_info[7] if sales_info else ''),  # WiS Sales
            (sales_info[8] if sales_info else ''),  # WiS Price
            (sales_info[9] if sales_info else ''),  # Onsite Sales
            (sales_info[10] if sales_info else ''),  # Onsite Price
            (sales_info[11] if sales_info else ''),  # Free Sales
            (sales_info[12] if sales_info else ''),  # Open Days This Month
            site_info[3],  # Population
            (beneficiaries[1] if beneficiaries else ''),  # Beneficiaries
            site_info[4],  # Households
            (operator[1] if operator else ''),  # Number of Operators
            (school_budget[1] if school_budget else ''),  # School Budget
            (wins_avg[1] if wins_avg else ''),  # Daily WinS Sales
            ((water[1] / (sales_info[2] * 20) - 1) if water and water[1] is not None and sales_info and sales_info[2] else 0),  # Water Consumption
            (debt[1] if debt else ''),  # Debt
            (bottle_bought_ytd[1] if bottle_bought_ytd else ''), #Bottle bought YTD
            (bottle_bought_N_1[1] if bottle_bought_N_1 else ''), #Bottle bought Y-1
            (sales_info[1] - sales_info[7]*sales_info[8] if sales_info else ''),  # Income Sales
            (sales_info[7]*sales_info[8] if sales_info else ''),  # Income WinS
            *expense_values,  # Production, Salary Ent, Salary Op, Delivery, Contribution, Investment, Technical
            (sales_info_m_1[2] if sales_info_m_1 else ''),  # Income Sales M_1
            (sales_info_m_1[3] if sales_info_m_1 else ''),  # Income WinS M_1
            *expense_values_m_1,  # Production M_1, Salary Ent M_1, Salary Op M_1, Delivery M_1, Contribution M_1, Investment M_1, Technical M_1
            (sales_ytd[2] if sales_ytd else ''),  # Income Sales YTD
            (sales_ytd[3] if sales_ytd else ''),  # Income WinS YTD
            *expense_values_ytd,  # Production YTD, Salary Ent YTD, Salary Op YTD, Delivery YTD, Contribution YTD, Investment YTD, Technical YTD
            (sales_ytd_n_1[2] if sales_ytd_n_1 else ''),  # Income Sales N-1
            (sales_ytd_n_1[3] if sales_ytd_n_1 else ''),  # Income WinS N-1
            *expense_values_ytd_n_1  # Production N-1, Salary Ent N-1, Salary Op N-1, Delivery N-1, Contribution N-1, Investment N-1, Technical N-1
        ])

    def data_monthly_header():
        columns = ["Site", "Platform", "Advisor", "Tier", "Entrepreneur Name", "Starting Date",
                    "Bot Day", "Bot Day no WinS",
                   "Bot Day no WinS YTD","Total Sales", "Hod Sales", "Hod Price",
               "Shopkeeper Sales", "Shopkeeper Price", "WiS Sales", "WiS Price", "Onsite Sales",
               "Onsite Price", "Free Sales", "Open Days",
               "Population", "Beneficiaries", "Households", "Number of Operators", "School Budget",
               "Daily WinS Sales", "Water Consumption", "Debt", "Nb Bot bought YTD", "Nb Bot bought Y-1",
               "Income Sales", "Income WinS", "Production", "Salary Ent", "Salary Op", "Delivery",
               "Contribution", "Investment", "Technical", "Income Sales M_1", "Income WinS M_1",
               "Production M_1", "Salary Ent M_1", "Salary Op M_1", "Delivery M_1",
               "Contribution M_1", "Investment M_1", "Technical M_1", "Income Sales YTD",
               "Income WinS YTD", "Production YTD", "Salary Ent YTD", "Salary Op YTD",
               "Delivery YTD", "Contribution YTD", "Investment YTD", "Technical YTD",
               "Income Sales N_1", "Income WinS N_1", "Production N_1", "Salary Ent N_1",
               "Salary Op N_1", "Delivery N_1", "Contribution N_1", "Investment N_1",
               "Technical N_1"]
        return columns

    def write_data_botday(ws):
        ws.write(0, 0, "Site")
        current = date_start_historic
        col = 1
        all_historic_sales = fetch_query(*query_map['HistoricSales'])
        sales_cache = defaultdict(dict)
        for site_id, month, sales, days in all_historic_sales:
            sales_cache[site_id][month.date()] = (sales, days) if hasattr(month, 'date') else (sales, days)
        
        while current <= Current_date:
            ws.write(0, col, current.strftime('%b'))
            col += 1
            current += relativedelta(months=1)
        
        # Add a row to select data for the site from 'Site Analysis!O2'
        ws.write(1, 0, "Selected Site")
        current = date_start_historic
        col = 1
        while current <= Current_date:
            ws.write_formula(1, col, 
            f"=INDEX({xl_col_to_name(col)}3:{xl_col_to_name(col)}{len(ListSiteActive) + 2}, MATCH('Site Analysis'!O2, A3:A{len(ListSiteActive) + 2}, 0))", 
            fmt['number']
            )
            col += 1
            current += relativedelta(months=1)
        
        for row_idx, site_row in enumerate(ListSiteActive, start=2):
            site_id = site_row[0]
            ws.write(row_idx, 0, site_id)
            current = date_start_historic
            col = 1
            while current <= Current_date:
                values = sales_cache.get(site_id, {}).get(current)
                if values and values[1]:
                    ws.write(row_idx, col, values[0]/values[1])
                col += 1
                current += relativedelta(months=1)

    def write_expenses(ws,cell_exchange_rate,cell_language):
        headers = ["Salary", "Prod.", "Deliv.","Cont.","Other","School Budget"]
        matching_headers_monthly_data = [["Salary Ent", "Salary Op"], ["Production"], ["Delivery"], ["Contribution"],
                                 ["Technical","Investment"], ["School Budget"]]
        
        matching_category_query = [["salary entrepreneur","salary operator"], ["production"], ["delivery"],
                       ["contribution"], ["investment", "technical"]]
        
        consolidated_expenses = []
        for categories in matching_category_query:
            total = sum(
                fetched['Expenses'][site_id].get(category, 0)
                for site_id in fetched['Expenses']
                for category in categories
            )
            average = total / len(fetched['Expenses']) if fetched['Expenses'] else 0
            consolidated_expenses.append(average)
        
        for row, header in enumerate(headers):
            ws.write(row, 0, header)
            column_indices = [
                col_letter_from_header(entry)
                for entry in matching_headers_monthly_data[row]
            ]
            sum_formula = "+".join(
                f"INDEX('Data Month Site Analysis'!{col}2:{col}{len(ListSiteActive) + 2}, "
                f"MATCH('Site Analysis'!O2, 'Data Month Site Analysis'!A2:A{len(ListSiteActive) + 2}, 0)) "
                f"/'Site Analysis'!{cell_exchange_rate}"
                for col in column_indices
            )
            ws.write(row, 1, f"={sum_formula}",fmt['normal_num'])
            if row <= 4:
                ws.write(row, 2, f"={consolidated_expenses[row]}/'Site Analysis'!{cell_exchange_rate}", fmt['normal_num'])
            
            ws.conditional_format(f'B{row + 1}:C{row + 1}', {
                'type': 'formula',
                'criteria': f'=\'Site Analysis\'!{cell_language}="Khmer"',
                'format': fmt['riel']
            })
            ws.conditional_format(f'B{row + 1}:C{row + 1}', {
                'type': 'formula',
                'criteria': f'=\'Site Analysis\'!{cell_language}="English"',
                'format': fmt['dollar']
            })
    
    def write_mix(ws):
        matching_header = ["Hod Sales","Shopkeeper Sales","WiS Sales","Onsite Sales","Free Sales"]
        headers = ["Hod (>50%)", "Shop", "WinS", "Onsite", "Free"]
        for row, header in enumerate(matching_header):
            ws.write(row, 0, headers[row])
            col = col_letter_from_header(header)
            formula = [f"INDEX('Data Month Site Analysis'!{col}2:{col}{len(ListSiteActive) + 2}, "
                      f"MATCH('Site Analysis'!O2, 'Data Month Site Analysis'!A2:A{len(ListSiteActive) + 2}, 0))"]
            ws.write(row, 1, f"={formula[0]}", fmt['normal_num'])

    def title_language(ws,cell_language_name,cell_language,cell_site,cell_platform_title,cell_platform,cell_advisor_title,cell_advisor,cell_exchange_rate_name,cell_exchange_rate,fmt):
        site_count = len(ListSiteActive) + 2
        ws.merge_range('A1:H1', 'Site Analysis', fmt['merge'])
        ws.data_validation(cell_site, {'validate': 'list', 'source': f"'Data Month Site Analysis'!A2:A{site_count}"})
        try:
            ws.write(cell_site, ListSiteActive[0][0],fmt['Select_format'])
        except:
            ws.write(cell_site,"CHOOSE SITE",fmt['Select_format'])
        ws.write(cell_language_name, 'Select Language/ជ្រើសរើស​ភាសា', fmt['bold'])
        ws.data_validation(cell_language, {'validate': 'list', 'source': ['Khmer', 'English']})
        ws.write(cell_language, "English" if F2F else "Khmer", fmt['bold'])
        ws.write_formula(cell_platform_title, f'=IF({cell_language}="Khmer","តំបន់","Platform")', fmt['bold'])
        ws.write(cell_platform, f"=INDEX('Data Month Site Analysis'!B2:B{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['normal_num'])
        ws.write_formula(cell_advisor_title, f'=IF({cell_language}="Khmer","មន្ត្រីប្រឹក្សា","Advisor")', fmt['bold'])
        ws.write(cell_advisor, f"=INDEX('Data Month Site Analysis'!C2:C{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['normal_num'])
        ws.write(cell_exchange_rate_name,f"=IF({cell_language}=\"Khmer\",\"អត្រាប្តូរប្រាក់\",\"Exch. Rate\")", fmt['bold'])
        ws.write(cell_exchange_rate, f"=IF({cell_language}=\"Khmer\",1,{exchange_rate_year(Current_date)})", fmt['bold'])

    def write_site_analysis_header(ws, fmt):
        site_count = len(ListSiteActive) + 2
        headers = {
            'A3': 'កូដស្ថានីយ|Site code',
            'C3': 'ខែ|Month',
            'E3': 'ឈ្មោះសហគ្រិន|Ent. name',
            'G3': 'ថ្ងៃចាប់ផ្តើម|Starting date'
        }
        value = {
            'B3': ('=O2', fmt['Green_subheader']),
            'D3': (f'{Current_date}', fmt['Green_subheader_date']),
            'F3': (f"=INDEX('Data Month Site Analysis'!E2:E{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['Green_subheader']),
            'H3': (f"=INDEX('Data Month Site Analysis'!F2:F{site_count}, MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{site_count},0))", fmt['Green_subheader_date'])
        }
        for cell, val in headers.items():
            kh, en = val.split('|')
            ws.write_formula(cell, f'=IF(D2="Khmer","{kh}","{en}")',fmt['Green_header'])
        for cell, (val, format_type) in value.items():
            ws.write(cell, val, format_type)

    def col_letter_from_header(header):
        header_monthly_data = data_monthly_header()
        col = xl_col_to_name(header_monthly_data.index(header))
        return col
    
    def write_site_summary(ws, ListSiteActive, fmt, start_row=4):
        site_count = len(ListSiteActive) + 2
        base = "'Data Month Site Analysis'!"
        match = f"MATCH('Site Analysis'!O2,{base}A2:A{site_count},0)"
        rows = [
            # (label_col, label_text, format_header, size_header, value_col, matching_header, format_formula, size_formula, row_offset)
            ('A', 'ប៊ី/ថ្ងៃ អត់ទឹកសាលាចាប់ពីខែមករា|bot/day exc WinS YTD', 'PandL_header', 18, 'B', ["Bot Day no WinS YTD"], 'number', 9, 0),
            ('A', 'ប៊ី/ថ្ងៃ អត់ទឹកសាលា​ក្នុងខែនេះ|bottles/day exc WinS', 'PandL_header', 18, 'B', ["Bot Day no WinS"], 'number', 9, 1),
            ('A', 'ប៊ី/ថ្ងៃ ទាំងទឹកសាលា|bottles/day', 'PandL_header', 18, 'B', ["Bot Day"], 'number', 9, 2),
            ('C', 'ប៊ីដុងលក់សរុប|Tot sales (bottle)', 'PandL_header', 16, 'D', ["Total Sales"], 'number', 8, 0),
            ('C', 'កម្រិត|Tier', 'PandL_header', 16, 'D', ["Tier"], 'number', 8, 1),
            ('C', 'ចំនួនថ្ងៃបើកលក់|Days open', 'PandL_header', 16, 'D', ["Open Days"], 'number', 8, 2),
            ('E', 'ទឹកបាត់បង់|Over waste', 'PandL_header', 14, 'F', ["Water Consumption"], 'percentage', 10, 0),
            ('E', 'ចំនួនប្រតិបត្តិករ|Nb of Operator', 'PandL_header', 14, 'F', ["Number of Operators"], 'number', 10, 1),
            ('E', 'អអ្នកទទួលផល|Beneficiaries', 'PandL_header', 14, 'F', ["Beneficiaries"], 'number', 10, 2),
            ('G', 'ជ្រៀតចូលទីផ្សារ|Penetration', 'PandL_header', 13, 'H', ["Beneficiaries", "Population"], 'percentage', 8, 0),
            ('G', 'ប្រជាជនសរុប|Pop Commune', 'PandL_header', 13, 'H', ["Population"], 'number', 8, 1),
            ('G', 'គ្រួសារសរុប|Households ', 'PandL_header', 13, 'H', ["Households"], 'number', 8, 2),
        ]

        
        for label_col, label_text, format_header, size_header, value_col, matching_header, format_formula, size_formula, row_offset in rows:
            row_num = start_row + row_offset
            kh, en = label_text.split('|')
            label_cell = f"{label_col}{row_num}"
            value_cell = f"{value_col}{row_num}"

            # Convert matching_header to column letters
            matching_columns = [col_letter_from_header(header) for header in matching_header]
            if len(matching_columns) > 1:
                formula = " / ".join(f"INDEX({base}{col}2:{col}{site_count},{match})" for col in matching_columns)
            else:
                formula = f"=INDEX({base}{matching_columns[0]}2:{matching_columns[0]}{site_count},{match})"

            ws.write_formula(label_cell, f'=IF({cell_language}="Khmer","{kh}","{en}")', fmt[format_header])
            ws.set_column(f'{label_col}:{label_col}', size_header)

            ws.write_formula(value_cell, formula, fmt[format_formula])
            ws.set_column(f'{value_col}:{value_col}', size_formula)

            
        # Find the matching row
        tier_row = next((row for row in rows if "កម្រិត|Tier" in row[1]), None)
        print(tier_row)
        penetration_row = next((row for row in rows if "ជ្រៀតចូលទីផ្សារ|Penetration" in row[1]), None)
        operator_row = next((row for row in rows if "ចំនួនប្រតិបត្តិករ|Nb of Operator" in row[1]), None)
        water_consumption_row = next((row for row in rows if "ទឹកបាត់បង់|Over waste" in row[1]), None)
        # Add conditionnal formatting for tier 3
        tier_row_index = rows.index(tier_row)%3 + start_row
        tier_col = tier_row[4]
        ws.conditional_format(f'{tier_col}{tier_row_index}', {
            'type': 'cell',
            'criteria': '==',
            'value': 3,
            'format': fmt['bg_red']
        })
        #Add conditional formatting for penetration < 25%
        penetration_row_index = rows.index(penetration_row)%3 + start_row
        penetration_col = penetration_row[4]
        ws.conditional_format(f'{penetration_col}{penetration_row_index}', {
            'type': 'cell',
            'criteria': '<',
            'value': 0.25,
            'format': fmt['bg_red']
        })
        # Add conditional formatting for operator < 3
        operator_row_index = rows.index(operator_row)%3 + start_row
        operator_col = operator_row[4]
        ws.conditional_format(f'{operator_col}{operator_row_index}', {
            'type': 'cell',
            'criteria': '<',
            'value': 3,
            'format': fmt['bg_red']
        })
        # Add conditional formatting for Over Waste > 20%
        over_waste_row = rows.index(water_consumption_row)%3 + start_row
        over_waste_col = water_consumption_row[4]
        ws.conditional_format(f'{over_waste_col}{over_waste_row}', {
            'type': 'cell',
            'criteria': '>',
            'value': 0.2,
            'format': fmt['bg_red']
        })

    def write_PandL(ws, fmt, cell_language,cell_exchange_rate,start_row):
        """
        Writes a P&L table under the graphs in the Site Analysis worksheet.
        """

        # Add the new header row with formatting for each element
        headers = [
            ("ប្រភេទ|Category", fmt['PandL_header']),
            ("P&L|P&L", fmt['PandL_header']),
            ("ខែ|Month", fmt['Green_header']),
            ("ខែមុន|M-1", fmt['Green_header']),
            ("YTD|YTD", fmt['PandL_header']),
            ("Y-1|Y-1", fmt['PandL_header'])
        ]

        for col_index, (header, format_type) in enumerate(headers):
            khmer, english = header.split('|')
            ws.write_formula(
                start_row, col_index,
                f'=IF({cell_language}="Khmer","{khmer}","{english}")',
                format_type
            )

        # Define headers for the table with their respective row spans for merging
        PandL_headers = [
                    ["Revenue", ["Sales", "WinS", "Total"] , [["Income Sales"],["Income WinS"]]],
                    ["Expenses", [ "Salary","Production", "Delivery", "Contribution", "Other", "Total"], 
                        [["Salary Ent","Salary Op"],["Production"],["Delivery"],["Contribution"],["Investment","Technical"]]],
                    ["Result", ["Result"]],
                    ["Inc Ent (sal + profit)", ["Sal+Profit"]]
                ]

        PandL_headers_Khmer = [
            ["ចំណូល", ["ការលក់", "ទឹកសាលា", "សរុប"]],
            ["ចំណាយ", ["ប្រាក់ខែ", "ផលិតកម្ម", "ដឹកជញ្ជូន", "វិភាគទាន", "ផ្សេងៗ", "សរុប"]],
            ["លទ្ធផល", ["លទ្ធផល"]],
            ["ប្ប្រាក់ខែ+ប្រាក់ចំណេញ", ["ប្រាក់ខែ+ប្រាក់ចំណេញ"]]
        ]

        # Write headers
        current_row = start_row + 1
        for header_group, header_group_khmer in zip(PandL_headers, PandL_headers_Khmer):
            main_header = header_group[0]
            main_header_khmer = header_group_khmer[0]
            sub_headers = header_group[1]
            sub_headers_khmer = header_group_khmer[1]
            # Merge cells for the main header if there are multiple sub-headers
            if len(sub_headers) > 1:
                ws.merge_range(
                    current_row, 0, current_row + len(sub_headers) - 1, 0,
                    f'=IF({cell_language}="Khmer","{main_header_khmer}","{main_header}")',
                    fmt['PandL_header']
                )
            elif header_group == PandL_headers[-1]:
                ws.merge_range(
                        current_row, 0, current_row, 1,
                        f'=IF({cell_language}="Khmer","{main_header_khmer}","{main_header}")',
                        fmt['PandL_header']
                    )
            else:
                ws.write_formula(
                    current_row, 0,
                    f'=IF({cell_language}="Khmer","{main_header_khmer}","{main_header}")',
                    fmt['PandL_header']
                )
            # Write sub-headers
            for sub_header, sub_header_khmer in zip(sub_headers, sub_headers_khmer):
                if header_group == PandL_headers[-1]:  # For the last element, merge two columns
                    pass
                else:
                    if sub_header in ["Total", "Result", "Sal+Profit"]:
                        ws.write_formula(
                            current_row, 1,
                            f'=IF({cell_language}="Khmer","{sub_header_khmer}","{sub_header}")',
                            fmt['PandL_subheader_bold']
                        )
                    else:
                        ws.write_formula(
                            current_row, 1,
                            f'=IF({cell_language}="Khmer","{sub_header_khmer}","{sub_header}")',
                            fmt['PandL_subheader']
                        )
                current_row += 1

        # Define formulas for the data column
        # Define formulas for the data column
        period_header = [""," M_1"," YTD"," N_1"]
        for i, period in enumerate(period_header):
            globals()[f"Column_Month_{period.strip()}"] = [
            [col_letter_from_header(header + period) for header in PandL_headers[0][2][0]],  # Sales
            [col_letter_from_header(header + period) for header in PandL_headers[0][2][1]],  # WinS
            ["total"],  # Total Revenue
            [col_letter_from_header(header + period) for header in PandL_headers[1][2][0]],  # Production
            [col_letter_from_header(header + period) for header in PandL_headers[1][2][1]],  # Salary
            [col_letter_from_header(header + period) for header in PandL_headers[1][2][2]],  # Delivery
            [col_letter_from_header(header + period) for header in PandL_headers[1][2][3]],  # Contribution
            [col_letter_from_header(header + period) for header in PandL_headers[1][2][4]],  # Other
            ]

        # Define formulas for the data column
        column_groups = [
            globals().get(f"Column_Month_{period.strip()}")
            for period in period_header
        ]
        base_formulas = [
            "INDEX('Data Month Site Analysis'!{col}2:{col}{row_count},"
            "MATCH('Site Analysis'!O2,'Data Month Site Analysis'!A2:A{row_count},0))/{cell_exchange_rate}",  # Base formula for INDEX
        ]
        
        # Write formulas for each column group
        for group_index, column_group in enumerate(column_groups):
            for col_index, col_letter in enumerate(column_group):
                row_count = len(ListSiteActive) + 2
                if isinstance(col_letter, list):
                    formula = " + ".join(base_formulas[0].format(col=col, row_count=row_count,cell_exchange_rate=cell_exchange_rate) for col in col_letter)
                else:
                    formula = base_formulas[0].format(col=col_letter, row_count=row_count,cell_exchange_rate=cell_exchange_rate)
                # Add the other 4 formulas after element number 2
                if col_index == 2:
                    ws.write_formula(start_row + col_index + 1, group_index + 2, f"={xl_rowcol_to_cell(start_row + 1, group_index + 2)} + {xl_rowcol_to_cell(start_row + 2, group_index + 2)}", fmt['PandL_subheader_bold'])
                    col_index+=1
                # Write the formula
                ws.write_formula(start_row + col_index + 1, group_index + 2, formula, fmt['PandL_number'])
                ws.write_formula(start_row + col_index + 2, group_index + 2, f"=SUM({xl_rowcol_to_cell(start_row + 4, group_index + 2)}:{xl_rowcol_to_cell(start_row + 8, group_index + 2)})", fmt['PandL_subheader_bold'])
                ws.write_formula(start_row + col_index + 3, group_index + 2, f"={xl_rowcol_to_cell(start_row + 3, group_index + 2)} - {xl_rowcol_to_cell(start_row + 9, group_index + 2)}", fmt['PandL_subheader_bold'])
                col_letter_salary_ent = col_letter_from_header("Salary Ent" + period_header[group_index])
                formula_salary_ent = f"=INDEX('Data Month Site Analysis'!{col_letter_salary_ent}2:{col_letter_salary_ent}{len(ListSiteActive) + 2}, MATCH('Site Analysis'!O2, 'Data Month Site Analysis'!A2:A{len(ListSiteActive) + 2}, 0))/{cell_exchange_rate}"
                ws.write_formula(start_row + col_index + 4, group_index + 2, formula_salary_ent + " + " + xl_rowcol_to_cell(start_row + 10, group_index + 2), fmt['PandL_subheader_bold'])

    def write_price_and_debt_table(ws, fmt, start_row, start_col, cell_exchange_rate):
        """
        Writes a table next to the P&L table with information about HOD Price, Shopkeeper Price, Onsite Price, and Debt.
        Adds conditional formatting for specific cells.
        """
        
        # Define headers for the table with a separator "|"
        headers = [["ប្រភេទ|Category", fmt['Green_header_line']], 
                   ["តម្លៃ|Value", fmt['Green_header']]]

        # Write headers dynamically based on the list
        for col_offset, header in enumerate(headers):
            khmer, english = header[0].split('|')
            ws.write(start_row, start_col + col_offset, f'=IF({cell_language}="Khmer","{khmer}","{english}")', header[1])
        
        # Define the categories and their corresponding data columns with Khmer translations
        categories = [
                    ("តម្លៃតាមផ្ទះ (៛)|HOD Price (៛)", "Hod Price"),
                    ("តម្លៃតាមស្តង់ (៛)|Shopkeeper Price (៛)", "Shopkeeper Price"),
                    ("តម្លៃនៅស្ថានីយ (៛)|Onsite Price (៛)", "Onsite Price"),
                    ("តម្លៃទឹកសាលា (៛)|WinS Price (៛)", "WiS Price"),
                    ("", ""),
                    ("ចំនួនប៊ីដុង YTD|Nb Bot YTD", "Nb Bot bought YTD"),
                    ("ចំនួនប៊ីដុង Y-1|Nb Bot Y-1", "Nb Bot bought Y-1"),
                    ("", ""),
                    ("បំណុល (-)/ សន្សំ (+)|Debt (-)/ Sav. (+)", "Debt")
                ]

        # Write the categories and formulas for their values
        for row_offset, (category, data_column) in enumerate(categories, start=1):
            if category == "":
                ws.write(start_row + row_offset, start_col, "", fmt['empty_with_line'])
                ws.write(start_row + row_offset, start_col + 1, "", fmt['empty'])
            else:
                print(category)
                khmer, english = category.split('|')
                col_letter = col_letter_from_header(data_column)
                formula = f"=INDEX('Data Month Site Analysis'!{col_letter}2:{col_letter}{len(ListSiteActive) + 2}, MATCH('Site Analysis'!O2, 'Data Month Site Analysis'!A2:A{len(ListSiteActive) + 2}, 0))"
                if data_column == "Debt":
                    formula += f" / {cell_exchange_rate}"
                ws.write_formula(start_row + row_offset, start_col, f'=IF({cell_language}="Khmer","{khmer}","{english}")', fmt['Green_subheader_line'])
                ws.write_formula(start_row + row_offset, start_col + 1, formula, fmt['PandL_number'])

        # Add conditional formatting
        # Debt > 0 => Red
        ws.conditional_format(start_row + 5, start_col + 1, start_row + 5, start_col + 1, {
            'type': 'cell',
            'criteria': '<',
            'value': 0,
            'format': fmt['bg_red']
        })

        # HOD Price < 2000 => Red
        ws.conditional_format(start_row + 1, start_col + 1, start_row + 1, start_col + 1, {
            'type': 'cell',
            'criteria': '<',
            'value': 2000,
            'format': fmt['bg_red']
        })

        # Shopkeeper Price < 1500 => Red
        ws.conditional_format(start_row + 2, start_col + 1, start_row + 2, start_col + 1, {
            'type': 'cell',
            'criteria': '<',
            'value': 1500,
            'format': fmt['bg_red']
        })

    def create_graph_bot_day(workbook, sheet_name, start_year, end_year):
        chart = workbook.add_chart({'type': 'line'})
        Color = ["#D0E4F7", "#91C3EB", "#519FD9", "#1F78B4", "#0A4C8A"]
        for year in range(start_year, end_year + 1):
            col_start = (year - start_year) * 12 + 1
            col_end = col_start + 11
            col_range = (xl_col_to_name(col_start), xl_col_to_name(col_end))
            chart.add_series({
                'name': str(year),
                'categories': f"='{sheet_name}'!{col_range[0]}1:{col_range[1]}1",
                'values': f"='{sheet_name}'!{col_range[0]}2:{col_range[1]}2",
                'line': {
                    'width': 4.5 if year == Current_date.year else 2.0,
                    'color': Color[year - start_year]
                }
            })
        chart.set_y_axis({'name': 'Bot/day exc. WinS'})
        chart.set_x_axis({'name': 'Months'})
        chart.set_size({'width': 713, 'height': 278})
        return chart

    def create_chart_mix(workbook):
        chart = workbook.add_chart({'type': 'pie'})
        Color = ["#D0E4F7", "#91C3EB", "#519FD9", "#1F78B4", "#0A4C8A"]
        chart.add_series({
            'name': 'Mix/ការលក់',
            'categories': "='Mix'!$A$1:$A$5",
            'values': "='Mix'!$B$1:$B$5",
            'data_labels': {'percentage': True},  # Show values as a percentage of the total
            'points': [{'fill': {'color': Color[i]}} for i in range(5)]  # Set colors for each slice
        })
        chart.set_title({
            'name': 'Mix/ការទាំងអស់ ',
            'name_font': {'name': 'Calibri', 'size': 12, 'color': 'black'}
        })
        chart.set_legend({'font': {'size': 8}})
        chart.set_size({'width': 320, 'height': 200})
        return chart

    def create_chart_expenses(workbook):
        Color = ["#0A4C8A","#D0E4F7"]  # Updated color list
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
                    'name': 'Average',
                    'categories': "='Expenses'!$A$1:$A$4",
                    'values': "='Expenses'!$C$1:$C$4",
                    'fill': {'color': Color[0]}
                })
        chart.add_series({
                    'name': 'Kiosk',
                    'categories': "='Expenses'!$A$1:$A$4",
                    'values': "='Expenses'!$B$1:$B$4",
                    'fill': {'color': Color[1]}
                })
        chart.set_title({
            'name': 'Expenses($)/ការចំណាយ(៛)',
            'name_font': {'name': 'Calibri', 'size': 12, 'color': 'black'}
        })
        chart.set_x_axis({'num_font': {'size': 8, 'bold': False}})
        chart.set_legend({'font': {'size': 8}})
        chart.set_size({'width': 397, 'height': 200})
        return chart

    date_start_historic = date(max(Current_date.year - 3, 2020), 1, 1)
    Category_expenses = CategoryExpenses()

    fetched,query_map = query()
    
    worksheet_site_analysis, worksheet_data_months, worksheet_data_historic, worksheet_expenses, worksheet_mix = add_worksheet()
    fmt = format_factory(workbook)
    cell_language = "D2"
    cell_exchange_rate = "O1"

    #Monthly Data tab
    headers = data_monthly_header()
    worksheet_data_months.write_row(1, 0, headers)
    for i, site_row in enumerate(ListSiteActive):
        site_id = site_row[0]
        write_data_monthly_data(worksheet_data_months, i + 1, site_id)
    
    #Lday Data tab
    write_data_botday(worksheet_data_historic)

    #Expenses
    write_expenses(worksheet_expenses,cell_exchange_rate,cell_language)

    #Miw
    write_mix(worksheet_mix)

    #Site Analysis tab
    add_vba(worksheet_site_analysis)
    title_language(worksheet_site_analysis,"A2",cell_language,"O2","G2","H2","E2","F2","L1",cell_exchange_rate,fmt)
    write_site_analysis_header(worksheet_site_analysis, fmt)
    write_site_summary(worksheet_site_analysis,ListSiteActive, fmt, start_row=4)
    # Insert charts
    chart_lday = create_graph_bot_day(workbook, 'Data Lday Site Analysis', date_start_historic.year, Current_date.year)
    worksheet_site_analysis.insert_chart('A8', chart_lday)

    chart_mixsales = create_chart_mix(workbook)
    worksheet_site_analysis.insert_chart('A23', chart_mixsales, {'x_offset': 1})

    chart_expenses = create_chart_expenses(workbook)
    worksheet_site_analysis.insert_chart('D23', chart_expenses, {'x_offset': 1})
    # Add the P&L table under the graphs
    write_PandL(worksheet_site_analysis, fmt, cell_language,cell_exchange_rate,start_row=33)

    # Add the Price and Debt table next to the P&L table
    write_price_and_debt_table(worksheet_site_analysis, fmt, start_row=34, start_col=6, cell_exchange_rate=cell_exchange_rate)
    
    
    if not F2F:
        workbook.close()

def LaunchExcelCreationSiteAnalysis(Date,ListSiteActive,ListTier,exchange_rate):
    global Current_date
    Current_date = Date
    workbook = CreateworkbookSiteAnalysis()
    SiteAnalysis(ListTier,ListSiteActive,workbook,Current_date,False)

