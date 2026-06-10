import pandas as pd
import db
con = db.pool.connect()

def debthistoric(doc):
    df = pd.read_excel(doc)
    name = df.columns.tolist()
    for index,row in df.iterrows():
        for i in range(len(name)-1):
            if not pd.isna(row[i+1]):
                print(row[0])
                Id_Site = row[0]
                Month = name[i+1]
                Expenses_amount = row[i+1]
                Ref_expenses = 'debt'
                query = con.execute("SELECT Code_Expenses FROM Expenses WHERE Ref_expenses = 'debt' AND Month = %s AND Id_Site = %s",(Month,Id_Site))
                test = query.fetchall()
                if not test:
                    query = ("INSERT INTO Expenses(Id_Site,Month,Amount_expenses,Ref_expenses) VALUES (%s,%s,%s,%s)")
                    con.execute(query,(Id_Site,Month,Expenses_amount,Ref_expenses))
                else:
                    con.execute("UPDATE Expenses SET Amount_expenses = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses=%s",(Expenses_amount,Id_Site, Month,Ref_expenses))

debthistoric('Debt Janv-June 2021.xlsx')
