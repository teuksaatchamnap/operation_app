import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta, datetime
from calendar import monthrange
import db
import tempfile
from dateutil.relativedelta import *
import calendar
from monthlyreport.ExcelSiteAnalysis import SiteAnalysis
from monthlyreport.Functionutils import CategoryExpenses, listSiteStillActive, CalculTier, Numberdaysopeningyear, CalculNombreMoisOuverture, Numberdaysopeningyear, listProvPlat, listDate, listAdvisorPerPlatform
import monthlyreport.ExcelKPI as ExcelKPI
from monthlyreport.ExcelSiteAnalysis import SiteAnalysis
import monthlyreport.Graph as Graph
import os


def CreateF2FROM(Current_date,Platform):
    global workbook
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    print(Platform)
    if len(Platform) > 1:
        filepath = tempfile.gettempdir()+'/F2F ' + Year + '-' + Month + '.xlsm'
        if os.path.exists(filepath):
            os.remove(filepath)
        workbook = xlsxwriter.Workbook(filepath)
    else:
        filepath = tempfile.gettempdir()+'/F2F %s '%(Platform[0]) + Year + '-' + Month + '.xlsm'
        if os.path.exists(filepath):
            os.remove(filepath)
        workbook = xlsxwriter.Workbook(filepath)

def WriteF2FYTD(Platform,Current_date,ListTier,exchange_rate):
    con = db.pool.connect()
    Date_janv = date(int(Current_date.year)-1,12,1)
    Date_N_1 = date(int(Current_date.year)-1,Current_date.month,1)
    Date_last_janv = date(int(Current_date.year)-2,12,1)
    Numberdays = ((Current_date + relativedelta(months =+1)) - (Date_janv + relativedelta(months =+1))).days

    worksheet_F2F = workbook.add_worksheet("F2F")
    worksheet_F2F.set_zoom(70)

    Site_format = workbook.add_format({'bg_color':"#DAEEF3",'bold': True, 'text_wrap' : True,'valign':'vcenter','center_across':True})
    Sales_format_YTD = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    Sales_format_month = workbook.add_format({'bg_color':"#00B050",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    Indicator_format_YTD = workbook.add_format({'bg_color':"#8DB4E2",'bold': True, 'text_wrap' : True,'valign':'vcenter','center_across':True})
    Indicator_format_month = workbook.add_format({'bg_color':"#C4E59F",'bold': True, 'text_wrap' : True,'valign':'vcenter','center_across':True})

    Date_format = workbook.add_format({'num_format' : 'dd/mm/yyyy'})
    Percentage_format = workbook.add_format({'num_format' : '0%'})
    Percentage_evol_format = workbook.add_format({'num_format' : '+0%;-0%'})
    Number_format = workbook.add_format({'num_format' : '# ##0'})
    Number_evol_format = workbook.add_format({'num_format' : '+# ##0;-# ##0'})
    Money_Dol_evol_format = workbook.add_format({'num_format' : '+# ##0 $;-# ##0 $'})
    
    Percentage_bold_format = workbook.add_format({'num_format' : '0%', 'bold':True})
    Percentage_bold_evol_format = workbook.add_format({'num_format' : '+0%;-0%', 'bold':True})
    Number_bold_format = workbook.add_format({'num_format' : '# ##0', 'bold': True})
    Money_Dol_bold_format = workbook.add_format({'num_format' : '# ##0 $', 'bold': True})
    Money_Riel_bold_format = workbook.add_format({'num_format' : '# ##0 ៛', 'bold': True})
    
    Title_format = workbook.add_format({'bold':True,"font_size":18,"center_across":True,'bg_color':'#FFFF00'})

    worksheet_F2F.set_column('A:BN',15)
    worksheet_F2F.freeze_panes(7,6)
    ColumnTotal = 1
    worksheet_F2F.write(6,ColumnTotal,"Site",Site_format)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Plaform",Site_format)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Advisor",Site_format)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Entrepreneur Arrival",Site_format)
    worksheet_F2F.write_comment(6,ColumnTotal, "Date of the last entrepreneur arrival on the site", {'x_scale': 3, 'y_scale': 0.8})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Tier",Site_format)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Total bottle exc. WinS",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Total bottle exc. WinS N-1",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"vs N-1 %",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Total bottle inc. WinS",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Total bottle inc. WinS N-1",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"vs N-1 %",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg Bot/day exc. WinS",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg Bot/day exc. WinS N-1",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"vs N-1 %",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg Bot/day inc. WinS",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg Bot/day inc. WinS N-1",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"vs N-1 %",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot Budget WinS",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% WinS vs Budget",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot Objectives exc. WinS",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% Sales vs Objecives",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot WinS",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot HOD",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot Shopkeeper",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% WinS",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% HOD",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% Shopkeeper",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot HOD N-1",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Increase HOD (#Hod vs #Hod N-1)",Sales_format_YTD)
    worksheet_F2F.set_column("%s:%s"%(xl_col_to_name(ColumnTotal),xl_col_to_name(ColumnTotal)),None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg Price",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg Price N-1",Sales_format_YTD)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% Price vs N-1",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"P&L $",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"P&L $ N-1",Sales_format_YTD)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"vs N-1 $",Sales_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Average Ent. Salary $",Sales_format_YTD)
    worksheet_F2F.write_comment(6,ColumnTotal, "Average Salary on YTD \n Empty cells means site is closed, cell = 0 means site is opened but paid 0 salary", {'x_scale': 3, 'y_scale': 0.8})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Average Inc. $",Sales_format_YTD)
    worksheet_F2F.write_comment(6,ColumnTotal, "Average Salary + Profit on YTD", {'x_scale': 3, 'y_scale': 0.8})
    ColumnEndYTD1 = ColumnTotal
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bottle exc. WinS",Sales_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bottle exc. WinS N-1",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"%s vs N-1",Sales_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bottle inc. WinS",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bottle inc. WinS N-1",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"%s vs N-1",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg bot/day exc. WinS",Sales_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg bot/day exc. WinS N-1",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% vs N-1",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg bot/day inc. WinS",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Avg bot/day inc. WinS N-1",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% vs N-1",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot objective exc. WinS",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% Sales vs objective",Sales_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot WinS Budget",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% WinS of budget",Sales_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot WinS",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot HOD",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"# Bot Shopkeeper",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% WinS of total",Sales_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnEndMonthly1 = ColumnTotal
    ColumnTotal +=1
    # worksheet_F2F.write(6,ColumnTotal,"% waste water (standard 20%)",Indicator_format_YTD)
    # ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Open days",Indicator_format_YTD)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"vs total possible",Indicator_format_YTD)
    ColumnEndYTD2 = ColumnTotal
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"% waste water (standard 20%)",Indicator_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Open days",Indicator_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"vs total possible",Indicator_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Number of delivery vehicle",Indicator_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Number of Operator",Indicator_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Number of Operator N-1",Indicator_format_month)
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'level':1,'hidden':True})
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Evolution Number of Operator",Indicator_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Bottles in Operation",Indicator_format_month)
    ColumnTotal +=1
    worksheet_F2F.write(6,ColumnTotal,"Bottles in Stock",Indicator_format_month)
    ColumnEndMonthly2 = ColumnTotal
    ColumnTotal +=1
    worksheet_F2F.set_column(ColumnTotal,ColumnTotal,None,None,{'hidden':True})

    for i in range(ColumnEndMonthly2):
        if i+6 <= ColumnEndYTD1:
            worksheet_F2F.write(0,i+6,"YTD",Title_format)
        elif i+6 <= ColumnEndMonthly1:
            worksheet_F2F.write(0,i+6,"Monthly",Title_format)
        elif i+6 <= ColumnEndYTD2:
            worksheet_F2F.write(0,i+6,"YTD",Title_format)
        elif i <= ColumnEndYTD2:
            worksheet_F2F.write(0,i+6,"Monthly",Title_format)

    Category_expenses = CategoryExpenses()
    ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Old_Platform IN %s 
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(Date_janv+relativedelta(month=+1),Platform)).fetchall()

    ListOnlysiteLikeforLike = [i[0] for i in ListSite_LikeforLike]
    ListSite_notLikeforLike = con.execute("SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites INNER JOIN Sales ON Sites.Id_Site = Sales.Id_Site WHERE 1 = %s AND Sites.Id_Site NOT IN %s AND Old_Platform IN %s ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site",(1,ListOnlysiteLikeforLike,Platform)).fetchall()

    ListAllSite = ListSite_LikeforLike + ListSite_notLikeforLike

    allSales_month = con.execute("SELECT Id_Site,SUM(Total_Sales - Bottle_Sales), SUM(WiS_Sales),SUM(Hod_Sales),SUM(Shopkeeper_Sales),SUM(Number_Open_Days) FROM Sales WHERE Month = %s GROUP BY Id_Site",(Current_date)).fetchall()
    allSales_lastyear_month = con.execute("SELECT Id_Site,SUM(Total_Sales - Bottle_Sales), SUM(WiS_Sales),SUM(Hod_Sales),SUM(Shopkeeper_Sales),SUM(Number_Open_Days) FROM Sales WHERE Month = %s GROUP BY Id_Site",(Date_N_1)).fetchall()
    allBot_day_month = con.execute("SELECT Sales.Id_Site,SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days), SUM(Total_Sales-WiS_Sales-Bottle_Sales)/SUM(Number_Open_Days) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month = %s GROUP BY Sales.Id_Site",(Current_date)).fetchall()
    allBot_day_lastyear_month = con.execute("SELECT Sales.Id_Site,SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days), SUM(Total_Sales-WiS_Sales-Bottle_Sales)/SUM(Number_Open_Days) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month = %s GROUP BY Sales.Id_Site",(Date_N_1)).fetchall()
    allObjectives_month = con.execute("SELECT Id_Site, PrevisionsSalesTot FROM PrevisionsSales WHERE Month = %s",Current_date).fetchall()

    allBot_day = con.execute("SELECT Sales.Id_Site,SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days), SUM(Total_Sales-WiS_Sales-Bottle_Sales)/SUM(Number_Open_Days) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Sales.Id_Site",(Current_date,Date_janv)).fetchall()
    allBot_day_lastyear = con.execute("SELECT Sales.Id_Site,SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days), SUM(Total_Sales-WiS_Sales-Bottle_Sales)/SUM(Number_Open_Days) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Sales.Id_Site",(Date_N_1,Date_last_janv)).fetchall()
    allDay = con.execute("SELECT COUNT(Total_Sales),SUM(Number_Open_Days),Id_Site FROM Sales WHERE Month <= %s AND Month > %s AND Number_Open_Days < 20 GROUP BY Id_Site",(Current_date,Date_janv)).fetchall()
    allDay_lastyear = con.execute("SELECT COUNT(Total_Sales),SUM(Number_Open_Days),Id_Site FROM Sales WHERE Month <= %s AND Month > %s AND Number_Open_Days < 20 GROUP BY Id_Site",(Date_N_1,Date_last_janv)).fetchall()
    allSales = con.execute("SELECT Id_Site,SUM(Total_Sales - Bottle_Sales), SUM(WiS_Sales),SUM(Hod_Sales),SUM(Shopkeeper_Sales),SUM(Number_Open_Days) FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(Current_date,Date_janv)).fetchall()
    allSales_lastyear = con.execute("SELECT Id_Site,SUM(Total_Sales - Bottle_Sales), SUM(WiS_Sales),SUM(Hod_Sales),SUM(Shopkeeper_Sales) FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(Date_N_1,Date_last_janv)).fetchall()

    allObjectives = con.execute("SELECT Id_Site, SUM(PrevisionsSalesTot) FROM PrevisionsSales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(Current_date,Date_janv)).fetchall()

    query = con.execute('SELECT SUM(Amount_Expenses)/%s,Expenses.Id_Site FROM Expenses JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Expenses.Month <= %s AND Expenses.Month > %s AND Category_expenses IN %s GROUP BY Sites.Id_Site', (exchange_rate,Current_date, Date_janv, Category_expenses))
    allTotal_cost = query.fetchall()
    allTotal_revenue = con.execute("SELECT Id_Site,SUM(Total_Income)/%s,AVG(Total_Price_Average),COUNT(Total_Sales) FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site ",(exchange_rate,Current_date,Date_janv)).fetchall()

    query = con.execute('SELECT SUM(Amount_Expenses)/%s,Expenses.Id_Site  FROM Expenses JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Expenses.Month <= %s AND Expenses.Month > %s AND Category_expenses IN %s GROUP BY Sites.Id_Site', (exchange_rate,Date_N_1, Date_last_janv, Category_expenses))
    allTotal_cost_lastyear = query.fetchall()
    allTotal_revenue_lastyear = con.execute("SELECT Id_Site,SUM(Total_Income)/%s,AVG(Total_Price_Average),COUNT(Total_Sales) FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site ",(exchange_rate,Date_N_1, Date_last_janv)).fetchall()

    allSalaryEnt = con.execute("SELECT SUM(Amount_Expenses)/%s,Expenses.Id_Site FROM Expenses WHERE (Ref_expenses='variable_salary_entrepreneurs' OR Ref_expenses='fix_salary_entrepreneurs') AND Expenses.Month <= %s AND Expenses.Month > %s GROUP BY Id_Site",(exchange_rate,Current_date,Date_janv)).fetchall()
    allSalaryEnt_lastyear = con.execute("SELECT SUM(Amount_Expenses)/%s,Expenses.Id_Site FROM Expenses WHERE (Ref_expenses='variable_salary_operators' OR Ref_expenses='fix_salary_operators') AND Expenses.Month <= %s AND Expenses.Month > %s GROUP BY Id_Site",(exchange_rate,Date_N_1,Date_last_janv)).fetchall()
    allIndicators = con.execute("SELECT Id_Site,SUM(Water_consume)/1000,AVG(Number_of_Vehicle),AVG(Number_Bottles_in_Operation),AVG(Number_of_Operator) FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(Current_date,Date_janv)).fetchall()
    allIndicators_lastyear = con.execute("SELECT Id_Site,SUM(Water_consume)/1000,AVG(Number_of_Vehicle),AVG(Number_Bottles_in_Operation),AVG(Number_of_Operator) FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(Date_N_1,Date_last_janv)).fetchall()

    allEntrepreneurDate = con.execute("""
        SELECT ep.Working_Date, ep.Id_Site, ep.Submitted_Date
        FROM entrepreneur_profiles ep
        INNER JOIN (
            SELECT Id_Site, MAX(Submitted_Date) AS Max_Submitted_Date
            FROM entrepreneur_profiles
            WHERE Status = 'new_entrepreneur_coming' AND Submitted_Date <= %s
            GROUP BY Id_Site
        ) latest ON ep.Id_Site = latest.Id_Site AND ep.Submitted_Date = latest.Max_Submitted_Date
        WHERE ep.Status = 'new_entrepreneur_coming'
        """,Current_date).fetchall()

    # allWaterConsume = con.execute("SELECT Id_Site,SUM(Water_consume)/1000 FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(Current_date,Date_janv+relativedelta(months=+2))).fetchall()
    # allWaterConsume_lastyear = con.execute("SELECT Id_Site,SUM(Water_consume)/1000 FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(Date_N_1,Date_last_janv+relativedelta(months=+2))).fetchall()
    
    ####    

    allIndicators_month = con.execute("SELECT Id_Site,SUM(Water_consume)/1000,AVG(Number_of_Vehicle),AVG(Number_Bottles_in_Operation),AVG(Number_of_Operator),AVG(Number_Bottles_in_Stock) FROM Indicators WHERE Month = %s GROUP BY Id_Site",(Current_date)).fetchall()
    allIndicators_month_lastyear = con.execute("SELECT Id_Site,SUM(Water_consume)/1000,AVG(Number_of_Vehicle),AVG(Number_Bottles_in_Operation),AVG(Number_of_Operator),AVG(Number_Bottles_in_Stock) FROM Indicators WHERE Month = %s GROUP BY Id_Site",(Date_N_1)).fetchall()


    allSchoolSalesBudget = con.execute("SELECT SchoolSalesBudget,Id_Site FROM Sites").fetchall()
    allSchoolSales_YTD = con.execute("SELECT COUNT(WiS_Sales),Id_Site FROM DailySales WHERE Month <= %s AND Month > %s AND WiS_Sales > 0 GROUP BY Id_Site",(Current_date,Date_janv)).fetchall()
    allSchoolSales_month = con.execute("SELECT COUNT(WiS_Sales),Id_Site FROM DailySales WHERE Month = %s AND WiS_Sales > 0 GROUP BY Id_Site",(Current_date)).fetchall()

    MaxOpenDays_YTD = 0
    ListMaxOpendays_YTD = []
    MaxOpenDays_month = 0
    ListMaxOpendays_month = []
    for i in range(len(allSchoolSales_YTD)):

        if allSchoolSales_YTD[i][0] > MaxOpenDays_YTD:
            ListMaxOpendays_YTD.append(allSchoolSales_YTD[i][0])

        if len(ListMaxOpendays_YTD)>5 and min(ListMaxOpendays_YTD) > MaxOpenDays_YTD:
            MaxOpenDays_YTD = min(ListMaxOpendays_YTD)
            ListMaxOpendays_YTD = []

    for j in range(len(allSchoolSales_month)):
        if allSchoolSales_month[j][0] > MaxOpenDays_month:
            ListMaxOpendays_month.append(allSchoolSales_month[j][0])
        if len(ListMaxOpendays_month)>5 and min(ListMaxOpendays_month) > MaxOpenDays_month:
            MaxOpenDays_month = min(ListMaxOpendays_month)
            ListMaxOpendays_month = []


    worksheet_F2F.autofilter(6,0,len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)+7,ColumnEndMonthly2)

    for i in range(len(ListAllSite)):
        Column = 0
        if i < len(ListSite_LikeforLike):
            worksheet_F2F.write(i+7,Column,"Like for Like",Number_bold_format)
            Column +=1
        else:
            worksheet_F2F.write(i+7,Column,"Others",Number_bold_format)
            Column +=1
        worksheet_F2F.write(i+7,Column,ListAllSite[i][0])
        Column +=1
        worksheet_F2F.write(i+7,Column,ListAllSite[i][1])
        Column +=1
        worksheet_F2F.write(i+7,Column,ListAllSite[i][2])
        Column +=1

        EntrepreneurArrival = list(filter(lambda row: row[1] == ListAllSite[i][0], allEntrepreneurDate)) or [("","","")]
        BotDay = list(filter(lambda row: row[0] == ListAllSite[i][0], allBot_day)) or [(0,"","")]
        BotDay_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allBot_day_lastyear)) or [(0,"","")]
        BotDay_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allBot_day_month)) or [(0,"","")]
        BotDay_lastyear_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allBot_day_lastyear_month)) or [(0,"","")]
        Sales = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales)) or [(0,0,0,0,0,0)]
        Sales_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales_lastyear)) or [(0,0,0,0,0,0)]
        ### SALES FOR MARCH BECAUSE OF WATER METER
        # Sales_MARCH = list(filter(lambda row: row[0] == ListAllSite[i][0], allSalesMARCH)) or [(0,0,0,0,0,0)]
        # Sales_lastyear_MARCH = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales_lastyear_MARCH)) or [(0,0,0,0,0,0)]
        ###
        ObjectiveSales = list(filter(lambda row: row[0] == ListAllSite[i][0], allObjectives)) or [(0,0)]
        Sales_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales_month)) or [(0,0,0,0,0,0)]
        Sales_lastyear_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales_lastyear_month)) or [(0,0,0,0,0,0)]
        ObjectiveSales_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allObjectives_month)) or [(0,0)]
        Cost = list(filter(lambda row: row[1] == ListAllSite[i][0], allTotal_cost)) or [(0,0)]
        Total_Revenue = list(filter(lambda row: row[0] == ListAllSite[i][0], allTotal_revenue)) or [(0,0,"",0)]
        Cost_lastyear = list(filter(lambda row: row[1] == ListAllSite[i][0], allTotal_cost_lastyear)) or [(0,0)]
        Total_Revenue_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allTotal_revenue_lastyear)) or [(0,0,"",0)]
        Salary_ent = list(filter(lambda row: row[1] == ListAllSite[i][0], allSalaryEnt)) or [(0,0)]
        Salary_ent_lastyear = list(filter(lambda row: row[1] == ListAllSite[i][0], allSalaryEnt_lastyear)) or [(0,0)]
        Indicators = list(filter(lambda row: row[0] == ListAllSite[i][0], allIndicators)) or [(0,0,0,0,0)]
        Indicators_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allIndicators_lastyear)) or [(0,0,0,0,0)]
        ##Change Water Consume to have it start on March because of issue with compteur
        # WaterConsume = list(filter(lambda row: row[0] == ListAllSite[i][0], allWaterConsume)) or [(0,0,0,0,0)]
        # WaterConsume_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allWaterConsume_lastyear)) or [(0,0,0,0,0)]
        ##
        Indicators_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allIndicators_month)) or [(0,0,0,0,0,0)]
        Indicators_monthlastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allIndicators_month_lastyear)) or [(0,0,0,0,0,0)]
        SchoolBudget = list(filter(lambda row: row[1] == ListAllSite[i][0], allSchoolSalesBudget)) or [(0,0,0,0,0)]
        Tier = list(filter(lambda row: row[0] == ListAllSite[i][0], ListTier)) or [(0,0)]

        worksheet_F2F.write(i+7,Column,EntrepreneurArrival[0][0],Date_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Tier[0][1])
        Column += 1

##############################################YTD#########################################
        #Bottles total
        worksheet_F2F.write(i+7,Column,(Sales[0][1]-Sales[0][2]),Number_format)
        ColumnTotBot_noWinS = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,(Sales_lastyear[0][1]-Sales_lastyear[0][2]),Number_format)
        ColumnTotBotLastYear_noWinS = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'=IFERROR((%s/%s)-1,0)'%(xl_rowcol_to_cell(i+7,ColumnTotBot_noWinS),xl_rowcol_to_cell(i+7,ColumnTotBotLastYear_noWinS)),Percentage_evol_format)
        Column +=1

        worksheet_F2F.write(i+7,Column,(Sales[0][1]),Number_format)
        ColumnTotBot = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,(Sales_lastyear[0][1]),Number_format)
        ColumnTotBotLastYear= Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'=IFERROR((%s/%s)-1,0)'%(xl_rowcol_to_cell(i+7,ColumnTotBot),xl_rowcol_to_cell(i+7,ColumnTotBotLastYear)),Percentage_evol_format)
        Column +=1

        #Bottles per day
        worksheet_F2F.write(i+7,Column,BotDay[0][2],Number_format)
        ColumnBotDayYTD_noWinS = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,BotDay_lastyear[0][2],Number_format)
        ColumnBotDayYTDLastYear_noWinS = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'=IFERROR((%s/%s)-1,0)'%(xl_rowcol_to_cell(i+7,ColumnBotDayYTD_noWinS),xl_rowcol_to_cell(i+7,ColumnBotDayYTDLastYear_noWinS)),Percentage_evol_format)
        ColumnEvolBotDay_noWiNS = Column
        Column +=1

        worksheet_F2F.write(i+7,Column,BotDay[0][1],Number_format)
        ColumnBotDayYTD = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,BotDay_lastyear[0][1],Number_format)
        ColumnBotDayYTDLastYear = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'=IFERROR((%s/%s)-1,0)'%(xl_rowcol_to_cell(i+7,ColumnBotDayYTD),xl_rowcol_to_cell(i+7,ColumnBotDayYTDLastYear)),Percentage_evol_format)
        ColumnEvolBotDay = Column
        Column +=1

        

        #Wins Budget
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s*%s,\"\")"%(SchoolBudget[0][0],MaxOpenDays_YTD),Number_format)
        ColumnBudgetSchool = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/%s,\"\")"%(Sales[0][2],xl_rowcol_to_cell(i+7,ColumnBudgetSchool)),Percentage_format)
        ColumnSalesvsBudget = Column
        Column +=1

        #Sales Objectives
        worksheet_F2F.write(i+7,Column,ObjectiveSales[0][1],Number_format)
        ColumnTargetSales = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"IFERROR(%s/%s,\"\")"%(xl_rowcol_to_cell(i+7,ColumnTotBot_noWinS),xl_rowcol_to_cell(i+7,ColumnTargetSales)),Percentage_format)
        Column +=1

        #Channel
        worksheet_F2F.write(i+7,Column,Sales[0][2],Number_format)
        ColumnSalesWinS = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales[0][3],Number_format)
        ColumnSalesHOD = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales[0][4],Number_format)
        ColumnSalesShop = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/(%s+%s+%s),0)"%(xl_rowcol_to_cell(i+7,ColumnSalesWinS),xl_rowcol_to_cell(i+7,ColumnSalesWinS),xl_rowcol_to_cell(i+7,ColumnSalesHOD),xl_rowcol_to_cell(i+7,ColumnSalesShop)),Percentage_format)
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/(%s+%s+%s),0)"%(xl_rowcol_to_cell(i+7,ColumnSalesHOD),xl_rowcol_to_cell(i+7,ColumnSalesWinS),xl_rowcol_to_cell(i+7,ColumnSalesHOD),xl_rowcol_to_cell(i+7,ColumnSalesShop)),Percentage_format)
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/(%s+%s+%s),0)"%(xl_rowcol_to_cell(i+7,ColumnSalesShop),xl_rowcol_to_cell(i+7,ColumnSalesWinS),xl_rowcol_to_cell(i+7,ColumnSalesHOD),xl_rowcol_to_cell(i+7,ColumnSalesShop)),Percentage_format)
        Column +=1

        #Channel vs last year
        worksheet_F2F.write(i+7,Column,Sales_lastyear[0][4],Number_format)
        ColumnSalesHODLastyear = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/%s-1,\"\")"%(xl_rowcol_to_cell(i+7,ColumnSalesHOD),xl_rowcol_to_cell(i+7,ColumnSalesHODLastyear)),Percentage_evol_format)
        Column +=1

        #Price
        worksheet_F2F.write(i+7,Column,Total_Revenue[0][2],Money_Riel_bold_format)
        ColumnRevenue = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Total_Revenue_lastyear[0][2],Money_Riel_bold_format)
        ColumnRevenueLastYear = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'=IFERROR(%s/%s-1,0)'%(xl_rowcol_to_cell(i+7,ColumnRevenue),xl_rowcol_to_cell(i+7,ColumnRevenueLastYear)),Percentage_evol_format)
        Column +=1

        #P&L
        worksheet_F2F.write(i+7,Column,Total_Revenue[0][1]-Cost[0][0],Money_Dol_bold_format)
        ColumnProfit = Column 
        Column +=1
        worksheet_F2F.write(i+7,Column,Total_Revenue_lastyear[0][1]-Cost_lastyear[0][0],Money_Dol_bold_format)
        ColumnProfitLastYear = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'=IFERROR(%s-%s,0)'%(xl_rowcol_to_cell(i+7,ColumnProfit),xl_rowcol_to_cell(i+7,ColumnProfitLastYear)),Money_Dol_evol_format)
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'IFERROR(%s/%s,"")'%(Salary_ent[0][0],Total_Revenue[0][3]),Money_Dol_bold_format)
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,'IFERROR((%s+%s)/%s,"")'%(Salary_ent[0][0],xl_rowcol_to_cell(i+7,ColumnProfit),Total_Revenue[0][3]),Money_Dol_bold_format)
        Column +=1

##############################################  Monthly  #########################################

        worksheet_F2F.write(i+7,Column,Sales_month[0][1]-Sales_month[0][2],Number_format)
        ColumnSalesMonthly_noWinS = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales_lastyear_month[0][1]-Sales_lastyear_month[0][2],Number_format)
        ColumnSalesMonthlyLastYear_noWinS = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnSalesMonthly_noWinS),xl_rowcol_to_cell(i+7,ColumnSalesMonthlyLastYear_noWinS)),Percentage_evol_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales_month[0][1],Number_format)
        ColumnSalesMonthly = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales_lastyear_month[0][1],Number_format)
        ColumnSalesMonthlyLastYear = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnSalesMonthly),xl_rowcol_to_cell(i+7,ColumnSalesMonthlyLastYear)),Percentage_evol_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,BotDay_month[0][2],Number_format)
        ColumnBotDayMonthly_noWinS = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,BotDay_lastyear_month[0][2],Number_format)
        ColumnBotDayMonthlyLastYear_noWinS = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnBotDayMonthly_noWinS),xl_rowcol_to_cell(i+7,ColumnBotDayMonthlyLastYear_noWinS)),Percentage_evol_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,BotDay_month[0][1],Number_format)
        ColumnBotDayMonthly = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,BotDay_lastyear_month[0][1],Number_format)
        ColumnBotDayMonthlyLastYear = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnBotDayMonthly),xl_rowcol_to_cell(i+7,ColumnBotDayMonthlyLastYear)),Percentage_evol_format)
        Column +=1

        #Budget Sales 
        worksheet_F2F.write(i+7,Column,ObjectiveSales_month[0][1],Number_format)
        ColumnTargetMonthly = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"IFERROR(%s/%s,0)"%(xl_rowcol_to_cell(i+7,ColumnSalesMonthly_noWinS),xl_rowcol_to_cell(i+7,ColumnTargetMonthly)),Percentage_format)
        Column +=1

        #WinS LINE NOT MODIFIED
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s*%s,0)"%(SchoolBudget[0][0],MaxOpenDays_month),Number_format)
        ColumnBudgetSchoolMonthly = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"=IFERROR(%s/%s,0)"%(Sales_month[0][2],xl_rowcol_to_cell(i+7,ColumnBudgetSchoolMonthly)),Percentage_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales_month[0][2],Number_format)
        ColumnWinSMonthly = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales_month[0][3],Number_format)
        ColumnHODMonthly = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales_month[0][4],Number_format)
        ColumnShopMonthly = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"IFERROR(%s/(%s+%s+%s),0)"%(xl_rowcol_to_cell(i+7,ColumnWinSMonthly),xl_rowcol_to_cell(i+7,ColumnWinSMonthly),xl_rowcol_to_cell(i+7,ColumnHODMonthly),xl_rowcol_to_cell(i+7,ColumnShopMonthly)),Percentage_format)
        Column +=1

##############################################  YTD  #########################################
        #Indicators
        # worksheet_F2F.write_formula(i+7,Column,'=IFERROR(%s/(%s*20/1000)-1,"")'%(WaterConsume[0][1],Sales_MARCH[0][1]),Percentage_format)
        # Column +=1

        worksheet_F2F.write(i+7,Column,Sales[0][5],Number_format)
        ColumnOpenDays = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"IFERROR(%s/%s,"")"%(xl_rowcol_to_cell(i+7,ColumnOpenDays),Numberdays),Percentage_format)
        Column +=1

##############################################  Monthly  #########################################
        #Indicators
        worksheet_F2F.write_formula(i+7,Column,'=IFERROR((%s-%s*20/1000)/%s,"")'%(Indicators_month[0][1],Sales_month[0][1],Indicators_month[0][1]),Percentage_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Sales_month[0][5],Number_format)
        ColumnOpenDaysMonthly = Column
        Column +=1
        worksheet_F2F.write_formula(i+7,Column,"IFERROR(%s/%s,"")"%(xl_rowcol_to_cell(i+7,ColumnOpenDaysMonthly),monthrange(Current_date.year,Current_date.month)[1]),Percentage_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Indicators_month[0][2],Number_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Indicators_month[0][4],Number_format)
        ColumnOperator = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,Indicators_monthlastyear[0][4],Number_format)
        ColumnOperatorLastYear = Column
        Column +=1
        worksheet_F2F.write(i+7,Column,"=IFERROR(%s-%s,0)"%(xl_rowcol_to_cell(i+7,ColumnOperator),xl_rowcol_to_cell(i+7,ColumnOperatorLastYear)),Number_evol_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Indicators_month[0][3],Number_format)
        Column +=1
        worksheet_F2F.write(i+7,Column,Indicators_month[0][5],Number_format)
        Column +=1

        worksheet_F2F.write_formula(i+7,Column,"SUBTOTAL(3,A%s)"%(i+8))
        LastColumnforFormula = Column
        Column +=1

##############################################  Total  #########################################
    red_bg_format = workbook.add_format({'bg_color':'#DA9694'})
    worksheet_F2F.conditional_format('%s8:%s%s'%(xl_col_to_name(ColumnEvolBotDay_noWiNS),xl_col_to_name(ColumnEvolBotDay_noWiNS),7+len(ListAllSite)),{'type':'icon_set','icon_style':'3_arrows','icons':[{'criteria':'>=','type':'number','value':0.001},{'criteria':'<=','type':'number','value':0.001}]})
    worksheet_F2F.conditional_format('%s8:%s%s'%(xl_col_to_name(ColumnEvolBotDay),xl_col_to_name(ColumnEvolBotDay),7+len(ListAllSite)),{'type':'icon_set','icon_style':'3_arrows','icons':[{'criteria':'>=','type':'number','value':0.001},{'criteria':'<=','type':'number','value':0.001}]})
    worksheet_F2F.conditional_format('%s8:%s%s'%(xl_col_to_name(ColumnSalesvsBudget),xl_col_to_name(ColumnSalesvsBudget),7+len(ListAllSite)),{'type':'cell','criteria':'>','value':1.01,'format':red_bg_format})
    worksheet_F2F.conditional_format('Y8:Y%s'%(7+len(ListAllSite)),{'type':'cell','criteria':'>=','value':0.3,'format':red_bg_format})
    worksheet_F2F.conditional_format('AI8:AI%s'%(7+len(ListAllSite)),{'type':'icon_set','icon_style':'3_arrows','icons':[{'criteria':'>=','type':'number','value':0.001},{'criteria':'<=','type':'number','value':0.001}]})
   
    worksheet_F2F.write('E3','Total Like for Like')
    worksheet_F2F.write('E4','Total Other')
    worksheet_F2F.write('E5','Total All')

    worksheet_F2F.write('F2',"Number of sites")
    ColumnSum = 5

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(%s8:%s%s>0)*(SUBTOTAL(3,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(%s8:%s%s>0)*(SUBTOTAL(3,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum+1),xl_col_to_name(ColumnSum+1),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=%s+%s'%(xl_rowcol_to_cell(2,ColumnSum),xl_rowcol_to_cell(3,ColumnSum)),Number_bold_format)
    ColumnSum +=1 

    ############## YTD Bot sold ###########
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1   
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    ############## YTD Bot/day ###########
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    ############## YTD WinS Budget + Channel  ###########
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1
    
    #T
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/(%s3),0)'%(xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnBudgetSchool)),Percentage_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/(%s4),0)'%(xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnBudgetSchool)),Percentage_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/(%s5),0)'%(xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnBudgetSchool)),Percentage_bold_format)
    ColumnSum +=1 
    
    #U
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/(%s3),0)'%(xl_col_to_name(ColumnTotBot_noWinS),xl_col_to_name(ColumnTargetSales)),Percentage_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/(%s4),0)'%(xl_col_to_name(ColumnTotBot_noWinS),xl_col_to_name(ColumnTargetSales)),Percentage_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/(%s5),0)'%(xl_col_to_name(ColumnTotBot_noWinS),xl_col_to_name(ColumnTargetSales)),Percentage_bold_format)
    ColumnSum +=1 
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1

    worksheet_F2F.write_formula(2,ColumnSum,"=IFERROR(%s3/(%s3+%s3+%s3),0)"%(xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,"=IFERROR(%s4/(%s4+%s4+%s4),0)"%(xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,"=IFERROR(%s5/(%s5+%s5+%s5),0)"%(xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    ColumnSum +=1 
    
    #AF
    worksheet_F2F.write_formula(2,ColumnSum,"=IFERROR(%s3/(%s3+%s3+%s3),0)"%(xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,"=IFERROR(%s4/(%s4+%s4+%s4),0)"%(xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,"=IFERROR(%s5/(%s5+%s5+%s5),0)"%(xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    ColumnSum +=1 
    
    #AG
    worksheet_F2F.write_formula(2,ColumnSum,"=IFERROR(%s3/(%s3+%s3+%s3),0)"%(xl_col_to_name(ColumnSalesShop),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,"=IFERROR(%s4/(%s4+%s4+%s4),0)"%(xl_col_to_name(ColumnSalesShop),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,"=IFERROR(%s5/(%s5+%s5+%s5),0)"%(xl_col_to_name(ColumnSalesShop),xl_col_to_name(ColumnSalesWinS),xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesShop)),Percentage_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesHODLastyear)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesHODLastyear)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSalesHOD),xl_col_to_name(ColumnSalesHODLastyear)),Percentage_bold_evol_format)
    ColumnSum +=1 

    ###################### P&L ####################

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 
    
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3-%s3,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4-%s4,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5-%s5,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    #############MONTHLY BOT SOLD##########

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    ########## MONTHLY BOT/DAY###########
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1  

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1  

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1   

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Like for Like",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(AVERAGEIFS(%s8:%s%s,A8:A%s,"Others",%s8:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(1,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1  

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSum-2),xl_col_to_name(ColumnSum-1)),Percentage_bold_evol_format)
    ColumnSum +=1 

    ################ OBJ AND CHANNEL ########
    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3,0)'%(xl_col_to_name(ColumnSalesMonthly_noWinS),xl_col_to_name(ColumnTargetMonthly)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4,0)'%(xl_col_to_name(ColumnSalesMonthly_noWinS),xl_col_to_name(ColumnTargetMonthly)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5,0)'%(xl_col_to_name(ColumnSalesMonthly_noWinS),xl_col_to_name(ColumnTargetMonthly)),Percentage_bold_evol_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3,0)'%(xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnBudgetSchoolMonthly)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(%s4/%s4,0)'%(xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnBudgetSchoolMonthly)),Percentage_bold_evol_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(%s5/%s5,0)'%(xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnBudgetSchoolMonthly)),Percentage_bold_evol_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnSum +=1 

    worksheet_F2F.write_formula(2,ColumnSum,"=IFERROR(%s3/(%s3+%s3+%s3),0)"%(xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnHODMonthly),xl_col_to_name(ColumnShopMonthly)),Percentage_bold_format)
    worksheet_F2F.write_formula(3,ColumnSum,"=IFERROR(%s4/(%s4+%s4+%s4),0)"%(xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnHODMonthly),xl_col_to_name(ColumnShopMonthly)),Percentage_bold_format)
    worksheet_F2F.write_formula(4,ColumnSum,"=IFERROR(%s5/(%s5+%s5+%s5),0)"%(xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnWinSMonthly),xl_col_to_name(ColumnHODMonthly),xl_col_to_name(ColumnShopMonthly)),Percentage_bold_format)
    ColumnSum +=1
    
def WriteKPIF2F(Current_date,Date_janv,exchange_rate):
    worksheet = workbook.add_worksheet("KPI F2F %s-%s %s"%((Date_janv+relativedelta(months=+1)).strftime("%b"),Current_date.strftime("%b"),Current_date.year))
    con= db.pool.connect()
    Platform_List = con.execute("SELECT DISTINCT Code_Platform FROM Platform ORDER BY Code_Platform").fetchall()

    Tier = ExcelKPI.KPIFormat(workbook,worksheet,Current_date,Date_janv,2018,Platform_List)
    ExcelKPI.KPINbSite(workbook,worksheet,2,Current_date,Date_janv,Tier,Platform_List)
    ExcelKPI.KPINbSitePercentage(workbook,worksheet,12,Current_date,Date_janv,Tier,Platform_List)
    ExcelKPI.KPIBeneficiaries(workbook,worksheet,21,Current_date,Date_janv,Tier,Platform_List)
    ExcelKPI.KPITotBotLikeForLikeGrowth(workbook,worksheet,30,Current_date,Date_janv,Tier,Platform_List)
    ExcelKPI.KPITotBot(workbook,worksheet,39,Current_date,Date_janv,Tier,Platform_List,False)
    ExcelKPI.KPITotBotGrowth(workbook,worksheet,48,Current_date,Date_janv,Tier,Platform_List)
    ExcelKPI.KPITotBot(workbook,worksheet,58,Current_date,Date_janv,Tier,Platform_List,True,True)
    ExcelKPI.KPIBotDay(workbook,worksheet,67,Current_date,Date_janv,Tier,Platform_List,False)
    ExcelKPI.KPINbSiteMoreThan3Operators(workbook,worksheet,77,Current_date,Date_janv,Tier,Platform_List)
    ExcelKPI.KPINbSiteMoreThan3OperatorsPercentage(workbook,worksheet,85,Current_date,Date_janv,Tier,Platform_List,True)
    ExcelKPI.KPISalaryEnt(workbook,worksheet,93,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPITotInc(workbook,worksheet,102,Current_date,Date_janv,Tier,Platform_List,exchange_rate,True)
    ExcelKPI.KPIPL(workbook,worksheet,111,Current_date,Date_janv,Tier,Platform_List,exchange_rate)

def WriteGraph(Current_date,ListPlatform):
    con = db.pool.connect()
    worksheet_graph = workbook.add_worksheet("Graphs")
    Date_format = workbook.add_format({'num_format':'mmm-yyyy'})
    Number_format = workbook.add_format({'num_format':'# ##0'})
    Date_N_1 = date(int(Current_date.year) - 1,Current_date.month,1)
    Date_N_2_janv = date(int(Current_date.year) - 2,1,1)
    Platform = con.execute("SELECT DISTINCT Old_Platform FROM Sites WHERE Old_Platform <> '' AND Old_Platform <> 'Stop' AND Old_Platform <> 'Dead'").fetchall()
    Total_Sales = con.execute("SELECT AVG((Total_Sales-Bottle_Sales)/(CASE WHEN Number_Open_Days>20 THEN DAYOFMONTH(LAST_DAY(Month)) ELSE Number_Open_Days END)),AVG((Total_Sales-Bottle_Sales-WiS_Sales)/(CASE WHEN Number_Open_Days>20 THEN DAYOFMONTH(LAST_DAY(Month)) ELSE Number_Open_Days END)),Month FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Platform <> 'Dead' AND Month <= %s AND Month >= %s GROUP BY Month ORDER BY Month",Current_date,Date_N_2_janv).fetchall()
    Total_Objective = con.execute("""SELECT AVG(PrevisionsSalesTot/DAYOFMONTH(LAST_DAY(Month))),Month FROM PrevisionsSales
                                        INNER JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site WHERE Platform <> 'Dead' AND 
                                        Month <= %s AND Month >= %s AND PrevisionsSalesTot > 0 GROUP BY Month ORDER BY Month""",date(Current_date.year,12,1),date(Current_date.year,1,1)).fetchall()   
    worksheet_graph.merge_range(0,50,0,52,"Total")
    worksheet_graph.write(1,49,"Month")
    worksheet_graph.write(1,50,"Total Sales (Bot/day)")
    worksheet_graph.write(1,51,"Total Sales exc. WinS (Bot/day)")
    worksheet_graph.write(1,52,"Objective exc. WinS (Bot/day)")

    for i in range(len(Total_Sales)):
        worksheet_graph.write(i+2,49,Total_Sales[i][2].month)
        worksheet_graph.write(i+2,50,Total_Sales[i][0],Number_format)
        worksheet_graph.write(i+2,51,Total_Sales[i][1],Number_format)
    for j in range(len(Total_Objective)):
        worksheet_graph.write(j+2,52,Total_Objective[j][0],Number_format)
    chart_totalsales = workbook.add_chart({'type' : 'line'})
    # chart_totalsales.add_series({
    # 'name' :     "Objective",
    # 'categories': '=\'Graphs\'!$AX$3:$AX$14',
    # 'values':     '=\'Graphs\'!$BA$3:$BA$14',
    # 'data_labels': {'value': False},
    # 'line' : {'color':'#4F6228','dash_type': 'dash_dot','width':2},
    # })
    chart_totalsales.add_series({
    'name' :     str(int(Current_date.year)-2),
    'categories': '=\'Graphs\'!$AX$3:$AX$14',
    'values':     '=\'Graphs\'!$AY$3:$AY$14',
    'data_labels': {'value': False},
    'line' : {'color':'#DCE6F2'},
    })
    chart_totalsales.add_series({
    'name' :     str(int(Current_date.year)-1),
    'categories': '=\'Graphs\'!$AX$15:$AX$26',
    'values':     '=\'Graphs\'!$AY$15:$AY$26',
    'data_labels': {'value': False},
    'line' : {'color':'#558ED5'},
    })
    chart_totalsales.add_series({
    'name' :     str(Current_date.year),
    'categories': '=\'Graphs\'!$AX$27:$AX$%s'%(27+int(Current_date.month)-1),
    'values':     '=\'Graphs\'!$AY$27:$AY$%s'%(27+int(Current_date.month)-1),
    'data_labels': {'value': False},
    'line' : {'color':'#254061'},
    'marker': {'type': 'diamond','fill':   {'color': '#254061'}},
    })
    chart_totalsales.set_title({
    'name': 'Total Sales (Bot/Day)',
    'name_font': {
        'name': 'Calibri',
        'size': 12,
        'color': 'black',
    },
    })
    chart_totalsales.set_size({'width': 425, 'height': 250})
    chart_totalsales.set_x_axis({'num_font': {'size': 8, 'bold': False}})
    chart_totalsales.set_legend({'font' : {'size' : 8}})
    chart_totalsales.set_y_axis({'min':60})
    chart_totalsales.show_hidden_data()
    worksheet_graph.insert_chart('E2',chart_totalsales,{'x_offset': 1})

    chart_total_sales_excWinS = workbook.add_chart({'type' : 'line'})
    chart_total_sales_excWinS.add_series({
    'name' :     "Objective",
    'categories': '=\'Graphs\'!$AX$3:$AX$14',
    'values':     '=\'Graphs\'!$BA$3:$BA$14',
    'data_labels': {'value': False},
    'line' : {'color':'#4F6228','dash_type': 'dash_dot','width':2},
    })
    chart_total_sales_excWinS.add_series({
    'name' :     str(int(Current_date.year)-2),
    'categories': '=\'Graphs\'!$AX$3:$AX$14',
    'values':     '=\'Graphs\'!$AZ$3:$AZ$14',
    'data_labels': {'value': False},
    'line' : {'color':'#DCE6F2'},
    })
    chart_total_sales_excWinS.add_series({
    'name' :     str(int(Current_date.year)-1),
    'categories': '=\'Graphs\'!$AX$15:$AX$26',
    'values':     '=\'Graphs\'!$AZ$15:$AZ$26',
    'data_labels': {'value': False},
    'line' : {'color':'#558ED5'},
    })
    chart_total_sales_excWinS.add_series({
    'name' :     str(Current_date.year),
    'categories': '=\'Graphs\'!$AY$27:$AY$%s'%(27+int(Current_date.month)-1),
    'values':     '=\'Graphs\'!$AZ$27:$AZ$%s'%(27+int(Current_date.month)-1),
    'data_labels': {'value': False},
    'line' : {'color':'#254061'},
    'marker': {'type': 'diamond','fill':   {'color': '#254061'}},
    })
    chart_total_sales_excWinS.set_title({
    'name': 'Total Sales (Bot/Day) exc. WinS',
    'name_font': {
        'name': 'Calibri',
        'size': 12,
        'color': 'black',
    },
    })
    chart_total_sales_excWinS.set_size({'width': 425, 'height': 250})
    chart_total_sales_excWinS.set_x_axis({'num_font': {'size': 8, 'bold': False}})
    chart_total_sales_excWinS.set_legend({'font' : {'size' : 8}})
    chart_total_sales_excWinS.set_y_axis({'min':40})
    chart_total_sales_excWinS.show_hidden_data()
    worksheet_graph.insert_chart('L2',chart_total_sales_excWinS,{'x_offset': 1})



    for k in range(len(Platform)):
        worksheet_graph.merge_range(0,50+4*(k+1),0,52+4*(k+1),Platform[k][0])
        worksheet_graph.write(1,50+4*(k+1),"Month")
        worksheet_graph.write(1,51+4*(k+1),"Total Sales (Bot/day)")
        worksheet_graph.write(1,52+4*(k+1),"Total Sales exc. WinS (Bot/day)")
        Total_Sales = con.execute("SELECT AVG((Total_Sales-Bottle_Sales)/(CASE WHEN Number_Open_Days>20 THEN DAYOFMONTH(LAST_DAY(Month)) ELSE Number_Open_Days END)), AVG((Total_Sales-Bottle_Sales-WiS_Sales)/(CASE WHEN Number_Open_Days>20 THEN DAYOFMONTH(LAST_DAY(Month)) ELSE Number_Open_Days END)),Month FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Old_Platform = %s AND Month <= %s AND Month >= %s GROUP BY Month ORDER BY Month",Platform[k][0],Current_date,Date_N_2_janv).fetchall()
        Total_Objective = con.execute("""SELECT AVG(PrevisionsSalesTot/DAYOFMONTH(LAST_DAY(Month))),Month FROM PrevisionsSales
                                        INNER JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site WHERE Old_Platform = %s AND
                                        Month <= %s AND Month >= %s AND PrevisionsSalesTot > 0 GROUP BY Month ORDER BY Month""",Platform[k][0],date(Current_date.year,12,1),date(Current_date.year,1,1)).fetchall()   
    
        for i in range(len(Total_Sales)):

            worksheet_graph.write(i+2,50+4*(k+1),Total_Sales[i][2].month)
            worksheet_graph.write(i+2,51+4*(k+1),Total_Sales[i][0],Number_format)
            worksheet_graph.write(i+2,52+4*(k+1),Total_Sales[i][1],Number_format)
        for j in range(len(Total_Objective)):
            worksheet_graph.write(j+2,53+4*(k+1),Total_Objective[j][0],Number_format)


        chart_botdayplat = workbook.add_chart({'type' : 'line'})
        chart_botdayplat.add_series({
        'name' :    'National Sales %s'%(str(Current_date.year)),
        'categories': '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1))),
        'values':     '=\'Graphs\'!$BA$27:$BA$%s'%(27+int(Current_date.month)-1),
        'data_labels': {'value': False},
        'marker': {'type': 'diamond','fill':   {'color': '#FF0000'}},
        'line' : {'color':'#FF0000','dash_type': 'dash_dot','width':2},
        })
        chart_botdayplat.add_series({
        'name' :     'Sales %s'%(int(Current_date.year)-2),
        'categories': '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1))),
        'values':     '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(51+4*(k+1)),xl_col_to_name(51+4*(k+1))),
        'data_labels': {'value': False},
        'line' : {'color':'#DCE6F2'},
        })
        chart_botdayplat.add_series({
        'name' :     'Sales %s'%(int(Current_date.year)-1),
        'categories': '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1))),
        'values':     '=\'Graphs\'!$%s$15:$%s$26'%(xl_col_to_name(51+4*(k+1)),xl_col_to_name(51+4*(k+1))),
        'data_labels': {'value': False},
        'line' : {'color':'#558ED5'},
        })
        chart_botdayplat.add_series({
        'name' :     'Sales %s'%(int(Current_date.year)),
        'categories': '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1))),
        'values':     '=\'Graphs\'!$%s$27:$%s$%s'%(xl_col_to_name(51+4*(k+1)),xl_col_to_name(51+4*(k+1)),27+int(Current_date.month)-1),
        'data_labels': {'value': False},
        'marker':  {'type': 'diamond','fill':   {'color': '#254061'}},
        'line' : {'color':'#254061'},
        })
        chart_botdayplat.set_title({
        'name': 'Sales %s (Bot/day)'%(Platform[k][0]),
        'name_font': {
            'name': 'Calibri',
            'size': 12,
            'color': 'black',
        },
        })
        chart_botdayplat.set_size({'width': 425, 'height': 250})
        chart_botdayplat.set_x_axis({'num_font': {'size': 8, 'bold': False}})
        chart_botdayplat.set_legend({'font' : {'size' : 8}})
        chart_botdayplat.show_hidden_data()
        chart_botdayplat.set_y_axis({'min':60})
        worksheet_graph.insert_chart('%s28'%(xl_col_to_name(7*k)),chart_botdayplat,{'x_offset': 1})

        chart_botdayplat_excWinS = workbook.add_chart({'type' : 'line'})
        chart_botdayplat_excWinS.add_series({
        'name' :     "Objective",
        'categories': '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1))),
        'values':     '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(53+4*(k+1)),xl_col_to_name(53+4*(k+1))),
        'data_labels': {'value': False},
        'line' : {'color':'#4F6228','dash_type': 'dash_dot','width':2},
        })
        chart_botdayplat_excWinS.add_series({
        'name' :    'National Sales %s'%(str(Current_date.year)),
        'categories': '=\'Graphs\'!$%s$27:$%s$%s'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1)),27+int(Current_date.month)-1),
        'values':     '=\'Graphs\'!$AZ$27:$AZ$%s'%(27+int(Current_date.month)-1),
        'data_labels': {'value': False},
        'marker': {'type': 'diamond','fill':   {'color': '#254061'}},
        'line' : {'color':'#FF0000','dash_type': 'dash_dot','width':2},
        })
        chart_botdayplat_excWinS.add_series({
        'name' :     'Sales %s'%(int(Current_date.year)-2),
        'categories': '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1))),
        'values':     '=\'Graphs\'!$%s$3:$%s$14'%(xl_col_to_name(52+4*(k+1)),xl_col_to_name(52+4*(k+1))),
        'data_labels': {'value': False},
        'line' : {'color':'#DCE6F2'},
        })
        chart_botdayplat_excWinS.add_series({
        'name' :     'Sales %s'%(int(Current_date.year)-1),
        'categories': '=\'Graphs\'!$%s$15:$%s$26'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1))),
        'values':     '=\'Graphs\'!$%s$15:$%s$26'%(xl_col_to_name(52+4*(k+1)),xl_col_to_name(52+4*(k+1))),
        'data_labels': {'value': False},
        'line' : {'color':'#558ED5'},
        })
        chart_botdayplat_excWinS.add_series({
        'name' :     'Sales %s'%(int(Current_date.year)),
        'categories': '=\'Graphs\'!$%s$27:$%s$%s'%(xl_col_to_name(50+4*(k+1)),xl_col_to_name(50+4*(k+1)),27+int(Current_date.month)-1),
        'values':     '=\'Graphs\'!$%s$27:$%s$%s'%(xl_col_to_name(52+4*(k+1)),xl_col_to_name(52+4*(k+1)),27+int(Current_date.month)-1),
        'data_labels': {'value': False},
        'marker': {'type': 'diamond','fill':   {'color': '#254061'}},
        'line' : {'color':'#254061'},
        })
        chart_botdayplat_excWinS.set_title({
        'name': 'Sales %s (Bot/day) exc. WinS'%(Platform[k][0]),
        'name_font': {
            'name': 'Calibri',
            'size': 12,
            'color': 'black',
        },
        })
        chart_botdayplat_excWinS.set_size({'width': 425, 'height': 250})
        chart_botdayplat_excWinS.set_x_axis({'num_font': {'size': 8, 'bold': False}})
        chart_botdayplat_excWinS.set_legend({'font' : {'size' : 8}})
        chart_botdayplat_excWinS.show_hidden_data()
        chart_botdayplat_excWinS.set_y_axis({'min':40})
        worksheet_graph.insert_chart('%s15'%(xl_col_to_name(7*k)),chart_botdayplat_excWinS,{'x_offset': 1})

        
    worksheet_graph.set_column("AY:CC",None,None,{'level':1,'hidden':True})
    worksheet_graph.set_zoom(60)

################## GRAPH ADVISOR ##########################
    Advisor = con.execute("SELECT DISTINCT Advisor,Platform FROM Sites WHERE Advisor <> %s AND Platform IN %s AND Advisor <> 'Stop' AND Advisor <> ''",'',ListPlatform).fetchall()
    Date_last_janv = date(int(Current_date.year)-2,12,1)
    ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Old_Platform IN %s 
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(date(Current_date.year-1,1,1),ListPlatform)).fetchall()
    ListSite_LikeforLike = [i[0] for i in ListSite_LikeforLike]

    allSales_year_likeforlike = con.execute("""SELECT SUM(Total_Sales - Bottle_Sales - WiS_Sales),Advisor,YEAR(Month),Platform FROM Sales 
                                                JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month >=%s AND 
                                                Sales.Id_Site IN %s GROUP BY Advisor,YEAR(Month),Platform""",(date(Current_date.year,1,1),ListSite_LikeforLike)).fetchall()
    
    allSales_year_other = con.execute("SELECT SUM(Total_Sales - Bottle_Sales - WiS_Sales),Advisor,YEAR(Month),Platform FROM Sales JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month >=%s AND Sales.Id_Site NOT IN %s GROUP BY Advisor,YEAR(Month),Platform",(date(Current_date.year,1,1),ListSite_LikeforLike)).fetchall()
    allSales_lastyear =  con.execute("SELECT SUM(Total_Sales - Bottle_Sales - WiS_Sales),Advisor,YEAR(Month),Platform FROM Sales JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month >=%s AND Month <= %s GROUP BY Advisor,YEAR(Month),Platform",(date(int(Current_date.year)-1,1,1),date(int(Current_date.year)-1,Current_date.month,1))).fetchall()
    
    allObjectives_year_likeforlike = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor,YEAR(Month),Platform FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month >= %s AND Month <= %s AND Advisor IS NOT NULL AND PrevisionsSales.Id_Site IN %s 
                                            GROUP BY Advisor,YEAR(Month),Platform""",(date(Current_date.year,1,1),Current_date,ListSite_LikeforLike)).fetchall()
    allObjectives_year_other = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor,YEAR(Month),Platform FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month >= %s AND Month <= %s AND Advisor IS NOT NULL AND PrevisionsSales.Id_Site NOT IN %s 
                                            GROUP BY Advisor,YEAR(Month),Platform""",(date(Current_date.year,1,1),Current_date,ListSite_LikeforLike)).fetchall()

    allSales_month_likeforlike = con.execute("SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month <=%s AND Month > %s AND Sales.Id_Site IN %s GROUP BY Advisor,Month",(Current_date,date(Current_date.year-2,12,1),ListSite_LikeforLike)).fetchall()
    allSales_month_other = con.execute("SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month <=%s AND Month > %s AND Sales.Id_Site NOT IN %s GROUP BY Advisor,Month",(Current_date,date(Current_date.year-2,12,1),ListSite_LikeforLike)).fetchall()
    allSales_month_last_year = con.execute("SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month <=%s AND Month > %s GROUP BY Advisor,Month",(Current_date,date(Current_date.year-2,12,1))).fetchall()
    
    allObjectives_month_likeforlike = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month > %s AND PrevisionsSales.Id_Site IN %s 
                                            GROUP BY Advisor,Month""",(Current_date,date(Current_date.year-1,12,1),ListSite_LikeforLike)).fetchall()
    allObjectives_month_other = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month > %s AND PrevisionsSales.Id_Site NOT IN %s 
                                            GROUP BY Advisor,Month""",(Current_date,date(Current_date.year-1,12,1),ListSite_LikeforLike)).fetchall()
    if 1==1:
        worksheet_graphadvisor = workbook.add_worksheet("Graph Advisor")
        worksheet_graphadvisor.set_column("Y:IZ",None,None,{'level':1,'hidden':True})

        Line = 0
        for k in range(len(ListPlatform)):
            Advisor_plat = list(filter(lambda row: row[1] == ListPlatform[k], Advisor))
            worksheet_graphadvisor.write(4*Line+2,24,ListPlatform[k])
            for i in range(len(Advisor_plat)):
                Sales_YTD_likeforlike_Platform = list(filter(lambda row: row[1] == Advisor_plat[i][0], allSales_year_likeforlike)) or [(0,0,0,0)]
                Sales_YTD_other_Platform = list(filter(lambda row: row[1] == Advisor_plat[i][0], allSales_year_other)) or [(0,0,0,0)]
                Sales_lastYTD_Platform = list(filter(lambda row: row[1] == Advisor_plat[i][0], allSales_lastyear)) or [(0,0,0,0)]

                Sales_YTD_likeforlike = list(filter(lambda row: row[3] == Advisor_plat[i][1], Sales_YTD_likeforlike_Platform)) or [(0,0,0)]
                Sales_YTD_other = list(filter(lambda row: row[3] == Advisor_plat[i][1], Sales_YTD_other_Platform)) or [(0,0,0)]
                Sales_lastYTD = list(filter(lambda row: row[3] == Advisor_plat[i][1], Sales_lastYTD_Platform)) or [(0,0,0)]

                Objective_like_for_like_Platform = list(filter(lambda row: row[1] == Advisor_plat[i][0], allObjectives_year_likeforlike)) or [(0,0,0,0)]
                Objective_other_Platform = list(filter(lambda row: row[1] == Advisor_plat[i][0], allObjectives_year_other)) or [(0,0,0,0)]

                Objective_likeforlike = list(filter(lambda row: row[3] == Advisor_plat[i][1], Objective_like_for_like_Platform)) or [(0,0,0)]
                Objective_other = list(filter(lambda row: row[3] == Advisor_plat[i][1], Objective_other_Platform)) or [(0,0,0)]

                worksheet_graphadvisor.write(4*(Line+i)+3,25,Advisor_plat[i][0])
                worksheet_graphadvisor.write(4*(Line+i)+2,26,Sales_YTD_likeforlike[0][0],Number_format)
                worksheet_graphadvisor.write(4*(Line+i)+2,27,Sales_YTD_other[0][0],Number_format)
                worksheet_graphadvisor.write(4*(Line+i)+3,28,Objective_likeforlike[0][0],Number_format)
                worksheet_graphadvisor.write(4*(Line+i)+3,29,Objective_other[0][0],Number_format)
                worksheet_graphadvisor.write(4*(Line+i)+4,30,Sales_lastYTD[0][0],Number_format)


            chart_sales_allplat = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
            chart_sales_allplat.add_series({
            'name' :     '%s'%(Current_date.year-1),
            'categories': '=\'Graph Advisor\'!$Z$%s:$Z$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'values':     '=\'Graph Advisor\'!$AE$%s:$AE$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'data_labels': {'value': False},
            })
            chart_sales_allplat.add_series({
            'name' :     'Objective Like for Like',
            'categories': '=\'Graph Advisor\'!$Z$%s:$Z$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'values':     '=\'Graph Advisor\'!$AC$%s:$AC$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'data_labels': {'value': False},
            })
            chart_sales_allplat.add_series({
            'name' :     'Objective Other',
            'categories': '=\'Graph Advisor\'!$Z$%s:$Z$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'values':     '=\'Graph Advisor\'!$AD$%s:$AD$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'data_labels': {'value': False},
            })
            
            chart_sales_allplat.add_series({
            'name' :     '%s like for like'%(Current_date.year),
            'categories': '=\'Graph Advisor\'!$Z$%s:$Z$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'values':     '=\'Graph Advisor\'!$AA$%s:$AA$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'data_labels': {'value': False},
            'gap' : 0,
            })
            chart_sales_allplat.add_series({
            'name' :     '%s other'%(Current_date.year),
            'categories': '=\'Graph Advisor\'!$Z$%s:$Z$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'values':     '=\'Graph Advisor\'!$AB$%s:$AB$%s'%(4*Line+3,4*(Line+len(Advisor_plat))+2),
            'data_labels': {'value': False},
            })
            
            chart_sales_allplat.set_title({
            'name': 'Total Bottles sold per Advisor YTD %s' %(ListPlatform[k]),
            'name_font': {
                'name': 'Calibri',
                'size': 12,
                'color': 'black',
            },
            })
            chart_sales_allplat.set_size({'width': 1300, 'height': 350})
            chart_sales_allplat.set_x_axis({'num_font': {'size': 8, 'bold': False}})
            chart_sales_allplat.set_legend({'font' : {'size' : 8}})
            chart_sales_allplat.show_hidden_data()
            chart_sales_allplat.set_table({'vertical':False})
            worksheet_graphadvisor.insert_chart('A%s'%(24+18*k),chart_sales_allplat)
            Line += len(Advisor_plat)

    start_date = date(Current_date.year-2,12,1)
    worksheet_graphadvisor.set_zoom(70)
    worksheet_graphadvisor.write(0,39,"Month")
    for i in range(len(Advisor)):
        Sales_date_likeforlike = list(filter(lambda row: row[1] == Advisor[i][0], allSales_month_likeforlike)) or [(0,0,0)]
        Sales_date_other = list(filter(lambda row: row[1] == Advisor[i][0], allSales_month_other)) or [(0,0,0)]
        Sales_date_lastyear = list(filter(lambda row: row[1] == Advisor[i][0], allSales_month_last_year)) or [(0,0,0)]
        Objectives_date_likeforlike = list(filter(lambda row: row[1] == Advisor[i][0], allObjectives_month_likeforlike)) or [(0,0,0)]
        Objectives_date_other = list(filter(lambda row: row[1] == Advisor[i][0], allObjectives_month_other)) or [(0,0,0)]

        worksheet_graphadvisor.write(i+1,32,Advisor[i][0])
        for k in range(1,13):
            Sales_likeforlike_thismonth = list(filter(lambda row: row[2] == str(date(Current_date.year,k,1)), Sales_date_likeforlike)) or [(0,0,0)]
            Sales_other_thismonth = list(filter(lambda row: row[2] == str(date(Current_date.year,k,1)), Sales_date_other)) or [(0,0,0)]
            Sales_lastyear = list(filter(lambda row: row[2] == str(date(int(Current_date.year)-1,k,1)), Sales_date_lastyear)) or [(0,0,0)]
            Objectives_likeforlike_thismonth = list(filter(lambda row: row[2] == str(date(Current_date.year,k,1)), Objectives_date_likeforlike)) or [(0,0,0)]
            Objectives_other_thismonth = list(filter(lambda row: row[2] == str(date(Current_date.year,k,1)), Objectives_date_other)) or [(0,0,0)]
            
            worksheet_graphadvisor.write(0,39+5*i,Advisor[i][0]+'-'+str(Current_date.year)+'-LfL')
            worksheet_graphadvisor.write(0,39+5*i+1,Advisor[i][0]+'-'+str(Current_date.year)+'-Other')
            worksheet_graphadvisor.write(0,39+5*i+2,Advisor[i][0]+'-'+'Objective-LfL')
            worksheet_graphadvisor.write(0,39+5*i+3,Advisor[i][0]+'-'+'Objective-Other')
            worksheet_graphadvisor.write(0,39+5*i+4,Advisor[i][0]+'-'+str(int(Current_date.year)-1))

            worksheet_graphadvisor.write(4*k-2,39+5*i,Sales_likeforlike_thismonth[0][0])
            worksheet_graphadvisor.write(4*k-2,39+5*i+1,Sales_other_thismonth[0][0])
            worksheet_graphadvisor.write(4*k-1,39+5*i+2,Objectives_likeforlike_thismonth[0][0])
            worksheet_graphadvisor.write(4*k-1,39+5*i+3,Objectives_other_thismonth[0][0])
            worksheet_graphadvisor.write(4*k,39+5*i+4,Sales_lastyear[0][0])


        worksheet_graphadvisor.data_validation('A1',{'validate' : 'list',
                                    'source' : "AG2:AG%s"%(len(Advisor)+2)})
    worksheet_graphadvisor.write_formula("A1","=AG2")
    for k in range(1,13):
        worksheet_graphadvisor.write(4*k-2,38,k)
        worksheet_graphadvisor.write_formula(4*k-2,33,"=INDEX(AI%s:%s%s,MATCH(CONCATENATE(A1,\"-\",%s,\"-LfL\"),AI1:%s1,0))"%(4*k-1,xl_col_to_name(len(Advisor)*5+39),4*k-1,str(Current_date.year),xl_col_to_name(len(Advisor)*5+39)))
        worksheet_graphadvisor.write_formula(4*k-2,34,"=INDEX(AI%s:%s%s,MATCH(CONCATENATE(A1,\"-\",%s,\"-Other\"),AI1:%s1,0))"%(4*k-1,xl_col_to_name(len(Advisor)*5+39),4*k-1,str(Current_date.year),xl_col_to_name(len(Advisor)*5+39)))
        worksheet_graphadvisor.write_formula(4*k-1,35,"=INDEX(AI%s:%s%s,MATCH(CONCATENATE(A1,\"-Objective-LfL\"),AI1:%s1,0))"%(4*k,xl_col_to_name(len(Advisor)*5+39),4*k,xl_col_to_name(len(Advisor)*5+39)))
        worksheet_graphadvisor.write_formula(4*k-1,36,"=INDEX(AI%s:%s%s,MATCH(CONCATENATE(A1,\"-Objective-Other\"),AI1:%s1,0))"%(4*k,xl_col_to_name(len(Advisor)*5+39),4*k,xl_col_to_name(len(Advisor)*5+39)))
        worksheet_graphadvisor.write_formula(4*k,37,"=INDEX(AI%s:%s%s,MATCH(CONCATENATE(A1,\"-\",%s),AI1:%s1,0))"%(4*k+1,xl_col_to_name(len(Advisor)*5+39),4*k+1,str(int(Current_date.year)-1),xl_col_to_name(len(Advisor)*5+39)))

    chart_sales_advisor = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
    chart_sales_advisor.add_series({
    'name' :     '%s'%(Current_date.year-1),
    'categories': '=\'Graph Advisor\'!$AM$3:$AM$37',
    'values':     '=\'Graph Advisor\'!$AL$3:$AL$37',
    'data_labels': {'value': False},
    })
    chart_sales_advisor.add_series({
    'name' :     'Objective Like for Like',
    'categories': '=\'Graph Advisor\'!$AM$3:$AM$37',
    'values':     '=\'Graph Advisor\'!$AJ$3:$AJ$37',
    'data_labels': {'value': False},
    })
    chart_sales_advisor.add_series({
    'name' :     'Objective Other',
    'categories': '=\'Graph Advisor\'!$AM$3:$AM$37',
    'values':     '=\'Graph Advisor\'!$AK$3:$AK$37',
    'data_labels': {'value': False},
    })
    chart_sales_advisor.add_series({
    'name' :     '%s Like for Like'%(Current_date.year),
    'categories': '=\'Graph Advisor\'!$AM$3:$AM$37',
    'values':     '=\'Graph Advisor\'!$AH$3:$AH$37',
    'data_labels': {'value': False},
    'gap' : 0,
    })
    chart_sales_advisor.add_series({
    'name' :     '%s Other'%(Current_date.year),
    'categories': '=\'Graph Advisor\'!$AM$3:$AM$37',
    'values':     '=\'Graph Advisor\'!$AI$3:$AI$37',
    'data_labels': {'value': False},
    })
    
    
    
    chart_sales_advisor.set_title({
    'name': 'Total Bot sold this year',
    'name_font': {
        'name': 'Calibri',
        'size': 12,
        'color': 'black',
    },
    })

    chart_sales_advisor.set_size({'width': 1400, 'height': 400})
    chart_sales_advisor.set_x_axis({'num_font': {'size': 8, 'bold': False}})
    chart_sales_advisor.set_legend({'font' : {'size' : 8}})
    chart_sales_advisor.show_hidden_data()
    chart_sales_advisor.set_table({'vertical':False})
    worksheet_graphadvisor.insert_chart('A3',chart_sales_advisor)

def GraphF2F(workbook,Current_date,ListPlatform):
    Name_worksheet="Graph"
    worksheet = workbook.add_worksheet(Name_worksheet)
    worksheet.set_zoom(70)
    ListPlatform.append("Total")
    Graph.GraphBotDay(workbook,worksheet,Name_worksheet,0,10,0,35,Current_date,ListPlatform,False)
    Graph.GraphBotDay(workbook,worksheet,Name_worksheet,0,17,3,35,Current_date,ListPlatform,True)
    Graph.GraphMonthlyPlatform(workbook,worksheet,Name_worksheet,28,10,3*(len(ListPlatform)+1),35,Current_date,ListPlatform)
    for i in range(len(ListPlatform)-1):
        Graph.GraphBotDay(workbook,worksheet,Name_worksheet,14,7*i,3*(i+2),35,Current_date,[ListPlatform[i]],False)
        Graph.GraphMonthlyPlatform(workbook,worksheet,Name_worksheet,42,7*i,3*(len(ListPlatform)+1),35+6*(i+1),Current_date,[ListPlatform[i]])

def GraphAdvisor(workbook,Current_date,ListPlatform):
    Name_worksheet="Graphs Advisor"
    worksheet = workbook.add_worksheet(Name_worksheet)
    worksheet.set_zoom(55)
    Graph.GraphMonthlyAdvisor(workbook,worksheet,Name_worksheet,1,1,1,45,0,0,Current_date)
    for i in range(len(ListPlatform)):
        Graph.GraphAdvisorperPlatform(workbook,worksheet,Name_worksheet,22+22*i,1,45,45+i*6,Current_date,[ListPlatform[i]])

def Objective(workbook,Current_date,Date_janv):
    con = db.pool.connect()
    name_format = workbook.add_format({'bold':True,'border':1})
    number_format = workbook.add_format({'num_format':'# ##0','border':1})
    percentage_format = workbook.add_format({'num_format':'0%','border':1})

    worksheet = workbook.add_worksheet("Objectives")
    allObjectivesAdvisor = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor FROM PrevisionsSales 
                            JOIN Sites ON PrevisionsSales.Id_Site = Sites.Id_Site
                            WHERE Month <= %s AND Month > %s 
                            GROUP BY Advisor""",(Current_date,Date_janv)).fetchall()

    allSalesAdvisor = con.execute("""SELECT SUM(Total_Sales-WiS_Sales-Bottle_Sales),Advisor FROM Sales
                            JOIN Sites ON Sales.Id_Site = Sites.Id_Site
                            WHERE Month <= %s AND Month > %s AND Advisor <> 'jonathan' AND Advisor <> 'Stop'
                            GROUP BY Advisor""",(Current_date,Date_janv)).fetchall()

    allObjectivesPlatform = con.execute("""SELECT SUM(PrevisionsSalesTot),Platform FROM PrevisionsSales 
                            JOIN Sites ON PrevisionsSales.Id_Site = Sites.Id_Site
                            WHERE Month <= %s AND Month > %s
                            GROUP BY Platform""",(Current_date,Date_janv)).fetchall()

    allSalesPlatform = con.execute("""SELECT SUM(Total_Sales-WiS_Sales-Bottle_Sales),Platform FROM Sales
                            JOIN Sites ON Sales.Id_Site = Sites.Id_Site
                            WHERE Month <= %s AND Month > %s
                            GROUP BY Platform""",(Current_date,Date_janv)).fetchall()

    Advisor = con.execute("""SELECT DISTINCT Advisor,Platform FROM Sites WHERE Advisor <> 'jonathan' AND Advisor <> 'Stop'""").fetchall()

    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead'""").fetchall()

    worksheet.set_column('A:J',15)
    worksheet.freeze_panes('B2')
    ColumnTitle=0
    worksheet.write(0,ColumnTitle,"Advisor",name_format)
    ColumnTitle+=1
    worksheet.write(0,ColumnTitle,"Platform",name_format)
    ColumnTitle+=1
    worksheet.write(0,ColumnTitle,"Objective",name_format)
    ColumnTitle+=1
    worksheet.write(0,ColumnTitle,"Sales",name_format)
    ColumnTitle+=1
    worksheet.write(0,ColumnTitle,"% achieved",name_format)
    ColumnTitle+=1
    ColumnTitle+=1
    for i in range(len(Advisor)):
        Column =0
        Objective = list(filter(lambda row: row[1] == Advisor[i][0], allObjectivesAdvisor)) or [(0,"","")]
        Sales = list(filter(lambda row: row[1] == Advisor[i][0], allSalesAdvisor)) or [(0,"","")]
        worksheet.write(i+1,Column,Advisor[i][0],name_format)
        Column+=1
        worksheet.write(i+1,Column,Advisor[i][1],name_format)
        Column+=1
        worksheet.write(i+1,Column,Objective[0][0],number_format)
        Column+=1
        worksheet.write(i+1,Column,Sales[0][0],number_format)
        Column+=1
        worksheet.write_formula(i+1,Column,"=IFERROR(%s/%s,\"\")"%(Sales[0][0],Objective[0][0]),percentage_format)
        Column+=1
    ColumnPlatform = Column +1
    worksheet.write(0,ColumnTitle,"Platform",name_format)
    ColumnTitle+=1
    worksheet.write(0,ColumnTitle,"Objective",name_format)
    ColumnTitle+=1
    worksheet.write(0,ColumnTitle,"Sales",name_format)
    ColumnTitle+=1
    worksheet.write(0,ColumnTitle,"% achieved",name_format)
    ColumnTitle+=1
    for i in range(len(Platform)):
        Column = ColumnPlatform
        Objective = list(filter(lambda row: row[1] == Platform[i][0], allObjectivesPlatform)) or [(0,"","")]
        Sales = list(filter(lambda row: row[1] == Platform[i][0], allSalesPlatform)) or [(0,"","")]
        worksheet.write(i+1,Column,Platform[i][0],name_format)
        Column+=1
        worksheet.write(i+1,Column,Objective[0][0],number_format)
        Column+=1
        worksheet.write(i+1,Column,Sales[0][0],number_format)
        Column+=1
        worksheet.write_formula(i+1,Column,"=IFERROR(%s/%s,\"\")"%(Sales[0][0],Objective[0][0]),percentage_format)
   
def InstructionTab(workbook,Current_date,Date_1):
    worksheet_instruction = workbook.add_worksheet("Instruction")
    worksheet_instruction.set_zoom(70)
    Title1_format = workbook.add_format({'font_size':15,'bold':True})
    Title2_format = workbook.add_format({'bold':True})
    Comment_format = workbook.add_format({'italic':True})
    worksheet_instruction.write(0,0,"Tier Rules",Title1_format)
    worksheet_instruction.write(1,0,"Dead :",Title2_format)
    worksheet_instruction.write(1,1,"closed site that will never reopen")
    worksheet_instruction.write(2,0,"Closed :",Title2_format)
    worksheet_instruction.write(2,1,"site closed for more than 12 months that might reopen")
    worksheet_instruction.write(3,0,"Inactive :",Title2_format)
    worksheet_instruction.write(3,1,"site closed for one month or more (but less than 12)")
    worksheet_instruction.write(4,0,"New :",Title2_format)
    worksheet_instruction.write(4,1,"site previously closed or inactive but has been reopened since less than 3 months")
    worksheet_instruction.write(5,0,"Reopen :",Title2_format)
    worksheet_instruction.write(5,1,"site that have been opened for less than 3 months")
    worksheet_instruction.write(6,0,"The rest : ",Title2_format)
    worksheet_instruction.write(7,0,"ST1 :",Title2_format)
    worksheet_instruction.write(7,1,"> 110 Bot/day exc. WinS")
    worksheet_instruction.write(8,0,"1 :",Title2_format)
    worksheet_instruction.write(8,1,"> 70 Bot/day exc. WinS")
    worksheet_instruction.write(9,0,"2 :",Title2_format)
    worksheet_instruction.write(9,1,"> 45 Bot/day exc. WinS")
    worksheet_instruction.write(10,0,"3 :",Title2_format)
    worksheet_instruction.write(10,1,"> 0 Bot/day exc. WinS")
    worksheet_instruction.write(12,0,"Like for like Rule",Title1_format)
    worksheet_instruction.write(13,0,"Like for like : sites that were opened in January %s "%(int(Current_date.year)-1))
    worksheet_instruction.write(14,0,"'=> The idea is to not count the new site opened to have a good understanding of the performance of our current kiosk without taking into account the most recent opening batch",Comment_format)
    worksheet_instruction.write(15,0,"YTD Rule",Title1_format)
    worksheet_instruction.write(16,0,"YTD means all the data from Jan to %s"%(calendar.month_name[Current_date.month]))

def LaunchExcelCreationF2F(Current_date, ListTier,Platform,exchange_rate):
    con = db.pool.connect()
    Date_N_1 = Current_date- relativedelta(months=+12)
    Date_janv = date(Current_date.year-1,12,1)
    Date_last_janv = date(Current_date.year-2,12,1)
    Platform_List = con.execute("SELECT DISTINCT Code_Platform FROM Platform").fetchall()
    AllPlatform = [i[0] for i in Platform_List]
    ListSiteActive = listSiteStillActive(Current_date,Date_N_1)
    CreateF2FROM(Current_date,Platform)
    WriteF2FYTD(Platform,Current_date,ListTier,exchange_rate)
    WriteKPIF2F(Current_date,Date_janv,exchange_rate)
    ExcelKPI.IndicatorsTeukSaat(workbook,Current_date,Date_N_1,Date_janv,Date_last_janv)
    GraphAdvisor(workbook,Current_date,AllPlatform)
    GraphF2F(workbook,Current_date,AllPlatform)
    Objective(workbook,Current_date,Date_janv)
    SiteAnalysis(ListTier,ListSiteActive,workbook,Current_date,True)
    InstructionTab(workbook,Current_date,Date_janv)
    workbook.close()


if __name__ == '__main__':
    Current_date = date(2022,8,1)
    ListDate = listDate(Current_date)
    Date_N_1 = Current_date- relativedelta(months=+12)
    Date_N_2 = Current_date- relativedelta(months=+24)
    exchange_rate = 4068
    ListSiteActive = listSiteStillActive(Current_date,Date_N_1)
    Opened_month = CalculNombreMoisOuverture(Current_date,Date_N_1,ListSiteActive)
    Opened_month_last_year = CalculNombreMoisOuverture(Date_N_1,Date_N_2,ListSiteActive)

    ListOpenDayThisYear = Numberdaysopeningyear(Current_date,Date_N_1,ListSiteActive,Opened_month)
    ListOpenDayLastYear = Numberdaysopeningyear(Date_N_1,Date_N_2,ListSiteActive,Opened_month_last_year)

    ListTierThisYear = CalculTier(Current_date,Date_N_1,Opened_month,ListSiteActive,ListOpenDayThisYear)
    ListTierLastYear = CalculTier(Date_N_1,Date_N_2,Opened_month_last_year,ListSiteActive,ListOpenDayLastYear)

    ListProvPlat = listProvPlat(ListSiteActive)
    ListPlatform = ListProvPlat[0]
    Platform = ["SR","PP","BTB","KSP","KC"]
    LaunchExcelCreationF2F(ListDate, ListSiteActive, ListTierThisYear,ListTierLastYear,Opened_month,ListOpenDayThisYear,ListProvPlat,Platform,exchange_rate)
