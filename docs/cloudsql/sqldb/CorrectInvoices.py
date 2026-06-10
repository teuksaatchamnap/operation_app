import pandas as pd
import db
from datetime import date,datetime
from monthlyreport.Functionutils import listSite
from dateutil.relativedelta import *
import mail
import traceback

def FinanceCheck(doc):
    con = db.pool.connect()
    xls = pd.ExcelFile(doc)
    try:
        df = pd.read_excel(xls, '5. Sites Database')
    except:
        df = pd.read_excel(xls, '5. Sites Database ')
    df.columns = range(len(df.columns))
    print('df')
    Date = str(df.iloc[12,9])[-10:]
    Current_date = date(int(Date[:4]),int(Date[5:7]),1)
    Date_M_plus_1 = Current_date + relativedelta(months=+1)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND Ref_expenses = 'stock_ts'",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND (Ref_expenses = 'entrepreneur_contribution')",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND (Ref_expenses = 'bottle_invoice')",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND (Ref_expenses = 'technical intervention')",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND (Ref_expenses = 'water quality alert')",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND (Ref_expenses = 'withdrawal')",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND (Ref_expenses = 'WinS_invoice')",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND Ref_expenses = 'adjustment'",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND Ref_expenses = 'debt'",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND Ref_expenses = 'delivery_program_fee'",Current_date)
    con.execute("DELETE FROM Expenses WHERE Month = %s AND Ref_expenses = 'total-other-cost'",Current_date)
    query = con.execute("SELECT Id_Site FROM Expenses WHERE Month = %s AND Ref_Expenses = 'debt'",Date_M_plus_1)
    alldebt_M_plus_1 =query.fetchall()
    List_Stock_invoice = []
    List_Bottle_invoice = []
    ListSite = listSite()

    for index,row in df.iterrows():
        Name_Site = str(row[1]).rstrip()
        if not pd.isna(row[1]): #update debt beginning and end of the month
            try:
                row[4] = (0 if pd.isna(row[4]) else row[4])
                row[9] = (0 if pd.isna(row[9]) else row[9])

                query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses) VALUES (%s,%s,%s,%s)")
                con.execute(query,[Name_Site,Current_date,"debt",row[4]])
                debt_M_plus_1 = list(filter(lambda row: row[0] == Name_Site, alldebt_M_plus_1))
                if debt_M_plus_1:
                    con.execute("UPDATE Expenses SET Amount_expenses = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'debt'",(row[9],Name_Site,Date_M_plus_1))
                else:
                    query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses) VALUES (%s,%s,%s,%s)")
                    con.execute(query,[Name_Site,Date_M_plus_1,"debt",row[9]])
            except:
                pass

    try:
        df = pd.read_excel(xls, '1. Invoice listing', usecols='C:E,J')
    except:
        df = pd.read_excel(xls, '1. Invoice listing ')
    df.columns = range(len(df.columns))
    df.info(verbose=False, memory_usage="deep")
    print('df')

    for index,row in df.iterrows(): #update invoices (what is due to TS)
        Name_Site = str(row[0]).rstrip()
        if str(row[1]).lower() == "stock invoice" and str(row[2]) != '401001' and str(row[2]) != '401002':
            row[3] = (0 if pd.isna(row[3]) else row[3])
            List_Stock_invoice.append((Name_Site,row[3]))

        if str(row[1]).lower() == 'bottle invoice' or str(row[2]) == '401001' or str(row[2]) == '401002':
            row[3] = (0 if pd.isna(row[3]) else row[3])
            List_Bottle_invoice.append((Name_Site,row[3]))

        if str(row[1]).lower() == "af invoice" or str(row[1]).lower() == "ec invoice":
            row[3] = (0 if pd.isna(row[3]) else row[3])
            query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses,Category_expenses) VALUES (%s,%s,%s,%s,%s)")
            con.execute(query,[Name_Site,Current_date,"entrepreneur_contribution",row[3],'contribution'])

        if (str(row[1]).lower() == "technical service" or str(row[1]).lower() == "technical intervention"):
            row[3] = (0 if pd.isna(row[3]) else row[3])
            query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses,Category_expenses) VALUES (%s,%s,%s,%s,%s)")
            con.execute(query,[Name_Site,Current_date,"technical intervention",row[3],"technical"])

        if (str(row[1]).lower() == "water quality" or str(row[1]).lower() == "water quality alert"):
            row[3] = (0 if pd.isna(row[3]) else row[3])
            query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses,Category_expenses) VALUES (%s,%s,%s,%s,%s)")
            con.execute(query,[Name_Site,Current_date,"water quality alert",row[3],"technical"])

        if str(row[1]).lower() == "delivery program fee":
            row[3] = (0 if pd.isna(row[3]) else row[3])
            query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses,Category_expenses) VALUES (%s,%s,%s,%s,%s)")
            con.execute(query,[Name_Site,Current_date,"delivery_program_fee",row[3],"delivery"])

    for i in range(len(ListSite)): #Calculate the stock invoice total (multiply line with stock invoice)
        List_stock = list(filter(lambda row: row[0] == ListSite[i][0], List_Stock_invoice))
        List_bottle = list(filter(lambda row: row[0] == ListSite[i][0], List_Bottle_invoice))

        Total_stock = 0
        Total_bottle = 0
        if List_stock:
            for j in range(len(List_stock)):
                Total_stock += List_stock[j][1]
        if List_bottle:
            for k in range(len(List_bottle)):
                Total_bottle += List_bottle[k][1]
        query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses,Category_expenses) VALUES (%s,%s,%s,%s,%s)")
        con.execute(query,[ListSite[i][0],Current_date,"stock_ts",Total_stock,"production"])
        query = ("INSERT INTO Expenses (Id_Site,Month,Ref_expenses,Amount_expenses,Category_expenses) VALUES (%s,%s,%s,%s,%s)")
        con.execute(query,[ListSite[i][0],Current_date,"bottle_invoice",Total_bottle,'production'])

    try:
        df = pd.read_excel(xls, '2. Payment report')
    except:
        df = pd.read_excel(xls, '2. Payment report ')
    df.columns = range(len(df.columns))
    df.info(verbose=False, memory_usage="deep")

    print('df')
    df = df.iloc[2: , :]
    for index,row in df.iterrows(): #Update what was actually paid by the entrepreneur
  
        try:
            Name_Site = str(row[3]).rstrip()
            if str(row[9]).lower() == "entrepreneur contribution" or str(row[9]).lower() == "assistant fee":
                row[7] = (0 if pd.isna(row[7]) else row[7])
                con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'entrepreneur_contribution'",(row[7],Name_Site,Current_date))
                
            if str(row[9]).lower() == "stock invoice":
                row[7] = (0 if pd.isna(row[7]) else row[7])
                con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'stock_ts'",(row[7],Name_Site,Current_date))
                
            if (str(row[9]).lower() == "technical service" or str(row[9]).lower() == "technical intervention"):
                row[7] = (0 if pd.isna(row[7]) else row[7])
                con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'technical intervention'",(row[7],Name_Site,Current_date))
               
            if (str(row[9]).lower() == "water quality" or str(row[9]).lower() == "water quality alert"):
                row[7] = (0 if pd.isna(row[7]) else row[7])
                con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'water quality alert'",(row[7],Name_Site,Current_date))
                
            if str(row[9]).lower() == "consumable bottle" :
                row[7] = (0 if pd.isna(row[7]) else row[7])
                con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'bottle_invoice'",(row[7],Name_Site,Current_date))
                  
            if str(row[9]).lower() == "adjustment" or str(row[9]).lower() == "adjustments":
                row[7] = (0 if pd.isna(row[7]) else row[7])
                query = ("INSERT INTO Expenses(Id_Site,Month,Ref_expenses,Paid) VALUES (%s,%s,%s,%s) ")
                con.execute(query,[Name_Site,Current_date,"adjustment",row[7]])

            if str(row[9]).lower() == "debts":
                row[7] = (0 if pd.isna(row[7]) else row[7])
                con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'debt'",(row[7],Name_Site,Current_date))
                
            if str(row[9]).lower() == "withdraw" or str(row[9]).lower() == "deposit":
                row[6] = (0 if pd.isna(row[6]) else row[6])
                row[7] = (0 if pd.isna(row[7]) else row[7])
                query = ("INSERT INTO Expenses(Id_Site,Month,Ref_expenses,Amount_expenses,Paid) VALUES (%s,%s,%s,%s,%s) ")
                con.execute(query,[Name_Site,Current_date,"withdrawal",row[6],row[7]])

            if str(row[9]).lower() == "school-program":
                row[6] = (0 if pd.isna(row[6]) else row[6])
                row[7] = (0 if pd.isna(row[7]) else row[7])
                query = ("INSERT INTO Expenses(Id_Site,Month,Ref_expenses,Amount_expenses,Paid) VALUES (%s,%s,%s,%s,%s) ")
                con.execute(query,[Name_Site,Current_date,"WinS_invoice",row[6],row[7]])
            
            if str(row[9]).lower() == "delivery program fee" :
                row[7] = (0 if pd.isna(row[7]) else row[7])
                con.execute("UPDATE Expenses SET Paid = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'delivery_program_fee'",(row[7],Name_Site,Current_date))
            
        except:
            pass

    con.close()

    try:
        mail.send_email(
            to_emails=['axel.liber@1001fontaines.com','vanny.i@teuksaat1001.com'],
            subject='Finance import Site Database',
            html_content='<p>Finance have updated the invoice at %s</p>'%(datetime.today()))
    except Exception as e:
        print(e)




if __name__ == '__main__':
    FinanceCheck('01-Site Database_January 2020 -QB integration _controle integrated Final.xlsx')
    FinanceCheck('02-Site Database_February_QB integration _control integrated Final.xlsx')
    FinanceCheck('03- Site database_March_QB integration _controle integrated- Final.xlsx')
    FinanceCheck('04- Site database_April 2020_QB integration _controle integrated Final _ VF.xlsx')
    FinanceCheck('05- Site database_May 2020_QB integration _controle integrated- Final.xlsx')
    FinanceCheck('06- Site database_June 2020_QB integration _controle integrated- Final.xlsx')
    FinanceCheck('07- Site database_July 2020_QB integration _controle integrated- Final.xlsx')
    FinanceCheck('08- Site database_ Aug 2020_QB integration _controle integrated- Final.xlsx')
    FinanceCheck('09- Site database_ 2020_QB integration _controle integrated- Final.xlsx')
    FinanceCheck('10- Site database_ 2020_QB integration _controle integrated- Final_V2.xlsx')
    FinanceCheck('11- Site database_ 2020_QB integration _controle integrated- Final.xlsx')
    FinanceCheck('12- Site database_ 2020_QB integration _controle integrated- Final.xlsx')

    FinanceCheck('01- Site database_ 2021_QB integration _controle integrated- Final_After WO.xlsx')
    FinanceCheck('02- Site database_ 2021_QB integration _controle integrated- Final_V2.xlsx')
    FinanceCheck('03- Site database_ March 2021_QB integration _controle integrated_Leak.xlsx')
    FinanceCheck('04- Site database_ April 2021_QB integration _controle integrated_Final.xlsx')
    FinanceCheck('05- Site database_ May 2021_QB integration _controle integrated_Final.xlsx')
    FinanceCheck('06_Site_database_Jun_2021_QB_integration_controle_integrated_V1_final.xlsx')
    FinanceCheck('07_Site_database_Jul_2021_QB_integration_controle_integrated_V1_Final_Leak.xlsx')
    FinanceCheck('08_Site_database_Aug_2021_QB_integration_controle_integrated_Leak review.xlsx')
    FinanceCheck('09_Site_database_Sept_2021_QB_integration_controle_integrated_V1_Final  (1).xlsx')
    FinanceCheck('10_Site_database_Oct_2021_QB_integration_controle_integrated _V1_update WQ.xlsx')
    FinanceCheck('11_Site_database_Nov_2021_QB_integration_controle_integrated_Leak review.xlsx')
    FinanceCheck('12_Site_database_Dec_2021_QB_integration_controle_integrated.xlsx')
