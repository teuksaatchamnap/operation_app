import datetime
from datetime import date, datetime
from dateutil.relativedelta import *
import db
import tempfile
from pathlib import Path
from monthlyreport.Functionutils import NewCalculTier,listSite, listSiteStillActive, CalculTier, Numberdaysopeningyear, CalculNombreMoisOuverture, Numberdaysopeningyear, listProvPlat, listDate
from monthlyreport.ExcelActivityIndicator import LaunchExcelCreationActivityIndicator
from monthlyreport.ExcelKPI import LaunchExcelCreationKPI
from monthlyreport.ExcelF2F import LaunchExcelCreationF2F
from monthlyreport.ExcelAdvisors import LaunchExcelCreationAdvisor
from monthlyreport.ExcelFlashReport import LaunchExcelCreationFlashReport
from monthlyreport.ExcelSiteAlert import LaunchExcelCreationAlert
from monthlyreport.ExcelConsumables import LaunchExcelCreationOrder,LaunchExcelCreationConsumableFollowup
from monthlyreport.ExcelClosure import LaunchExcelCreationClosure
from monthlyreport.ExcelFinanceReport import LaunchExcelFinanceReport
from monthlyreport.ExcelSiteAnalysis import LaunchExcelCreationSiteAnalysis
from monthlyreport.ExcelTechnicalIntervention import LaunchExcelCreationTechnical
from monthlyreport.ExcelQuality import LaunchExcelCreationQuality
from monthlyreport.Management_Dashboard import LaunchExcelCreationManagementDashboard
from monthlyreport.ProvinceReport import ProvinceReport
from monthlyreport.ExcelOFD import LaunchExcelCreationOFD
from monthlyreport.Functionutils import exchange_rate_year
from carbonreport.CarbonReportingEcoAct import LaunchExcelCreationCarbonEcoAct
from monthlyreport.ExcelSalesTeamPerformance import LaunchExcelSalesTeamPerformance
from monthlyreport.ExcelVehicleDeliveryImpact import LaunchExcelVehicleDeliveryImpact
from monthlyreport.CreateAdvisorBonus import create_template_excel

con = db.pool.connect()

def CreateSalesTeamPerformance(Date):
    Current_date = Date
    LaunchExcelSalesTeamPerformance(Current_date)


def CreateVehicleDeliveryImpact(Date):
    Current_date = Date
    LaunchExcelVehicleDeliveryImpact(Current_date)


def CreateAdvisorBonus(Date):
    """Generate the Advisor Bonus workbook in the temp directory."""
    Current_date = date(Date.year, Date.month, 1)
    Year = str(Current_date.year)
    Month = str(Current_date.month).zfill(2)
    output_path = Path(tempfile.gettempdir()) / f"AdvisorBonus {Year}-{Month}.xlsx"
    create_template_excel(output_path=output_path, reference_month=Current_date)
    return str(output_path)


def CreateConsumableOrder(Date,First_date = 0):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    if First_date == 0:
        LaunchExcelCreationOrder(exchange_rate,Current_date)
    else:
        LaunchExcelCreationOrder(exchange_rate,Current_date,First_date)

def CreateConsumableFollowup(Date):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    LaunchExcelCreationConsumableFollowup(exchange_rate,Current_date)
    
def CreateManagementDashboard(Date):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    LaunchExcelCreationManagementDashboard(Current_date,exchange_rate)

def CreateTechnicalDashboard(Date):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    LaunchExcelCreationTechnical(Current_date,exchange_rate)

def CreateQualityDashboard(Date):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    LaunchExcelCreationQuality(Current_date)

def CreateSiteAnalysis(Date,ListSite):
    con = db.pool.connect()
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    Date_N_1 = Current_date - relativedelta(months=+12)
    if ListSite == None:
        ListSite = con.execute("SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s",Current_date).fetchall()
    ListTier = NewCalculTier(Current_date)[0]
    LaunchExcelCreationSiteAnalysis(Current_date,ListSite,ListTier,exchange_rate)

def CreateActivityIndicators(Date):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    ListTier = NewCalculTier(Current_date)[0]
    LaunchExcelCreationActivityIndicator(Current_date,ListTier,exchange_rate)

def CreateExcelClosure(Date):
    Current_date = Date
    LaunchExcelCreationClosure(Current_date)

def CreateFinanceReport(Date):
    Current_date = Date
    Tier = NewCalculTier(Date)[0]
    exchange_rate = exchange_rate_year(Current_date)
    LaunchExcelFinanceReport(Current_date,Tier,exchange_rate)

def CreateSiteAlert(Date):
    ListDate = listDate(Date)
    Current_date = ListDate[-1]
    Date_N_1 = Current_date- relativedelta(months=+12)
    exchange_rate = exchange_rate_year(Current_date)
    ListSiteActive = listSiteStillActive(Current_date,Date_N_1)
    LaunchExcelCreationAlert(Current_date,ListSiteActive)

def CreateF2F(Date,Platform):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    ListTier = NewCalculTier(Current_date)[0]

    LaunchExcelCreationF2F(Current_date,ListTier,Platform,exchange_rate)

def CreateFlashReport(Date,Period="EndMonth"):
    LaunchExcelCreationFlashReport(Date,Period)

def CreateProvince(Date):
    Current_date = Date
    exchange_rate = exchange_rate_year(Current_date)
    ProvinceReport(Current_date,exchange_rate)

def CreateOFD(Date,Platform):
    Tier = NewCalculTier(Date)[0]
    exchange_rate = exchange_rate_year(Date)
    LaunchExcelCreationOFD(Date,exchange_rate,Tier,Platform)

def CreateCarbonReportEcoAct(Date):

    exchange_rate = exchange_rate_year(Date)
    LaunchExcelCreationCarbonEcoAct(Date,exchange_rate)


previousTime = datetime.now().timestamp()
def printTime(label):
    global previousTime
    now = datetime.now().timestamp()
    print(label, round(now-previousTime, 3), "s")
    previousTime = now

if __name__ == '__main__':
    #CreateVolume(date(2019,12,1))
    CreateF2F(date(2022,4,1),["PP",'BTB',"KC","SR"])
