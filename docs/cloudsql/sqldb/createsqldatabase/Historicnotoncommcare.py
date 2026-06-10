import pandas as pd
import db
from monthlyreport.Functionutils import listSite,CalculNombreMoisOuverture,Numberdaysopeningyear,CalculTier
from dateutil.relativedelta import *

con = db.pool.connect()

def Dataimport(doc):
    df = pd.read_excel(doc)
    Sitefromdoc = list(df)
    for i in range(len(Sitefromdoc)):
        Sitefromdoc[i] = (Sitefromdoc[i],)
    del(Sitefromdoc[0],Sitefromdoc[0])
    ListSite = listSite()
    for index,row in df.iterrows():
        print(row[0])
        mostRecentDate = row[0]
        Date2 = mostRecentDate - relativedelta(months=+12)
        Opened_month = CalculNombreMoisOuverture(mostRecentDate,Date2,Sitefromdoc)
        ListOpenDay = Numberdaysopeningyear(mostRecentDate,Date2,Sitefromdoc)
        Tier = CalculTier(mostRecentDate,Date2,Opened_month, Sitefromdoc,ListOpenDay)
        for i in range(len(Sitefromdoc)):

            if not Sitefromdoc[i] in ListSite:
                query = ("INSERT INTO Sites (Id_Site,Platform,Province,Code_Province,Advisor,Advisor_first_semester,Advisor_second_semester) VALUES (%s,%s,%s,%s,%s,%s,%s)")
                con.execute(query,[Sitefromdoc[i][0],'Stop','Stop','Stop','Stop','Stop','Stop'])

            query = con.execute("SELECT Total_Sales FROM Sales WHERE Id_Site = %s AND Month = %s", (Sitefromdoc[i][0],row[0]))
            Test = query.fetchone()
            #print(Test)

            if not Test:
                if row[i+2] and row[i+2] > 0:
                    con.execute("INSERT INTO Sales (Id_Site,Month,Total_Sales,Bottle_Sales) VALUES (%s,%s,%s)", (Sitefromdoc[i][0],row[0],row[i+2]*row[1]/20,0))

                    #print(Tier,Sitefromdoc[i],row[0])
                    con.execute("UPDATE Sales SET Tier = %s WHERE Id_Site = %s AND Month = %s",(Tier[i],Sitefromdoc[i][0],row[0]))
                    # print(Tier)

            else:
                if row[i+2] and row[i+2] >0:
                    Bottle_Sales = con.execute("SELECT Bottle_Sales FROM Sales WHERE Id_Site = %s AND Month = %s",(Sitefromdoc[i][0],row[0])).fetchone()
                    if Bottle_Sales and Bottle_Sales[0]:
                        #print((row[i+2]*row[1]/20), Bottle_Sales)
                        con.execute("UPDATE Sales SET Total_Sales = %s WHERE Id_Site = %s AND Month = %s",((row[i+2]*row[1]/20)+Bottle_Sales[0],Sitefromdoc[i][0],row[0]))
                        con.execute("UPDATE Sales SET Tier = %s WHERE Id_Site = %s AND Month = %s",(Tier[i],Sitefromdoc[i][0],row[0]))
                        #print(Tier)
                    else:
                        con.execute("UPDATE Sales SET Total_Sales = %s,Bottle_Sales=0 WHERE Id_Site = %s AND Month = %s",(row[i+2]*row[1]/20,Sitefromdoc[i][0],row[0]))
                        con.execute("UPDATE Sales SET Tier = %s WHERE Id_Site = %s AND Month = %s",(Tier[i],Sitefromdoc[i][0],row[0]))


if __name__ == '__main__':
    Dataimport('Historicdata.xlsx')
