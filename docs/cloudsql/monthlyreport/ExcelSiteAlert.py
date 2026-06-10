import db
from monthlyreport.Functionutils import listSiteStillActive,CalculNombreMoisOuverture,Numberdaysopeningyear
from dateutil.relativedelta import *
from datetime import date
import xlsxwriter
from calendar import monthrange
import tempfile



def LaunchExcelCreationAlert(Current_date,ListSiteActive):
    Date_N_1 = Current_date - relativedelta(months=+12)
    con = db.pool.connect()
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir()+'/Alert Site Report '+Year+'-'+Month+'.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    worksheet_decreaseSite = workbook.add_worksheet("Decreasing Sites")
    worksheet_closeSite = workbook.add_worksheet("Sites Closed this month")
    worksheet_newSites = workbook.add_worksheet("New Sites")
    worksheet_data = workbook.add_worksheet("Data")
    worksheet_data_noWinS = workbook.add_worksheet("Data no WinS")
    query = con.execute("SELECT (Total_Sales-Bottle_Sales)*20,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d'),Number_open_days FROM Sales WHERE Month >= %s ", Date_N_1 -relativedelta(months=+12))
    allSalesSites = query.fetchall()

    query = con.execute("SELECT (Total_Sales-Bottle_Sales-WiS_Sales)*20,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d'),Number_open_days FROM Sales WHERE Month >= %s",Date_N_1 -relativedelta(months=+12))
    allSalesSites_nowins = query.fetchall()
    query = con.execute("SELECT SUM(Total_Sales),Id_Site FROM Sales WHERE Month <= %s GROUP BY Id_Site",Date_N_1)
    allOld_Sales = query.fetchall()
    query = con.execute("SELECT Id_Site,Platform,Advisor FROM Sites")
    allInfoSite = query.fetchall()

    WinS_format = workbook.add_format({'font_size' : 15, 'font_color' : 'red', 'bold' : True})
    Txt_format = workbook.add_format({'bold' : True})
    j=0
    l=0
    k=0
    worksheet_data.write(1,0,'Site')
    worksheet_data.write(1,1,'Platform')
    worksheet_data.write(1,2,'Advisor')
    worksheet_data.write(1,3,'M')
    worksheet_data.write(1,4,'M-1')
    worksheet_data.write(1,5,'M-2')
    worksheet_data.write(1,6,'M-3')
    worksheet_data.write(1,7,'M-4')
    worksheet_data.write(1,8,'M-5')
    worksheet_data.write(1,9,'M-6')
    worksheet_data.write(1,10,'M-7')
    worksheet_data.write(1,11,'M-8')
    worksheet_data.write(1,12,'M-9')
    worksheet_data.write(1,13,'M-10')
    worksheet_data.write(1,14,'M-11')
    worksheet_data.write(1,15,'M-12')
    worksheet_data.write(1,16,'M-13')
    worksheet_data.write(1,17,'M-14')
    worksheet_data.write(1,18,'M-15')
    worksheet_data.write(1,19,'M-16')
    worksheet_data.write(1,20,'M-17')
    worksheet_data.write(1,21,'M-18')
    worksheet_data.write(1,22,'M-19')
    worksheet_data.write(1,23,'M-20')
    worksheet_data.write(1,24,'M-21')
    worksheet_data.write(1,25,'M-22')
    worksheet_data.write(1,26,'M-23')
    worksheet_data.write(1,27,'M-24')
    worksheet_data.write(1,29,'Sum N')
    worksheet_data.write(1,30,'Sum N-1')
    worksheet_data.set_column('C:C',len('M-12 vs M-24   '))

    worksheet_data_noWinS.write(1,0,'Site')
    worksheet_data_noWinS.write(1,1,'Platform')
    worksheet_data_noWinS.write(1,2,'Advisor')
    worksheet_data_noWinS.write(1,3,'M')
    worksheet_data_noWinS.write(1,4,'M-1')
    worksheet_data_noWinS.write(1,5,'M-2')
    worksheet_data_noWinS.write(1,6,'M-3')
    worksheet_data_noWinS.write(1,7,'M-4')
    worksheet_data_noWinS.write(1,8,'M-5')
    worksheet_data_noWinS.write(1,9,'M-6')
    worksheet_data_noWinS.write(1,10,'M-7')
    worksheet_data_noWinS.write(1,11,'M-8')
    worksheet_data_noWinS.write(1,12,'M-9')
    worksheet_data_noWinS.write(1,13,'M-10')
    worksheet_data_noWinS.write(1,14,'M-11')
    worksheet_data_noWinS.write(1,15,'M-12')
    worksheet_data_noWinS.write(1,16,'M-13')
    worksheet_data_noWinS.write(1,17,'M-14')
    worksheet_data_noWinS.write(1,18,'M-15')
    worksheet_data_noWinS.write(1,19,'M-16')
    worksheet_data_noWinS.write(1,20,'M-17')
    worksheet_data_noWinS.write(1,21,'M-18')
    worksheet_data_noWinS.write(1,22,'M-19')
    worksheet_data_noWinS.write(1,23,'M-20')
    worksheet_data_noWinS.write(1,24,'M-21')
    worksheet_data_noWinS.write(1,25,'M-22')
    worksheet_data_noWinS.write(1,26,'M-23')
    worksheet_data_noWinS.write(1,27,'M-24')
    worksheet_data_noWinS.write(1,29,'Sum N')
    worksheet_data_noWinS.write(1,30,'Sum N-1')
    worksheet_data_noWinS.set_column('C:C',len('M-12 vs M-24   '))

    worksheet_decreaseSite.write(0,0,'Select With or Without WinS',Txt_format)
    worksheet_decreaseSite.data_validation('D1',{'validate' : 'list',
                                    'source' : ['With WinS', 'Without WinS']})
    worksheet_decreaseSite.write(0,3,"With WinS",WinS_format)
    worksheet_decreaseSite.write(1,0,'Site')
    worksheet_decreaseSite.write(1,1,'Platform')
    worksheet_decreaseSite.write(1,2,'Advisor')
    worksheet_decreaseSite.write(1,3,'M vs M-12')
    worksheet_decreaseSite.write(1,4,'Quart N vs Quart N-1')
    worksheet_decreaseSite.write(1,5,'Sem N vs Sem N-1')
    worksheet_decreaseSite.write(1,6,'N vs N-1')
    worksheet_decreaseSite.set_column('C:H',len('M-12 vs M-24   '))


    worksheet_newSites.write(0,0,'Select With or Without WinS',Txt_format)
    worksheet_newSites.data_validation('D1',{'validate' : 'list',
                                    'source' : ['With WinS', 'Without WinS']})
    worksheet_newSites.write(0,3,"With WinS",WinS_format)
    worksheet_newSites.write(1,0,'Site')
    worksheet_newSites.write(1,1,'Platform')
    worksheet_newSites.write(1,2,'Advisor')
    worksheet_newSites.write(1,3,'M')
    worksheet_newSites.write(1,4,'M-3')
    worksheet_newSites.write(1,5,'M-6')
    worksheet_newSites.write(1,6,'M-9')
    worksheet_newSites.write(1,8,'M vs M-3')
    worksheet_newSites.write(1,9,'M vs M-6')
    worksheet_newSites.write(1,10,'M vs M-9')
    worksheet_newSites.set_column('C:C',len('M-12 vs M-24   '))

    worksheet_closeSite.write(0,0,'Select With or Without WinS',Txt_format)
    worksheet_closeSite.data_validation('D1',{'validate' : 'list',
                                    'source' : ['With WinS', 'Without WinS']})
    worksheet_closeSite.write(0,3,"With WinS",WinS_format)
    worksheet_closeSite.write(1,0,'Site')
    worksheet_closeSite.write(1,1,'Platform')
    worksheet_closeSite.write(1,2,'Advisor')
    worksheet_closeSite.write(1,3,'Closing Date')
    worksheet_closeSite.write(1,4,'Quart N vs Quart N-1')
    worksheet_closeSite.write(1,5,'Sem N vs Sem N-1')
    worksheet_closeSite.write(1,6,'N vs N-1')
    worksheet_closeSite.set_column('C:H',len('M-12 vs M-24   '))

    Percentage_format = workbook.add_format({'num_format' : '0.0%','border' : 1})
    Site_format = workbook.add_format({'bg_color' : '#D9D9D9'})
    Number_format = workbook.add_format({'num_format' : '# ##0','border' : 1})
    Date_format = workbook.add_format({'num_format' : 'yyyy-mm-dd','border' : 1})

    ListDate = []
    for inc in range(25):
        ListDate.append(Current_date - relativedelta(months=+inc))
    for i in range(len(ListSiteActive)):
        InfoSite = list(filter(lambda row: row[0] == ListSiteActive[i][0], allInfoSite))
        allSales = list(filter(lambda row: row[1] == ListSiteActive[i][0], allSalesSites))

        Current_sales = list(filter(lambda row: row[2] == str(Current_date), allSales))
        LastMonth_sales = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+1)), allSales))

        Date_N_1_sales = list(filter(lambda row: row[2] == str(Date_N_1), allSales))
        M_3_N_sales = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+3)), allSales))
        M_3_N_1_sales = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+3)), allSales))
        M_6_N_sales = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+6)), allSales))
        M_6_N_1_sales = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+6)), allSales))
        M_9_N_sales = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+9)), allSales))
        M_9_N_1_sales = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+9)), allSales))
        M_12_N_1_sales = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+12)), allSales))

        allSales_noWins = list(filter(lambda row: row[1] == ListSiteActive[i][0], allSalesSites_nowins))

        Current_sales_noWins = list(filter(lambda row: row[2] == str(Current_date), allSales_noWins))
        LastMonth_sales_noWins = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+1)), allSales_noWins))

        Date_N_1_sales_noWins = list(filter(lambda row: row[2] == str(Date_N_1), allSales_noWins))
        M_3_N_sales_noWins = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+3)), allSales_noWins))
        M_3_N_1_sales_noWins = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+3)), allSales_noWins))
        M_6_N_sales_noWins = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+6)), allSales_noWins))
        M_6_N_1_sales_noWins = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+6)), allSales_noWins))
        M_9_N_sales_noWins = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+9)), allSales_noWins))
        M_9_N_1_sales_noWins = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+9)), allSales_noWins))
        M_12_N_1_sales_noWins = list(filter(lambda row: row[2] == str(Date_N_1-relativedelta(months=+12)), allSales_noWins))

        worksheet_data.write(i+2,0,ListSiteActive[i][0],Site_format)
        worksheet_data.write(i+2,1,InfoSite[0][1],Site_format)
        worksheet_data.write(i+2,2,InfoSite[0][2],Site_format)

        for m in range(len(ListDate)):
            Volume = list(filter(lambda row: row[2] == str(ListDate[m]), allSales))
            Volume_no_wins = list(filter(lambda row: row[2] == str(ListDate[m]), allSales_noWins))
            Number_days = monthrange(ListDate[m].year,ListDate[m].month)[1]
            if Volume and Volume[0][0] and Volume[0][0] != 0 and Volume[0][3] !=0:
                if Volume[0][3] and Volume[0][3]< 20 :
                    worksheet_data.write(i+2,m+3,float(((Volume[0][0])/Volume[0][3])),Number_format)
                    if m ==0 and Current_sales:
                        Current_sales_Lday = Current_sales[0][0]/Volume[0][3]
                    elif m==11 and Date_N_1_sales:
                        Sales_N_1_Lday = Date_N_1_sales[0][0]/Volume[0][3]
                else:
                    if Volume[0][0]:
                        worksheet_data.write(i+2,m+3,float(((Volume[0][0])/Number_days)),Number_format)
                        if m ==0 and Current_sales:
                            Current_sales_Lday = Current_sales[0][0]/Number_days
                        elif m==12 and Date_N_1_sales:
                            Sales_N_1_Lday = Date_N_1_sales[0][0]/Number_days
            if Volume_no_wins and Volume_no_wins[0][0] and Volume_no_wins[0][0] != 0 and Volume_no_wins[0][3] !=0:
                if Volume_no_wins[0][3] and Volume_no_wins[0][3]< 20 :
                    worksheet_data_noWinS.write(i+2,m+3,float(((Volume_no_wins[0][0])/Volume_no_wins[0][3])),Number_format)
                    if m ==0 and Current_sales_noWins:
                        Current_sales_Lday_noWins = Current_sales_noWins[0][0]/Volume[0][3]
                    elif m==12 and Date_N_1_sales_noWins:
                        Sales_N_1_Lday_noWins = Date_N_1_sales_noWins[0][0]/Volume[0][3]
                else:
                    if Volume_no_wins[0][0]:
                        worksheet_data_noWinS.write(i+2,m+3,float(((Volume_no_wins[0][0])/Number_days)),Number_format)
                        if m ==0 and Current_sales_noWins:
                            Current_sales_Lday_noWins = Current_sales_noWins[0][0]/Number_days
                        elif m==12 and Date_N_1_sales_noWins:
                            Sales_N_1_Lday_noWins = Date_N_1_sales_noWins[0][0]/Number_days


        worksheet_data_noWinS.write(i+2,0,ListSiteActive[i][0],Site_format)
        worksheet_data_noWinS.write(i+2,1,InfoSite[0][1],Site_format)
        worksheet_data_noWinS.write(i+2,2,InfoSite[0][2],Site_format)
        worksheet_data_noWinS.write_formula(i+2,29,'=SUM($A%s:$O%s)'%(i+3,i+3),Number_format)
        worksheet_data_noWinS.write_formula(i+2,30,'=SUM($P%s:$AA%s)'%(i+3,i+3),Number_format)
        worksheet_data.write_formula(i+2,29,'=SUM($A%s:$O%s)'%(i+3,i+3),Number_format)
        worksheet_data.write_formula(i+2,30,'=SUM($P%s:$AA%s)'%(i+3,i+3),Number_format)


        Old_Sales = list(filter(lambda row: row[1] == ListSiteActive[i][0], allOld_Sales))
        if not Old_Sales:
            worksheet_newSites.write(l+2,0,ListSiteActive[i][0],Site_format)
            worksheet_newSites.write(l+2,1,InfoSite[0][1],Site_format)
            worksheet_newSites.write(l+2,2,InfoSite[0][2],Site_format)
            worksheet_newSites.write_formula(l+2,3,"=IFERROR(IF($D$1=\"With WinS\",INDEX(Data!$D$3:$D$%s,MATCH($A%s,Data!$A$3:$A$%s)),INDEX('Data no WinS'!$D$3:$D$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,l+3,len(ListSiteActive)+2,len(ListSiteActive)+2,l+3,len(ListSiteActive)+2),Number_format)
            worksheet_newSites.write_formula(l+2,4,"=IFERROR(IF($D$1=\"With WinS\",INDEX(Data!$G$3:$G$%s,MATCH($A%s,Data!$A$3:$A$%s)),INDEX('Data no WinS'!$G$3:$G$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,l+3,len(ListSiteActive)+2,len(ListSiteActive)+2,l+3,len(ListSiteActive)+2),Number_format)
            worksheet_newSites.write_formula(l+2,5,"=IFERROR(IF($D$1=\"With WinS\",INDEX(Data!$J$3:$J$%s,MATCH($A%s,Data!$A$3:$A$%s)),INDEX('Data no WinS'!$J$3:$J$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,l+3,len(ListSiteActive)+2,len(ListSiteActive)+2,l+3,len(ListSiteActive)+2),Number_format)
            worksheet_newSites.write_formula(l+2,6,"=IFERROR(IF($D$1=\"With WinS\",INDEX(Data!$M$3:$M$%s,MATCH($A%s,Data!$A$3:$A$%s)),INDEX('Data no WinS'!$M$3:$M$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,l+3,len(ListSiteActive)+2,len(ListSiteActive)+2,l+3,len(ListSiteActive)+2),Number_format)

            worksheet_newSites.write_formula(l+2,8,"IFERROR((D%s/E%s)-1,0)"%(l+3,l+3),Percentage_format)
            worksheet_newSites.write_formula(l+2,9,"IFERROR((D%s/F%s)-1,0)"%(l+3,l+3),Percentage_format)
            worksheet_newSites.write_formula(l+2,10,"IFERROR((D%s/G%s)-1,0)"%(l+3,l+3),Percentage_format)
            l+=1

        elif not Current_sales:
            worksheet_closeSite.write(k+2,0,ListSiteActive[i][0],Site_format)
            worksheet_closeSite.write(k+2,1,InfoSite[0][1],Site_format)
            worksheet_closeSite.write(k+2,2,InfoSite[0][2],Site_format)
            query = con.execute("SELECT MAX(Closing_date) FROM Closure WHERE Id_Site = %s",(ListSiteActive[i][0]))
            date_closing = query.fetchall()
            if date_closing:
                worksheet_closeSite.write(k+2,3,date_closing[0][0],Date_format)

            worksheet_closeSite.write_formula(k+2,4,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$D$3:$F$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$R$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$R$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$D$3:$F$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$R$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$R$%s))),0)"%(len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2),Percentage_format)

            worksheet_closeSite.write_formula(k+2,5,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$D$3:$I$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$U$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$U$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$D$3:$I$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$U$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$U$%s))),0)"%(len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2),Percentage_format)

            worksheet_closeSite.write_formula(k+2,6,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$D$3:$O$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$AA$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$AA$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$D$3:$O$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$AA$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$AA$%s))),0)"%(len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2,len(ListSiteActive)+2,k+3,len(ListSiteActive)+2),Percentage_format)


            k=k+1


        # if Current_sales and Sales_N_1_Lday:
        #     print(Current_sales_Lday, Sales_N_1_Lday)
        #     wait = input("go")
        if Date_N_1_sales and Sales_N_1_Lday and (Current_sales and (Current_sales_Lday-Sales_N_1_Lday)/Sales_N_1_Lday<-0.1):

            worksheet_decreaseSite.write(2+j,0,ListSiteActive[i][0],Site_format)
            worksheet_decreaseSite.write(j+2,1,InfoSite[0][1],Site_format)
            worksheet_decreaseSite.write(j+2,2,InfoSite[0][2],Site_format)
            worksheet_decreaseSite.write_formula(j+2,3,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$D$3:$D$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$P$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$P$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$D$3:$D$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$P$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$P$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)

            worksheet_decreaseSite.write_formula(j+2,4,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$D$3:$F$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$R$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$R$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$D$3:$F$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$R$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$R$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)

            worksheet_decreaseSite.write_formula(j+2,5,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$D$3:$I$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$U$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$U$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$D$3:$I$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$U$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$U$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)

            worksheet_decreaseSite.write_formula(j+2,6,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$D$3:$O$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$AA$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A%s)*(Data!$P$3:$AA$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$D$3:$O$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$AA$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A%s)*('Data no WinS'!$P$3:$AA$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)

            # worksheet_decreaseSite.write_formula(j+2,3,"=IFERROR(IF($D$1=\"With WinS\",(SUMPRODUCT((Data!$A$3:$A$%s=$A$%s)*(Data!$D$3:$D$%s))-SUMPRODUCT((Data!$A$3:$A$%s=$A$%s)*(Data!$P$3:$P$%s)))/SUMPRODUCT((Data!$A$3:$A$%s=$A$%s)*(Data!$P$3:$P$%s)),(SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A$%s)*(Data!$D$3:$D$%s))-SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A$%s)*(Data!$P$3:$P$%s)))/SUMPRODUCT(('Data no WinS'!$A$3:$A$%s=$A$%s)*(Data!$P$3:$P$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)
            #
            #
            #
            #
            # worksheet_decreaseSite.write_formula(j+2,4,"=IFERROR(IF($D$1=\"With WinS\",(INDEX(Data!$G$3:$G$%s,MATCH($A%s,Data!$A$3:$A$%s))-INDEX(Data!$S$3:$S$%s,MATCH($A%s,Data!$A$3:$A$%s)))/INDEX(Data!$S$3:$S$%s,MATCH($A%s,Data!$A$3:$A$%s)),(INDEX('Data no WinS'!$G$3:$G$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))-INDEX('Data no WinS'!$S$3:$S$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s)))/INDEX('Data no WinS'!$S$3:$S$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)
            #
            # worksheet_decreaseSite.write_formula(j+2,5,"=IFERROR(IF($D$1=\"With WinS\",(INDEX(Data!$J$3:$J$%s,MATCH($A%s,Data!$A$3:$A$%s))-INDEX(Data!$V$3:$V$%s,MATCH($A%s,Data!$A$3:$A$%s)))/INDEX(Data!$V$3:$V$%s,MATCH($A%s,Data!$A$3:$A$%s)),(INDEX('Data no WinS'!$J$3:$J$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))-INDEX('Data no WinS'!$V$3:$V$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s)))/INDEX('Data no WinS'!$V$3:$V$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)
            #
            # worksheet_decreaseSite.write_formula(j+2,6,"=IFERROR(IF($D$1=\"With WinS\",(INDEX(Data!$M$3:$M$%s,MATCH($A%s,Data!$A$3:$A$%s))-INDEX(Data!$Y$3:$Y$%s,MATCH($A%s,Data!$A$3:$A$%s)))/INDEX(Data!$Y$3:$Y$%s,MATCH($A%s,Data!$A$3:$A$%s)),(INDEX('Data no WinS'!$M$3:$M$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))-INDEX('Data no WinS'!$Y$3:$Y$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s)))/INDEX('Data no WinS'!$Y$3:$Y$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)
            #
            # worksheet_decreaseSite.write_formula(j+2,7,"=IFERROR(IF($D$1=\"With WinS\",(INDEX(Data!$P$3:$P$%s,MATCH($A%s,Data!$A$3:$A$%s))-INDEX(Data!$AB$3:$AB$%s,MATCH($A%s,Data!$A$3:$A$%s)))/INDEX(Data!$AB$3:$AB$%s,MATCH($A%s,Data!$A$3:$A$%s)),(INDEX('Data no WinS'!$P$3:$P$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))-INDEX('Data no WinS'!$AB$3:$AB$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s)))/INDEX('Data no WinS'!$AB$3:$AB$%s,MATCH($A%s,'Data no WinS'!$A$3:$A$%s))),0)"%(len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2,len(ListSiteActive)+2,j+3,len(ListSiteActive)+2),Percentage_format)

            j=j+1
    worksheet_decreaseSite.autofilter(1,0,j+2,6)
    worksheet_closeSite.autofilter(1,0,k+2,6)
    worksheet_newSites.autofilter(1,0,l+2,6)
    worksheet_data.autofilter(1,0,len(ListSiteActive)+2,14)
    worksheet_data_noWinS.autofilter(1,0,len(ListSiteActive)+2,14)
    workbook.close()

if __name__ == '__main__':
    Current_date = date(2021,10,1)
    Date_N_1 = date(2020,10,1)

    ListSiteActive = listSiteStillActive(Current_date,Date_N_1)
    LaunchExcelCreationAlert(Current_date,ListSiteActive)
