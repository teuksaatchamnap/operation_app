import monthlyreport.CreateExcels as CreateExcels
from datetime import date,datetime
import tempfile
import db
from calendar import monthrange
from dateutil.relativedelta import *
import calendar
import json
import mail
import monthlyreport.TeukSaatIndicatorsEmail as TeukSaatIndicatorsEmail
import traceback

con = db.pool.connect()

def safeRound(value, digits=0):
    if value is None:
        return 0
    return round(value, digits)

def SendMailTest():
    try:
        mail.send_email(
            to_emails=['jo.faucher@1001fontaines.com'],
            subject='Test Email',
            html_content='<h1>This is a test</h1><p>hello</p>'
        )
    except Exception as e:
        print(e.message)

def SendMailReporting():
    datej = date(datetime.today().year,datetime.today().month, 1) - relativedelta(months=+1)
    datej_lastyear = date(datej.year - 1,datej.month,1)
    ListPlatform = con.execute("SELECT Code_Platform FROM Platform").fetchall()
    Platform = [i[0] for i in ListPlatform]
    CreateExcels.CreateActivityIndicators(datej)
    CreateExcels.CreateF2F(datej,Platform)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Requete_Ldaythisyear = con.execute("SELECT SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days)*20 FROM Sales WHERE Month =%s",datej).fetchall()
    Ldaythisyear = Requete_Ldaythisyear[0][0]

    Requete_Ldaylastyear = con.execute("SELECT SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days)*20 FROM Sales WHERE Month =%s",datej_lastyear).fetchall()
    Ldaylastyear = Requete_Ldaylastyear[0][0]

    query = con.execute("SELECT SUM(Total_Sales-Bottle_Sales), SUM(WiS_Sales), Count(Total_Sales) FROM Sales WHERE Total_Sales>0 AND Month = %s", datej)
    all_sales_t_month = query.fetchall()

    Jugs_sold_t_month = all_sales_t_month[0][0]
    Wins_sold_t_month = all_sales_t_month[0][1]
    Site_active_t_month = all_sales_t_month[0][2]

    query = con.execute("SELECT SUM(Total_Sales-Bottle_Sales), SUM(WiS_Sales), Count(Total_Sales) FROM Sales WHERE Total_Sales>0 AND Month = %s", datej_lastyear)
    all_sales_l_year = query.fetchall()

    Jugs_sold_l_year = all_sales_l_year[0][0]
    Wins_sold_l_year = all_sales_l_year[0][1]
    Site_active_l_year = all_sales_l_year[0][2]

    Requete_Ldaythisyear_new = con.execute("SELECT SUM(Total_Sales-Bottle_Sales)/SUM(Number_Open_Days)*20 FROM Sales JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Month =%s AND (Last_Tier = 'New' OR Last_Tier = 'Reopen')",datej).fetchall()
    Ldaythisyear_new = Requete_Ldaythisyear_new[0][0]

    query = con.execute("SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s",(datej))
    ListSiteactifmonth = [row[0] for row in query.fetchall()]
    query = con.execute("SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s",(datej-relativedelta(months=+1)))
    ListSiteactiflastmonth = [row[0] for row in query.fetchall()]

    Site_no_actif_this_month = str(set(ListSiteactiflastmonth).difference(set(ListSiteactifmonth)))
    if Site_no_actif_this_month == "set()":
        No_Actif = 0
    else:
        No_Actif = len(Site_no_actif_this_month.split(","))


    Name_month = calendar.month_name[datej.month]
    Last_year = int(Year) - 1
    Name_last_month = calendar.month_name[(datej-relativedelta(months=+1)).month]

    Message = """<p> Please find attached the monthly reporting for the month of %s %s. 
    </p> <p> The key figures to have in mind are the following: <br /> 
    - <b>Average of %s L/day </b> vs %s L/day in %s %s. <br /> 
    - <b> %s bottles delivered </b> (including <b> %s for clients </b> and <b> %s for the Water in School program </b>) vs %s in %s %s (including %s for clients and %s for the Water in School program). <br />
    -<b> %s sites active </b> in %s %s vs %s in %s %s. <br /> 
    -<b> ‘New’ and ‘Reopen’ sites </b> (opened for less than 3 months) had an <b> average of %s L/day. </b> <br /> 
    - <b>%s sites </b>were opened in %s but <b> closed in %s %s : %s. </b> </p>"""%(Name_month,int(Year),safeRound(Ldaythisyear),safeRound(Ldaylastyear),Name_month,Last_year,safeRound(Jugs_sold_t_month),safeRound(Jugs_sold_t_month)-safeRound(Wins_sold_t_month),safeRound(Wins_sold_t_month),safeRound(Jugs_sold_l_year),Name_month,Last_year,safeRound(Jugs_sold_l_year)-safeRound(Wins_sold_l_year),safeRound(Wins_sold_l_year),int(Site_active_t_month),Name_month,int(Year),int(Site_active_l_year),Name_month,Last_year,safeRound(Ldaythisyear_new),No_Actif,Name_last_month,Name_month,int(Year),Site_no_actif_this_month)

    Email = con.execute("SELECT email from users WHERE permissions like '%%receive_monthly_report%%'").fetchall()

    ListFile = [
        tempfile.gettempdir() + '/Activity Indicators ' + Year + '-' + Month + '.xlsx',
        tempfile.gettempdir() + '/F2F ' + Year + '-' + Month + '.xlsm'
    ]
    try:
        mail.send_email(
            to_emails=[Email[i][0] for i in range(len(Email))],
            #to_emails=['axel.liber@1001fontaines.com','quentin.pelletier@1001fontaines.com','fr.jaquenoud@gmail.com','ju.ancele@1001fontaines.com','am.muret@1001fontaines.com','amandine.chaussinand@1001fontaines.com','eva.leneveu@1001fontaines.com',"stephanie.s@teuksaat1001.com",'touch.i@teuksaat1001.com','sota.h@teuksaat1001.com','alise.andre@1001fontaines.com','jeanpierremartial1948@gmail.com','veasna.ch@teuksaat1001.com','chandara.r@teuksaat1001.com','saly.s@teuksaat1001.com','romain.joly@1001fontaines.com','  '],
            subject='KH Monthly Reporting ' + Year + '-' + Month,
            html_content=Message,
            attachments=ListFile
        )
    except Exception as e:
        print(e.message)


def SendMailTeukSaatIndicatorsEmail():
    # Sends an HTML email equivalent to the IndicatorsTeukSaat Excel tab,
    # with Like-for-Like + sites with >3 operators added.
    try:
        TeukSaatIndicatorsEmail.send_teuksaat_indicators_email()
    except Exception as e:
        print("SendMailTeukSaatIndicatorsEmail failed:")
        print(traceback.format_exc())


def SendMailSalesTeamPerformance():
    datej = date(datetime.today().year, datetime.today().month, 1) - relativedelta(months=+1)
    CreateExcels.CreateSalesTeamPerformance(datej)

    Year = str(datej.year)
    Month = str(datej.month).zfill(2)
    subject = 'SalesTeam Performance ' + Year + '-' + Month
    ListFile = [tempfile.gettempdir() + '/SalesTeam Performance ' + Year + '-' + Month + '.xlsx']

    MailROM = con.execute("SELECT DISTINCT Mail_ROM FROM Platform",).fetchall()
    MailROM = [i[0] for i in MailROM] 
    try:
        mail.send_email(
            to_emails=["axel.liber@1001fontaines.com","amandine.chaussinand@1001fontaines.com","rom@teuksaat1001.com","sousdey.y@teuksaat1001.com"],
            subject=subject,
            html_content='Please find attached the SalesTeam Performance report.',
            attachments=ListFile,
        )
    except Exception as e:
        print(e)


def SendMailAdvisorBonusQuarterly():
    """Send Advisor Sales Recap on the 13th, only for quarter-end months (Mar/Jun/Sep/Dec)."""
    datej = date(datetime.today().year, datetime.today().month, 1) - relativedelta(months=+1)
    if datej.month not in (3, 6, 9, 12):
        print(f"Skip AdvisorBonus: {datej} is not quarter end")
        return

    CreateExcels.CreateAdvisorBonus(datej)

    Year = str(datej.year)
    Month = str(datej.month).zfill(2)
    subject = f"Advisor Bonus {Year}-{Month}"
    ListFile = [tempfile.gettempdir() + f"/AdvisorBonus {Year}-{Month}.xlsx"]

    try:
        mail.send_email(
            to_emails=[
                'amandine.chaussinand@1001fontaines.com',
                'axel.liber@1001fontaines.com',
            ],
            subject=subject,
            html_content='Please find attached the Advisor Bonus.',
            attachments=ListFile,
        )
    except Exception as e:
        print(e)

def SendMailFlashReport(Period):
    con = db.pool.connect()
    if Period == 'EndMonth':
        datej = date(datetime.today().year,datetime.today().month, 1) - relativedelta(months=+1)
    else:
        datej = date(datetime.today().year,datetime.today().month, 1)
    
    Email = con.execute("SELECT email from users WHERE permissions like '%%receive_flash_report%%'").fetchall()
    CreateExcels.CreateFlashReport(datej,Period)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    if Period == "EndMonth":
        Object='KH Flash Report ' + Year + '-' + Month
        ListFile = [tempfile.gettempdir() + '/Flash report ' + Year + '-' + Month + '.xlsx']
    else:
        Object='KH Mid Flash Report ' + Year + '-' + Month + '-15'
        ListFile = [tempfile.gettempdir() + '/Mid Flash report ' + Year + '-' + Month + '-15'+'.xlsx']

    try:
        mail.send_email(
            #to_emails=["chamnap.keo@teuksaat1001.com", "axel.liber@1001fontaines.com"],
            to_emails=[Email[i][0] for i in range(len(Email))],
            subject=Object,
            #html_content="Here is the list of recipient:<br>" + "<br>".join([Email[i][0] for i in range(len(Email))]),
            html_content='Please Find attached last month Flash Report',
            attachments=ListFile
        )
    except Exception as e:
        print(e.message)
    con.execute("UPDATE FlashReport SET AlreadySentFlash = True WHERE Month = %s AND Period = %s",(datej,Period))
    print("Sending")

def SendMailSiteClosure(site, user, closureDate, reason, description):
    con = db.pool.connect()
    Email = con.execute("SELECT email from users WHERE permissions like '%%receive_site_closure_email%%'").fetchall()    
    try:
        mail.send_email(
            to_emails=[Email[i][0] for i in range(len(Email))],
            subject='Site closure notification : ' + site,
            html_content='<p>You receive this email because user '+user+' has closed the site '+site+'.</p><p>Closure date : '+closureDate+'</p><p>Reason for closure: '+reason+'.</p><p> Description : '+description+'</p>')
    except Exception as e:
        print(e.message)

def SendMailSiteReopen(site,reopeningDate,user):
    con = db.pool.connect()
    Email = con.execute("SELECT email from users WHERE permissions like '%%receive_site_closure_email%%'").fetchall()
    try:
        mail.send_email(
            to_emails=[Email[i][0] for i in range(len(Email))],
            subject='Site reopen notification : ' + site,
            html_content='<p>You receive this email because user '+user+' has reopen the site '+site+'.on.'+reopeningDate+'.</p>')
    except Exception as e:
        print(e.message)

def SendMailAlertSite():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    CreateExcels.CreateSiteAlert(datej)
    CreateExcels.CreateExcelClosure(datej)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    ListFile = [
        tempfile.gettempdir() + '/Alert Site Report ' + Year + '-' + Month + '.xlsx',
        tempfile.gettempdir() + '/Site Closing Report ' + Year + '-' + Month + '.xlsx'
    ]
    try:
        mail.send_email(
            to_emails=['axel.liber@1001fontaines.com','quentin.pelletier@1001fontaines.com','amandine.chaussinand@1001fontaines.com','stephanie.s@teuksaat1001.com','chamnap.keo@teuksaat1001.com'],
            subject='Site Alert Report ' + Year + '-' + Month,
            html_content='Find attached two documents highlighting the sites that are having difficulties',
            attachments=ListFile            
        )
    except Exception as e:
        print(e)

def SendMailFinanceReport():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    Email = con.execute("SELECT email from users WHERE permissions like '%%receive_collection_rate%%'").fetchall()
    CreateExcels.CreateFinanceReport(datej)
    CreateExcels.CreateConsumableFollowup(datej)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)

    ListFile = [
        tempfile.gettempdir() + '/Finance Report ' + Year + '-' + Month + '.xlsm',
        tempfile.gettempdir() + '/Consumable Follow Up ' + Year + '-' + Month +'.xlsx'
    ]
    try:
        mail.send_email(
            to_emails=[Email[i][0] for i in range(len(Email))],
            subject='Finance Report ' + Year + '-' + Month,
            html_content='Find attached the Finance Reports',
            attachments=ListFile)
    except Exception as e:
        print(e.message)

def SendMailOFD():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    ListPlatform = con.execute("SELECT Code_Platform FROM Platform").fetchall()
    Platform = [i[0] for i in ListPlatform]
    CreateExcels.CreateOFD(datej,Platform)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    ListFile = [tempfile.gettempdir() + '/OFD ' + Year + '-' + Month + '.xlsm']
    try:
        mail.send_email(
            #['amandine.chaussinand@1001fontaines.com','ju.ancele@1001fontaines.com','quentin.pelletier@1001fontaines.com',]
            to_emails=['amandine.chaussinand@1001fontaines.com','quentin.pelletier@1001fontaines.com','axel.liber@1001fontaines.com','reaksmey.p@teuksaat1001.com','chamnap.keo@teuksaat1001.com','geklorng.kh@teuksaat1001.com'],
            subject='OFD ' + Year + '-' + Month,
            html_content='Find attached the OFD for this month',
            attachments=ListFile)
    except Exception as e:
        print(e.message)

def SendMailManagementDashboardBeforeFinance():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    CreateExcels.CreateManagementDashboard(datej)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    ListFile = [tempfile.gettempdir() + '/Mngt Dashboard TS ' + Year + '-' + Month + '.xlsx']
    try:
        mail.send_email(
            #['amandine.chaussinand@1001fontaines.com','ju.ancele@1001fontaines.com','quentin.pelletier@1001fontaines.com',]
            to_emails=['amandine.chaussinand@1001fontaines.com','quentin.pelletier@1001fontaines.com','axel.liber@1001fontaines.com','reaksmey.p@teuksaat1001.com','chamnap.keo@teuksaat1001.com'],
            subject='Mngt Dashboard ' + Year + '-' + Month,
            html_content='Find attached the Management Dashboard for this month !! Data from Finance team are missing so there might be some error regarding the debt situation and the consummables sales.',
            attachments=ListFile)
    except Exception as e:
        print(e.message)

def SendMailManagementDashboardAfterFinance():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    CreateExcels.CreateManagementDashboard(datej)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    ListFile = [tempfile.gettempdir() + '/Mngt Dashboard TS ' + Year + '-' + Month + '.xlsx']
    try:        
        mail.send_email(
            #['amandine.chaussinand@1001fontaines.com','ju.ancele@1001fontaines.com','quentin.pelletier@1001fontaines.com',]
            to_emails=['amandine.chaussinand@1001fontaines.com','quentin.pelletier@1001fontaines.com','axel.liber@1001fontaines.com','reaksmey.p@teuksaat1001.com','chamnap.keo@teuksaat1001.com','pa.terisse@1001fontaines.com'],
            subject='Mngt Dashboard ' + Year + '-' + Month,
            html_content='Find attached the Management Dashboard for this month',
            attachments=ListFile)
    except Exception as e:
        print(e.message)

def SendMailQualityAlert(Samplejson):
    Sample = json.load(Samplejson)
    con=db.pool.connect()
    Advisor = con.execute("SELECT Advisor FROM Sites WHERE Id_Site = %s",Sample['site']).fetchall()
    try:
        mail.send_email(
            to_emails=['axel.liber@1001fontaines.com','chamnap.keo@teuksaat1001.com'],
            subject='quality alert on site %s'%(Sample['site']),
            html_content='<p>Here are the analysis result :</p>'
                            '<p>- Site : %s </p>'
                            '<p>- Sample Date : %s </p>'
                            '<p>- Analysis Date : %s </p>'
                            '<p>- Contamination level bottle : %s </p>'
                            '<p>- Coliform bottle : %s </p>'
                            '<p>- Ecoli bottle : %s </p>'
                            '<p>- Contamination level bottle : %s </p>'
                            '<p>- Coliform machine : %s </p>'
                            '<p>- Ecoli machine : %s </p>'
                            '<p>- Comment : %s</p>'
                            '<p>- Advisor in charge : %s </p>'
                            '<p>- Click here to acess the quality app : <a href="url">%s</a> </p>'%(Sample['site'],Sample['sampleDate'],Sample['analysisDate'],Sample['contaminationLevelBottle'],Sample['totalColiformBottle'],Sample['escherichiaBottle'],Sample['contaminationLevelMachine'],Sample['totalColiform'],Sample['escherichia'],Sample['comment'],Advisor[0][0],'https://sims-2-140009.appspot.com/quality/'))
    except Exception as e:
        print(e.message)

def SendMailROM():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    Platform = con.execute("SELECT Code_Platform FROM Platform").fetchall()
    CreateExcels.CreateActivityIndicators(datej)
    for i in range(len(Platform)):
        CreateExcels.CreateF2F(datej,[Platform[i][0]])
        MailROM = con.execute("SELECT Mail_ROM FROM Platform WHERE Code_Platform = %s",(Platform[i][0],)).fetchall()
        MailROM = [i[0] for i in MailROM]
        Year = str(datej.year)
        Month = datej.month
        if Month < 10:
            Month = '0' + str(Month)
        else:
            Month = str(Month)
        
        ListFile = [tempfile.gettempdir() + '/F2F %s '%(Platform[i][0]) + Year + '-' + Month + '.xlsm', tempfile.gettempdir() + '/Activity Indicators ' + Year + '-' + Month + '.xlsx']
        try:
           mail.send_email(
            to_emails=['axel.liber@1001fontaines.com','amandine.chaussinand@1001fontaines.com','chamnap.keo@teuksaat1001.com'] + MailROM,
            subject='F2F %s '%(Platform[i][0]) + Year + '-' + Month,
            html_content='Find attached the activity indicators and the face to face for %s this month.'%(Platform[i][0]),
            attachments=ListFile)
        except Exception as e:
            print(e.message)

def SendMailROMOFD():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    Platform = con.execute("SELECT Code_Platform FROM Platform").fetchall()
    for i in range(len(Platform)):
        CreateExcels.CreateOFD(datej,[Platform[i][0]])
        MailROM = con.execute("SELECT Mail_ROM FROM Platform WHERE Code_Platform = %s",(Platform[i][0],)).fetchall()
        MailROM = [i[0] for i in MailROM]
        Year = str(datej.year)
        Month = datej.month
        if Month < 10:
            Month = '0' + str(Month)
        else:
            Month = str(Month)
       
        ListFile = [tempfile.gettempdir() + '/OFD %s '%(Platform[i][0]) + Year + '-' + Month + '.xlsm']
        try:
            mail.send_email(
                to_emails=['axel.liber@1001fontaines.com','amandine.chaussinand@1001fontaines.com','chamnap.keo@teuksaat1001.com'] + MailROM,
                subject='OFD %s '%(Platform[i][0]) + Year + '-' + Month,
                html_content='Find attached the Operational Financial Dashboard for %s this month.'%(Platform[i][0]),
                attachments=ListFile)
        except Exception as e:
            print(e.message)

def SendMailProvince():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    CreateExcels.CreateProvince(datej)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)

    ListFile = [tempfile.gettempdir() + '/Province Report ' + Year + '-' + Month +'.xlsm']    
    try:
        mail.send_email(
            #to_emails=['axel.liber@1001fontaines.com'],
            to_emails=['axel.liber@1001fontaines.com','sophors.n@teuksaat1001.com','amandine.chaussinand@1001fontaines.com','farida.m@teuksaat1001.com','chamnap.keo@teuksaat1001.com'],
            subject='Province Report ' + Year + '-' + Month,
            html_content='Please find attached the Province report.',
            attachments=ListFile)
    except Exception as e:
        print(e.message)

def SendMailTechnical():
    datej = date(datetime.today().year,datetime.today().month,1)- relativedelta(months=+1)
    CreateExcels.CreateTechnicalDashboard(datej)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    MailROM = con.execute("SELECT Mail_ROM FROM Platform").fetchall()
    MailROM = [i[0] for i in MailROM]    
    ListFile = [tempfile.gettempdir() + '/Technical Dashboard ' + Year + '-' + Month +'.xlsx']    
    try:
        mail.send_email(
            #to_emails=['axel.liber@1001fontaines.com'],
            to_emails=['axel.liber@1001fontaines.com','amandine.chaussinand@1001fontaines.com',
                       'bros.t@teuksaat1001.com','chanthan.m@teuksaat1001.com',
                       'sarady.p@teuksaat1001.com','borin.t@teuksaat1001.com',
                       'andrea.delsoldato@teuksaat1001.com','olivier.tognetti@1001fontaines.com',
                       'reaksmey.p@teuksaat1001.com','chamnap.keo@teuksaat1001.com'] + MailROM,
            subject='Technical Dashboard ' + Year + '-' + Month,
            html_content='Please find attached the technical report.',
            attachments=ListFile)
    except Exception as e:
        print(e.message)

def SendMailQuality():
    datej = date(datetime.today().year,datetime.today().month,1)
    CreateExcels.CreateQualityDashboard(datej)
    Year = str(datej.year)
    Month = datej.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    MailROM = con.execute("SELECT Mail_ROM FROM Platform").fetchall()
    MailROM = [i[0] for i in MailROM]
    ListFile = [tempfile.gettempdir() + '/Quality Dashboard ' + Year + '-' + Month +'.xlsx']    
    try:
        mail.send_email(
            to_emails=['axel.liber@1001fontaines.com','amandine.chaussinand@1001fontaines.com',
                       'bros.t@teuksaat1001.com','chanthan.m@teuksaat1001.com',
                       'sarady.p@teuksaat1001.com','borin.t@teuksaat1001.com',
                       'andrea.delsoldato@teuksaat1001.com','olivier.tognetti@1001fontaines.com',
                       'reaksmey.p@teuksaat1001.com','chamnap.keo@teuksaat1001.com'] + MailROM,
            subject='Quality Dashboard ' + Year + '-' + Month,
            html_content='Please find attached the quality report.',
            attachments=ListFile)
    except Exception as e:
        print(e.message)
if __name__ == '__main__':
    pass
