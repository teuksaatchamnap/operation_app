import json
import datetime
from datetime import date
from sqldb.Script_Get_Data import get_data_delivery_program,get_data_Entrepreneur_resignation,get_data_withdrawal,get_data_wins_invoice,get_data_bottle_invoice,get_data_partially_paid,get_data_consumable,get_data_flash_report,get_data_debt, get_tier,get_data_beneficiaries, get_data_sale, get_data_expenses, get_data_ts_expenses, get_data_indicators, get_data_daily_sales, get_data_stock_ts, get_data_technical_intervention_item, get_data_water_alert, get_data_vehicles, get_data_weekly_flash_report
import db
from api.api import closeSiteApi

def UpdateBDD(Data_dict):
    con = db.pool.connect()
    if Data_dict and Data_dict.get("form") and Data_dict["form"].get("@name") and Data_dict["form"].get("site_name"):
        if Data_dict["form"]["site_name"][0] == 'X' or Data_dict["form"]["site_name"][0] == 'A':
            print("X and A1 sites not imported")
            return("X and A1 sites not imported")
        Querytest = con.execute("SELECT Id_Site FROM Sites WHERE Id_Site = %s", Data_dict["form"]["site_name"])
        test = Querytest.fetchall()
        if not test:
            query1 = ("INSERT INTO Sites (Id_Site, Advisor) VALUES (%s,%s)")
            con.execute(query1, (Data_dict["form"]["site_name"],Data_dict["form"]["meta"]["username"]))


        if Data_dict["form"]["@name"] == "1. Register Sales": #checking which requests is coming
            data_sales = get_data_sale(Data_dict) #extracting data from this request (return list)
            Number_days = Data_dict["form"]["days-in-month"]
            Querytest = con.execute("SELECT Code_Sales FROM Sales WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_sales[0]) )
            Test = Querytest.fetchall()
            if not Test: #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                query1 = ("INSERT INTO Sales (Id_Site, Month, Total_Sales, Total_Income, Total_Price_Average,"
                        "Hod_Sales, Hod_Income,Hod_Price, Shopkeeper_Sales, Shopkeeper_Income,"
                        "Shopkeeper_Price, WiS_Sales, WiS_Income, WiS_Price, Onsite_Sales,"
                        "Onsite_Income, Onsite_Price, Free_Sales, Bottle_Sales, Bottle_Income, Bottle_Price, Other_Sales, Other_Income, Other_Price, Number_Open_Days)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                con.execute(query1, data_sales)
                
                for i in range(1,int(Number_days)+1):
                    data_dailysales = get_data_daily_sales(Data_dict,i)
                    query = ("INSERT INTO DailySales (Id_Site,Month,Day,Total_Sales,Hod_Sales,Shopkeeper_Sales,WiS_Sales,Onsite_Sales,Free_Sales,Bottle_Sales,Other_Sales)"
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                    con.execute(query,data_dailysales)
                con.execute("UPDATE Sales SET Tier = %s WHERE Id_Site = %s AND Month = %s",(get_tier(data_sales[0],data_sales[1],data_sales[2]),data_sales[0],data_sales[1]))
                
                data_beneficiaries = get_data_beneficiaries(Data_dict)
                query2 = ("INSERT INTO Beneficiaries (Id_Site, Month, Beneficiaries)"
                        "VALUES (%s, %s, %s)")
                con.execute(query2,data_beneficiaries)
            elif Test: #updating the database
                con.execute("DELETE FROM Beneficiaries WHERE Month = %s AND Id_Site = %s", (data_sales[1],data_sales[0]))
                data_sales.append(data_sales[0])
                data_sales.append(data_sales[1])
                con.execute("UPDATE Sales SET Id_Site = %s, Month = %s, Total_Sales = %s, Total_Income= %s, Total_Price_Average= %s,"
                        "Hod_Sales= %s, Hod_Income= %s, Hod_Price= %s, Shopkeeper_Sales= %s, Shopkeeper_Income= %s,"
                        "Shopkeeper_Price= %s, WiS_Sales= %s, WiS_Income= %s, WiS_Price= %s, Onsite_Sales= %s,"
                        "Onsite_Income= %s, Onsite_Price= %s, Free_Sales= %s, Bottle_Sales= %s, Bottle_Income= %s, Bottle_Price= %s, Other_Sales = %s, Other_Income = %s, Other_Price = %s, Number_Open_Days= %s "
                        "WHERE Id_Site = %s AND Month = %s",data_sales)

                data_beneficiaries = get_data_beneficiaries(Data_dict)
                query2 = ("INSERT INTO Beneficiaries (Id_Site, Month, Beneficiaries)"
                        "VALUES (%s, %s, %s)")
                con.execute(query2,data_beneficiaries)
                for i in range(1,int(Number_days)+1):
                    data_dailysales = get_data_daily_sales(Data_dict,i)
                    data_dailysales.append(data_dailysales[0])
                    data_dailysales.append(data_dailysales[2])
                    con.execute ("UPDATE DailySales SET Id_Site = %s,Month= %s,Day= %s,Total_Sales= %s,Hod_Sales= %s,Shopkeeper_Sales= %s,WiS_Sales= %s,Onsite_Sales= %s,Free_Sales= %s,Bottle_Sales= %s,Other_Sales = %s WHERE Id_Site = %s AND Day = %s", data_dailysales)

                con.execute("UPDATE Sales SET Tier = %s WHERE Id_Site = %s AND Month = %s",(get_tier(data_sales[0],data_sales[1],data_sales[2]),data_sales[0],data_sales[1]))
                Project = con.execute("SELECT Project FROM Sites WHERE Id_Site = %s",(data_sales[0])).fetchall()
                con.execute("UPDATE Sales SET Project = %s WHERE Id_Site = %s AND Month = %s",(Project[0][0],data_sales[0],data_sales[1]))

            con.execute("UPDATE Sites SET Advisor = %s WHERE Id_Site = %s", (Data_dict["form"]["meta"]["username"],data_sales[0]))
            if data_sales[1].month >= 7:
                con.execute("UPDATE Sites SET Advisor_second_semester = %s WHERE Id_Site = %s", (Data_dict["form"]["meta"]["username"],data_sales[0]))
            elif data_sales[1].month < 7:
                print(test)
                con.execute("UPDATE Sites SET Advisor_first_semester = %s WHERE Id_Site = %s", (Data_dict["form"]["meta"]["username"],data_sales[0]))
            if 'id' in Data_dict:
                print(Data_dict["form"]["@name"],Data_dict['id'])

            con.execute("UPDATE Closure SET Closed = %s,Reopening_date = %s WHERE Id_Site = %s AND Closed = %s",(False,data_beneficiaries[1],data_beneficiaries[0],True))

        elif Data_dict["form"]["@name"] == "3. Settle Invoices": #checking which requests is coming
            print("here")
            data_fee = get_data_ts_expenses(Data_dict) #extracting data from this request
            data_stock = get_data_stock_ts(Data_dict)
            data_technical_intervention = get_data_technical_intervention_item(Data_dict)
            data_water_alert = get_data_water_alert(Data_dict)
            data_delivery_program = get_data_delivery_program(Data_dict)
            #data_debt = get_data_debt(Data_dict)
            data_WinS = get_data_wins_invoice(Data_dict)
            data_Bottle = get_data_bottle_invoice(Data_dict)

            if data_fee != "no date":
                #UPDATING ENTREPRENEUR CONTRIBUTION
                Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'entrepreneur_contribution'", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_fee[0]) )
                Test = Querytest.fetchall()
                if not Test: #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                            "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_fee)
                if Test:
                    con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'entrepreneur_contribution'", [Data_dict["form"]["month"],Data_dict["form"]["year"],data_fee[0]])
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                            "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_fee)

                #UPDATING STOCK INVOICE
                Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'stock_ts'", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_stock[0]) )
                Test = Querytest.fetchall()
                if not Test: #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_stock)
                if Test:
                    con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'stock_ts'", [Data_dict["form"]["month"],Data_dict["form"]["year"],data_stock[0]])
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_stock)

                #UPDATING BOTTLE CONSOMMABLE
                Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'bottle_invoice'", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_Bottle[0]) )
                Test = Querytest.fetchall()
                if not Test:
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_Bottle)
                if Test:
                    con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'bottle_invoice'", [Data_dict["form"]["month"],Data_dict["form"]["year"],data_Bottle[0]])
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_Bottle)
                
                #UPDATING DELIVERY PROGRAM FEE
                Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'delivery_program_fee'", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_stock[0]) )
                Test = Querytest.fetchall()
                if not Test: #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_delivery_program)
                if Test:
                    con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'delivery_program_fee'", [Data_dict["form"]["month"],Data_dict["form"]["year"],data_stock[0]])
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_delivery_program)

                #UPDATING WinS Invoice
                Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'WinS_invoice'", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_WinS[0]) )
                Test = Querytest.fetchall()
                if not Test:
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                                "VALUES (%s, %s, %s, %s)")
                    con.execute(query,data_WinS)
                if Test:
                    con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'WinS_invoice'", [Data_dict["form"]["month"],Data_dict["form"]["year"],data_WinS[0]])
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses)"
                                "VALUES (%s, %s, %s, %s)")
                    con.execute(query,data_WinS)

                #UPDATING TECHNICAL INTERVENTION
                Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'technical intervention'", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_technical_intervention[0]) )
                Test = Querytest.fetchall()
                if not Test: #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_technical_intervention)
                if Test:
                    con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'technical intervention'", [Data_dict["form"]["month"],Data_dict["form"]["year"],data_technical_intervention[0]])
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_technical_intervention)

                #UPDATING WATER QUALITY ALERT
                Querytest = con.execute("SELECT Code_expenses FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'water quality alert'", (Data_dict["form"]["month"],Data_dict["form"]["year"],data_water_alert[0]) )
                Test = Querytest.fetchall()
                if not Test: #Testing if Test is empty : if empty we create the entry and if not empty we update the old entry (correcting a mistake.)
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_water_alert)
                if Test:
                    con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses = 'water quality alert'", [Data_dict["form"]["month"],Data_dict["form"]["year"],data_water_alert[0]])
                    query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses,Category_expenses)"
                                "VALUES (%s, %s, %s, %s,%s)")
                    con.execute(query,data_water_alert)

                
                data_paid = get_data_partially_paid(Data_dict)
                print(data_paid)
                if data_paid != "no data":
                    for i in range(len(data_paid)):
                        con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = %s",(data_paid[i][3],data_paid[i][0],data_paid[i][1],data_paid[i][2]))

            #con.execute("UPDATE Sites SET Advisor = %s WHERE Id_Site = %s", (Data_dict["form"]["meta"]["username"],data_sales[0]))
            if 'id' in Data_dict:
                print(Data_dict["form"]["@name"],Data_dict['id'])
            

        # elif Data_dict["form"]["@name"] == "3. Register Expenses": #checking which requests is coming
        #     Querytest = con.execute("""SELECT Code_expenses FROM Expenses WHERE 
        #     Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND 
        #     Ref_expenses <> 'entrepreneur_contribution' AND Ref_expenses <> 'stock_ts' AND 
        #     Ref_expenses <> 'debt' AND Ref_expenses <> 'bottle_invoice' AND 
        #     Ref_expenses <>'water quality alert' AND Ref_expenses <> 'technical intervention' AND 
        #     Ref_expenses <> 'WinS_invoice' AND Ref_expenses <> 'delivery_program_fee'""", (Data_dict["form"]["month"],Data_dict["form"]["year"],Data_dict["form"]["site_name"]) )
        #     Test = Querytest.fetchall()
        #     if not Test:  #Testing if Test contains an element : if empty we create the entry and if not empty we erase the old entries and write back (correcting a mistake.)
        #         for j in range(len(Data_dict["form"]["site_confirmed"]["expenses-group"])): #in this database we have one entry per type of expense so we need to add every entry from the request (hence the "for")
        #             data = get_data_expenses(Data_dict,j) #extracting data from this request
        #             query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses, Category_expenses)"
        #                     "VALUES (%s, %s, %s, %s, %s)")
        #             con.execute(query,data)

        #     elif Test:
        #         con.execute("DELETE FROM Expenses WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s AND Ref_expenses <> 'entrepreneur_contribution' AND Ref_expenses <> 'stock_ts' AND Ref_expenses <> 'debt' AND Ref_expenses <> 'bottle_invoice' AND Ref_expenses <>'water quality alert' AND Ref_expenses <> 'technical intervention' AND Ref_expenses <> 'WinS_invoice' AND Ref_expenses <> 'delivery_program_fee'", (Data_dict["form"]["month"],Data_dict["form"]["year"],Data_dict["form"]["site_name"]) )
        #         for j in range(len(Data_dict["form"]["site_confirmed"]["expenses-group"])): #in this database we have one entry per type of expense so we need to add every entry from the request (hence the "for")
        #             data = get_data_expenses(Data_dict,j) #extracting data from this request
        #             query = ("INSERT INTO Expenses (Id_Site, Month, Ref_expenses, Amount_expenses, Category_expenses)"
        #                     "VALUES (%s, %s, %s, %s, %s)")
        #             con.execute(query,data)
        #     print(Data_dict["form"]["@name"],Data_dict['id'])

        elif Data_dict["form"]["@name"] == "5. Production Report":
            data = get_data_indicators(Data_dict)
            Querytest = con.execute("SELECT Number_of_Operator FROM Indicators WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s", (Data_dict["form"]["month"],Data_dict["form"]["year"],data[0]) )
            Test = Querytest.fetchall()
            Querytest2 = con.execute("SELECT Number_of_Vehicle FROM Indicators WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s", (Data_dict["form"]["month"],Data_dict["form"]["year"],data[0]))
            Test2 = Querytest2.fetchall()
            if not Test and not Test2:
                query = ("INSERT INTO Indicators (Id_Site, Month, Number_of_Operator, Number_Bottles_in_Operation, Number_Bottles_in_Stock, Number_Bottles_Broken_Lost, Water_Consume, Machine_begining,Machine_end, Water_begining, Water_end,Saving_outside_TS)"
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)")
                con.execute(query,data)
            else:
                con.execute("UPDATE Indicators SET Number_of_Operator = %s, Number_Bottles_in_Operation = %s, Number_Bottles_in_Stock = %s, Number_Bottles_Broken_Lost = %s, Water_Consume =%s, Machine_begining =%s,Machine_end = %s, Water_begining = %s, Water_end = %s, Saving_outside_TS = %s WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s", (data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9],data[10],data[11],Data_dict["form"]["month"],Data_dict["form"]["year"],data[0]))

        elif Data_dict["form"]["@name"] == "6. Site Checklist":
            data = get_data_vehicles(Data_dict)
            if data != "no date":
                Querytest = con.execute("SELECT Code_Indicator FROM Indicators WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s", (Data_dict["form"]["month"],Data_dict["form"]["year"],data[0]))
                Test = Querytest.fetchall()
                if not Test:
                    query = ("INSERT INTO Indicators (Id_Site, Month, Number_of_Vehicle, Number_of_disinfection,Number_of_delivery)"
                            "VALUES (%s, %s, %s, %s, %s)")
                    con.execute(query,data)
                else:
                    con.execute("UPDATE Indicators SET Number_of_Vehicle = %s, Number_of_disinfection = %s, Number_of_delivery = %s WHERE Month(Month) = %s AND Year(Month) = %s AND Id_Site = %s", (data[2],data[3],data[4],Data_dict["form"]["month"],Data_dict["form"]["year"],data[0]) )

        elif Data_dict["form"]["@name"] == "11. Flash Report":

            
            if (Data_dict["form"]['copy-1-of-site_name']['do_you_want_to_do_monthly_or_weekly_flash_report']=='monthly_report' or Data_dict["form"]['copy-1-of-site_name']['do_you_want_to_do_monthly_or_weekly_flash_report']=='mid_flash_report'):
                data = get_data_flash_report(Data_dict)
                query = con.execute("SELECT Code_Flash_report FROM FlashReport WHERE Month = %s AND Id_Site = %s AND Period = %s",(data[1],data[0],data[6]))
                Test = query.fetchall()
                if not Test:
                    query = ("INSERT INTO FlashReport (Id_Site,Month,Number_jugs_village,Number_jugs_school,Number_bot_displace_people,Open_days,Comment,Period)"
                            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
                    con.execute(query,data)
                else:
                    con.execute("UPDATE FlashReport SET Number_jugs_village = %s, Number_jugs_school = %s, Number_bot_displace_people = %s, Open_days = %s, Comment = %s WHERE Id_Site = %s AND Month = %s AND Period = %s", (data[2],data[3],data[4],data[5],data[6],data[0],data[1],data[7]))
                con.execute("UPDATE Sites SET Advisor = %s WHERE Id_Site = %s", (Data_dict["form"]["meta"]["username"],data[0]))
 
            elif (Data_dict["form"]['copy-1-of-site_name']['do_you_want_to_do_monthly_or_weekly_flash_report']=='weekly_flash_report'):
                data = get_data_weekly_flash_report(Data_dict)
                print(data)
                query = con.execute("SELECT Code_Flash_report FROM WeeklyFlashReport WHERE Month = %s AND Id_Site = %s AND Week = %s",(data[1],data[0],data[6]))
                Test = query.fetchall()
                if not Test:
                     query = ("INSERT INTO WeeklyFlashReport (Id_Site,Month,Number_jugs_village,Number_jugs_school,Open_days,Comment,week)"
                             "VALUES (%s,%s,%s,%s,%s,%s,%s)")
                     con.execute(query,data)
                else:
                     con.execute("UPDATE WeeklyFlashReport SET Number_jugs_village = %s, Number_jugs_school = %s, Open_days = %s, Comment = %s WHERE Id_Site = %s AND week =%s AND Month = %s" , (data[2],data[3],data[4],data[5],data[0],data[6],data[1]))
                     con.execute("UPDATE Sites SET Advisor = %s WHERE Id_Site = %s", (Data_dict["form"]["meta"]["username"],data[0]))

# end change
        elif Data_dict["form"]["@name"] == "7. Request Form":
            ListItem = list(Data_dict["form"]["price_list"]['@ids'].split())

            for i in range(len(ListItem)):
                data_consumable = get_data_consumable(Data_dict,ListItem[i],i)
                if data_consumable[5] != 0:
                    query = ("INSERT INTO Consumable (Id_Site,Month,Date_submission,Category,Item,Number_item,Price_item,Khmer_name,English_name,Unit,Payment_method) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                    con.execute(query,data_consumable)

            con.execute("UPDATE Sites SET Advisor = %s WHERE Id_Site = %s", (Data_dict["form"]["meta"]["username"],data_consumable[0]))
            
        elif Data_dict["form"]["@name"] == "4. Deposit and Withdrawal Form":
            data = get_data_withdrawal(Data_dict)
            print(data)

        elif Data_dict["form"]["@name"] == "8. Entrepreneur Form":
            data = get_data_Entrepreneur_resignation(Data_dict)
            if len(data[0]) > 0: #Resignation
                Resignation_date = datetime.datetime.strptime(data[0][6], '%Y-%m-%d')
                Test = con.execute("SELECT Code_Entrepreneur FROM NewEntrepreneur WHERE Id_Site = %s AND Resignation = %s",data[0][0],False).fetchall()
                if Test:
                    con.execute("UPDATE NewEntrepreneur SET Resignation = %s, Reason_leaving = %s, Resignation_date = %s WHERE Code_entrepreneur = %s",(True,data[0][3],Resignation_date,Test[0][0]))
                if not Test:
                    query = ("INSERT INTO NewEntrepreneur (Id_Site, Entrepreneur_English_name,Entrepreneur_Khmer_name,Resignation, Reason_leaving,Sex,Resignation_date) VALUES (%s,%s,%s,%s,%s,%s,%s)")
                    con.execute(query,[data[0][0],data[0][1],data[0][2],True,data[0][3],data[0][4],Resignation_date])
                if data[0][5] == "Not_Active":
                    Closing_date = Resignation_date.strftime("%Y-%m-%d")
                    closeSiteApi(data[0][0], "សហគ្រិនលាលែង - Entrepreneur resignation", Closing_date, data[0][3],data[2])

            if len(data[1]) > 0: #New Entrepreneur
                data[1][3] = datetime.datetime.strptime(data[1][3], '%Y-%m-%d')
                data[1][9] = datetime.datetime.strptime(data[1][9], '%Y-%m-%d')
                query = ("INSERT INTO NewEntrepreneur (Id_Site,Entrepreneur_English_name,Entrepreneur_Khmer_name,Date_start_working,Education,Sex,Phone_number,Second_phone_number,Commune,Date_of_birth,Province,Previous_job,Resignation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                data[1].append(False)
                con.execute(query,data[1])
                query = ("""UPDATE Sites SET Entrepreneur_English_name = %s, Entrepreneur_Khmer_name = %s,
                                        Date_start_working = %s, Education = %s, Sex = %s, Phone_number = %s, 
                                        Commune_Entrepreneur = %s, Date_of_birth = %s, Province_Entrepreneur = %s, 
                                        Previous_job = %s, Resignation = %s WHERE Id_Site = %s
                                        """,(data[1][1],data[1][2],data[1][3],data[1][4],data[1][5],data[1][6],data[1][8],data[1][9],data[1][10],data[1][11],data[1][12],data[1][0]))
        return "ok"

    else :
        return("Error : not a valid form.")

def UpdateBDDIntervention(Data_dict):
    null = None
    for i in range(Data_dict):
        data = [Data_dict[i]["site"],Data_dict[i]["date"],Data_dict[i]["date_submitted"],Data_dict[i]["item_ref"][2],Data_dict[i]["item_ref"],Data_dict[i]["quantity"],Data_dict[i]["unit_price"],Data_dict[i]["khmer_name"],Data_dict[i]["eng_name"],Data_dict[i]["unit"]]
        query = ("INSERT INTO Consumable (Id_Site,Month,Date_submission,Category,Item,Number_item,Price_item,Khmer_name,English_name,Unit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
        con.execute(query,data_consumable)
