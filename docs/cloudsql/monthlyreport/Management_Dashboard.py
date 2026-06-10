import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell,xl_col_to_name
import db
from datetime import date
import calendar
import tempfile
from dateutil.relativedelta import *
from monthlyreport.Functionutils import ConsumableType,exchange_rate_year,NewCalculTier


def TabData(workbook,Current_date,exchange_rate):
    con=db.pool.connect()

    #GENERAL FORMAT
    Title = workbook.add_format({'bg_color':'#ED7D31','bold':True,'center_across': True})
    Date_format = workbook.add_format({'num_format' : 'yyyy-mm'})
    grey_format = workbook.add_format({'bg_color': '#C0C0C0'})
    Number_format = workbook.add_format({'num_format':'# ### ### ##0'})
    Percentage_format = workbook.add_format({'num_format':'0%'})
    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    Bold_Percentage_format = workbook.add_format({'num_format':'0%','bold': True,'center_across':True})
    worksheet_1Kioks = workbook.add_worksheet("1.Kiosks")
    worksheet_1Kioks.set_zoom(100)
    worksheet_1Kioks.set_tab_color('#8EA9DB')

    worksheet_2Volume = workbook.add_worksheet("2.Volumes")
    worksheet_2Volume.set_zoom(85)
    worksheet_2Volume.set_tab_color('#92D050')

    worksheet_3ChannelMix = workbook.add_worksheet("3.Channel Mix")
    worksheet_3ChannelMix.set_zoom(85)
    worksheet_3ChannelMix.set_tab_color('#C00000')

    worksheet_4SitesRevenues = workbook.add_worksheet("4.Sites Revenues")
    worksheet_4SitesRevenues.set_zoom(85)
    worksheet_4SitesRevenues.set_tab_color('#305496')

    worksheet_5Consumables = workbook.add_worksheet("5.Consumables")
    worksheet_5Consumables.set_zoom(85)
    worksheet_5Consumables.set_tab_color('#BF8F00')

    worksheet_6Debts = workbook.add_worksheet("6.Debts")
    worksheet_6Debts.set_zoom(85)
    worksheet_6Debts.set_tab_color('#808080')

###########SELECT DATAFIRST TAB 'KIOSKS'##########
    Site_that_closed_this_month = con.execute("SELECT Sales.Id_Site,Platform FROM Sales JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month=%s AND Sales.Id_Site NOT IN (SELECT Sales.Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) AND Sales.Id_Site IN (SELECT Sales.Id_Site FROM Sales WHERE MONTH = %s AND Total_Sales IS NOT NULL) ORDER BY Sales.Id_Site",(Current_date-relativedelta(months=+1),Current_date,Current_date-relativedelta(months=+1))).fetchall()
    Sales_of_Site_that_closed_this_month = con.execute("SELECT Total_Sales,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales WHERE Month<=%s AND Month > %s AND Id_Site NOT IN (SELECT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) AND Id_Site IN (SELECT Id_Site FROM Sales WHERE MONTH = %s AND Total_Sales IS NOT NULL) ORDER BY Id_Site",(Current_date,Current_date-relativedelta(months=+12),Current_date,Current_date-relativedelta(months=+1))).fetchall()
    Site_that_opened_this_month = con.execute("SELECT Total_Sales,Sales.Id_Site,Platform FROM Sales JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month=%s AND Sales.Id_Site IN (SELECT Sales.Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) AND Sales.Id_Site NOT IN (SELECT Sales.Id_Site FROM Sales WHERE MONTH = %s AND Total_Sales IS NOT NULL) ORDER BY Sales.Id_Site",(Current_date,Current_date,Current_date-relativedelta(months=+1))).fetchall()

########WRITE DATA#############""
    #FIRST TABLE IN 1KIOSK

    List_date =[]
    Date = Current_date-relativedelta(months=+11)
    while Date<= Current_date:
        List_date.append(Date)
        Date = Date + relativedelta(months=+1)
    columns_settings = [{'header' : 'Site'},
                        {'header' : 'Platform'}] + [{'header' : str(s.year) + '-' + str(s.month), 'header_format' : Date_format} for s in List_date]
    worksheet_1Kioks.add_table(4,0,len(Site_that_closed_this_month)+4,len(List_date)+1, {'columns' : columns_settings})

    worksheet_1Kioks.merge_range(0,0,0,7,"Closed sites this month (bottles/month)",Title)
    worksheet_1Kioks.write('B3','Total bottles',Bold_Number_format)
    worksheet_1Kioks.write('B4','Nb Sites',Bold_Number_format)
    for k in range(len(List_date)):
        all_Site_closed_per_month = list(filter(lambda row: row[2] == str(List_date[k]), Sales_of_Site_that_closed_this_month))
        worksheet_1Kioks.write_formula(2,k+2,'IFERROR(SUBTOTAL(1,%s6:%s),0)'%(xl_col_to_name(k+2),xl_rowcol_to_cell(len(Site_that_closed_this_month)+4,k+2)),Bold_Number_format)
        worksheet_1Kioks.write_formula(3,k+2,'IFERROR(SUBTOTAL(3,%s6:%s),0)'%(xl_col_to_name(k+2),xl_rowcol_to_cell(len(Site_that_closed_this_month)+4,k+2)),Bold_Number_format)

        for i in range(len(Site_that_closed_this_month)):
            Site_closed_now = list(filter(lambda row: row[1] == Site_that_closed_this_month[i][0], all_Site_closed_per_month))
            worksheet_1Kioks.write(i+5,0,Site_that_closed_this_month[i][0])
            worksheet_1Kioks.write(i+5,1,Site_that_closed_this_month[i][1])
            if Site_closed_now:
                worksheet_1Kioks.write(i+5,k+2,Site_closed_now[0][0],Number_format)
            else:
                worksheet_1Kioks.write(i+5,k+2,None,grey_format)

    #SECOND TABLE IN 1KIOSK

    columns_settings = [{'header' : 'Site'},
                        {'header' : 'Platform'},
                        {'header' : str(Current_date.year) + '-' + str(Current_date.month), 'header_format' : Date_format}]
    worksheet_1Kioks.add_table(len(Site_that_closed_this_month)+12,0,len(Site_that_closed_this_month)+12+len(Site_that_opened_this_month),2,{'columns' : columns_settings})

    worksheet_1Kioks.merge_range(len(Site_that_closed_this_month)+8,0,len(Site_that_closed_this_month)+8,7,'Opening sites this month (bottles/month)',Title)
    worksheet_1Kioks.write(len(Site_that_closed_this_month)+10,1,'Total bottles',Bold_Number_format)
    worksheet_1Kioks.write(len(Site_that_closed_this_month)+11,1,'Nb sites',Bold_Number_format)
    worksheet_1Kioks.write_formula(len(Site_that_closed_this_month)+10,2,'IFERROR(SUBTOTAL(9,C%s:C%s),0)'%(len(Site_that_closed_this_month)+14,len(Site_that_closed_this_month)+13+len(Site_that_opened_this_month)),Bold_Number_format)
    worksheet_1Kioks.write_formula(len(Site_that_closed_this_month)+11,2,'IFERROR(SUBTOTAL(3,C%s:C%s),0)'%(len(Site_that_closed_this_month)+14,len(Site_that_closed_this_month)+13+len(Site_that_opened_this_month)),Bold_Number_format)
    for j in range(len(Site_that_opened_this_month)):
        worksheet_1Kioks.write(len(Site_that_closed_this_month)+13+j,0,Site_that_opened_this_month[j][1])
        worksheet_1Kioks.write(len(Site_that_closed_this_month)+13+j,1,Site_that_opened_this_month[j][2])
        worksheet_1Kioks.write(len(Site_that_closed_this_month)+13+j,2,Site_that_opened_this_month[j][0])

#########SELECT DATA SECOND TAB VOLUME#########
    allVolumeSales = con.execute("SELECT Total_Sales-Bottle_Sales,WiS_Sales,Sales.Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales WHERE Month<=%s AND Month > %s",(Current_date,date(2017,1,1))).fetchall()
    SitesOpen = con.execute("SELECT DISTINCT Sales.Id_Site FROM Sales  WHERE Month<=%s AND Month > %s",(Current_date,date(2017,1,1))).fetchall()
    allOld_Platform = con.execute("SELECT Id_Site,Platform FROM Sites").fetchall()

    List_date = []
    Date = date(2017,1,1)
    while Date<= Current_date:
        List_date.append(Date)
        Date = Date + relativedelta(months=+1)

    worksheet_2Volume.set_column("A:A",17)
    columns_settings = [{'header' : 'Site'},
                        {'header' : 'Platform'}] + [{'header' : str(s.year) + '-' + str(s.month), 'header_format' : Date_format} for s in List_date]
    worksheet_2Volume.add_table(3,0,len(SitesOpen)+3,len(List_date)+1, {'columns' : columns_settings})
    worksheet_2Volume.data_validation('A2',{'validate' : 'list',
                                    'source' : ['Total', 'WinS','Total without WinS']})

    worksheet_2Volume.write(1,0,'Total',Title)
    worksheet_2Volume.merge_range(0,0,0,7,'Bottle sold',Title)
    worksheet_2Volume.write(1,1,'Total Bottles',Bold_Number_format)
    worksheet_2Volume.write(2,1,'Nb Sites',Bold_Number_format)

    for k in range(len(List_date)):
        VolumeSales = list(filter(lambda row: row[3] == str(List_date[k]), allVolumeSales))
        worksheet_2Volume.write_formula(1,k+2,'IFERROR(SUBTOTAL(9,%s5:%s),0)'%(xl_col_to_name(k+2),xl_rowcol_to_cell(len(SitesOpen)+3,k+2)),Bold_Number_format)
        worksheet_2Volume.write_formula(2,k+2,'IFERROR(SUBTOTAL(3,%s5:%s),0)'%(xl_col_to_name(k+2),xl_rowcol_to_cell(len(SitesOpen)+3,k+2)),Bold_Number_format)
        for i in range(len(SitesOpen)):
            VolumeSalesPerSite = list(filter(lambda row: row[2] == SitesOpen[i][0], VolumeSales))
            Old_Platform = list(filter(lambda row: row[0] == SitesOpen[i][0], allOld_Platform))
            worksheet_2Volume.write(4+i,0,SitesOpen[i][0])

            worksheet_2Volume.write(4+i,1,Old_Platform[0][1])
            if VolumeSalesPerSite:
                if not VolumeSalesPerSite[0][1]:
                    VolumeSalesPerSite = [(VolumeSalesPerSite[0][0],0)]
                worksheet_2Volume.write_formula(4+i,k+2,'IF($A$2="WinS",%s,IF($A$2="Total",%s,%s))'%(VolumeSalesPerSite[0][1],VolumeSalesPerSite[0][0],VolumeSalesPerSite[0][0]-VolumeSalesPerSite[0][1]),Number_format)
            else:
                worksheet_2Volume.write(4+i,k+2,None,grey_format)

#########SELECT DATA THIRD TAB MIX#########
    allMix_Channel_Month = con.execute("SELECT Hod_Sales,Hod_Price,Shopkeeper_Sales,Shopkeeper_Price,(Total_Sales-WiS_Sales-Bottle_Sales),Sales.Id_Site,Platform,Last_Tier,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month = %s OR Month = %s ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allMix_Channel_this_year = con.execute("SELECT SUM(Hod_Sales),AVG(Hod_Price),SUM(Shopkeeper_Sales),AVG(Shopkeeper_Price),SUM(Total_Sales-WiS_Sales-Bottle_Sales),Sales.Id_Site,Platform,Last_Tier FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Total_Sales-WiS_Sales-Onsite_Sales-Free_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allMix_Channel_last_year = con.execute("SELECT SUM(Hod_Sales),AVG(Hod_Price),SUM(Shopkeeper_Sales),AVG(Shopkeeper_Price),SUM(Total_Sales-WiS_Sales-Bottle_Sales),Sales.Id_Site,Platform,Last_Tier FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Total_Sales-WiS_Sales-Onsite_Sales-Free_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+24))).fetchall()
    allPriceHod_this_year = con.execute("SELECT AVG(Hod_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Hod_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allPriceHod_last_year = con.execute("SELECT AVG(Hod_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Hod_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+24))).fetchall()
    allPriceShopkeeper_this_year = con.execute("SELECT AVG(Shopkeeper_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Shopkeeper_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allPriceShopkeeper_last_year = con.execute("SELECT AVG(Shopkeeper_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Shopkeeper_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+24))).fetchall()
    allMix_Channel_YTD = con.execute("SELECT SUM(Hod_Sales),AVG(Hod_Price),SUM(Shopkeeper_Sales),AVG(Shopkeeper_Price),SUM(Total_Sales-WiS_Sales-Bottle_Sales),Sales.Id_Site,Platform,Last_Tier FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Total_Sales-WiS_Sales-Onsite_Sales-Free_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date,Current_date-relativedelta(months=+int(Current_date.month)))).fetchall()
    allMix_Channel_last_YTD = con.execute("SELECT SUM(Hod_Sales),AVG(Hod_Price),SUM(Shopkeeper_Sales),AVG(Shopkeeper_Price),SUM(Total_Sales-WiS_Sales-Bottle_Sales),Sales.Id_Site,Platform,Last_Tier FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Total_Sales-WiS_Sales-Onsite_Sales-Free_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+int(Current_date.month)+12))).fetchall()
    allPriceHod_YTD = con.execute("SELECT AVG(Hod_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Hod_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date,Current_date-relativedelta(months=+int(Current_date.month)))).fetchall()
    allPriceHod_last_YTD = con.execute("SELECT AVG(Hod_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Hod_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+int(Current_date.month)+12))).fetchall()
    allPriceShopkeeper_YTD = con.execute("SELECT AVG(Shopkeeper_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Shopkeeper_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date,Current_date-relativedelta(months=+int(Current_date.month)))).fetchall()
    allPriceShopkeeper_last_YTD = con.execute("SELECT AVG(Shopkeeper_Price),Sales.Id_Site FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Month > %s AND Shopkeeper_Sales>0 GROUP BY Id_Site ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+int(Current_date.month)+12))).fetchall()

#########WRITE DATA###########
    #Specific format
    Price_format = workbook.add_format({'bg_color':'#6AADB2','center_across':True})
    Mix_Sales_format = workbook.add_format({'bg_color':'#C4E59F','center_across':True})
    Sites_format = workbook.add_format({'bg_color':'#DCE6F1','bold':True})

    #Width column
    worksheet_3ChannelMix.set_column("A:A",16.22)
    worksheet_3ChannelMix.set_column("B:C",7.56)
    worksheet_3ChannelMix.set_column("D:H",13.33)
    worksheet_3ChannelMix.set_column("J:L",7.56)
    worksheet_3ChannelMix.set_column("M:Q",13.33)

    worksheet_3ChannelMix.autofilter(5,0,len(allMix_Channel_this_year)+6,16)

    #(3rd tab) Writing data of last year (First TABLE)

    worksheet_3ChannelMix.merge_range(0,0,0,6,'=IF($A$2="12 Months Period","Mix Channel last 12 months",IF($A$2="YTD","Mix Channel YTD","Mix Channel this month"))',Title)
    worksheet_3ChannelMix.data_validation('A2',{'validate' : 'list',
                                    'source' : ['12 Months Period', 'This Month','YTD']})
    worksheet_3ChannelMix.write(1,0,'This Month',Title)

    worksheet_3ChannelMix.merge_range(1,3,1,4,"Average Price",Bold_Number_format)
    worksheet_3ChannelMix.merge_range(1,5,1,6,"Average Mix",Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,3,"IFERROR(SUBTOTAL(1,D6:D%s),0)"%(len(allMix_Channel_this_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,4,"IFERROR(SUBTOTAL(1,E6:E%s),0)"%(len(allMix_Channel_this_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,5,"IFERROR(SUBTOTAL(9,F6:F%s),0)"%(len(allMix_Channel_this_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,6,"IFERROR(SUBTOTAL(9,G6:G%s),0)"%(len(allMix_Channel_this_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,7,"IFERROR(SUBTOTAL(9,H6:H%s),0)"%(len(allMix_Channel_this_year)+6),Bold_Number_format)

    worksheet_3ChannelMix.write_formula(3,5,"IFERROR(SUBTOTAL(9,F6:F%s)/SUBTOTAL(9,H6:H%s),0)"%(len(allMix_Channel_this_year)+6,len(allMix_Channel_this_year)+6),Bold_Percentage_format)
    worksheet_3ChannelMix.write_formula(3,6,"IFERROR(SUBTOTAL(9,G6:G%s)/SUBTOTAL(9,H6:H%s),0)"%(len(allMix_Channel_this_year)+6,len(allMix_Channel_this_year)+6),Bold_Percentage_format)


    worksheet_3ChannelMix.write(5,0,'Site',Sites_format)
    worksheet_3ChannelMix.write(5,1,'Platform',Sites_format)
    worksheet_3ChannelMix.write(5,2,'Tier',Sites_format)
    worksheet_3ChannelMix.merge_range(4,3,4,4,'Price (USD)',Price_format)
    worksheet_3ChannelMix.write(5,3,'Home Delivery',Price_format)
    worksheet_3ChannelMix.write(5,4,'Shopkeeper',Price_format)
    worksheet_3ChannelMix.merge_range(4,5,4,7,'Mix Sales (Bottles)',Mix_Sales_format)
    worksheet_3ChannelMix.write(5,5,'Home Delivery',Mix_Sales_format)
    worksheet_3ChannelMix.write(5,6,'Shopkeeper',Mix_Sales_format)
    worksheet_3ChannelMix.write(5,7,'Total (exc. WinS)',Mix_Sales_format)
    for i in range(len(allMix_Channel_this_year)):
        Mix_Channel_Month_date = list(filter(lambda row: row[5] == allMix_Channel_this_year[i][5], allMix_Channel_Month))
        Mix_Channel_Month = list(filter(lambda row: row[8] == str(Current_date), Mix_Channel_Month_date))
        Mix_Channel_this_year = list(filter(lambda row: row[5] == allMix_Channel_this_year[i][5], allMix_Channel_this_year))
        PriceHod_this_year = list(filter(lambda row: row[1] == allMix_Channel_this_year[i][5], allPriceHod_this_year))
        PriceShopkeeper_this_year = list(filter(lambda row: row[1] == allMix_Channel_this_year[i][5], allPriceShopkeeper_this_year))
        Mix_Channel_YTD = list(filter(lambda row: row[5] == allMix_Channel_this_year[i][5], allMix_Channel_YTD))
        PriceHod_YTD = list(filter(lambda row: row[1] == allMix_Channel_this_year[i][5], allPriceHod_YTD))
        PriceShopkeeper_YTD = list(filter(lambda row: row[1] == allMix_Channel_this_year[i][5], allPriceShopkeeper_YTD))
        worksheet_3ChannelMix.write(6+i,0,Mix_Channel_this_year[0][5],Sites_format)
        worksheet_3ChannelMix.write(6+i,1,Mix_Channel_this_year[0][6],Sites_format)
        worksheet_3ChannelMix.write(6+i,2,Mix_Channel_this_year[0][7],Sites_format)
        if not Mix_Channel_Month:
            empty = '""'
            Mix_Channel_Month = [(empty,empty,empty,empty,empty)]
        if not PriceHod_this_year:
            empty = '""'
            PriceHod_this_year = [(empty,empty,empty,empty,empty)]
        if not PriceShopkeeper_this_year:
            empty = '""'
            PriceShopkeeper_this_year = [(empty,empty,empty,empty,empty)]
        if not PriceHod_YTD:
            empty = '""'
            PriceHod_YTD = [(empty,empty,empty,empty,empty)]
        if not PriceShopkeeper_YTD:
            empty = '""'
            PriceShopkeeper_YTD = [(empty,empty,empty,empty,empty)]
        if not Mix_Channel_YTD:
            empty = '""'
            Mix_Channel_YTD = [(empty,empty,empty,empty,empty)]
        worksheet_3ChannelMix.write_formula(6+i,3,'IF($A$2="12 Months Period",IF(%s=0,"",%s),IF($A$2="YTD",IF(%s=0,"",%s),IF(%s=0,"",%s)))'%(PriceHod_this_year[0][0],PriceHod_this_year[0][0],PriceHod_YTD[0][0],PriceHod_YTD[0][0],Mix_Channel_Month[0][1],Mix_Channel_Month[0][1]),Number_format)
        worksheet_3ChannelMix.write_formula(6+i,4,'IF($A$2="12 Months Period",IF(%s=0,"",%s),IF($A$2="YTD",IF(%s=0,"",%s),IF(%s=0,"",%s)))'%(PriceShopkeeper_this_year[0][0],PriceShopkeeper_this_year[0][0],PriceShopkeeper_YTD[0][0],PriceShopkeeper_YTD[0][0],Mix_Channel_Month[0][3],Mix_Channel_Month[0][3]),Number_format)
        worksheet_3ChannelMix.write_formula(6+i,5,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Mix_Channel_this_year[0][0],Mix_Channel_YTD[0][0],Mix_Channel_Month[0][0]),Number_format)
        worksheet_3ChannelMix.write_formula(6+i,6,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Mix_Channel_this_year[0][2],Mix_Channel_YTD[0][2],Mix_Channel_Month[0][2]),Number_format)
        worksheet_3ChannelMix.write_formula(6+i,7,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Mix_Channel_this_year[0][4],Mix_Channel_YTD[0][4],Mix_Channel_Month[0][4]),Number_format)

    worksheet_3ChannelMix.conditional_format('D6:H%s'%(len(allMix_Channel_this_year)+6),{"type" : "formula", "criteria" : "D6=\"\"", "format" : grey_format})

    #(3rd tab) Writing data of last year (SECOND TABLE)

    worksheet_3ChannelMix.merge_range(0,9,0,15,'=IF($A$2="12 Months Period","Mix Channel 12 months last year",IF($A$2="YTD","Mix Channel last YTD","Mix Channel month last year"))',Title)

    worksheet_3ChannelMix.merge_range(1,12,1,13,"Average Price",Bold_Number_format)
    worksheet_3ChannelMix.merge_range(1,14,1,15,"Average Mix",Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,12,"IFERROR(SUBTOTAL(1,M6:M%s),0)"%(len(allMix_Channel_last_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,13,"IFERROR(SUBTOTAL(1,N6:N%s),0)"%(len(allMix_Channel_last_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,14,"IFERROR(SUBTOTAL(9,O6:O%s),0)"%(len(allMix_Channel_last_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,15,"IFERROR(SUBTOTAL(9,P6:P%s),0)"%(len(allMix_Channel_last_year)+6),Bold_Number_format)
    worksheet_3ChannelMix.write_formula(2,16,"IFERROR(SUBTOTAL(9,Q6:Q%s),0)"%(len(allMix_Channel_this_year)+6),Bold_Number_format)

    worksheet_3ChannelMix.write_formula(3,14,"IFERROR(SUBTOTAL(9,O6:O%s)/SUBTOTAL(9,Q6:Q%s),0)"%(len(allMix_Channel_this_year)+6,len(allMix_Channel_this_year)+6),Bold_Percentage_format)
    worksheet_3ChannelMix.write_formula(3,15,"IFERROR(SUBTOTAL(9,P6:P%s)/SUBTOTAL(9,Q6:Q%s),0)"%(len(allMix_Channel_this_year)+6,len(allMix_Channel_this_year)+6),Bold_Percentage_format)

    worksheet_3ChannelMix.write(5,9,'Site',Sites_format)
    worksheet_3ChannelMix.write(5,10,'Platform',Sites_format)
    worksheet_3ChannelMix.write(5,11,'Tier',Sites_format)
    worksheet_3ChannelMix.merge_range(4,12,4,13,'Price (USD)',Price_format)
    worksheet_3ChannelMix.write(5,12,'Home Delivery',Price_format)
    worksheet_3ChannelMix.write(5,13,'Shopkeeper',Price_format)
    worksheet_3ChannelMix.merge_range(4,14,4,16,'Mix Sales (Bottles)',Mix_Sales_format)
    worksheet_3ChannelMix.write(5,14,'Home Delivery',Mix_Sales_format)
    worksheet_3ChannelMix.write(5,15,'Shopkeeper',Mix_Sales_format)
    worksheet_3ChannelMix.write(5,16,'Total (exc. WinS)',Mix_Sales_format)
    for i in range(len(allMix_Channel_last_year)):
        Mix_Channel_Month_date = list(filter(lambda row: row[5] == allMix_Channel_last_year[i][5], allMix_Channel_Month))
        Mix_Channel_Month_last_year = list(filter(lambda row: row[8] == str(Current_date-relativedelta(months=+12)), Mix_Channel_Month_date))
        Mix_Channel_last_year = list(filter(lambda row: row[5] == allMix_Channel_last_year[i][5], allMix_Channel_last_year))
        PriceHod_last_year = list(filter(lambda row: row[1] == allMix_Channel_last_year[i][5], allPriceHod_last_year))
        PriceShopkeeper_last_year = list(filter(lambda row: row[1] == allMix_Channel_last_year[i][5], allPriceShopkeeper_last_year))
        Mix_Channel_last_YTD = list(filter(lambda row: row[5] == allMix_Channel_last_year[i][5], allMix_Channel_last_YTD))
        PriceHod_last_YTD = list(filter(lambda row: row[1] == allMix_Channel_this_year[i][5], allPriceHod_last_YTD))
        PriceShopkeeper_last_YTD = list(filter(lambda row: row[1] == allMix_Channel_this_year[i][5], allPriceShopkeeper_last_YTD))
        #
        worksheet_3ChannelMix.write(6+i,9,Mix_Channel_last_year[0][5],Sites_format)
        worksheet_3ChannelMix.write(6+i,10,Mix_Channel_last_year[0][6],Sites_format)
        worksheet_3ChannelMix.write(6+i,11,Mix_Channel_last_year[0][7],Sites_format)
        if not Mix_Channel_Month_last_year:
            empty = '""'
            Mix_Channel_Month_last_year = [(empty,empty,empty,empty,empty)]
        if not PriceHod_last_year:
            empty = '""'
            PriceHod_last_year = [(empty,empty,empty,empty,empty)]
        if not PriceShopkeeper_last_year:
            empty = '""'
            PriceShopkeeper_last_year = [(empty,empty,empty,empty,empty)]
        if not PriceHod_last_YTD:
            empty = '""'
            PriceHod_last_YTD = [(empty,empty,empty,empty,empty)]
        if not PriceShopkeeper_last_YTD:
            empty = '""'
            PriceShopkeeper_last_YTD = [(empty,empty,empty,empty,empty)]
        if not Mix_Channel_last_YTD:
            empty = '""'
            Mix_Channel_last_YTD = [(empty,empty,empty,empty,empty)]
        if Mix_Channel_last_year:
            worksheet_3ChannelMix.write_formula(6+i,12,'IF($A$2="12 Months Period",IF(%s=0,"",%s),IF($A$2="YTD",IF(%s=0,"",%s),IF(%s=0,"",%s)))'%(PriceHod_last_year[0][0],PriceHod_last_year[0][0],PriceHod_last_YTD[0][0],PriceHod_last_YTD[0][0],Mix_Channel_Month_last_year[0][1],Mix_Channel_Month_last_year[0][1]),Number_format)
            worksheet_3ChannelMix.write_formula(6+i,13,'IF($A$2="12 Months Period",IF(%s=0,"",%s),IF($A$2="YTD",IF(%s=0,"",%s),IF(%s=0,"",%s)))'%(PriceShopkeeper_last_year[0][0],PriceShopkeeper_last_year[0][0],PriceShopkeeper_last_YTD[0][0],PriceShopkeeper_last_YTD[0][0],Mix_Channel_Month_last_year[0][3],Mix_Channel_Month_last_year[0][3]),Number_format)
            worksheet_3ChannelMix.write_formula(6+i,14,'IF($A$2="12 Months Period",IF(%s="None","",%s),IF($A$2="YTD",IF(%s="None","",%s),IF(%s="None","",%s)))'%(Mix_Channel_last_year[0][0],Mix_Channel_last_year[0][0],Mix_Channel_last_YTD[0][0],Mix_Channel_last_YTD[0][0],Mix_Channel_Month_last_year[0][0],Mix_Channel_Month_last_year[0][0]),Number_format)
            worksheet_3ChannelMix.write_formula(6+i,15,'IF($A$2="12 Months Period",IF(%s="None","",%s),IF($A$2="YTD",IF(%s="None","",%s),IF(%s="None","",%s)))'%(Mix_Channel_last_year[0][2],Mix_Channel_last_year[0][2],Mix_Channel_last_YTD[0][2],Mix_Channel_last_YTD[0][2],Mix_Channel_Month_last_year[0][2],Mix_Channel_Month_last_year[0][2]),Number_format)
            worksheet_3ChannelMix.write_formula(6+i,16,'IF($A$2="12 Months Period",IF(%s="None","",%s),IF($A$2="YTD",IF(%s="None","",%s),IF(%s="None","",%s)))'%(Mix_Channel_last_year[0][4],Mix_Channel_last_year[0][4],Mix_Channel_last_YTD[0][4],Mix_Channel_last_YTD[0][4],Mix_Channel_Month_last_year[0][4],Mix_Channel_Month_last_year[0][4]),Number_format)

    worksheet_3ChannelMix.conditional_format('N6:R%s'%(len(allMix_Channel_last_year)+6),{"type" : "formula", "criteria" : "M6=\"\"", "format" : grey_format})

#############SELECT DATA FOURTH TAB SitesRevenues######

    allIncome_month = con.execute("SELECT Hod_Income/%s,Shopkeeper_Income/%s,WiS_Income/%s,(Onsite_Income+Other_Income+Bottle_Income)/%s,(Total_Income)/%s,"
                        "Sales.Id_Site,Platform,Last_Tier,DATE_FORMAT(Month, '%%Y-%%m-%%d') "
                        "FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                        "WHERE Month =%s OR Month = %s "
                        "ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site",(exchange_rate,exchange_rate,exchange_rate,exchange_rate,exchange_rate,Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allIncome_this_year = con.execute("SELECT SUM(Hod_Income)/%s,SUM(Shopkeeper_Income)/%s,SUM(WiS_Income)/%s,SUM(Onsite_Income+Other_Income+Bottle_Income)/%s,SUM(Total_Income)/%s,"
                            "Sales.Id_Site,Platform,Last_Tier "
                            "FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                            "WHERE Month<=%s AND Month> %s "
                            "GROUP BY Sales.Id_Site "
                            "ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site ",(exchange_rate,exchange_rate,exchange_rate,exchange_rate,exchange_rate,Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allIncome_last_year = con.execute("SELECT SUM(Hod_Income)/%s,SUM(Shopkeeper_Income)/%s,SUM(WiS_Income)/%s,SUM(Onsite_Income+Other_Income+Bottle_Income)/%s,SUM(Total_Income)/%s,"
                            "Sales.Id_Site,Platform,Last_Tier "
                            "FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                            "WHERE Month<=%s AND Month> %s "
                            "GROUP BY Sales.Id_Site "
                            "ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site ",(exchange_rate,exchange_rate,exchange_rate,exchange_rate,exchange_rate,Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+24))).fetchall()
    allIncome_YTD = con.execute("SELECT SUM(Hod_Income)/%s,SUM(Shopkeeper_Income)/%s,SUM(WiS_Income)/%s,SUM(Onsite_Income+Other_Income+Bottle_Income)/%s,SUM(Total_Income)/%s,"
                            "Sales.Id_Site,Platform,Last_Tier "
                            "FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                            "WHERE Month<=%s AND Month> %s "
                            "GROUP BY Sales.Id_Site "
                            "ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site ",(exchange_rate,exchange_rate,exchange_rate,exchange_rate,exchange_rate,Current_date,Current_date-relativedelta(months=+int(Current_date.month)))).fetchall()
    allIncome_last_YTD = con.execute("SELECT SUM(Hod_Income)/%s,SUM(Shopkeeper_Income)/%s,SUM(WiS_Income)/%s,SUM(Onsite_Income+Other_Income+Bottle_Income)/%s,SUM(Total_Income)/%s,"
                            "Sales.Id_Site,Platform,Last_Tier "
                            "FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site "
                            "WHERE Month<=%s AND Month> %s "
                            "GROUP BY Sales.Id_Site "
                            "ORDER BY Left(Sales.Id_Site,1),LENGTH(Sales.Id_Site),Sales.Id_Site ",(exchange_rate,exchange_rate,exchange_rate,exchange_rate,exchange_rate,Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+int(Current_date.month)+12))).fetchall()

########WRITE DATA##########
    #Specific format
    Total_Revenue_format = workbook.add_format({'bg_color':'#FF6050','center_across':True})
    Revenue_format = workbook.add_format({'bg_color':'#FF7C80','center_across':True})
    Sites_format = workbook.add_format({'bg_color':'#DCE6F1','bold':True})

    #Width column
    worksheet_4SitesRevenues.set_column("A:A",16.22)
    worksheet_4SitesRevenues.set_column("B:C",7.56)
    worksheet_4SitesRevenues.set_column("D:G",13.33)
    worksheet_4SitesRevenues.set_column("J:L",7.56)
    worksheet_4SitesRevenues.set_column("M:P",13.33)

    #Data writing

    worksheet_4SitesRevenues.autofilter(4,0,len(allIncome_this_year)+5,17)

    #First Table (4SitesRevenues)
    worksheet_4SitesRevenues.merge_range(0,0,0,7,'=IF($A$2="12 Months Period","Revenue of all kiosk last 12 months",IF($A$2="YTD","Revenue of all kiosk YTD","Revenue of all kiosk this month"))',Title)
    worksheet_4SitesRevenues.data_validation('A2',{'validate' : 'list',
                                    'source' : ['12 Months Period', '1 Month Period','YTD']})
    worksheet_4SitesRevenues.write(1,0,'1 Month Period',Title)

    worksheet_4SitesRevenues.merge_range(1,3,1,7,'Total Revenue ($)',Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,3,'SUBTOTAL(9,D6:D%s)'%(len(allIncome_this_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,4,'SUBTOTAL(9,E6:E%s)'%(len(allIncome_this_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,5,'SUBTOTAL(9,F6:F%s)'%(len(allIncome_this_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,6,'SUBTOTAL(9,G6:G%s)'%(len(allIncome_this_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,7,'SUBTOTAL(9,H6:H%s)'%(len(allIncome_this_year)+5),Bold_Number_format)


    worksheet_4SitesRevenues.write(4,0,'Site',Sites_format)
    worksheet_4SitesRevenues.write(4,1,'Platform',Sites_format)
    worksheet_4SitesRevenues.write(4,2,'Tier',Sites_format)

    worksheet_4SitesRevenues.merge_range(3,3,3,7,'Revenues ($)',Revenue_format)
    worksheet_4SitesRevenues.write(4,3,'Home delivery',Revenue_format)
    worksheet_4SitesRevenues.write(4,4,'Shopkeeper',Revenue_format)
    worksheet_4SitesRevenues.write(4,5,'WinS',Revenue_format)
    worksheet_4SitesRevenues.write(4,6,'Other',Revenue_format)
    worksheet_4SitesRevenues.write(4,7,'Total',Revenue_format)

    for i in range(len(allIncome_this_year)):
        Income_this_year = list(filter(lambda row: row[5] == allIncome_this_year[i][5], allIncome_this_year))
        Income_YTD = list(filter(lambda row: row[5] == allIncome_this_year[i][5], allIncome_YTD))
        Income_this_month_date = list(filter(lambda row: row[8] == str(Current_date), allIncome_month))
        Income_this_month = list(filter(lambda row: row[5] == allIncome_this_year[i][5], Income_this_month_date))
        worksheet_4SitesRevenues.write(5+i,0,Income_this_year[0][5],Sites_format)
        worksheet_4SitesRevenues.write(5+i,1,Income_this_year[0][6],Sites_format)
        worksheet_4SitesRevenues.write(5+i,2,Income_this_year[0][7],Sites_format)
        if not Income_this_month:
            empty = '""'
            Income_this_month = [(empty,empty,empty,empty,empty)]
        if not Income_YTD:
            empty = '""'
            Income_YTD = [(empty,empty,empty,empty,empty)]
        worksheet_4SitesRevenues.write_formula(5+i,3,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_this_year[0][0],Income_YTD[0][0],Income_this_month[0][0]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,4,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_this_year[0][1],Income_YTD[0][1],Income_this_month[0][1]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,5,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_this_year[0][2],Income_YTD[0][2],Income_this_month[0][2]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,6,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_this_year[0][3],Income_YTD[0][3],Income_this_month[0][3]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,7,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_this_year[0][4],Income_YTD[0][4],Income_this_month[0][4]),Bold_Number_format)

    worksheet_4SitesRevenues.conditional_format('D6:H%s'%(len(allIncome_this_year)+5),{"type" : "formula", "criteria" : "D6=\"\"", "format" : grey_format})

    #Second Table (4SitesRevenues)

    worksheet_4SitesRevenues.merge_range(0,10,0,17,'=IF($A$2="12 Months Period","Revenue of all kiosk over 12 months last year",IF($A$2="YTD","Revenue of all kiosk last YTD","Revenue of all kiosk over a month last year"))',Title)

    worksheet_4SitesRevenues.merge_range(1,13,1,17,'Total Revenue ($)',Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,13,'SUBTOTAL(9,N6:N%s)'%(len(allIncome_last_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,14,'SUBTOTAL(9,O6:O%s)'%(len(allIncome_last_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,15,'SUBTOTAL(9,P6:P%s)'%(len(allIncome_last_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,16,'SUBTOTAL(9,Q6:Q%s)'%(len(allIncome_last_year)+5),Bold_Number_format)
    worksheet_4SitesRevenues.write_formula(2,17,'SUBTOTAL(9,R6:R%s)'%(len(allIncome_last_year)+5),Bold_Number_format)

    worksheet_4SitesRevenues.write(4,10,'Site',Sites_format)
    worksheet_4SitesRevenues.write(4,11,'Platform',Sites_format)
    worksheet_4SitesRevenues.write(4,12,'Tier',Sites_format)

    worksheet_4SitesRevenues.merge_range(3,13,3,17,'Revenues ($)',Revenue_format)
    worksheet_4SitesRevenues.write(4,13,'Home delivery',Revenue_format)
    worksheet_4SitesRevenues.write(4,14,'Shopkeeper',Revenue_format)
    worksheet_4SitesRevenues.write(4,15,'WinS',Revenue_format)
    worksheet_4SitesRevenues.write(4,16,'Other',Revenue_format)
    worksheet_4SitesRevenues.write(4,17,'Total',Revenue_format)

    for i in range(len(allIncome_last_year)):
        Income_last_year = list(filter(lambda row: row[5] == allIncome_last_year[i][5], allIncome_last_year))
        Income_last_YTD = list(filter(lambda row: row[5] == allIncome_last_year[i][5], allIncome_last_YTD))
        Income_last_month_date = list(filter(lambda row: row[8] == str(Current_date-relativedelta(months=+12)), allIncome_month))
        Income_last_month = list(filter(lambda row: row[5] == allIncome_last_year[i][5], Income_last_month_date))
        worksheet_4SitesRevenues.write(5+i,10,Income_last_year[0][5],Sites_format)
        worksheet_4SitesRevenues.write(5+i,11,Income_last_year[0][6],Sites_format)
        worksheet_4SitesRevenues.write(5+i,12,Income_last_year[0][7],Sites_format)
        if not Income_last_month:
            empty = '""'
            Income_last_month = [(empty,empty,empty,empty,empty)]
        if not Income_last_YTD:
            empty = '""'
            Income_last_YTD = [(empty,empty,empty,empty,empty)]
        worksheet_4SitesRevenues.write_formula(5+i,13,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_last_year[0][0],Income_last_YTD[0][0],Income_last_month[0][0]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,14,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_last_year[0][1],Income_last_YTD[0][1],Income_last_month[0][1]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,15,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_last_year[0][2],Income_last_YTD[0][2],Income_last_month[0][2]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,16,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_last_year[0][3],Income_last_YTD[0][3],Income_last_month[0][3]),Number_format)
        worksheet_4SitesRevenues.write_formula(5+i,17,'IF($A$2="12 Months Period",%s,IF($A$2="YTD",%s,%s))'%(Income_last_year[0][4],Income_last_YTD[0][4],Income_last_month[0][4]),Bold_Number_format)

    worksheet_4SitesRevenues.conditional_format('N6:R%s'%(len(allIncome_last_year)+5),{"type" : "formula", "criteria" : "N6=\"\"", "format" : grey_format})

######### SELECT DATA FIFTH TAB Consumables#########

    allConsumable_month = con.execute("SELECT Amount_expenses/%s,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d'),Ref_expenses FROM Expenses WHERE (Month = %s OR Month = %s) AND (Ref_expenses ='stock_ts' OR Ref_expenses = 'bottle_invoice') AND Amount_expenses <> 0",(exchange_rate_year(Current_date),Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allConsumable_year = con.execute("SELECT SUM(Amount_expenses)/%s,Id_Site,Ref_expenses FROM Expenses WHERE (Month <= %s AND Month > %s) AND (Ref_expenses ='stock_ts' OR Ref_expenses = 'bottle_invoice') AND Amount_expenses <> 0 GROUP BY Id_Site,Ref_expenses",(exchange_rate_year(Current_date),Current_date,Current_date-relativedelta(months=+12))).fetchall()
    allConsumable_last_year =con.execute("SELECT SUM(Amount_expenses)/%s,Id_Site,Ref_expenses FROM Expenses WHERE (Month <= %s AND Month > %s) AND (Ref_expenses ='stock_ts' OR Ref_expenses = 'bottle_invoice') AND Amount_expenses <> 0 GROUP BY Id_Site,Ref_expenses",(exchange_rate_year(Current_date-relativedelta(months=+12)),Current_date-relativedelta(months=+12),Current_date-relativedelta(months=+24))).fetchall()
    allConsumable_YTD = con.execute("SELECT SUM(Amount_expenses)/%s,Id_Site,Ref_expenses FROM Expenses WHERE (Month <= %s AND Month >= %s) AND (Ref_expenses ='stock_ts' OR Ref_expenses = 'bottle_invoice') AND Amount_expenses <> 0 GROUP BY Id_Site,Ref_expenses",(exchange_rate_year(Current_date),Current_date,date(Current_date.year,1,1))).fetchall()
    allConsumable_last_YTD =con.execute("SELECT SUM(Amount_expenses)/%s,Id_Site,Ref_expenses FROM Expenses WHERE (Month <= %s AND Month >= %s) AND (Ref_expenses ='stock_ts' OR Ref_expenses = 'bottle_invoice') AND Amount_expenses <> 0 GROUP BY Id_Site,Ref_expenses",(exchange_rate_year(Current_date-relativedelta(months=+12)),Current_date-relativedelta(months=+12),date(Current_date.year-1,1,1))).fetchall()
    all_site = con.execute("SELECT DISTINCT Expenses.Id_Site,Platform,Last_Tier FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE Month <= %s AND Month > %s AND (Ref_expenses = 'stock_ts' OR Ref_expenses = 'bottle_invoice') AND Amount_expenses <> 0",(Current_date,Current_date-relativedelta(months=+24))).fetchall()

#######WRITE DATA###########
    #Specific format
    This_month_year_format = workbook.add_format({'bg_color':'#D8E4BC','center_across':True})
    Last_month_year_format = workbook.add_format({'bg_color':'#F8CBAD','center_across':True})

    #Width column
    worksheet_5Consumables.set_column("A:A",16.22)
    worksheet_5Consumables.set_column("B:C",7.56)
    worksheet_5Consumables.set_column("D:G",16.89)
    worksheet_5Consumables.set_column("E:E",11.78)
    worksheet_5Consumables.set_column("G:G",11.78)

    # Data writing

    worksheet_5Consumables.autofilter(4,0,len(all_site)+5,6)
    worksheet_5Consumables.write(4,0,"Site",Sites_format)
    worksheet_5Consumables.write(4,1,"Platform",Sites_format)
    worksheet_5Consumables.write(4,2,"Tier",Sites_format)


    worksheet_5Consumables.merge_range(0,0,0,6,"Consumable sold by TS to kiosk",Title)
    worksheet_5Consumables.data_validation('A2',{'validate' : 'list',
                                        'source' : ['12 Months Period', '1 Month Period','YTD']})
    worksheet_5Consumables.write(1,0,'1 Month Period',Title)

    worksheet_5Consumables.merge_range(1,3,1,6,"Total Sales",Bold_Number_format)
    worksheet_5Consumables.write_formula(2,3,"SUBTOTAL(9,D6:D%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_5Consumables.write_formula(2,4,"SUBTOTAL(9,E6:E%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_5Consumables.write_formula(2,5,"SUBTOTAL(9,F6:F%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_5Consumables.write_formula(2,6,"SUBTOTAL(9,G6:G%s)"%(len(all_site)+5),Bold_Number_format)

    worksheet_5Consumables.merge_range(3,3,3,4,'=IF($A$2 = "12 Months Period","This year",IF($A$2="YTD","YTD","This month"))',This_month_year_format)
    worksheet_5Consumables.merge_range(3,5,3,6,'=IF($A$2 = "12 Months Period","Last year",IF($A$2="YTD","YTD last year","Same month last year"))',Last_month_year_format)
    worksheet_5Consumables.write(4,3,'Consumable Sold',This_month_year_format)
    worksheet_5Consumables.write(4,4,'Bottles Sold',This_month_year_format)
    worksheet_5Consumables.write(4,5,'Consumable Sold',Last_month_year_format)
    worksheet_5Consumables.write(4,6,'Bottles Sold',Last_month_year_format)


    for i in range(len(all_site)):
        Consumable_year= list(filter(lambda row: row[1] == all_site[i][0], allConsumable_year))
        Consumable_year_stock = list(filter(lambda row: row[2] == 'stock_ts', Consumable_year)) or [("",)]
        Consumable_year_bottle = list(filter(lambda row: row[2] == 'bottle_invoice', Consumable_year)) or [("",)]

        Consumable_last_year = list(filter(lambda row: row[1] == all_site[i][0], allConsumable_last_year))
        Consumable_last_year_stock = list(filter(lambda row: row[2] == 'stock_ts', Consumable_last_year)) or [("",)]
        Consumable_last_year_bottle = list(filter(lambda row: row[2] == 'bottle_invoice', Consumable_last_year)) or [("",)]

        Consumable_YTD= list(filter(lambda row: row[1] == all_site[i][0], allConsumable_YTD))
        Consumable_YTD_stock = list(filter(lambda row: row[2] == 'stock_ts', Consumable_YTD)) or [("",)]
        Consumable_YTD_bottle = list(filter(lambda row: row[2] == 'bottle_invoice', Consumable_YTD)) or [("",)]

        Consumable_last_YTD = list(filter(lambda row: row[1] == all_site[i][0], allConsumable_last_YTD))
        Consumable_last_YTD_stock = list(filter(lambda row: row[2] == 'stock_ts', Consumable_last_YTD)) or [("",)]
        Consumable_last_YTD_bottle = list(filter(lambda row: row[2] == 'bottle_invoice', Consumable_last_YTD)) or [("",)]

        Consumable_month_date = list(filter(lambda row: row[2] == str(Current_date), allConsumable_month))
        Consumable_month = list(filter(lambda row: row[1] == all_site[i][0], Consumable_month_date))
        Consumable_month_stock = list(filter(lambda row: row[3] == 'stock_ts', Consumable_month)) or [("",)]
        Consumable_month_bottle = list(filter(lambda row: row[3] == 'bottle_invoice', Consumable_month)) or [("",)]

        Consumable_last_month_date = list(filter(lambda row: row[2] == str(Current_date-relativedelta(months=+12)), allConsumable_month))
        Consumable_last_month = list(filter(lambda row: row[1] == all_site[i][0], Consumable_last_month_date))
        Consumable_last_month_stock = list(filter(lambda row: row[3] == 'stock_ts', Consumable_last_month)) or [("",)]
        Consumable_last_month_bottle = list(filter(lambda row: row[3] == 'bottle_invoice', Consumable_last_month)) or [("",)]

        worksheet_5Consumables.write(i+5,0,all_site[i][0],Sites_format)
        worksheet_5Consumables.write(i+5,1,all_site[i][1],Sites_format)
        worksheet_5Consumables.write(i+5,2,all_site[i][2],Sites_format)
        worksheet_5Consumables.write_formula(i+5,3,'=IF($A$2 = "12 Months Period",%s,IF($A$2 = "YTD",%s,%s))'%(Consumable_year_stock[0][0],Consumable_YTD_stock[0][0],Consumable_month_stock[0][0]),Number_format)
        worksheet_5Consumables.write_formula(i+5,4,'=IF($A$2 = "12 Months Period",%s,IF($A$2 = "YTD",%s,%s))'%(Consumable_year_bottle[0][0],Consumable_YTD_bottle[0][0],Consumable_month_bottle[0][0]),Number_format)
        worksheet_5Consumables.write_formula(i+5,5,'=IF($A$2 = "12 Months Period",%s,IF($A$2 = "YTD",%s,%s))'%(Consumable_last_year_stock[0][0],Consumable_last_YTD_stock[0][0],Consumable_last_month_stock[0][0]),Number_format)
        worksheet_5Consumables.write_formula(i+5,6,'=IF($A$2 = "12 Months Period",%s,IF($A$2 = "YTD",%s,%s))'%(Consumable_last_year_bottle[0][0],Consumable_last_YTD_bottle[0][0],Consumable_last_month_bottle[0][0]),Number_format)

    worksheet_5Consumables.conditional_format('D6:G%s'%(len(all_site)+5),{"type" : "formula", "criteria" : "D6=\"\"", "format" : grey_format})

####### SELECT DATA SIXTH TAB Debts###########

    all_debt = con.execute("SELECT Expenses.Id_Site,Amount_expenses/%s,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Expenses WHERE (Month = %s OR Month = %s) AND Ref_expenses = 'debt' AND Amount_expenses <> 0",(exchange_rate,Current_date+relativedelta(months=+1),Current_date)).fetchall()

    all_paid_year = con.execute("SELECT IFNULL(SUM(Paid),0)/%s,Id_Site FROM Expenses WHERE Month <= %s AND Month >=%s AND Ref_expenses <> 'debt' AND Ref_expenses <> 'WinS_invoice' AND Ref_expenses <> 'withdrawal' GROUP BY Id_Site",(exchange_rate,Current_date,date(Current_date.year,1,1))).fetchall()
    all_expenses_year = con.execute("SELECT IFNULL(SUM(Amount_expenses),0)/%s,Id_Site FROM Expenses WHERE Month <= %s AND Month >=%s AND (Ref_expenses = 'stock_ts' OR Ref_expenses = 'bottle_invoice' OR Ref_expenses = 'technical intervention' OR Ref_expenses = 'water quality alert' OR Ref_expenses = 'entrepreneur_contribution') GROUP BY Id_Site",(exchange_rate,Current_date,date(Current_date.year,1,1))).fetchall()
    all_paid_last_year = con.execute("SELECT IFNULL(SUM(Paid),0)/%s,Id_Site FROM Expenses WHERE Month <= %s AND Month >=%s AND Ref_expenses <> 'debt' AND Ref_expenses <> 'WinS_invoice' AND Ref_expenses <> 'withdrawal' GROUP BY Id_Site",(exchange_rate,Current_date-relativedelta(months=+12),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()
    all_expenses_last_year = con.execute("SELECT IFNULL(SUM(Amount_expenses),0)/%s,Id_Site FROM Expenses WHERE Month <= %s AND Month >=%s AND (Ref_expenses = 'stock_ts' OR Ref_expenses = 'bottle_invoice' OR Ref_expenses = 'technical intervention' OR Ref_expenses = 'water quality alert' OR Ref_expenses = 'entrepreneur_contribution') GROUP BY Id_Site",(exchange_rate,(Current_date-relativedelta(months=+12)),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()

    all_paid_debt1_year = con.execute("SELECT IFNULL(SUM(Paid),0)/%s, Id_Site FROM Expenses WHERE (Month <= %s AND Month >= %s) AND Ref_expenses= 'debt' AND Amount_expenses > 0 AND Amount_expenses-Paid >= 0 GROUP BY Id_Site",(exchange_rate,Current_date,date(Current_date.year,1,1))).fetchall()
    all_paid_debt2_year = con.execute("SELECT IFNULL(SUM(Amount_expenses),0)/%s, Id_Site FROM Expenses WHERE (Month <= %s AND Month >= %s) AND Ref_expenses= 'debt' AND Amount_expenses > 0 AND Amount_expenses - Paid < 0 GROUP BY Id_Site",(exchange_rate,Current_date,date(Current_date.year,1,1))).fetchall()
    all_paid_debt1_last_year = con.execute("SELECT IFNULL(SUM(Paid),0)/%s, Id_Site FROM Expenses WHERE (Month <= %s AND Month >= %s) AND Ref_expenses= 'debt' AND Amount_expenses > 0 AND Amount_expenses-Paid >= 0 GROUP BY Id_Site",(exchange_rate,Current_date-relativedelta(months=+12),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()
    all_paid_debt2_last_year = con.execute("SELECT IFNULL(SUM(Amount_expenses),0)/%s, Id_Site FROM Expenses WHERE (Month <= %s AND Month >= %s) AND Ref_expenses= 'debt' AND Amount_expenses > 0 AND Amount_expenses - Paid < 0 GROUP BY Id_Site",(exchange_rate,Current_date,date(Current_date.year,1,1))).fetchall()
    all_debt_january = con.execute("SELECT IFNULL(Amount_expenses,0)/%s,IFNULL(Paid,0)/%s,Expenses.Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE (Month = %s OR Month = %s) AND Ref_expenses = 'debt' AND Amount_Expenses > 0",(exchange_rate,exchange_rate,date(Current_date.year,1,1),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()
    all_site = con.execute("SELECT DISTINCT Expenses.Id_Site FROM Expenses WHERE Month > %s AND Amount_expenses <> 0",(Current_date-relativedelta(months=+12))).fetchall()
    all_site_info = con.execute("SELECT Id_Site,Platform,Last_Tier FROM Sites").fetchall()

########WRITE DATA###########
    #Specific format
    Title_format_debt = workbook.add_format({'bg_color':'#76933C','center_across':True,'bold' : True})
    Title_format_CR = workbook.add_format({'bg_color':'#16365C','center_across':True,'bold' : True})
    This_month_format_debt = workbook.add_format({'bg_color':'#C4D79B','center_across':True})
    Last_month_format_debt = workbook.add_format({'bg_color':'#EBF1DE','center_across':True})
    This_month_format_CR = workbook.add_format({'bg_color':'#538DD5','center_across':True})
    Last_month_format_CR = workbook.add_format({'bg_color':'#C5D9F1','center_across':True})

    #Column width
    worksheet_6Debts.set_column('D:K',22)

    #Data writing

    worksheet_6Debts.autofilter(4,0,len(all_site)+5,10)

    worksheet_6Debts.merge_range(0,0,0,10,'Debts to TS',Title)

    worksheet_6Debts.merge_range(1,3,1,10,'Total Debt/Savings and Average CR',Bold_Number_format)
    worksheet_6Debts.write_formula(2,3,"=SUBTOTAL(9,D6:D%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_6Debts.write_formula(2,4,"=SUBTOTAL(9,E6:E%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_6Debts.write_formula(2,5,"=SUBTOTAL(9,F6:F%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_6Debts.write_formula(2,6,"=SUBTOTAL(9,G6:G%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_6Debts.write_formula(2,7,"=F3/G3",Bold_Percentage_format)
    worksheet_6Debts.write_formula(2,8,"=SUBTOTAL(9,I6:I%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_6Debts.write_formula(2,9,"=SUBTOTAL(9,J6:J%s)"%(len(all_site)+5),Bold_Number_format)
    worksheet_6Debts.write_formula(2,10,"=I3/J3",Bold_Percentage_format)

    worksheet_6Debts.merge_range(3,3,3,4,'Debts (+), Savings (-)',Title_format_debt)
    worksheet_6Debts.merge_range(3,5,3,10,'Collection Rate YTD',Title_format_CR)
    worksheet_6Debts.write(4,3,'This Month',This_month_format_debt)
    worksheet_6Debts.write(4,4,'Last month',Last_month_format_debt)
    worksheet_6Debts.write(4,5,'Paid to TS %s'%(Current_date.year),This_month_format_CR)
    worksheet_6Debts.write(4,6,'Due to TS %s'%(Current_date.year),This_month_format_CR)
    worksheet_6Debts.write(4,7,'Collection rate %s'%(Current_date.year),This_month_format_CR)
    worksheet_6Debts.write(4,8,'Paid to TS %s'%(int(Current_date.year)-1),Last_month_format_CR)
    worksheet_6Debts.write(4,9,'Due to TS %s'%(int(Current_date.year)-1),Last_month_format_CR)
    worksheet_6Debts.write(4,10,'Collection rate %s'%(int(Current_date.year)-1),Last_month_format_CR)

    worksheet_6Debts.write(4,0,'Site',Sites_format)
    worksheet_6Debts.write(4,1,'Platform',Sites_format)
    worksheet_6Debts.write(4,2,'Tier',Sites_format)

    for i in range(len(all_site)):
        debt_date_month = list(filter(lambda row: row[0] == all_site[i][0], all_debt))
        debt_month = list(filter(lambda row: row[2] == str(Current_date+relativedelta(months=+1)), debt_date_month)) or [("","")]

        debt_date_last_month = list(filter(lambda row: row[0] == all_site[i][0], all_debt))
        debt_last_month = list(filter(lambda row: row[2] == str(Current_date), debt_date_last_month)) or [("","")]

        debt_january_date_month = list(filter(lambda row: row[2] == all_site[i][0], all_debt_january)) or [(0,0,0,date(2000,1,1))]
        debt_january_month = list(filter(lambda row: row[3]  == str(date(Current_date.year,1,1)), debt_january_date_month)) or [(0,0)]
        debt_january_date_last_month = list(filter(lambda row: row[2] == all_site[i][0], all_debt_january)) or [(0,0,0,date(2000,1,1))]
        debt_january_last_month = list(filter(lambda row: row[3]  == str(date((Current_date-relativedelta(months=+12)).year,1,1)), debt_january_date_last_month)) or [(0,0)]
        paid_year = list(filter(lambda row: row[1] == all_site[i][0], all_paid_year)) or [(0,0)]
        expenses_year = list(filter(lambda row: row[1] == all_site[i][0], all_expenses_year)) or [(0,0)]
        paid_last_year = list(filter(lambda row: row[1] == all_site[i][0], all_paid_last_year)) or [(0,0)]
        expenses_last_year = list(filter(lambda row: row[1] == all_site[i][0], all_expenses_last_year)) or [(0,0)]

        debt_paid_year_1 = list(filter(lambda row: row[1] == all_site[i][0], all_paid_debt1_year)) or [(0,0)]
        debt_paid_year_2 = list(filter(lambda row: row[1] == all_site[i][0], all_paid_debt2_year)) or [(0,0)]
        debt_paid_lastyear_1 = list(filter(lambda row: row[1] == all_site[i][0], all_paid_debt1_last_year)) or [(0,0)]
        debt_paid_lastyear_2 = list(filter(lambda row: row[1] == all_site[i][0], all_paid_debt2_last_year)) or [(0,0)]

        site_info = list(filter(lambda row: row[0] == all_site[i][0], all_site_info))

        worksheet_6Debts.write(5+i,0,site_info[0][0],Sites_format)
        worksheet_6Debts.write(5+i,1,site_info[0][1],Sites_format)
        worksheet_6Debts.write(5+i,2,site_info[0][2],Sites_format)


        worksheet_6Debts.write_formula(5+i,3,"=%s"%debt_month[0][1],Number_format)
        worksheet_6Debts.write_formula(5+i,4,'=%s'%(debt_last_month[0][1]),Number_format)

        worksheet_6Debts.write_formula(5+i,5,'=%s'%(paid_year[0][0]+debt_paid_year_1[0][0]+debt_paid_year_2[0][0]),Number_format)
        worksheet_6Debts.write_formula(5+i,6,'=%s'%(expenses_year[0][0]+debt_january_month[0][0]),Number_format)
        worksheet_6Debts.write_formula(5+i,7,'=IFERROR(F%s/G%s,"")'%(6+i,6+i),Percentage_format)

        worksheet_6Debts.write_formula(5+i,8,'=%s'%(paid_last_year[0][0]+debt_paid_lastyear_1[0][0]+debt_paid_lastyear_2[0][0]),Number_format)
        worksheet_6Debts.write_formula(5+i,9,'=%s'%(expenses_last_year[0][0]+debt_january_last_month[0][0]),Number_format)
        worksheet_6Debts.write_formula(5+i,10,'=IFERROR(I%s/J%s,"")'%(6+i,6+i),Percentage_format)
        
    worksheet_6Debts.conditional_format('D6:J%s'%(len(all_site)+5),{"type" : "formula", "criteria" : "D6=\"\"", "format" : grey_format})

def KioskNetwork(workbook,worksheet,Current_date,Date_1,Line,Column):
    con = db.pool.connect()
    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    KPI1_Title_format = workbook.add_format({'bg_color' : '#31869B','bold' : True, 'center_across': True,'bottom' : 2,'top' : 2})
    KPI1_format = workbook.add_format({'bg_color' : '#92CDDC','center_across' : True})
    KPI1_italic_format = workbook.add_format({'bg_color' : '#92CDDC','center_across' : True,'italic':True})
    KPI1_bottom_format = workbook.add_format({'bg_color' : '#92CDDC','center_across' : True,'bottom' : 2})
    KPI1_bold_format= workbook.add_format({'bg_color' : '#92CDDC','center_across' : True , 'bold' : True})
    KPI1_bold_italic_format= workbook.add_format({'bg_color' : '#92CDDC','center_across' : True , 'bold' : True,'italic':True})
    KPI1_bottom_bold_format = workbook.add_format({'bg_color' : '#92CDDC','center_across' : True,'bottom' : 2,'bold' : True})
    KPI2_format = workbook.add_format({'bg_color' : '#DAEEF3','center_across' : True})
    KPI2_italic_format = workbook.add_format({'bg_color' : '#DAEEF3','center_across' : True,'italic':True})
    KPI2_italic_bottom_format = workbook.add_format({'bg_color' : '#DAEEF3','center_across' : True,'italic':True,'bottom':2,'num_format':'+# ##0;-# ##0'})
    KPI2_bottom_format = workbook.add_format({'bg_color' : '#DAEEF3','center_across' : True,'bottom':2})
    KPI2_bold_format= workbook.add_format({'bg_color' : '#DAEEF3','center_across' : True , 'bold' : True})
    KPI2_bold_italic_format= workbook.add_format({'bg_color' : '#DAEEF3','center_across' : True , 'bold' : True,'italic':True})
    KPI2_bottom_bold_format = workbook.add_format({'bg_color' : '#DAEEF3','center_across' : True,'bottom' : 2,'bold' : True})

###########DATA SELECTION###########
    
    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' ORDER BY Platform""").fetchall()

    allSites_Open = con.execute("""SELECT COUNT(DISTINCT Sales.Id_Site),Platform FROM Sales 
                            JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                            WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                            Current_date,Date_1).fetchall()
    
    allNewly_open = con.execute("""SELECT COUNT(DISTINCT Sales.Id_Site),Platform FROM Sales 
                            JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                            WHERE Month <= %s AND Month >= %s AND 
                            Sales.Id_Site NOT IN (SELECT Sales.Id_Site FROM Sales WHERE Month < %s) 
                            GROUP BY Platform""",
                            Current_date,Date_1,Date_1).fetchall()
    
    allReopen = con.execute("""SELECT COUNT(DISTINCT Sales.Id_Site),Platform FROM Sales 
                            JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                            WHERE Month <= %s AND Month >= %s AND Sales.Id_Site NOT IN 
                                (SELECT Sales.Id_Site FROM Sales WHERE Month = %s) 
                            AND Sales.Id_Site IN (SELECT Sales.Id_Site FROM Sales WHERE Month < %s) 
                            GROUP BY Platform""",
                            Current_date,Date_1,Date_1-relativedelta(months=+1),Date_1).fetchall()

    allClosed = con.execute("""SELECT COUNT(DISTINCT Sales.Id_Site),Platform FROM Sales 
                            JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                            WHERE Sales.Id_Site IN  (SELECT Sales.Id_Site FROM Sales WHERE Month = %s) 
                            AND Sales.Id_Site NOT IN (SELECT Sales.Id_Site FROM Sales WHERE Month <= %s AND Month >= %s) 
                            GROUP BY Platform""",
                            Date_1-relativedelta(months=+1),Current_date,Date_1).fetchall()

    allSites_Open_N_1 = con.execute("""SELECT COUNT(DISTINCT Sales.Id_Site),Platform FROM Sales 
                            JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                            WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                            Current_date-relativedelta(months=+12),Date_1-relativedelta(months=+12)).fetchall()

    ListST1 = NewCalculTier(Current_date)[1][0]
    ListST1_N_1 = NewCalculTier(Current_date-relativedelta(months=+12))[1][0]

    ListST1 = NewCalculTier(Current_date)[1][0]
    ListST1_N_1 = NewCalculTier(Current_date-relativedelta(months=+12))[1][0]

    # ST1 current
    if not ListST1:
        allST1perPlatform = []  # or a default structure you expect later
    else:
        allST1perPlatform = con.execute(
            """
            SELECT COUNT(DISTINCT Id_Site), Platform
            FROM Sites
            WHERE 1 = %s AND Id_Site IN %s
            GROUP BY Platform
            """,
            (1, tuple(ListST1)),
        ).fetchall()

    # ST1 last year
    if not ListST1_N_1:
        allST1perPlatform_N_1 = []
    else:
        allST1perPlatform_N_1 = con.execute(
            """
            SELECT COUNT(DISTINCT Id_Site), Platform
            FROM Sites
            WHERE 1 = %s AND Id_Site IN %s
            GROUP BY Platform
            """,
            (1, tuple(ListST1_N_1)),
        ).fetchall()
###########WRITE TITLE#########
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column),xl_col_to_name(Column)),22.91)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+1),xl_col_to_name(Column+1)),40.36)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+2),xl_col_to_name(Column+len(Platform)+1)),10)

    LineTitle =0 
    worksheet.write(Line+LineTitle,Column,'KPI 1 - Kiosk Network',Bold_Number_format)
    worksheet.write(Line+LineTitle,Column+1,'%s %s - %s %s'%(calendar.month_name[int(Date_1.month)][0:3],Date_1.year,calendar.month_name[int(Current_date.month)][0:3],Current_date.year),KPI1_Title_format)
    LineTitle+=1

    worksheet.write(Line+LineTitle,Column+1,'Opened sites - end of month',KPI1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI1_italic_format)
    LineTitle+=1
    if Date_1 == Current_date:
        worksheet.write(Line+LineTitle,Column+1,'last month',KPI1_italic_format)
        LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Newly opened',KPI1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Reopened',KPI1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Closed',KPI1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Super Tier 1',KPI2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'evolution YoY',KPI2_bottom_format)
    LineTitle+=1

########WRITE DATA#####
    TotalSites = [sum(i[0] for i in allSites_Open),"Total"] 
    allSites_Open.append(TotalSites)

    TotalNew = [sum(i[0] for i in allNewly_open),"Total"] 
    allNewly_open.append(TotalNew)

    TotalReopen = [sum(i[0] for i in allReopen),"Total"] 
    allReopen.append(TotalReopen)

    TotalClosed = [sum(i[0] for i in allClosed),"Total"] 
    allClosed.append(TotalClosed)

    TotalSites_N_1 = [sum(i[0] for i in allSites_Open_N_1),"Total"] 
    allSites_Open_N_1.append(TotalSites_N_1)

    ST1 = [len(ListST1),"Total"] 
    allST1perPlatform.append(ST1)

    ST1_N_1 = [len(ListST1_N_1),"Total"] 
    allST1perPlatform_N_1.append(ST1_N_1)

    Platform.append(("Total",))

    for i in range(len(Platform)):
        Linefor = 0
        #Data Exctraction
        TotalSites = list(filter(lambda row: row[1] == Platform[i][0], allSites_Open)) or [(0,0)]
        TotalNew = list(filter(lambda row: row[1] == Platform[i][0], allNewly_open)) or [(0,0)]
        TotalReopen = list(filter(lambda row: row[1] == Platform[i][0], allReopen)) or [(0,0)]
        TotalClosed = list(filter(lambda row: row[1] == Platform[i][0], allClosed)) or [(0,0)]
        TotalSites_N_1 = list(filter(lambda row: row[1] == Platform[i][0], allSites_Open_N_1)) or [(0,0)]
        Site_ST1 = list(filter(lambda row: row[1] == Platform[i][0], allST1perPlatform)) or [(0,0)]
        Site_ST1_N_1 = list(filter(lambda row: row[1] == Platform[i][0], allST1perPlatform_N_1)) or [(0,0)]
        print(Site_ST1_N_1)

        worksheet.write(Line+Linefor,i+2+Column,Platform[i][0],KPI1_Title_format)
        Linefor+=1

        worksheet.write(Line+Linefor,i+2+Column,TotalSites[0][0],KPI1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,TotalSites_N_1[0][0],KPI1_italic_format)
        Linefor+=1
        if Current_date == Date_1:
            worksheet.write(Line+Linefor,i+2+Column,TotalSites[0][0]-TotalReopen[0][0]-TotalNew[0][0]+TotalClosed[0][0],KPI1_italic_format)
            Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,TotalNew[0][0],KPI1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,TotalReopen[0][0],KPI1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,TotalClosed[0][0],KPI1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,Site_ST1[0][0],KPI2_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,Site_ST1_N_1[0][0],KPI2_italic_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,Site_ST1[0][0]-Site_ST1_N_1[0][0],KPI2_italic_bottom_format)
        Linefor+=1
    return(LineTitle+1)

def Volume(workbook,worksheet,Current_date,Date_1,Line,Column):

    con = db.pool.connect()

    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    KPI2_Title_format = workbook.add_format({'bg_color' : '#E2EFDA','bold': True,'center_across': True,'bottom':2,'top':2})
    KPI2_1_format = workbook.add_format({'bg_color' : '#70AD47','center_across': True,'num_format':'# ### ##0','text_wrap':True})
    KPI2_1_bold_format = workbook.add_format({'bg_color' : '#70AD47','center_across': True,'bold':True,'num_format':'# ### ##0'})
    KPI2_2_format = workbook.add_format({'bg_color' : '#A9D08E','center_across': True,'italic':True,'num_format':'# ### ##0'})
    KPI2_2_invisible_format = workbook.add_format({'bg_color' : '#A9D08E','font_color': '#A9D08E','center_across': True,'italic':True,'num_format':'# ### ##0'})
    KPI2_2_bold_format = workbook.add_format({'bg_color' : '#A9D08E','center_across': True,'italic':True,'bold':True,'num_format':'# ### ##0'})
    KPI2_3_format = workbook.add_format({'bg_color' : '#E2EFDA','center_across': True,'italic':True,'num_format':'+0%;-0%'})
    KPI2_3_bold_format = workbook.add_format({'bg_color' : '#E2EFDA','center_across': True,'italic':True,'bold':True,'num_format':'+0%;-0%'})
    KPI2_3_bottom_format = workbook.add_format({'bg_color' : '#E2EFDA','center_across': True,'italic':True,'bottom':2,'num_format':'+0%;-0%'})
    KPI2_3_bold_bottom_format = workbook.add_format({'bg_color' : '#E2EFDA','center_across': True,'italic':True,'bold':True,'bottom':2,'num_format':'+0%;-0%'})

##########DATA SELECTION############
    
    Date_LfL = date(Current_date.year-1,1,1)

    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' ORDER BY Platform""").fetchall()

    allWaterSales = con.execute("""SELECT SUM(Total_Sales-Bottle_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales),
                                SUM(Total_Sales-Bottle_Sales),SUM(Number_Open_Days),SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(Number_Open_Days),Platform
                                FROM Sales JOIN Sites ON Sales.Id_Site=Sites.Id_Site
                                WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                                Current_date,Date_1).fetchall()

    allWaterSales_N_1 = con.execute("""SELECT SUM(Total_Sales-Bottle_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales),
                                SUM(Total_Sales-Bottle_Sales),SUM(Number_Open_Days),SUM(Total_Sales-Bottle_Sales-WiS_Sales),SUM(Number_Open_Days),Platform
                                FROM Sales JOIN Sites ON Sales.Id_Site=Sites.Id_Site
                                WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                                Current_date-relativedelta(months=+12),Date_1-relativedelta(months=+12)).fetchall()

    allWaterSales_LfL = con.execute("""SELECT SUM(Total_Sales-Bottle_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales),Platform
                                FROM Sales JOIN Sites ON Sales.Id_Site=Sites.Id_Site
                                WHERE Month <= %s AND Month >= %s AND Sales.Id_Site IN 
                                    (SELECT Sales.Id_Site FROM Sales WHERE Month = %s)
                                GROUP BY Platform""",Current_date,Date_1,Date_LfL).fetchall()

    allWaterSales_LfL_N_1 = con.execute("""SELECT SUM(Total_Sales-Bottle_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales),Platform
                                FROM Sales JOIN Sites ON Sales.Id_Site=Sites.Id_Site
                                WHERE Month <= %s AND Month >= %s AND Sales.Id_Site IN 
                                    (SELECT Sales.Id_Site FROM Sales WHERE Month = %s)
                                GROUP BY Platform""",Current_date-relativedelta(months=+12),Date_1-relativedelta(months=+12),Date_LfL).fetchall()

##########WRITE TITLE#########
    
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column),xl_col_to_name(Column)),22.91)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+1),xl_col_to_name(Column+1)),40.36)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+2),xl_col_to_name(Column+len(Platform)+1)),10)

    LineTitle = 0
    worksheet.write(Line+LineTitle,Column,'KPI 2 - Volumes',Bold_Number_format)
    worksheet.write(Line+LineTitle,Column+1,'%s %s - %s %s'%(calendar.month_name[int(Date_1.month)][0:3],Date_1.year,calendar.month_name[int(Current_date.month)][0:3],Current_date.year),KPI2_Title_format)
    LineTitle +=1 

    worksheet.write(Line+LineTitle,Column+1,'Total bottles this month (inc WinS)',KPI2_1_format)
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'evolution YoY',KPI2_3_format)
    LineTitle +=1 

    worksheet.write(Line+LineTitle,Column+1,'Bottles sold - excluding WinS',KPI2_1_format)
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'evolution YoY',KPI2_3_format)
    LineTitle +=1 

    worksheet.write(Line+LineTitle,Column+1,'Bottles sold WinS only',KPI2_1_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'evolution YoY',KPI2_3_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 

    worksheet.write(Line+LineTitle,Column+1,'Total bottles - like-for-like basis',KPI2_1_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'organic evolution YoY',KPI2_3_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 

    worksheet.write(Line+LineTitle,Column+1,'Total bottles - like-for-like basis exc WinS',KPI2_1_format)
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'organic evolution YoY',KPI2_3_format)
    LineTitle +=1 

    worksheet.write(Line+LineTitle,Column+1,'Bottles/day inc. WinS',KPI2_1_format)
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'organic evolution YoY',KPI2_3_format)
    LineTitle +=1 

    worksheet.write(Line+LineTitle,Column+1,'Bottles/day exc. WinS',KPI2_1_format)
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI2_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle +=1 
    worksheet.write(Line+LineTitle,Column+1,'organic evolution YoY',KPI2_3_bottom_format)
    LineTitle +=1 
    
#########WRITE DATA###########
    
    TotalSales = [sum(i[0] for i in allWaterSales),sum(i[1] for i in allWaterSales),
                    sum(i[2] for i in allWaterSales),sum(i[3] for i in allWaterSales),
                    sum(i[4] for i in allWaterSales),sum(i[5] for i in allWaterSales),"Total"] 
    allWaterSales.append(TotalSales)

    TotalSales_N_1 = [sum(i[0] for i in allWaterSales_N_1),sum(i[1] for i in allWaterSales_N_1),
                        sum(i[2] for i in allWaterSales_N_1),sum(i[3] for i in allWaterSales_N_1),
                        sum(i[4] for i in allWaterSales_N_1),sum(i[5] for i in allWaterSales_N_1),"Total"]
    allWaterSales_N_1.append(TotalSales_N_1)

    TotalSales_LfL_N_1 = [sum(i[0] for i in allWaterSales_LfL),sum(i[1] for i in allWaterSales_LfL),"Total"]
    allWaterSales_LfL.append(TotalSales_LfL_N_1)

    TotalSales_LfL_N_1 = [sum(i[0] for i in allWaterSales_LfL_N_1),sum(i[1] for i in allWaterSales_LfL_N_1),"Total"]
    allWaterSales_LfL_N_1.append(TotalSales_LfL_N_1)

    Platform.append(("Total",))

    for i in range(len(Platform)):
        Linefor = 0
        #Data Exctraction
        WaterSales = list(filter(lambda row: row[6] == Platform[i][0], allWaterSales)) or [(0,0,0,0,0,0)]
        
        WaterSales_N_1 = list(filter(lambda row: row[6] == Platform[i][0], allWaterSales_N_1)) or [(0,0,0,0,0)]

        Sales_LfL = list(filter(lambda row: row[2] == Platform[i][0], allWaterSales_LfL)) or [(0,0)]

        Sales_LfL_N_1 = list(filter(lambda row: row[2] == Platform[i][0], allWaterSales_LfL_N_1)) or [(0,0)]
       
        worksheet.write(Line,i+2+Column,Platform[i][0],KPI2_Title_format)
        Linefor+=1

        worksheet.write(Line+Linefor,i+2+Column,WaterSales[0][0],KPI2_1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,WaterSales_N_1[0][0],KPI2_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s-1,"")'%(WaterSales[0][0],WaterSales_N_1[0][0]),KPI2_3_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,WaterSales[0][1],KPI2_1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,WaterSales_N_1[0][1],KPI2_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s)/(%s))-1,"")'%(WaterSales[0][1],WaterSales_N_1[0][1]),KPI2_3_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,WaterSales[0][0]-WaterSales[0][1],KPI2_1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,WaterSales_N_1[0][0]-WaterSales_N_1[0][1],KPI2_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s-1,"")'%(WaterSales[0][0]-WaterSales[0][1],WaterSales_N_1[0][0]-WaterSales_N_1[0][1]),KPI2_3_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,Sales_LfL[0][0],KPI2_1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,Sales_LfL_N_1[0][0],KPI2_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s-1,"")'%(Sales_LfL[0][0],Sales_LfL_N_1[0][0]),KPI2_3_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,Sales_LfL[0][1],KPI2_1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,Sales_LfL_N_1[0][1],KPI2_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s-1,"")'%(Sales_LfL[0][1],Sales_LfL_N_1[0][1]),KPI2_3_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(WaterSales[0][2],WaterSales[0][3]),KPI2_1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,WaterSales_N_1[0][2]/float(WaterSales_N_1[0][3]),KPI2_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR((%s/%s)/(%s/%s)-1,"")'%(WaterSales[0][2],float(WaterSales[0][3]),WaterSales_N_1[0][2],float(WaterSales_N_1[0][3])),KPI2_3_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(WaterSales[0][4],WaterSales[0][5]),KPI2_1_format)
        Linefor+=1
        worksheet.write(Line+Linefor,i+2+Column,WaterSales_N_1[0][4]/float(WaterSales_N_1[0][5]),KPI2_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR((%s/%s)/(%s/%s)-1,"")'%(WaterSales[0][4],float(WaterSales[0][5]),WaterSales_N_1[0][4],float(WaterSales_N_1[0][5])),KPI2_3_bottom_format)
        Linefor+=1
    return(LineTitle+1)   

def ChannelMix(workbook,worksheet,Current_date,Date_1,Line,Column):

    con = db.pool.connect()

    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    KPI3_Title_format = workbook.add_format({'bg_color' : '#FF0000','center_across':True,'bold':True,'bottom':2,'top':2})
    
    KPI3_1_Number_format = workbook.add_format({'bg_color':'#960000','center_across':True,'num_format':'# ### ##0'})
    KPI3_1_Number_bold_format = workbook.add_format({'bg_color':'#960000','center_across':True,'num_format':'# ### ##0','bold':True})
    KPI3_1_percent_format = workbook.add_format({'bg_color':'#960000','center_across':True,'num_format':'0.0%'})
    KPI3_1_percent_bold_format = workbook.add_format({'bg_color':'#960000','center_across':True,'num_format':'0.0%','bold':True})
    
    KPI3_2_format = workbook.add_format({'bg_color':'#FD9991','center_across':True})
    KPI3_2_Number_format = workbook.add_format({'bg_color':'#FD9991','center_across':True,'num_format':'# ### ##0'})
    KPI3_2_Number_bold_format = workbook.add_format({'bg_color':'#FD9991','center_across':True,'num_format':'# ### ##0','bold':True})
    KPI3_2_percent_format = workbook.add_format({'bg_color':'#FD9991','center_across':True,'num_format':'0.0%'})
    KPI3_2_percent_bold_format = workbook.add_format({'bg_color':'#FD9991','center_across':True,'num_format':'0.0%','bold':True})
    
    KPI3_3_format = workbook.add_format({'bg_color':'#FECAC6','center_across':True})
    KPI3_3_bottom_format = workbook.add_format({'bg_color':'#FECAC6','center_across':True,'bottom':2})
    KPI3_3_Number_format = workbook.add_format({'bg_color':'#FECAC6','center_across':True,'num_format':'+ # ##0;-# ##0'})
    KPI3_3_Number_bold_format = workbook.add_format({'bg_color':'#FECAC6','center_across':True,'num_format':'+ # ##0;-# ##0','bold':True})
    KPI3_3_pt_format = workbook.add_format({'bg_color':'#FECAC6','center_across':True,'num_format':'+0.0pt;-0.0pt'})
    KPI3_3_pt_bold_format = workbook.add_format({'bg_color':'#FECAC6','center_across':True,'num_format':'+0.0pt;-0.0pt','bold':True})
    KPI3_3_pt_bottom_format = workbook.add_format({'bg_color':'#FECAC6','center_across':True,'num_format':'+0.0pt;-0.0pt','bottom':2})

##########DATA SELECTION############
    
    Date_LfL = date(Current_date.year-1,1,1)

    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' ORDER BY Platform""").fetchall()

    allChannelSales = con.execute("""SELECT SUM(Total_Income- WiS_Income - Bottle_Income), SUM(Total_Sales - WiS_Sales - Bottle_Sales),SUM(Hod_Income), SUM(Hod_Sales),
                                SUM(Shopkeeper_Income), SUM(Shopkeeper_Sales),SUM(Onsite_Income), SUM(Onsite_Sales),
                                SUM(Free_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales), 
                                Platform FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                                WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                                Current_date,Date_1).fetchall()

    allChannelSales_N_1 = con.execute("""SELECT SUM(Total_Income- WiS_Income - Bottle_Income), SUM(Total_Sales - WiS_Sales - Bottle_Sales),SUM(Hod_Income), SUM(Hod_Sales),
                                SUM(Shopkeeper_Income), SUM(Shopkeeper_Sales),SUM(Onsite_Income), SUM(Onsite_Sales),
                                SUM(Free_Sales),SUM(Total_Sales-Bottle_Sales-WiS_Sales), 
                                Platform FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                                WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                                Current_date-relativedelta(months=+12),Date_1-relativedelta(months=+12)).fetchall()

##########WRITE TITLE#########
    
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column),xl_col_to_name(Column)),22.91)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+1),xl_col_to_name(Column+1)),40.36)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+2),xl_col_to_name(Column+len(Platform)+1)),10)

    LineTitle = 0
    worksheet.write(Line+LineTitle,Column,'KPI 3 Channel mix',Bold_Number_format)
    worksheet.write(Line+LineTitle,Column+1,'%s %s - %s %s'%(calendar.month_name[int(Date_1.month)][0:3],Date_1.year,calendar.month_name[int(Current_date.month)][0:3],Current_date.year),KPI3_Title_format)
    LineTitle+=1

    worksheet.write(Line+LineTitle,Column+1,"Total av. price (KHR/bottle) exc. WinS",KPI3_1_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"HOD av. price (KHR/bottle)",KPI3_1_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Shop av. price (KHR/bottle)",KPI3_1_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Onsite av. price (KHR/bottle)",KPI3_1_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Total av. price (KHR/bottle) last year exc. WinS",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"HOD av. price (KHR/bottle) last year",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Shop av. price (KHR/bottle) last year",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Onsite av. price (KHR/bottle) last year",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Total price evolution YoY (KHR/bottle) exc. WinS",KPI3_3_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"HOD price evolution YoY (KHR/bottle)",KPI3_3_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Shop price evolution YoY (KHR/bottle)",KPI3_3_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Onsite price evolution YoY (KHR/bottle)",KPI3_3_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"HOD % mix bottles sales",KPI3_1_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Shop % mix bottles sales",KPI3_1_Number_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Onsite % mix bottles sales",KPI3_1_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Free % mix bottles sales",KPI3_1_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"HOD % mix bottles sales last year",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Shop % mix bottles sales last year",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Onsite % mix bottles sales last year",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Free % mix bottles sales last year",KPI3_2_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"HOD % mix evolution YoY",KPI3_3_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Shop % mix evolution YoY",KPI3_3_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Onsite % mix evolution YoY",KPI3_3_Number_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,"Free % mix evolution YoY",KPI3_3_bottom_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    
#########WRITE DATA###########
    
    ChannelSales = [sum(i[0] for i in allChannelSales),sum(i[1] for i in allChannelSales),
                        sum(i[2] for i in allChannelSales),sum(i[3] for i in allChannelSales),
                        sum(i[4] for i in allChannelSales),sum(i[5] for i in allChannelSales),
                        sum(i[6] for i in allChannelSales),sum(i[7] for i in allChannelSales),
                        sum(i[8] for i in allChannelSales),sum(i[9] for i in allChannelSales),"Total"] 

    allChannelSales.append(ChannelSales)

    ChannelSales_N_1 = [sum(i[0] for i in allChannelSales_N_1),sum(i[1] for i in allChannelSales_N_1),
                        sum(i[2] for i in allChannelSales_N_1),sum(i[3] for i in allChannelSales_N_1),
                        sum(i[4] for i in allChannelSales_N_1),sum(i[5] for i in allChannelSales_N_1),
                        sum(i[6] for i in allChannelSales_N_1),sum(i[7] for i in allChannelSales_N_1),
                        sum(i[8] for i in allChannelSales_N_1),sum(i[9] for i in allChannelSales_N_1),"Total"] 
    allChannelSales_N_1.append(ChannelSales_N_1)
    Platform.append(("Total",))

    for i in range(len(Platform)):
        Linefor = 0
        #Data Exctraction
        ChannelSales = list(filter(lambda row: row[10] == Platform[i][0], allChannelSales)) or [(0,0,0,0,0,0,0,0,0,0)]
        
        ChannelSales_N_1 = list(filter(lambda row: row[10] == Platform[i][0], allChannelSales_N_1)) or [(0,0,0,0,0,0,0,0,0)]
       
        worksheet.write(Line+Linefor,i+2+Column,Platform[i][0],KPI3_Title_format)
        Linefor += 1

        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][0],ChannelSales[0][1]),KPI3_1_Number_format)
        Linefor += 1
        worksheet.write(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][2],ChannelSales[0][3]),KPI3_1_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][4],ChannelSales[0][5]),KPI3_1_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][6],ChannelSales[0][7]),KPI3_1_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][0],ChannelSales_N_1[0][1]),KPI3_2_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][2],ChannelSales_N_1[0][3]),KPI3_2_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][4],ChannelSales_N_1[0][5]),KPI3_2_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][6],ChannelSales_N_1[0][7]),KPI3_2_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR((%s/%s)-(%s/%s),"")'%(ChannelSales[0][0],ChannelSales[0][1],ChannelSales_N_1[0][0],ChannelSales_N_1[0][1]),KPI3_3_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR((%s/%s)-(%s/%s),"")'%(ChannelSales[0][2],ChannelSales[0][3],ChannelSales_N_1[0][2],ChannelSales_N_1[0][3]),KPI3_3_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR((%s/%s)-(%s/%s),"")'%(ChannelSales[0][4],ChannelSales[0][5],ChannelSales_N_1[0][4],ChannelSales_N_1[0][5]),KPI3_3_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR((%s/%s)-(%s/%s),"")'%(ChannelSales[0][6],ChannelSales[0][7],ChannelSales_N_1[0][6],ChannelSales_N_1[0][7]),KPI3_3_Number_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][3],ChannelSales[0][9]),KPI3_1_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][5],ChannelSales[0][9]),KPI3_1_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][7],ChannelSales[0][9]),KPI3_1_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales[0][8],ChannelSales[0][9]),KPI3_1_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][3],ChannelSales_N_1[0][9]),KPI3_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][5],ChannelSales_N_1[0][9]),KPI3_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][7],ChannelSales_N_1[0][9]),KPI3_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(ChannelSales_N_1[0][8],ChannelSales_N_1[0][9]),KPI3_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(ChannelSales[0][3],ChannelSales[0][9],ChannelSales_N_1[0][3],ChannelSales_N_1[0][9]),KPI3_3_pt_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(ChannelSales[0][5],ChannelSales[0][9],ChannelSales_N_1[0][5],ChannelSales_N_1[0][9]),KPI3_3_pt_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(ChannelSales[0][7],ChannelSales[0][9],ChannelSales_N_1[0][7],ChannelSales_N_1[0][9]),KPI3_3_pt_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(ChannelSales[0][8],ChannelSales[0][9],ChannelSales_N_1[0][8],ChannelSales_N_1[0][9]),KPI3_3_pt_bottom_format)
        Linefor += 1
    return(LineTitle+1)  

def Revenue(workbook,worksheet,Current_date,Date_1,Line,Column):

    con = db.pool.connect()
    
    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    
    KPI4_Title_format = workbook.add_format({'bg_color':'#305496','center_across':True,'bold':True,'bottom':2,'top':2})
    KPI4_1_format = workbook.add_format({'bg_color': '#8EA9DB','center_across':True})
    KPI4_1_dol_format = workbook.add_format({'bg_color': '#8EA9DB','center_across':True,'num_format':'$# ### ##0'})
    KPI4_1_percent_format = workbook.add_format({'bg_color': '#8EA9DB','center_across':True,'num_format':'+0.0%;-0.0%'})
    
    KPI4_2_format = workbook.add_format({'bg_color':'#B4C6E7','center_across':True})
    KPI4_2_percent_format = workbook.add_format({'bg_color':'#B4C6E7','center_across':True,'num_format':'0%'})
    
    KPI4_3_format = workbook.add_format({'bg_color':'#D9E1F2','center_across':True,'italic' : True})
    KPI4_3_bottom_format = workbook.add_format({'bg_color':'#D9E1F2','center_across':True,'bottom':2,'italic' : True})
    KPI4_3_pt_format = workbook.add_format({'bg_color':'#D9E1F2','center_across':True,'num_format':'+0pt;-0pt','italic' : True})
    KPI4_3_pt_bottom_format = workbook.add_format({'bg_color':'#D9E1F2','center_across':True,'num_format':'+0pt;-0pt','bottom':2,'italic' : True})
    
##########DATA SELECTION############
    
    Date_LfL = date(Current_date.year-1,1,1)

    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' ORDER BY Platform""").fetchall()

    allRevenuePerChannel = con.execute("""SELECT SUM(Total_Income),SUM(Hod_Income),
                                        SUM(Shopkeeper_Income),SUM(WiS_Income),
                                        SUM(Total_Income-WiS_Income-Hod_Income-Shopkeeper_Income),
                                        Platform FROM Sales 
                                        JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                                        Current_date,Date_1).fetchall()

    allRevenuePerChannel_N_1 = con.execute("""SELECT SUM(Total_Income),SUM(Hod_Income),
                                        SUM(Shopkeeper_Income),SUM(WiS_Income),
                                        SUM(Total_Income-WiS_Income-Hod_Income-Shopkeeper_Income),
                                        Platform FROM Sales 
                                        JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month <= %s AND Month >= %s GROUP BY Platform""",
                                        (Current_date-relativedelta(months=+12),Date_1-relativedelta(months=+12))).fetchall()

##########WRITE TITLE#########
    
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column),xl_col_to_name(Column)),22.91)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+1),xl_col_to_name(Column+1)),40.36)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+2),xl_col_to_name(Column+len(Platform)+1)),10)

    LineTitle = 0
    worksheet.write(Line+LineTitle,0,'KPI 4 - Sites Revenues',Bold_Number_format)
    worksheet.write(Line+LineTitle,Column+1,'%s %s - %s %s'%(calendar.month_name[int(Date_1.month)][0:3],Date_1.year,calendar.month_name[int(Current_date.month)][0:3],Current_date.year),KPI4_Title_format)
    LineTitle+=1

    worksheet.write(Line+LineTitle,Column+1,'Total Sites Revenues',KPI4_1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Total Sites Revenues last year',KPI4_1_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI4_1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'% Sites Revenues HOD',KPI4_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI4_3_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'% Sites Revenues Shopkeeper',KPI4_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI4_3_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'% Sites Revenues WinS',KPI4_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI4_3_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'% Sites Revenues Other',KPI4_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI4_3_bottom_format)
    LineTitle+=1
    
#########WRITE DATA###########
    
    Revenue = [sum(i[0] for i in allRevenuePerChannel),sum(i[1] for i in allRevenuePerChannel),sum(i[2] for i in allRevenuePerChannel),sum(i[3] for i in allRevenuePerChannel),sum(i[4] for i in allRevenuePerChannel),"Total"] 
    allRevenuePerChannel.append(Revenue)

    Revenue_N_1 = [sum(i[0] for i in allRevenuePerChannel_N_1),sum(i[1] for i in allRevenuePerChannel_N_1),sum(i[2] for i in allRevenuePerChannel_N_1),sum(i[3] for i in allRevenuePerChannel_N_1),sum(i[4] for i in allRevenuePerChannel_N_1),"Total"]
    allRevenuePerChannel_N_1.append(Revenue_N_1)


    Platform.append(("Total",))

    for i in range(len(Platform)):
        Linefor = 0
        #Data Exctraction
        RevenuePerChannel = list(filter(lambda row: row[5] == Platform[i][0], allRevenuePerChannel)) or [(0,0,0,0,0)]
        
        RevenuePerChannel_N_1 = list(filter(lambda row: row[5] == Platform[i][0], allRevenuePerChannel_N_1)) or [(0,0,0,0,0)]
       
        worksheet.write(Line+Linefor,i+2+Column,Platform[i][0],KPI4_Title_format)
        Linefor += 1

        worksheet.write(Line+Linefor,i+2+Column,RevenuePerChannel[0][0]/exchange_rate_year(Current_date),KPI4_1_dol_format)
        Linefor += 1
        worksheet.write(Line+Linefor,i+2+Column,RevenuePerChannel_N_1[0][0]/exchange_rate_year(Current_date-relativedelta(months=+12)),KPI4_1_dol_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s-1,"")'%(RevenuePerChannel[0][0],RevenuePerChannel_N_1[0][0]),KPI4_1_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(RevenuePerChannel[0][1],RevenuePerChannel[0][0]),KPI4_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(RevenuePerChannel[0][1],RevenuePerChannel[0][0],RevenuePerChannel_N_1[0][1],RevenuePerChannel_N_1[0][0]),KPI4_3_pt_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(RevenuePerChannel[0][2],RevenuePerChannel[0][0]),KPI4_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(RevenuePerChannel[0][2],RevenuePerChannel[0][0],RevenuePerChannel_N_1[0][2],RevenuePerChannel_N_1[0][0]),KPI4_3_pt_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(RevenuePerChannel[0][3],RevenuePerChannel[0][0]),KPI4_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(RevenuePerChannel[0][3],RevenuePerChannel[0][0],RevenuePerChannel_N_1[0][3],RevenuePerChannel_N_1[0][0]),KPI4_3_pt_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s,"")'%(RevenuePerChannel[0][4],RevenuePerChannel[0][0]),KPI4_2_percent_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(((%s/%s)-(%s/%s))*100,"")'%(RevenuePerChannel[0][4],RevenuePerChannel[0][0],RevenuePerChannel_N_1[0][4],RevenuePerChannel_N_1[0][0]),KPI4_3_pt_bottom_format)
        Linefor += 1
    return(LineTitle+1)

def Consumable(workbook,worksheet,Current_date,Date_1,Line,Column):
    
    con = db.pool.connect()
    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    
    KPI5_Title_format = workbook.add_format({'bg_color':'#ED7D31','align':'center','bold':True,'bottom':2,'top':2})
    KPI5_1_format = workbook.add_format({'bg_color':'#BF8F00','align':'center'})
    KPI5_1_dol_format = workbook.add_format({'bg_color':'#BF8F00','align':'center','num_format':'$# ### ##0'})
    KPI5_1_dol_invisible_format = workbook.add_format({'bg_color':'#BF8F00','font_color':'#BF8F00','align':'center','num_format':'$# ### ##0'})
    KPI5_1_dol_bold_format = workbook.add_format({'bg_color':'#BF8F00','align':'center','num_format':'$# ### ##0','bold':True})
    KPI5_2_format = workbook.add_format({'bg_color':'#FFD966','align':'center','italic' : True})
    KPI5_2_bottom_format = workbook.add_format({'bg_color':'#FFD966','align':'center','bottom':2,'italic' : True})
    KPI5_2_percent_format = workbook.add_format({'bg_color':'#FFD966','align':'center','num_format':'+0%;-0%','italic' : True})
    KPI5_2_percent_bold_format = workbook.add_format({'bg_color':'#FFD966','align':'center','num_format':'+0%;-0%','bold':True,'italic' : True})
    KPI5_2_percent_bottom_format = workbook.add_format({'bg_color':'#FFD966','align':'center','num_format':'+0%;-0%','italic' : True,'bottom':2})
    KPI5_2_percent_bold_bottom_format = workbook.add_format({'bg_color':'#FFD966','align':'center','num_format':'+0%;-0%','bold':True,'italic' : True,'bottom':2})

##########DATA SELECTION############
    Item = ConsumableType()
    Consumable = Item[0]
    Bottle = Item[1]
    
    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' ORDER BY Platform""").fetchall()

    allBottleSold_YTD = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item),Platform FROM Consumable 
                                        JOIN Sites ON Consumable.Id_Site = Sites.Id_Site
                                        WHERE Month <= %s AND Month >= %s AND Item in %s
                                        GROUP BY Platform""",(Current_date,Date_1,Bottle)).fetchall()

    allConsumableSold_YTD = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item),Platform FROM Consumable 
                                        JOIN Sites ON Consumable.Id_Site = Sites.Id_Site
                                        WHERE Month <= %s AND Month >= %s AND Item in %s
                                        GROUP BY Platform""",(Current_date,Date_1,Consumable)).fetchall()
    
    allBottleSold_YTD_N_1 = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item),Platform FROM Consumable 
                                        JOIN Sites ON Consumable.Id_Site = Sites.Id_Site
                                        WHERE Month <= %s AND Month >= %s AND Item in %s 
                                        GROUP BY Platform""",(Current_date-relativedelta(months =+12),Date_1-relativedelta(months =+12),Bottle)).fetchall() 
    allConsumableSold_YTD_N_1 = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item),Platform FROM Consumable 
                                        JOIN Sites ON Consumable.Id_Site = Sites.Id_Site
                                        WHERE Month <= %s AND Month >= %s AND Item in %s 
                                        GROUP BY Platform""",(Current_date-relativedelta(months =+12),Date_1-relativedelta(months =+12),Consumable)).fetchall() 

##########WRITE TITLE#########

    worksheet.set_column('%s:%s'%(xl_col_to_name(Column),xl_col_to_name(Column)),22.91)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+1),xl_col_to_name(Column+1)),40.36)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+2),xl_col_to_name(Column+len(Platform)+1)),10)
    LineTitle=0
    worksheet.write(Line+LineTitle,0,'KPI 5 - Consumables',Bold_Number_format)
    worksheet.write(Line+LineTitle,Column+1,'%s %s - %s %s'%(calendar.month_name[int(Date_1.month)][0:3],Date_1.year,calendar.month_name[int(Current_date.month)][0:3],Current_date.year),KPI5_Title_format)
    LineTitle+=1

    worksheet.write(Line+LineTitle,Column+1,'Revenues bottles sold by TS',KPI5_1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Revenues bottles sold by TS last year',KPI5_1_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI5_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Revenues other consumables sold by TS',KPI5_1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Revenues other conumables sold by TS last year',KPI5_1_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI5_2_bottom_format)
    LineTitle+=1

#########WRITE DATA###########
    
    BottleSold = [sum(i[0] for i in allBottleSold_YTD),sum(i[1] for i in allBottleSold_YTD),"Total"] 
    allBottleSold_YTD.append(BottleSold)
    ConsumableSold = [sum(i[0] for i in allConsumableSold_YTD),sum(i[1] for i in allConsumableSold_YTD),"Total"] 
    allConsumableSold_YTD.append(ConsumableSold)

    BottleSold_N_1 = [sum(i[0] for i in allBottleSold_YTD_N_1),sum(i[1] for i in allBottleSold_YTD_N_1),"Total"] 
    allBottleSold_YTD_N_1.append(BottleSold_N_1)
    ConsumableSold_N_1 = [sum(i[0] for i in allConsumableSold_YTD_N_1),sum(i[1] for i in allConsumableSold_YTD_N_1),"Total"] 
    allConsumableSold_YTD_N_1.append(ConsumableSold_N_1)


    Platform.append(("Total",))
    for i in range(len(Platform)):
        Linefor = 0
        #Data Exctraction
        BottleSold = list(filter(lambda row: row[2] == Platform[i][0], allBottleSold_YTD)) or [(0,0,0,0,0)]
        ConsumableSold = list(filter(lambda row: row[2] == Platform[i][0], allConsumableSold_YTD)) or [(0,0,0,0,0)]
        
        BottleSold_N_1 = list(filter(lambda row: row[2] == Platform[i][0], allBottleSold_YTD_N_1)) or [(0,0,0,0,0)]
        ConsumableSold_N_1 = list(filter(lambda row: row[2] == Platform[i][0], allConsumableSold_YTD_N_1)) or [(0,0,0,0,0)]

        worksheet.write(Line+Linefor,i+2+Column,Platform[i][0],KPI5_Title_format)
        Linefor += 1

        worksheet.write(Line+Linefor,i+2+Column,BottleSold[0][1]/exchange_rate_year(Current_date),KPI5_1_dol_format)
        Linefor += 1
        worksheet.write(Line+Linefor,i+2+Column,BottleSold_N_1[0][1]/exchange_rate_year(Current_date-relativedelta(months=+12)),KPI5_1_dol_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s-1,"")'%(BottleSold[0][1],BottleSold_N_1[0][1]),KPI5_2_percent_format)
        Linefor += 1
        worksheet.write(Line+Linefor,i+2+Column,ConsumableSold[0][1]/exchange_rate_year(Current_date),KPI5_1_dol_format)
        Linefor += 1
        worksheet.write(Line+Linefor,i+2+Column,ConsumableSold_N_1[0][1]/exchange_rate_year(Current_date-relativedelta(months=+12)),KPI5_1_dol_format)
        Linefor += 1
        worksheet.write_formula(Line+Linefor,i+2+Column,'=IFERROR(%s/%s-1,"")'%(ConsumableSold[0][1],ConsumableSold_N_1[0][1]),KPI5_2_percent_bottom_format)
        Linefor += 1    
    return(LineTitle+1)

def operators(workbook,worksheet,Current_date,Date_1,Line,Column):
    """
    KPI 6 - Operators per site (average, excluding entrepreneur)
    For the selected period [Date_1..Current_date], compute per-site average Number_of_Operator,
    then average across sites by platform. Subtract 1 to exclude entrepreneur.
    Also provide last year (shifted by 12 months) and YoY delta (points).
    """
    con = db.pool.connect()

    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    KPI7_Title_format = workbook.add_format({'bg_color':'#7030A0','center_across':True,'bold':True,'bottom':2,'top':2})
    # Average operators per site (numbers with one decimal)
    KPI7_1_format = workbook.add_format({'bg_color':'#9E60C9','center_across':True,'num_format':'0.0'})
    KPI7_2_format = workbook.add_format({'bg_color':'#C9A4E4','center_across':True,'italic':True,'num_format':'0.0'})
    KPI7_3_format = workbook.add_format({'bg_color':'#E4DFEC','center_across':True,'num_format':'+0.0;-0.0'})
    KPI7_3_bottom_format = workbook.add_format({'bg_color':'#E4DFEC','center_across':True,'bottom':2,'num_format':'+0.0;-0.0'})
    # Counts (integer) and percentages
    KPI7_1_int_format = workbook.add_format({'bg_color':'#9E60C9','center_across':True,'num_format':'# ### ##0'})
    KPI7_2_int_format = workbook.add_format({'bg_color':'#C9A4E4','center_across':True,'italic':True,'num_format':'# ### ##0'})
    KPI7_3_int_format = workbook.add_format({'bg_color':'#E4DFEC','center_across':True,'num_format':'+# ### ##0;-# ### ##0'})
    KPI7_1_pct_format = workbook.add_format({'bg_color':'#9E60C9','center_across':True,'num_format':'0.0%'})
    KPI7_2_pct_format = workbook.add_format({'bg_color':'#C9A4E4','center_across':True,'italic':True,'num_format':'0.0%'})
    KPI7_3_pt_bottom_format = workbook.add_format({'bg_color':'#E4DFEC','center_across':True,'bottom':2,'num_format':'+0.0pt;-0.0pt'})

    # Data selection
    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' ORDER BY Platform""").fetchall()

    # Per-site averages for the selected window
    site_avg_now = con.execute(
        """
        SELECT AVG(Number_of_Operator) AS avg_ops, Indicators.Id_Site, Sites.Platform
        FROM Indicators
        JOIN Sites ON Sites.Id_Site = Indicators.Id_Site
        WHERE Month <= %s AND Month >= %s
        GROUP BY Indicators.Id_Site, Sites.Platform
        """,
        Current_date, Date_1
    ).fetchall()

    # Per-site averages for last year (shifted by 12 months)
    site_avg_last = con.execute(
        """
        SELECT AVG(Number_of_Operator) AS avg_ops, Indicators.Id_Site, Sites.Platform
        FROM Indicators
        JOIN Sites ON Sites.Id_Site = Indicators.Id_Site
        WHERE Month <= %s AND Month >= %s
        GROUP BY Indicators.Id_Site, Sites.Platform
        """,
        Current_date-relativedelta(months=+12), Date_1-relativedelta(months=+12)
    ).fetchall()

    # Helper to compute platform average from per-site averages
    def platform_avg(site_avgs, platform_name):
        if platform_name == "Total":
            rows = [r[0] for r in site_avgs if r[0] is not None]
        else:
            rows = [r[0] for r in site_avgs if r[2] == platform_name and r[0] is not None]
        if not rows:
            return None
        return float(sum(rows)) / float(len(rows))

    # Helper to get list of per-site averages (excluding entrepreneur) for a platform
    def platform_site_values(site_avgs, platform_name):
        if platform_name == "Total":
            vals = [float(r[0]) for r in site_avgs if r[0] is not None]
        else:
            vals = [float(r[0]) for r in site_avgs if r[2] == platform_name and r[0] is not None]
        return vals

    # Prepare totals as pseudo-platform
    Platform.append(("Total",))

    # Layout
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column),xl_col_to_name(Column)),22.91)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+1),xl_col_to_name(Column+1)),40.36)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+2),xl_col_to_name(Column+len(Platform)+1)),10)

    LineTitle = 0
    worksheet.write(Line+LineTitle,Column,'KPI 6 - Operators',Bold_Number_format)
    worksheet.write(Line+LineTitle,Column+1,'%s %s - %s %s'%(calendar.month_name[int(Date_1.month)][0:3],Date_1.year,calendar.month_name[int(Current_date.month)][0:3],Current_date.year),KPI7_Title_format)
    LineTitle += 1

    worksheet.write(Line+LineTitle,Column+1,'Operators per site (avg)',KPI7_1_format)
    LineTitle += 1
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI7_2_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle += 1
    worksheet.write(Line+LineTitle,Column+1,'evolution YoY (pts)',KPI7_3_format)
    LineTitle += 1

    worksheet.write(Line+LineTitle,Column+1,'Sites with >=3 operators',KPI7_1_int_format)
    LineTitle += 1
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI7_2_int_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle += 1
    worksheet.write(Line+LineTitle,Column+1,'evolution YoY (nb sites)',KPI7_3_int_format)
    LineTitle += 1

    worksheet.write(Line+LineTitle,Column+1,'% sites with >=3 operators',KPI7_1_pct_format)
    LineTitle += 1
    worksheet.write(Line+LineTitle,Column+1,'last year',KPI7_2_pct_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle += 1
    worksheet.write(Line+LineTitle,Column+1,'evolution YoY (pt)',KPI7_3_pt_bottom_format)
    LineTitle += 1

    # Write data per platform
    for i in range(len(Platform)):
        plat_name = Platform[i][0]
        # Compute averages per platform (including entrepreneur)
        avg_now = platform_avg(site_avg_now, plat_name)
        avg_last = platform_avg(site_avg_last, plat_name)
        value_now = avg_now if avg_now is not None else None
        value_last = avg_last if avg_last is not None else None
        yoy = (value_now - value_last) if (value_now is not None and value_last is not None) else None

        # Compute counts and percentages of sites with >3 operators (excluding entrepreneur)
        vals_now = platform_site_values(site_avg_now, plat_name)
        vals_last = platform_site_values(site_avg_last, plat_name)
        denom_now = len(vals_now)
        denom_last = len(vals_last)
        count_now = sum(1 for v in vals_now if v >= 3.0) if denom_now > 0 else None
        count_last = sum(1 for v in vals_last if v >= 3.0) if denom_last > 0 else None
        yoy_count = (count_now - count_last) if (count_now is not None and count_last is not None) else None
        pct_now = (float(count_now) / float(denom_now)) if (count_now is not None and denom_now > 0) else None
        pct_last = (float(count_last) / float(denom_last)) if (count_last is not None and denom_last > 0) else None
        yoy_pct_pt = ((pct_now - pct_last) * 100.0) if (pct_now is not None and pct_last is not None) else None

        Linefor = 0
        worksheet.write(Line+Linefor, i+2+Column, plat_name, KPI7_Title_format)
        Linefor += 1
        if value_now is None:
            worksheet.write(Line+Linefor, i+2+Column, None, KPI7_1_format)
        else:
            worksheet.write(Line+Linefor, i+2+Column, value_now, KPI7_1_format)
        Linefor += 1
        if value_last is None:
            worksheet.write(Line+Linefor, i+2+Column, None, KPI7_2_format)
        else:
            worksheet.write(Line+Linefor, i+2+Column, value_last, KPI7_2_format)
        Linefor += 1
        if yoy is None:
            worksheet.write(Line+Linefor, i+2+Column, None, KPI7_3_format)
        else:
            worksheet.write(Line+Linefor, i+2+Column, yoy, KPI7_3_format)
        Linefor += 1

        # Count >3 operators
        worksheet.write(Line+Linefor, i+2+Column, count_now, KPI7_1_int_format) if count_now is not None else worksheet.write(Line+Linefor, i+2+Column, None, KPI7_1_int_format)
        Linefor += 1
        worksheet.write(Line+Linefor, i+2+Column, count_last, KPI7_2_int_format) if count_last is not None else worksheet.write(Line+Linefor, i+2+Column, None, KPI7_2_int_format)
        Linefor += 1
        worksheet.write(Line+Linefor, i+2+Column, yoy_count, KPI7_3_int_format) if yoy_count is not None else worksheet.write(Line+Linefor, i+2+Column, None, KPI7_3_int_format)
        Linefor += 1

        # Percent of sites >3 operators
        worksheet.write(Line+Linefor, i+2+Column, pct_now, KPI7_1_pct_format) if pct_now is not None else worksheet.write(Line+Linefor, i+2+Column, None, KPI7_1_pct_format)
        Linefor += 1
        worksheet.write(Line+Linefor, i+2+Column, pct_last, KPI7_2_pct_format) if pct_last is not None else worksheet.write(Line+Linefor, i+2+Column, None, KPI7_2_pct_format)
        Linefor += 1
        worksheet.write(Line+Linefor, i+2+Column, yoy_pct_pt, KPI7_3_pt_bottom_format) if yoy_pct_pt is not None else worksheet.write(Line+Linefor, i+2+Column, None, KPI7_3_pt_bottom_format)
        Linefor += 1

    return (LineTitle+1)

def Debt(workbook,worksheet,Current_date,Line,Column):
    con = db.pool.connect()
    Bold_Number_format = workbook.add_format({'num_format':'# ### ### ##0','bold': True,'center_across':True})
    
    KPI6_Title_format = workbook.add_format({'bg_color':'#808080','center_across':True,'bold':True,'bottom':2,'top':2})
    KPI6_1_format = workbook.add_format({'bg_color':'#ACB9CA','center_across':True})
    KPI6_1_dol_format = workbook.add_format({'bg_color':'#ACB9CA','center_across':True,'num_format':'$# ### ##0'})
    KPI6_2_format = workbook.add_format({'bg_color':'#D6DCE4','center_across':True})
    KPI6_3_format = workbook.add_format({'bg_color':'#EDEDED','center_across':True})
    KPI6_3_bottom_format = workbook.add_format({'bg_color':'#EDEDED','center_across':True,'bottom':2})
    KPI6_3_percent_format = workbook.add_format({'bg_color':'#EDEDED','center_across':True,'num_format':'0%'})
    KPI6_3_pt_bottom_format = workbook.add_format({'bg_color':'#EDEDED','center_across':True,'num_format':'+0pt;-0pt','bottom':2})
    
#########DATA SELECTION#########
    Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead' ORDER BY Platform""").fetchall()

    allDebt = con.execute("""SELECT SUM(IF(Amount_expenses >0,Amount_expenses,0)),SUM(IF(Amount_expenses <0,Amount_expenses,0)),
                            COUNT(IF(Amount_Expenses>0,1,NULL)),COUNT(IF(Amount_Expenses>1000*%s,1,NULL)),Platform
                            FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
                            WHERE Month = %s AND Ref_expenses = 'debt' 
                            GROUP BY Month,Platform""",
                            exchange_rate_year(Current_date+relativedelta(months=+1)),Current_date+relativedelta(months=+1)).fetchall()

    allDebt_M_1 = con.execute("""SELECT SUM(IF(Amount_expenses >0,Amount_expenses,0)),SUM(IF(Amount_expenses <0,Amount_expenses,0)),
                            COUNT(IF(Amount_Expenses>0,1,NULL)),COUNT(IF(Amount_Expenses>1000*%s,1,NULL)),Platform
                            FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
                            WHERE Month = %s AND Ref_expenses = 'debt' 
                            GROUP BY Month,Platform""",
                            exchange_rate_year(Current_date),Current_date).fetchall()

    all_paid_YTD= con.execute("SELECT IFNULL(SUM(Paid),0),Platform FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site "
                                "WHERE Month <= %s AND Month >=%s AND Ref_expenses <> 'debt' AND Ref_expenses <> 'WinS_invoice' "
                                "AND Ref_expenses <> 'withdrawal' GROUP BY Platform",
                                (Current_date,date(Current_date.year,1,1))).fetchall()
    all_expenses_YTD = con.execute("SELECT SUM(Amount_expenses),Platform FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site "
                                    "WHERE Month <= %s AND Month >=%s AND (Ref_expenses = 'stock_ts' OR Ref_expenses = 'bottle_invoice' "
                                    "OR Ref_expenses = 'technical intervention' OR Ref_expenses = 'water quality alert' "
                                    "OR Ref_expenses = 'entrepreneur_contribution') GROUP BY Platform",
                                    (Current_date,date(Current_date.year,1,1))).fetchall()

    all_paid_YTD_N_1 = con.execute("""SELECT IFNULL(SUM(Paid),0),Platform FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site
                                    WHERE Month <= %s AND Month >=%s AND Ref_expenses <> 'debt' AND Ref_expenses <> 'WinS_invoice'
                                    AND Ref_expenses <> 'withdrawal' GROUP BY Platform""",
                                    (Current_date-relativedelta(months=+12),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()
    
    all_expenses_YTD_N_1 = con.execute("""SELECT SUM(Amount_expenses),Platform FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site
                                        WHERE Month <= %s AND Month >=%s AND (Ref_expenses = 'stock_ts' OR Ref_expenses = 'bottle_invoice'
                                        OR Ref_expenses = 'technical intervention' OR Ref_expenses = 'water quality alert'
                                        OR Ref_expenses = 'entrepreneur_contribution') GROUP BY Platform""",
                                        ((Current_date-relativedelta(months=+12)),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()

    all_paid_debt1_YTD = con.execute("""SELECT SUM(Paid), Platform 
                            FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
                            WHERE (Month <= %s AND Month >= %s) 
                            AND ((Ref_expenses= 'debt' AND Amount_expenses > 0)
                                    OR (Ref_expenses = 'adjustment' AND Paid >0)) AND Amount_expenses-Paid >= 0
                            GROUP BY Platform""",(Current_date,date(Current_date.year,1,1))).fetchall()
    
    all_paid_debt2_YTD = con.execute("""SELECT SUM(Amount_expenses), Platform 
                            FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
                            WHERE (Month <= %s AND Month >= %s) AND ((Ref_expenses= 'debt' AND Amount_expenses > 0) OR Ref_expenses = "adjustment")
                            AND Amount_expenses - Paid < 0 
                            GROUP BY Platform""",(Current_date,date(Current_date.year,1,1))).fetchall()

    all_paid_debt1_YTD_N_1 = con.execute("""SELECT SUM(Paid), Platform 
                            FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
                            WHERE (Month <= %s AND Month >= %s) AND ((Ref_expenses= 'debt' AND Amount_expenses > 0)
                                    OR (Ref_expenses = 'adjustment' AND Paid >0)) AND Amount_expenses-Paid >= 0
                            GROUP BY Platform""",(Current_date-relativedelta(months=+12),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()
    all_paid_debt2_YTD_N_1 = con.execute("""SELECT SUM(Amount_expenses), Platform 
                            FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
                            WHERE (Month <= %s AND Month >= %s) AND Ref_expenses= 'debt' AND Amount_expenses > 0 
                            AND Amount_expenses - Paid < 0 
                            GROUP BY Platform""",(Current_date-relativedelta(months=+12),date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()

    all_debt_january = con.execute("""SELECT SUM(Amount_expenses),SUM(Paid),Platform
                                    FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE Month = %s 
                                    AND Ref_expenses = 'debt' AND Amount_Expenses > 0 GROUP BY Platform,Month""",
                                    (date(Current_date.year,1,1))).fetchall()
    all_debt_january_N_1 = con.execute("""SELECT SUM(Amount_expenses),SUM(Paid),Platform
                                    FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site WHERE Month = %s 
                                    AND Ref_expenses = 'debt' AND Amount_Expenses > 0 GROUP BY Platform,Month""",
                                    (date((Current_date-relativedelta(months=+12)).year,1,1))).fetchall()

##########WRITE TITLE#########

    worksheet.set_column('%s:%s'%(xl_col_to_name(Column),xl_col_to_name(Column)),22.91)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+1),xl_col_to_name(Column+1)),40.36)
    worksheet.set_column('%s:%s'%(xl_col_to_name(Column+2),xl_col_to_name(Column+len(Platform)+1)),10)
    LineTitle = 0
    worksheet.write(Line+LineTitle,Column,'KPI 7 - Debts',Bold_Number_format)
    worksheet.write(Line+LineTitle,Column+1,'%s %s - %s %s'%(calendar.month_name[int(Current_date.month)][0:3],Current_date.year,calendar.month_name[int(Current_date.month)][0:3],Current_date.year),KPI6_Title_format)
    LineTitle+=1


    worksheet.write(Line+LineTitle,Column+1,'Total Debts',KPI6_1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Total Debts last month',KPI6_1_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Total Savings',KPI6_1_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Total Savings last month',KPI6_1_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Nb sites with debts',KPI6_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'vs last month',KPI6_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Nb sites with debts > 1000$',KPI6_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'vs last month',KPI6_2_format)
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Collection Rate with debt settlement YTD',KPI6_3_format)
    worksheet.write_comment(Line+LineTitle,Column+1,'The collection rate including debts is typically lower earlier in the year as the weight of debts in the total of the amounts to be recovered is higher. The CR will automatically increase after a few months just because of the weighting.', {'x_scale': 4.5, 'y_scale': 0.5})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Collection Rate last year',KPI6_3_format)
    worksheet.set_row(Line+LineTitle,None,None,{'level':1,'hidden':True})
    LineTitle+=1
    worksheet.write(Line+LineTitle,Column+1,'Evolution YoY',KPI6_3_bottom_format)
    LineTitle+=1

#########WRITE DATA###########
    
    Debt = [sum(i[0] for i in allDebt),sum(i[1] for i in allDebt),sum(i[2] for i in allDebt),sum(i[3] for i in allDebt),"Total"] 
    allDebt.append(Debt)
    Debt_M_1 = [sum(i[0] for i in allDebt_M_1),sum(i[1] for i in allDebt_M_1),sum(i[2] for i in allDebt_M_1),sum(i[3] for i in allDebt_M_1),"Total"] 
    allDebt_M_1.append(Debt_M_1)

    Paid = [sum(i[0] for i in all_paid_YTD),"Total"] 
    all_paid_YTD.append(Paid)
    Expenses = [sum(i[0] for i in all_expenses_YTD),"Total"] 
    all_expenses_YTD.append(Expenses)

    Paid_N_1 = [sum(i[0] for i in all_paid_YTD_N_1),"Total"] 
    all_paid_YTD_N_1.append(Paid_N_1)
    Expenses_N_1 = [sum(i[0] for i in all_expenses_YTD_N_1),"Total"] 
    all_expenses_YTD_N_1.append(Expenses_N_1)
    
    Paid_debt_1 = [sum(i[0] for i in all_paid_debt1_YTD),"Total"] 
    all_paid_debt1_YTD.append(Paid_debt_1)
    Paid_debt_2 = [sum(i[0] for i in all_paid_debt2_YTD),"Total"] 
    all_paid_debt2_YTD.append(Paid_debt_2)

    Paid_debt_1_N_1 = [sum(i[0] for i in all_paid_debt1_YTD_N_1),"Total"] 
    all_paid_debt1_YTD_N_1.append(Paid_debt_1_N_1)
    Paid_debt_2_N_1 = [sum(i[0] for i in all_paid_debt2_YTD_N_1),"Total"] 
    all_paid_debt2_YTD_N_1.append(Paid_debt_2_N_1)

    Debt_january = [sum(i[0] for i in all_debt_january if i[0] is not None),sum(i[1] for i in all_debt_january if i[1] is not None),"Total"] 
    all_debt_january.append(Debt_january)
    Debt_january_N_1 = [sum(i[0] for i in all_debt_january_N_1 if i[0] is not None),sum(i[1] for i in all_debt_january_N_1 if i[1] is not None),"Total"] 
    all_debt_january_N_1.append(Debt_january_N_1)

    Platform.append(("Total",))

    for i in range(len(Platform)):
        Linefor = 0
        #Data Exctraction
        Debt = list(filter(lambda row: row[4] == Platform[i][0], allDebt)) or [(0,0,0,0,0)]
        Debt_M_1 = list(filter(lambda row: row[4] == Platform[i][0], allDebt_M_1)) or [(0,0,0,0,0)]

        Paid = list(filter(lambda row: row[1] == Platform[i][0], all_paid_YTD)) or [(0,0)]
        Expenses = list(filter(lambda row: row[1] == Platform[i][0], all_expenses_YTD)) or [(0,0)]

        Paid_N_1 = list(filter(lambda row: row[1] == Platform[i][0], all_paid_YTD_N_1)) or [(0,0)]
        Expenses_N_1 = list(filter(lambda row: row[1] == Platform[i][0], all_expenses_YTD_N_1)) or [(0,0)]
        
        Paid_debt1 = list(filter(lambda row: row[1] == Platform[i][0], all_paid_debt1_YTD)) or [(0,0)]
        Paid_debt2 = list(filter(lambda row: row[1] == Platform[i][0], all_paid_debt2_YTD)) or [(0,0)]
        Paid_debt1_N_1 = list(filter(lambda row: row[1] == Platform[i][0], all_paid_debt1_YTD_N_1)) or [(0,0)]
        Paid_debt2_N_1 = list(filter(lambda row: row[1] == Platform[i][0], all_paid_debt2_YTD_N_1)) or [(0,0)]

        DebtJanuary = list(filter(lambda row: row[2] == Platform[i][0], all_debt_january)) or [(0,0,0)]
        DebtJanuary_N_1 = list(filter(lambda row: row[2] == Platform[i][0], all_debt_january_N_1)) or [(0,0,0)]

       
        worksheet.write(Line+Linefor,2+i+Column,Platform[i][0],KPI6_Title_format)
        Linefor+=1

        worksheet.write(Line+Linefor,2+i+Column,Debt[0][0]/exchange_rate_year(Current_date),KPI6_1_dol_format)
        Linefor+=1
        worksheet.write(Line+Linefor,2+i+Column,Debt_M_1[0][0]/exchange_rate_year(Current_date-relativedelta(months=+1)),KPI6_1_dol_format)
        Linefor+=1
        worksheet.write(Line+Linefor,2+i+Column,Debt[0][1]/exchange_rate_year(Current_date),KPI6_1_dol_format)
        Linefor+=1
        worksheet.write(Line+Linefor,2+i+Column,Debt_M_1[0][1]/exchange_rate_year(Current_date-relativedelta(months=+1)),KPI6_1_dol_format)
        Linefor+=1
        worksheet.write(Line+Linefor,2+i+Column,Debt[0][2],KPI6_2_format)
        Linefor+=1
        worksheet.write(Line+Linefor,2+i+Column,Debt_M_1[0][2],KPI6_2_format)
        Linefor+=1
        worksheet.write(Line+Linefor,2+i+Column,Debt[0][3],KPI6_2_format)
        Linefor+=1
        worksheet.write(Line+Linefor,2+i+Column,Debt_M_1[0][3],KPI6_2_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,2+i+Column,"=(%s+%s+%s)/(%s+%s)"%(Paid[0][0],Paid_debt1[0][0],Paid_debt2[0][0],Expenses[0][0],DebtJanuary[0][0]),KPI6_3_percent_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,2+i+Column,"=(%s+%s+%s)/(%s+%s)"%(Paid_N_1[0][0],Paid_debt1_N_1[0][0],Paid_debt2_N_1[0][0],Expenses_N_1[0][0],DebtJanuary_N_1[0][0]),KPI6_3_percent_format)
        Linefor+=1
        worksheet.write_formula(Line+Linefor,2+i+Column,"=((%s+%s+%s)/(%s+%s)-(%s+%s+%s)/(%s+%s))*100"%(Paid[0][0],Paid_debt1[0][0],Paid_debt2[0][0],Expenses[0][0],DebtJanuary[0][0],Paid_N_1[0][0],Paid_debt1_N_1[0][0],Paid_debt2_N_1[0][0],Expenses_N_1[0][0],DebtJanuary_N_1[0][0]),KPI6_3_pt_bottom_format)
        Linefor+=1
    return(LineTitle+1)

def RecapTable(workbook,Current_date,Date_1):
    if Current_date == Date_1:
        worksheet = workbook.add_worksheet('Dashboard Monthly')
    elif Date_1.month == 1:
        worksheet = workbook.add_worksheet('Dashboard YTD')
    else:
        worksheet = workbook.add_worksheet('Dashboard 12 months')
    worksheet.set_zoom(85)
    worksheet.set_tab_color('#000000')
    worksheet.hide_gridlines(2)
    Line = 1
    if not(Date_1 == Current_date-relativedelta(months=+12) and Date_1.month != 1):
         Line += KioskNetwork(workbook,worksheet,Current_date,Date_1,Line,0)
    Line += Volume(workbook,worksheet,Current_date,Date_1,Line,0)
    Line += ChannelMix(workbook,worksheet,Current_date,Date_1,Line,0)
    Line += Revenue(workbook,worksheet,Current_date,Date_1,Line,0)
    Line += Consumable(workbook,worksheet,Current_date,Date_1,Line,0)
    # Operators per site KPI
    Line += operators(workbook,worksheet,Current_date,Date_1,Line,0)
    if Date_1 == Current_date:
        Line += Debt(workbook,worksheet,Date_1,Line,0)

def ObjectifTS(workbook):
    con = db.pool.connect()
    worksheet = workbook.add_worksheet("Objectives")

########DATA SELECTION ACTIVE SITES########
    

def LaunchExcelCreationManagementDashboard(Date,exchange_rate):
    Current_date = Date

    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir()+'/Mngt Dashboard TS '+Year+'-'+Month+'.xlsx'
    workbook = xlsxwriter.Workbook(filepath)


    RecapTable(workbook,Current_date,Current_date)
    if Current_date.month != 1:
        RecapTable(workbook,Current_date,date(Current_date.year,1,1))
    if Current_date.month !=12:
        RecapTable(workbook,Current_date,Current_date-relativedelta(months=+11))
    TabData(workbook,Current_date,exchange_rate)
    workbook.close()

if __name__ == '__main__':
    Current_date = date(2022,7,1)
    TabData(Current_date,4068)
    RecapTable(Current_date,4068)
    #workbook.close()
