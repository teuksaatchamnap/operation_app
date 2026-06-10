from re import I
import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta
from calendar import monthrange
import db
from dateutil.relativedelta import *
from google.cloud import translate_v2 as translate
from google.oauth2.service_account import Credentials
import os
import json
import flask

con = db.pool.connect()

def exchange_rate_year(Date):
    if isinstance(Date, int):
        Year = Date
    else:
        Year = Date.year
        
    if Year <= 2020:
        exchange_rate = 4040
    elif Year == 2021:
        exchange_rate = 4065
    elif Year == 2022 :
        exchange_rate = 4068
    elif Year == 2023:
        exchange_rate = 4085
    elif Year == 2024:
        exchange_rate = 4105
    elif Year == 2025:
        exchange_rate = 4070
    else:
        exchange_rate = 4020
    return(exchange_rate)

    
def listSite(): #create list of ALL site
    querysite = con.execute("SELECT Id_Site FROM Sites ORDER BY Left(Id_Site,1),LENGTH(Id_Site),Id_Site")
    ListSite = querysite.fetchall()
    # if ('X1',) in ListSite:
    #     del(ListSite[ListSite.index(('X1',))])
    return(ListSite)

def listSiteStillActive(Current_date, Date_N_1): 
    """
    Create a list of sites that had any activity over the last year.
    """
    ListSite = listSite()
    ListSiteActive = list(ListSite)
    
    query = con.execute(
        """
        SELECT Sites.Id_Site 
        FROM Sales 
        INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
        WHERE Platform <> 'Dead' AND Old_Platform <> 'Dead'
        AND Month <= %s 
        AND Month > %s 
        GROUP BY Sites.Id_Site 
        HAVING SUM(Total_Sales) > 0 
        ORDER BY Left(Sites.Id_Site, 1), LENGTH(Sites.Id_Site), Sites.Id_Site
        """, 
        [Current_date, Date_N_1]
    )
    ListSiteActive = query.fetchall()
    ListSiteActive = [site for site in ListSiteActive if site[0] not in {'X1', 'X2', 'A3', 'A4', 'A1', 'C12'}]
    
    return ListSiteActive

def listSiteStillActiveFlashReport(Current_date, Date_N_1): #create list of site which had any activity over the last 2 years
    ListSite = listSite()
    ListSiteActive = list(ListSite)
    query = con.execute("SELECT SUM(Number_jugs_village),Id_Site FROM FlashReport WHERE Month <= %s AND Month > %s GROUP BY Id_Site ORDER BY Left(Id_Site,1),LENGTH(Id_Site),Id_Site", [Current_date,Date_N_1])
    allTotal_sale = query.fetchall()
    for i in range(len(ListSite)):
        if ListSite[i][0] == 'X1' or ListSite[i][0] == 'X2':
            del(ListSiteActive[ListSiteActive.index(ListSite[i])])
        else:
            TotalSalesN = list(filter(lambda row: row[1] == ListSite[i][0], allTotal_sale))
            if not TotalSalesN or TotalSalesN[0][0] is (None) or TotalSalesN[0][0] == 0:
                del ListSiteActive[ListSiteActive.index(ListSite[i])]
    return(ListSiteActive)

def listDate(current_date): #create list of date from janv-2017 to this month
    start_date = date(2017,1,1)
    end_date = current_date
    L = [start_date]
    while start_date < end_date:
        start_date += timedelta(monthrange(start_date.year,start_date.month)[1])
        L.append(start_date)
    return(L)

def NewCalculTier(Current_date):

    Date_N_1 = Current_date-relativedelta(months=+12)

    ListSiteDead = con.execute("SELECT Id_Site FROM Sites WHERE Platform = 'Dead'").fetchall()
    ListSiteDead = [i[0] for i in ListSiteDead] or [""]
    ListSiteDead_Tier = [(i,"Dead") for i in ListSiteDead]

    ListSiteClosed = con.execute("""SELECT DISTINCT Sites.Id_Site FROM Sites 
            INNER JOIN Sales ON Sales.Id_Site = Sites.Id_Site 
            WHERE Sites.Id_Site NOT IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month <= %s AND Month > %s) 
            AND Sites.Id_Site IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month < %s)
            AND Sites.Id_Site NOT IN %s""",(Current_date,Date_N_1,Current_date,ListSiteDead)).fetchall()
    ListSiteClosed = [i[0] for i in ListSiteClosed] or [""]
    ListSiteClosed_Tier = [(i,"Closed") for i in ListSiteClosed]

    ListSiteInactive = con.execute("""SELECT DISTINCT Sites.Id_Site FROM Sites 
            INNER JOIN Sales ON Sales.Id_Site = Sites.Id_Site 
            WHERE Sites.Id_Site NOT IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s) 
            AND Sites.Id_Site IN (SELECT DISTINCT Id_Site FROM Sales WHERE Month < %s)
            AND Sites.Id_Site NOT IN %s AND Sites.Id_Site NOT IN %s""",(Current_date,Current_date,ListSiteDead,ListSiteClosed)).fetchall()
    ListSiteInactive = [i[0] for i in ListSiteInactive] or [""]
    ListSiteInactive_Tier = [(i,"Inactive") for i in ListSiteInactive]

    ListSiteNew = con.execute("SELECT DISTINCT Sites.Id_Site FROM Sites INNER JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Month <= %s AND Sites.Id_Site NOT IN %s AND Sites.Id_Site NOT IN %s AND Sites.Id_Site NOT IN %s GROUP BY Sites.Id_Site HAVING COUNT(Total_Sales) <= 3",(Current_date,ListSiteDead,ListSiteClosed,ListSiteInactive)).fetchall()
    ListSiteNew = [i[0] for i in ListSiteNew] or [""]
    ListSiteNew_Tier = [(i,"New") for i in ListSiteNew]

    ListSiteReopen = con.execute("SELECT DISTINCT Sales.Id_Site FROM Sales WHERE Month <= %s AND Month >= %s AND Id_Site NOT IN %s AND Id_Site NOT IN %s AND Id_Site NOT IN %s AND Id_Site NOT IN %s GROUP BY Id_Site HAVING COUNT(Total_Sales)<4",(Current_date,Current_date-relativedelta(months=+3),ListSiteDead,ListSiteClosed,ListSiteInactive,ListSiteNew)).fetchall()
    ListSiteReopen = [i[0] for i in ListSiteReopen] or [""]
    ListSiteReopen_Tier = [(i,"Reopen") for i in ListSiteReopen]

    ListAllNoTierSite = ListSiteDead + ListSiteClosed + ListSiteInactive + ListSiteNew + ListSiteReopen


    ListAllSite = con.execute("SELECT Id_Site,SUM(Total_Sales-WiS_Sales-Bottle_Sales)/SUM(Number_Open_Days) FROM Sales WHERE Month <= %s AND Month > %s AND Id_Site NOT IN %s GROUP BY Id_Site",(Current_date,Date_N_1,ListAllNoTierSite)).fetchall()

    ListSiteST1_Tier = []
    ListSite1_Tier = []
    ListSite2_Tier = []
    ListSite3_Tier = []
    ListSiteST1 = []
    ListSite1 = []
    ListSite2 = []
    ListSite3 = []
    for i in range(len(ListAllSite)):
        if ListAllSite[i][1] > 110:
            ListSiteST1.append((ListAllSite[i][0]))
            ListSiteST1_Tier.append((ListAllSite[i][0],"ST1"))
        elif ListAllSite[i][1] > 70:
            ListSite1.append((ListAllSite[i][0]))
            ListSite1_Tier.append((ListAllSite[i][0],"1"))
        elif ListAllSite[i][1] >= 45:
            ListSite2.append((ListAllSite[i][0]))
            ListSite2_Tier.append((ListAllSite[i][0],"2"))
        elif ListAllSite[i][1] > 0:
            ListSite3.append((ListAllSite[i][0]))
            ListSite3_Tier.append((ListAllSite[i][0],"3"))

    AllSite_Tier = ListSiteDead_Tier + ListSiteClosed_Tier + ListSiteInactive_Tier + ListSiteNew_Tier + ListSiteReopen_Tier + ListSiteST1_Tier + ListSite1_Tier + ListSite2_Tier + ListSite3_Tier

    return(AllSite_Tier, [ListSiteST1,ListSite1,ListSite2,ListSite3,ListSiteNew,ListSiteReopen,ListSiteInactive,ListSiteClosed,ListSiteDead])

def CalculTier(mostRecentDate,Date2,Opened_month, ListSiteActiveGlobal,ListOpenDay): #Return tier with Total_sale last 12 month
    List_tier = []
    query = con.execute("SELECT SUM(Total_Sales),Id_Site FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site", (Date2, date(2004,1,1)))
    allSales = query.fetchall()
    query = con.execute("SELECT SUM(Total_Sales-Bottle_Sales),Id_Site FROM Sales Where Month <= %s AND Month > %s GROUP BY Id_Site", (mostRecentDate,Date2))
    allList_volume = query.fetchall()
    Date_minus_4_month = mostRecentDate - relativedelta(months=+4)
    query = con.execute("SELECT Sum(Total_Sales),Id_Site FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site ", (mostRecentDate,Date_minus_4_month))
    allSales_inactive = query.fetchall()
    query = con.execute("SELECT Project, Id_Site FROM Sales WHERE Month = %s",mostRecentDate)
    allProject = query.fetchall()
    for i in range(len(ListSiteActiveGlobal)):
        Sales = list(filter(lambda row: row[1] == ListSiteActiveGlobal[i][0], allSales))
        if not Sales:
            Sales = [(0,)]
        List_volume = list(filter(lambda row: row[1] == ListSiteActiveGlobal[i][0], allList_volume))

        if not List_volume:
            List_volume = [(0,)]
        Sales_inactive = list(filter(lambda row: row[1] == ListSiteActiveGlobal[i][0], allSales_inactive))
        Project = list(filter(lambda row: row[1] == ListSiteActiveGlobal[i][0], allProject))
        if Project and Project[0][0]:
            if (not Sales[0][0] or Sales[0][0] == 0) and (List_volume[0][0] and List_volume[0][0] > 0):
                List_tier.append('New')
            elif Sales_inactive and Sales_inactive[0][0]:
                List_tier.append('Reopen')
            else:
                List_tier.append('Inactive')

        else:
            if Opened_month[i] != 0 and ListOpenDay[i] ==0:
                ListOpenDay[i] = Opened_month[i] * 29 #fix issue with data in case we have 0 open day but some open month (may be some error for data in year 2017 beginning of commcare)
            if Opened_month[i]<9 and List_volume[0][0] and List_volume[0][0] > 0 and (not Sales_inactive or not Sales_inactive[0][0] or Sales_inactive[0][0] ==0):
                List_tier.append('Inactive')
            elif Opened_month[i] != 0 and List_volume[0][0] and List_volume[0][0]*20/ListOpenDay[i] > 2500:
                List_tier.append("ST1")
            elif Opened_month[i] != 0 and List_volume[0][0] and List_volume[0][0]*20/ListOpenDay[i] > 1700:
                List_tier.append(1)
            elif Opened_month[i] != 0 and List_volume[0][0] and List_volume[0][0]*20/ListOpenDay[i] > 1200:
                List_tier.append(2)
            elif Opened_month[i] != 0 and List_volume[0][0] and List_volume[0][0]*20/ListOpenDay[i] > 0:
                List_tier.append(3)
            else:
                List_tier.append("Closed")
    return(List_tier)

def CalculNombreMoisOuverture(mostRecentDate,Date2,ListSiteActive):
    List_open_month = []
    query = con.execute("SELECT Total_Sales,Id_Site FROM Sales WHERE Month <= %s AND Month > %s", [mostRecentDate,Date2])
    allSales = query.fetchall()
    for i in range(len(ListSiteActive)):
        Sales = list(filter(lambda row: row[1] == ListSiteActive[i][0], allSales))
        Open_Month = 0
        for k in range(len(Sales)):
            if Sales[k][0] and Sales[k][0] > 0:
                Open_Month += 1
        List_open_month.append(Open_Month)
    return(List_open_month)

def listProvPlat(ListSiteActive):
    ListProvince =[]
    ListPlatform=[]
    ListProvinceName = []
    query = con.execute("SELECT Platform,Code_Province,Province,Id_Site FROM Sites")
    allProvPlat = query.fetchall()
    for i in range(len(ListSiteActive)):
        ListProvPlat = list(filter(lambda row: row[3] == ListSiteActive[i][0], allProvPlat))
        if ListProvPlat[0][1] not in ListProvince and ListProvPlat[0][2] != 'Stop' and ListProvPlat[0][2] != 'STOP':
            ListProvince.append(ListProvPlat[0][1])
            ListProvinceName.append(ListProvPlat[0][2])
        if ListProvPlat[0][0] not in ListPlatform and ListProvPlat[0][0] != 'Stop' and ListProvPlat[0][0] != 'STOP':
            ListPlatform.append(ListProvPlat[0][0])
    return(ListPlatform,ListProvince,ListProvinceName)

def Numberdaysopeningyear(mostRecentDate,Date2,ListSiteActive,Open_month):
    L=[]
    query = con.execute("SELECT Number_open_days,Total_Sales,Month,Id_Site FROM Sales Where Month <= %s AND Month > %s", (mostRecentDate,Date2))
    allOpenDays = query.fetchall()
    for k in range(len(ListSiteActive)):

        Nb_days_this_year = 0
        L_open_days = list(filter(lambda row: row[3] == ListSiteActive[k][0], allOpenDays))
        if Date2 > date(2016,12,1): #data after the creation of commcare
            for i in range(len(L_open_days)):
                if not L_open_days or not L_open_days[i][0]:
                    pass
                elif L_open_days[i][0] < 20:
                    Nb_days_this_year += L_open_days[i][0]
                else:
                    Nb_days_this_year += timedelta(monthrange(L_open_days[i][2].year,L_open_days[i][2].month)[1]).days
            L.append(Nb_days_this_year)
        else:
            for i in range(len(L_open_days)):
                Nb_days_this_year += timedelta(monthrange(L_open_days[i][2].year,L_open_days[i][2].month)[1]).days
            L.append(Nb_days_this_year)


    return(L)

def NumberdaysopeningyearHistoricData(mostRecentDate,Date2,ListSiteActive,Open_month): #Used only for the data before Commcare
    L=[]
    query = con.execute("SELECT Number_open_days,Month,Id_Site FROM Sales Where Month <= %s AND Month > %s", (mostRecentDate,Date2))
    allOpenDays = query.fetchall()
    for k in range(len(ListSiteActive)):

        Nb_days_this_year = 0
        L_open_days = list(filter(lambda row: row[2] == ListSiteActive[k][0], allOpenDays))
        for i in range(len(L_open_days)):
            if L_open_days and L_open_days[i][0] and L_open_days[i][0] < 20:
                Nb_days_this_year += L_open_days[i][0]
            else:
                Nb_days_this_year += timedelta(monthrange(L_open_days[i][1].year,L_open_days[i][1].month)[1]).days
        L.append(Nb_days_this_year)
    return(L)

def listAdvisorPerPlatform(Current_date):
    Year = int(Current_date.year)
    if Current_date >= date(Year,7,1):
        N = con.execute("SELECT DISTINCT Platform, Advisor_second_semester, COUNT(Sales.Id_Site) FROM Sites JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Advisor_second_semester <> 'Stop' AND Month = %s AND Sales.Project IS NULL GROUP BY Sites.Platform,Advisor_second_semester",Current_date).fetchall()
    elif Current_date < date(Year,7,1):
        N = con.execute("SELECT DISTINCT Platform, Advisor_first_semester, COUNT(Sales.Id_Site) FROM Sites JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Advisor_first_semester <> 'Stop' AND Month = %s AND Sales.Project IS NULL GROUP BY Sites.Platform,Advisor_first_semester",Current_date).fetchall()

    return(N)

def translate_text(target, text):
    service_account_info = json.load(open(flask.current_app.root_path+'/certs/datastore_writer_appengine.json'))
    credentials = Credentials.from_service_account_info(service_account_info)
    translate_client = translate.Client(credentials=credentials)
    result = translate_client.translate(text, target_language=target)
    return(result["translatedText"])

def ListSiteOverSchoolBudget(date):
    Current_date = datetime.datetime.strptime(date,'%Y-%m').date()
    allList_Site = con.execute("SELECT Sites.Id_Site, NumberSchoolsWinS, SchoolSalesBudget,Platform FROM Sites ").fetchall()
    allDailySales = con.execute("SELECT Id_Site,SUM(WiS_Sales),COUNT(WiS_Sales) FROM DailySales WHERE Month = %s AND WiS_Sales > 0 GROUP BY Id_Site ",Current_date).fetchall()
    MaxOpenDays = 0
    ListMaxOpendays = []
    SiteOverBudget = []
    for j in range(len(allDailySales)):
        if allDailySales[j][2] > MaxOpenDays:
            ListMaxOpendays.append(allDailySales[j][2])
            if len(ListMaxOpendays)>5:
                MaxOpenDays = max(ListMaxOpendays)
                ListMaxOpendays = []
    for i in range(len(allList_Site)):
        Dailysales = list(filter(lambda row: row[0] == str(allList_Site[i][0]), allDailySales)) or [(0,0)]
        List_Site = list(filter(lambda row: row[0] == str(allList_Site[i][0]), allList_Site)) or [(0,0,0)]
        if List_Site[0][2] and Dailysales[0][1]/MaxOpenDays > List_Site[0][2]:
            SiteOverBudget.append([List_Site[0][0],List_Site[0][3],List_Site[0][1],Dailysales[0][1]/MaxOpenDays-List_Site[0][2]])

    return(SiteOverBudget)

def ConsumableType():
    con = db.pool.connect()
    Item = con.execute('SELECT DISTINCT Item FROM Consumable').fetchall()
    ListItem = [i[0] for i in Item]
    ListBottle = ["401002","401001"]
    for i in ListBottle:
        ListItem.remove(i)
    return(ListItem,ListBottle)

def ListIntervention():
    ListProblem = ["Power Failure","Solar Failure","RT_plan","Alert_WQ",
    "Machine_Not_Work","Water_Quality","បញ្ហាប្រភពទឹក/Water Source",
    "បញ្ហាចម្រោះបឋម/Pre-treatment Problem","បញ្ហាប្រភពអគ្គិសនី&ប្រភពទឹក/Electricity and Water Source",
    "បញ្ហាប្រព័ន្ធយូវី/UV System Problem","ត្រួតពិនិត្យស្ថានីយ/Site Inspection","ប្រព័ន្ធសូឡារ/Solar System","Other",
    "ការវាយតំលៃស្ថានីយ៏/Site Assessment","ការឆែកស្ថានីយ័/Site Routine","ប្រពន្ធភ្លើង/Grid","បញ្ហាម៉ូទ័រ/Motor",
    "សូឡា/Sola","យូវី/UV","បញ្ហាប្រភពទឹក/Water Source","ការសំអាត/Pre-treatment","ប្រពន្ធ័ចំរោះ/Micro filter",
    "បណ្តុះបណ្តាល/Training","WQ_Alert","ប្រពន្ធ័សំលាប់មេរោគ/Treated Water"]

    ListQualityIntervention = ["Water_Quality","បញ្ហាប្រភពទឹក/Water Source"]
    ListAlertWQ = ["Alert_WQ","WQ_Alert"]
    ListPlannedTechnical = ["RT_plan","ត្រួតពិនិត្យស្ថានីយ/Site Inspection","ការវាយតំលៃស្ថានីយ៏/Site Assessment","ការឆែកស្ថានីយ័/Site Routine",
                            ]
    ListTechnicalIntervention = list(set(ListProblem) - set(ListQualityIntervention)- set(ListAlertWQ))
    ListTechnicalInterventionNotPlanned = list(set(ListProblem) - set(ListQualityIntervention)- set(ListAlertWQ) - set(ListPlannedTechnical))
    return(ListTechnicalIntervention,ListQualityIntervention,ListAlertWQ,ListPlannedTechnical,ListTechnicalInterventionNotPlanned)

def isFloat(toCheck):
    try:
        Number = float(toCheck)
        return Number
    except:
        return toCheck
    
def Test_is_float(toCheck):
    try:
        Number = float(toCheck)
        return True
    except:
        return False
    
def QualityFailure(ResultEcoli,ResultColiform):
    if (Test_is_float(ResultEcoli) and isFloat(ResultEcoli) > 0) or ResultEcoli == 'TNTC':
        return(3)
    elif (Test_is_float(ResultColiform) and isFloat(ResultColiform) > 100) or ResultColiform == 'TNTC':
        return(2)
    elif (Test_is_float(ResultColiform) and isFloat(ResultColiform) > 0):
        return(1)
    else:
        return(0)
    
def CheckTechnicalItem(IdItem):
    listTechnicalItem = ["112001","112002","113001","113002",
                        "113003","212007","212010","208004","208005",
                         "208003","208006","208007","208008",
                         "208009","208010","208011","208012","208014",
                         "501006"]
    if IdItem in listTechnicalItem:
        return(True)
    else:
        return(False)
    
def ConsumableForOFD():
    Item = ["401009","401004","401003","401008"]
    Bottles = ["401002","401001"]
    Total = Item + Bottles
    return(Item,Bottles,Total)
    
def CalculBeneficiaries(Botday):
    Beneficiaries = Botday * 30
    return(Beneficiaries)

def CategoryExpenses():
    Category_expenses = ["production","salary","delivery","contribution","investment","technical"]
    return(Category_expenses)

def get_site_tier(site_id, current_date):
    """Return tier for a single site quickly.

    Tier logic replicates `NewCalculTier` ordering but restricted to one site:
    Order of evaluation:
      Dead -> Closed -> Inactive -> New -> Reopen -> Performance tiers (ST1,1,2,3)

    Performance tiers based on average (Total_Sales - WiS_Sales - Bottle_Sales) / Number_Open_Days
      >110 => ST1
      >70  => 1
      >=45 => 2
      >0   => 3
      else Closed

    Arguments:
      site_id (str): Site identifier.
      current_date (date | str): Reference month (YYYY-MM or date object). If str 'YYYY-MM' parsed.

    Returns:
      str: Tier label.
    """
    # Normalize date
    if isinstance(current_date, str):
        # Accept 'YYYY-MM' or 'YYYY-MM-01'
        try:
            if len(current_date) == 7:
                current_date = datetime.date.fromisoformat(current_date + '-01')
            else:
                current_date = datetime.date.fromisoformat(current_date)
        except Exception:
            raise ValueError("current_date must be 'YYYY-MM' or ISO date string")
    elif isinstance(current_date, datetime.datetime):
        current_date = current_date.date()
    elif not isinstance(current_date, date):
        raise TypeError("current_date must be date, datetime, or YYYY-MM string")

    date_n_1 = current_date - relativedelta(months=+12)
    date_minus_3 = current_date - relativedelta(months=+3)

    # Single round-trip: fetch platform, counts, and performance aggregates
    row = con.execute(
        """
        SELECT s.Platform,
               SUM(CASE WHEN sa.Month <= %s AND sa.Month > %s THEN 1 ELSE 0 END) AS last_12_months_count,
               SUM(CASE WHEN sa.Month < %s THEN 1 ELSE 0 END) AS any_previous_sales,
               SUM(CASE WHEN sa.Month = %s THEN 1 ELSE 0 END) AS current_month_sales,
               SUM(CASE WHEN sa.Month <= %s THEN 1 ELSE 0 END) AS lifetime_months_count,
               SUM(CASE WHEN sa.Month <= %s AND sa.Month >= %s THEN 1 ELSE 0 END) AS recent_3_months_count,
               COALESCE(SUM(CASE WHEN sa.Month <= %s AND sa.Month > %s THEN (sa.Total_Sales - sa.WiS_Sales - sa.Bottle_Sales) END), 0) AS volume,
               COALESCE(SUM(CASE WHEN sa.Month <= %s AND sa.Month > %s THEN sa.Number_Open_Days END), 0) AS open_days
        FROM Sites s
        LEFT JOIN Sales sa ON sa.Id_Site = s.Id_Site
        WHERE s.Id_Site = %s
        GROUP BY s.Platform
        """,
        (
            current_date, date_n_1,
            current_date,
            current_date,
            current_date,
            current_date, date_minus_3,
            current_date, date_n_1,
            current_date, date_n_1,
            site_id,
        ),
    ).fetchone()

    if not row:
        raise ValueError(f"Site '{site_id}' not found")

    (
        platform,
        last_12_months_count,
        any_previous_sales,
        current_month_sales,
        lifetime_months_count,
        recent_3_months_count,
        volume,
        open_days,
    ) = row

    if platform == 'Dead':
        return 'Dead'

    # Closed: no sales in last 12 months but had some before current_date
    if last_12_months_count == 0 and any_previous_sales > 0:
        return 'Closed'

    # Inactive: had previous sales but none this current month (and not closed)
    if current_month_sales == 0 and any_previous_sales > 0:
        return 'Inactive'

    # New: total count of months with records up to current_date is <= 3
    if lifetime_months_count <= 3:
        return 'New'

    # Reopen: some activity within last 3 months but < 4 months in that window
    if recent_3_months_count > 0 and recent_3_months_count < 4:
        return 'Reopen'

    # Performance tiers over last 12 months
    # Ensure consistent numeric types (avoid float/Decimal division issues)
    try:
        avg_per_day = (float(volume) / float(open_days)) if open_days and float(open_days) > 0 else 0
    except Exception:
        avg_per_day = 0

    if avg_per_day > 110:
        return 'ST1'
    elif avg_per_day > 70:
        return '1'
    elif avg_per_day >= 45:
        return '2'
    elif avg_per_day > 0:
        return '3'
    else:
        return 'Closed'

if __name__ == '__main__':
    print(ListSiteOverSchoolBudget(date(2022,8,1)))
