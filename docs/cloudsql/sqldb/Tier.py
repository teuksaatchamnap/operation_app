from ast import List
import os #used for importing datastore
from datetime import timedelta, date,datetime
from calendar import monthrange
import db
from dateutil.relativedelta import *
from monthlyreport.Functionutils import listSite, listDate, CalculBeneficiaries as calc_beneficiaries

con = db.pool.connect()

def CalculBeneficiaries():
    """Compute beneficiaries over the last 12 months and store it for last month.

    Writes into table `Beneficiaries` (column `Beneficiaries12months`).
    If the row (Id_Site, Month) doesn't exist yet, it will be inserted.
    """
    lastmonth = datetime.now() - relativedelta(months=+1)
    month_key = datetime(lastmonth.year, lastmonth.month, 1)

    ListSiteAll = con.execute(
        """SELECT SUM(COALESCE(Total_Sales, 0) - COALESCE(WiS_Sales, 0)), Id_Site FROM Sales
                              WHERE Month <=%s AND Month > %s
                              GROUP BY Id_Site""",
        (lastmonth, lastmonth - relativedelta(months=+12)),
    ).fetchall()

    for total_botday, site_id in ListSiteAll:
        beneficiaries_12m = calc_beneficiaries(total_botday or 0)

        result = con.execute(
            """UPDATE Beneficiaries
               SET Beneficiaries12months = %s
               WHERE Month = %s AND Id_Site = %s""",
            (beneficiaries_12m, month_key, site_id),
        )

        if getattr(result, "rowcount", 0) == 0:
            con.execute(
                """INSERT INTO Beneficiaries (Id_Site, Month, Beneficiaries12months)
                   VALUES (%s, %s, %s)""",
                (site_id, month_key, beneficiaries_12m),
            )


def BackfillBeneficiaries12months():
    """One-off: fill Beneficiaries.Beneficiaries12months for all months present in Sales.

    This iterates over each distinct `Sales.Month` and computes the rolling 12-month
    total per site, then upserts into `Beneficiaries` for that month.
    """
    months = con.execute(
        """SELECT DISTINCT Month
           FROM Sales
           WHERE Month IS NOT NULL
           ORDER BY Month"""
    ).fetchall()

    for (month_value,) in months:
        month_key = datetime(month_value.year, month_value.month, 1)
        window_start = month_key - relativedelta(months=+12)

        site_totals = con.execute(
            """SELECT SUM(COALESCE(Total_Sales, 0) - COALESCE(WiS_Sales, 0))/SUM(Number_Open_Days), Id_Site FROM Sales
                                  WHERE Month <= %s AND Month > %s
                                  GROUP BY Id_Site""",
            (month_key, window_start),
        ).fetchall()

        for total_botday, site_id in site_totals:
            beneficiaries_12m = calc_beneficiaries(total_botday or 0)

            result = con.execute(
                """UPDATE Beneficiaries
                   SET Beneficiaries = %s
                   WHERE Month = %s AND Id_Site = %s""",
                (beneficiaries_12m, month_key, site_id),
            )

            if getattr(result, "rowcount", 0) == 0:
                con.execute(
                    """INSERT INTO Beneficiaries (Id_Site, Month, Beneficiaries)
                       VALUES (%s, %s, %s)""",
                    (site_id, month_key, beneficiaries_12m),
                )


def CalculTier(): #Update Last Tier in Sites
    lastmonth = datetime.now() - relativedelta(months=+1)
    Current_date = date(lastmonth.year,lastmonth.month,1)

    Date_N_1 = Current_date-relativedelta(months=+12)

    ListSiteDead = con.execute("SELECT Id_Site FROM Sites WHERE Platform = 'Dead'").fetchall()
    ListSiteDead = [i[0] for i in ListSiteDead] or [""]
    ListSiteDead_Tier = [(i,"Dead") for i in ListSiteDead if i != ""]

    ListSiteClosed = con.execute("SELECT DISTINCT Sites.Id_Site FROM Sites INNER JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Sites.Id_Site NOT IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month <= %s AND Month > %s) AND Sites.Id_Site NOT IN %s",(Current_date,Date_N_1,ListSiteDead)).fetchall()
    ListSiteClosed = [i[0] for i in ListSiteClosed] or [""]
    ListSiteClosed_Tier = [(i,"Closed") for i in ListSiteClosed if i != ""]

    ListSiteInactive = con.execute("SELECT DISTINCT Sites.Id_Site FROM Sites INNER JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Sites.Id_Site NOT IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s) AND Sites.Id_Site NOT IN %s AND Sites.Id_Site NOT IN %s",(Current_date,ListSiteDead,ListSiteClosed)).fetchall()
    ListSiteInactive = [i[0] for i in ListSiteInactive] or [""]
    ListSiteInactive_Tier = [(i,"Inactive") for i in ListSiteInactive if i != ""]

    ListSiteNew = con.execute("SELECT DISTINCT Sites.Id_Site FROM Sites INNER JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Sites.Id_Site NOT IN %s AND Sites.Id_Site NOT IN %s AND Sites.Id_Site NOT IN %s GROUP BY Sites.Id_Site HAVING COUNT(Total_Sales) <= 3",(Current_date,ListSiteDead,ListSiteClosed,ListSiteInactive)).fetchall()
    ListSiteNew = [i[0] for i in ListSiteNew] or [""]
    ListSiteNew_Tier = [(i,"New") for i in ListSiteNew if i != ""]

    ListSiteReopen = con.execute("SELECT DISTINCT Sales.Id_Site FROM Sales WHERE Month <= %s AND Month >= %s AND Id_Site NOT IN %s AND Id_Site NOT IN %s AND Id_Site NOT IN %s AND Id_Site NOT IN %s GROUP BY Id_Site HAVING COUNT(Total_Sales)<4",(Current_date,Current_date-relativedelta(months=+3),ListSiteDead,ListSiteClosed,ListSiteInactive,ListSiteNew)).fetchall()
    ListSiteReopen = [i[0] for i in ListSiteReopen] or [""]
    ListSiteReopen_Tier = [(i,"Reopen") for i in ListSiteReopen if i != ""]

    ListAllNoTierSite = ListSiteDead + ListSiteClosed + ListSiteInactive + ListSiteNew + ListSiteReopen

    ListAllSite = con.execute("SELECT Id_Site,SUM(Total_Sales)/SUM(Number_Open_Days) FROM Sales WHERE Month <= %s AND Month > %s AND Id_Site NOT IN %s GROUP BY Id_Site",(Current_date,Date_N_1,ListAllNoTierSite)).fetchall()

    ListSiteST1_Tier = []
    ListSite1_Tier = []
    ListSite2_Tier = []
    ListSite3_Tier = []
    ListSiteST1 = []
    ListSite1 = []
    ListSite2 = []
    ListSite3 = []
    for i in range(len(ListAllSite)):
        if ListAllSite[i][1] > 125:
            ListSiteST1_Tier.append((ListAllSite[i][0],"ST1"))
        elif ListAllSite[i][1] > 85:
            ListSite1_Tier.append((ListAllSite[i][0],"1"))
        elif ListAllSite[i][1] >= 60:
            ListSite2_Tier.append((ListAllSite[i][0],"2"))
        elif ListAllSite[i][1] > 0:
            ListSite3_Tier.append((ListAllSite[i][0],"3"))
    AllSite_Tier = ListSiteDead_Tier + ListSiteClosed_Tier + ListSiteInactive_Tier + ListSiteReopen_Tier + ListSiteNew_Tier + ListSiteST1_Tier + ListSite1_Tier + ListSite2_Tier + ListSite3_Tier

    for i in range(len(AllSite_Tier)):
        con.execute("UPDATE Sites SET Last_Tier = %s WHERE Id_Site = %s",(AllSite_Tier[i][1],AllSite_Tier[i][0]))
        #print((AllSite_Tier[i][0],AllSite_Tier[i][1]))
    return "ok"

def Chlorine():
    #Order for chlorine are made on the 19th of the month before every even month automatically (cron job) for every active site
    Current_date = date.today()
    Date_start_of_month = date(Current_date.year,Current_date.month,1)
    Date_order = date(Current_date.year,Current_date.month,1)
    if int(Current_date.month) in [2,4,6,8,10,12]:
        ListSite = con.execute("SELECT Sales.Id_Site FROM Sales WHERE (Total_Sales IS NOT NULL AND Month = %s) ",Date_start_of_month-relativedelta(months=+2)).fetchall()
        ListSiteClosedThisMonth = con.execute("SELECT Id_Site FROM Closure WHERE Closing_date > %s AND Reopening_date IS NULL",Date_start_of_month-relativedelta(months=+4)).fetchall()
        #SiteExcluded = ["I29", "I30", "K11", "M34","L35"]
        SiteExcluded = ["I29", "I30", "K11", "M34","L35"]
        Site2_0 = ["H3","G24","E7"]
        SiteExtraFilter = [
            "I17", "O4", "Q3", "K11", "H22", "P20", "Q16", "Q15", 
            "C7", "Q6", "K18", "K19", "L12", "Q11", "P15", "M24", "M15"
        ]

        for i in range(len(ListSite)):
            if ListSite[i] not in ListSiteClosedThisMonth:
                query = ("INSERT INTO Consumable (Id_Site,Month,Date_submission,Category,Item,Number_item,Price_Item,Khmer_name,English_name,Validate,Unit,Payment_method) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
                con.execute(query,(ListSite[i][0],Date_order,Current_date,'2','501001',1,10000,'ម្សៅក្លរីន','Chlorine powder',False,'kg', 'Invoice'))
                if ListSite[i][0] not in SiteExcluded and ListSite[i][0] not in Site2_0:
                    con.execute(query,(ListSite[i][0],Date_order,Current_date,'4','211001',4,32000,'តម្រង 1 មីក្រុង','1µm filter fitting with 10" length house',False,'pcs', 'Invoice'))
                    con.execute(query,(ListSite[i][0],Date_order,Current_date,'4','211002',4,32000,'តម្រង 5 មីក្រុង','5µm filter fitting with 10" length house',False,'pcs', 'Invoice'))
                    con.execute(query,(ListSite[i][0],Date_order,Current_date,'4','211003',4,32000,'តម្រង 10 មីក្រុង','10µm filter fitting with 10" length house',False,'pcs', 'Invoice'))
                    con.execute(query,(ListSite[i][0],Date_order,Current_date,'4','211004',4,42400,'តម្រង 50 មីក្រុង','50µm filter fitting with 10" length house',False,'pcs', 'Invoice'))
                    if ListSite[i][0] in SiteExtraFilter:
                        con.execute(query, (ListSite[i][0], Date_order, Current_date, '4', '211007', 4, 87200, 'PP Filter Bigblue 20 Inch (1 Micron) / សំឡីចម្រោះទឹក', '1µm "big" filter fitting with 20" length house', False, 'pcs', 'Invoice'))
                elif ListSite[i][0] in Site2_0:
                    con.execute(query, (ListSite[i][0], Date_order, Current_date, '4', '211005', 4, 24800, '1µm filter fitting with 20" length house', '1µm filter fitting with 20" length house', False, 'kg', 'Invoice'))
                    con.execute(query, (ListSite[i][0], Date_order, Current_date, '4', '211006', 4, 24800, '5µm filter - Fitting with 20" length cartridge filter housing', '5µm filter fitting with 20" length house', False, 'kg', 'Invoice'))
    return("ok")

if __name__ == '__main__':
    pass
    #print(con.execute("SELECT Id_Site,Last_Tier,Platform,Province FROM Sites").fetchall())
