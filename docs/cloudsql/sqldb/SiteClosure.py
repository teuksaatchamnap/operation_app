import db
from datetime import date
from dateutil.relativedelta import *
from monthlyreport.Functionutils import translate_text

con = db.pool.connect()

def closeSite(siteName, dateFermeture, raisonFermetureAnglais, raisonFermetureKhmer, Description):
    DescriptionEnglish = translate_text("en",Description)
    query = ("INSERT INTO Closure(Id_Site,Closed,Closing_date,Closing_reason_english,Closing_reason_khmer,Description,Description_english) VALUES (%s,%s,%s,%s,%s,%s,%s)")
    con.execute(query,(siteName,"1",dateFermeture,raisonFermetureAnglais,raisonFermetureKhmer,Description,DescriptionEnglish))
    con.execute("UPDATE Sites SET Last_Tier = 'Inactive' WHERE Id_Site = %s",(siteName))

def reopenSite(siteName, dateOuverture):
    con.execute("UPDATE Closure SET Closed = %s,Reopening_date = %s WHERE Id_Site = %s AND Closed = %s",(False,dateOuverture,siteName,True))


def InitiateClosure():
    query = con.execute("SELECT Sites.Id_Site FROM Sites JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Sales.Month = %s AND Total_Sales IS NOT NULL ORDER BY Sites.Id_Site",(date(2021,8,1)))
    Site_actif = query.fetchall()
    query = con.execute("SELECT Id_Site FROM Sites")
    Site = query.fetchall()
    for i in Site_actif:
        Site.remove(i)
    Site.remove(('A1',))
    print(Site)
    query = con.execute('SELECT Max(Month),Id_Site FROM Sales WHERE Total_Sales is NOT NULL GROUP BY Id_Site')
    last_sales = (query.fetchall())
    for i in range(len(Site)):
        Date = list(filter(lambda row: row[1] == Site[i][0], last_sales))
        if Date:
            query = ("INSERT INTO Closure(Id_Site,Closed,Closing_date) VALUES (%s,%s,%s)")
            con.execute(query,(Site[i][0]),True,Date[0][0]+relativedelta(months=+1))
        print(Date)

def HistoricDateClosure():
    start_date = date(2005,1,1)
    end_date = date(2021,7,1)
    ListSiteOpen = []
    ListSiteOpen_lastmonth = []
    ListSiteClose_now = []
    con.execute("DELETE FROM Closure WHERE Closing_date <= %s",(end_date))
    while start_date <= end_date:
        query = con.execute("SELECT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL",start_date)
        List_Site = query.fetchall()
        for i in range(len(List_Site)):
            if List_Site[i] not in ListSiteOpen:
                ListSiteOpen.append(List_Site[i])
            elif List_Site[i] in ListSiteClose_now:
                ListSiteClose_now.remove(List_Site[i])
                #print(con.execute("SELECT Reopening_date FROM Closure WHERE Reopening_date = %s AND Id_Site = %s AND Closed = '1'",(start_date,List_Site[i][0])).fetchall())
                con.execute("UPDATE Closure SET Closed = %s, Reopening_date = %s WHERE Id_Site = %s AND Closed = '1' AND Closing_date< %s",(False,start_date,List_Site[i][0],end_date))
        for j in range(len(ListSiteOpen_lastmonth)):
            if ListSiteOpen_lastmonth[j] not in List_Site:
                ListSiteClose_now.append(ListSiteOpen_lastmonth[j])
                query = ("INSERT INTO Closure (Id_Site, Closed, Closing_date)"
                        "VALUES (%s, %s, %s)")
                con.execute(query,(ListSiteOpen_lastmonth[j][0],"1",start_date))
        ListSiteOpen_lastmonth = List_Site
        # print('ListSite This month : ', List_Site)
        # print('ListSite Open from beginning : ', ListSiteOpen)
        # print('ListSite Closed : ',ListSiteClose_now)
        # wait = input("go")

        start_date += relativedelta(months=+1)
if __name__ == '__main__':
    HistoricDateClosure()
