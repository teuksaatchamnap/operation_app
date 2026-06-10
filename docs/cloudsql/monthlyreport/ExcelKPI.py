import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta, datetime
from calendar import monthrange
import db
import xlsxwriter
from monthlyreport.Functionutils import NewCalculTier,CategoryExpenses
import tempfile
import calendar
from dateutil.relativedelta import *

def KPIFormat(workbook,worksheet,Current_date,Date_1,YearStart,Platform_List):

    Bold_format = workbook.add_format({'bold':True})
    Italic_format = workbook.add_format({'italic':True})

    NbYear = Current_date.year - YearStart +1
    Col = 0
    Tier = []
    worksheet.set_column('A:BA',13)
    worksheet.set_column("A:A",15)
    worksheet.set_column("B:B",11)
    worksheet.freeze_panes(2,2)
    worksheet.set_zoom(70)
    
    for i in range(NbYear):
        worksheet.write(0,2+Col+len(Platform_List),Current_date.year-i)
        worksheet.write(1,2+Col+len(Platform_List),"Total",Bold_format)
        if i >0:
            worksheet.set_column('%s:%s'%(xl_col_to_name(2+Col),xl_col_to_name(1+Col+len(Platform_List))),13,None,{'level':1,'hidden':True})
        for k in range(len(Platform_List)):
            worksheet.write(1,2+Col,Platform_List[k][0],Bold_format)
            Col += 1
        worksheet.set_column('%s:%s'%(xl_col_to_name(2+Col),xl_col_to_name(2+Col)),14)
        worksheet.set_column('%s:%s'%(xl_col_to_name(3+Col),xl_col_to_name(3+Col)),2)
        Col +=2
        

        Tier.append(NewCalculTier(date(Current_date.year-i,Current_date.month,1)))
    return(Tier)

def KPIBeneficiaries(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List):
    con = db.pool.connect()

    Date_1 = Current_date - relativedelta(months=+12) #ONLY FOR BENEFICIARIES BECAUSE CALCULATED FOR THE LAST 12 MONTHS ALWAYS

    Beneficiaries_format = workbook.add_format({'num_format' : '# ### ### ##0','border':1})
    Beneficiaries_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    Beneficiaries_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",Beneficiaries_bold_format)
    worksheet.write(Line+1,1,"Tier 1",Beneficiaries_bold_format)
    worksheet.write(Line+2,1,"Tier 2",Beneficiaries_bold_format)
    worksheet.write(Line+3,1,"Tier 3",Beneficiaries_bold_format)
    worksheet.write(Line+4,1,"New",Beneficiaries_bold_format)
    worksheet.write(Line+5,1,"Reopen",Beneficiaries_bold_format)
    worksheet.write(Line+6,1,"Inactive",Beneficiaries_bold_format)
    worksheet.write(Line+7,1,"Total",Beneficiaries_bold_format)
    worksheet.merge_range(Line,0,Line+7,0,"Consumers \n%s %s - %s %s"%(calendar.month_name[(Date_1+relativedelta(months=+1)).month],(Date_1+relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),Beneficiaries_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        Beneficiaries = con.execute("SELECT Beneficiaries,Old_Platform,Beneficiaries.Id_Site FROM Beneficiaries INNER JOIN Sites ON Beneficiaries.Id_Site = Sites.Id_Site WHERE Month = %s GROUP BY Old_Platform,Beneficiaries.Id_Site",(Current_date-relativedelta(months=+12*m))).fetchall()
        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            BeneficiariesPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], Beneficiaries))
            BeneficiariesTot = 0
            for j in range(Nb_of_tier):
                BeneficiariesTotPlat = 0
                for k in range(len(BeneficiariesPlatform)):

                    if BeneficiariesPlatform[k][2] in Tier1[1][j]:
                        BeneficiariesTotPlat += BeneficiariesPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),BeneficiariesTotPlat,Beneficiaries_format)
                BeneficiariesTot += BeneficiariesTotPlat
                Total_per_tier[j] += BeneficiariesTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],Beneficiaries_bold_format)


            worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2),BeneficiariesTot,Beneficiaries_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),Beneficiaries_bold_format)
    return("ok")

def KPINbSite(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List):
    con = db.pool.connect()

    NbSite_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    NbSite_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbSite_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",NbSite_bold_format)
    worksheet.write(Line+1,1,"Tier 1",NbSite_bold_format)
    worksheet.write(Line+2,1,"Tier 2",NbSite_bold_format)
    worksheet.write(Line+3,1,"Tier 3",NbSite_bold_format)
    worksheet.write(Line+4,1,"New",NbSite_bold_format)
    worksheet.write(Line+5,1,"Reopen",NbSite_bold_format)
    worksheet.write(Line+6,1,"Total",NbSite_bold_format)
    worksheet.write(Line+7,1,"Inactive",NbSite_bold_format)
    worksheet.write(Line+8,1,"Closed",NbSite_bold_format)
    worksheet.merge_range(Line,0,Line+8,0,"Nb of Sites \n%s %s - %s %s"%(calendar.month_name[(Date_1+relativedelta(months=+1)).month],(Date_1+relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),NbSite_Title)

    Nb_of_tier = len(Tier[0][1])-1

    for m in range(len(Tier)):
        NbSite = con.execute("SELECT DISTINCT Sales.Id_Site,1,Old_Platform FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Sales.Id_Site <> %s",'EBM').fetchall()
        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            NbSitePlatform = list(filter(lambda row: row[2] == Platform_List[i][0], NbSite))
            NbSiteTot = 0
            for j in range(Nb_of_tier):
                NbSiteTotPlat = 0
                for k in range(len(NbSitePlatform)):
                    if NbSitePlatform[k][0] in Tier1[1][j]:
                        NbSiteTotPlat += NbSitePlatform[k][1] or 0
                if j <= Nb_of_tier - 3:
                    worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),NbSiteTotPlat,NbSite_format)
                    NbSiteTot += NbSiteTotPlat
                    Total_per_tier[j] += NbSiteTotPlat
                    worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],NbSite_bold_format)
                else:
                    worksheet.write(Line+j+1,(m*(len(Platform_List)+2)+i+2),NbSiteTotPlat,NbSite_format)
                    Total_per_tier[j] += NbSiteTotPlat
                    worksheet.write(Line+j+1,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],NbSite_bold_format)


            worksheet.write(Line+len(Tier1[1])-3,(m*(len(Platform_List)+2)+i+2),NbSiteTot,NbSite_bold_format)
        worksheet.write(Line+Nb_of_tier-2,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier)-Total_per_tier[-1]-Total_per_tier[-2],NbSite_bold_format)
    return("ok")

def KPINbSitePercentage(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List):
    con = db.pool.connect()

    NbSitePercentage_format = workbook.add_format({'num_format' : '0%','border':1})
    NbSitePercentage_bold_format = workbook.add_format({'num_format' : '0%','bold':True, 'border': 1})
    NbSite_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbSite_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",NbSitePercentage_bold_format)
    worksheet.write(Line+1,1,"Tier 1",NbSitePercentage_bold_format)
    worksheet.write(Line+2,1,"Tier 2",NbSitePercentage_bold_format)
    worksheet.write(Line+3,1,"Tier 3",NbSitePercentage_bold_format)
    worksheet.write(Line+4,1,"New",NbSitePercentage_bold_format)
    worksheet.write(Line+5,1,"Reopen",NbSitePercentage_bold_format)
    worksheet.write(Line+6,1,"Inactive",NbSitePercentage_bold_format)
    worksheet.write(Line+7,1,"Total",NbSitePercentage_bold_format)
    worksheet.merge_range(Line,0,Line+7,0,"Nb of Sites %% \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),NbSite_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        NbSitePercentage = con.execute("SELECT DISTINCT 1,Old_Platform,Id_Site FROM Sites WHERE Id_Site <> %s ",('EBM')).fetchall()
        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            NbSitePercentagePlatform = list(filter(lambda row: row[1] == Platform_List[i][0], NbSitePercentage))
            NbSitePercentageTot = 0
            for j in range(Nb_of_tier):
                NbSitePercentageTotPlat = 0
                for k in range(len(NbSitePercentagePlatform)):

                    if NbSitePercentagePlatform[k][2] in Tier1[1][j]:
                        NbSitePercentageTotPlat += NbSitePercentagePlatform[k][0] or 0

                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(NbSitePercentageTotPlat,xl_rowcol_to_cell(Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2))),NbSitePercentage_format)
                NbSitePercentageTot += NbSitePercentageTotPlat
                Total_per_tier[j] += NbSitePercentageTotPlat
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/%s,0)"%(Total_per_tier[j],xl_rowcol_to_cell(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2))),NbSitePercentage_bold_format)


            worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2),NbSitePercentageTot,NbSite_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),NbSite_bold_format)
    return("ok")

def KPIBotDay(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,WithSchool,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    Bot_day_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    Bot_day_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    Bot_day_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",Bot_day_bold_format)
    worksheet.write(Line+1,1,"Tier 1",Bot_day_bold_format)
    worksheet.write(Line+2,1,"Tier 2",Bot_day_bold_format)
    worksheet.write(Line+3,1,"Tier 3",Bot_day_bold_format)
    worksheet.write(Line+4,1,"New",Bot_day_bold_format)
    worksheet.write(Line+5,1,"Reopen",Bot_day_bold_format)
    worksheet.write(Line+6,1,"Inactive",Bot_day_bold_format)
    worksheet.write(Line+7,1,"Closed",Bot_day_bold_format)
    worksheet.write(Line+8,1,"Total",Bot_day_bold_format)
    if WithSchool:
        worksheet.merge_range(Line,0,Line+8,0,"Bot/day inc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),Bot_day_Title)
    else:
        worksheet.merge_range(Line,0,Line+8,0,"Bot/day exc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),Bot_day_Title)

    Nb_of_tier = len(Tier[0][1])-1

    for m in range(len(Tier)):
        if WithSchool:
            Bot_day = con.execute("SELECT SUM(Total_Sales-Bottle_Sales),Old_Platform,Sales.Id_Site,SUM(Number_Open_Days) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        else:
            Bot_day = con.execute("SELECT SUM(Total_Sales-WiS_Sales-Bottle_Sales),Old_Platform,Sales.Id_Site,SUM(Number_Open_Days) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()

        Tier1 = Tier[m]
        TotalBot_per_tier = [0]*Nb_of_tier
        TotalSite_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            Bot_dayPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], Bot_day))
            Bot_dayTot = 0
            NbSiteTot = 0
            for j in range(Nb_of_tier):
                Bot_dayTotPlat = 0
                NbSiteTotPlat = 0
                for k in range(len(Bot_dayPlatform)):

                    if Bot_dayPlatform[k][2] in Tier1[1][j]:
                        Bot_dayTotPlat += float(Bot_dayPlatform[k][0])/float(Bot_dayPlatform[k][3]) or 0
                        NbSiteTotPlat += 1

                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(Bot_dayTotPlat,NbSiteTotPlat),Bot_day_format)
                Bot_dayTot += Bot_dayTotPlat
                NbSiteTot += NbSiteTotPlat
                TotalBot_per_tier[j] += Bot_dayTotPlat
                TotalSite_per_tier[j] += NbSiteTotPlat
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/%s,0)"%(TotalBot_per_tier[j],TotalSite_per_tier[j]),Bot_day_bold_format)


            worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(Bot_dayTot,NbSiteTot),Bot_day_bold_format)
        worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/%s,0)"%(sum(TotalBot_per_tier),sum(TotalSite_per_tier)),Bot_day_bold_format)
    return("ok")

def KPITotBot(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,WithSchool,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    TotBot_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    TotBot_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    TotBot_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",TotBot_bold_format)
    worksheet.write(Line+1,1,"Tier 1",TotBot_bold_format)
    worksheet.write(Line+2,1,"Tier 2",TotBot_bold_format)
    worksheet.write(Line+3,1,"Tier 3",TotBot_bold_format)
    worksheet.write(Line+4,1,"New",TotBot_bold_format)
    worksheet.write(Line+5,1,"Reopen",TotBot_bold_format)
    worksheet.write(Line+6,1,"Inactive",TotBot_bold_format)
    worksheet.write(Line+7,1,"Total",TotBot_bold_format)
    if WithSchool:
        worksheet.merge_range(Line,0,Line+7,0,"Total Sales (Bot) inc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),TotBot_Title)
    else:
        worksheet.merge_range(Line,0,Line+7,0,"Total Sales (Bot) exc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),TotBot_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        if WithSchool:
            TotBot = con.execute("SELECT SUM(Total_Sales - Bottle_sales),Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        else:
            TotBot = con.execute("SELECT SUM(Total_Sales - Bottle_sales-WiS_Sales),Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()

        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            TotBotPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], TotBot))
            TotBotTot = 0
            for j in range(Nb_of_tier):
                TotBotTotPlat = 0
                for k in range(len(TotBotPlatform)):

                    if TotBotPlatform[k][2] in Tier1[1][j]:
                        TotBotTotPlat += TotBotPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),TotBotTotPlat,TotBot_format)
                TotBotTot += TotBotTotPlat
                Total_per_tier[j] += TotBotTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],TotBot_bold_format)


            worksheet.write(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),TotBotTot,TotBot_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),TotBot_bold_format)
    return("ok")

def KPITotBotGrowth(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,WithSchool=False,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    Growth_format = workbook.add_format({'num_format' : '+0%;-0%','border':1})
    Growth_bold_format = workbook.add_format({'num_format' : '+0%;-0%','bold':True, 'border': 1})
    Growth_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",Growth_bold_format)
    worksheet.write(Line+1,1,"Tier 1",Growth_bold_format)
    worksheet.write(Line+2,1,"Tier 2",Growth_bold_format)
    worksheet.write(Line+3,1,"Tier 3",Growth_bold_format)
    worksheet.write(Line+4,1,"New",Growth_bold_format)
    worksheet.write(Line+5,1,"Reopen",Growth_bold_format)
    worksheet.write(Line+6,1,"Inactive",Growth_bold_format)
    worksheet.write(Line+7,1,"Closed",Growth_bold_format)
    worksheet.write(Line+8,1,"Total",Growth_bold_format)
    if WithSchool:
        worksheet.merge_range(
            Line,0,Line+8,0,
            "Total Sales (Bot) inc. WinS vs N-1 %% \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),
            Growth_Title
        )
    else:
        worksheet.merge_range(
            Line,0,Line+8,0,
            "Total Sales (Bot) exc. WinS vs N-1 %% \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),
            Growth_Title
        )

    # Include Closed, exclude only Dead
    Nb_of_tier = len(Tier[0][1])-1

    for m in range(len(Tier)):
        if WithSchool:
            TotBot_N = con.execute(
                "SELECT SUM(Total_Sales - Bottle_sales),Old_Platform,Sales.Id_Site "
                "FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                "WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",
                (Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))
            ).fetchall()
        else:
            TotBot_N = con.execute(
                "SELECT SUM(Total_Sales - Bottle_sales - WiS_Sales),Old_Platform,Sales.Id_Site "
                "FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                "WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",
                (Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))
            ).fetchall()

        # For this KPI, bucket N and N-1 using the same tiers (tiers of year N).
        TierN = Tier[m]
        Tier1 = TierN

        if (m+1) < len(Tier):
            if WithSchool:
                TotBot_N_1 = con.execute(
                    "SELECT SUM(Total_Sales - Bottle_sales),Old_Platform,Sales.Id_Site "
                    "FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                    "WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",
                    (Current_date-relativedelta(months=+12*(m+1)),Date_1-relativedelta(months=+12*(m+1)))
                ).fetchall()
            else:
                TotBot_N_1 = con.execute(
                    "SELECT SUM(Total_Sales - Bottle_sales - WiS_Sales),Old_Platform,Sales.Id_Site "
                    "FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                    "WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",
                    (Current_date-relativedelta(months=+12*(m+1)),Date_1-relativedelta(months=+12*(m+1)))
                ).fetchall()
        else:
            TotBot_N_1 = []

        Total_n_per_tier = [0]*Nb_of_tier
        Total_n1_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            TotBotNPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], TotBot_N))
            TotBotN1Platform = list(filter(lambda row: row[1] == Platform_List[i][0], TotBot_N_1))

            TotN = 0
            TotN1 = 0
            for j in range(Nb_of_tier):
                TotNPlat = 0
                TotN1Plat = 0
                for k in range(len(TotBotNPlatform)):
                    if TotBotNPlatform[k][2] in TierN[1][j]:
                        TotNPlat += TotBotNPlatform[k][0] or 0
                for k in range(len(TotBotN1Platform)):
                    if TotBotN1Platform[k][2] in TierN[1][j]:
                        TotN1Plat += TotBotN1Platform[k][0] or 0

                worksheet.write_formula(
                    Line+j,(m*(len(Platform_List)+2)+i+2),
                    "=IFERROR((%s-%s)/%s,0)"%(TotNPlat,TotN1Plat,TotN1Plat),
                    Growth_format
                )
                TotN += TotNPlat
                TotN1 += TotN1Plat
                Total_n_per_tier[j] += TotNPlat
                Total_n1_per_tier[j] += TotN1Plat
                worksheet.write_formula(
                    Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),
                    "=IFERROR((%s-%s)/%s,0)"%(Total_n_per_tier[j],Total_n1_per_tier[j],Total_n1_per_tier[j]),
                    Growth_bold_format
                )

            worksheet.write_formula(
                Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2),
                "=IFERROR((%s-%s)/%s,0)"%(TotN,TotN1,TotN1),
                Growth_bold_format
            )

        worksheet.write_formula(
            Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),
            "=IFERROR((%s-%s)/%s,0)"%(sum(Total_n_per_tier),sum(Total_n1_per_tier),sum(Total_n1_per_tier)),
            Growth_bold_format
        )
    return("ok")

def KPITotBotLikeForLike(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(8):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    # LFL KPIs: don't display "New" and "Inactive" categories.
    worksheet.set_row(Line+4, None, None, {'level': 1, 'hidden': True})
    worksheet.set_row(Line+6, None, None, {'level': 1, 'hidden': True})

    TotBot_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    TotBot_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    TotBot_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",TotBot_bold_format)
    worksheet.write(Line+1,1,"Tier 1",TotBot_bold_format)
    worksheet.write(Line+2,1,"Tier 2",TotBot_bold_format)
    worksheet.write(Line+3,1,"Tier 3",TotBot_bold_format)
    worksheet.write(Line+5,1,"Reopen",TotBot_bold_format)
    worksheet.write(Line+7,1,"Total",TotBot_bold_format)
    worksheet.merge_range(
        Line,0,Line+7,0,
        "Total Sales (Bot) LFL exc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),
        TotBot_Title
    )

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        # Like-for-Like sites definition: sites that have sales in January of the analyzed year.
        analyzed_year = (Current_date - relativedelta(months=+12*m)).year - 1
        reference_month = date(analyzed_year, 1, 1)
        lfl_sites = con.execute(
            "SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL",
            (reference_month,)
        ).fetchall()
        lfl_site_ids = [row[0] for row in lfl_sites]
        if not lfl_site_ids:
            lfl_site_ids = ['EBM']

        TotBot = con.execute(
            "SELECT SUM(Total_Sales - Bottle_sales - WiS_Sales),Old_Platform,Sales.Id_Site "
            "FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
            "WHERE Month <= %s AND Month > %s AND Sales.Id_Site IN %s "
            "GROUP BY Old_Platform,Sales.Id_Site",
            (Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m),tuple(lfl_site_ids))
        ).fetchall()

        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            TotBotPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], TotBot))
            TotBotTot = 0
            for j in range(Nb_of_tier):
                TotBotTotPlat = 0
                for k in range(len(TotBotPlatform)):
                    if TotBotPlatform[k][2] in Tier1[1][j]:
                        TotBotTotPlat += TotBotPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),TotBotTotPlat,TotBot_format)
                TotBotTot += TotBotTotPlat
                Total_per_tier[j] += TotBotTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],TotBot_bold_format)

            worksheet.write(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),TotBotTot,TotBot_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),TotBot_bold_format)
    return("ok")

def KPITotBotLikeForLikeGrowth(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(8):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    # LFL KPIs: don't display "New" and "Inactive" categories.
    worksheet.set_row(Line+4, None, None, {'level': 1, 'hidden': True})
    worksheet.set_row(Line+6, None, None, {'level': 1, 'hidden': True})

    Growth_format = workbook.add_format({'num_format' : '+0%;-0%','border':1})
    Growth_bold_format = workbook.add_format({'num_format' : '+0%;-0%','bold':True, 'border': 1})
    Growth_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",Growth_bold_format)
    worksheet.write(Line+1,1,"Tier 1",Growth_bold_format)
    worksheet.write(Line+2,1,"Tier 2",Growth_bold_format)
    worksheet.write(Line+3,1,"Tier 3",Growth_bold_format)
    worksheet.write(Line+5,1,"Reopen",Growth_bold_format)
    worksheet.write(Line+7,1,"Total",Growth_bold_format)
    worksheet.merge_range(
        Line,0,Line+7,0,
        "Total Sales (Bot) LFL exc. WinS vs N-1 %% \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),
        Growth_Title
    )

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        # IMPORTANT: N and N-1 must use the exact same LFL list.
        analyzed_year = (Current_date - relativedelta(months=+12*m)).year - 1
        reference_month = date(analyzed_year, 1, 1)
        lfl_sites = con.execute(
            "SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL",
            (reference_month,)
        ).fetchall()
        lfl_site_ids = [row[0] for row in lfl_sites]
        if not lfl_site_ids:
            lfl_site_ids = ['EBM']

        TotBot_N = con.execute(
            "SELECT SUM(Total_Sales - Bottle_sales - WiS_Sales),Old_Platform,Sales.Id_Site "
            "FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
            "WHERE Month <= %s AND Month > %s AND Sales.Id_Site IN %s "
            "GROUP BY Old_Platform,Sales.Id_Site",
            (Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m),tuple(lfl_site_ids))
        ).fetchall()

        TotBot_N_1 = con.execute(
            "SELECT SUM(Total_Sales - Bottle_sales - WiS_Sales),Old_Platform,Sales.Id_Site "
            "FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
            "WHERE Month <= %s AND Month > %s AND Sales.Id_Site IN %s "
            "GROUP BY Old_Platform,Sales.Id_Site",
            (Current_date-relativedelta(months=+12*(m+1)),Date_1-relativedelta(months=+12*(m+1)),tuple(lfl_site_ids))
        ).fetchall()

        Tier1 = Tier[m]
        Total_n_per_tier = [0]*Nb_of_tier
        Total_n1_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            TotBotNPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], TotBot_N))
            TotBotN1Platform = list(filter(lambda row: row[1] == Platform_List[i][0], TotBot_N_1))

            TotN = 0
            TotN1 = 0
            for j in range(Nb_of_tier):
                TotNPlat = 0
                TotN1Plat = 0
                for k in range(len(TotBotNPlatform)):
                    if TotBotNPlatform[k][2] in Tier1[1][j]:
                        TotNPlat += TotBotNPlatform[k][0] or 0
                for k in range(len(TotBotN1Platform)):
                    if TotBotN1Platform[k][2] in Tier1[1][j]:
                        TotN1Plat += TotBotN1Platform[k][0] or 0

                worksheet.write_formula(
                    Line+j,(m*(len(Platform_List)+2)+i+2),
                    "=IFERROR((%s-%s)/%s,0)"%(TotNPlat,TotN1Plat,TotN1Plat),
                    Growth_format
                )
                TotN += TotNPlat
                TotN1 += TotN1Plat
                Total_n_per_tier[j] += TotNPlat
                Total_n1_per_tier[j] += TotN1Plat
                worksheet.write_formula(
                    Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),
                    "=IFERROR((%s-%s)/%s,0)"%(Total_n_per_tier[j],Total_n1_per_tier[j],Total_n1_per_tier[j]),
                    Growth_bold_format
                )

            worksheet.write_formula(
                Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),
                "=IFERROR((%s-%s)/%s,0)"%(TotN,TotN1,TotN1),
                Growth_bold_format
            )

        worksheet.write_formula(
            Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),
            "=IFERROR((%s-%s)/%s,0)"%(sum(Total_n_per_tier),sum(Total_n1_per_tier),sum(Total_n1_per_tier)),
            Growth_bold_format
        )
    return("ok")

def KPITotLit(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,WithSchool,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    TotBot_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    TotBot_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    TotBot_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",TotBot_bold_format)
    worksheet.write(Line+1,1,"Tier 1",TotBot_bold_format)
    worksheet.write(Line+2,1,"Tier 2",TotBot_bold_format)
    worksheet.write(Line+3,1,"Tier 3",TotBot_bold_format)
    worksheet.write(Line+4,1,"New",TotBot_bold_format)
    worksheet.write(Line+5,1,"Reopen",TotBot_bold_format)
    worksheet.write(Line+6,1,"Inactive",TotBot_bold_format)
    worksheet.write(Line+7,1,"Total",TotBot_bold_format)
    if WithSchool:
        worksheet.merge_range(Line,0,Line+7,0,"Total Sales (Litres) inc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),TotBot_Title)
    else:
        worksheet.merge_range(Line,0,Line+7,0,"Total Sales (Litres) exc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),TotBot_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        if WithSchool:
            TotBot = con.execute("SELECT SUM(Total_Sales - Bottle_sales)*20,Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        else:
            TotBot = con.execute("SELECT SUM(Total_Sales - Bottle_sales-WiS_Sales)*20,Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()

        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            TotBotPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], TotBot))
            TotBotTot = 0
            for j in range(Nb_of_tier):
                TotBotTotPlat = 0
                for k in range(len(TotBotPlatform)):

                    if TotBotPlatform[k][2] in Tier1[1][j]:
                        TotBotTotPlat += TotBotPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),TotBotTotPlat,TotBot_format)
                TotBotTot += TotBotTotPlat
                Total_per_tier[j] += TotBotTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],TotBot_bold_format)


            worksheet.write(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),TotBotTot,TotBot_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),TotBot_bold_format)
    return("ok")

def KPITotInc(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate,WithSchool,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    TotInc_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    TotInc_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    TotInc_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",TotInc_bold_format)
    worksheet.write(Line+1,1,"Tier 1",TotInc_bold_format)
    worksheet.write(Line+2,1,"Tier 2",TotInc_bold_format)
    worksheet.write(Line+3,1,"Tier 3",TotInc_bold_format)
    worksheet.write(Line+4,1,"New",TotInc_bold_format)
    worksheet.write(Line+5,1,"Reopen",TotInc_bold_format)
    worksheet.write(Line+6,1,"Inactive",TotInc_bold_format)
    worksheet.write(Line+7,1,"Total",TotInc_bold_format)
    if WithSchool:
        worksheet.merge_range(Line,0,Line+7,0,"Total Sales ($) inc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),TotInc_Title)
    else:
        worksheet.merge_range(Line,0,Line+7,0,"Total Sales ($) exc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),TotInc_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        if WithSchool:
            TotInc = con.execute("SELECT SUM(Total_Income)/%s,Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",(exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        else:
            TotInc = con.execute("SELECT SUM(Total_Income-WiS_Income)/%s,Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Sales.Id_Site",(exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()

        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            TotIncPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], TotInc))
            TotIncTot = 0
            for j in range(Nb_of_tier):
                TotIncTotPlat = 0
                for k in range(len(TotIncPlatform)):

                    if TotIncPlatform[k][2] in Tier1[1][j]:
                        TotIncTotPlat += TotIncPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),TotIncTotPlat,TotInc_format)
                TotIncTot += TotIncTotPlat
                Total_per_tier[j] += TotIncTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],TotInc_bold_format)


            worksheet.write(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),TotIncTot,TotInc_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),TotInc_bold_format)
    return("ok")

def KPIPrice(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate,WithSchool,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    Price_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    Price_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    Price_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",Price_bold_format)
    worksheet.write(Line+1,1,"Tier 1",Price_bold_format)
    worksheet.write(Line+2,1,"Tier 2",Price_bold_format)
    worksheet.write(Line+3,1,"Tier 3",Price_bold_format)
    worksheet.write(Line+4,1,"New",Price_bold_format)
    worksheet.write(Line+5,1,"Reopen",Price_bold_format)
    worksheet.write(Line+6,1,"Inactive",Price_bold_format)
    worksheet.write(Line+7,1,"Total",Price_bold_format)
    if WithSchool:
        worksheet.merge_range(Line,0,Line+7,0,"Price (Riels) inc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),Price_Title)
    else:
        worksheet.merge_range(Line,0,Line+7,0,"Price (Riels) exc. WinS \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),Price_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        if WithSchool:
            Price = con.execute("SELECT SUM(Total_Income-Bottle_Income),Old_Platform,Sales.Id_Site,SUM(Total_Sales-Bottle_Sales) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        else:
            Price = con.execute("SELECT SUM(Total_Income-Bottle_Income-WiS_Income),Old_Platform,Sales.Id_Site,SUM(Total_Sales-Bottle_Sales-WiS_Sales) FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()

        Tier1 = Tier[m]
        TotalBot_per_tier = [0]*Nb_of_tier
        TotalSite_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            PricePlatform = list(filter(lambda row: row[1] == Platform_List[i][0], Price))
            PriceTot = 0
            NbSiteTot = 0
            for j in range(Nb_of_tier):
                PriceTotPlat = 0
                NbSiteTotPlat = 0
                for k in range(len(PricePlatform)):

                    if PricePlatform[k][2] in Tier1[1][j]:
                        PriceTotPlat += float(PricePlatform[k][0])/float(PricePlatform[k][3]) or 0
                        NbSiteTotPlat += 1

                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(PriceTotPlat,NbSiteTotPlat),Price_format)
                PriceTot += PriceTotPlat
                NbSiteTot += NbSiteTotPlat
                TotalBot_per_tier[j] += PriceTotPlat
                TotalSite_per_tier[j] += NbSiteTotPlat
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/%s,0)"%(TotalBot_per_tier[j],TotalSite_per_tier[j]),Price_bold_format)


            worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(PriceTot,NbSiteTot),Price_bold_format)
        worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/%s,0)"%(sum(TotalBot_per_tier),sum(TotalSite_per_tier)),Price_bold_format)
    return("ok")

def KPISalaryEnt(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    SalaryEnt_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    SalaryEnt_bold_format = workbook.add_format({'num_format' : '# ### ##0 $','bold':True, 'border': 1})
    SalaryEnt_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",SalaryEnt_bold_format)
    worksheet.write(Line+1,1,"Tier 1",SalaryEnt_bold_format)
    worksheet.write(Line+2,1,"Tier 2",SalaryEnt_bold_format)
    worksheet.write(Line+3,1,"Tier 3",SalaryEnt_bold_format)
    worksheet.write(Line+4,1,"New",SalaryEnt_bold_format)
    worksheet.write(Line+5,1,"Reopen",SalaryEnt_bold_format)
    worksheet.write(Line+6,1,"Inactive",SalaryEnt_bold_format)
    worksheet.write(Line+7,1,"Total",SalaryEnt_bold_format)
    worksheet.merge_range(Line,0,Line+7,0,"Avg Salary Ent \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),SalaryEnt_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):

        SalaryEnt = con.execute("SELECT SUM(Amount_Expenses)/%s,Old_Platform,Expenses.Id_Site FROM Expenses JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Expenses.Month <= %s AND Expenses.Month > %s AND (Ref_expenses = 'variable_salary_entrepreneurs' OR Ref_expenses = 'fix_salary_entrepreneurs')  GROUP BY Old_Platform,Expenses.Id_Site",(exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        ActiveMonth = con.execute("SELECT COUNT(Total_Sales),Old_Platform,Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Old_Platform,Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()

        Tier1 = Tier[m]
        TotalBot_per_tier = [0]*Nb_of_tier
        TotalMonth_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            ActiveMonthPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], ActiveMonth))
            SalaryEntTot = 0
            MonthTot = 0
            for j in range(Nb_of_tier):
                SalaryEntTotPlat = 0
                MonthTotPlat = 0
                SiteTotPlat = 0
                for k in range(len(ActiveMonthPlatform)):

                    if ActiveMonthPlatform[k][2] in Tier1[1][j]:
                        SalaryMonthPlatform = list(filter(lambda row: row[2] == ActiveMonthPlatform[k][2], SalaryEnt)) or [(0,0)]
                        SalaryEntTotPlat += float(SalaryMonthPlatform[0][0]) or 0
                        MonthTotPlat += ActiveMonthPlatform[k][0] or 0

                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(SalaryEntTotPlat,MonthTotPlat),SalaryEnt_format)
                SalaryEntTot += SalaryEntTotPlat
                MonthTot += MonthTotPlat
                TotalBot_per_tier[j] += SalaryEntTotPlat
                TotalMonth_per_tier[j] += MonthTotPlat
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/(%s),0)"%(TotalBot_per_tier[j],TotalMonth_per_tier[j]),SalaryEnt_bold_format)


            worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/(%s),0)"%(SalaryEntTot,MonthTot),SalaryEnt_bold_format)
        worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/(%s),0)"%(sum(TotalBot_per_tier),sum(TotalMonth_per_tier)),SalaryEnt_bold_format)
    return("ok")

def KPIIncomeEnt(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate,Hide = 0):
    con = db.pool.connect()
    Category_expenses = CategoryExpenses()
    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    SalaryEnt_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    SalaryEnt_bold_format = workbook.add_format({'num_format' : '# ### ##0 $','bold':True, 'border': 1})
    SalaryEnt_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",SalaryEnt_bold_format)
    worksheet.write(Line+1,1,"Tier 1",SalaryEnt_bold_format)
    worksheet.write(Line+2,1,"Tier 2",SalaryEnt_bold_format)
    worksheet.write(Line+3,1,"Tier 3",SalaryEnt_bold_format)
    worksheet.write(Line+4,1,"New",SalaryEnt_bold_format)
    worksheet.write(Line+5,1,"Reopen",SalaryEnt_bold_format)
    worksheet.write(Line+6,1,"Inactive",SalaryEnt_bold_format)
    worksheet.write(Line+7,1,"Total",SalaryEnt_bold_format)
    worksheet.merge_range(Line,0,Line+7,0,"Avg Income Ent \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),SalaryEnt_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):

        SalaryEnt = con.execute("SELECT SUM(Amount_Expenses)/%s,Old_Platform,Expenses.Id_Site FROM Expenses JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Expenses.Month <= %s AND Expenses.Month > %s AND (Ref_expenses = 'variable_salary_entrepreneurs' OR Ref_expenses = 'fix_salary_entrepreneurs')  GROUP BY Old_Platform,Expenses.Id_Site",(exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        Revenue = con.execute("SELECT SUM(Total_Income)/%s,Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Old_Platform,Sales.Id_Site ",(exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        Cost = con.execute('SELECT SUM(Amount_Expenses)/%s,Old_Platform,Expenses.Id_Site FROM Expenses JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Expenses.Month <= %s AND Expenses.Month > %s AND Category_expenses IN %s GROUP BY Sites.Id_Site', (exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m),Category_expenses)).fetchall()
        ActiveMonth = con.execute("SELECT COUNT(Total_Sales),Old_Platform,Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Old_Platform,Sales.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()

        Tier1 = Tier[m]
        TotalInc_per_tier = [0]*Nb_of_tier
        TotalMonth_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            ActiveMonthPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], ActiveMonth))
            IncEntTot = 0
            MonthTot = 0
            for j in range(Nb_of_tier):
                IncomeEntTotPlat = 0
                MonthTotPlat = 0
                SiteTotPlat = 0
                for k in range(len(ActiveMonthPlatform)):

                    if ActiveMonthPlatform[k][2] in Tier1[1][j]:
                        MonthTotPlat += ActiveMonthPlatform[k][0] or 0
                        SalaryMonthPlatform = list(filter(lambda row: row[2] == ActiveMonthPlatform[k][2], SalaryEnt)) or [(0,0)]
                        RevenueMonthPlatform = list(filter(lambda row: row[2] == ActiveMonthPlatform[k][2], Revenue)) or [(0,0)]
                        CostMonthPlatform = list(filter(lambda row: row[2] == ActiveMonthPlatform[k][2], Cost)) or [(0,0)]
                        IncomeEntTotPlat += (float(SalaryMonthPlatform[0][0])+float(RevenueMonthPlatform[0][0])-float(CostMonthPlatform[0][0]))
                        
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(IncomeEntTotPlat,MonthTotPlat),SalaryEnt_format)
                IncEntTot += IncomeEntTotPlat
                MonthTot += MonthTotPlat
                TotalInc_per_tier[j] += IncomeEntTotPlat
                TotalMonth_per_tier[j] += MonthTotPlat
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/(%s),0)"%(TotalInc_per_tier[j],TotalMonth_per_tier[j]),SalaryEnt_bold_format)


            worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/(%s),0)"%(IncEntTot,MonthTot),SalaryEnt_bold_format)
        worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/(%s),0)"%(sum(TotalInc_per_tier),sum(TotalMonth_per_tier)),SalaryEnt_bold_format)
    return("ok")

def KPIPL(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate):
    con = db.pool.connect()
    Category_expenses = CategoryExpenses()

    PL_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    PL_bold_format = workbook.add_format({'num_format' : '# ### ##0 $','bold':True, 'border': 1})
    PL_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",PL_bold_format)
    worksheet.write(Line+1,1,"Tier 1",PL_bold_format)
    worksheet.write(Line+2,1,"Tier 2",PL_bold_format)
    worksheet.write(Line+3,1,"Tier 3",PL_bold_format)
    worksheet.write(Line+4,1,"New",PL_bold_format)
    worksheet.write(Line+5,1,"Reopen",PL_bold_format)
    worksheet.write(Line+6,1,"Inactive",PL_bold_format)
    worksheet.write(Line+7,1,"Total",PL_bold_format)
    worksheet.merge_range(Line,0,Line+7,0,"P&L Tot ($) \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),PL_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        Revenue = con.execute("SELECT SUM(Total_Income)/%s,Old_Platform,Sales.Id_Site FROM Sales INNER JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s GROUP BY Old_Platform,Sales.Id_Site ",(exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        Cost = con.execute('SELECT SUM(Amount_Expenses)/%s,Old_Platform,Expenses.Id_Site FROM Expenses JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Expenses.Month <= %s AND Expenses.Month > %s AND Category_expenses IN %s GROUP BY Sites.Id_Site', (exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m),Category_expenses)).fetchall()
        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            RevenuePlatform = list(filter(lambda row: row[1] == Platform_List[i][0], Revenue)) or [(0,0,0)]
            CostPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], Cost)) or [(0,0,0)]
            PLTot = 0
            for j in range(Nb_of_tier):
                RevenueTotPlat = 0
                CostTotPlat = 0
                for k in range(len(RevenuePlatform)):
                    if RevenuePlatform[k][2] in Tier1[1][j]:
                        RevenueTotPlat += RevenuePlatform[k][0] or 0
                for p in range(len(CostPlatform)):
                    if CostPlatform[p][2] in Tier1[1][j]:
                        CostTotPlat += CostPlatform[p][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),RevenueTotPlat-CostTotPlat,PL_format)
                PLTot += RevenueTotPlat-CostTotPlat
                Total_per_tier[j] += RevenueTotPlat-CostTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],PL_bold_format)


            worksheet.write(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),PLTot,PL_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),PL_bold_format)
    return("ok")

def KPIDebt(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    Debt_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    Debt_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    Debt_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",Debt_bold_format)
    worksheet.write(Line+1,1,"Tier 1",Debt_bold_format)
    worksheet.write(Line+2,1,"Tier 2",Debt_bold_format)
    worksheet.write(Line+3,1,"Tier 3",Debt_bold_format)
    worksheet.write(Line+4,1,"New",Debt_bold_format)
    worksheet.write(Line+5,1,"Reopen",Debt_bold_format)
    worksheet.write(Line+6,1,"Inactive",Debt_bold_format)
    worksheet.write(Line+7,1,"Total",Debt_bold_format)
    worksheet.merge_range(Line,0,Line+8,0,"Total Debts \n%s %s"%(calendar.month_name[Current_date.month],Current_date.year),Debt_Title)

    Nb_of_tier = len(Tier[0][1])-1

    for m in range(len(Tier)):
        Debt = con.execute("SELECT SUM(Amount_Expenses)/%s,Old_Platform,Expenses.Id_Site FROM Expenses INNER JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_Expenses > 0 GROUP BY Old_Platform,Expenses.Id_Site",(exchange_rate,Current_date-relativedelta(months=+12*m-1))).fetchall()

        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            DebtPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], Debt))
            DebtTot = 0
            for j in range(Nb_of_tier):
                DebtTotPlat = 0
                for k in range(len(DebtPlatform)):

                    if DebtPlatform[k][2] in Tier1[1][j]:
                        DebtTotPlat += DebtPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),DebtTotPlat,Debt_format)
                DebtTot += DebtTotPlat
                Total_per_tier[j] += DebtTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],Debt_bold_format)


            worksheet.write(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),DebtTot,Debt_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),Debt_bold_format)
    return("ok")

def KPISaving(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate,Hide=0):
    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    Saving_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    Saving_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    Saving_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",Saving_bold_format)
    worksheet.write(Line+1,1,"Tier 1",Saving_bold_format)
    worksheet.write(Line+2,1,"Tier 2",Saving_bold_format)
    worksheet.write(Line+3,1,"Tier 3",Saving_bold_format)
    worksheet.write(Line+4,1,"New",Saving_bold_format)
    worksheet.write(Line+5,1,"Reopen",Saving_bold_format)
    worksheet.write(Line+6,1,"Inactive",Saving_bold_format)
    worksheet.write(Line+7,1,"Total",Saving_bold_format)
    worksheet.merge_range(Line,0,Line+8,0,"Total Savings \n%s %s"%(calendar.month_name[Current_date.month],Current_date.year),Saving_Title)

    Nb_of_tier = len(Tier[0][1])-1

    for m in range(len(Tier)):
        Saving = con.execute("SELECT -Amount_Expenses/%s,Old_Platform,Expenses.Id_Site FROM Expenses INNER JOIN Sites ON Expenses.Id_Site = Sites.Id_Site WHERE Month = %s AND Ref_expenses = 'debt' AND Amount_Expenses < 0",(exchange_rate,Current_date-relativedelta(months=+12*m+-1))).fetchall()

        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            SavingPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], Saving))
            SavingTot = 0
            for j in range(Nb_of_tier):
                SavingTotPlat = 0
                for k in range(len(SavingPlatform)):

                    if SavingPlatform[k][2] in Tier1[1][j]:
                        SavingTotPlat += SavingPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),SavingTotPlat,Saving_format)
                SavingTot += SavingTotPlat
                Total_per_tier[j] += SavingTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],Saving_bold_format)


            worksheet.write(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),SavingTot,Saving_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),Saving_bold_format)
    return("ok")

def KPICollectionRate(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate,Hide=0):
    #ONLY YTD
    Date_1 = date(Current_date.year-1,12,1)

    con = db.pool.connect()

    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})

    CR_format = workbook.add_format({'num_format' : '0%','border':1})
    CR_bold_format = workbook.add_format({'num_format' : '0%','bold':True, 'border': 1})
    CR_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",CR_bold_format)
    worksheet.write(Line+1,1,"Tier 1",CR_bold_format)
    worksheet.write(Line+2,1,"Tier 2",CR_bold_format)
    worksheet.write(Line+3,1,"Tier 3",CR_bold_format)
    worksheet.write(Line+4,1,"New",CR_bold_format)
    worksheet.write(Line+5,1,"Reopen",CR_bold_format)
    worksheet.write(Line+6,1,"Inactive",CR_bold_format)
    worksheet.write(Line+7,1,"Total",CR_bold_format)
    worksheet.merge_range(Line,0,Line+7,0,"Collection Rate (with debt Settlement) \n%s %s - %s %s"%(calendar.month_name[(Date_1 + relativedelta(months=+1)).month],(Date_1 + relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),CR_Title)

    Nb_of_tier = len(Tier[0][1])-2

    for m in range(len(Tier)):
        CollectionRate = con.execute("SELECT SUM(Amount_Expenses)/%s,Old_Platform,Expenses.Id_Site,IFNULL(SUM(Paid),0)/%s FROM Expenses INNER JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE (Ref_expenses = 'stock_ts' OR Ref_expenses = 'bottle_invoice' OR Ref_expenses = 'entrepreneur_contribution' OR Ref_expenses = 'water quality alert' OR Ref_expenses = 'technical intervention' OR Ref_expenses = 'delivery_program_fee') AND Month <= %s AND Month > %s GROUP BY Id_Site",(exchange_rate,exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        allDebtPaid = con.execute("SELECT IFNULL(SUM(CASE WHEN Paid>Amount_Expenses THEN Amount_Expenses ELSE Paid END),0)/%s,Old_Platform,Expenses.Id_Site FROM Expenses INNER JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE Ref_expenses ='debt' AND Amount_Expenses > 0 AND Month <= %s AND Month > %s GROUP BY Id_Site",(exchange_rate,Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        allonlydebtjanv = con.execute("""SELECT Amount_Expenses/%s,Old_Platform,Expenses.Id_Site FROM Expenses 
            INNER JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
            WHERE Ref_expenses = 'debt' AND Month = %s AND Amount_Expenses > 0 """,(exchange_rate,Date_1-relativedelta(months=+12*m-1))).fetchall()

        Tier1 = Tier[m]
        Total_due_per_tier = [0]*Nb_of_tier
        Total_paid_per_tier = [0]*Nb_of_tier
        Total_debt_per_tier = [0]*Nb_of_tier
        Total_debt_janv_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            CRPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], CollectionRate)) or [(0,0,0,0)]
            paidTot = 0
            dueTot = 0
            DebtTot = 0
            DebtJanvTot = 0
            for j in range(Nb_of_tier):
                paidTotPlat = 0
                dueTotPlat = 0
                DebtTotPlat = 0
                DebtJanvTotPlat = 0
                for k in range(len(CRPlatform)):

                    if CRPlatform[k][2] in Tier1[1][j]:
                        debtPaid = list(filter(lambda row: row[2] == CRPlatform[k][2], allDebtPaid)) or [(0,0,0,0)]
                        debtJanvPaid = list(filter(lambda row: row[2] == CRPlatform[k][2], allonlydebtjanv)) or [(0,0,0,0)]
                        paidTotPlat += CRPlatform[k][3]
                        dueTotPlat += CRPlatform[k][0]
                        DebtTotPlat += debtPaid[0][0]
                        DebtJanvTotPlat += debtJanvPaid[0][0]


                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+i+2),"=IFERROR((%s+%s)/(%s+%s),\"\")"%(paidTotPlat,DebtTotPlat,dueTotPlat,DebtJanvTotPlat),CR_format)
                paidTot += paidTotPlat
                dueTot += dueTotPlat
                DebtTot += DebtTotPlat
                DebtJanvTot += DebtJanvTotPlat
                Total_paid_per_tier[j] += paidTotPlat
                Total_due_per_tier[j] += dueTotPlat
                Total_debt_per_tier[j] += DebtTotPlat
                Total_debt_janv_per_tier[j] += DebtJanvTotPlat
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR((%s+%s)/(%s+%s),\"\")"%(Total_paid_per_tier[j],Total_debt_per_tier[j],Total_due_per_tier[j],Total_debt_janv_per_tier[j]),CR_bold_format)


            worksheet.write_formula(Line+len(Tier1[1])-2,(m*(len(Platform_List)+2)+i+2),"=IFERROR((%s+%s)/(%s+%s),\"\")"%(paidTot,DebtTot,dueTot,DebtJanvTot),CR_bold_format)
        worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR((%s+%s)/(%s+%s),\"\")"%(sum(Total_paid_per_tier),sum(Total_debt_per_tier),sum(Total_due_per_tier),sum(Total_debt_janv_per_tier)),CR_bold_format)
    return("ok")

def KPINumberOperator(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,exchange_rate):

    con = db.pool.connect()

    NbOperator_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    NbOperator_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbOperator_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",NbOperator_bold_format)
    worksheet.write(Line+1,1,"Tier 1",NbOperator_bold_format)
    worksheet.write(Line+2,1,"Tier 2",NbOperator_bold_format)
    worksheet.write(Line+3,1,"Tier 3",NbOperator_bold_format)
    worksheet.write(Line+4,1,"New",NbOperator_bold_format)
    worksheet.write(Line+5,1,"Reopen",NbOperator_bold_format)
    worksheet.write(Line+6,1,"Total",NbOperator_bold_format)
    worksheet.merge_range(Line,0,Line+6,0,"Nb O-we Jobs Created \n%s %s - %s %s"%(calendar.month_name[(Date_1+relativedelta(months=+1)).month],(Date_1+relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),NbOperator_Title)

    Nb_of_tier = len(Tier[0][1])-3

    for m in range(len(Tier)):
        NbOperator = con.execute("SELECT SUM(Number_of_Operator),Old_Platform,Indicators.Id_Site FROM Indicators JOIN Sites ON Sites.Id_Site = Indicators.Id_Site WHERE Month <= %s AND Month >%s GROUP BY Old_Platform,Indicators.Id_Site",(Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))).fetchall()
        
        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            NbOperatorPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], NbOperator))
            NbOperatorTot = 0
            for j in range(Nb_of_tier):
                NbOperatorTotPlat = 0
                for k in range(len(NbOperatorPlatform)):

                    if NbOperatorPlatform[k][2] in Tier1[1][j]:
                        NbOperatorTotPlat += NbOperatorPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),NbOperatorTotPlat,NbOperator_format)
                NbOperatorTot += NbOperatorTotPlat
                Total_per_tier[j] += NbOperatorTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],NbOperator_bold_format)


            worksheet.write(Line+len(Tier1[1])-3,(m*(len(Platform_List)+2)+i+2),NbOperatorTot,NbOperator_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),NbOperator_bold_format)
    return("ok")

def KPINbSiteMoreThan3Operators(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,Hide=0):

    con = db.pool.connect()
    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})
    NbSiteOperator_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    NbSiteOperator_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbSiteOperator_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",NbSiteOperator_bold_format)
    worksheet.write(Line+1,1,"Tier 1",NbSiteOperator_bold_format)
    worksheet.write(Line+2,1,"Tier 2",NbSiteOperator_bold_format)
    worksheet.write(Line+3,1,"Tier 3",NbSiteOperator_bold_format)
    worksheet.write(Line+4,1,"New",NbSiteOperator_bold_format)
    worksheet.write(Line+5,1,"Reopen",NbSiteOperator_bold_format)
    worksheet.write(Line+6,1,"Total",NbSiteOperator_bold_format)
    worksheet.merge_range(Line,0,Line+6,0,"Nb Sites > 3 workers \n%s %s - %s %s"%(calendar.month_name[(Date_1+relativedelta(months=+1)).month],(Date_1+relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),NbSiteOperator_Title)

    Nb_of_tier = len(Tier[0][1])-3

    for m in range(len(Tier)):
        # Use MAX(Number_of_Operator) over the period for each site (not SUM),
        # then count sites where this value is strictly > 3.
        SiteOperators = con.execute(
            "SELECT MAX(Number_of_Operator),Old_Platform,Indicators.Id_Site "
            "FROM Indicators JOIN Sites ON Sites.Id_Site = Indicators.Id_Site "
            "WHERE Month <= %s AND Month > %s "
            "GROUP BY Old_Platform,Indicators.Id_Site",
            (Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))
        ).fetchall()

        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            SiteOperatorsPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], SiteOperators))
            NbSiteTot = 0
            for j in range(Nb_of_tier):
                NbSiteTotPlat = 0
                for k in range(len(SiteOperatorsPlatform)):
                    if SiteOperatorsPlatform[k][2] in Tier1[1][j]:
                        if (SiteOperatorsPlatform[k][0] or 0) >= 3:
                            NbSiteTotPlat += 1

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),NbSiteTotPlat,NbSiteOperator_format)
                NbSiteTot += NbSiteTotPlat
                Total_per_tier[j] += NbSiteTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],NbSiteOperator_bold_format)

            worksheet.write(Line+len(Tier1[1])-3,(m*(len(Platform_List)+2)+i+2),NbSiteTot,NbSiteOperator_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),NbSiteOperator_bold_format)
    return("ok")

def KPINbSiteMoreThan3OperatorsPercentage(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List,Hide=0):

    con = db.pool.connect()
    if Hide:
        for i in range(9):
            worksheet.set_row(Line+i,None,None,{'level':1,'hidden':True})
    NbSiteOperatorPercentage_format = workbook.add_format({'num_format' : '0%','border':1})
    NbSiteOperatorPercentage_bold_format = workbook.add_format({'num_format' : '0%','bold':True, 'border': 1})
    NbSiteOperator_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbSiteOperatorPercentage_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",NbSiteOperatorPercentage_bold_format)
    worksheet.write(Line+1,1,"Tier 1",NbSiteOperatorPercentage_bold_format)
    worksheet.write(Line+2,1,"Tier 2",NbSiteOperatorPercentage_bold_format)
    worksheet.write(Line+3,1,"Tier 3",NbSiteOperatorPercentage_bold_format)
    worksheet.write(Line+4,1,"New",NbSiteOperatorPercentage_bold_format)
    worksheet.write(Line+5,1,"Reopen",NbSiteOperatorPercentage_bold_format)
    worksheet.write(Line+6,1,"Total",NbSiteOperatorPercentage_bold_format)
    worksheet.merge_range(Line,0,Line+6,0,"Nb Sites >= 3 workers %% \n%s %s - %s %s"%(calendar.month_name[(Date_1+relativedelta(months=+1)).month],(Date_1+relativedelta(months=+1)).year,calendar.month_name[Current_date.month],Current_date.year),NbSiteOperatorPercentage_Title)

    Nb_of_tier = len(Tier[0][1])-3

    for m in range(len(Tier)):
        SiteOperators = con.execute(
            "SELECT MAX(Number_of_Operator),Old_Platform,Indicators.Id_Site "
            "FROM Indicators JOIN Sites ON Sites.Id_Site = Indicators.Id_Site "
            "WHERE Month <= %s AND Month > %s "
            "GROUP BY Old_Platform,Indicators.Id_Site",
            (Current_date-relativedelta(months=+12*m),Date_1-relativedelta(months=+12*m))
        ).fetchall()

        # Denominator: number of sites in this category (tier) AND this platform.
        # Build a site -> platform map once to avoid scanning lists repeatedly.
        NbSite = con.execute("SELECT DISTINCT Old_Platform,Id_Site FROM Sites WHERE Id_Site <> %s",'EBM').fetchall()
        platform_by_site = {row[1]: row[0] for row in NbSite}

        Tier1 = Tier[m]
        Total_num_per_tier = [0]*Nb_of_tier
        Total_den_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            platform_code = Platform_List[i][0]
            sites_gt3 = set(
                row[2] for row in SiteOperators
                if row[1] == platform_code and (row[0] or 0) >= 3
            )

            NumTot = 0
            DenTot = 0
            for j in range(Nb_of_tier):
                DenPlat = 0
                NumPlat = 0

                for site_id in Tier1[1][j]:
                    if platform_by_site.get(site_id) == platform_code:
                        DenPlat += 1
                        if site_id in sites_gt3:
                            NumPlat += 1

                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(NumPlat,DenPlat),NbSiteOperatorPercentage_format)
                NumTot += NumPlat
                DenTot += DenPlat
                Total_num_per_tier[j] += NumPlat
                Total_den_per_tier[j] += DenPlat
                worksheet.write_formula(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/%s,0)"%(Total_num_per_tier[j],Total_den_per_tier[j]),NbSiteOperatorPercentage_bold_format)

            worksheet.write_formula(Line+len(Tier1[1])-3,(m*(len(Platform_List)+2)+i+2),"=IFERROR(%s/%s,0)"%(NumTot,DenTot),NbSiteOperatorPercentage_bold_format)

        worksheet.write_formula(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),"=IFERROR(%s/%s,0)"%(sum(Total_num_per_tier),sum(Total_den_per_tier)),NbSiteOperatorPercentage_bold_format)
    return("ok")

def KPIIntervention(workbook,worksheet,Line,Current_date,Date_1,Tier,TypeIntervention,NameInterventionType,Platform_List):
    con = db.pool.connect()

    NbIntervention_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    NbIntervention_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbIntervention_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",NbIntervention_bold_format)
    worksheet.write(Line+1,1,"Tier 1",NbIntervention_bold_format)
    worksheet.write(Line+2,1,"Tier 2",NbIntervention_bold_format)
    worksheet.write(Line+3,1,"Tier 3",NbIntervention_bold_format)
    worksheet.write(Line+4,1,"New",NbIntervention_bold_format)
    worksheet.write(Line+5,1,"Reopen",NbIntervention_bold_format)
    worksheet.write(Line+6,1,"Inactive",NbIntervention_bold_format)
    worksheet.write(Line+7,1,"Closed",NbIntervention_bold_format)
    worksheet.write(Line+8,1,"Total",NbIntervention_bold_format)
    worksheet.merge_range(Line,0,Line+8,0,"Total %s Intervention \n%s %s - %s %s"%(NameInterventionType,calendar.month_name[(Date_1).month],(Date_1).year,calendar.month_name[Current_date.month],Current_date.year),NbIntervention_Title)

    Nb_of_tier = len(Tier[0][1])-1

    
    for m in range(len(Tier)):
        NbIntervention = con.execute("""SELECT COUNT(rt_site_problem_description),Old_Platform,site FROM technicals 
                        JOIN Sites ON Sites.Id_Site = site
                        WHERE start_intervention < %s AND start_intervention >= %s AND rt_site_problem_description in %s
                        GROUP BY Old_Platform,site 
                        ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(Current_date-relativedelta(months=+12*m-1),Date_1-relativedelta(months=+12*m),TypeIntervention)).fetchall()
        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            NbInterventionPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], NbIntervention))
            NbInterventionTot = 0
            for j in range(Nb_of_tier):
                NbInterventionTotPlat = 0
                for k in range(len(NbInterventionPlatform)):
                    if NbInterventionPlatform[k][2] in Tier1[1][j]:
                        NbInterventionTotPlat += NbInterventionPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),NbInterventionTotPlat,NbIntervention_format)
                NbInterventionTot += NbInterventionTotPlat
                Total_per_tier[j] += NbInterventionTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],NbIntervention_bold_format)


            worksheet.write(Line+len(Tier1[1])-1,(m*(len(Platform_List)+2)+i+2),NbInterventionTot,NbIntervention_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),NbIntervention_bold_format)
    return("ok")

def KPIAllIntervention(workbook,worksheet,Line,Current_date,Date_1,Tier,ListIntervention,Platform_List):
    con = db.pool.connect()

    NbIntervention_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    NbIntervention_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbIntervention_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    for i in range(len(ListIntervention)):
        worksheet.write(Line+i,1,ListIntervention[i],NbIntervention_bold_format)
    worksheet.write(Line+len(ListIntervention),1,"Total",NbIntervention_bold_format)
    worksheet.merge_range(Line,0,Line+len(ListIntervention),0,"Total Intervention per issue \n%s %s - %s %s"%(calendar.month_name[(Date_1).month],(Date_1).year,calendar.month_name[Current_date.month],Current_date.year),NbIntervention_Title)

    Nb_InterventionType = len(ListIntervention)

    
    for m in range(len(Tier)):
        NbIntervention = con.execute("""SELECT COUNT(rt_site_problem_description),Old_Platform,rt_site_problem_description FROM technicals 
                        JOIN Sites ON Sites.Id_Site = site
                        WHERE start_intervention < %s AND start_intervention >= %s AND rt_site_problem_description in %s
                        GROUP BY Old_Platform,rt_site_problem_description 
                        ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(Current_date-relativedelta(months=+12*m-1),Date_1-relativedelta(months=+12*m),ListIntervention)).fetchall()
        
        Total_per_TypeIntervention = [0]*Nb_InterventionType
        for i in range(len(Platform_List)):
            NbInterventionPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], NbIntervention))
            NbInterventionTot = 0
            for j in range(Nb_InterventionType):
                NbInterventionTotPlat = 0
                for k in range(len(NbInterventionPlatform)):
                    if NbInterventionPlatform[k][2] == ListIntervention[j]:
                        NbInterventionTotPlat += NbInterventionPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),NbInterventionTotPlat,NbIntervention_format)
                NbInterventionTot += NbInterventionTotPlat
                Total_per_TypeIntervention[j] += NbInterventionTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_TypeIntervention[j],NbIntervention_bold_format)


            worksheet.write(Line+len(ListIntervention),(m*(len(Platform_List)+2)+i+2),NbInterventionTot,NbIntervention_bold_format)
        worksheet.write(Line+Nb_InterventionType,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_TypeIntervention),NbIntervention_bold_format)
    return("ok")
    
def KPIClosedDays(workbook,worksheet,Line,Current_date,Date_1,Tier,Platform_List):
    con = db.pool.connect()

    NbIntervention_format = workbook.add_format({'num_format' : '# ### ##0','border':1})
    NbIntervention_bold_format = workbook.add_format({'num_format' : '# ### ##0','bold':True, 'border': 1})
    NbIntervention_Title = workbook.add_format({'valign':'vcenter','bold':True,'text_wrap':True,'center_across':True})

    worksheet.write(Line,1,"Super Tier 1",NbIntervention_bold_format)
    worksheet.write(Line+1,1,"Tier 1",NbIntervention_bold_format)
    worksheet.write(Line+2,1,"Tier 2",NbIntervention_bold_format)
    worksheet.write(Line+3,1,"Tier 3",NbIntervention_bold_format)
    worksheet.write(Line+4,1,"New",NbIntervention_bold_format)
    worksheet.write(Line+5,1,"Reopen",NbIntervention_bold_format)
    worksheet.write(Line+6,1,"Inactive",NbIntervention_bold_format)
    worksheet.write(Line+7,1,"Closed",NbIntervention_bold_format)
    worksheet.write(Line+8,1,"Total",NbIntervention_bold_format)
    worksheet.merge_range(Line,0,Line+8,0,"Total Day w/o production \n%s %s - %s %s"%(calendar.month_name[(Date_1).month],(Date_1).year,calendar.month_name[Current_date.month],Current_date.year),NbIntervention_Title)

    Nb_of_tier = len(Tier[0][1])-1

    
    for m in range(len(Tier)):
        NbIntervention = con.execute("""SELECT SUM(DATEDIFF(IFNULL(end_intervention,%s),problem_date)),Old_Platform,site FROM technicals 
                        JOIN Sites ON Sites.Id_Site = site
                        WHERE start_intervention < %s AND start_intervention >= %s AND problem_status = "Can Not Produce"
                        GROUP BY Old_Platform,site 
                        ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(Current_date+relativedelta(months=+1),Current_date-relativedelta(months=+12*m-1),Date_1-relativedelta(months=+12*m))).fetchall()
        Tier1 = Tier[m]
        Total_per_tier = [0]*Nb_of_tier
        for i in range(len(Platform_List)):
            NbInterventionPlatform = list(filter(lambda row: row[1] == Platform_List[i][0], NbIntervention))
            NbInterventionTot = 0
            for j in range(Nb_of_tier):
                NbInterventionTotPlat = 0
                for k in range(len(NbInterventionPlatform)):

                    if NbInterventionPlatform[k][2] in Tier1[1][j]:
                        NbInterventionTotPlat += NbInterventionPlatform[k][0] or 0

                worksheet.write(Line+j,(m*(len(Platform_List)+2)+i+2),NbInterventionTotPlat,NbIntervention_format)
                NbInterventionTot += NbInterventionTotPlat
                Total_per_tier[j] += NbInterventionTotPlat
                worksheet.write(Line+j,(m*(len(Platform_List)+2)+len(Platform_List)+2),Total_per_tier[j],NbIntervention_bold_format)


            worksheet.write(Line+len(Tier1[1])-1,(m*(len(Platform_List)+2)+i+2),NbInterventionTot,NbIntervention_bold_format)
        worksheet.write(Line+Nb_of_tier,(m*(len(Platform_List)+2)+len(Platform_List)+2),sum(Total_per_tier),NbIntervention_bold_format)
    return("ok")

def KPI1001fontaines(ListDate, ListSite, Tier_this_year, Tier_last_year, ListOpenDayThisYear, ListOpenDayLastYear):
    con = db.pool.connect()
    ListSite = con.execute("SELECT Id_Site FROM Sales W")
    Teuk_saat_format = workbook.add_format({'font' : 'Calibri', 'underline' : True, 'font_size' : 14, 'bg_color' : '#D9E1F2', 'align' : 'right' })
    Date_format = workbook.add_format({'font' : 'Calibri', 'bold' : True, 'font_size' : 14, 'bg_color' : '#D9E1F2', 'num_format' : 'mmmm-yyyy'})

    Title_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 14, 'font_color' :  '#1F4E78', 'bg_color' : '#D9E1F2', 'align' : 'right', 'bold' : True})
    Title_number_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 14, 'font_color' :  '#1F4E78', 'bg_color' : '#D9E1F2', 'num_format' : '# ### ##0',  'align' : 'right', 'bold' : True })
    Title_percentage_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 14, 'font_color' :  '#1F4E78', 'bg_color' : '#D9E1F2', 'num_format' : '0%', 'align' : 'right', 'bold' : True })
    Title_kiosk_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 14, 'font_color' :  '#1F4E78', 'bg_color' : '#D9E1F2', 'num_format' : '# ### ### ##0 "kiosks"', 'align' : 'right', 'bold' : True })
    Title_riels_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 14, 'font_color' :  '#1F4E78', 'bg_color' : '#D9E1F2', 'num_format' : '"Riels "# ### ### ##0', 'align' : 'right', 'bold' : True })

    Small_title_number_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11, 'font_color' :  '#1F4E78', 'bg_color' : '#D9E1F2', 'num_format' : '# ### ##0',  'align' : 'right', 'bold' : True })

    Italic_right_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11, 'bg_color' : '#D9E1F2', 'align' : 'right' })
    Italic_left_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11, 'bg_color' : '#D9E1F2', 'align' : 'left', 'num_format' : '# ### ##0' })
    Italic_left_grey_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11, 'bg_color' : '#D9E1F2', 'align' : 'left', 'font_color' : '#808080' })

    Red_percentage_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11,  'bg_color' : '#D9E1F2', 'align' : 'left', 'num_format' : ' 0%', "font_color" : '#9C0006'})
    Green_percentage_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11,  'bg_color' : '#D9E1F2', 'align' : 'left', 'num_format' : '+ 0%', "font_color" : '#548235'})
    Percentage_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11,  'bg_color' : '#D9E1F2', 'align' : 'left', 'num_format' : '0%'})


    Red_kiosks_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11,  'bg_color' : '#D9E1F2', 'align' : 'left', 'num_format' : ' # ### ##0 "kiosks"', "font_color" : '#9C0006'})
    Green_kiosks_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11,  'bg_color' : '#D9E1F2', 'align' : 'left', 'num_format' : '+ # ### ##0 "kiosks"', "font_color" : '#548235'})
    Italic_kiosks_format = workbook.add_format({'font' : 'Calibri', 'font_size' : 11,  'bg_color' : '#D9E1F2', 'align' : 'left', 'num_format' : '0'})

    Indication_format = workbook.add_format({'font' : 'Calibri', 'bold' : True, 'font_color' : '#974706'})

    Brown_format = workbook.add_format({'font_color': '#974706'})
    Brown_percentage_format = workbook.add_format({'font_color': '#974706','num_format' : '0%'})

    worksheet_monthly_report = workbook.add_worksheet('Indicators')

    worksheet_monthly_report.set_column('C:C', len('Revenue/bottle (12 months)       '))
    worksheet_monthly_report.set_column('F:F', len('compared to last year (00  ' ))
    worksheet_monthly_report.set_column('D:D', len('NOVEMBER 2222     '))
    worksheet_monthly_report.set_column('E:E', len('+ 100 kiosk'))

    Beneficiaries= Beneficiaries_last_year = 0
    Total_sale_L_day = 0
    Nb_site = 0
    Nb_site_l_year = 0
    Total_sale_L_day_l_year = 0
    Site_active_l_year = Site_active_l_month = Site_active_t_month = 0
    Nb_tier_1 = Nb_tier_1_l_year = 0
    Income_tot = Income_tot_l_year = Sales_tot = Sales_tot_l_year = 0
    # Sales_this_month_L = 0
    Nb_tier_t_year = Nb_tier_l_year = 0
    Price_last_year = Price = 0



    query = con.execute("SELECT Beneficiaries,Id_Site FROM Beneficiaries WHERE Month = %s GROUP BY Id_Site", (Current_date))
    allmax_ben = query.fetchall()
    query = con.execute("SELECT Beneficiaries,Id_Site FROM Beneficiaries WHERE Month = %s GROUP BY Id_Site ", (Date_N_1))
    allmax_ben_l_year = query.fetchall()
    max_ben_l_year = 0
    for i in range(len(allmax_ben_l_year)):
        if allmax_ben_l_year[i][0]:
            max_ben_l_year += allmax_ben_l_year[i][0]


    query = con.execute("SELECT Total_Sales - Bottle_Sales,Number_Open_Days,Id_Site FROM Sales Where Month = %s",(Current_date))
    allL_volume_t_month = query.fetchall()

    query = con.execute("SELECT Total_Sales - Bottle_Sales,Number_Open_Days,Id_Site FROM Sales Where Month = %s",(Date_N_1))
    allL_volume_last_month = query.fetchall()

    query = con.execute("SELECT SUM(Total_Sales - Bottle_Sales),Id_Site FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site", (Current_date,Date_N_1))
    allL_volume_t_year = query.fetchall()

    query = con.execute("SELECT SUM(Total_Sales - Bottle_Sales),Id_Site FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site", (Date_N_1,Date_N_2))
    allL_volume_last_year = query.fetchall()
    Number_days_last_year = monthrange(Date_N_1.year,Date_N_1.month)[1]
    lessthan20lastyear = (con.execute("SELECT AVG((Total_Sales - Bottle_Sales)/Number_Open_Days)*20,Count(Number_Open_Days) FROM Sales WHERE Month = %s AND Number_Open_Days < 20 AND Number_Open_Days > 0", Date_N_1).fetchall())
    morethan20lastyear = (con.execute("SELECT AVG((Total_Sales - Bottle_Sales)/%s)*20,Count(Number_Open_Days) FROM Sales WHERE Month = %s AND Number_Open_Days >= 20", Number_days_last_year,Date_N_1).fetchall())
    lessthan20lastyear[0] = tuple(x if x is not None else 0 for x in lessthan20lastyear[0])
    morethan20lastyear[0] = tuple(x if x is not None else 0 for x in morethan20lastyear[0])
    Lday_N_1 = ((morethan20lastyear[0][0]*morethan20lastyear[0][1]+lessthan20lastyear[0][0]*lessthan20lastyear[0][1])/(morethan20lastyear[0][1]+lessthan20lastyear[0][1]))

    query = con.execute("SELECT Total_Sales,Id_Site FROM Sales Where Month = %s",(Current_date))
    allL_active = query.fetchall()
    query = con.execute("SELECT Total_Sales,Id_Site FROM Sales Where Month = %s",(ListDate[-2]))
    allL_active_lmonth = query.fetchall()
    query = con.execute("SELECT Total_Sales, Id_Site FROM Sales Where Month = %s",(Date_N_1))
    allL_active_lyear = query.fetchall()
    query = con.execute("SELECT SUM(Total_Sales - Bottle_Sales - WiS_Sales), SUM(Total_Income - Bottle_Income-WiS_Income),Id_Site FROM Sales Where Month = %s GROUP BY Id_Site",(Current_date))
    allL_price = query.fetchall()
    query = con.execute("SELECT SUM(Total_Sales - Bottle_Sales - WiS_Sales), SUM(Total_Income - Bottle_Income - WiS_Income), Id_Site FROM Sales Where Month = %s GROUP BY Id_Site",(Date_N_1))
    allL_price_lyear = query.fetchall()

    for i in range (len(ListSite)):


        max_ben = list(filter(lambda row: row[1] == ListSite[i][0], allmax_ben))
        if max_ben and max_ben[0][0]:
            Beneficiaries += max_ben[0][0]


        Number_days = monthrange(Current_date.year,Current_date.month)[1]
        L_volume = list(filter(lambda row: row[2] == ListSite[i][0], allL_volume_t_month))
        if L_volume and L_volume[0][0] and L_volume[0][1] and L_volume[0][1]<20:
            Total_sale_L_day += L_volume[0][0] * 20/ L_volume[0][1]
            Nb_site+=1
        elif L_volume and L_volume[0][0] and L_volume[0][1] and L_volume[0][1]>=20:
            Total_sale_L_day += L_volume[0][0] * 20 / Number_days
            Nb_site +=1

        # L_volume = list(filter(lambda row: row[2] == ListSite[i][0], allL_volume))
        # if L_volume and L_volume[0][0]:
        #     Sales_this_month_L += L_volume[0][0] * 20 / L_volume[0][1]

        Number_days_last_year = monthrange(Date_N_1.year,Date_N_1.month)[1]
        L_volume_last_month = list(filter(lambda row: row[2] == ListSite[i][0], allL_volume_last_month))
        if L_volume_last_month and L_volume_last_month[0][0] and L_volume_last_month[0][1] < 20:
            Total_sale_L_day_l_year += L_volume_last_month[0][0] * 20 / L_volume_last_month[0][1]
            Nb_site_l_year+=1
        elif L_volume_last_month and L_volume_last_month[0][0] and L_volume_last_month[0][1] >= 20:
            Total_sale_L_day_l_year += L_volume_last_month[0][0] * 20 / Number_days_last_year
            Nb_site_l_year+=1

        L_active = list(filter(lambda row: row[1] == ListSite[i][0], allL_active))
        if L_active and L_active[0][0] and L_active[0][0] != 0:
            Site_active_t_month += 1

        L_active = list(filter(lambda row: row[1] == ListSite[i][0], allL_active_lmonth))
        if L_active and L_active[0][0] and L_active[0][0] != 0:
            Site_active_l_month += 1

        L_active = list(filter(lambda row: row[1] == ListSite[i][0], allL_active_lyear))
        if L_active and L_active[0][0] and L_active[0][0] != 0:
            Site_active_l_year += 1


        L_volume_t_year = list(filter(lambda row: row[1] == ListSite[i][0], allL_volume_t_year))
        if L_volume and ((Tier_this_year[i] == 1 or Tier_this_year[i] == 'ST1') or (Tier_this_year[i] =="Reopen" and L_volume_t_year and (L_volume_t_year[0][0]*20/ListOpenDayThisYear[i] >= 1700 or L_volume_t_year[0][0]*20/ListOpenDayThisYear[i] >= 2500))):
            Nb_tier_1 += 1

        elif L_volume and (Tier_this_year[i] == 2 or Tier_this_year[i]== 3 or Tier_this_year[i] == "Reopen" and L_volume_t_year):
            Nb_tier_t_year += 1


        L_volume_last_year = list(filter(lambda row: row[1] == ListSite[i][0], allL_volume_last_year))

        if L_volume_last_month and ((Tier_last_year[i] == 1 or Tier_last_year[i] == 'ST1') or (Tier_last_year[i] =="Reopen" and L_volume_last_year and (L_volume_last_year[0][0]*20/ListOpenDayLastYear[i] >= 1700 or L_volume_t_year[0][0]*20/ListOpenDayThisYear[i] >= 2500))) :
            Nb_tier_1_l_year +=1
        elif L_volume_last_month and (Tier_last_year[i] ==2 or Tier_last_year[i] == 3 or (Tier_last_year[i] == "Reopen" and L_volume_last_year)):
            Nb_tier_l_year +=1


        L_price = list(filter(lambda row: row[2] == ListSite[i][0], allL_price))

        if L_price and L_price[0][1]:
            Price += L_price[0][1] / L_price[0][0]

        L_price = list(filter(lambda row: row[2] == ListSite[i][0], allL_price_lyear))
        if L_price and L_price[0][1]:
            Price_last_year += L_price[0][1] / L_price[0][0]
    L_day = L_day_l_year = 0
    if Nb_site !=0:
        L_day = Total_sale_L_day/Nb_site
    if Nb_site_l_year != 0:
        L_day_l_year = Total_sale_L_day_l_year/Nb_site_l_year

    worksheet_monthly_report.write('D2','%s %s'%(calendar.month_name[ListDate[-1].month],ListDate[-1].year),Date_format)
    worksheet_monthly_report.write('D3', None,Title_format)
    worksheet_monthly_report.write_formula('D4', '=D5+I3', Title_number_format)
    worksheet_monthly_report.write('D5', Beneficiaries, Small_title_number_format)
    worksheet_monthly_report.write('I2', "Indicate the number of beneficiaries for the school programm in H5 :",Brown_format)
    worksheet_monthly_report.write('I3', 315000,Brown_format)
    worksheet_monthly_report.write("I4", 'Annual target L/day',Brown_format)
    worksheet_monthly_report.write('I5', 2000,Brown_format)
    worksheet_monthly_report.write('I6', "Rate by month",Brown_format)
    Rate = []
    Rate_by_month = [
    ["January",0.08],
    ("February",0.09),
    ("March",0.11),
    ("April",0.1),
    ("Mai",0.1),
    ("June",0.09),
    ("July",0.08),
    ("August",0.08),
    ("September",0.06),
    ("October",0.06),
    ("November",0.08),
    ("December",0.08)
    ]
    for i in range(len(Rate_by_month)):
        worksheet_monthly_report.write('I%s'%(7+i),Rate_by_month[i][0],Brown_format)
        worksheet_monthly_report.write('J%s'%(7+i),Rate_by_month[i][1],Brown_percentage_format)


    worksheet_monthly_report.write('D6', None,Title_format)

    worksheet_monthly_report.write('D7',L_day,Title_number_format )
    worksheet_monthly_report.write('D8','L/day',Italic_right_format)

    worksheet_monthly_report.write('D9', None,Title_format)

    worksheet_monthly_report.write('D10',Site_active_t_month,Title_kiosk_format)

    worksheet_monthly_report.write('D11', None,Title_format)
    worksheet_monthly_report.write('D12', None,Title_format)
    worksheet_monthly_report.write('D13', None,Title_format)

    if Nb_tier_t_year+Nb_tier_1 != 0:
        worksheet_monthly_report.write('D14', Nb_tier_1/(Nb_tier_t_year+Nb_tier_1), Title_percentage_format)

    worksheet_monthly_report.write('D15', None,Title_format)
    worksheet_monthly_report.write('D16', None,Title_format)
    worksheet_monthly_report.write_formula('D17',"=IFERROR(%s/%s,"")" %(Price,Site_active_t_month), Title_riels_format)

    worksheet_monthly_report.write('E5', (Beneficiaries-max_ben_l_year)/max_ben_l_year)
    if L_day != 0 and L_day_l_year != 0 :
        worksheet_monthly_report.write('E7', (L_day - L_day_l_year)/L_day_l_year)

    worksheet_monthly_report.write('E10', (Site_active_t_month-Site_active_l_year))
    worksheet_monthly_report.write('E11', (Site_active_t_month-Site_active_l_month))
    if Nb_tier_t_year+Nb_tier_1 > 0 and Nb_tier_l_year+Nb_tier_1_l_year > 0:
        worksheet_monthly_report.write('E14', ((Nb_tier_1/(Nb_tier_t_year+Nb_tier_1))-(Nb_tier_1_l_year/(Nb_tier_l_year+Nb_tier_1_l_year))))
    if Sales_tot !=0 and Sales_tot_l_year != 0:
        worksheet_monthly_report.write('E17', ((Income_tot/Sales_tot)-(Income_tot_l_year/Sales_tot_l_year))/(Income_tot_l_year/Sales_tot_l_year))

    worksheet_monthly_report.conditional_format('E3:E9',{"type" : "formula", "criteria" : "E3<0", "format" : Red_percentage_format})
    worksheet_monthly_report.conditional_format('E3:E9',{"type" : "formula", "criteria" : "E3>0", "format" : Green_percentage_format})
    worksheet_monthly_report.conditional_format('E3:E9',{"type" : "formula", "criteria" : "E3=0", "format" : Percentage_format})

    worksheet_monthly_report.conditional_format('E10:E11',{"type" : "formula", "criteria" : "E10<0", "format" : Red_kiosks_format})
    worksheet_monthly_report.conditional_format('E10:E11',{"type" : "formula", "criteria" : "E10>0", "format" : Green_kiosks_format})
    worksheet_monthly_report.conditional_format('E10:E11',{"type" : "formula", "criteria" : "E10=0", "format" : Italic_kiosks_format})

    worksheet_monthly_report.conditional_format('E12:E17',{"type" : "formula", "criteria" : "E12<0", "format" : Red_percentage_format})
    worksheet_monthly_report.conditional_format('E12:E17',{"type" : "formula", "criteria" : "E12>0", "format" : Green_percentage_format})
    worksheet_monthly_report.conditional_format('E12:E17',{"type" : "formula", "criteria" : "E12=0", "format" : Percentage_format})

    worksheet_monthly_report.write('C2', 'TEUK SAAT 1001 INDICATORS', Teuk_saat_format)
    worksheet_monthly_report.write('C3', None, Title_format)

    worksheet_monthly_report.write('C4', 'Beneficiaries', Title_format)
    worksheet_monthly_report.write('C5', 'excluding WinS', Italic_right_format)
    worksheet_monthly_report.write('C6', None, Title_format)

    worksheet_monthly_report.write('C7', 'Volume / day', Title_format)
    worksheet_monthly_report.write('C8', 'average liter per day per kiosk',Italic_right_format)
    worksheet_monthly_report.write('C9', None, Title_format)

    worksheet_monthly_report.write('C10', 'Number of active kiosks', Title_format)
    worksheet_monthly_report.write('C11', None, Title_format)
    worksheet_monthly_report.write('C12', None, Title_format)
    worksheet_monthly_report.write('C13', None, Title_format)

    worksheet_monthly_report.write('C14', 'Tier 1', Title_format)
    worksheet_monthly_report.write('C15', '%kiosks > 1700L/day in average',Italic_right_format)
    worksheet_monthly_report.write('C16', None, Title_format)

    worksheet_monthly_report.write('C17', 'Revenue/bottle (12 months)', Title_format)


    worksheet_monthly_report.write('F2', None, Title_format)
    worksheet_monthly_report.write('F3', None, Title_format)


    worksheet_monthly_report.write('F4', 'including WinS', Italic_left_format)
    worksheet_monthly_report.write_formula('F5', '="compared to last year ("& Text(%s,"# ### ##0") & ")"'%int(max_ben_l_year), Italic_left_format)
    worksheet_monthly_report.write('F6', None, Title_format)


    worksheet_monthly_report.write_formula('F7', '="compared to last year ("& Text(%s,"# ### ##0") & ")"'%int(Lday_N_1), Italic_left_format)
    worksheet_monthly_report.write_formula('F8', '="Target 2023: " & (I5*12)*VLOOKUP("%s",I7:J18,2,)'%(Rate_by_month[ListDate[-1].month-1][0]), Italic_left_format)
    worksheet_monthly_report.write('F9', None, Title_format)

    worksheet_monthly_report.write('F10', 'compared to last year (%s)'%Site_active_l_year, Italic_left_format)
    worksheet_monthly_report.write('F11', 'compared to last month (%s)'%Site_active_l_month, Italic_left_grey_format)
    worksheet_monthly_report.write('F12', 'Target end 2021: %s kiosks' %300, Italic_left_format)
    worksheet_monthly_report.write('F13', None, Title_format)

    worksheet_monthly_report.write('F14', 'compared to last year (%s%%)'%int(round((Nb_tier_1_l_year/(Nb_tier_l_year+Nb_tier_1_l_year))*100)), Italic_left_format)
    worksheet_monthly_report.write('F15', 'Target %s %% Tier 1'%80, Italic_left_format)
    worksheet_monthly_report.write('F16', None, Title_format)

    worksheet_monthly_report.write_formula('F17', '="compared to last year ("& Text(%s,"# ### ##0") & ")"'%int(Price_last_year/Site_active_l_year), Italic_left_format)

    worksheet_monthly_report.write('E2:E17', None, Title_format)

def IndicatorsTeukSaat(workbook,Current_date,Date_N_1,Date_janv,Date_last_janv):
    from monthlyreport.TeukSaatIndicatorsEmail import compute_teuksaat_indicators, DEFAULT_CONSUMERS_OBJECTIVE
    from xlsxwriter.utility import xl_rowcol_to_cell

    ind = compute_teuksaat_indicators(
        report_month=Current_date,
        consumers_objective=DEFAULT_CONSUMERS_OBJECTIVE,
    )

    bg = '#D9E1F2'

    # ── Formats ──────────────────────────────────────────────────────
    title_fmt = workbook.add_format({
        'font': 'Calibri', 'bold': True, 'font_size': 16, 'bg_color': '#002060',
        'font_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter',
        'bottom': 1, 'top': 1,
    })
    col_hdr_fmt = workbook.add_format({
        'font': 'Calibri', 'bold': True, 'font_size': 12, 'bg_color': '#002060',
        'font_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter',
        'bottom': 1, 'top': 1,
    })
    section_fmt = workbook.add_format({
        'font': 'Calibri', 'bold': True, 'font_size': 13, 'bg_color': '#002060',
        'font_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter',
        'bottom': 1, 'top': 1,
    })
    metric_fmt = workbook.add_format({
        'font': 'Calibri', 'bold': True, 'font_size': 13, 'bg_color': bg,
        'font_color': '#1F4E78', 'align': 'left', 'valign': 'vcenter',
        'text_wrap': True, 'bottom': 1,
    })
    sub_metric_fmt = workbook.add_format({
        'font': 'Calibri', 'italic': True, 'font_size': 11, 'bg_color': bg,
        'font_color': '#0F172A', 'align': 'left', 'valign': 'vcenter',
        'text_wrap': True, 'bottom': 1,
    })
    val_fmt = workbook.add_format({
        'font': 'Calibri', 'bold': True, 'font_size': 13, 'bg_color': bg,
        'font_color': '#0F172A', 'align': 'right', 'valign': 'vcenter',
        'num_format': '# ### ##0', 'bottom': 1,
    })
    val_sub_fmt = workbook.add_format({
        'font': 'Calibri', 'italic': True, 'font_size': 11, 'bg_color': bg,
        'font_color': '#0F172A', 'align': 'right', 'valign': 'vcenter',
        'num_format': '# ### ##0', 'bottom': 1,
    })
    val_pct_fmt = workbook.add_format({
        'font': 'Calibri', 'italic': True, 'font_size': 11, 'bg_color': bg,
        'font_color': '#0F172A', 'align': 'right', 'valign': 'vcenter',
        'num_format': '0%', 'bottom': 1,
    })
    # Cell-level format for "vs" columns (wrap + bg + alignment)
    vs_cell = workbook.add_format({
        'font': 'Calibri', 'font_size': 11, 'bg_color': bg,
        'align': 'left', 'valign': 'vcenter', 'text_wrap': True, 'bottom': 1,
    })
    obj_cell = workbook.add_format({
        'font': 'Calibri', 'font_size': 11, 'bg_color': bg,
        'font_color': '#7C2D12', 'align': 'left', 'valign': 'vcenter',
        'text_wrap': True, 'bottom': 1,
    })
    # Rich-string fragment formats (font-only — no bg/alignment)
    f_normal  = workbook.add_format({'font': 'Calibri', 'font_size': 11, 'font_color': '#334155'})
    f_green   = workbook.add_format({'font': 'Calibri', 'font_size': 11, 'font_color': '#047857', 'bold': True})
    f_red     = workbook.add_format({'font': 'Calibri', 'font_size': 11, 'font_color': '#B91C1C', 'bold': True})
    f_obj     = workbook.add_format({'font': 'Calibri', 'font_size': 11, 'font_color': '#7C2D12'})
    f_sep     = workbook.add_format({'font': 'Calibri', 'font_size': 11, 'font_color': '#94A3B8'})
    Brown_format = workbook.add_format({'font_color': '#974706'})

    # ── Worksheet setup ──────────────────────────────────────────────
    ws = workbook.add_worksheet("TS1001 KPIs")
    ws.set_zoom(70)
    ws.set_column('A:A', 42)   # Indicator
    ws.set_column('B:B', 18)   # Current
    ws.set_column('C:C', 28)   # vs last year / month
    ws.set_column('D:D', 26)   # vs objective
    ws.set_default_row(20)

    # WinS beneficiaries override (hidden helper cells)
    ws.write('F1', "Beneficiaries WinS override:", Brown_format)
    ws.write('F2', ind.beneficiaries_wins, Brown_format)

    # ── Helpers ──────────────────────────────────────────────────────
    def _fi(v):
        """Format integer with thousands separator."""
        if v is None: return "\u2014"
        return f"{int(v):,}".replace(",", " ")

    def _fp(v):
        """Format as percentage string."""
        if v is None: return "\u2014"
        return f"{v * 100:.0f}%"

    def _fsi(v):
        """Format signed integer."""
        if v is None: return "\u2014"
        sign = "+" if v > 0 else ""
        return f"{sign}{int(v):,}".replace(",", " ")

    def _fsp(v):
        """Format signed percentage."""
        if v is None: return "\u2014"
        sign = "+" if v > 0 else ""
        return f"{sign}{v * 100:.0f}%"

    def _fspp(v):
        """Format signed percentage points."""
        if v is None: return "\u2014"
        sign = "+" if v > 0 else ""
        return f"{sign}{v * 100:.0f} pp"

    def _di(c, p):
        if c is None or p is None: return None
        return int(c) - int(p)

    def _pc(c, p):
        if c is None or p is None or p == 0: return None
        return float(c) / float(p) - 1.0

    def _dcol(v):
        """Pick green/red/neutral format for a delta value."""
        if v is None: return f_normal
        return f_green if v > 0 else (f_red if v < 0 else f_normal)

    def _dcol_obj(v):
        """Pick green/red for objective (>= 0 is green)."""
        if v is None: return f_normal
        return f_green if v >= 0 else f_red

    # ── "vs" column writers ──────────────────────────────────────────
    def _write_vs(r, c, curr, prev, label):
        """Rich cell: 'Label: prev_value\nΔ: +delta (+pct%)'"""
        if prev is None:
            ws.write(r, c, "", vs_cell)
            return
        d = _di(curr, prev)
        p = _pc(float(curr), float(prev))
        ws.write_rich_string(r, c,
            f_normal, f"{label}: {_fi(prev)}\n",
            f_normal, "\u0394: ",
            _dcol(d), f"{_fsi(d)} ({_fsp(p)})",
            vs_cell)

    def _write_vs_round(r, c, curr, prev, label):
        if curr is None or prev is None:
            ws.write(r, c, "", vs_cell)
            return
        _write_vs(r, c, int(round(curr)), int(round(prev)), label)

    def _write_vs_pct_pp(r, c, curr, prev, label):
        if curr is None or prev is None:
            ws.write(r, c, "", vs_cell)
            return
        d = curr - prev
        ws.write_rich_string(r, c,
            f_normal, f"{label}: {_fp(prev)}\n",
            f_normal, "\u0394: ",
            _dcol(d), _fspp(d),
            vs_cell)

    def _write_vs_active(r, c):
        """Special: shows both vs-last-month AND vs-last-year."""
        parts = []
        if ind.active_kiosks_last_month is not None:
            dm = _di(ind.active_kiosks, ind.active_kiosks_last_month)
            pm = _pc(float(ind.active_kiosks), float(ind.active_kiosks_last_month))
            parts += [
                f_normal, f"Last month: {_fi(ind.active_kiosks_last_month)}\n",
                f_normal, "\u0394: ",
                _dcol(dm), f"{_fsi(dm)} ({_fsp(pm)})",
            ]
        if ind.active_kiosks_last_year is not None:
            if parts:
                parts += [f_sep, "\n"]
            dy = _di(ind.active_kiosks, ind.active_kiosks_last_year)
            py = _pc(float(ind.active_kiosks), float(ind.active_kiosks_last_year))
            parts += [
                f_normal, f"Last year: {_fi(ind.active_kiosks_last_year)}\n",
                f_normal, "\u0394: ",
                _dcol(dy), f"{_fsi(dy)} ({_fsp(py)})",
            ]
        if len(parts) >= 4:
            ws.write_rich_string(r, c, *parts, vs_cell)
        else:
            ws.write(r, c, "", vs_cell)

    def _write_obj(r, c, curr, objective):
        """Rich cell: 'Objective: X\nΔ: +delta (+pct%)'"""
        if objective is None:
            ws.write(r, c, "", obj_cell)
            return
        d = int(curr) - int(objective)
        p = _pc(float(curr), float(objective))
        ws.write_rich_string(r, c,
            f_obj, f"Objective: {_fi(objective)}\n",
            f_obj, "\u0394: ",
            _dcol_obj(d), f"{_fsi(d)} ({_fsp(p)})",
            obj_cell)

    def _write_obj_round(r, c, curr, objective):
        if curr is None or objective is None:
            ws.write(r, c, "", obj_cell)
            return
        _write_obj(r, c, int(round(curr)), int(round(objective)))

    # ── Build the sheet ──────────────────────────────────────────────
    r = 0

    # Title
    ws.merge_range(r, 0, r, 3,
        "Teuk Saat 1001 Indicators \u2014 %s %s" % (calendar.month_name[Current_date.month], Current_date.year),
        title_fmt)
    ws.set_row(r, 30)
    r += 1

    # Column headers
    for ci, txt in enumerate(["Indicator", "Current", "vs last year / month", "vs objective"]):
        ws.write(r, ci, txt, col_hdr_fmt)
    ws.set_row(r, 22)
    r += 1

    # ═══════════════ MONTHLY ═══════════════
    ws.merge_range(r, 0, r, 3, "Monthly", section_fmt)
    ws.set_row(r, 22)
    r += 1

    # Row: Number of active kiosks
    ws.set_row(r, 72)
    active_row = r
    ws.write(r, 0, "Number of active kiosks", metric_fmt)
    ws.write(r, 1, ind.active_kiosks, val_fmt)
    _write_vs_active(r, 2)
    _write_obj(r, 3, ind.active_kiosks, ind.active_kiosks_objective)
    r += 1

    # Row: Nb Sites >= 3 Workers
    ws.set_row(r, 42)
    ws.write(r, 0, "Nb Sites \u2265 3 Workers", metric_fmt)
    ws.write(r, 1, ind.sites_gt_3_operators, val_fmt)
    _write_vs(r, 2, ind.sites_gt_3_operators, ind.sites_gt_3_operators_last_year, "Last year")
    _write_obj(r, 3, ind.sites_gt_3_operators, ind.sites_gt_3_operators_objective)
    r += 1

    # Row: B/day exc. WinS
    ws.set_row(r, 42)
    ws.write(r, 0, "B/day exc. WinS", metric_fmt)
    ws.write(r, 1, round(ind.bot_day_exc_wins) if ind.bot_day_exc_wins else 0, val_fmt)
    _write_vs_round(r, 2, ind.bot_day_exc_wins, ind.bot_day_exc_wins_last_year, "Last year")
    _write_obj_round(r, 3, ind.bot_day_exc_wins, ind.bot_day_exc_wins_objective)
    r += 1

    # Row: B/day inc. WinS  (sub-row)
    ws.set_row(r, 42)
    ws.write(r, 0, "B/day inc. WinS", sub_metric_fmt)
    ws.write(r, 1, round(ind.bot_day_inc_wins) if ind.bot_day_inc_wins else 0, val_sub_fmt)
    _write_vs_round(r, 2, ind.bot_day_inc_wins, ind.bot_day_inc_wins_last_year, "Last year")
    ws.write(r, 3, "", obj_cell)
    r += 1

    # ═══════════════ YTD ═══════════════
    ws.merge_range(r, 0, r, 3, "YTD", section_fmt)
    ws.set_row(r, 22)
    r += 1

    # Row: Total bottle sold exc. WinS
    ws.set_row(r, 42)
    ws.write(r, 0, "Total bottle sold exc. WinS", metric_fmt)
    ws.write(r, 1, ind.ytd_bot_exc_wins, val_fmt)
    _write_vs(r, 2, ind.ytd_bot_exc_wins, ind.ytd_bot_exc_wins_last_year, "Last year")
    _write_obj(r, 3, ind.ytd_bot_exc_wins, ind.ytd_objective_exc_wins)
    r += 1

    # Row: Total bottle sold inc. WinS  (sub-row)
    ws.set_row(r, 42)
    ws.write(r, 0, "Total bottle sold inc. WinS", sub_metric_fmt)
    ws.write(r, 1, ind.ytd_bot_inc_wins, val_sub_fmt)
    _write_vs(r, 2, ind.ytd_bot_inc_wins, ind.ytd_bot_inc_wins_last_year, "Last year")
    ws.write(r, 3, "", obj_cell)
    r += 1

    # Row: Like-for-Like (YTD)
    ws.set_row(r, 42)
    ws.write(r, 0, "Total Sales (Bot) LFL exc. WinS (YTD)", metric_fmt)
    ws.write(r, 1, ind.lfl_ytd_bot_exc_wins, val_fmt)
    _write_vs(r, 2, ind.lfl_ytd_bot_exc_wins, ind.lfl_ytd_bot_exc_wins_last_year, "Last year")
    _write_obj(r, 3, ind.lfl_ytd_bot_exc_wins, ind.lfl_ytd_objective_exc_wins)
    r += 1

    # ═══════════════ 12 MONTHS ═══════════════
    ws.merge_range(r, 0, r, 3, "12 Months", section_fmt)
    ws.set_row(r, 22)
    r += 1

    # Row: Consumers
    ws.set_row(r, 42)
    ws.write(r, 0, "Consumers", metric_fmt)
    ws.write(r, 1, ind.consumers, val_fmt)
    _write_vs(r, 2, ind.consumers, ind.consumers_last_year, "Last year")
    _write_obj(r, 3, ind.consumers, ind.consumers_objective)
    r += 1

    # Row: Beneficiaries WinS
    ws.set_row(r, 22)
    ws.write(r, 0, "Beneficiaries WinS", metric_fmt)
    ws.write_formula(r, 1, "=F2", val_fmt)
    ws.write(r, 2, "", vs_cell)
    ws.write(r, 3, "", obj_cell)
    r += 1

    # Row: Number of ST1
    ws.set_row(r, 42)
    st1_row = r
    ws.write(r, 0, "Number of ST1", metric_fmt)
    ws.write(r, 1, ind.st1_count, val_fmt)
    _write_vs(r, 2, ind.st1_count, ind.st1_count_last_year, "Last year")
    _write_obj(r, 3, ind.st1_count, 125)
    r += 1

    # Row: % of ST1  (sub-row)
    ws.set_row(r, 42)
    ws.write(r, 0, "% of ST1", sub_metric_fmt)
    # Formula: =ST1_value / Active_kiosks_value
    st1_cell = xl_rowcol_to_cell(st1_row, 1)
    active_cell = xl_rowcol_to_cell(active_row, 1)
    ws.write_formula(r, 1, "=%s/%s" % (st1_cell, active_cell), val_pct_fmt)
    _write_vs_pct_pp(r, 2, ind.st1_pct, ind.st1_pct_last_year, "Last year")
    ws.write(r, 3, "", obj_cell)
    r += 1


def CreateKPI(workbook,Current_date,Date_1,Platform_List,exchange_rate):
    if Current_date.month - Date_1.month == 1:
        worksheet = workbook.add_worksheet("KPI %s'%s%s"%(Current_date.strftime("%b"),str(Current_date.year)[2],str(Current_date.year)[3]))
    else:
        worksheet = workbook.add_worksheet("KPI %s'%s%s %s'%s%s"%((Date_1+relativedelta(months=+1)).strftime("%b"),str(Date_1.year)[2],str(Date_1.year)[3],Current_date.strftime("%b"),str(Current_date.year)[2],str(Current_date.year)[3]))

    Tier = KPIFormat(workbook,worksheet,Current_date,Date_1,Platform_List)
    KPINbSite(workbook,worksheet,2,Current_date,Date_1,Tier,Platform_List)
    KPINbSitePercentage(workbook,worksheet,12,Current_date,Date_1,Tier,Platform_List)
    KPIBeneficiaries(workbook,worksheet,21,Current_date,Date_1,Tier,Platform_List)
    KPIBotDay(workbook,worksheet,30,Current_date,Date_1,Tier,Platform_List,False)
    KPIBotDay(workbook,worksheet,40,Current_date,Date_1,Tier,Platform_List,True)
    KPITotBot(workbook,worksheet,50,Current_date,Date_1,Tier,Platform_List,False)
    KPITotBot(workbook,worksheet,59,Current_date,Date_1,Tier,Platform_List,True,True)
    KPITotInc(workbook,worksheet,68,Current_date,Date_1,Tier,Platform_List,exchange_rate,True)
    KPISalaryEnt(workbook,worksheet,77,Current_date,Date_1,Tier,Platform_List,exchange_rate)
    KPIPL(workbook,worksheet,86,Current_date,Date_1,Tier,Platform_List,exchange_rate)
    KPINbSiteMoreThan3Operators(workbook,worksheet,95,Current_date,Date_1,Tier,Platform_List)
    KPINbSiteMoreThan3OperatorsPercentage(workbook,worksheet,104,Current_date,Date_1,Tier,Platform_List)
    KPITotBotLikeForLike(workbook,worksheet,113,Current_date,Date_1,Tier,Platform_List)
    KPITotBotLikeForLikeGrowth(workbook,worksheet,122,Current_date,Date_1,Tier,Platform_List)

def LaunchExcelCreationKPI(Current_date, exchange_rate):
    con= db.pool.connect()
    Date_janv_1 = date(Current_date.year-1,12,1)
    Date_N_1 = date(Current_date.year-1,Current_date.month,1)
    Date_N_2 = date(Current_date.year-2,Current_date.month,1)
    Date_M_1 = Current_date - relativedelta(months=+1)

    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir()+'/KPI '+Year+ '-' +Month+'.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    Platform_List = con.execute("SELECT DISTINCT Code_Platform FROM Platform").fetchall()

    CreateKPI(workbook,Current_date,Date_M_1,Platform_List,exchange_rate)
    CreateKPI(workbook,Current_date,Date_janv_1,Platform_List,exchange_rate)
    if Date_janv_1 != Date_N_1:
        CreateKPI(workbook,Current_date,Date_N_1,Platform_List,exchange_rate)
    #KPI1001fontaines(ListDate,ListSiteActive,Tier_this_year,Tier_last_year,ListOpenDayThisYear,ListOpenDayLastYear)
    workbook.close()
