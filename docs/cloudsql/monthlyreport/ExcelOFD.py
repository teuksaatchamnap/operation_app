from ast import List
import xlsxwriter
from datetime import date
from xlsxwriter.utility import xl_col_to_name,xl_rowcol_to_cell
import db
import tempfile
from dateutil.relativedelta import *
import monthlyreport.ExcelKPI as ExcelKPI
import monthlyreport.ExcelF2F as ExcelF2F
from monthlyreport.ExcelSiteAnalysis import SiteAnalysis
import monthlyreport.Graph as Graph
from monthlyreport.Functionutils import exchange_rate_year, CategoryExpenses,NewCalculTier,ConsumableForOFD, listSiteStillActive

con = db.pool.connect()
def CreateOFD(Current_date,ListPlatform):
    global workbook
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    if len(ListPlatform) > 1:
         filepath = tempfile.gettempdir()+'/OFD ' + Year + '-' + Month + '.xlsm'
         workbook = xlsxwriter.Workbook(filepath)
    else:
        filepath = tempfile.gettempdir()+'/OFD %s '%(ListPlatform[0]) + Year + '-' + Month + '.xlsm'
        workbook = xlsxwriter.Workbook(filepath)
    print(filepath)

def WriteOFD(Current_date,Date_janv,Date_N_1,Date_last_janv,exchange_rate,ListTier,ListPlatform):

    worksheet_OFD = workbook.add_worksheet("OFD")

    Title_format = workbook.add_format({'bold':True,"font_size":18,"center_across":True,'bg_color':'#FFFF00'})

    Date_format = workbook.add_format({'num_format' : 'dd/mm/yyyy'})
    Site_format = workbook.add_format({'bg_color':"#DAEEF3",'bold': True, 'text_wrap' : True,'valign':'vcenter','center_across':True})
    YTD_Format_One = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    YTD_Format_Two = workbook.add_format({'bg_color':"#538DD5",'bold': True, 'text_wrap' : True,'font_color':'black','valign':'vcenter','center_across':True})
    YTD_Format_Three = workbook.add_format({'bg_color':"#C5D9F1",'bold': True, 'text_wrap' : True,'font_color':'black','valign':'vcenter','center_across':True})
    
    Monthly_Format_One = workbook.add_format({'bg_color':"#76933C",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    Monthly_Format_Two = workbook.add_format({'bg_color':"#C4D79B",'bold': True, 'text_wrap' : True,'font_color':'black','valign':'vcenter','center_across':True})
    
    Debt_format = workbook.add_format({'bg_color':"#DA9694",'bold': True, 'text_wrap' : True,'font_color':'black','valign':'vcenter','center_across':True})
    
    Percentage_format = workbook.add_format({'num_format' : '0%'})
    Percentage_evol_format = workbook.add_format({'num_format' : '+0%;-0%'})
    Number_format = workbook.add_format({'num_format' : '# ##0'})
    Money_format = workbook.add_format({'num_format' : '# ##0 $'})
    Money_evol_format = workbook.add_format({'num_format' : '+# ##0 $;-# ##0 $'})

    Percentage_bold_evol_format = workbook.add_format({'num_format' : '+0%;-0%', 'bold':True})
    Number_bold_format = workbook.add_format({'num_format' : '# ##0', 'bold': True})
    
######### SELECT DATA ###########  
    Category_expenses = CategoryExpenses()
    ListSite_LikeforLike = con.execute("SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites WHERE Sites.Id_Site IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) AND Old_Platform IN %s ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site",Date_last_janv+relativedelta(months=+1),ListPlatform).fetchall()
    ListOnlysiteLikeforLike = [i[0] for i in ListSite_LikeforLike] or [0]
    ListSite_notLikeforLike = con.execute("SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites INNER JOIN Sales ON Sites.Id_Site = Sales.Id_Site WHERE 1 = %s AND Sites.Id_Site NOT IN %s AND Old_Platform IN %s ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site",(1,ListOnlysiteLikeforLike,ListPlatform)).fetchall()

    ListAllSite = ListSite_LikeforLike + ListSite_notLikeforLike

    allSales = con.execute("SELECT Id_Site,SUM(Total_Sales - Bottle_Sales - WiS_Sales),SUM(Total_Sales - Bottle_Sales),SUM(Total_Income - WiS_Income)/%s,SUM(Total_Income)/%s,COUNT(Total_Sales) FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(exchange_rate,exchange_rate,Current_date,Date_janv)).fetchall()
    allSales_lastyear = con.execute("SELECT Id_Site,SUM(Total_Sales - Bottle_Sales - WiS_Sales),SUM(Total_Sales - Bottle_Sales),SUM(Total_Income - WiS_Income)/%s,SUM(Total_Income)/%s,COUNT(Total_Sales) FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",(exchange_rate,exchange_rate,Date_N_1,Date_last_janv)).fetchall()

    allSales_month = con.execute(
        """
        SELECT Id_Site,
               SUM(Total_Sales - Bottle_Sales - WiS_Sales),
               SUM(Total_Sales - Bottle_Sales),
               SUM(Total_Income - WiS_Income) / %s,
               SUM(Total_Income) / %s,
               COUNT(Total_Sales)
        FROM Sales
        WHERE Month = %s
        GROUP BY Id_Site
        """,
        (exchange_rate, exchange_rate, Current_date)
    ).fetchall()

    allSales_month_lastyear = con.execute(
        """
        SELECT Id_Site,
               SUM(Total_Sales - Bottle_Sales - WiS_Sales),
               SUM(Total_Sales - Bottle_Sales),
               SUM(Total_Income - WiS_Income) / %s,
               SUM(Total_Income) / %s,
               COUNT(Total_Sales)
        FROM Sales
        WHERE Month = %s
        GROUP BY Id_Site
        """,
        (exchange_rate, exchange_rate, Date_N_1)
    ).fetchall()

    # Fetch total costs
    allTotal_cost = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        JOIN Sites ON Expenses.Id_Site = Sites.Id_Site 
        WHERE Expenses.Month <= %s AND Expenses.Month > %s 
        AND Category_expenses IN %s 
        GROUP BY Sites.Id_Site
        """, 
        (exchange_rate, Current_date, Date_janv, Category_expenses)
    ).fetchall()

    allTotal_cost_month = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        JOIN Sites ON Expenses.Id_Site = Sites.Id_Site 
        WHERE Expenses.Month = %s
        AND Category_expenses IN %s 
        GROUP BY Sites.Id_Site
        """, 
        (exchange_rate, Current_date, Category_expenses)
    ).fetchall()

    allTotal_cost_lastyear = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        JOIN Sites ON Expenses.Id_Site = Sites.Id_Site 
        WHERE Expenses.Month <= %s AND Expenses.Month > %s 
        AND Category_expenses IN %s 
        GROUP BY Sites.Id_Site
        """, 
        (exchange_rate, Date_N_1, Date_last_janv, Category_expenses)
    ).fetchall()

    allTotal_cost_month_lastyear = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        JOIN Sites ON Expenses.Id_Site = Sites.Id_Site 
        WHERE Expenses.Month = %s
        AND Category_expenses IN %s 
        GROUP BY Sites.Id_Site
        """, 
        (exchange_rate, Date_N_1, Category_expenses)
    ).fetchall()

    allDue_YTD = con.execute(
        """
        SELECT Id_Site, SUM(Amount_Expenses) / %s,Ref_expenses
        FROM Expenses
        WHERE (Ref_expenses = 'stock_ts' 
               OR Ref_expenses = 'bottle_invoice' 
               OR Ref_expenses = 'entrepreneur_contribution' 
               OR Ref_expenses = 'water quality alert' 
               OR Ref_expenses = 'technical intervention' 
               OR Ref_expenses = 'delivery_program_fee'
               OR Ref_expenses = 'WinS_invoice') 
        AND Month > %s AND Month <= %s
        GROUP BY Id_Site,Ref_expenses
        """,
        (exchange_rate, Date_janv, Current_date)
    ).fetchall()

    allDue_Month = con.execute(
        """
        SELECT Id_Site, SUM(Amount_Expenses) / %s,Ref_expenses
        FROM Expenses
        WHERE (Ref_expenses = 'stock_ts' 
               OR Ref_expenses = 'bottle_invoice' 
               OR Ref_expenses = 'entrepreneur_contribution' 
               OR Ref_expenses = 'water quality alert' 
               OR Ref_expenses = 'technical intervention' 
               OR Ref_expenses = 'delivery_program_fee'
               OR Ref_expenses = 'WinS_invoice') 
        AND Month = %s
        GROUP BY Id_Site,Ref_expenses
        """,
        (exchange_rate, Current_date)
    ).fetchall()

    # Fetch salary expenses
    allSalaryEnt = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        WHERE (Ref_expenses = 'variable_salary_entrepreneurs' 
               OR Ref_expenses = 'fix_salary_entrepreneurs' 
               OR Ref_expenses = 's3-bonus') 
        AND Expenses.Month <= %s AND Expenses.Month > %s 
        GROUP BY Id_Site
        """, 
        (exchange_rate, Current_date, Date_janv)
    ).fetchall()

    allSalaryEnt_month = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        WHERE (Ref_expenses = 'variable_salary_entrepreneurs' 
               OR Ref_expenses = 'fix_salary_entrepreneurs') 
        AND Expenses.Month = %s
        GROUP BY Id_Site
        """, 
        (exchange_rate, Current_date)
    ).fetchall()

    allSalaryEnt_lastyear = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        WHERE (Ref_expenses = 'variable_salary_entrepreneurs' 
               OR Ref_expenses = 'fix_salary_entrepreneurs' 
               OR Ref_expenses = 's3-bonus') 
        AND Expenses.Month <= %s AND Expenses.Month > %s 
        GROUP BY Id_Site
        """, 
        (exchange_rate, Date_N_1, Date_last_janv)
    ).fetchall()

    allSalaryEnt_month_lastyear = con.execute(
        """
        SELECT Expenses.Id_Site, SUM(Amount_Expenses) / %s 
        FROM Expenses 
        WHERE (Ref_expenses = 'variable_salary_entrepreneurs' 
               OR Ref_expenses = 'fix_salary_entrepreneurs') 
        AND Expenses.Month = %s
        GROUP BY Id_Site
        """, 
        (exchange_rate, Date_N_1)
    ).fetchall()

    # Fetch collection rates
    allCollectionRate = con.execute(
        """
        SELECT Id_Site, SUM(Amount_Expenses) / %s, IFNULL(SUM(Paid), 0) / %s 
        FROM Expenses 
        WHERE (Ref_expenses = 'stock_ts' 
               OR Ref_expenses = 'bottle_invoice' 
               OR Ref_expenses = 'entrepreneur_contribution' 
               OR Ref_expenses = 'water quality alert' 
               OR Ref_expenses = 'technical intervention' 
               OR Ref_expenses = 'delivery_program_fee')
        AND Month > %s AND Month <= %s 
        GROUP BY Id_Site
        """, 
        (exchange_rate, exchange_rate, Date_janv, Current_date)
    ).fetchall()

    allCollectionRate_month = con.execute(
        """
        SELECT Id_Site, SUM(Amount_Expenses) / %s, IFNULL(SUM(Paid), 0) / %s 
        FROM Expenses 
        WHERE (Ref_expenses = 'stock_ts' 
               OR Ref_expenses = 'bottle_invoice' 
               OR Ref_expenses = 'entrepreneur_contribution' 
               OR Ref_expenses = 'water quality alert' 
               OR Ref_expenses = 'technical intervention' 
               OR Ref_expenses = 'delivery_program_fee') 
        AND Month = %s
        GROUP BY Id_Site
        """, 
        (exchange_rate, exchange_rate, Current_date)
    ).fetchall()

    # Fetch debt payments
    allDebtPaid = con.execute(
        """
        SELECT Id_Site, IFNULL(SUM(CASE WHEN Paid > Amount_Expenses THEN Amount_Expenses ELSE Paid END), 0) / %s 
        FROM Expenses 
        WHERE Ref_expenses = 'debt' 
        AND Amount_Expenses > 0 
        AND Month > %s AND Month <= %s 
        GROUP BY Id_Site
        """, 
        (exchange_rate, Date_janv, Current_date)
    ).fetchall()

    # Fetch debt details
    allonlydebtjanv = con.execute(
        """
        SELECT Id_Site, Amount_Expenses / %s 
        FROM Expenses 
        WHERE Ref_expenses = 'debt' 
        AND Month = %s 
        AND Amount_Expenses > 0
        """, 
        (exchange_rate, Date_janv + relativedelta(months=+1))
    ).fetchall()

    alldebt = con.execute(
        """
        SELECT Id_Site, Amount_Expenses / %s 
        FROM Expenses 
        WHERE Ref_expenses = 'debt' 
        AND Month = %s
        """, 
        (exchange_rate, Current_date + relativedelta(months=+1))
    ).fetchall()

    alldebtM_1 = con.execute(
        """
        SELECT Id_Site, Amount_Expenses / %s 
        FROM Expenses 
        WHERE Ref_expenses = 'debt' 
        AND Month = %s
        """, 
        (exchange_rate, Current_date)
    ).fetchall()

    alldebtjanv = con.execute(
        """
        SELECT Id_Site, Amount_Expenses / %s 
        FROM Expenses 
        WHERE Ref_expenses = 'debt' 
        AND Month = %s
        """, 
        (exchange_rate, Date_janv + relativedelta(months=+1))
    ).fetchall()

    # Fetch Entrepreneur arrival dates
    allEntrepreneurDate = con.execute("""
        SELECT ep.Working_Date, ep.Id_Site, ep.Submitted_Date
        FROM entrepreneur_profiles ep
        INNER JOIN (
            SELECT Id_Site, MAX(Submitted_Date) AS Latest_Submitted
            FROM entrepreneur_profiles
            WHERE Submitted_Date <= %s AND Status = 'new_entrepreneur_coming' 
            GROUP BY Id_Site
        ) latest ON ep.Id_Site = latest.Id_Site AND ep.Submitted_Date = latest.Latest_Submitted
        """,Current_date).fetchall()
    
######### WRITE TITLE ###########
    
    worksheet_OFD.freeze_panes(7,6)
    worksheet_OFD.autofilter(6,0,len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)+7,40)
    worksheet_OFD.set_zoom(70)

    ColumnTitle = 0
    worksheet_OFD.write(6,ColumnTitle,"Like for Like",Site_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,11)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Site",Site_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,11)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Platform",Site_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,11)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Advisor",Site_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,11)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Entrepreneur Arrival",Site_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,11)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Tier",Site_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,11)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Total bot exc. WinS",YTD_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Total bot exc. WinS N-1",YTD_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"vs N-1 %",YTD_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Total bot inc. WinS",YTD_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Total bot inc. WinS N-1",YTD_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"vs N-1 %",YTD_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Sales $ exc. WinS",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Sales $ exc. WinS N-1",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"vs N-1 %",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Sales $ inc. WinS",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Sales $ inc. WinS N-1",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"vs N-1 %",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Income (profit + salary) $",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Income $ N-1",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"vs N-1 $",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Bottles Purchased $",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Consum Purchased $",YTD_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
   
    
    worksheet_OFD.write(6,ColumnTitle,"#Total Due $",YTD_Format_Three)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total EC Due $",YTD_Format_Three)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total Consum Due $",YTD_Format_Three)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total Other Due $ (debt + int)",YTD_Format_Three)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total WinS Due $",YTD_Format_Three)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total Paid $",YTD_Format_Three)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Collection Rate (inc. debt Settlement)",YTD_Format_Three)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Money collected since Jan %s"%(Current_date.year),YTD_Format_Three)
    worksheet_OFD.write_comment(6,ColumnTitle, "(+) : Collected/Deposited \n (-) : Unpaid/Withdrawal", {'x_scale': 3, 'y_scale': 0.8})
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1

    worksheet_OFD.write(6,ColumnTitle,"Sales $ inc. WinS",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Sales $ inc. WinS N-1",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"vs N-1 %",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Income (profit + salary) $",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Income $ N-1",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"vs N-1 $",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Bottles Purchased $",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Consum Purchased $",Monthly_Format_One)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1

    worksheet_OFD.write(6,ColumnTitle,"#Total Due $",Monthly_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total EC Due $",Monthly_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total Consum Due $",Monthly_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total Other Due $ (debt + int)",Monthly_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total WinS Due $",Monthly_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"#Total Paid $",Monthly_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Collection Rate (inc. debt Settlement)",Monthly_Format_Two)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Money collected this month",Monthly_Format_Two)
    worksheet_OFD.write_comment(6,ColumnTitle, "(+) : Collected/Deposited \n (-) : Unpaid/Withdrawal", {'x_scale': 3, 'y_scale': 0.8})
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Debt (-) / Savings(+) $",Debt_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14)
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Debt (-) / Savings(+) $ M-1",Debt_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    worksheet_OFD.write(6,ColumnTitle,"Debt (-) / Savings(+) Jan %s"%(Current_date.year),Debt_format)
    worksheet_OFD.set_column(ColumnTitle,ColumnTitle,14,None,{'level':1,'hidden':True})
    ColumnTitle+=1
    ColumnTitle+=1

    for i in range(ColumnTitle-9):
        if i+6 < 31:
            worksheet_OFD.write(0,i+6,"YTD",Title_format)
        else:
            worksheet_OFD.write(0,i+6,"Monthly",Title_format)

########WRITE DATA########
    for i in range(len(ListAllSite)):
        Column = 0 
        Entrepreneur_arrival = list(filter(lambda row: row[1] == ListAllSite[i][0], allEntrepreneurDate)) or [("",0,0)]
        Tier = list(filter(lambda row: row[0] == ListAllSite[i][0], ListTier)) or [("",'')]
        Sales = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales)) or [(0,0,0,0,0,0)]
        Sales_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales_lastyear)) or [(0,0,0,0,0,0)]
        Sales_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales_month)) or [(0,0,0,0,0,0)]
        Sales_month_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allSales_month_lastyear)) or [(0,0,0,0,0,0)]
        Expenses = list(filter(lambda row: row[0] == ListAllSite[i][0], allTotal_cost)) or [(0,0,0)]
        Expenses_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allTotal_cost_lastyear)) or [(0,0,0)]
        Expenses_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allTotal_cost_month)) or [(0,0,0)]
        Expenses_month_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allTotal_cost_month_lastyear)) or [(0,0,0)]
        Bottles_YTD = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "bottle_invoice", allDue_YTD)) or [(0,0,0)]
        Bottles_month = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "bottle_invoice", allDue_Month)) or [(0,0,0)]
        Consum_YTD = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "stock_ts", allDue_YTD)) or [(0,0,0)]
        Consum_month = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "stock_ts", allDue_Month)) or [(0,0,0)]
        EC_YTD = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "entrepreneur_contribution", allDue_YTD)) or [(0,0,0)]
        EC_month = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "entrepreneur_contribution", allDue_Month)) or [(0,0,0)]
        Other_YTD = list(filter(lambda row: row[0] == ListAllSite[i][0] and (row[2] == "water quality alert" or row[2]=="technical intervention" or row[2]=="delivery_program_fee"), allDue_YTD)) or [(0,0,0)]
        Other_month = list(filter(lambda row: row[0] == ListAllSite[i][0] and (row[2] == "water quality alert" or row[2] == "technical intervention" or row[2] == "delivery_program_fee"), allDue_Month)) or [(0,0,0)]
        WinS_YTD = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "WinS_invoice", allDue_YTD)) or [(0,0,0)]
        WinS_month = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[2] == "WinS_invoice", allDue_Month)) or [(0,0,0)]
        Salary_ent = list(filter(lambda row: row[0] == ListAllSite[i][0], allSalaryEnt)) or [(0,0,0)]
        Salary_ent_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allSalaryEnt_lastyear)) or [(0,0,0)]
        Salary_ent_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allSalaryEnt_month)) or [(0,0,0)]
        Salary_ent_month_lastyear = list(filter(lambda row: row[0] == ListAllSite[i][0], allSalaryEnt_month_lastyear)) or [(0,0,0)]
        Collection_rate = list(filter(lambda row: row[0] == ListAllSite[i][0], allCollectionRate)) or [(0,0,0)]
        Collection_rate_month = list(filter(lambda row: row[0] == ListAllSite[i][0], allCollectionRate_month)) or [(0,0,0)]
        DebtPaid = list(filter(lambda row: row[0] == ListAllSite[i][0], allDebtPaid)) or [(0,0,0)]
        Debt = list(filter(lambda row: row[0] == ListAllSite[i][0], alldebt)) or [(0,0,0)]
        DebtM_1 = list(filter(lambda row: row[0] == ListAllSite[i][0], alldebtM_1)) or [(0,0,0)]
        Debt_janv = list(filter(lambda row: row[0] == ListAllSite[i][0], alldebtjanv)) or [(0,0,0)]
        Debtonly_janv = list(filter(lambda row: row[0] == ListAllSite[i][0], allonlydebtjanv)) or [(0,0,0)]
        
        if i < len(ListSite_LikeforLike):
            worksheet_OFD.write(i+7,Column,"Like for Like",Number_bold_format)
            Column +=1
        else:
            worksheet_OFD.write(i+7,Column,"Others",Number_bold_format)
            Column +=1
        worksheet_OFD.write(i+7,Column,ListAllSite[i][0])
        Column +=1
        worksheet_OFD.write(i+7,Column,ListAllSite[i][1])
        Column +=1
        worksheet_OFD.write(i+7,Column,ListAllSite[i][2])
        Column +=1
        worksheet_OFD.write(i+7,Column,Entrepreneur_arrival[0][0],Date_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,Tier[0][1])
        Column +=1

        worksheet_OFD.write(i+7,Column,Sales[0][1],Number_format)
        ColumnTotBotexcWinSYTD = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_lastyear[0][1],Number_format)
        ColumnTotBotexcWinSYTD_lastyear = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s/%s-1,"")"%(xl_rowcol_to_cell(i+7,ColumnTotBotexcWinSYTD),xl_rowcol_to_cell(i+7,ColumnTotBotexcWinSYTD_lastyear)),Percentage_evol_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales[0][2],Number_format)
        ColumnTotBotincWinSYTD = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_lastyear[0][2],Number_format)
        ColumnTotBotincWinSYTD_lastyear = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnTotBotincWinSYTD),xl_rowcol_to_cell(i+7,ColumnTotBotincWinSYTD_lastyear)),Percentage_evol_format)
        Column +=1

        worksheet_OFD.write(i+7,Column,Sales[0][3],Money_format)
        ColumnSalesexcWinSYTD = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_lastyear[0][3],Money_format)
        ColumnSalesexcWinSYTD_lastyear = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnSalesexcWinSYTD),xl_rowcol_to_cell(i+7,ColumnSalesexcWinSYTD_lastyear)),Percentage_evol_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales[0][4],Money_format)
        ColumnSalesincWinSYTD = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_lastyear[0][4],Money_format)
        ColumnSalesincWinSYTD_lastyear = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnSalesincWinSYTD),xl_rowcol_to_cell(i+7,ColumnSalesincWinSYTD_lastyear)),Percentage_evol_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales[0][4]-Expenses[0][1]+Salary_ent[0][1],Money_format)
        ColumnIncomeYTD = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_lastyear[0][4]-Expenses_lastyear[0][1]+Salary_ent_lastyear[0][1],Money_format)
        ColumnIncomeYTD_lastyear = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s-%s,0)"%(xl_rowcol_to_cell(i+7,ColumnIncomeYTD),xl_rowcol_to_cell(i+7,ColumnIncomeYTD_lastyear)),Money_evol_format)
        Column +=1

    ################Collection rate ###############

        #Explication différence avec Collection Rate doc => Si le site ne paie pas les EC mais met des savings (qui vont donc dans les EC pour la finance) on le prend en compte dans le CR doc mais pas ici (arrive très rarement)
        worksheet_OFD.write(i+7,Column,Bottles_YTD[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Consum_YTD[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Collection_rate[0][1]+Debtonly_janv[0][1],Money_format)
        ColumnDueYTD = Column
        Column+=1
        worksheet_OFD.write(i+7,Column,EC_YTD[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Consum_YTD[0][1]+Bottles_YTD[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Other_YTD[0][1]+Debtonly_janv[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,WinS_YTD[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Collection_rate[0][2]+DebtPaid[0][1],Money_format)
        ColumnPaidYTD = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s/%s,\"\")"%(xl_rowcol_to_cell(i+7,ColumnPaidYTD),xl_rowcol_to_cell(i+7,ColumnDueYTD)),Percentage_format)
        ColumnCRYTD = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR((%s-%s),0)"%(-Debt[0][1],-Debt_janv[0][1]),Money_evol_format)
        Column +=1
        
        ##Monthly
        #ONE
        worksheet_OFD.write(i+7,Column,Sales_month[0][4],Money_format)
        ColumnSalesincWinSMonth = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_month_lastyear[0][4],Money_format)
        ColumnSalesincWinSMonth_lastyear = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s/%s-1,0)"%(xl_rowcol_to_cell(i+7,ColumnSalesincWinSMonth),xl_rowcol_to_cell(i+7,ColumnSalesincWinSMonth_lastyear)),Percentage_evol_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_month[0][4]-Expenses_month[0][1]+Salary_ent_month[0][1],Money_format)
        ColumnIncomeMonth = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,Sales_month_lastyear[0][4]-Expenses_month_lastyear[0][1]+Salary_ent_month_lastyear[0][1],Money_format)
        ColumnIncomeMonth_lastyear = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s-%s,0)"%(xl_rowcol_to_cell(i+7,ColumnIncomeMonth),xl_rowcol_to_cell(i+7,ColumnIncomeMonth_lastyear)),Money_evol_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,Bottles_month[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Consum_month[0][1],Money_format)
        Column+=1
        
        #TWO
        worksheet_OFD.write(i+7,Column,Collection_rate_month[0][1],Money_format)
        ColumnDueMonth= Column
        Column+=1
        worksheet_OFD.write(i+7,Column,EC_month[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Consum_month[0][1]+Bottles_month[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Other_month[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,WinS_month[0][1],Money_format)
        Column+=1
        worksheet_OFD.write(i+7,Column,Collection_rate_month[0][2],Money_format)
        ColumnPaidMonth = Column
        Column +=1
        worksheet_OFD.write_formula(i+7,Column,"=IFERROR(%s/%s,\"\")"%(xl_rowcol_to_cell(i+7,ColumnPaidMonth),xl_rowcol_to_cell(i+7,ColumnDueMonth)),Percentage_format)
        ColumnCRYTD = Column
        Column +=1
        worksheet_OFD.write(i+7,Column,"=IFERROR((%s-%s),0)"%(-Debt[0][1],-DebtM_1[0][1]),Money_evol_format)
        Column +=1


    ###################Debt ##################

        worksheet_OFD.write(i+7,Column,-Debt[0][1],Money_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,-DebtM_1[0][1],Money_format)
        Column +=1
        worksheet_OFD.write(i+7,Column,-Debt_janv[0][1],Money_format)
        Column +=1
        
        worksheet_OFD.write_formula(i+7,Column,"SUBTOTAL(3,A%s)"%(i+8))
        ColumnEndDoc = Column
        Column +=1

#######WRITE TOTAL#######
    ColumnTitle = 4
    worksheet_OFD.write(2,ColumnTitle,'Total Like for Like')
    worksheet_OFD.write(3,ColumnTitle,'Total Other')
    worksheet_OFD.write(4,ColumnTitle,'Total All')
    ColumnTitle+=1

    worksheet_OFD.write(1,ColumnTitle,"Number of sites")

    worksheet_OFD.write_formula(2,ColumnTitle,'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(F8:F%s>0)*(SUBTOTAL(3,OFFSET(F8,ROW(F8:F%s)-MIN(ROW(F8:F%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula(3,ColumnTitle,'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(F8:F%s>0)*(SUBTOTAL(3,OFFSET(F8,ROW(F8:F%s)-MIN(ROW(F8:F%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula(4,ColumnTitle,'=%s3+%s4'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnTotBotexcWinSYTD),xl_col_to_name(ColumnTotBotexcWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnTotBotexcWinSYTD),xl_col_to_name(ColumnTotBotexcWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnTotBotexcWinSYTD),xl_col_to_name(ColumnTotBotexcWinSYTD_lastyear)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnTotBotincWinSYTD),xl_col_to_name(ColumnTotBotincWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnTotBotincWinSYTD),xl_col_to_name(ColumnTotBotincWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnTotBotincWinSYTD),xl_col_to_name(ColumnTotBotincWinSYTD_lastyear)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSalesexcWinSYTD),xl_col_to_name(ColumnSalesexcWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSalesexcWinSYTD),xl_col_to_name(ColumnSalesexcWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSalesexcWinSYTD),xl_col_to_name(ColumnSalesexcWinSYTD_lastyear)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSalesincWinSYTD),xl_col_to_name(ColumnSalesincWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSalesincWinSYTD),xl_col_to_name(ColumnSalesincWinSYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSalesincWinSYTD),xl_col_to_name(ColumnSalesincWinSYTD_lastyear)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnIncomeYTD),xl_col_to_name(ColumnIncomeYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnIncomeYTD),xl_col_to_name(ColumnIncomeYTD_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnIncomeYTD),xl_col_to_name(ColumnIncomeYTD_lastyear)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1
    
    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3,0)'%(xl_col_to_name(ColumnPaidYTD),xl_col_to_name(ColumnDueYTD)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4,0)'%(xl_col_to_name(ColumnPaidYTD),xl_col_to_name(ColumnDueYTD)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5,0)'%(xl_col_to_name(ColumnPaidYTD),xl_col_to_name(ColumnDueYTD)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSalesincWinSMonth),xl_col_to_name(ColumnSalesincWinSMonth_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnSalesincWinSMonth),xl_col_to_name(ColumnSalesincWinSMonth_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnSalesincWinSMonth),xl_col_to_name(ColumnSalesincWinSMonth_lastyear)),Percentage_bold_evol_format)
    ColumnTitle+=1
    
    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnIncomeMonth),xl_col_to_name(ColumnIncomeMonth_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4-1,0)'%(xl_col_to_name(ColumnIncomeMonth),xl_col_to_name(ColumnIncomeMonth_lastyear)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5-1,0)'%(xl_col_to_name(ColumnIncomeMonth),xl_col_to_name(ColumnIncomeMonth_lastyear)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s3/%s3,0)'%(xl_col_to_name(ColumnPaidMonth),xl_col_to_name(ColumnDueMonth)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s4/%s4,0)'%(xl_col_to_name(ColumnPaidMonth),xl_col_to_name(ColumnDueMonth)),Percentage_bold_evol_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(%s5/%s5,0)'%(xl_col_to_name(ColumnPaidMonth),xl_col_to_name(ColumnDueMonth)),Percentage_bold_evol_format)
    ColumnTitle+=1

    worksheet_OFD.write_formula('%s3'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s4'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUMPRODUCT((A8:A%s="Others")*(SUBTOTAL(9,OFFSET(%s8,ROW(%s8:%s%s)-MIN(ROW(%s8:%s%s)),0)))),0)'%(7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    worksheet_OFD.write_formula('%s5'%(xl_col_to_name(ColumnTitle)),'=IFERROR(SUBTOTAL(9,%s8:%s%s),0)'%(xl_col_to_name(ColumnTitle),xl_col_to_name(ColumnTitle),7+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Number_bold_format)
    ColumnTitle+=1

def KPIOFD(Current_date,Date_janv,exchange_rate):
    worksheet = workbook.add_worksheet("KPI")
    con= db.pool.connect()
    Platform_List = con.execute("SELECT DISTINCT Code_Platform FROM Platform ORDER BY Code_Platform").fetchall()

    Tier = ExcelKPI.KPIFormat(workbook,worksheet,Current_date,Date_janv,2018,Platform_List)
    ExcelKPI.KPITotInc(workbook,worksheet,2,Current_date,Date_janv,Tier,Platform_List,exchange_rate,False)
    ExcelKPI.KPITotInc(workbook,worksheet,11,Current_date,Date_janv,Tier,Platform_List,exchange_rate,True)
    ExcelKPI.KPISalaryEnt(workbook,worksheet,20,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPIPL(workbook,worksheet,29,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPIDebt(workbook,worksheet,38,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPISaving(workbook,worksheet,48,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPICollectionRate(workbook,worksheet,58,Current_date,Date_janv,Tier,Platform_List,exchange_rate,Hide=0)

def GraphOFD(Current_date):

    worksheetGraphName = "Graph"
    worksheet = workbook.add_worksheet(worksheetGraphName)
    worksheet.set_zoom(70)

    ListPlatform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' """).fetchall()
    colGraph = 1
    lineData = 3
    for i in range(len(ListPlatform)):
        Graph.GraphDebtEvolution(workbook,worksheet,worksheetGraphName,1,colGraph,lineData,50,Current_date,ListPlatform[i][0])
        colGraph += 8
        lineData +=3

    Graph.GraphDebtEvolution(workbook,worksheet,worksheetGraphName,17,1,20,70,Current_date,"Total")

def DebtEvolution(Current_date,Date_N_1,ListPlatform):
    worksheet = workbook.add_worksheet("Debt Evolution")
    worksheet.freeze_panes(2,2)
    number_format = workbook.add_format({'num_format' : '# ##0'})
    number_format_bold = workbook.add_format({'num_format' : '# ##0','bold':True})
    qualitive_info_format = workbook.add_format({"bg_color": '#DCE6F1'})
    Date_format = workbook.add_format({'num_format': 'mmm-yy','bg_color' : '#EBF1DE'})
    Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
    
######SELECT DATA########
    Category_expenses = CategoryExpenses()
    allDebt_situation = con.execute("SELECT Amount_expenses,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Expenses WHERE Month >= %s AND Ref_expenses = 'debt'",date(int(Current_date.year)-1,1,1)).fetchall()
    allSalaryEnt_situation = con.execute("""SELECT SUM(Amount_expenses),Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') 
                                         FROM Expenses WHERE Month >= %s AND 
                                         (Ref_expenses='variable_salary_entrepreneurs' OR Ref_expenses='fix_salary_entrepreneurs')
                                         GROUP BY Month, Id_Site""",date(int(Current_date.year)-1,1,1)).fetchall()
    allRevenue_situation = con.execute("""SELECT SUM(Total_Income),Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') 
                                         FROM Sales WHERE Month >= %s GROUP BY Month, Id_Site""",date(int(Current_date.year)-1,1,1)).fetchall()
    allCost_situation = con.execute("""SELECT SUM(Amount_expenses),Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') 
                                         FROM Expenses WHERE Month >= %s AND
                                         (Category_expenses IN %s)
                                         GROUP BY Month, Id_Site""",(date(int(Current_date.year)-1,1,1),Category_expenses)).fetchall()
    InfoSite = con.execute("SELECT Id_Site,Platform,Advisor FROM Sites WHERE 1 = %s AND Platform IN %s",(1,ListPlatform)).fetchall()
    
######WRITE DATA#########
    worksheet.data_validation('A1',{'validate' : 'list',
                                    'source' : ['Debt', 'Salary','P&L','Income']})
    worksheet.write('A1', 'Debt',Select_format)
    worksheet.write('A3','Site',qualitive_info_format)
    worksheet.write('B3','Platform',qualitive_info_format)
    worksheet.write('C3','Advisor',qualitive_info_format)
    worksheet.write("C1","Total Savings",number_format_bold)
    worksheet.write("C2","Total Debts",number_format_bold)
    
    for i in range(len(InfoSite)):
        Column = 0

        debt_Site = list(filter(lambda row: row[1] == InfoSite[i][0], allDebt_situation))
        salary_Site = list(filter(lambda row: row[1] == InfoSite[i][0], allSalaryEnt_situation))
        revenue_Site = list(filter(lambda row: row[1] == InfoSite[i][0], allRevenue_situation))
        cost_Site = list(filter(lambda row: row[1] == InfoSite[i][0], allCost_situation))

        if InfoSite[i][1] == 'Dead':
            worksheet.set_row(i+3,options={'hidden': True})
        worksheet.write(i+3,Column,InfoSite[i][0],number_format)
        Column+=1
        worksheet.write(i+3,Column,InfoSite[i][1])
        Column+=1
        worksheet.write(i+3,Column,InfoSite[i][2])
        Column+=1

        start_date = date(Date_N_1.year,1,1)
        Loop = 0
        while start_date >= date(Date_N_1.year,1,1) and start_date<= Current_date:
            debtSituation = list(filter(lambda row: row[2] == str(start_date+relativedelta(months=+1)), debt_Site)) or [(0,0)]
            salarySituation = list(filter(lambda row: row[2] == str(start_date), salary_Site)) or [(0,0)]
            revenueSituation = list(filter(lambda row: row[2] == str(start_date), revenue_Site)) or [(0,0)]
            costSituation = list(filter(lambda row: row[2] == str(start_date), cost_Site)) or [(0,0)]
            worksheet.write_formula(i+3,Loop+Column,"""=CHOOSE(
                                                            MATCH($A$1, {"Debt", "Salary","P&L", "Income"}, 0),
                                                            %s,
                                                            %s,
                                                            %s,
                                                            %s,           
                                                            )/%s"""%(-debtSituation[0][0],salarySituation[0][0],revenueSituation[0][0]-costSituation[0][0],revenueSituation[0][0]+salarySituation[0][0]-costSituation[0][0],exchange_rate_year(start_date)),number_format)
            start_date += relativedelta(months=+1)
            Loop +=1

        

    start_date = date(Date_N_1.year,1,1)
    Loop = 0 
    while start_date >= date(Date_N_1.year,1,1) and start_date<= Current_date:
        worksheet.write(2,Loop+3,str(start_date.year) + '-' + str(start_date.month),Date_format)
        worksheet.write_formula(0,Loop+3,"=SUMPRODUCT((%s4:%s%s>0)*(SUBTOTAL(9,OFFSET(%s4,ROW(%s4:%s%s)-MIN(ROW(%s4:%s%s)),0))))"%(xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3),number_format_bold)
        worksheet.write_formula(1,Loop+3,"=SUMPRODUCT((%s4:%s%s<0)*(SUBTOTAL(9,OFFSET(%s4,ROW(%s4:%s%s)-MIN(ROW(%s4:%s%s)),0))))"%(xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3),number_format_bold)
        start_date += relativedelta(months=+1)
        Loop += 1


    worksheet.write(2,Loop+4,"Debt/Saving",number_format_bold)
    worksheet.autofilter('A3:%s3'%(xl_col_to_name(Loop +2)))
    worksheet.filter_column(1,'Platform <> Dead')

def Expenses(Current_date,Date_last_janv,ListPlatform,workbook):

    Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})

    ListSite_LikeforLike = con.execute("SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites WHERE Sites.Id_Site IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) AND Old_Platform IN %s ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site",Date_last_janv+relativedelta(months=+1),ListPlatform).fetchall()
    ListOnlysiteLikeforLike = [i[0] for i in ListSite_LikeforLike] or [0]
    ListSite_notLikeforLike = con.execute("SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites INNER JOIN Sales ON Sites.Id_Site = Sales.Id_Site WHERE 1 = %s AND Sites.Id_Site NOT IN %s AND Old_Platform IN %s ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site",(1,ListOnlysiteLikeforLike,ListPlatform)).fetchall()

    ListAllSite = ListSite_LikeforLike + ListSite_notLikeforLike

    allExpenses_Monthly = con.execute("""SELECT Id_Site,Ref_expenses,Amount_expenses
                                   FROM Expenses WHERE Month = %s""",Current_date).fetchall()
    
    allExpenses_YTD = con.execute("""SELECT Id_Site,Ref_expenses,SUM(Amount_expenses)
                                        FROM Expenses WHERE Month >= %s AND Month <= %s
                                        GROUP BY Id_Site,Ref_expenses""",date(Current_date.year,1,1),Current_date).fetchall()

    allRevenue_Monthly = con.execute("""SELECT Id_Site,Hod_income,Shopkeeper_income,WiS_Income, Onsite_Income + Bottle_Income + Other_Income
                                        FROM Sales WHERE Month = %s""",Current_date).fetchall()
    
    allRevenue_YTD = con.execute("""SELECT Id_Site,SUM(Hod_income),SUM(Shopkeeper_income),SUM(WiS_Income),SUM(Onsite_Income + Bottle_Income + Other_Income)
                                        FROM Sales WHERE Month >= %s AND Month <= %s
                                        GROUP BY Id_Site""",date(Current_date.year,1,1),Current_date).fetchall()
    
    worksheet = workbook.add_worksheet("Exp")
    worksheet.set_zoom(70)

    Name_Revenue = ["HOD","Shopkeeper","WiS","Others"]
    Name_Expenses = ["Production","Salary","Delivery","Contribution","Intervention","Investment"]
    Expenses = [[
                    ["Consumables","consumable_production"],
                    ["Consumables TS","stock_ts"],
                    ["Bottles","bottle_invoice"],
                    ["Electricity","electricity"],
                    ["Gasoline Water-pump","gasoline_waterpump"],
                    ["Raw Water","raw_water"]
                ],
                [
                    ["Fixed salary Entrepreneur","fix_salary_entrepreneurs"],
                    ["Variable salary Entrepreneur","variable_salary_entrepreneurs"],
                    ["Fixed salary Operators","fix_salary_operators"],
                    ["Variable salary Operators","variable_salary_operators"]
                ],
                [
                    ["Maintenance","maintenance_delivery"],
                    ["Gasoline Delivery","gasoline_delivery"]
                ],
                [
                    ["Commune Contribution","commune_contribution"],
                    ["Entrepreneur Contribution","entrepreneur_contribution"]
                ],
                [
                    ["Technical Intervention","technical intervention"],
                    ["Water Quality Intervention","water quality alert"]
                ],
                [
                    ["Investment","investment"]
                ]]
            
    
    worksheet.data_validation('A1',{'validate' : 'list',
                                    'source' : ['YTD', 'Monthly']})
    worksheet.write('A1', 'YTD',Select_format)
    worksheet.merge_range(0,3,0,3+len(Name_Revenue)-1,"Income",workbook.add_format({'bold':True}))
    for i in range(len(Name_Revenue)):
        worksheet.write(1,i+3,Name_Revenue[i],workbook.add_format({'bold':True}))
    Number_expenses_previous = len(Name_Revenue)
    for j in range(len(Name_Expenses)):
            Number_expenses = len(Expenses[j])
            worksheet.merge_range(0,2+Number_expenses_previous+1,0,2+Number_expenses_previous+Number_expenses,Name_Expenses[j],workbook.add_format({'bold':True}))
            for k in range(len(Expenses[j])):
                worksheet.write(1,3+k+Number_expenses_previous,Expenses[j][k][0],workbook.add_format({'bold':True}))
            Number_expenses_previous += Number_expenses


    for i in range(len(ListAllSite)):
        Column = 0
        worksheet.write(i+2,Column,ListAllSite[i][0])
        Column += 1
        worksheet.write(i+2,Column,ListAllSite[i][1])
        Column += 1
        worksheet.write(i+2,Column,ListAllSite[i][2])
        Column += 1
        for j in range(len(Name_Revenue)):
            Revenue_Monthly = list(filter(lambda row: row[0] == ListAllSite[i][0], allRevenue_Monthly)) or [(0,0,0,0,0,0)]
            Revenue_YTD = list(filter(lambda row: row[0] == ListAllSite[i][0], allRevenue_YTD)) or [(0,0,0,0,0,0)]
            worksheet.write_formula(i+2,Column,'=IF($A$1 = "YTD",%s,IF($A$1="Monthly",%s,""))'%(Revenue_YTD[0][j+1],Revenue_Monthly[0][j+1]),workbook.add_format({'num_format' : '# ##0'}))
            Column += 1
        for j in range(len(Expenses)):
            for k in range(len(Expenses[j])):
                Expenses_Month = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[1] == Expenses[j][k][1], allExpenses_Monthly)) or [(0,0,0,0)]
                Expenses_YTD = list(filter(lambda row: row[0] == ListAllSite[i][0] and row[1] == Expenses[j][k][1], allExpenses_YTD)) or [(0,0,0,0)]
                worksheet.write_formula(i+2,Column+k,'=IF($A$1 = "YTD",%s,IF($A$1="Monthly",%s,""))'%(Expenses_YTD[0][2],Expenses_Month[0][2]),workbook.add_format({'num_format' : '# ##0'}))
            Column += len(Expenses[j])

def DataConsumableSold(workbook,exchange_rate,Current_date,ListPlatform=0):
    con=db.pool.connect()
    worksheet = workbook.add_worksheet("Consum")
    worksheet.set_zoom(70)
#####################Data Extraction #######################
    if ListPlatform==0:
        ListPlatform = tuple(
            platform[0] for platform in con.execute(
                "SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead'"
            ).fetchall()
        )
    Date_janv = date(Current_date.year-1,12,1)

    ListTier = NewCalculTier(Current_date)[0]
    allSiteInfo = con.execute("""SELECT Id_Site,Platform,Advisor 
                              FROM Sites WHERE Old_Platform <>"Dead" 
                              AND 1 = %s AND Platform IN %s""",
                                (1,ListPlatform)).fetchall()
    allItemSold_Month = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Id_Site,Item 
                                    FROM Consumable 
                                    WHERE Month = %s AND Validate = 1 AND Item IN %s
                                    GROUP BY Id_Site,Item
                                    ORDER BY Id_Site""",(exchange_rate,Current_date,ConsumableForOFD()[2])).fetchall()

    allItemSold_YTD = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Id_Site,Item 
                                    FROM Consumable 
                                    WHERE Month <= %s AND Month > %s AND Validate = 1 AND Item IN %s 
                                    GROUP BY Id_Site,Item""",(exchange_rate,Current_date,Date_janv,ConsumableForOFD()[2])).fetchall() 

    ItemName = con.execute("""
                                WITH RankedUnits AS (
                                    SELECT 
                                        Item, 
                                        English_name, 
                                        Unit, 
                                        COUNT(*) AS count,
                                        RANK() OVER (PARTITION BY Item ORDER BY COUNT(*) DESC) AS rnk
                                    FROM Consumable
                                    GROUP BY Item, English_name, Unit
                                )
                                SELECT Item, English_name, Unit
                                FROM RankedUnits
                                WHERE rnk = 1
                            """).fetchall()

#################### Format #############################
    
    Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
    Site_format = workbook.add_format({'bg_color':"#DAEEF3",'bold': True, 'text_wrap' : True,'valign':'vcenter','center_across':True})
    bg_grey_format = workbook.add_format({'bg_color':'#BFBFBF','font_color':'#BFBFBF'})
    Title_Item_number_format = workbook.add_format({'bg_color':'#D8E4BC','bold':True,'text_wrap': True,'align':'center','valign':'vcenter'})
    Title_Item_revenue_format = workbook.add_format({'bg_color':'#538DD5','bold':True,'text_wrap': True,'align':'center','valign':'vcenter'})
    Number_format = workbook.add_format({'num_format':'# ### ##0'})
    Number_bold_format = workbook.add_format({'num_format':'# ### ##0','bold':True})

    worksheet.set_column('A:A',15)
    worksheet.set_column('B:AP',9)
    worksheet.set_column('F:F',15.5)
    worksheet.freeze_panes(2,4)
#######################Writing data ########################
    
    worksheet.data_validation('A1',{'validate' : 'list',
                                    'source' : ['Monthly','YTD']})
    worksheet.write('A1', 'YTD',Select_format)

    worksheet.write("D2","Total",Number_bold_format)

    worksheet.write(2,0,"Site",Site_format)
    worksheet.write(2,1,"Platform",Site_format)
    worksheet.write(2,2,"Advisor",Site_format)
    worksheet.write(2,3,"Tier",Site_format)
    
    ListItems = [["Bottles"],ConsumableForOFD()[0]]
    Number_of_column = len(ListItems[0])+len(ListItems[1])
    for j in range(len(ListItems)):
        for k in range(len(ListItems[j])):
            Item_Name = list(filter(lambda row: row[0] == ListItems[j][k], ItemName)) or [("\"\"","Bottles","unit")]

            worksheet.write_formula(0,4+j+k,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(4+j+k),xl_col_to_name(4+j+k),len(allSiteInfo)+3),Number_bold_format)
            worksheet.write_formula(0,4+j+k+Number_of_column,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(4+j+k+Number_of_column),xl_col_to_name(4+j+k+Number_of_column),len(allSiteInfo)+3),Number_bold_format)
            
            worksheet.write(1,4+j+k,Item_Name[0][2],Title_Item_number_format)
            worksheet.write(1,4+j+k+Number_of_column,"$",Title_Item_revenue_format)
            
            worksheet.write(2,4+j+k,Item_Name[0][1],Title_Item_number_format)
            worksheet.write(2,4+j+k+Number_of_column,Item_Name[0][1],Title_Item_revenue_format)
            
            worksheet.set_column(4+j+k, 4+j+k, 15)  # Increase column width
            worksheet.set_column(4+j+k+Number_of_column, 4+j+k+Number_of_column, 15)  # Increase column width
                
    for i in range(len(allSiteInfo)):
        Sites_info = list(filter(lambda row: row[0] == allSiteInfo[i][0], allSiteInfo)) or [("\"\"","\"\"","\"\"")]
        Tier = list(filter(lambda row: row[0] == allSiteInfo[i][0], ListTier)) or [("\"\"","\"\"","\"\"")]

        worksheet.write(i+3,0,Sites_info[0][0])
        worksheet.write(i+3,1,Sites_info[0][1])
        worksheet.write(i+3,2,Sites_info[0][2])
        worksheet.write(i+3,3,Tier[0][1])
        
        #SUM OF BOTTLES
        Bottles_month = 0
        Bottles_YTD =0
        Bottles_month_rev = 0
        Bottles_YTD_rev = 0
        Bottles_items = ConsumableForOFD()[1]
        for m in range(len(ConsumableForOFD()[1])):
            ItemSold_Month = list(filter(lambda row: row[2] == allSiteInfo[i][0] and row[3] == Bottles_items[m], allItemSold_Month)) or [(0,0,0,0)]
            
            ItemSold_YTD = list(filter(lambda row: row[2] == allSiteInfo[i][0] and row[3] == Bottles_items[m], allItemSold_YTD)) or [(0,0,0,0)]
            Bottles_month += ItemSold_Month[0][0]
            Bottles_month_rev += ItemSold_Month[0][1]
            Bottles_YTD += ItemSold_YTD[0][0]
            Bottles_YTD_rev += ItemSold_YTD[0][1]
        #Write datas
        for j in range(len(ListItems)):
            for k in range(len(ListItems[j])):
                if ListItems[j][k] == "Bottles":
                    ItemSold_Month = [(Bottles_month,Bottles_month_rev,0,0)]
                    ItemSold_YTD = [(Bottles_YTD,Bottles_YTD_rev,0,0)]
                else:
                    ItemSold_Month = list(filter(lambda row: row[2] == allSiteInfo[i][0] and row[3] == ListItems[j][k], allItemSold_Month)) or [(0,0,0,0)]
                    ItemSold_YTD = list(filter(lambda row: row[2] == allSiteInfo[i][0] and row[3] == ListItems[j][k], allItemSold_YTD)) or [(0,0,0,0)]
                
                worksheet.write_formula(i+3,4+j+k,
                                        '=IF($A$1="Monthly",%s,IF($A$1="YTD",%s,""))' % (ItemSold_Month[0][0], ItemSold_YTD[0][0]),
                                        Number_format)
                worksheet.write_formula(i+3,4+j+k+Number_of_column,
                                        '=IF($A$1="Monthly",%s,IF($A$1="YTD",%s,""))' % (ItemSold_Month[0][1], ItemSold_YTD[0][1]),
                                        Number_format)
    worksheet.conditional_format('E4:%s%s'%(xl_col_to_name(2*Number_of_column+3),(len(allSiteInfo)+3)),{"type" : "formula", "criteria" : "E4=0", "format" : bg_grey_format})

    worksheet.autofilter(2,0,(len(allSiteInfo)+3),2*Number_of_column+3)

def LaunchExcelCreationOFD(Current_date,exchange_rate,ListTier,ListPlatform):
    Date_janv = date(Current_date.year-1,12,1)
    Date_N_1 = date(Current_date.year-1,Current_date.month,1)
    Date_last_janv = date(Date_N_1.year-1,12,1)
    ListSiteActive = listSiteStillActive(Current_date,Date_N_1)
    
    CreateOFD(Current_date,ListPlatform)
    WriteOFD(Current_date,Date_janv,Date_N_1,Date_last_janv,exchange_rate,ListTier,ListPlatform)
    DataConsumableSold(workbook,exchange_rate,Current_date,ListPlatform)
    DebtEvolution(Current_date,Date_N_1,ListPlatform)
    Expenses(Current_date,Date_last_janv,ListPlatform,workbook)
    KPIOFD(Current_date,Date_janv,exchange_rate)
    GraphOFD(Current_date)
    SiteAnalysis(ListTier,ListSiteActive,workbook,Current_date,True)
    ExcelF2F.InstructionTab(workbook,Current_date,Date_N_1)
    workbook.close()
