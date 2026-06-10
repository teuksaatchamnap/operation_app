from math import e
import db
import xlsxwriter
from datetime import date
import tempfile
from dateutil.relativedelta import *
from xlsxwriter.utility import xl_col_to_name
import os
import calendar
from monthlyreport import ExcelKPI
from monthlyreport.ExcelOFD import DataConsumableSold
from monthlyreport.ExcelSiteAnalysis import SiteAnalysis
from monthlyreport.Functionutils import exchange_rate_year, listSiteStillActive
from monthlyreport.Graph import GraphDebtEvolution


def CreateSummary(Current_date,exchange_rate,workbook):
    con = db.pool.connect()
    worksheet_income = workbook.add_worksheet("Site Balance")
    brown_format = workbook.add_format({'font_color': '#974706'})
    Title_format = workbook.add_format({'border' : 1,'bold' : True,'center_across': True})
    Title_expenses_format = workbook.add_format({'border' : 1,'bold' : True,'center_across': True, 'bg_color' : '#FE6262'})
    Title_income_format = workbook.add_format({'border' : 1,'bold' : True,'center_across': True, 'bg_color' : '#D8E4BC'})
    Title_total_format = workbook.add_format({'border' : 1,'bold' : True,'center_across': True, 'bg_color' : '#B7DEE8','text_wrap':True})
    Title_Evol_format = workbook.add_format({'border' : 1,'bold' : True,'center_across': True, 'bg_color' : '#4F6228','text_wrap':True})
    grey_border_format = workbook.add_format({'bg_color' : "#C0C0C0"})
    Number_format = workbook.add_format({'num_format' : "# ### ##0"})
    NumberEvol_format = workbook.add_format({'num_format' : "+# ### ##0;-# ### ##0"})
    Bold_Number_format = workbook.add_format({'num_format' : "# ### ##0",'bold':True})

##########WRITE TITLE###########

    worksheet_income.set_zoom(70)
    worksheet_income.freeze_panes(3,4)
    worksheet_income.set_column('C:E',len("consumable i  "))
    worksheet_income.set_column('F:K',len("consumable income     "))
    worksheet_income.set_column('L:L',2)
    worksheet_income.set_column('M:R',len("consumable income     "))
    worksheet_income.set_column('T:U',len("Debt vs M-12 "))
    
    ColumnTitle=0
    worksheet_income.write(2,ColumnTitle,"Site")
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Platform")
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Project ?")
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Advisor")
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Tier")
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Initial Balance",Title_total_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"WinS Cost",Title_expenses_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Jugs Sold",Title_income_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Consumable Sold",Title_income_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"EC",Title_income_format)
    ColumnTitle+=1
    worksheet_income.write(2,10,"Intervention",Title_income_format)
    ColumnTitle+=1
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Due/Owed",Title_total_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Paid",Title_total_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Debt Repaid",Title_total_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Withdrawal/Deposit",Title_total_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Adjustment (+) debts repaid (-) withdrawal",Title_total_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Final Balance (+) debts (-) savings",Title_total_format)
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Savings outside TS (+) debts (-) savings",Title_total_format)
    ColumnTitle+=1
    ColumnTitle+=1
    worksheet_income.write(2,ColumnTitle,"Debt vs M-1",Title_Evol_format)
    ColumnTitle+=1  
    worksheet_income.write(2,ColumnTitle,"Debt vs M-12",Title_Evol_format)
    ColumnTitle+=1
    worksheet_income.write(0,0,'Pick the currency for the document in A2',brown_format)
    worksheet_income.data_validation('A2',{'validate' : 'list',
                                    'source' : ['USD', 'Riel']})
    worksheet_income.write_formula('B2','=IF(A2="Riel",1,%s)'%(exchange_rate))
    worksheet_income.write('A2','USD')

#######DATA SELECTION######

    query = con.execute("SELECT IFNULL(Amount_expenses,0),Id_Site FROM Expenses WHERE Ref_expenses = 'WinS_invoice' AND Month = %s",(Current_date))
    allWinSCost = query.fetchall()
    query = con.execute("SELECT IFNULL(Amount_expenses,0),Id_Site FROM Expenses WHERE Ref_expenses = 'bottle_invoice' AND Month = %s",(Current_date))
    allBottleIncome = query.fetchall()
    query = con.execute("SELECT IFNULL(Amount_expenses,0),Id_Site FROM Expenses WHERE Ref_expenses = 'stock_ts' AND Month = %s",(Current_date))
    allStockConsommable = query.fetchall()
    query = con.execute("SELECT IFNULL(Amount_expenses,0),Id_Site FROM Expenses WHERE Ref_expenses = 'entrepreneur_contribution' AND Month = %s",(Current_date))
    allAssistantFee = query.fetchall()
    query = con.execute("SELECT IFNULL(Amount_expenses,0),Id_Site FROM Expenses WHERE Ref_expenses = 'debt' AND Month = %s",(Current_date))
    allDebt_M_1 = query.fetchall()
    query = con.execute("SELECT IFNULL(Amount_expenses,0),Id_Site FROM Expenses WHERE Ref_expenses = 'debt' AND Month = %s",(Current_date-relativedelta(months=+11)))
    allDebt_M_12 = query.fetchall()
    query = con.execute("SELECT IFNULL(paid,0),Id_Site FROM Expenses WHERE Ref_expenses = 'debt' AND Month = %s",(Current_date))
    allDebt_paid = query.fetchall()
    query = con.execute("SELECT IFNULL(Paid,0),Id_Site FROM Expenses WHERE Ref_expenses = 'withdrawal' AND Month = %s",(Current_date))
    allWithdrawal = query.fetchall()
    query = con.execute("SELECT IFNULL(Paid,0),Id_Site FROM Expenses WHERE Ref_expenses = 'adjustment' AND Month = %s",(Current_date))
    allAdjustment = query.fetchall()
    query = con.execute("SELECT Id_Site,Platform,Advisor,Project,Last_Tier FROM Sites")
    ListSite = query.fetchall()
    query = con.execute("SELECT IFNULL(SUM(Paid),0),Id_Site FROM Expenses WHERE (Ref_expenses = 'entrepreneur_contribution' OR Ref_expenses = 'technical intervention' OR Ref_expenses = 'water quality alert' OR Ref_expenses ='stock_ts' OR Ref_expenses ='bottle_invoice' OR Ref_expenses = 'WinS_invoice') AND Month = %s GROUP BY Id_Site",(Current_date))
    allPaidtoTS = query.fetchall()
    query = con.execute("SELECT IFNULL(Amount_expenses,0),Id_Site FROM Expenses WHERE Ref_expenses = 'debt' AND Month = %s",(Current_date+relativedelta(months=+1)))
    allDebt = query.fetchall()
    query = con.execute ("SELECT IFNULL(SUM(Amount_expenses),0),Id_Site FROM Expenses WHERE Month = %s AND (Ref_expenses = 'technical intervention' OR Ref_expenses = 'water quality alert')  GROUP BY Id_Site",(Current_date))
    allIntervention = query.fetchall()
    query = con.execute("SELECT IFNULL(Saving_outside_TS,0),Id_Site FROM Indicators WHERE Month = %s",Current_date)
    allSavingoutsideTS = query.fetchall()

#######WRITE DATA######
    for i in range(len(ListSite)):

        WinSCost = list(filter(lambda row: row[1] == ListSite[i][0], allWinSCost)) or [(0,0)]
        BottleIncome = list(filter(lambda row: row[1] == ListSite[i][0], allBottleIncome)) or [(0,0)]
        StockConsommable = list(filter(lambda row: row[1] == ListSite[i][0], allStockConsommable)) or [(0,0)]
        AssistantFee = list(filter(lambda row: row[1] == ListSite[i][0], allAssistantFee)) or [(0,0)]
        Debt_M_1 = list(filter(lambda row: row[1] == ListSite[i][0], allDebt_M_1)) or [(0,0)]
        Debt_M_12 = list(filter(lambda row: row[1] == ListSite[i][0], allDebt_M_12)) or [(0,0)]
        PaidtoTS = list(filter(lambda row: row[1] == ListSite[i][0], allPaidtoTS)) or [(0,0)]
        Debt = list(filter(lambda row: row[1] == ListSite[i][0], allDebt)) or [(0,0)]
        Withdrawal = list(filter(lambda row: row[1] == ListSite[i][0], allWithdrawal)) or [(0,0)]
        Adjustment = list(filter(lambda row: row[1] == ListSite[i][0], allAdjustment)) or [(0,0)]
        Debt_paid = list(filter(lambda row: row[1] == ListSite[i][0], allDebt_paid)) or [(0,0)]
        Intervention = list(filter(lambda row: row[1] == ListSite[i][0], allIntervention)) or [(0,0)]
        Saving_outside_TS = list(filter(lambda row: row[1] == ListSite[i][0], allSavingoutsideTS)) or [(0,0)]
        Total_due = 0

        Column =0
        SiteInfo = list(filter(lambda row: row[0] == ListSite[i][0], ListSite))

        worksheet_income.write(i+3,Column,ListSite[i][0],Bold_Number_format)
        Column+=1
        worksheet_income.write(i+3,Column,SiteInfo[0][1],Bold_Number_format)
        Column+=1
        if SiteInfo[0][3]:
            worksheet_income.write(i+3,Column,"yes",Bold_Number_format)
            Column+=1
        else:
            worksheet_income.write(i+3,Column,"no",Bold_Number_format)
            Column+=1
        
        if SiteInfo[0][1] == 'Dead':
            worksheet_income.set_row(i+3,options={'hidden': True})
        worksheet_income.write(i+3,Column,SiteInfo[0][2],Bold_Number_format)
        Column+=1
        worksheet_income.write(i+3,Column,SiteInfo[0][4],Bold_Number_format)
        Column+=1

        worksheet_income.write_formula(i+3,Column,"=IFERROR(%s/$B$2,\"\")"%Debt_M_1[0][0],Number_format)
        Column+=1

        worksheet_income.write_formula(i+3,Column,"=IFERROR(%s/$B$2,\"\")"%WinSCost[0][0],Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=IFERROR(%s/$B$2,\"\")"%BottleIncome[0][0],Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=IFERROR(%s/$B$2,\"\")"%StockConsommable[0][0],Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=IFERROR(%s/$B$2,\"\")"%AssistantFee[0][0],Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=IFERROR(%s/$B$2,\"\")"%Intervention[0][0],Number_format)
        Column+=1
        Column+=1
        worksheet_income.write_formula(i+3,Column,'=%s/$B$2'%(WinSCost[0][0]+BottleIncome[0][0]+StockConsommable[0][0]+AssistantFee[0][0]+Intervention[0][0]),Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=%s/$B$2"%PaidtoTS[0][0],Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=%s/$B$2"%Debt_paid[0][0],Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=%s/$B$2"%(-Withdrawal[0][0]),Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=%s/$B$2"%(Adjustment[0][0]),Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=%s/$B$2"%(Debt[0][0]),Number_format)
        Column+=1
        worksheet_income.write_formula(i+3,Column,"=-%s/$B$2"%Saving_outside_TS[0][0],Number_format)
        Column+=1
        Column+=1
        worksheet_income.write(i+3,Column,"=(%s-%s)/$B$2"%(Debt[0][0],Debt_M_1[0][0]),NumberEvol_format)
        Column+=1
        worksheet_income.write(i+3,Column,"=(%s-%s)/$B$2"%(Debt[0][0],Debt_M_12[0][0]),NumberEvol_format)



    worksheet_income.autofilter(2,0,len(ListSite)+3,18)
    worksheet_income.filter_column(1,'Platform <> Dead')

    worksheet_income.write_formula(1,5,'=SUBTOTAL(9,F4:F%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,6,'=SUBTOTAL(9,G4:G%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,7,'=SUBTOTAL(9,H4:H%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,8,'=SUBTOTAL(9,I4:I%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,9,'=SUBTOTAL(9,J4:J%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,10,'=SUBTOTAL(9,K4:K%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,12,'=SUBTOTAL(9,M4:M%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,13,'=SUBTOTAL(9,N4:N%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,14,'=SUBTOTAL(9,O4:O%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,15,'=SUBTOTAL(9,P4:P%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,16,'=SUBTOTAL(9,Q4:Q%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,17,'=SUBTOTAL(9,R4:R%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,19,'=SUBTOTAL(9,T4:T%s)'%(len(ListSite) + 3),Bold_Number_format)
    worksheet_income.write_formula(1,20,'=SUBTOTAL(9,U4:U%s)'%(len(ListSite) + 3),Bold_Number_format)

def CreateDebtEvolution(Current_date,Date_N_1,workbook):
    con = db.pool.connect()
    worksheet_debt = workbook.add_worksheet("Debt Evolution")
    worksheet_debt.hide_gridlines(2)

    Number_format = workbook.add_format({'num_format' : "# ### ##0", 'border' : 1})
    Bold_Number_format = workbook.add_format({'num_format' : "# ### ##0", 'border' : 1,'bold':True})
    Bold_grey_format = workbook.add_format({'bg_color' : "#C0C0C0",'border' : 1,'bold':True})
    worksheet_debt.merge_range(2,0,4,0,Current_date.year,Bold_Number_format)
    worksheet_debt.merge_range(7,0,9,0,Date_N_1.year,Bold_Number_format)
    worksheet_debt.write(2,1,"Debts",Bold_grey_format)
    worksheet_debt.write(3,1,"Savings",Bold_grey_format)
    worksheet_debt.write(4,1,"Total",Bold_grey_format)
    worksheet_debt.write(7,1,"Debts",Bold_grey_format)
    worksheet_debt.write(8,1,"Savings",Bold_grey_format)
    worksheet_debt.write(9,1,"Total",Bold_grey_format)
    ListPlatform = con.execute("SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Stop' AND Platform <>'' AND Platform <> 'Dead'").fetchall()
    for i in range(1,Current_date.month+1):
        Month_number = Current_date.month+1-i
        This_month = date(Current_date.year,Month_number,1)
        query = con.execute("SELECT SUM(Amount_expenses)/%s,Platform FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_expenses > 0 AND Platform <> '' GROUP BY Platform",(exchange_rate_year(This_month),This_month+relativedelta(months=+1)))
        alldebt = query.fetchall()
        query = con.execute("SELECT SUM(Amount_expenses)/%s,Platform FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_expenses < 0 AND Platform <> '' GROUP BY Platform",(exchange_rate_year(This_month),This_month+relativedelta(months=+1)))
        allsaving = query.fetchall()
        Name_month = calendar.month_name[This_month.month]
        Date = str(Name_month) + '-' + str(This_month.year)
        #worksheet_debt.set_column('%s:%s'%(xl_col_to_name(i+2),xl_col_to_name(i+2)),len(Date))
        worksheet_debt.write(5*i+7,2,Date,Bold_Number_format)
        worksheet_debt.write(5*i+8,2,"Debts",Bold_grey_format)
        worksheet_debt.write(5*i+9,2,"Savings",Bold_grey_format)
        worksheet_debt.write(5*i+10,2,"Total",Bold_grey_format)
        Total_debt = Total_saving = 0

        for j in range(len(ListPlatform)):
            debt = list(filter(lambda row: row[1] == ListPlatform[j][0], alldebt))
            saving = list(filter(lambda row: row[1] == ListPlatform[j][0], allsaving))

            worksheet_debt.write(5*i+7,3+j,ListPlatform[j][0],Bold_Number_format)
            if debt and debt[0][0]:
                worksheet_debt.write(5*i+8,3+j,debt[0][0],Number_format)
                Total_debt += debt[0][0]
            if saving and saving[0][0]:
                Total_saving += saving[0][0]
                worksheet_debt.write(5*i+9,3+j,saving[0][0],Number_format)
            worksheet_debt.write_formula(10+5*i,3+j,"=%s%s+%s%s"%(xl_col_to_name(3+j),5*i+9,xl_col_to_name(3+j),10+5*i),Number_format)
        #Writing Stop Platform
        debt_dead = list(filter(lambda row: row[1] == "Dead", alldebt)) or [(0,)]
        saving_dead = list(filter(lambda row: row[1] == "Dead", allsaving)) or [(0,)]
        worksheet_debt.write(5*i+7,len(ListPlatform)+3,"Closed Sites",Bold_Number_format)
        worksheet_debt.write(5*i+8,len(ListPlatform)+3,debt_dead[0][0],Number_format)
        worksheet_debt.write(5*i+9,len(ListPlatform)+3,saving_dead[0][0],Number_format)
        Total_debt += debt_dead[0][0]
        Total_saving += saving_dead[0][0]
        worksheet_debt.write_formula(10+5*i,len(ListPlatform)+3,"=%s%s+%s%s"%(xl_col_to_name(len(ListPlatform)+3),5*i+9,xl_col_to_name(len(ListPlatform)+3),10+5*i),Number_format)
        #Writing Total
        worksheet_debt.write(5*i+7,len(ListPlatform)+4,'Total',Bold_Number_format)
        worksheet_debt.write(5*i+8,len(ListPlatform)+4,Total_debt,Bold_Number_format)
        worksheet_debt.write(5*i+9,len(ListPlatform)+4,Total_saving,Bold_Number_format)
        worksheet_debt.write(5*i+10,len(ListPlatform)+4,Total_debt+Total_saving,Bold_Number_format)

    for k in range(1,Current_date.month+1):
        This_month = date(Current_date.year,k,1)
        query = con.execute("SELECT SUM(Amount_expenses)/%s FROM Expenses WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_expenses > 0",(exchange_rate_year(This_month),This_month+relativedelta(months=+1)))
        debt = query.fetchall()
        Name_month = calendar.month_name[This_month.month]
        Date = str(Name_month) + '-' + str(This_month.year)
        worksheet_debt.set_column('%s:%s'%(xl_col_to_name(k+1),xl_col_to_name(k+1)),len(Date ))
        worksheet_debt.write(1,k+1,Date,Bold_Number_format)
        query = con.execute("SELECT SUM(Amount_expenses)/%s FROM Expenses WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_expenses < 0 ",(exchange_rate_year(This_month),This_month+relativedelta(months=+1)))
        saving = query.fetchall()
        worksheet_debt.write(2,k+1,debt[0][0],Number_format)
        worksheet_debt.write(3,k+1,saving[0][0],Number_format)
        worksheet_debt.write_formula(4,k+1,"=%s3+%s4"%(xl_col_to_name(k+1),xl_col_to_name(k+1)),Bold_Number_format)
    for l in range(1,13):
        This_month = date(Date_N_1.year,l,1)
        query = con.execute("SELECT SUM(Amount_expenses)/%s FROM Expenses WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_expenses > 0",(exchange_rate_year(This_month),This_month+relativedelta(months=+1)))
        debt = query.fetchall()
        Name_month = calendar.month_name[This_month.month]
        Date = str(Name_month) + '-' + str(This_month.year)
        worksheet_debt.set_column('%s:%s'%(xl_col_to_name(l+1),xl_col_to_name(l+1)),len(Date ))
        worksheet_debt.write(6,l+1,Date,Bold_Number_format)
        query = con.execute("SELECT SUM(Amount_expenses)/%s FROM Expenses WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_expenses < 0",(exchange_rate_year(This_month),This_month+relativedelta(months=+1)))
        saving = query.fetchall()
        worksheet_debt.write(7,l+1,debt[0][0],Number_format)
        worksheet_debt.write(8,l+1,saving[0][0],Number_format)
        worksheet_debt.write_formula(9,l+1,"=%s8+%s9"%(xl_col_to_name(l+1),xl_col_to_name(l+1)),Bold_Number_format)

def CreateMonthlyBalance(Current_date,Date_N_1,workbook):
    con = db.pool.connect()
    worksheet_monthly_balance = workbook.add_worksheet("Monthly Balance")
    worksheet_monthly_balance.freeze_panes(3,2)

    number_format = workbook.add_format({'num_format' : '# ##0'})
    number_format_bold = workbook.add_format({'num_format' : '# ##0','bold':True})
    qualitive_info_format = workbook.add_format({"bg_color": '#DCE6F1'})
    Date_format = workbook.add_format({'num_format': 'mmm-yy','bg_color' : '#EBF1DE'})
    
######SELECT DATA########

    allDebt_situation = con.execute("SELECT Amount_expenses,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Expenses WHERE Month >= %s AND Ref_expenses = 'debt'",date(int(Current_date.year)-1,1,1)).fetchall()
    InfoSite = con.execute("SELECT Id_Site,Platform,Advisor FROM Sites").fetchall()

######WRITE DATA#########
    worksheet_monthly_balance.write('A3','Site',qualitive_info_format)
    worksheet_monthly_balance.write('B3','Platform',qualitive_info_format)
    worksheet_monthly_balance.write('C3','Advisor',qualitive_info_format)
    worksheet_monthly_balance.write("C1","Total Savings",number_format_bold)
    worksheet_monthly_balance.write("C2","Total Debts",number_format_bold)
    
    for i in range(len(InfoSite)):
        Column = 0

        debt_Site = list(filter(lambda row: row[1] == InfoSite[i][0], allDebt_situation))

        if InfoSite[i][1] == 'Dead':
            worksheet_monthly_balance.set_row(i+3,options={'hidden': True})
        worksheet_monthly_balance.write(i+3,Column,InfoSite[i][0],number_format)
        Column+=1
        worksheet_monthly_balance.write(i+3,Column,InfoSite[i][1])
        Column+=1
        worksheet_monthly_balance.write(i+3,Column,InfoSite[i][2])
        Column+=1

        start_date = date(Date_N_1.year,1,1)
        Loop = 0
        while start_date >= date(Date_N_1.year,1,1) and start_date<= Current_date:
            debtSituation = list(filter(lambda row: row[2] == str(start_date+relativedelta(months=+1)), debt_Site)) or [(0,0)]
            worksheet_monthly_balance.write(i+3,Loop+Column,debtSituation[0][0]/exchange_rate_year(start_date),number_format)
            start_date += relativedelta(months=+1)
            Loop +=1

        worksheet_monthly_balance.write_formula(i+3,Loop+4,'IF(%s%s > 0,"Debts",IF(%s%s<0,"Savings",""))'%(xl_col_to_name(Loop+2),i+4,xl_col_to_name(Loop+2),i+4))
    

    start_date = date(Date_N_1.year,1,1)
    Loop = 0 
    while start_date >= date(Date_N_1.year,1,1) and start_date<= Current_date:
        worksheet_monthly_balance.write(2,Loop+3,str(start_date.year) + '-' + str(start_date.month),Date_format)
        worksheet_monthly_balance.write_formula(0,Loop+3,"=SUMPRODUCT((%s4:%s%s<0)*(SUBTOTAL(9,OFFSET(%s4,ROW(%s4:%s%s)-MIN(ROW(%s4:%s%s)),0))))"%(xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3),number_format_bold)
        worksheet_monthly_balance.write_formula(1,Loop+3,"=SUMPRODUCT((%s4:%s%s>0)*(SUBTOTAL(9,OFFSET(%s4,ROW(%s4:%s%s)-MIN(ROW(%s4:%s%s)),0))))"%(xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3,xl_col_to_name(Loop+3),xl_col_to_name(Loop+3),len(InfoSite)+3),number_format_bold)
        start_date += relativedelta(months=+1)
        Loop += 1


    worksheet_monthly_balance.write(2,Loop+4,"Debt/Saving",number_format_bold)
    worksheet_monthly_balance.autofilter('A3:%s3'%(xl_col_to_name(Loop +2)))
    worksheet_monthly_balance.filter_column(1,'Platform <> Dead')

def CreatedocCollectionrate(Current_date,workbook):
    con = db.pool.connect()

    Gotolineformat = workbook.add_format({'text_wrap' : True})

    worksheet_recap = workbook.add_worksheet("CR")
    worksheet_recap.write(1,2,"Actual Invoice Listing",Gotolineformat)
    worksheet_recap.write(1,3,"Actual Cash collected",Gotolineformat)
    worksheet_recap.write(1,4,"C.R. inc. debt settlement",Gotolineformat)
    worksheet_recap.write(1,5,"C.R. inc. debt settlement N-1",Gotolineformat)
    if Current_date.year - 2 > 2019:
        worksheet_recap.write(1,6,"C.R. inc. debt settlement N-2",Gotolineformat)
    worksheet_recap.set_column('C:C',len("Actual Invoice Listing"))
    worksheet_recap.set_column('D:D',len("Actual Cash collected"))
    worksheet_recap.set_column('E:J',13.64)



    ListSiteActive = con.execute("""SELECT DISTINCT Id_Site FROM Sales""").fetchall()
    ListSiteActivePropre = [x[0] for x in ListSiteActive]
    List_Month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    # Query for Entrepreneur Contribution
    query = con.execute(
        """
        SELECT IFNULL(SUM(Amount_expenses),0), IFNULL(SUM(Paid),0), DATE_FORMAT(Month, '%%Y-%%m-%%d')
        FROM Expenses 
        WHERE Ref_expenses = 'entrepreneur_contribution'
        GROUP BY Month
        """
    )
    allEC = query.fetchall()

    query = con.execute(
        """
        SELECT SUM(Amount_expenses), SUM(Paid), YEAR(Month)
        FROM Expenses 
        WHERE Ref_expenses = 'entrepreneur_contribution'
        AND MONTH(Expenses.Month) <= %s
        GROUP BY YEAR(Month)
        """,
        (Current_date.month)
    )
    allEC_Year = query.fetchall()

    # Query for Consumables
    query = con.execute(
        """
        SELECT IFNULL(SUM(Amount_expenses),0), IFNULL(SUM(Paid),0),DATE_FORMAT(Month, '%%Y-%%m-%%d') 
        FROM Expenses 
        WHERE Ref_expenses IN ('stock_ts', 'bottle_invoice')
        GROUP BY Month
        """
    )
    allConsumable = query.fetchall()

    query = con.execute(
        """
        SELECT SUM(Amount_expenses), SUM(Paid),YEAR(Month)
        FROM Expenses 
        WHERE Ref_expenses IN ('stock_ts', 'bottle_invoice')
        AND MONTH(Expenses.Month) <= %s
        GROUP BY YEAR(Month)
        """,
        (Current_date.month)
    )
    allConsumable_Year = query.fetchall()

    # Query for Technical Interventions
    query = con.execute(
        """
        SELECT IFNULL(SUM(Amount_expenses),0), IFNULL(SUM(Paid),0),DATE_FORMAT(Month, '%%Y-%%m-%%d') 
        FROM Expenses 
        WHERE Ref_expenses IN ('technical intervention', 'water quality alert', 'delivery_program_fee')
        GROUP BY Month
        """
    )
    allTSIntervention = query.fetchall()

    query = con.execute(
        """
        SELECT IFNULL(SUM(Amount_expenses),0), IFNULL(SUM(Paid),0),YEAR(Month)
        FROM Expenses 
        WHERE Ref_expenses IN ('technical intervention', 'water quality alert', 'delivery_program_fee')
        GROUP BY YEAR(Month)
        """
    )
    allTSIntervention_Year = query.fetchall()
    

    # Query for Debt
    query = con.execute(
        """
        SELECT SUM(Amount_expenses), 
               LEAST(SUM(Amount_expenses), SUM(Paid)),DATE_FORMAT(Month, '%%Y-%%m-%%d')
        FROM Expenses 
        WHERE ((Ref_expenses = 'debt' AND Amount_expenses > 0)
                OR (Ref_expenses = 'adjustments' AND Paid > 0))
        GROUP BY Month
        """
    )
    alldebt = query.fetchall()

    query = con.execute(
        """
        SELECT SUM(Amount_expenses), 
               LEAST(SUM(Amount_expenses), SUM(Paid)),YEAR(Month)
        FROM Expenses 
        WHERE ((Ref_expenses = 'debt' AND Amount_expenses > 0)
                OR (Ref_expenses = 'adjustments' AND Paid > 0))
            AND MONTH(Month) <= %s
        GROUP BY YEAR(Month)
        """,
        (Current_date.month)
    )
    alldebt_Year = query.fetchall()

    #DATA TOTAL YEAR 
    Percentage_format = workbook.add_format({'num_format' : '0%','border' : 1,'bg_color' : '#E6B8B7'})
    Number_format = workbook.add_format({'num_format' : '# ### ##0','border' : 1,'bg_color' : '#E6B8B7'})
    
    EC = list(filter(lambda row: row[2] == Current_date.year, allEC_Year)) or [(0,0)]
    Consumable = list(filter(lambda row: row[2] == Current_date.year, allConsumable_Year)) or [(0,0)]
    TSIntervention = list(filter(lambda row: row[2] == Current_date.year, allTSIntervention_Year)) or [(0,0)]
    debt_jan = list(filter(lambda row: row[2] == str(date(Current_date.year,2,1)), alldebt)) or [(0,0)]
    debt_Year = list(filter(lambda row: row[2] == Current_date.year, alldebt_Year)) or [(0,0)]

    exchange_rate = exchange_rate_year(Current_date.year)
    
    worksheet_recap.merge_range(2,0,6,0,"YTD",Number_format)
    worksheet_recap.write(2,1,"EC",Number_format)
    worksheet_recap.write(3,1,"Consommable",Number_format)
    worksheet_recap.write(4,1,"TS Intervention",Number_format)
    worksheet_recap.write(5,1,"Debt",Number_format)
    worksheet_recap.write(6,1,"Total",Number_format)
    worksheet_recap.write(2,2,EC[0][0]/exchange_rate,Number_format)
    worksheet_recap.write(2,3,EC[0][1]/exchange_rate,Number_format)
    worksheet_recap.write(2,4,None,Percentage_format)
    worksheet_recap.write(3,2,Consumable[0][0]/exchange_rate,Number_format)
    worksheet_recap.write(3,3,Consumable[0][1]/exchange_rate,Number_format)
    worksheet_recap.write(3,4,None,Percentage_format)
    worksheet_recap.write(4,2,TSIntervention[0][0]/exchange_rate,Number_format)
    worksheet_recap.write(4,3,TSIntervention[0][1]/exchange_rate,Number_format)
    worksheet_recap.write(4,4,None,Percentage_format)
    worksheet_recap.write_formula(5,2,"=C3-D3+C4-D4+C5-D5+%s"%(debt_jan[0][0]/exchange_rate),Number_format)
    worksheet_recap.write_formula(5,3,"%s"%(debt_Year[0][1]/exchange_rate),Number_format)
    worksheet_recap.write(5,4,None,Percentage_format)
    worksheet_recap.write_formula(6,2,"=C3+C4+C5+%s"%(debt_jan[0][0]/exchange_rate),Number_format)
    worksheet_recap.write_formula(6,3,"=D3+D4+D5+D6",Number_format)
    worksheet_recap.write_formula(6,4,"=D7/C7",Percentage_format)
    
    #CR 2 previous year
    for k in range(1,3):
        EC = list(filter(lambda row: row[2] == Current_date.year-k, allEC_Year)) or [(0,0)]
        Consumable = list(filter(lambda row: row[2] == Current_date.year-k, allConsumable_Year)) or [(0,0)]
        TSIntervention = list(filter(lambda row: row[2] == Current_date.year-k, allTSIntervention_Year)) or [(0,0)]
        debt_jan = list(filter(lambda row: row[2] == str(date(Current_date.year-k,1,1)), alldebt)) or [(0,0)]
        debt_Year = list(filter(lambda row: row[2] == Current_date.year-k, alldebt_Year)) or [(0,0)]

        worksheet_recap.write(2,4+k,None,Percentage_format)
        worksheet_recap.write(3,4+k,None,Percentage_format)
        worksheet_recap.write(4,4+k,None,Percentage_format)
        worksheet_recap.write(5,4+k,None,Percentage_format)
        worksheet_recap.write_formula(6,4+k,'=(%s+%s+%s+%s)/(%s+%s+%s+%s)'%(EC[0][1],Consumable[0][1],TSIntervention[0][1],debt_Year[0][1],EC[0][0],Consumable[0][0],TSIntervention[0][0],debt_jan[0][0]),Percentage_format)


    #INFO MONTH BY MONTH 
    for j in range(1,int(Current_date.month)+1):
        EC = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), allEC)) or [(0,0)]
        Consumable = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), allConsumable)) or [(0,0)]
        TSIntervention = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), allTSIntervention)) or [(0,0)]
        debt = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)+ relativedelta(months=1)), alldebt)) or [(0,0)]
        debt_paid = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), alldebt)) or [(0,0)] #month before
        
        if j%2 ==0 and j != 0:
            color = '#D9D9D9'
        elif j%2 ==1:
            color = '#FCD5B4'
        
        Percentage_format = workbook.add_format({'num_format' : '0%','border' : 1,'bg_color' : '%s'%(color)})
        Number_format = workbook.add_format({'num_format' : '# ### ##0','border' : 1,'bg_color' : '%s'%(color)})
        
        worksheet_recap.merge_range(5*j+2,0,5*j+6,0,"%s-%s"%(str(List_Month[j-1]),Current_date.year),Number_format)
        worksheet_recap.write(5*j+2,1,'EC',Number_format)
        worksheet_recap.write(5*j+3,1,'Consommable',Number_format)
        worksheet_recap.write(5*j+4,1,'TS Intervention',Number_format)
        worksheet_recap.write(5*j+5,1,'Debt',Number_format)
        worksheet_recap.write(5*j+6,1,'Total',Number_format)

        worksheet_recap.write(5*j+2,2,EC[0][0]/exchange_rate,Number_format)
        worksheet_recap.write(5*j+2,3,EC[0][1]/exchange_rate,Number_format)

        worksheet_recap.write(5*j+3,2,Consumable[0][0]/exchange_rate,Number_format)
        worksheet_recap.write(5*j+3,3,Consumable[0][1]/exchange_rate,Number_format)

        worksheet_recap.write(5*j+4,2,TSIntervention[0][0]/exchange_rate,Number_format)
        print(TSIntervention)
        worksheet_recap.write(5*j+4,3,TSIntervention[0][1]/exchange_rate,Number_format)

        worksheet_recap.write(5*j+5,2,debt[0][0]/exchange_rate,Number_format)
        worksheet_recap.write_formula(5*j+5,3,"IFERROR(%s/%s,0)"%(debt_paid[0][1],exchange_rate),Number_format)

        worksheet_recap.write(5*j+6,2,(EC[0][0]+Consumable[0][0]+TSIntervention[0][0])/exchange_rate,Number_format)
        worksheet_recap.write(5*j+6,3,(EC[0][1]+Consumable[0][1]+TSIntervention[0][1])/exchange_rate,Number_format)

        worksheet_recap.write(5*j+2,4,None,Percentage_format)
        worksheet_recap.write(5*j+3,4,None,Percentage_format)
        worksheet_recap.write(5*j+4,4,None,Percentage_format)
        worksheet_recap.write(5*j+5,4,None,Percentage_format)
        if j == 1:
            worksheet_recap.write_formula(5*j+6,4,"(D%s+D%s)/(C%s+C%s)"%(5*j+7,5*j+6,5*j+7,5*j+6),Percentage_format)
        else:
            worksheet_recap.write_formula(5*j+6,4,"(D%s+D%s)/C%s"%(5*j+7,5*j+6,5*j+7),Percentage_format)

def KPIFinanceReport(Current_date,Date_janv,exchange_rate,workbook):
    worksheet = workbook.add_worksheet("KPI")
    con= db.pool.connect()
    Platform_List = con.execute("SELECT DISTINCT Code_Platform FROM Platform").fetchall()
    Date_janv = Date_janv - relativedelta(months=1)
    Tier = ExcelKPI.KPIFormat(workbook,worksheet,Current_date,Date_janv,2018,Platform_List)
    ExcelKPI.KPITotInc(workbook,worksheet,2,Current_date,Date_janv,Tier,Platform_List,exchange_rate,False)
    ExcelKPI.KPITotInc(workbook,worksheet,11,Current_date,Date_janv,Tier,Platform_List,exchange_rate,True)
    ExcelKPI.KPISalaryEnt(workbook,worksheet,20,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPIPL(workbook,worksheet,29,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPIDebt(workbook,worksheet,38,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPISaving(workbook,worksheet,48,Current_date,Date_janv,Tier,Platform_List,exchange_rate)
    ExcelKPI.KPICollectionRate(workbook,worksheet,58,Current_date,Date_janv,Tier,Platform_List,exchange_rate,Hide=0)


def LaunchExcelFinanceReport(Date,ListTier,exchange_rate):
    Current_date = Date
    Date_N_1 = Date - relativedelta(months =+12)

    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir()+'/Finance Report '+Year+'-'+Month+'.xlsm'
    if os.path.exists(filepath):
       os.remove(filepath)
    workbook = xlsxwriter.Workbook(filepath)
    Date_janv = date(Current_date.year,1,1)
    Worksheetdebt_name = "Graph"
    ListSiteActive = listSiteStillActive(Current_date,Date_N_1)
    
    CreatedocCollectionrate(Current_date,workbook)
    CreateSummary(Current_date,exchange_rate,workbook)
    CreateMonthlyBalance(Current_date, Date_N_1,workbook)
    CreateDebtEvolution(Current_date,Date_N_1,workbook)
    worksheet_graph = workbook.add_worksheet(Worksheetdebt_name)
    GraphDebtEvolution(workbook,worksheet_graph,Worksheetdebt_name,0,0,4,25,Current_date,"Total")
    KPIFinanceReport(Current_date,Date_janv,exchange_rate,workbook)
    DataConsumableSold(workbook,exchange_rate,Current_date)
    SiteAnalysis(ListTier,ListSiteActive,workbook,Current_date,True)
    workbook.close()

if __name__ == '__main__':
    LaunchExcelCreationBalance()
