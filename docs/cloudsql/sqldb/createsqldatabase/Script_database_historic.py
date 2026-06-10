import os #used for importing datastore
import json
import datetime
from datetime import timedelta, date
from Script_Get_Data import get_data_withdrawal,get_data_wins_invoice, get_data_bottle_invoice,get_data_partially_paid,get_data_consumable, get_data_debt,get_data_flash_report,get_data_open_days, get_tier, get_data_stock_ts, get_data_sale, get_data_beneficiaries, listsite, get_data_expenses, get_data_ts_expenses, get_data_site, get_data_indicators, get_data_daily_sales, get_data_technical_intervention_item, get_data_water_alert, get_data_vehicles,get_data_technical_intervention,get_data_quality_app
from create_all_tables import create_database_struct
from google.cloud import datastore
from calendar import monthrange
import db
from sqlalchemy import text
from Functionutils import listDate, listSite
import flask

con = db.pool.connect()

datastore_client = datastore.Client.from_service_account_json('certs/client_secret_appengine.json')

def WriteTableSalesAndBeneficiariesAndDailySales():
    #COMPLETE TABLES SALES BENEFICIARIES AND DAILYSALES WITH THE DATA FROM THE DATASTORE

    ListSite = listsite()
    #del ListSite[ListSite.index('P3')]
    print("sales")
    for sitename in ListSite:
        print(sitename)
        query_pivot = datastore_client.query(kind="Pivot")
        query_pivot.add_filter("site","=",sitename)
        query_pivot.add_filter("form","=","1. Register Sales")
        query_pivot.order = ["-integration_date"]
        Query_registered_sales = list(query_pivot.fetch())
        for i in range(len(Query_registered_sales)):
            data_dict = json.loads(Query_registered_sales[i]["data"])
            data_sales = get_data_sale(data_dict)
            data_beneficiaries = get_data_beneficiaries(data_dict)
            Number_days = data_dict["form"]["days-in-month"]
            Querytest = con.execute("SELECT Code_Sales FROM Sales WHERE Month = %s AND Id_Site = %s", (data_sales[1], data_sales[0]))
            Test = Querytest.fetchall()
            if not Test: #we ordered by decreasing order so the request already in database is the latest request.
                print("here")
                query = ("INSERT INTO Sales (Id_Site, Month, Total_Sales, Total_Income, Total_Price_Average,"
                        "Hod_Sales, Hod_Income,Hod_Price, Shopkeeper_Sales, Shopkeeper_Income,"
                        "Shopkeeper_Price, WiS_Sales, WiS_Income, WiS_Price, Onsite_Sales,"
                        "Onsite_Income, Onsite_Price, Free_Sales, Bottle_Sales, Bottle_Income, Bottle_Price, Other_Sales, Other_Income, Other_Price, Number_Open_Days)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s)")
                con.execute(query, data_sales)
                query = ("INSERT INTO Beneficiaries (Id_Site, Month, Beneficiaries)"
                        "VALUES (%s, %s, %s)")
                con.execute(query,data_beneficiaries)
            Querytest = con.execute("SELECT Code_Daily FROM DailySales WHERE Month = %s AND Id_Site = %s", (data_sales[1],data_sales[0]))
            Test = Querytest.fetchall()
            if not Test:
                for i in range(1,int(Number_days)+1):
                    data = get_data_daily_sales(data_dict,i)
                    query = ("INSERT INTO DailySales (Id_Site,Month,Day,Total_Sales,Hod_Sales,Shopkeeper_Sales,WiS_Sales,Onsite_Sales,Free_Sales,Bottle_Sales,Other_Sales)"
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                    con.execute(query,data)

def WriteTableExpenses():
    #COMPLETE EXPENSES WITH THE DATA FROM THE DATASTORE
    ListSite = listsite()
    print("tableexpenses")
    for sitename in ListSite:
        print(sitename)
        query_settlesinvoice = datastore_client.query(kind="Pivot")
        query_settlesinvoice.add_filter("site","=",sitename)
        query_settlesinvoice.add_filter("form","=","2. Settle Invoices")
        query_settlesinvoice.order = ["-integration_date"]
        Query_settles_invoices = list(query_settlesinvoice.fetch())
        for i in range(len(Query_settles_invoices)):
            Data_dict = json.loads(Query_settles_invoices[i]["data"])
            data = get_data_ts_expenses(Data_dict)
            Querytest = con.execute("SELECT Amount_expenses FROM Expenses WHERE Month = %s AND Id_Site = %s AND Ref_expenses = 'entrepreneur_contribution'", (data[1], data[0]))
            Test = Querytest.fetchall()
            if not Test and data != 'no date': #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                            "VALUES (%s, %s, %s, %s)")
                con.execute(query,data)
            data_stock = get_data_stock_ts(Data_dict)
            Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month = %s AND Id_Site = %s AND Ref_expenses = 'stock_ts'", (data_stock[1], data_stock[0]))
            Test = Querytest.fetchall()
            if not Test and data_stock != 'no date': #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                            "VALUES (%s, %s, %s, %s)")
                con.execute(query,data_stock)

            data_technical_intervention = get_data_technical_intervention_item(Data_dict)
            Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month = %s AND Id_Site = %s AND Ref_expenses = 'technical intervention'", (data_technical_intervention[1], data_technical_intervention[0]))
            Test = Querytest.fetchall()
            if not Test and data_technical_intervention != 'no date': #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                            "VALUES (%s, %s, %s, %s)")
                con.execute(query,data_technical_intervention)

            data_water_alert = get_data_water_alert(Data_dict)
            Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month = %s AND Id_Site = %s AND Ref_expenses = 'water quality alert'", (data_water_alert[1], data_water_alert[0]))
            Test = Querytest.fetchall()
            if not Test and data_water_alert != 'no date': #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                            "VALUES (%s, %s, %s, %s)")
                con.execute(query,data_water_alert)

        query_expenses = datastore_client.query(kind="Pivot")
        query_expenses.add_filter("site","=",sitename)
        query_expenses.add_filter("form","=","3. Register Expenses")
        query_expenses.order = ["-integration_date"]
        Query_registered_expenses = list(query_expenses.fetch())
        for j in range(len(Query_registered_expenses)):
            Salary = ["a1-variable_salary","a2-fixed_salary","a3-bonus","s1-Variable-salary-chief-OP","s2-Fixed-salary-chief-OP","s3-bonus"]
            Other_cost = ["c6-soap","c7-carbon","c8-consumables","d1-gasoline","d2-moto-repair","d3-oil-moto",
                            "o1-association_de_gestion","o10-furnitures","o11-others","o3-electricity","o4-site-equipment","o5-transportation-fee","o6-communication",
                            "o7-caps","o8-spray","o9-brush","w1-gasoline-for-waterpump","w2-raw-water","w3-koyen-fee","w4-charge-battery","stock_ts","unknown_code","bottle_invoice"]
            Salary_amount = 0
            Other_cost_amount = 0
            Data_dict = json.loads(Query_registered_expenses[j]["data"])
            Site = Data_dict["form"]["site_name"]
            Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
            Querytest = con.execute("SELECT Code_Expenses,Ref_expenses FROM Expenses WHERE Month = %s AND Id_Site = %s AND Ref_expenses <> 'entrepreneur_contribution' AND Ref_expenses <> 'stock_ts' AND Ref_expenses <> 'technical intervention' AND Ref_expenses <> 'water quality alert'", (Date, Site))
            Test = Querytest.fetchall()
            if not Test:
                for j in range(len(Data_dict["form"]["site_confirmed"]["display_expense"]["loop"])):
                    data = get_data_expenses(Data_dict,j)
                    if data[2] and data[3]:
                            query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                            "VALUES (%s, %s, %s, %s)")
                            con.execute(query,data)
                    if data[2] in Salary:
                        Salary_amount += int(data[3])
                    elif data[2] in Other_cost:
                        Other_cost_amount += int(data[3])
                query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                        "VALUES (%s, %s, %s, %s)")
                L = [data[0], data[1], 'total-salary', Salary_amount]
                con.execute(query,L)
                query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                        "VALUES (%s, %s, %s, %s)")
                L = [data[0], data[1], 'total-other-cost', Other_cost_amount]
                con.execute(query,L)


def WriteTableSite():
    ListSite = listsite()
    for sitename in ListSite:
        data = get_data_site(sitename)
        query = ("INSERT INTO Sites (Id_Site, Platform, Province, Wave, Longi, Lati)"
                "VALUES (%s, %s, %s, %s, %s, %s)")
        con.execute(query,data)


def WriteTableIndicators():
    ListSite = listsite()
    print("indicators")
    for sitename in ListSite:
        print(sitename)
        query_indicators = datastore_client.query(kind="Pivot")
        query_indicators.add_filter("site","=",sitename)
        query_indicators.add_filter("form","=","5. Production Report")
        query_indicators.order = ["-integration_date"]
        Query_production_report = list(query_indicators.fetch())
        for i in range(len(Query_production_report)):
            data_dict = json.loads(Query_production_report[i]["data"])
            try:
                data = get_data_indicators(data_dict)
                Querytest = con.execute("SELECT Code_Indicator FROM Indicators WHERE Month = %s AND Id_Site = %s", (data[1], data[0]))
                Test = Querytest.fetchall()
                if not Test:
                    query = ("INSERT INTO Indicators (Id_Site, Month, Number_of_Operator, Number_Bottles_in_Operation, Number_Bottles_in_Stock, Number_Bottles_Broken_Lost, Water_Consume)"
                            "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                    con.execute(query,data)
            except:
                print("error")
                print(sitename)

    for sitename in ListSite:
        print(sitename)
        query_indicators = datastore_client.query(kind="Pivot")
        query_indicators.add_filter("site","=",sitename)
        query_indicators.add_filter("form","=","6. Site Checklist")
        query_indicators.order = ["-integration_date"]
        Query_vehicule = list(query_indicators.fetch())
        for i in range(len(Query_vehicule)):
            data_dict = json.loads(Query_vehicule[i]["data"])
            data = get_data_vehicles(data_dict)
            if data != "no date":
                Querytest= con.execute("SELECT Number_of_Operator FROM Indicators WHERE Month = %s AND Id_Site = %s", (data[1], data[0]))
                Test = Querytest.fetchall()
                Querytest2 = con.execute("SELECT Number_of_Vehicle FROM Indicators WHERE Month = %s AND Id_Site = %s", (data[1], data[0]))
                Test2 = Querytest2.fetchall()
                if not Test:
                    query = ("INSERT INTO Indicators (Id_Site, Month, Number_of_Vehicle)"
                            "VALUES (%s, %s, %s)")
                    con.execute(query,data)
                elif not Test2[0][0]:
                    con.execute("UPDATE Indicators SET Number_of_Vehicle = %s WHERE Month = %s AND Id_Site = %s", (data[2],data[1], data[0]) )
            else:
                print(data)

def WriteTableFlashReport():
    ListSite = listsite()
    for sitename in ListSite:
        print(sitename)
        query_flash = datastore_client.query(kind="Pivot")
        query_flash.add_filter("site","=",sitename)
        query_flash.add_filter("form","=","11. Flash Report")
        query_flash.order = ["-integration_date"]
        Query_flash_report = list(query_flash.fetch())
        for i in range(len(Query_flash_report)):
            data_dict = json.loads(Query_flash_report[i]["data"])
            data = get_data_flash_report(data_dict)
            Querytest = con.execute("SELECT Code_Flash_report FROM FlashReport WHERE Month = %s AND Id_Site = %s", (data[1], data[0]))
            Test = Querytest.fetchall()
            if not Test:
                query = ("INSERT INTO FlashReport (Id_Site, Month, Number_jugs_village, Number_jugs_school, Open_days, Comment, Number_of_delivery,Number_of_deinfection, Moto_cart, Kuyon, Car,Staff)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                con.execute(query,data)

def ModifyTotalOtherCost():  #CORRECTING Total-other-cost in the Expenses Table
    ListSite = listsite()
    for j in range(len(ListSite)):
        query = con.execute("SELECT DISTINCT Month FROM Expenses WHERE Id_Site = %s", ListSite[j])
        Date = query.fetchall()
        print(ListSite[j])
        for i in range(len(Date)):
            query = con.execute("SELECT Sum(Amount_Expenses) FROM Expenses WHERE Month = %s AND Id_Site = %s AND (Ref_expenses = 'c6-soap' OR Ref_expenses = 'c7-carbon' OR Ref_expenses = 'c8-consumables' OR Ref_expenses = 'd1-gasoline' OR Ref_expenses = 'd2-moto-repair' OR Ref_expenses = 'd3-oil-moto' OR Ref_expenses = 'o1-association_de_gestion' OR Ref_expenses = 'o10-furnitures' OR Ref_expenses = 'o11-others' OR Ref_expenses = 'o3-electricity' OR Ref_expenses = 'o4-site-equipment' OR Ref_expenses = 'o5-transportation-fee' OR Ref_expenses = 'o6-communication' OR Ref_expenses = 'o7-caps' OR Ref_expenses = 'o8-spray' OR Ref_expenses = 'o9-brush' OR Ref_expenses = 'w1-gasoline-for-waterpump' OR Ref_expenses = 'w2-raw-water' OR Ref_expenses = 'w3-koyen-fee' OR Ref_expenses = 'w4-charge-battery' OR Ref_expenses = 'technical intervention' OR Ref_expenses = 'water quality alert' OR Ref_expenses = 'stock_ts' OR Ref_expenses = 'bottle_invoice' OR Ref_expenses = 'unknown_code')", (Date[i][0],ListSite[j]))

            total_other_cost = query.fetchall()
            querytest = con.execute("SELECT Ref_expenses FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'total-other-cost'", (ListSite[j], Date[i][0]))
            test = querytest.fetchall()
            if total_other_cost and total_other_cost[0][0]:
                if test:
                    con.execute("UPDATE Expenses SET Amount_expenses = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'total-other-cost'", (total_other_cost[0][0],ListSite[j], Date[i][0]))
                if not test:
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                            "VALUES (%s, %s, %s, %s)")
                    con.execute(query,[ListSite[j], Date[i][0],"total-other-cost",total_other_cost[0][0]])

def ModifyExpensesAddingUnknownCode():
    ListSite = listsite()
    print("tableexpenses")
    for sitename in ListSite:
        print(sitename)
        query_expenses = datastore_client.query(kind="Pivot")
        query_expenses.add_filter("site","=",sitename)
        query_expenses.add_filter("form","=","3. Register Expenses")
        query_expenses.order = ["-integration_date"]
        Query_registered_expenses = list(query_expenses.fetch())
        for j in range(len(Query_registered_expenses)):
            Salary_amount = 0
            Other_cost_amount = 0
            Data_dict = json.loads(Query_registered_expenses[j]["data"])
            Site = Data_dict["form"]["site_name"]
            Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
            if Data_dict["form"].get("site_confirmed"):
                for j in range(len(Data_dict["form"]["site_confirmed"]["display_expense"]["loop"])):
                    data = get_data_expenses(Data_dict,j)
                    if data[2] == "unknown_code" and data[3] != '':
                        query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                        "VALUES (%s, %s, %s, %s)")
                        con.execute(query,data)
                        total_other_cost = con.execute("SELECT Amount_Expenses FROM Expenses WHERE Month = %s AND Id_Site = %s AND Ref_expenses = 'total-other-cost'",(Date,Site)).fetchall()
                        print(total_other_cost)
                        if total_other_cost and total_other_cost[0][0]:
                            try:
                                print(float(data[3])+float(total_other_cost[0][0]))
                                con.execute("UPDATE Expenses SET Amount_Expenses = %s WHERE Month = %s AND Id_Site = %s AND Ref_expenses = 'total-other-cost'",(float(data[3])+float(total_other_cost[0][0]),Date,Site))
                            except:
                                print(data[3])
def ModifyDebt(): #Not used
    ListSite = listSite()
    # con.execute("ALTER TABLE Sites DROP Debt")
    # con.execute("ALTER TABLE Sites ADD Debt Float(15)")
    for sitename in ListSite:
        print(sitename)
        query_invoice = datastore_client.query(kind="Pivot")
        query_invoice.add_filter("site","=",sitename)
        query_invoice.add_filter("form","=","2. Settle Invoices")
        query_invoice.order = ["-integration_date"]
        Query_debt = list(query_invoice.fetch())
        if len(Query_debt) > 0:
            data_dict = json.loads(Query_debt[0]["data"])
            data = get_data_debt(data_dict)
            con.execute("UPDATE Sites SET Debt = %s WHERE Id_Site = %s", (data[1],sitename))
        else:
            con.execute("UPDATE Sites SET Debt = 0 WHERE Id_Site = %s", (sitename))


def ModifyTier():
    ListSite = listsite()
    ListDate = listDate(date(2021,2,1))
    del ListSite[ListSite.index('P3')]
    print("sales")
    for sitename in ListSite:
        print(sitename)
        for month in ListDate:
            query = con.execute('SELECT Total_Sales FROM Sales WHERE Id_Site = %s AND Month = %s',(sitename,month))
            sales = query.fetchall()
            if sales:
                con.execute("UPDATE Sales SET Tier = %s WHERE Id_Site = %s AND Month = %s",(get_tier(sitename,month,sales[0][0]),sitename,month))
            else:
                con.execute("UPDATE Sales SET Tier = %s WHERE Id_Site = %s AND Month = %s",(get_tier(sitename,month,0),sitename,month)) #Adding Tier in Sales Table (launch after the first 4 )

def ModifyBeneficiaries():
    ListDate = listDate(date(2021,8,1))
    ListSite = listSite()
    for j in range(len(ListDate)):
        actual_date = ListDate[j]
        print(actual_date)
        allBeneficiaries = con.execute("SELECT Max(Beneficiaries),Id_Site FROM Beneficiaries WHERE Month <= %s AND Month > %s GROUP BY Id_Site", (actual_date,date(actual_date.year -1,actual_date.month,actual_date.day))).fetchall()
        for i in range(len(ListSite)):
            #print(ListSite[i])
            Beneficiaries =  list(filter(lambda row: row[1] == ListSite[i][0], allBeneficiaries))
            Test = con.execute("SELECT Code_Beneficiaries FROM Beneficiaries WHERE Month = %s AND Id_Site = %s",(actual_date, ListSite[i][0])).fetchall()
            if Beneficiaries and Beneficiaries[0][0]:
                if Test:
                    con.execute("UPDATE Beneficiaries SET Beneficiaries = %s WHERE Id_Site = %s AND Month = %s", (Beneficiaries[0][0],ListSite[i][0],actual_date))
                else:
                    query = ("INSERT INTO Beneficiaries(Id_Site,Month,Beneficiaries) VALUES (%s,%s,%s)")
                    con.execute(query,(ListSite[i][0],actual_date,Beneficiaries[0][0]))

def WriteConsumable():

    ListSite = ["P30","P4","P5","P6","P7","P8","P9"]
    for sitename in ListSite:
        print(sitename)
        query_settle_consumable = datastore_client.query(kind="Pivot")
        query_settle_consumable.add_filter("site","=",sitename)
        query_settle_consumable.add_filter("form","=","7. Request Form")
        query_settle_consumable.order = ["-integration_date"]
        Query_settle_consumable = list(query_settle_consumable.fetch())
        for i in range(len(Query_settle_consumable)):
            Data_dict = json.loads(Query_settle_consumable[i]["data"])
            if Query_settle_consumable[i].get("isLogisticValidated"):
                Validation_dict = json.loads(Query_settle_consumable[i]["isLogisticValidated"])
            else:
                Validation_dict = None
            try:
                ListItem = list(Data_dict["form"]["price_list"]['@ids'].split())
            except:
                ListItem = []
            for i in range(len(ListItem)):
                data = get_data_consumable(Data_dict,ListItem[i],i)

                if int(data[5]) != 0:
                    if Validation_dict and ListItem[i] in Validation_dict:
                        query = ("INSERT INTO Consumable (Id_Site,Month,Date_submission,Category,Item,Number_item,Price_item,Khmer_name,English_name,Unit,Validate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                        #print(data)
                        con.execute(query,data+[True])
                    else:
                        query = ("INSERT INTO Consumable (Id_Site,Month,Date_submission,Category,Item,Number_item,Price_item,Khmer_name,English_name,Unit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                        #print(data)
                        con.execute(query,data)
            #wait = input("ok")


def ModifyInvoices():
    ListSite = listSite()
    for sitename in ListSite:
        print(sitename[0])
        query_settlesinvoice = datastore_client.query(kind="Pivot")
        query_settlesinvoice.add_filter("site","=",sitename[0])
        query_settlesinvoice.add_filter("form","=","2. Settle Invoices")
        query_settlesinvoice.order = ["-integration_date"]
        Query_settles_invoices = list(query_settlesinvoice.fetch())
        date = 0
        for j in range(len(Query_settles_invoices)):
            Data_dict = json.loads(Query_settles_invoices[j]["data"])
            data = get_data_partially_paid(Data_dict)
            data_wins = get_data_wins_invoice(Data_dict)
            data_bottle = get_data_bottle_invoice(Data_dict)
            if data != "no data" and data and date != data[0][1]:
                query = ("INSERT INTO Expenses(Id_Site,Month,Ref_expenses,Amount_Expenses) VALUES (%s,%s,%s,%s)")
                if data_wins and data_wins[3]:
                    con.execute(query,data_wins)
                if data_bottle and data_bottle[3]:
                    con.execute(query,data_bottle)
                for i in range(len(data)):
                    #print(data,i)
                    test = con.execute("SELECT Amount_expenses,Id_Site,Month,Ref_expenses FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = %s",(data[i][0],data[i][1],data[i][2])).fetchall()
                    if test:
                        con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = %s",(data[i][3],data[i][0],data[i][1],data[i][2]))
                    else:
                        # print(data[i])
                        # print(con.execute("SELECT Amount_expenses,Id_Site,Month,Ref_expenses FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'entrepreneur_contribution'",(data[i][0],data[i][1])).fetchall())
                        # wait=input("go")
                        query = ("INSERT INTO Expenses(Id_Site,Month,Ref_expenses,Paid) VALUES (%s,%s,%s,%s)")
                        con.execute(query,data[i])

                date = data[0][1]

        query_withdraw = datastore_client.query(kind="Pivot")
        query_withdraw.add_filter("site","=",sitename[0])
        query_withdraw.add_filter("form","=","4. Deposit and Withdrawal Form")
        query_withdraw.order = ["-integration_date"]
        Query_withdraw = list(query_withdraw.fetch())
        date = 0
        for k in range(len(Query_withdraw)):
            Data_dict = json.loads(Query_withdraw[k]["data"])
            data = get_data_withdrawal(Data_dict)
            if data != "no date" and data and date != data[0][1]:
                query = ("INSERT INTO Expenses(Id_Site,Month,Ref_expenses,Amount_expenses) VALUES (%s,%s,%s,%s)")
                if data and data[3]:
                    con.execute(query,data)
                date = data[1]

def ModifyIndicators():
    ListSite = listsite()
    print("indicators")
    for sitename in ListSite:
        print(sitename)
        query_indicators = datastore_client.query(kind="Pivot")
        query_indicators.add_filter("site","=",sitename)
        query_indicators.add_filter("form","=","5. Production Report")
        query_indicators.order = ["-integration_date"]
        Query_production_report = list(query_indicators.fetch())
        for i in range(len(Query_production_report)):
            data_dict = json.loads(Query_production_report[i]["data"])
            data = get_data_indicators(data_dict)
            if data != "no date":
                if data:
                    #con.execute("UPDATE Indicators SET Machine_begining =%s, Machine_end = %s, Water_begining = %s, Water_end = %s WHERE Id_Site = %s AND Month = %s",(data[7],data[8],data[9],data[10],data[0],data[1]))
                    con.execute("UPDATE Indicators SET Saving_outside_TS = %s WHERE Id_Site = %s AND Month = %s",(data[11],data[0],data[1]))

def WriteTechnical():
    ListSite = listSite()
    for sitename in ListSite:
        print(sitename[0])
        query_technicalintervention = datastore_client.query(kind="Intervention")
        query_technicalintervention.add_filter("site","=",sitename[0])
        Query_technical_intervention = list(query_technicalintervention.fetch())
        for j in range(len(Query_technical_intervention)):
            #print((Query_technical_intervention[j][0]))
            Data_dict = (Query_technical_intervention[j])
            data_intervention = get_data_technical_intervention(Data_dict)
            query = ("INSERT INTO Technical(Id_Site,Month,Start_date,Stop_date,Technician_Name,Reported_by,Problem_Status,Site_problem_description,Sub_Site_problem_description,Comment,Comment_problem,Status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
            con.execute(query,data_intervention)

def WriteQuality():
    ListSite = listSite()
    for sitename in ListSite:
        print(sitename[0])
        query_quality = datastore_client.query(kind="Sample")
        query_quality.add_filter("site","=",sitename[0])
        Query_quality = list(query_quality.fetch())
        for j in range(len(Query_quality)):
            #print((Query_technical_intervention[j][0]))
            Data_dict = (Query_quality[j])
            data_quality = get_data_quality_app(Data_dict)
            if data_quality != "Stop":
                query = "INSERT INTO Quality(Id_Site,Month,Coliform_bottle,Coliform_Machine,Escherichia_Bottle,Escherichia_Machine,Sample_source) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                con.execute(query,data_quality)

if __name__ == '__main__':
    #WriteTableSite()

    # WriteTableSalesAndBeneficiariesAndDailySales()
    # WriteTableExpenses()
    # WriteTableIndicators()
    # WriteTableFlashReport()
    # ModifyTotalOtherCost()
    # ModifyDebt()
    # ModifyTier()
    # ModifyIndicators()
    # WriteConsumable()
    # ModifyInvoices()
    #ModifyExpensesAddingUnknownCode()
    con.execute("TRUNCATE TABLE Quality")
    WriteQuality()
