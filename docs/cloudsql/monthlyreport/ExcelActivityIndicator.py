import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta, datetime
from calendar import monthrange
import db
import tempfile
from dateutil.relativedelta import *
from monthlyreport.Functionutils import NewCalculTier
import monthlyreport.ExcelKPI as ExcelKPI

con = db.pool.connect()
def RawData(workbook,Current_date,ListTier,exchange_rate):

    worksheet_data = workbook.add_worksheet("Data")
    ListTier = NewCalculTier(Current_date)[0]
    start_date = date(2017,1,1)
    ListDate = []
    Year_to_hide = (Current_date.year-3 - start_date.year)*12 -1
    Date_format = workbook.add_format({'num_format' : 'yyyy-mm'})
    Number_format = workbook.add_format({'num_format':'# ### ##0'})
    Number_bold_format = workbook.add_format({'num_format':'# ### ##0', 'bold' : True})
    grey_format = workbook.add_format({'bg_color':"#C0C0C0"})
    Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
    Subtotal_format = workbook.add_format({'bold':True,'font_size':15})

    while start_date <= Current_date:
        ListDate.append(start_date)
        start_date += relativedelta(months=+1)



    allSales = con.execute("""SELECT SUM(Total_Income)/%s,SUM(Total_Income - WiS_Income)/%s, SUM(Total_Sales-Bottle_Sales),
                                SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days),
                                SUM(Total_Sales-Bottle_Sales-WiS_Sales)/SUM(Number_Open_Days),
                                SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days)*20,SUM(Number_Open_Days), SUM(WiS_Sales),
                                Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales WHERE Month <=%s 
                                GROUP BY Id_Site,Month""",(exchange_rate,exchange_rate,Current_date)).fetchall()
    allOperator = con.execute("""SELECT Number_of_Operator,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Indicators 
                              WHERE Month <=%s
                        """,Current_date).fetchall()
    allBeneficiaries = con.execute("SELECT Beneficiaries,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Beneficiaries WHERE Month <=%s",Current_date).fetchall()
    allSchool_Beneficiaries = con.execute("SELECT SUM(number_of_children),Id_Site,academy_year FROM school_programs " \
                                            "GROUP BY Id_Site,academy_year").fetchall()
    Academy_month = [1,2,3,4,5,6,7,8,9,10] #IN those month in 2025 the school year in Commcare is "2024" (same every year)
    SitesInfo = con.execute("SELECT DISTINCT Sales.Id_Site,Platform,Province,Advisor FROM Sales " \
    "INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site" \
    " ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site").fetchall()
    LineData = 4
    worksheet_data.set_zoom(70)
    worksheet_data.write(0,4,"Average",Subtotal_format)
    worksheet_data.write(1,4,"Sum",Subtotal_format)
    worksheet_data.write(2,4,"Nb Active Sites",Subtotal_format)
    worksheet_data.set_column('A:A', 25)
    worksheet_data.set_column('B:B', 10)
    worksheet_data.set_column('C:C', len('Banteay Meanchey'))
    worksheet_data.set_column('D:D', 15)
    worksheet_data.set_column('E:%s'%xl_col_to_name(len(ListDate)+4),13)

    columns_settings = [{'header' : 'Site'},
                        {'header' : 'Platform'},
                        {'header' : 'Province'},
                        {'header' : 'Advisor'},
                        {'header' : 'Tier'}] + [{'header' : str(s.year) + '-' + str(s.month), 'header_format' : Date_format} for s in ListDate]
    worksheet_data.add_table(LineData-1,0,len(SitesInfo)+LineData-1,len(ListDate)+4, {'autofilter': True,'columns' : columns_settings})

    worksheet_data.freeze_panes(LineData,5)

    worksheet_data.data_validation('A1',{'validate' : 'list',
                                    'source' : ['L/day inc. WinS', 'Bot/day inc. WinS',
                                                'Bot/day exc. WinS','Sales (Bot) inc. WinS','Sales (Bot) exc. WinS',
                                                'Sales (Bot) WinS','Sales ($) exc. WinS','Sales ($) inc. WinS',
                                                'Number Open Days','Beneficiaries','Beneficiaries School','Operators']})
    worksheet_data.write('A1', 'L/day inc. WinS',Select_format)

    for i in range(len(SitesInfo)):
        Tier = list(filter(lambda row: row[0] == SitesInfo[i][0], ListTier)) or [(0,"\"\"")]
        Sales_Month = list(filter(lambda row: row[9] == SitesInfo[i][0], allSales))
        Operator_Month = list(filter(lambda row: row[1] == SitesInfo[i][0], allOperator)) or [("\"\"","\"\"","\"\"")]
        Beneficiaries_Month = list(filter(lambda row: row[1] == SitesInfo[i][0], allBeneficiaries))
        Beneficiaries_School_Month = list(filter(lambda row: row[1] == SitesInfo[i][0], allSchool_Beneficiaries)) or [("\"\"","\"\"","\"\"")]
        worksheet_data.write(LineData+i,0,SitesInfo[i][0])
        if SitesInfo[i][1] == 'Dead':
            worksheet_data.set_row(LineData+i,options={'hidden': True})
        worksheet_data.write(LineData+i,1,SitesInfo[i][1])
        worksheet_data.write(LineData+i,2,SitesInfo[i][2])
        worksheet_data.write(LineData+i,3,SitesInfo[i][3])
        worksheet_data.write(LineData+i,4,Tier[0][1])

        for k in range(len(ListDate)):
            Sales = list(filter(lambda row: row[10] == str(ListDate[k]), Sales_Month)) or [("\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"")]
            Operators = list(filter(lambda row: row[2] == str(ListDate[k]), Operator_Month)) or [("\"\"", "\"\"", "\"\"")]
            Beneficiaries = list(filter(lambda row: row[2] == str(ListDate[k]), Beneficiaries_Month)) or [("\"\"","\"\"","\"\"")]
            if ListDate[k].month in Academy_month:
                Beneficiaries_School = list(filter(lambda row: row[2] == ListDate[k].year -1, Beneficiaries_School_Month)) or [("\"\"","\"\"","\"\"")]
            else:
                Beneficiaries_School = list(filter(lambda row: row[2] == ListDate[k].year, Beneficiaries_School_Month)) or [("\"\"", "\"\"", "\"\"")]
            # Optimized formula: use MATCH + CHOOSE instead of deep nested IFs for better performance & readability
            # $A$1 is data-validated to allowed metric labels, so MATCH will return a position 1..10 or #N/A; IFERROR => blank
            # Order of metrics must align with the sequence of values provided to CHOOSE.
            optimized_formula = (
                '=IFERROR(CHOOSE(MATCH($A$1,'
                '{"Sales ($) inc. WinS","Sales ($) exc. WinS","Sales (Bot) inc. WinS","Sales (Bot) exc. WinS","Sales (Bot) WinS","Bot/day inc. WinS","Bot/day exc. WinS","L/day inc. WinS","Number Open Days","Beneficiaries","Beneficiaries School","Operators"},0)'
                ',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s),"")'
                % (Sales[0][0],  # Sales ($) inc. WinS
                   Sales[0][1],  # Sales ($) exc. WinS
                   Sales[0][2],  # Sales (Bot) inc. WinS
                   Sales[0][3],  # Sales (Bot) exc. WinS
                   Sales[0][8],  # Sales (Bot) WinS
                   Sales[0][4],  # Bot/day inc. WinS
                   Sales[0][5],  # Bot/day exc. WinS
                   Sales[0][6],  # L/day inc. WinS
                   Sales[0][7],  # Number Open Days
                   Beneficiaries[0][0],# Beneficiaries
                   Beneficiaries_School[0][0],
                   Operators[0][0])  # Operators
            )
            worksheet_data.write_formula(LineData+i,5+k, optimized_formula, Number_format)

            worksheet_data.write(0,k+5,"=IFERROR(SUBTOTAL(1,%s%s:%s%s),0)"%(xl_col_to_name(k+5),LineData,xl_col_to_name(k+5),len(SitesInfo)+LineData),Number_bold_format)
            worksheet_data.write(1,k+5,"=IFERROR(SUBTOTAL(9,%s%s:%s%s),0)"%(xl_col_to_name(k+5),LineData,xl_col_to_name(k+5),len(SitesInfo)+LineData),Number_bold_format)
            worksheet_data.write(2,k+5,"=IFERROR(SUBTOTAL(2,%s%s:%s%s),0)"%(xl_col_to_name(k+5),LineData,xl_col_to_name(k+5),len(SitesInfo)+LineData),Number_bold_format)
            
    worksheet_data.conditional_format('F%s:%s'%(LineData,xl_rowcol_to_cell(len(SitesInfo)+2,len(ListDate)+LineData)),{"type" : "formula", "criteria" : "=F%s=\"\""%(LineData), "format" : grey_format})
    worksheet_data.set_column("F:%s"%(xl_col_to_name(Year_to_hide+5)),None,None,{'level':1,'hidden':True})
    worksheet_data.filter_column('B', 'Platform <> Dead')

def Summary(workbook,Current_date,ListTier,exchange_rate):
    Date_janv = date(Current_date.year-1,12,1)
    Date_N_1 = date(Current_date.year-1,Current_date.month,1)

    worksheet_summary = workbook.add_worksheet("Summary")


    Date_format = workbook.add_format({'num_format' : 'yyyy-mm'})
    Number_format = workbook.add_format({'num_format':'# ### ##0'})
    Number_format_rightborder = workbook.add_format({'num_format':'# ### ##0','right':2})
    Number_bold_format = workbook.add_format({'num_format':'# ### ##0', 'bold' : True})
    grey_format = workbook.add_format({'bg_color':"#C0C0C0"})
    Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})

    Site_format = workbook.add_format({'bg_color' : '#F2F2F2'})

    Title_format_year_1 = workbook.add_format({'bold': True,'bg_color':'#F2DCDB','text_wrap':True})
    Title_format_year_2 = workbook.add_format({'bold': True,'bg_color':'#EBF1DE','text_wrap':True})
    Title_format_year_3 = workbook.add_format({'bold': True,'bg_color':'#C5D9F1','text_wrap':True})
    Title_format_year_4 = workbook.add_format({'bold': True,'bg_color':'#DAEEF3','text_wrap':True})

    worksheet_summary.set_column('A:A', 15)
    worksheet_summary.set_column('B:B', 10)
    worksheet_summary.set_column('C:C', 25)
    worksheet_summary.set_column('D:D', 15)
    worksheet_summary.set_column('E:Q',20)
    worksheet_summary.set_row(2,45)
    worksheet_summary.set_zoom(70)

    worksheet_summary.freeze_panes(3,5)

    SitesInfo = con.execute("SELECT DISTINCT Sales.Id_Site,Platform,Province,Advisor FROM Sales " \
    "INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site" \
    " ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site").fetchall()
    worksheet_summary.data_validation('A1',{'validate' : 'list',
                                    'source' : ['Month','YTD','Last 12 Months']})
    worksheet_summary.write('A1', 'YTD',Select_format)

    worksheet_summary.data_validation('C1',{'validate' : 'list',
                                    'source' : ['Bot/day','Sales (Bot)','Sales ($)','Beneficiaries','Open Days']})
    worksheet_summary.write('C1', 'Bot/day',Select_format)

    worksheet_summary.write(2,0,"Site",Site_format)
    worksheet_summary.write(2,1,"Platform",Site_format)
    worksheet_summary.write(2,2,"Province",Site_format)
    worksheet_summary.write(2,3,"Advisor",Site_format)
    worksheet_summary.write(2,4,"Tier",Site_format)
    worksheet_summary.write(0,4,"Total",Number_bold_format)
    worksheet_summary.write(1,4,"Average",Number_bold_format)

    worksheet_summary.autofilter(2,0,len(SitesInfo) +2,16)
    worksheet_summary.filter_column('B', 'Platform <> Dead')

    for i in range(4): #We only show the last 4 years
        if i ==0:
            format = Title_format_year_1
        elif i ==1:
            format = Title_format_year_2
        elif i ==2:
            format = Title_format_year_3
        elif i ==3:
            format = Title_format_year_4

        worksheet_summary.write_formula(2,5+3*i,'=IF($A$1="Month",CONCATENATE($C$1," \n inc. WinS %s-%s"),IF($A$1="YTD",CONCATENATE($C$1," \n inc. WinS %s-%s %s-%s"),IF($A$1="Last 12 Months",CONCATENATE($C$1," \n inc. WinS %s-%s %s-%s"))))'%(str(Current_date.month).zfill(2),Current_date.year - i,str((Date_janv + relativedelta(months=+1)).month).zfill(2),Current_date.year-i,str(Current_date.month).zfill(2),Current_date.year -i,str((Date_N_1+ relativedelta(months=+1)).month).zfill(2),(Date_N_1+ relativedelta(months=+1)).year-i,str(Current_date.month).zfill(2),Current_date.year-i),format)
        worksheet_summary.write_formula(2,6+3*i,'=IF($A$1="Month",CONCATENATE($C$1," \n exc. WinS %s-%s"),IF($A$1="YTD",CONCATENATE($C$1," \n exc. WinS %s-%s %s-%s"),IF($A$1="Last 12 Months",CONCATENATE($C$1," \n exc. WinS %s-%s %s-%s"))))'%(str(Current_date.month).zfill(2),Current_date.year - i,str((Date_janv + relativedelta(months=+1)).month).zfill(2),Current_date.year-i,str(Current_date.month).zfill(2),Current_date.year -i,str((Date_N_1+ relativedelta(months=+1)).month).zfill(2),(Date_N_1+ relativedelta(months=+1)).year-i,str(Current_date.month).zfill(2),Current_date.year-i),format)
        worksheet_summary.write_formula(2,7+3*i,'=IF($A$1="Month",CONCATENATE($C$1," \n WinS %s-%s"),IF($A$1="YTD",CONCATENATE($C$1," \n WinS %s-%s %s-%s"),IF($A$1="Last 12 Months",CONCATENATE($C$1," \n WinS %s-%s %s-%s"))))'%(str(Current_date.month).zfill(2),Current_date.year - i,str((Date_janv + relativedelta(months=+1)).month).zfill(2),Current_date.year-i,str(Current_date.month).zfill(2),Current_date.year -i,str((Date_N_1+ relativedelta(months=+1)).month).zfill(2),(Date_N_1+ relativedelta(months=+1)).year-i,str(Current_date.month).zfill(2),Current_date.year-i),format)

        allSales_month = con.execute("SELECT SUM(Total_Income)/%s,SUM(Total_Income - WiS_Income)/%s, SUM(WiS_Income)/%s, SUM(Total_Sales-Bottle_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(WiS_Sales),SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days),SUM(Total_Sales-Bottle_Sales-WiS_Sales)/SUM(Number_Open_Days),SUM(WiS_Sales)/SUM(Number_Open_Days),SUM(Number_Open_Days),Id_Site FROM Sales WHERE Month = %s GROUP BY Id_Site",(exchange_rate,exchange_rate,exchange_rate,Current_date-relativedelta(months =+ 12*i))).fetchall()
        allSales_YTD = con.execute("SELECT SUM(Total_Income)/%s,SUM(Total_Income - WiS_Income)/%s, SUM(WiS_Income)/%s, SUM(Total_Sales-Bottle_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(WiS_Sales),SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days),SUM(Total_Sales-Bottle_Sales-WiS_Sales)/SUM(Number_Open_Days),SUM(WiS_Sales)/SUM(Number_Open_Days),SUM(Number_Open_Days),Id_Site FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(exchange_rate,exchange_rate,exchange_rate,Current_date-relativedelta(months =+ 12*i),Date_janv-relativedelta(months =+ 12*i))).fetchall()
        allSales_12months = con.execute("SELECT SUM(Total_Income)/%s,SUM(Total_Income - WiS_Income)/%s, SUM(WiS_Income)/%s, SUM(Total_Sales-Bottle_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(WiS_Sales),SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days),SUM(Total_Sales-Bottle_Sales-WiS_Sales)/SUM(Number_Open_Days),SUM(WiS_Sales)/SUM(Number_Open_Days),SUM(Number_Open_Days),Id_Site FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(exchange_rate,exchange_rate,exchange_rate,Current_date-relativedelta(months =+ 12*i),Date_N_1-relativedelta(months =+ 12*i))).fetchall()
        allBeneficiaries_month = con.execute("SELECT IFNULL(Beneficiaries,0),Id_Site FROM Beneficiaries WHERE Month = %s GROUP BY Id_Site",Current_date-relativedelta(months =+ 12*i)).fetchall()
        for j in range(len(SitesInfo)):

            Tier = list(filter(lambda row: row[0] == SitesInfo[j][0], ListTier)) or [(0,"\"\"")]
            Sales_Month = list(filter(lambda row: row[10] == SitesInfo[j][0], allSales_month)) or [("\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"")]

            Beneficiaries_Month = list(filter(lambda row: row[1] == SitesInfo[j][0], allBeneficiaries_month)) or [("\"\"","\"\"","\"\"")]
            Sales_YTD = list(filter(lambda row: row[10] == SitesInfo[j][0], allSales_YTD)) or [("\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"")]
            Sales_12Month = list(filter(lambda row: row[10] == SitesInfo[j][0], allSales_12months)) or [("\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"","\"\"")]
            worksheet_summary.write(3+j,0,SitesInfo[j][0],Site_format)
            worksheet_summary.write(3+j,1,SitesInfo[j][1],Site_format)
            if SitesInfo[j][1] == 'Dead':
                worksheet_summary.set_row(3+j,options={'hidden': True})
            worksheet_summary.write(3+j,2,SitesInfo[j][2],Site_format)
            worksheet_summary.write(3+j,3,SitesInfo[j][3],Site_format)
            worksheet_summary.write(3+j,4,Tier[0][1],Site_format)

            worksheet_summary.write_formula(3+j,3*i+5,'=IF($A$1="Month",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),IF($A$1="YTD",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),IF($A$1="Last 12 Months",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),"")))'%(Sales_Month[0][6],Sales_Month[0][3],Sales_Month[0][0],Beneficiaries_Month[0][0],Sales_Month[0][9],Sales_YTD[0][6],Sales_YTD[0][3],Sales_YTD[0][0],Beneficiaries_Month[0][0],Sales_YTD[0][9],Sales_12Month[0][6],Sales_12Month[0][3],Sales_12Month[0][0],Beneficiaries_Month[0][0],Sales_12Month[0][9]),Number_format)
            worksheet_summary.write_formula(3+j,3*i+6,'=IF($A$1="Month",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),IF($A$1="YTD",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),IF($A$1="Last 12 Months",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),"")))'%(Sales_Month[0][7],Sales_Month[0][4],Sales_Month[0][1],"\"\"","\"\"",Sales_YTD[0][7],Sales_YTD[0][4],Sales_YTD[0][1],"\"\"","\"\"",Sales_12Month[0][7],Sales_12Month[0][4],Sales_12Month[0][1],"\"\"","\"\""),Number_format)
            worksheet_summary.write_formula(3+j,3*i+7,'=IF($A$1="Month",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),IF($A$1="YTD",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),IF($A$1="Last 12 Months",IF($C$1="Bot/day",%s,IF($C$1="Sales (Bot)",%s,IF($C$1="Sales ($)",%s,IF($C$1="Beneficiaries",%s,IF($C$1="Open Days",%s,""))))),"")))'%(Sales_Month[0][8],Sales_Month[0][5],Sales_Month[0][2],"\"\"","\"\"",Sales_YTD[0][8],Sales_YTD[0][5],Sales_YTD[0][2],"\"\"","\"\"",Sales_12Month[0][8],Sales_12Month[0][5],Sales_12Month[0][2],"\"\"","\"\""),Number_format_rightborder)

        worksheet_summary.write_formula(0,5+i*3,"=IFERROR(SUBTOTAL(9,%s:%s),0)"%(xl_rowcol_to_cell(3,5+i*3),xl_rowcol_to_cell(len(SitesInfo)+3,5+i*3)),Number_bold_format)
        worksheet_summary.write_formula(0,6+i*3,"=IFERROR(SUBTOTAL(9,%s:%s),0)"%(xl_rowcol_to_cell(3,6+i*3),xl_rowcol_to_cell(len(SitesInfo)+3,6+i*3)),Number_bold_format)
        worksheet_summary.write_formula(0,7+i*3,"=IFERROR(SUBTOTAL(9,%s:%s),0)"%(xl_rowcol_to_cell(3,7+i*3),xl_rowcol_to_cell(len(SitesInfo)+3,7+i*3)),Number_bold_format)
        worksheet_summary.write_formula(1,5+i*3,"=IFERROR(SUBTOTAL(1,%s:%s),0)"%(xl_rowcol_to_cell(3,5+i*3),xl_rowcol_to_cell(len(SitesInfo)+3,5+i*3)),Number_bold_format)
        worksheet_summary.write_formula(1,6+i*3,"=IFERROR(SUBTOTAL(1,%s:%s),0)"%(xl_rowcol_to_cell(3,6+i*3),xl_rowcol_to_cell(len(SitesInfo)+3,6+i*3)),Number_bold_format)
        worksheet_summary.write_formula(1,7+i*3,"=IFERROR(SUBTOTAL(1,%s:%s),0)"%(xl_rowcol_to_cell(3,7+i*3),xl_rowcol_to_cell(len(SitesInfo)+3,7+i*3)),Number_bold_format)
    worksheet_summary.conditional_format('F4:Q%s'%(len(SitesInfo)+3),{"type" : "formula", "criteria" : "=F4=\"\"", "format" : grey_format})

def ActivityKPI(workbook,Current_date,Date_1,Platform_List,exchange_rate):
    if Current_date.month - Date_1.month == 1:
        worksheet = workbook.add_worksheet("KPI %s'%s%s"%(Current_date.strftime("%b"),str(Current_date.year)[2],str(Current_date.year)[3]))
    else:
        worksheet = workbook.add_worksheet("KPI %s'%s%s %s'%s%s"%((Date_1+relativedelta(months=+1)).strftime("%b"),str((Date_1+relativedelta(months=+1)).year)[2],str((Date_1+relativedelta(months=+1)).year)[3],Current_date.strftime("%b"),str(Current_date.year)[2],str(Current_date.year)[3]))

    Tier = ExcelKPI.KPIFormat(workbook,worksheet,Current_date,Date_1,2018,Platform_List)
    ExcelKPI.KPINbSite(workbook,worksheet,2,Current_date,Date_1,Tier,Platform_List)
    ExcelKPI.KPINbSitePercentage(workbook,worksheet,12,Current_date,Date_1,Tier,Platform_List)
    ExcelKPI.KPIBeneficiaries(workbook,worksheet,21,Current_date,Date_1,Tier,Platform_List)
    ExcelKPI.KPIBotDay(workbook,worksheet,30,Current_date,Date_1,Tier,Platform_List,False)
    ExcelKPI.KPIBotDay(workbook,worksheet,40,Current_date,Date_1,Tier,Platform_List,True)
    ExcelKPI.KPITotBot(workbook,worksheet,50,Current_date,Date_1,Tier,Platform_List,True,True)
    ExcelKPI.KPITotBot(workbook,worksheet,59,Current_date,Date_1,Tier,Platform_List,False,True)
    ExcelKPI.KPITotLit(workbook,worksheet,68,Current_date,Date_1,Tier,Platform_List,True,False)
    ExcelKPI.KPITotLit(workbook,worksheet,77,Current_date,Date_1,Tier,Platform_List,False,False)
    ExcelKPI.KPITotInc(workbook,worksheet,86,Current_date,Date_1,Tier,Platform_List,exchange_rate,False,True)
    ExcelKPI.KPITotInc(workbook,worksheet,95,Current_date,Date_1,Tier,Platform_List,exchange_rate,True)
    ExcelKPI.KPIPrice(workbook,worksheet,104,Current_date,Date_1,Tier,Platform_List,exchange_rate,False)
    ExcelKPI.KPISalaryEnt(workbook,worksheet,114,Current_date,Date_1,Tier,Platform_List,exchange_rate,True)
    ExcelKPI.KPIIncomeEnt(workbook,worksheet,123,Current_date,Date_1,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPIPL(workbook,worksheet,132,Current_date,Date_1,Tier,Platform_List,exchange_rate)
    if Current_date.month == (Date_1 +relativedelta(months=+1)).month:
        ExcelKPI.KPINumberOperator(workbook,worksheet,141,Current_date,Date_1,Tier,Platform_List,exchange_rate)

def LaunchExcelCreationActivityIndicator(Current_date,ListTier,exchange_rate):
    Date_janv_1 = date(Current_date.year-1,12,1)
    Date_N_1 = date(Current_date.year-1,Current_date.month,1)
    Date_M_1 = Current_date - relativedelta(months=+1)
    Platform_List = con.execute("SELECT DISTINCT Code_Platform FROM Platform ORDER BY Code_Platform").fetchall()

    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir()+'/Activity Indicators '+Year+ '-' +Month+'.xlsx'
    workbook = xlsxwriter.Workbook(filepath)

    RawData(workbook,Current_date,ListTier,exchange_rate)
    Summary(workbook,Current_date,ListTier,exchange_rate)
    if Current_date.month !=1:
        ActivityKPI(workbook,Current_date,Date_M_1,Platform_List,exchange_rate)
    ActivityKPI(workbook,Current_date,Date_janv_1,Platform_List,exchange_rate)
    if Date_janv_1 != Date_N_1:
        ActivityKPI(workbook,Current_date,Date_N_1,Platform_List,exchange_rate)
    workbook.close()

if __name__ == '__main__':
    Current_date = date(2022,10,1)
    ListTier = NewCalculTier(Current_date)[0]
    RawData(Current_date,ListTier)
