import db
from datetime import date

con = db.pool.connect()

def DeleteFromDB(Month,Site,Request):
    if Request == "1. Register Sales":
        con.execute("DELETE FROM DailySales WHERE Id_Site = %s AND Month = %s",(Site,Month))
        con.execute("DELETE FROM Sales WHERE Id_Site = %s AND Month = %s",(Site,Month))
        con.execute("DELETE FROM Beneficiaries WHERE Id_Site = %s AND Month = %s", (Site,Month))

    elif Request == "2. Settle Invoices":
        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'entrepreneur_contribution'",(Site,Month))
        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'stock_ts'",(Site,Month))
        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'bottle_invoice'",(Site,Month))
        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'technical intervention'",(Site,Month))
        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'water quality alert'",(Site,Month))
        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'WinS_invoice'",(Site,Month))
        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month = %s AND Ref_expenses = 'delivery_program_fee'",(Site,Month))


    elif Request == "3. Register Expenses":

        con.execute("DELETE FROM Expenses WHERE Id_Site = %s AND Month =%s AND Ref_expenses<> 'bottle_invoice' AND Ref_expenses <> 'WinS_invoice' AND Ref_expenses <> 'entrepreneur_contribution' AND Ref_expenses <> 'stock_ts' AND Ref_expenses <> 'technical intervention' AND Ref_expenses <> 'water quality alert' AND Ref_expenses <> 'delivery_program_fee'",(Site,Month))

        
    elif Request == "5. Production Report":
        con.execute("DELETE FROM Indicators WHERE Id_Site = %s AND Month = %s", (Site,Month))

    elif Request == "11. Flash Report":
        con.execute("DELETE FROM FlashReport WHERE Id_Site = %s AND Month = %s",(Site,Month))

    elif Request == "6. Site Checklist":
        con.execute("DELETE FROM Indicators WHERE Id_Site = %s AND Month = %s",(Site,Month))

    return("ok")

if __name__ == '__main__':
    Month = date(2017,1,1)
    Site = 'A1'
    DeleteFromDB(Month,Site,"1. Register Sales")
    query = con.execute("SELECT * FROM Sales WHERE Id_Site = %s AND Month = %s",(Site,Month))
    print(query.fetchall())
