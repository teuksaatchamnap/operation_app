from re import A
import db
from monthlyreport.Functionutils import CheckTechnicalItem,NewCalculTier
import xlsxwriter
from datetime import date,datetime
import tempfile
from dateutil.relativedelta import *
from xlsxwriter.utility import xl_col_to_name,xl_rowcol_to_cell
import os



def ExcelOrder(exchange_rate,Current_date,workbook,First_date = 0):
    con=db.pool.connect()
    worksheet_invoice = workbook.add_worksheet("1. Invoice listing")
    worksheet_request = workbook.add_worksheet("requests")
    format_bgorange = workbook.add_format({"bg_color": "F8CBAD",'center_across':True, 'bold' : True})
    format_bold = workbook.add_format({"bold": True})
    format_title_request = workbook.add_format({"bg_color" : '00B0F0', 'font_color' : 'white','bold' : True})
    format_title = workbook.add_format({"top" : 2, 'bottom' : 2, 'center_across' : True, 'bold' : True})
    format_date_title = workbook.add_format({'num_format' : 'yyyy-mm-dd hh:mm:ss','bold' : True})
    format_date = workbook.add_format({'num_format' : 'yyyy/mm/dd'})
    format_number = workbook.add_format({'num_format' : '# ##0'})
    format_number_normal = workbook.add_format({'num_format' : 1})

    format_dec = workbook.add_format({'num_format' : '# ##0.00'})
    worksheet_invoice.set_column("A:A",11.89)
    worksheet_invoice.set_column("B:B",18.67)
    worksheet_invoice.set_column("C:E",9.11)
    worksheet_invoice.set_column("F:F",15.22)
    worksheet_invoice.set_column("G:K",9.11)
    worksheet_invoice.set_column("L:M",12.89)
    worksheet_invoice.set_column("N:O",9.11)

    worksheet_invoice.write(0,0,"Company Name",format_bold)
    worksheet_invoice.write(1,0,"Report Type",format_bold)
    worksheet_invoice.write(2,0,"Report Date",format_bold)

    worksheet_invoice.write(0,1,"Teuk Saat",format_bold)
    worksheet_invoice.write(1,1,"Invoice listing",format_bold)
    worksheet_invoice.write(2,1,datetime.today(),format_date_title)

    worksheet_invoice.merge_range(3,0,3,1,"Invoice cancelled/no stock release",format_bgorange)

    worksheet_invoice.write(4,0,"Date",format_title)
    worksheet_invoice.write(4,1,"Invoice num (Reference)",format_title)
    worksheet_invoice.write(4,2,"Sites",format_title)
    worksheet_invoice.write(4,3,"Type",format_title)
    worksheet_invoice.write(4,4,"Item Code",format_title)
    worksheet_invoice.write(4,5,"Item name Khmer",format_title)
    worksheet_invoice.write(4,6,"Sale Quantity",format_title)
    worksheet_invoice.write(4,7,"Sale Unit",format_title)
    worksheet_invoice.write(4,8,"Unit Price (Riel)",format_title)
    worksheet_invoice.write(4,9,"Amount",format_title)
    worksheet_invoice.write(4,10,"Amount Dollar",format_title)
    worksheet_invoice.write(4,11,"Cashier/Admin",format_title)
    worksheet_invoice.write(4,12,"Advisor/ToE",format_title)
    worksheet_invoice.write(4,13,"WH_Locations",format_title)
    worksheet_invoice.write(4,14,"Allocation",format_title)
    worksheet_invoice.write(4,15,"Payment Method",format_title)
    worksheet_invoice.write(4,16,"Date Submission",format_title)
    worksheet_invoice.write(4,17,"PO",format_title)
    worksheet_invoice.write(4,18,"Supplier",format_title)
    worksheet_invoice.write(4,19,"Email_Requestor",format_title)
    worksheet_invoice.write(4,20,"Email_Approver",format_title)
    worksheet_invoice.write(4,21,"Remark",format_title)

    worksheet_request.set_column('A:A',10)
    worksheet_request.set_column('D:D',42)
    worksheet_request.set_column('E:E',45)
    worksheet_request.set_column('I:J',14)

    worksheet_request.write(0,0,"Date",format_title_request)
    worksheet_request.write(0,1,"Sites",format_title_request)
    worksheet_request.write(0,2,"Item Code",format_title_request)
    worksheet_request.write(0,3,"Item name",format_title_request)
    worksheet_request.write(0,4,"Item name Khmer",format_title_request)
    worksheet_request.write(0,5,"Sale Quantity",format_title_request)
    worksheet_request.write(0,6,"Unit",format_title_request)
    worksheet_request.write(0,7,"Unit price (Riel)",format_title_request)
    worksheet_request.write(0,8,"Amount to pay",format_title_request)
    worksheet_request.write(0,9,"Advisor/ToE",format_title_request)
    worksheet_request.write(0,10,"Platform",format_title_request)
    worksheet_request.write(0,11,"Validated",format_title_request)
    worksheet_request.write(0,12,"Payment",format_title_request)
    worksheet_request.write(0,13,"Date Submission",format_title_request)
    if First_date == 0:
        # Queries for current month
        # Validated consumables for current month
        query = con.execute("""
        SELECT c.Id_Site, s.Advisor, s.Platform, c.Month, c.Item, c.Khmer_name, c.English_name,
               c.Number_Item, c.Unit, c.Price_Item, p.Cashier, s.Project, c.Payment_method,
               c.Date_Submission, c.PO, c.Supplier, c.EmailRequestor, c.EmailApprover, c.Remark
        FROM Consumable c
        LEFT JOIN Sites s ON c.Id_Site = s.Id_Site
        LEFT JOIN (
            SELECT DISTINCT Code_Platform, Cashier
            FROM Platform
        ) p ON s.Old_Platform = p.Code_Platform
        WHERE c.Month = %s AND c.Validate = %s
        ORDER BY c.Id_Site, c.Month
        """, (Current_date, 1))
        allListConsumable_validate = query.fetchall()

        # All consumables for current month
        query = con.execute("""
        SELECT c.Id_Site, s.Advisor, s.Platform, c.Month, c.Item, c.Khmer_name, c.English_name,
               c.Number_Item, c.Unit, c.Price_Item, p.Cashier, s.Project, c.Validate,
               c.Payment_method, c.Date_Submission, c.PO, c.Supplier, c.EmailRequestor, c.EmailApprover, c.Remark
        FROM Consumable c
        LEFT JOIN Sites s ON c.Id_Site = s.Id_Site
        LEFT JOIN (
            SELECT DISTINCT Code_Platform, Cashier
            FROM Platform
        ) p ON s.Old_Platform = p.Code_Platform
        WHERE c.Month = %s
        ORDER BY c.Code_Consumable
        """, (Current_date,))
        allListConsumable = query.fetchall()

        # Distinct sites with consumables for current month
        query = con.execute("""
        SELECT DISTINCT Id_Site, Month
        FROM Consumable
        WHERE Month = %s
        ORDER BY Month
        """, (Current_date,))
        ListSite_validated = query.fetchall()

        query = con.execute("""
        SELECT DISTINCT Id_Site, Month
        FROM Consumable
        WHERE Month = %s
        ORDER BY Month
        """, (Current_date,))
        ListSite = query.fetchall()
    else:
        # Queries for a date range
        # Validated consumables for date range
        query = con.execute("""
        SELECT DISTINCT c.Id_Site, s.Advisor, s.Platform, c.Month, c.Item, c.Khmer_name, c.English_name,
               c.Number_Item, c.Unit, c.Price_Item, p.Cashier, s.Project,
               c.Payment_method, c.Date_Submission, c.PO, c.Supplier, c.EmailRequestor, c.EmailApprover, c.Remark
        FROM Consumable c
        LEFT JOIN Sites s ON c.Id_Site = s.Id_Site
        LEFT JOIN (
            SELECT DISTINCT Code_Platform, Cashier
            FROM Platform
        ) p ON s.Old_Platform = p.Code_Platform
        WHERE c.Month <= %s AND c.Month >= %s AND c.Validate = %s
        ORDER BY c.Code_Consumable
        """, (Current_date, First_date, 1))
        allListConsumable_validate = query.fetchall()

        # All consumables for date range
        query = con.execute("""
        SELECT DISTINCT c.Id_Site, s.Advisor, s.Platform, c.Month, c.Item, c.Khmer_name, c.English_name,
               c.Number_Item, c.Unit, c.Price_Item, p.Cashier, s.Project, c.Validate,
               c.Payment_method, c.Date_Submission
        FROM Consumable c
        LEFT JOIN Sites s ON c.Id_Site = s.Id_Site
        LEFT JOIN (
            SELECT DISTINCT Code_Platform, Cashier
            FROM Platform
        ) p ON s.Old_Platform = p.Code_Platform
        WHERE c.Month <= %s AND c.Month >= %s
        ORDER BY c.Code_Consumable
        """, (Current_date, First_date))
        allListConsumable = query.fetchall()

        # Distinct sites with consumables for date range
        query = con.execute("""
        SELECT DISTINCT Id_Site, Month
        FROM Consumable
        WHERE Month <= %s AND Month >= %s
        ORDER BY Month
        """, (Current_date, First_date))
        ListSite_validated = query.fetchall()

        query = con.execute("""
        SELECT DISTINCT Id_Site, Month
        FROM Consumable
        WHERE Month <= %s AND Month >= %s
        ORDER BY Month
        """, (Current_date, First_date))
        ListSite = query.fetchall()

    Line_Number = 5
    Line_Number_request = 1
    for k in range(len(allListConsumable_validate)):
        if k ==0:
            Number_Invoice = 1
        else:
            if allListConsumable_validate[k][0] != allListConsumable_validate[k-1][0]:
                Number_Invoice +=1

        if allListConsumable_validate[k][7] >= 0:
            worksheet_invoice.write(k+Line_Number,0,allListConsumable_validate[k][3],format_date)
            worksheet_invoice.write(k+Line_Number,2,allListConsumable_validate[k][0])
            worksheet_invoice.write(k+Line_Number,4,allListConsumable_validate[k][4])
            if (allListConsumable_validate[k][4] == '401001' or allListConsumable_validate[k][4] == '401002') and allListConsumable_validate[k][2]:
                            
                if allListConsumable_validate[k][11]:
                    worksheet_invoice.write(k+Line_Number,1,"BT%s%s%s%s%s-%s"%('P','P',str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                elif allListConsumable_validate[k][2] == 'BTB':
                    worksheet_invoice.write(k+Line_Number,1,"BT%s%s%s%s%s-%s"%(allListConsumable_validate[k][2][0],allListConsumable_validate[k][2][2],str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                else:
                    worksheet_invoice.write(k+Line_Number,1,"BT%s%s%s%s%s-%s"%(allListConsumable_validate[k][2][0],allListConsumable_validate[k][2][1],str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                worksheet_invoice.write(k+Line_Number,3,"Bottle Invoice")
            elif allListConsumable_validate[k][2] and CheckTechnicalItem(allListConsumable_validate[k][4]):
                if allListConsumable_validate[k][11]:
                    worksheet_invoice.write(k+Line_Number,1,"TI%s%s%s%s%s-%s"%('P','P',str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                elif allListConsumable_validate[k][2] == 'BTB':
                    worksheet_invoice.write(k+Line_Number,1,"TI%s%s%s%s%s-%s"%(allListConsumable_validate[k][2][0],allListConsumable_validate[k][2][2],str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                else:
                    worksheet_invoice.write(k+Line_Number,1,"TI%s%s%s%s%s-%s"%(allListConsumable_validate[k][2][0],allListConsumable_validate[k][2][1],str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                worksheet_invoice.write(k+Line_Number,3,"Technical Intervention")

            elif allListConsumable_validate[k][2]:
                if allListConsumable_validate[k][11]:
                    worksheet_invoice.write(k+Line_Number,1,"SI%s%s%s%s%s-%s"%('P','P',str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                elif allListConsumable_validate[k][2] == 'BTB':
                    worksheet_invoice.write(k+Line_Number,1,"SI%s%s%s%s%s-%s"%(allListConsumable_validate[k][2][0],allListConsumable_validate[k][2][2],str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                else:
                    worksheet_invoice.write(k+Line_Number,1,"SI%s%s%s%s%s-%s"%(allListConsumable_validate[k][2][0],allListConsumable_validate[k][2][1],str(Current_date.year)[2],str(Current_date.year)[3],str(Current_date.month).zfill(2),str(Number_Invoice+1).zfill(4)))
                worksheet_invoice.write(k+Line_Number,3,"Stock Invoice")

            worksheet_invoice.write(k+Line_Number,5,allListConsumable_validate[k][5])
            worksheet_invoice.write(k+Line_Number,6,allListConsumable_validate[k][7],format_number_normal)
            worksheet_invoice.write(k+Line_Number,7,allListConsumable_validate[k][8])
            worksheet_invoice.write_formula(k+Line_Number,8,'=IFERROR(%s/%s,0)'%(allListConsumable_validate[k][9],allListConsumable_validate[k][7]),format_number)
            worksheet_invoice.write(k+Line_Number,9,allListConsumable_validate[k][9],format_number)
            worksheet_invoice.write(k+Line_Number,10,allListConsumable_validate[k][9]/exchange_rate,format_dec)
            worksheet_invoice.write(k+Line_Number,12,allListConsumable_validate[k][1])
            if allListConsumable_validate[k][11]:
                worksheet_invoice.write(k+Line_Number,11,allListConsumable_validate[k][10])
                worksheet_invoice.write(k+Line_Number,13,allListConsumable_validate[k][2])
                worksheet_invoice.write(k+Line_Number,14,"Project")
            else:
                worksheet_invoice.write(k+Line_Number,11,allListConsumable_validate[k][10])
                worksheet_invoice.write(k+Line_Number,13,allListConsumable_validate[k][2])
                worksheet_invoice.write(k+Line_Number,14,allListConsumable_validate[k][2])
            worksheet_invoice.write(k+Line_Number,15,allListConsumable_validate[k][12])
            worksheet_invoice.write(k+Line_Number,16,allListConsumable_validate[k][13],format_date)
            worksheet_invoice.write(k+Line_Number,17,allListConsumable_validate[k][14],format_date)
            worksheet_invoice.write(k+Line_Number,18,allListConsumable_validate[k][15],format_date)
            worksheet_invoice.write(k+Line_Number,19,allListConsumable_validate[k][16],format_date)
            worksheet_invoice.write(k+Line_Number,20,allListConsumable_validate[k][17],format_date)
            worksheet_invoice.write(k+Line_Number,21,allListConsumable_validate[k][18],format_date)
            
            

    worksheet_invoice.autofilter(4,0,Line_Number+len(allListConsumable_validate),16)

    for j in range(len(allListConsumable)):
        if allListConsumable[j][7] > 0 :
            worksheet_request.write(Line_Number_request+j,0,allListConsumable[j][3],format_date)
            worksheet_request.write(Line_Number_request+j,1,allListConsumable[j][0])
            worksheet_request.write(Line_Number_request+j,2,allListConsumable[j][4])

            worksheet_request.write(Line_Number_request+j,3,allListConsumable[j][6])
            worksheet_request.write(Line_Number_request+j,4,allListConsumable[j][5])
            worksheet_request.write(Line_Number_request+j,5,allListConsumable[j][7],format_number)
            worksheet_request.write(Line_Number_request+j,6,allListConsumable[j][8])
            worksheet_request.write(Line_Number_request+j,7,allListConsumable[j][9]/allListConsumable[j][7],format_number)
            worksheet_request.write(Line_Number_request+j,8,allListConsumable[j][9],format_number)
            worksheet_request.write(Line_Number_request+j,9,allListConsumable[j][1])
            if allListConsumable[j][11]:
                worksheet_request.write(Line_Number_request+j,10,"PP")
            else:
                worksheet_request.write(Line_Number_request+j,10,allListConsumable[j][2])
            if allListConsumable[j][12]:
                worksheet_request.write(Line_Number_request+j,11,"yes")
            else:
                worksheet_request.write(Line_Number_request+j,11,"no")
            if allListConsumable[j][13] == 1:
                worksheet_request.write(Line_Number_request+j,12,"Invoice")
            elif allListConsumable[j][13] == 2:
                worksheet_request.write(Line_Number_request+j,12,"Cash")
            else:
                worksheet_request.write(Line_Number_request+j,12,"Project")
            worksheet_request.write(Line_Number_request+j,13,allListConsumable[j][14],format_date)


    workbook.close()

def DataConsumableSold(workbook,exchange_rate,Current_date):
    con=db.pool.connect()
    worksheet = workbook.add_worksheet("Data Sites")

#####################Data Extraction #######################
    Date_N_1 = Current_date - relativedelta(months=+12)
    Date_N_2 = Date_N_1 - relativedelta(months=+12)
    Date_janv = date(Current_date.year-1,12,1)
    Date_janv_ly = date(Date_N_1.year-1,12,1)

    ListTier = NewCalculTier(Current_date)[0]
    allSiteInfo = con.execute("""SELECT Id_Site,Old_Platform,Advisor FROM Sites WHERE Old_Platform IS NOT NULL AND Old_Platform <>"Dead" """).fetchall()

    allSales_Month = con.execute("""SELECT Total_Sales - Bottle_Sales,Id_Site,(Total_income-Bottle_income)/%s FROM Sales WHERE Month = %s""",(exchange_rate,Current_date)).fetchall()
    allSales_YTD = con.execute("""SELECT SUM(Total_Sales - Bottle_Sales),Id_Site,SUM(Total_income-Bottle_income)/%s FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(exchange_rate,Current_date,Date_janv)).fetchall() 
    allSales_12months = con.execute("""SELECT SUM(Total_Sales - Bottle_Sales),Id_Site,SUM(Total_income-Bottle_income)/%s FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(exchange_rate,Current_date,Date_N_1)).fetchall()  

    allWaterMeter_Month = con.execute("""SELECT Water_consume/20,Id_Site FROM Indicators WHERE Month = %s""",(Current_date)).fetchall()
    allWaterMeter_YTD = con.execute("""SELECT SUM(Water_consume)/20,Id_Site FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(Current_date,Date_janv)).fetchall() 
    allWaterMeter_12months = con.execute("""SELECT SUM(Water_consume)/20,Id_Site FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(Current_date,Date_N_1)).fetchall()

    allSales_Month_ly = con.execute("""SELECT Total_Sales - Bottle_Sales,Id_Site,(Total_income-Bottle_income)/%s FROM Sales WHERE Month = %s""",(exchange_rate,Date_N_1)).fetchall()
    allSales_YTD_ly = con.execute("""SELECT SUM(Total_Sales - Bottle_Sales),Id_Site,SUM(Total_income-Bottle_income)/%s FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(exchange_rate,Date_N_1,Date_janv_ly)).fetchall() 
    allSales_12months_ly = con.execute("""SELECT SUM(Total_Sales - Bottle_Sales),Id_Site,SUM(Total_income-Bottle_income)/%s FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(exchange_rate,Date_N_1,Date_N_2)).fetchall()  

    allWaterMeter_Month_ly = con.execute("""SELECT Water_consume/20,Id_Site FROM Indicators WHERE Month = %s""",(Date_N_1)).fetchall()
    allWaterMeter_YTD_ly = con.execute("""SELECT SUM(Water_consume)/20,Id_Site FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(Date_N_1,Date_janv_ly)).fetchall() 
    allWaterMeter_12months_ly = con.execute("""SELECT SUM(Water_consume)/20,Id_Site FROM Indicators WHERE Month <= %s AND Month > %s GROUP BY Id_Site""",(Date_N_1,Date_N_2)).fetchall()

    allItemSold_Month = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Id_Site,Item FROM Consumable 
                                    WHERE Month = %s AND Validate = 1 GROUP BY Id_Site,Item""",(exchange_rate,Current_date)).fetchall()
    allItemSold_YTD = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Id_Site,Item FROM Consumable 
                                    WHERE Month <= %s AND Month > %s AND Validate = 1 GROUP BY Id_Site,Item""",(exchange_rate,Current_date,Date_janv)).fetchall() 
    allItemSold_12months = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s AS Sales_total,Id_Site,Item FROM Consumable 
                                    WHERE Month <= %s AND Month > %s AND Validate = 1 GROUP BY Id_Site,Item 
                                    ORDER BY Sales_total""",(exchange_rate,Current_date,Date_N_1)).fetchall()

    allItemSold_Month_ly = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Id_Site,Item 
                                       FROM Consumable WHERE Month = %s AND Validate = 1 
                                       GROUP BY Id_Site,Item""",(exchange_rate,Date_N_1)).fetchall()
    allItemSold_YTD_ly = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Id_Site,Item 
                                     FROM Consumable WHERE Month <= %s AND Month > %s AND Validate = 1  
                                     GROUP BY Id_Site,Item""",(exchange_rate,Date_N_1,Date_janv_ly)).fetchall() 
    allItemSold_12months_ly = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s 
                                          AS Sales_total,Id_Site,Item FROM Consumable 
                                          WHERE Month <= %s AND Month > %s AND Validate = 1  
                                          GROUP BY Id_Site,Item ORDER BY Sales_total""",(exchange_rate,Date_N_1,Date_N_2)).fetchall()

    allItemSoldbyItem = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item) AS Sales_total,Item 
                                    FROM Consumable WHERE Month <= %s AND Month > %s AND Validate = 1  
                                    GROUP BY Item ORDER BY Sales_total DESC""",(Current_date,Date_N_1)).fetchall()
    ItemName = con.execute("""SELECT DISTINCT Item,English_name FROM Consumable""").fetchall()

#################### Format #############################
    
    Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
    bg_grey_format = workbook.add_format({'bg_color':'#BFBFBF'})
    Title_Sales_format = workbook.add_format({'bg_color':'#0070C0','font_color':'white','bold':True})
    Title_Item_format = workbook.add_format({'bg_color':'#DA9694','bold':True})
    Title_Item_percent_format = workbook.add_format({'bg_color':'#F4B084','bold':True})
    percent_format = workbook.add_format({'num_format' : '0%'})
    Number_format = workbook.add_format({'num_format':'# ### ##0'})
    Percentage_format = workbook.add_format({'num_format':'+0%;-0%'})
    Number_bold_format = workbook.add_format({'num_format':'# ### ##0','bold':True})

    worksheet.set_column('A:A',15)
    worksheet.set_column('B:AP',9)
    worksheet.set_column('F:F',15.5)
    worksheet.freeze_panes(2,3)
#######################Writing data ########################
    
    worksheet.write("D1","Average",Number_bold_format)
    worksheet.write("D2","Total",Number_bold_format)

    worksheet.data_validation('A1',{'validate' : 'list',
                                    'source' : ['Current Month', 'Last 12 Months','YTD']})
    worksheet.write('A1', 'YTD',Select_format)

    worksheet.data_validation('A2',{'validate' : 'list',
                                    'source' : ['Quantity','Revenue ($)']})
    worksheet.write('A2', 'Revenue ($)',Select_format)

    worksheet.write(2,0,"Site",Number_bold_format)
    worksheet.write(2,1,"Platform",Number_bold_format)
    worksheet.write(2,2,"Advisor",Number_bold_format)
    worksheet.write(2,3,"Tier",Number_bold_format)
    worksheet.write(2,4,"Bot Delivered (inc WinS)",Title_Sales_format)
    worksheet.write(2,5,"Water Meter",Title_Sales_format)
    worksheet.write(2,6,"Bot Delivered (inc WinS) vs N-1",Title_Sales_format)
    worksheet.write(2,7,"Water Meter vs N-1",Title_Sales_format)

    worksheet.write("AR1","evolution vs. N-1 same period in %",Number_bold_format)
    
    worksheet.set_column("F:H",None,None,{'level':1,'hidden':True})

    for i in range(len(allSiteInfo)):
        Sites_info = list(filter(lambda row: row[0] == allSiteInfo[i][0], allSiteInfo)) or [("\"\"","\"\"","\"\"")]
        Tier = list(filter(lambda row: row[0] == allSiteInfo[i][0], ListTier)) or [("\"\"","\"\"","\"\"")]

        Sales_Month = list(filter(lambda row: row[1] == allSiteInfo[i][0], allSales_Month)) or [("\"\"","\"\"","\"\"")]
        Sales_YTD = list(filter(lambda row: row[1] == allSiteInfo[i][0], allSales_YTD)) or [("\"\"","\"\"","\"\"")]
        Sales_12months = list(filter(lambda row: row[1] == allSiteInfo[i][0], allSales_12months)) or [("\"\"","\"\"","\"\"")]

        WaterMeter_Month = list(filter(lambda row: row[1] == allSiteInfo[i][0], allWaterMeter_Month)) or [("\"\"","\"\"","\"\"")]
        WaterMeter_YTD = list(filter(lambda row: row[1] == allSiteInfo[i][0], allWaterMeter_YTD)) or [("\"\"","\"\"","\"\"")]
        WaterMeter_12months = list(filter(lambda row: row[1] == allSiteInfo[i][0], allWaterMeter_12months)) or [("\"\"","\"\"","\"\"")]

        Sales_Month_ly = list(filter(lambda row: row[1] == allSiteInfo[i][0], allSales_Month_ly)) or [("\"\"","\"\"","\"\"")]
        Sales_YTD_ly = list(filter(lambda row: row[1] == allSiteInfo[i][0], allSales_YTD_ly)) or [("\"\"","\"\"","\"\"")]
        Sales_12months_ly = list(filter(lambda row: row[1] == allSiteInfo[i][0], allSales_12months_ly)) or [("\"\"","\"\"","\"\"")]

        WaterMeter_Month_ly = list(filter(lambda row: row[1] == allSiteInfo[i][0], allWaterMeter_Month_ly)) or [("\"\"","\"\"","\"\"")]
        WaterMeter_YTD_ly= list(filter(lambda row: row[1] == allSiteInfo[i][0], allWaterMeter_YTD_ly)) or [("\"\"","\"\"","\"\"")]
        WaterMeter_12months_ly = list(filter(lambda row: row[1] == allSiteInfo[i][0], allWaterMeter_12months_ly)) or [("\"\"","\"\"","\"\"")]

        Site_ItemSold_Month = list(filter(lambda row: row[2] == allSiteInfo[i][0], allItemSold_Month)) or [("\"\"","\"\"","\"\"","\"\"")]
        Site_ItemSold_YTD = list(filter(lambda row: row[2] == allSiteInfo[i][0], allItemSold_YTD)) or [("\"\"","\"\"","\"\"","\"\"")]
        Site_ItemSold_12Months = list(filter(lambda row: row[2] == allSiteInfo[i][0], allItemSold_12months)) or [("\"\"","\"\"","\"\"","\"\"")]

        Site_ItemSold_Month_ly = list(filter(lambda row: row[2] == allSiteInfo[i][0], allItemSold_Month_ly)) or [("\"\"","\"\"","\"\"","\"\"")]
        Site_ItemSold_YTD_ly = list(filter(lambda row: row[2] == allSiteInfo[i][0], allItemSold_YTD_ly)) or [("\"\"","\"\"","\"\"","\"\"")]
        Site_ItemSold_12Months_ly = list(filter(lambda row: row[2] == allSiteInfo[i][0], allItemSold_12months_ly)) or [("\"\"","\"\"","\"\"","\"\"")]

        worksheet.write(i+3,0,Sites_info[0][0])
        worksheet.write(i+3,1,Sites_info[0][1])
        worksheet.write(i+3,2,Sites_info[0][2])
        worksheet.write(i+3,3,Tier[0][1])

        worksheet.write_formula(i+3,4,"""=IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))"""%(Sales_Month[0][0],Sales_YTD[0][0],Sales_12months[0][0]),Number_format)
        worksheet.write_formula(i+3,5,"""=IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))"""%(WaterMeter_Month[0][0],WaterMeter_YTD[0][0],WaterMeter_12months[0][0]),Number_format)
        
        worksheet.write_formula(i+3,6,"""=IFERROR(IF($A$1="Current Month",%s/%s-1,IF($A$1="YTD",%s/%s-1,IF($A$1="Last 12 Months",%s/%s-1,""))),0)"""%(Sales_Month[0][0],Sales_Month_ly[0][0],Sales_YTD[0][0],Sales_YTD_ly[0][0],Sales_12months[0][0],Sales_12months_ly[0][0]),Percentage_format)
        worksheet.write_formula(i+3,7,"""=IFERROR(IF($A$1="Current Month",%s/%s-1,IF($A$1="YTD",%s/%s-1,IF($A$1="Last 12 Months",%s/%s-1,""))),0)"""%(WaterMeter_Month[0][0],WaterMeter_Month_ly[0][0],WaterMeter_YTD[0][0],WaterMeter_YTD_ly[0][0],WaterMeter_12months[0][0],WaterMeter_12months_ly[0][0]),Percentage_format)
        
        worksheet.write_formula(0,4,"=SUBTOTAL(1,%s4:%s%s)"%(xl_col_to_name(4),xl_col_to_name(4),len(allSiteInfo)+4),Number_bold_format)
        worksheet.write_formula(0,5,"=SUBTOTAL(1,%s4:%s%s)"%(xl_col_to_name(5),xl_col_to_name(5),len(allSiteInfo)+4),Number_bold_format)
        #worksheet.write_formula(0,6,"=SUBTOTAL(1,%s4:%s%s)"%(xl_col_to_name(6),xl_col_to_name(6),len(allSales_12months)+4),Number_bold_format)
        #worksheet.write_formula(0,7,"=SUBTOTAL(1,%s4:%s%s)"%(xl_col_to_name(7),xl_col_to_name(7),len(allSales_12months)+4),Number_bold_format)
        
        worksheet.write_formula(1,4,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(4),xl_col_to_name(4),len(allSiteInfo)+4),Number_bold_format)
        worksheet.write_formula(1,5,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(5),xl_col_to_name(5),len(allSiteInfo)+4),Number_bold_format)
        #worksheet.write_formula(1,6,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(6),xl_col_to_name(6),len(allSales_12months)+4),Number_bold_format)
        #worksheet.write_formula(1,7,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(7),xl_col_to_name(7),len(allSales_12months)+4),Number_bold_format)
        
        for j in range(len(allItemSoldbyItem)):
            
            ItemSold_Month = list(filter(lambda row: row[3] == allItemSoldbyItem[j][2], Site_ItemSold_Month)) or [("\"\"","\"\"","\"\"")]
            ItemSold_YTD = list(filter(lambda row: row[3] == allItemSoldbyItem[j][2], Site_ItemSold_YTD)) or [("\"\"","\"\"","\"\"")]
            ItemSold_12Months = list(filter(lambda row: row[3] == allItemSoldbyItem[j][2], Site_ItemSold_12Months)) or [("\"\"","\"\"","\"\"")]

            ItemSold_Month_ly = list(filter(lambda row: row[3] == allItemSoldbyItem[j][2], Site_ItemSold_Month_ly)) or [("\"\"","\"\"","\"\"")]
            ItemSold_YTD_ly = list(filter(lambda row: row[3] == allItemSoldbyItem[j][2], Site_ItemSold_YTD_ly)) or [("\"\"","\"\"","\"\"")]
            ItemSold_12Months_ly = list(filter(lambda row: row[3] == allItemSoldbyItem[j][2], Site_ItemSold_12Months_ly)) or [("\"\"","\"\"","\"\"")]

            ItemEnglishName = list(filter(lambda row: row[0] == allItemSoldbyItem[j][2], ItemName)) or [("\"\"","\"\"","\"\"")]

            worksheet.write(2,j+8,allItemSoldbyItem[j][2],Title_Item_format)
            worksheet.write_comment(2,j+8,ItemEnglishName[0][1])
            worksheet.write(2,j+8+len(allItemSoldbyItem),allItemSoldbyItem[j][2],Title_Item_percent_format)
            worksheet.write_comment(2,j+8+len(allItemSoldbyItem),ItemEnglishName[0][1])
            
            worksheet.write_formula(i+3,j+8,"""=IF($A$2="Quantity",IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,""))),IF($A$2="Revenue ($)",IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,""))),""))"""%(ItemSold_Month[0][0],ItemSold_YTD[0][0],ItemSold_12Months[0][0],ItemSold_Month[0][1],ItemSold_YTD[0][1],ItemSold_12Months[0][1]),Number_format)
            worksheet.write_formula(i+3,j+8+len(allItemSoldbyItem),"""=IFERROR(IF($A$2="Quantity",IF($A$1="Current Month",%s/%s-1,IF($A$1="YTD",%s/%s-1,IF($A$1="Last 12 Months",%s/%s-1,""))),IF($A$2="Revenue ($)",IF($A$1="Current Month",%s/%s-1,IF($A$1="YTD",%s/%s-1,IF($A$1="Last 12 Months",%s/%s-1,""))),"")),"")"""%(ItemSold_Month[0][0],ItemSold_Month_ly[0][0],ItemSold_YTD[0][0],ItemSold_YTD_ly[0][0],ItemSold_12Months[0][0],ItemSold_12Months_ly[0][0],ItemSold_Month[0][1],ItemSold_Month_ly[0][1],ItemSold_YTD[0][1],ItemSold_YTD_ly[0][1],ItemSold_12Months[0][1],ItemSold_12Months_ly[0][1]),Percentage_format)
            

            worksheet.write_formula(0,j+8,"=SUBTOTAL(1,%s4:%s%s)"%(xl_col_to_name(j+8),xl_col_to_name(j+8),len(allSiteInfo)+4),Number_bold_format)
            worksheet.write_formula(1,j+8,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(j+8),xl_col_to_name(j+8),len(allSiteInfo)+4),Number_bold_format)

    worksheet.set_column("%s:%s"%(xl_col_to_name(12),xl_col_to_name(len(allItemSoldbyItem)+7)),None,None,{'level':1,'hidden':True})
    worksheet.set_column("%s:%s"%(xl_col_to_name(len(allItemSoldbyItem)+7+5),xl_col_to_name(2*len(allItemSoldbyItem)+5+4)),None,None,{'level':1,'hidden':True})

    worksheet.conditional_format('I4:%s%s'%(xl_col_to_name(2*len(allItemSoldbyItem)+7),(len(allSiteInfo)+3)),{"type" : "formula", "criteria" : "I4=\"\"", "format" : bg_grey_format})

    worksheet.autofilter(2,0,2*len(allItemSoldbyItem)+7,(len(allSiteInfo)+3))

def KPIConsumable(workbook,exchange_rate,Current_date):
    con=db.pool.connect()
    worksheet = workbook.add_worksheet("Recap")

    Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
    Number_format = workbook.add_format({'num_format':'# ### ##0'})
    Number_bold_format = workbook.add_format({'num_format':'# ### ##0','bold':True})
    Title_Sales_format = workbook.add_format({'bg_color':'#0070C0','font_color':'white','bold':True})
    Title_Name_format = workbook.add_format({'bg_color':'#0070C0','font_color':'white','bold':True,'center_across':True,'font_size':20})
    Title_Item_format = workbook.add_format({'bg_color':'#F4B084','bold':True})

    worksheet.data_validation('A1',{'validate' : 'list',
                                    'source' : ['Current Month', 'Last 12 Months','YTD']})
    worksheet.write('A1', 'YTD',Select_format)
    worksheet.data_validation('B1',{'validate' : 'list',
                                    'source' : ['Operation', 'Project','Total']})
    worksheet.write('B1', 'Total',Select_format)

    worksheet.set_column('B:B',45)
    worksheet.set_column('C:C',22)
    worksheet.freeze_panes(4,3)


    Date_N_1 = Current_date - relativedelta(months=+12)
    Date_janv = date(Current_date.year-1,12,1)
    Date_janv_N_1 = date(Date_N_1.year-1,12,1)
    Date_N_2 = Date_N_1 - relativedelta(months=+12)

    allItemSold_Month = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Item,
                                    IFNULL(Old_Platform,"Project"), Payment_method FROM Consumable JOIN Sites ON 
                                    Sites.Id_Site = Consumable.Id_Site 
                                    WHERE Month = %s AND Validate = 1
                                    GROUP BY Item,Old_Platform,Payment_method""",exchange_rate,Current_date).fetchall()
    allItemSold_Month_ly = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Item,
                                       IFNULL(Old_Platform,"Project"),Payment_method FROM Consumable JOIN Sites ON 
                                       Sites.Id_Site = Consumable.Id_Site 
                                       WHERE Month = %s AND Validate = 1
                                       GROUP BY Item,Old_Platform,Payment_method""",exchange_rate,Date_N_1).fetchall()

    allItemSold_YTD = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Item,IFNULL(Old_Platform,"Project"),Payment_method 
                                  FROM Consumable JOIN Sites ON Sites.Id_Site = Consumable.Id_Site 
                                  WHERE Month <= %s AND Month > %s AND Validate = 1
                                  GROUP BY Item,Old_Platform,Payment_method""",exchange_rate,Current_date,Date_janv).fetchall()
    allItemSold_YTD_ly = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Item,IFNULL(Old_Platform,"Project"),Payment_method 
                                    FROM Consumable JOIN Sites ON Sites.Id_Site = Consumable.Id_Site 
                                    WHERE Month <= %s AND Month > %s AND Validate = 1
                                    GROUP BY Item,Old_Platform,Payment_method""",exchange_rate,Date_N_1,Date_janv_N_1).fetchall()

    allItemSold_12months = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Item,IFNULL(Old_Platform,"Project"),Payment_method 
                                       FROM Consumable JOIN Sites ON Sites.Id_Site = Consumable.Id_Site 
                                       WHERE Month <= %s AND Month > %s AND Validate = 1
                                       GROUP BY Item,Old_Platform,Payment_method""",exchange_rate,Current_date,Date_N_1).fetchall()
    allItemSold_12months_ly = con.execute("""SELECT SUM(Number_Item),SUM(Price_Item)/%s,Item,IFNULL(Old_Platform,"Project"),Payment_method 
                                          FROM Consumable JOIN Sites ON Sites.Id_Site = Consumable.Id_Site 
                                          WHERE Month <= %s AND Month > %s AND Validate = 1 
                                          GROUP BY Item,Old_Platform,Payment_method""",exchange_rate,Date_N_1,Date_N_2).fetchall()

    ListItem = con.execute("SELECT Distinct Item FROM Consumable ORDER BY Item").fetchall()
    ListItemName = con.execute("SELECT Distinct Item,English_name FROM Consumable ORDER BY Item").fetchall()

    ListPlatform = con.execute("SELECT DISTINCT Code_Platform FROM Platform").fetchall()

    worksheet.autofilter(3,0,len(ListPlatform)+4,3+len(ListPlatform)+len(ListPlatform)+2+3*len(ListPlatform))

    worksheet.set_column('%s:%s'%(xl_col_to_name(3+len(ListPlatform)+2),xl_col_to_name(3+2*len(ListPlatform)+1)),None,None,{'level':1,'hidden':True})
    worksheet.set_column('%s:%s'%(xl_col_to_name(2+len(ListPlatform)+2+3*len(ListPlatform)),xl_col_to_name(1+len(ListPlatform)+2+4*len(ListPlatform))),None,None,{'level':1,'hidden':True})

    worksheet.write_formula(1,3+len(ListPlatform),"=IF($A$1=\"Current Month\",\"%s - %s\",IF($A$1=\"YTD\",%s,IF($A$1=\"Last 12 Months\",\"%s-%s to %s-%s\",\"\")))"%(Current_date.month,Current_date.year,Current_date.year,Current_date.month,Current_date.year,(Current_date-relativedelta(months=+11)).month,(Current_date-relativedelta(months=+11)).year),Title_Sales_format)
    worksheet.write_formula(1,3+len(ListPlatform)+len(ListPlatform)+2,"=IF($A$1=\"Current Month\",\"%s - %s\",IF($A$1=\"YTD\",%s,IF($A$1=\"Last 12 Months\",\"%s-%s to %s-%s\",\"\")))"%(Date_N_1.month,Date_N_1.year,Date_N_1.year,Date_N_1.month,Date_N_1.year,(Date_N_1-relativedelta(months=+11)).month,(Date_N_1-relativedelta(months=+11)).year),Title_Sales_format)
    worksheet.write_formula(1,2+len(ListPlatform)+3*len(ListPlatform),"=IF($A$1=\"Current Month\",\"%s - %s\",IF($A$1=\"YTD\",%s,IF($A$1=\"Last 12 Months\",\"%s-%s to %s-%s\",\"\")))"%(Current_date.month,Current_date.year,Current_date.year,Current_date.month,Current_date.year,(Current_date-relativedelta(months=+11)).month,(Current_date-relativedelta(months=+11)).year),Title_Sales_format)
    worksheet.write_formula(1,2+len(ListPlatform)+len(ListPlatform)+2+3*len(ListPlatform),"=IF($A$1=\"Current Month\",\"%s - %s\",IF($A$1=\"YTD\",%s,IF($A$1=\"Last 12 Months\",\"%s-%s to %s-%s\",\"\")))"%(Date_N_1.month,Date_N_1.year,Date_N_1.year,Date_N_1.month,Date_N_1.year,(Date_N_1-relativedelta(months=+11)).month,(Date_N_1-relativedelta(months=+11)).year),Title_Sales_format)

    worksheet.write(3,0,"Item",Number_bold_format)
    worksheet.write(3,1,"Name",Number_bold_format)
    worksheet.write(3,2,"Type",Number_bold_format)
    for k in range(len(ListItem)):
        worksheet.write(k+4,0,ListItem[k][0])

        ItemName = list(filter(lambda row: row[0] == ListItem[k][0], ListItemName)) or ["",""]

        worksheet.write(k+4,1,ItemName[0][1])
        if ListItem[k][0] in ['401001','401002']:
            worksheet.write(k+4,2,"Bottle")
        
        elif CheckTechnicalItem(ListItem[k][0]):
            worksheet.write(k+4,2,"Technical intervention")
        else:
            worksheet.write(k+4,2,"Consumable")

        worksheet.write(3,3+len(ListPlatform),"Total",Title_Sales_format)
        worksheet.write(3,3+len(ListPlatform)+len(ListPlatform)+2,"Total",Title_Sales_format)
        worksheet.write(3,2+len(ListPlatform)+3*len(ListPlatform),"Total",Title_Sales_format)
        worksheet.write(3,2+len(ListPlatform)+len(ListPlatform)+2+3*len(ListPlatform),"Total",Title_Sales_format)

        ItemSoldPlatform_month = list(filter(lambda row: row[2] == ListItem[k][0], allItemSold_Month))
        ItemSoldPlatform_month_ly = list(filter(lambda row: row[2] == ListItem[k][0], allItemSold_Month_ly))
        ItemSoldPlatform_YTD = list(filter(lambda row: row[2] == ListItem[k][0], allItemSold_YTD))
        ItemSoldPlatform_YTD_ly = list(filter(lambda row: row[2] == ListItem[k][0], allItemSold_YTD_ly))
        ItemSoldPlatform_12months = list(filter(lambda row: row[2] == ListItem[k][0], allItemSold_12months))
        ItemSoldPlatform_12months_ly = list(filter(lambda row: row[2] == ListItem[k][0], allItemSold_12months_ly))

        for i in range(len(ListPlatform)):
            worksheet.write(3,3+i,ListPlatform[i][0],Title_Sales_format)
            worksheet.write(3,3+i+len(ListPlatform)+2,ListPlatform[i][0],Title_Sales_format)
            worksheet.write(3,2+i+3*len(ListPlatform),ListPlatform[i][0],Title_Sales_format)
            worksheet.write(3,2+i+len(ListPlatform)+2+3*len(ListPlatform),ListPlatform[i][0],Title_Sales_format)

            ItemSold_month = list(filter(lambda row: row[3] == ListPlatform[i][0], ItemSoldPlatform_month)) or [(0,0,"\"\"","\"\"","\"\"")]
            ItemSold_month_project = list(filter(lambda row: row[4] == 'Project', ItemSold_month)) or [(0,0,"\"\"")]
            AmountItemSold_month_project = [ItemSold_month_project[0][0],ItemSold_month_project[0][1]]
            ItemSold_month_operation = list(filter(lambda row: row[4] != 'Project', ItemSold_month)) or [(0,0,"\"\"")]
            AmountItemSold_month_operation = [sum(i[0] for i in ItemSold_month_operation),sum(i[1] for i in ItemSold_month_operation)]
            
            ItemSold_month_ly = list(filter(lambda row: row[3] == ListPlatform[i][0], ItemSoldPlatform_month_ly)) or [(0,0,"\"\"","\"\"","\"\"")]
            ItemSold_month_ly_project = list(filter(lambda row: row[4] == 'Project', ItemSold_month_ly)) or [(0,0,"\"\"")]
            AmountItemSold_month_ly_project = [ItemSold_month_ly_project[0][0],ItemSold_month_ly_project[0][1]]
            ItemSold_month_ly_operation = list(filter(lambda row: row[4] != 'Project', ItemSold_month_ly)) or [(0,0,"\"\"")]
            AmountItemSold_month_ly_operation = [sum(i[0] for i in ItemSold_month_ly_operation),sum(i[1] for i in ItemSold_month_ly_operation)]
            
            ItemSold_YTD = list(filter(lambda row: row[3] == ListPlatform[i][0], ItemSoldPlatform_YTD)) or [(0,0,"\"\"","\"\"","\"\"")]
            ItemSold_YTD_project = list(filter(lambda row: row[4] == 'Project', ItemSold_YTD)) or [(0,0,"\"\"")]
            AmountItemSold_YTD_project = [ItemSold_YTD_project[0][0],ItemSold_YTD_project[0][1]]
            ItemSold_YTD_operation = list(filter(lambda row: row[4] != 'Project', ItemSold_YTD)) or [(0,0,"\"\"")]
            AmountItemSold_YTD_operation = [sum(i[0] for i in ItemSold_YTD_operation),sum(i[1] for i in ItemSold_YTD_operation)]

            ItemSold_YTD_ly = list(filter(lambda row: row[3] == ListPlatform[i][0], ItemSoldPlatform_YTD_ly)) or [(0,0,"\"\"","\"\"","\"\"")]
            ItemSold_YTD_ly_project = list(filter(lambda row: row[4] == 'Project', ItemSold_YTD_ly)) or [(0,0,"\"\"")]
            AmountItemSold_YTD_ly_project = [ItemSold_YTD_ly_project[0][0],ItemSold_YTD_ly_project[0][1]]
            ItemSold_YTD_ly_operation = list(filter(lambda row: row[4] != 'Project', ItemSold_YTD_ly)) or [(0,0,"\"\"")]
            AmountItemSold_YTD_ly_operation = [sum(i[0] for i in ItemSold_YTD_ly_operation),sum(i[1] for i in ItemSold_YTD_ly_operation)]

            ItemSold_12months = list(filter(lambda row: row[3] == ListPlatform[i][0], ItemSoldPlatform_12months)) or [(0,0,"\"\"","\"\"","\"\"")]
            ItemSold_12months_project = list(filter(lambda row: row[4] == 'Project', ItemSold_12months)) or [(0,0,"\"\"")]
            AmountItemSold_12months_project = [ItemSold_12months_project[0][0],ItemSold_12months_project[0][1]]
            ItemSold_12months_operation = list(filter(lambda row: row[4] != 'Project', ItemSold_12months)) or [(0,0,"\"\"")]
            AmountItemSold_12months_operation = [sum(i[0] for i in ItemSold_12months_operation),sum(i[1] for i in ItemSold_12months_operation)]
            
            ItemSold_12months_ly = list(filter(lambda row: row[3] == ListPlatform[i][0], ItemSoldPlatform_12months_ly)) or [(0,0,"\"\"","\"\"","\"\"")]
            ItemSold_12months_ly_project = list(filter(lambda row: row[4] == 'Project', ItemSold_12months_ly)) or [(0,0,"\"\"")]
            AmountItemSold_12months_ly_project = [ItemSold_12months_ly_project[0][0],ItemSold_12months_ly_project[0][1]]
            ItemSold_12months_ly_operation = list(filter(lambda row: row[4] != 'Project', ItemSold_12months_ly)) or [(0,0,"\"\"")]
            AmountItemSold_12months_ly_operation = [sum(i[0] for i in ItemSold_12months_ly_operation),sum(i[1] for i in ItemSold_12months_ly_operation)]
            
            worksheet.write_formula(k+4,3+i,"""=IF($B$1="Operation",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Project",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Total",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))))))"""
                                    %(AmountItemSold_month_operation[0],AmountItemSold_YTD_operation[0],AmountItemSold_12months_project[0],
                                      AmountItemSold_month_project[0],AmountItemSold_YTD_project[0],AmountItemSold_12months_project[0],
                                      AmountItemSold_month_project[0]+AmountItemSold_month_operation[0],AmountItemSold_YTD_project[0]+AmountItemSold_YTD_operation[0],AmountItemSold_12months_project[0]+AmountItemSold_12months_operation[0]),Number_format)
            
            worksheet.write_formula(k+4,3+i+len(ListPlatform)+2,"""=IF($B$1="Operation",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Project",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Total",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))))))"""
                                    %(AmountItemSold_month_ly_operation[0],AmountItemSold_YTD_ly_operation[0],AmountItemSold_12months_ly_project[0],
                                      AmountItemSold_month_ly_project[0],AmountItemSold_YTD_ly_project[0],AmountItemSold_12months_ly_project[0],
                                      AmountItemSold_month_ly_project[0]+AmountItemSold_month_ly_operation[0],AmountItemSold_YTD_ly_project[0]+AmountItemSold_YTD_ly_operation[0],AmountItemSold_12months_ly_project[0]+AmountItemSold_12months_ly_operation[0]),Number_format)
            
            worksheet.write_formula(k+4,2+i+3*len(ListPlatform),"""=IF($B$1="Operation",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Project",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Total",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))))))"""
                                    %(AmountItemSold_month_operation[1],AmountItemSold_YTD_operation[1],AmountItemSold_12months_project[1],
                                      AmountItemSold_month_project[1],AmountItemSold_YTD_project[1],AmountItemSold_12months_project[1],
                                      AmountItemSold_month_project[1]+AmountItemSold_month_operation[1],AmountItemSold_YTD_project[1]+AmountItemSold_YTD_operation[1],AmountItemSold_12months_project[1]+AmountItemSold_12months_operation[1]),Number_format)
            
            worksheet.write_formula(k+4,2+i+len(ListPlatform)+2+3*len(ListPlatform),"""=IF($B$1="Operation",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Project",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))),
                                                IF($B$1="Total",(IF($A$1="Current Month",%s,IF($A$1="YTD",%s,IF($A$1="Last 12 Months",%s,"")))))))"""
                                    %(AmountItemSold_month_ly_operation[1],AmountItemSold_YTD_ly_operation[1],AmountItemSold_12months_ly_project[1],
                                      AmountItemSold_month_ly_project[1],AmountItemSold_YTD_ly_project[1],AmountItemSold_12months_ly_project[1],
                                      AmountItemSold_month_ly_project[1]+AmountItemSold_month_ly_operation[1],AmountItemSold_YTD_ly_project[1]+AmountItemSold_YTD_ly_operation[1],AmountItemSold_12months_ly_project[1]+AmountItemSold_12months_ly_operation[1]),Number_format)
        
            worksheet.write_formula(2,3+i,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(3+i),xl_col_to_name(3+i),len(ListItem)+4),Number_bold_format)
            worksheet.write_formula(2,3+i+len(ListPlatform)+2,"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(3+i+len(ListPlatform)+2),xl_col_to_name(3+i+len(ListPlatform)+2),len(ListItem)+4),Number_bold_format)
            worksheet.write_formula(2,2+i+3*len(ListPlatform),"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(2+i+3*len(ListPlatform)),xl_col_to_name(2+i+3*len(ListPlatform)),len(ListItem)+4),Number_bold_format)
            worksheet.write_formula(2,2+i+len(ListPlatform)+2+3*len(ListPlatform),"=SUBTOTAL(9,%s4:%s%s)"%(xl_col_to_name(2+i+len(ListPlatform)+2+3*len(ListPlatform)),xl_col_to_name(2+i+len(ListPlatform)+2+3*len(ListPlatform)),len(ListItem)+4),Number_bold_format)

        worksheet.write_formula(k+4,3+len(ListPlatform),'=SUM(%s:%s)'%(xl_rowcol_to_cell(k+4,3),xl_rowcol_to_cell(k+4,2+len(ListPlatform))),Number_bold_format)
        worksheet.write_formula(k+4,3+len(ListPlatform)+len(ListPlatform)+2,'=SUM(%s:%s)'%(xl_rowcol_to_cell(k+4,3+len(ListPlatform)+2),xl_rowcol_to_cell(k+4,3+len(ListPlatform)+len(ListPlatform)+1)),Number_bold_format)
        worksheet.write_formula(k+4,2+len(ListPlatform)+3*len(ListPlatform),'=SUM(%s:%s)'%(xl_rowcol_to_cell(k+4,2+3*len(ListPlatform)),xl_rowcol_to_cell(k+4,2+len(ListPlatform)+3*len(ListPlatform)-1)),Number_bold_format)
        worksheet.write_formula(k+4,2+len(ListPlatform)+len(ListPlatform)+2+3*len(ListPlatform),'=SUM(%s:%s)'%(xl_rowcol_to_cell(k+4,2+len(ListPlatform)+2+3*len(ListPlatform)),xl_rowcol_to_cell(k+4,2+len(ListPlatform)+len(ListPlatform)+1+3*len(ListPlatform))),Number_bold_format)

    worksheet.write_formula(2,3+len(ListPlatform),'=SUM(%s:%s)'%(xl_rowcol_to_cell(2,3),xl_rowcol_to_cell(2,2+len(ListPlatform))),Number_bold_format)
    worksheet.write_formula(2,3+len(ListPlatform)+len(ListPlatform)+2,'=SUM(%s:%s)'%(xl_rowcol_to_cell(2,3+len(ListPlatform)+2),xl_rowcol_to_cell(2,3+len(ListPlatform)+len(ListPlatform)+1)),Number_bold_format)
    worksheet.write_formula(2,2+len(ListPlatform)+3*len(ListPlatform),'=SUM(%s:%s)'%(xl_rowcol_to_cell(2,2+3*len(ListPlatform)),xl_rowcol_to_cell(2,2+len(ListPlatform)+3*len(ListPlatform)-1)),Number_bold_format)
    worksheet.write_formula(2,2+len(ListPlatform)+len(ListPlatform)+2+3*len(ListPlatform),'=SUM(%s:%s)'%(xl_rowcol_to_cell(2,2+len(ListPlatform)+2+3*len(ListPlatform)),xl_rowcol_to_cell(2,2+len(ListPlatform)+len(ListPlatform)+1+3*len(ListPlatform))),Number_bold_format)

    worksheet.merge_range(0,3,0,3+len(ListPlatform)+len(ListPlatform)+2,"Quantity",Title_Name_format)
    worksheet.merge_range(0,2+len(ListPlatform)+len(ListPlatform)+5,0,2+len(ListPlatform)+len(ListPlatform)+2+3*len(ListPlatform),"Revenue ($)",Title_Name_format)

def LaunchExcelCreationOrder(exchange_rate,Current_date,First_date = 0):
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)

    if First_date == 0:
        filepath = tempfile.gettempdir()+'/Order '+Year+'-'+Month+'.xlsx'
        if os.path.exists(filepath):
            os.remove(filepath)
        workbook = xlsxwriter.Workbook(filepath)
        ExcelOrder(exchange_rate,Current_date,workbook)
    else:
        FirstMonth = First_date.month
        if FirstMonth < 10:
            FirstMonth = '0' + str(FirstMonth)
        else:
            FirstMonth = str(FirstMonth)
        FirstYear = str(First_date.year)
        filepath = tempfile.gettempdir()+'/Order '+FirstYear + '-' + FirstMonth + ' to ' +Year+'-'+Month+'.xlsx'
        if os.path.exists(filepath):
            os.remove(filepath)
        workbook = xlsxwriter.Workbook(filepath)
        ExcelOrder(exchange_rate,Current_date,workbook,First_date) 

def LaunchExcelCreationConsumableFollowup(exchange_rate,Current_date):
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)

    filepath = tempfile.gettempdir()+'/Consumable Follow Up '+Year+'-'+Month+'.xlsx'
    if os.path.exists(filepath):
       os.remove(filepath)
    workbook = xlsxwriter.Workbook(filepath)
    DataConsumableSold(workbook,exchange_rate,Current_date)
    KPIConsumable(workbook,exchange_rate,Current_date)
    workbook.close()

if __name__ == '__main__':
    global Current_date
    Current_date = date(2021,11,1)
