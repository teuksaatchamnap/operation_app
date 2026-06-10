import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta
from calendar import monthrange
import db
from dateutil.relativedelta import *
from google.cloud import translate_v2 as translate
import os

con = db.pool.connect()


def listSite(): #create list of ALL site
    querysite = con.execute("SELECT Id_Site FROM Sites ORDER BY Left(Id_Site,1),LENGTH(Id_Site),Id_Site")
    ListSite = querysite.fetchall()
    # if ('X1',) in ListSite:
    #     del(ListSite[ListSite.index(('X1',))])
    return(ListSite)

def listSiteStillActive(Current_date, Date_N_1): #create list of site which had any activity over the last 2 years
    ListSite = listSite()
    ListSiteActive = list(ListSite)
    query = con.execute("SELECT SUM(Total_Sales),Sites.Id_Site FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Last_Tier <> 'Dead' AND Month <= %s AND Month > %s GROUP BY Sites.Id_Site ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site", [Current_date,Date_N_1])
    allTotal_sale = query.fetchall()
    for i in range(len(ListSite)):
        if ListSite[i][0] == 'X1' or ListSite[i][0] == 'X2':
            del(ListSiteActive[ListSiteActive.index(ListSite[i])])
        else:
            TotalSalesN = list(filter(lambda row: row[1] == ListSite[i][0], allTotal_sale))
            if not TotalSalesN or TotalSalesN[0][0] is (None) or TotalSalesN[0][0] == 0:
                del ListSiteActive[ListSiteActive.index(ListSite[i])]
    return(ListSiteActive)

def listSiteStillActiveFlashReport(Current_date, Date_N_1): #create list of site which had any activity over the last 2 years
    ListSite = listSite()
    ListSiteActive = list(ListSite)
    query = con.execute("SELECT SUM(Number_jugs_village),Sites.Id_Site,Project FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site WHERE Platform <> 'Dead' AND (Platform <> 'Stop' OR (Platform = 'Stop' AND Project = 1)) AND Month <= %s AND Month > %s GROUP BY Sites.Id_Site ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site", [Current_date,Date_N_1])
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
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    translate_client = translate.Client()

    # if isinstance(text, six.binary_type):
    #     text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
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
        # print(List_Site)
        # print(Dailysales)
        if List_Site[0][2] and Dailysales[0][1]/MaxOpenDays > List_Site[0][2]:
            SiteOverBudget.append([List_Site[0][0],List_Site[0][3],List_Site[0][1],Dailysales[0][1]/MaxOpenDays-List_Site[0][2]])

    return(SiteOverBudget)

if __name__ == '__main__':
    print(ListSiteOverSchoolBudget(date(2022,8,1)))
