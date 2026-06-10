import db
from datetime import date

con = db.pool.connect()

def Debt(Dicdebt,current_date):
    # ListSite = list(Dicdebt.keys())
    # ListDebt = list(Dicdebt.values())
    
    # for i in range(len(ListSite)):
    #     Test = con.execute("SELECT Code_expenses FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'debt'",(ListSite[i],current_date)).fetchall()
    #     print("Debts update", ListSite[i], ListDebt[i])
    #     if Test:
    #         con.execute("UPDATE Expenses SET Amount_expenses = %s WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'debt'",(-ListDebt[i],ListSite[i],current_date))
    #     else:
    #         con.execute("INSERT INTO Expenses(Id_Site,Month,Ref_expenses,Amount_expenses) VALUES (%s,%s,%s,%s)",(ListSite[i],current_date,'debt',-ListDebt[i]))
    # return Dicdebt
    return("ok")

if __name__ == '__main__':
    Dicdebt = {
     "A2": 52000,
     "C6": 17000
    }
    Debt(Dicdebt,'2021-05-01')
