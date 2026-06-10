import db, os, json
import requests as simple_requests
from google.cloud import datastore
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import session
from monthlyreport.Mail import SendMailSiteClosure
from google.oauth2.service_account import Credentials
from sqldb.SiteClosure import closeSite, reopenSite
from datetime import datetime
from dateutil.relativedelta import *
import simplejson as _json
from monthlyreport.CreateExcels import exchange_rate_year
from monthlyreport.Functionutils import CategoryExpenses, NewCalculTier
import pandas as pd
import io
from flask import make_response
import flask
from PIL import Image
import pillow_heif
from extensions import cache
import json
from datetime import datetime
_datastore_client = None

def get_datastore_client():
    global _datastore_client
    if _datastore_client is None:
        path = flask.current_app.root_path + '/certs/client_secret_appengine.json'
        _datastore_client = datastore.Client.from_service_account_json(path)
    return _datastore_client

def getAuth():
    if "email" in session:
        con = db.pool.connect()
        query = con.execute("SELECT * FROM users WHERE email = %s", session['email'])
        user =  query.fetchone()
        permissions = "[]"
        if user != None:
            permissions = user['permissions']
        return {
            'email': session['email'],
            'permissions': permissions,
        }
    return 'unauthenticated'

def login(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), '736073153554-ka51oha7hvt3n5q4b1vqfhcsckpc3s96.apps.googleusercontent.com',  clock_skew_in_seconds=10)
        session['email'] = idinfo['email']
        con = db.pool.connect()
        query = con.execute("SELECT * FROM users WHERE email = %s", idinfo['email'])
        user =  query.fetchone()
        if user != None:
            session['permissions'] = user['permissions']
            idinfo['permissions'] = user['permissions']
        else:
            session['permissions'] = "[]"
            idinfo['permissions'] = "[]"
        return idinfo
    except ValueError as e:
        # Invalid token
        print(e)
        pass
    return {'email' : 'invalid'}

def logout():
    session.pop('email', None)
    session.pop('role', None)
    return {'email' : 'disconnected'}

def GetWarning(Site,month):
    '''List Warning :
    - PL trop faible
    - Diminution de -10% des ventes Total
    - Moins de 25 jours d'activités
    - Hod Price too low
    - Shopkeeper price too low '''
    con = db.pool.connect()
    Current_date = datetime.strptime(month,'%Y-%m').date()
    exchange_rate = exchange_rate_year(Current_date)
    Date_N_1 = Current_date - relativedelta(months=+12)
    dic_alert = {}
    Category_expenses = CategoryExpenses()
    inserted = con.execute("SELECT COUNT(*) FROM Sales WHERE Id_Site = %s AND Month = %s",Site,Current_date).fetchone()[0]
    Sales = con.execute("SELECT Total_Sales,Number_Open_Days,Hod_Price,Shopkeeper_Price,Hod_Sales,Shopkeeper_Sales,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales WHERE Id_Site = %s AND (Month =%s OR Month = %s) ORDER BY Month",Site,Current_date,Date_N_1).fetchall()

    Cost = con.execute("SELECT SUM(Amount_expenses)/%s FROM Expenses WHERE Id_Site = %s AND Category_expenses IN %s AND Month = %sGROUP BY Id_Site",(exchange_rate,Site,Category_expenses,Current_date)).fetchall()
    Revenue = con.execute("SELECT SUM(Total_income)/%s FROM Sales WHERE Id_Site = %s AND Month = %s",(exchange_rate,Site,Current_date)).fetchall()
    SalesWinS = con.execute("SELECT AVG(WiS_Sales),Id_Site FROM DailySales WHERE Id_Site = %s AND Month >= %s AND Month < %s",(Site,Current_date,Current_date+relativedelta(months=+1))).fetchall()
    Budget = con.execute("SELECT SchoolSalesBudget,Id_Site FROM Sites WHERE Id_Site = %s",Site).fetchall()
    if SalesWinS and SalesWinS[0][0]:
        if not Budget or not Budget[0][0]:
            dic_alert['WinS'] = 'No school budget for this site'
        elif SalesWinS[0][0]> Budget[0][0]:
            dic_alert['WinS'] = 'School sales are over budget (Sales : %s jugs/days; Budget : %s jugs/days)'%(int(SalesWinS[0][0]),int(Budget[0][0]))

    if not Revenue or not Revenue[0][0]:
        Revenue = [(0,)]
    if not Cost or not Cost[0][0]:
        Cost = [(0,)]


    if Revenue[0][0]-Cost[0][0]<0:
        dic_alert['P_L'] = '%s lost money this month ($%s)'%(Site,int(Revenue[0][0]-Cost[0][0]))

    Sales_now = list(filter(lambda row: row[6] == str(Current_date), Sales))
    Sales_N_1 = list(filter(lambda row: row[6] == str(Date_N_1), Sales))

    if Sales_now :
        if Sales_N_1:
            if Sales_now and Sales_N_1[0][0]*0.9>Sales_now[0][0]:
                dic_alert['Decreasing_Sales'] = '%s total sales went down by more than 10%% this month (%s %%)'%(Site,round((Sales_now[0][0]/Sales_N_1[0][0]-1)*100,2))

        if Sales_now and Sales_now[0][1] < 25:
            dic_alert['Opening_Days'] = '%s has been open for only %s days this month'%(Site,Sales_now[0][1])

        if Sales_now and Sales_now[0][2] < 1800 and Sales_now[0][2] != 0:
            dic_alert['Hod_Price'] = 'The home delivery price is below 1800៛ for %s (%s៛)'%(Site,Sales_now[0][2])

        if Sales_now and Sales_now[0][3] < 1600 and Sales_now[0][3] != 0:
            dic_alert['Shopkeeper_Price'] = 'The shopkeeper price is below 1600៛ for %s (%s៛)'%(Site,Sales_now[0][3])

        if Sales_now and (Sales_now[0][4]/(Sales_now[0][4]+Sales_now[0][5])) < 0.6:
            dic_alert['Hod_Mix'] = 'Home delivery sales are too low (%s%%)'%(int(Sales_now[0][4]/(Sales_now[0][4]+Sales_now[0][5])*100))

    return(dic_alert)

def GetSiteActive(Current_date):
    #Current_date = datetime.strptime(month,'%Y-%m').date()
    con = db.pool.connect()
    data = {}
    query = con.execute("SELECT Sales.Id_Site,Platform FROM Sales JOIN Sites ON Sites.Id_Site = Sales.Id_Site WHERE Total_Sales > 0 AND Month = %s",Current_date)
    data['Site_Active'] = [dict(row) for row in query.fetchall()]
    return(data)

def getUsers():
    data = {}
    data['users'] = []
    con = db.pool.connect()
    query = con.execute("SELECT * FROM users ORDER BY email")
    for row in query.fetchall():
        data['users'].append(
            {
                'email': row['email'],
                'permissions': json.loads(row['permissions'])
            }
        )
    return data

def listOrder(month):
    con = db.pool.connect()
    data={}
    month = month + "-01"
    query = con.execute("SELECT Code_Consumable, DATE_FORMAT(Month, '%%Y-%%m') as Month, DATE_FORMAT(Date_submission, '%%Y-%%m-%%d') as Date_submission,EmailApprover,Consumable.Id_Site,item,Khmer_name,English_name,Number_Item,Price_Item/Number_Item as unit_price,Price_Item,Advisor,Validate,Payment_method,Unit,PO, Remark, EmailRequestor,track FROM Consumable JOIN Sites ON Consumable.Id_Site = Sites.Id_Site WHERE Month = %s",month)
    data['consumables'] = [dict(row) for row in query.fetchall()]
    return _json.dumps(data,default=str)

def validatelogistics(id_consumable,valid):
    con = db.pool.connect()
    if valid == False:
        con.execute("UPDATE Consumable SET Validate = 0 WHERE Code_Consumable = %s", id_consumable)
    else:
        con.execute("UPDATE Consumable SET Validate = 1 WHERE Code_Consumable = %s", id_consumable)
    return "ok"

def validateAlllogistics(id_consumable):
    con = db.pool.connect()
    con.execute(
        "UPDATE Consumable SET Validate = 1 WHERE Code_Consumable IN ({}) AND (Payment_method = 'Invoice' OR Payment_method = 'Cash')"
        .format(",".join(id_consumable))
    )
    return "ok"

def saveOrder(item):
    con = db.pool.connect()
    month = item["Month"] + "-01"
    row = con.execute("SELECT track FROM Consumable WHERE Code_Consumable = %s", item["Code_Consumable"]).fetchone()
    raw = row["track"] if row and row["track"] else []
    if isinstance(raw, list):
        track = raw
    else:
        try:
            track = json.loads(raw)
        except (ValueError, TypeError):
            track = []
    track.append({"user": session["email"], "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    con.execute("UPDATE Consumable SET Month = %s, item = %s, Price_Item = %s, Number_Item = %s, Id_Site=%s, English_name=%s, Khmer_name=%s, Payment_method=%s, Unit=%s, track=%s WHERE Code_Consumable = %s",
        month, item["item"], item["Price_Item"], item["Number_Item"], item["Id_Site"], item["English_name"], item["Khmer_name"], item["Payment_method"], item["Unit"], json.dumps(track), item["Code_Consumable"])
    return "ok"

def editSiteProfile(item):
    con = db.pool.connect()
    con.execute("""UPDATE Sites SET
                    Platform = %s,
                    Advisor = %s,
                    Village = %s,
                    Village_khmer = %s,
                    Code_Village = %s,
                    Commune = %s,
                    Commune_khmer = %s,
                    Code_Commune = %s,
                    District = %s,
                    District_khmer = %s,
                    Code_District = %s,
                    Province = %s,
                    Province_khmer = %s,
                    Code_Province = %s,
                    Latitude = %s,
                    Longitude = %s,
                    ProjectAgreement = %s,
                    Wave = %s,
                    Sale_Starting_Date = %s,
                    Funder_1 = %s,
                    Funder_2 = %s,
                    Funder_3 = %s,
                    Building_cost = %s,
                    Number_Village = %s,
                    Number_Family = %s,
                    Number_Households = %s,
                    Number_Population = %s,
                    Number_Women = %s,
                    Number_Migration = %s,
                    Number_Village_5km = %s,
                    Number_Family_5km = %s,
                    Number_Households_5km = %s,
                    Number_Population_5km = %s,
                    Number_Women_5km = %s,
                    Number_Migration_5km = %s,
                    Number_Pagoda = %s,
                    Number_Primary_School = %s,
                    Land_of_kiosk = %s,
                    Road_Leading_to_Kiosk = %s,
                    Paved_Asphalt_Road = %s,
                    Concrete_Road = %s,
                    Laterite_Road = %s,
                    White_Soiled_Road = %s,
                    Water_Source = %s,
                    Well_Pond_Ownership = %s,
                    Depth_Well_Pond = %s,
                    Water_Source_Distance_From_Kiosk = %s,
                    Second_Water_Source = %s,
                    Well_Pond_Ownership_Second_Source = %s,
                    Depth_Well_Pond_Second_Source = %s,
                    Water_Source_Distance_From_Kiosk_Second_Source = %s,
                    Main_Power_Source = %s,
                    Second_Power_Source = %s,
                    Type_of_Water_Tank = %s,
                    Monthly_Income_Average_per_Person = %s,
                    Labour_Market = %s,
                    Monthly_Income_Average_per_Worker = %s 
                    WHERE Id_Site = %s""",item["Platform"], item["Advisor"], item["Village"], item["Village_khmer"], item["Code_Village"], item["Commune"], item["Commune_khmer"], item["Code_Commune"], item["District"], item["District_khmer"], item["Code_District"]
        , item["Province"], item["Province_khmer"], item["Code_Province"], item["Lati"], item["Longi"], item["ProjectAgreement"], item["Wave"], item["Sale_Starting_Date"]
        , item["Funder_1"], item["Funder_2"], item["Funder_3"]
        , item["Building_cost"], item["Number_Village"], item["Number_Family"], item["Number_Households"], item["Number_Population"], item["Number_Women"]
        , item["Number_Migration"], item["Number_Village_5km"], item["Number_Family_5km"], item["Number_Households_5km"], item["Number_Population_5km"]
        , item["Number_Women_5km"], item["Number_Migration_5km"], item["Number_Pagoda"], item["Number_Primary_School"], item["Land_of_kiosk"], item["Road_Leading_to_Kiosk"]
        , item["Paved_Asphalt_Road"], item["Concrete_Road"], item["Laterite_Road"], item["White_Soiled_Road"], item["Water_Source"], item["Well_Pond_Ownership"]
        , item["Depth_Well_Pond"], item["Water_Source_Distance_From_Kiosk"], item["Second_Water_Source"], item["Well_Pond_Ownership_Second_Source"], item["Depth_Well_Pond_Second_Source"]
        , item["Water_Source_Distance_From_Kiosk_Second_Source"], item["Main_Power_Source"], item["Second_Power_Source"], item["Type_of_Water_Tank"], item["Monthly_Income_Average_per_Person"]
        , item["Labour_Market"], item["Monthly_Income_Average_per_Worker"], item["Id_Site"])
    return "ok"

def createOrder(item):
    
    con = db.pool.connect()
    month = item["Month"] + "-01"
    track = json.dumps([{"user": session["email"], "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}])
    con.execute("INSERT INTO Consumable (Month, Id_Site, item, Price_Item, Number_Item, Date_submission, English_name, Khmer_name, Payment_method, Unit, track) VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s)",
        month, item["Id_Site"], item["item"], item["Price_Item"] , item["Number_Item"], item["English_name"], item["Khmer_name"], item["Payment_method"], item["Unit"], track)
    return "ok"

def deleteOrder(item):
    con = db.pool.connect()
    con.execute("DELETE FROM Consumable WHERE Code_Consumable = %s", item["Code_Consumable"])
    return "ok"

def getSiteProfile(site):
    con = db.pool.connect()
    data = {}
    query = con.execute("SELECT * FROM Sites WHERE Id_Site = %s",site)
    data['Site_Profile'] = [dict(row) for row in query.fetchall()]
    return data

def getAllSiteProfile():
    con = db.pool.connect()
    data = {}
    query = con.execute("SELECT * FROM Sites")
    data['All_Site_Profile'] = [dict(row) for row in query.fetchall()]
    return data

def getMapData():
    """Return all sites with their status for the map display.
    Status: 'active' (blue), 'closed_inactive' (red), 'opening_soon' (green), 'dead' (excluded).
    """
    from datetime import date
    con = db.pool.connect()

    today = date.today()
    # Reference month: day < 10 use M-2, day >= 10 use M-1
    if today.day < 10:
        current_date = date(today.year, today.month, 1) - relativedelta(months=2)
    else:
        current_date = date(today.year, today.month, 1) - relativedelta(months=1)

    # Get all sites with their info
    sites_query = con.execute(
        "SELECT Id_Site, Platform, Commune, District, Province, Latitude, Longitude, "
        "Commune_khmer, District_khmer, Province_khmer, Code_Commune FROM Sites"
    )
    all_sites = [dict(row) for row in sites_query.fetchall()]

    # Build tier lookup for all sites at once (bulk, avoids N per-site queries)
    all_tiers_raw, _ = NewCalculTier(current_date)
    tier_dict = {sid: t for sid, t in all_tiers_raw}

    # Get sites that have ever had sales
    sales_ever = con.execute(
        "SELECT DISTINCT Id_Site FROM Sales WHERE Total_Sales > 0"
    ).fetchall()
    sites_with_sales = set(row[0] for row in sales_ever)

    # Get sites with sales in the last month (reference month)
    sales_last_month = con.execute(
        "SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales > 0",
        (current_date,)
    ).fetchall()
    sites_last_month = set(row[0] for row in sales_last_month)

    # Average daily sales per site over last 12 months (bottles/day)
    # Uses same formula and parameter style as NewCalculTier (which works in production)
    date_12m_ago = current_date - relativedelta(months=12)
    daily_sales_dict = {}
    try:
        daily_sales_rows = con.execute(
            "SELECT Id_Site, SUM(Total_Sales-WiS_Sales)/SUM(Number_Open_Days) "
            "FROM Sales WHERE Month <= %s AND Month > %s GROUP BY Id_Site",
            (current_date, date_12m_ago)
        ).fetchall()
        daily_sales_dict = {row[0]: float(row[1]) if row[1] is not None else 0.0
                            for row in daily_sales_rows}
    except Exception as e:
        print(f"[getMapData] daily_sales query failed: {e}")

    result = []
    for site in all_sites:
        site_id = site['Id_Site']
        platform = site.get('Platform', '')
        platform_normalized = str(platform).strip().lower()

        # Skip dead sites
        if platform_normalized == 'dead':
            continue

        if site_id in sites_last_month:
            status = 'active'
        elif site_id in sites_with_sales:
            status = 'closed_inactive'
        else:
            status = 'opening_soon'

        result.append({
            'id': site_id,
            'commune': site.get('Commune', ''),
            'commune_code': site.get('Code_Commune'),
            'district': site.get('District', ''),
            'province': site.get('Province', ''),
            'commune_khmer': site.get('Commune_khmer', ''),
            'lat': site.get('Latitude'),
            'lng': site.get('Longitude'),
            'status': status,
            'platform': platform,
            'tier': tier_dict.get(site_id, ''),
            'daily_sales': daily_sales_dict.get(site_id, 0.0)
        })

    # Get list of all communes for the dropdown
    communes_query = con.execute(
        "SELECT DISTINCT Commune, District, Province FROM Sites WHERE Commune IS NOT NULL AND Commune != '' ORDER BY Province, District, Commune"
    )
    all_communes = [dict(row) for row in communes_query.fetchall()]

    # Commune code → name lookup for import resolution
    code_commune_query = con.execute(
        "SELECT DISTINCT Code_Commune, Commune FROM Sites WHERE Code_Commune IS NOT NULL AND Commune IS NOT NULL AND Commune != ''"
    )
    code_to_commune = {str(row[0]): row[1] for row in code_commune_query.fetchall()}

    # Also get distinct communes from GeoJSON matching (all possible communes)
    return {
        'sites': result,
        'communes': all_communes,
        'code_to_commune': code_to_commune,
        'reference_date': str(current_date),
        'counts': {
            'active': sum(1 for s in result if s['status'] == 'active'),
            'closed_inactive': sum(1 for s in result if s['status'] == 'closed_inactive'),
            'opening_soon': sum(1 for s in result if s['status'] == 'opening_soon'),
            'total': len(result)
        }
    }

def getSales(site, month):
    con = db.pool.connect()
    data = {}
    query = con.execute("SELECT * FROM DailySales WHERE Id_Site = %s AND DATE_FORMAT(Month, '%%Y-%%m') = %s ORDER BY Day ASC", site, month)
    data['sales'] = [dict(row) for row in query.fetchall()]
    if len(data['sales']) == 0:
        # No sales from daily sales, check if there are sales from cashier app
        query = con.execute("""
            SELECT sale_date as Day, sum(quantity) as quantity, type 
            FROM cashier_sales 
            WHERE site = %s AND DATE_FORMAT(sale_date, '%%Y-%%m') = %s 
            GROUP BY sale_date, type 
            ORDER BY sale_date
        """, site, month)
        sales_rows = query.fetchall()
        mapping = {
            'free': 'Free_Sales',
            'hod': 'Hod_Sales',
            'shop': 'Shopkeeper_Sales',
            'wis': 'WiS_Sales',
            'onsite': 'Onsite_Sales',
            'bottle': 'Bottle_Sales',
            'other': 'Others_Sales',
            'emergency': 'Emergency_Sales'
        }
        pivoted = {}
        for row in sales_rows:
            r = dict(row)
            day = str(r['Day'])
            if day not in pivoted:
                pivoted[day] = {col: None for col in mapping.values()}
                pivoted[day]['Code_Daily'] = day + site
                pivoted[day]['Total_Sales'] = 0
                pivoted[day].update({'Day': r['Day'], 'Id_Site': site})
            target_col = mapping.get(r['type'])
            if target_col:
                pivoted[day][target_col] = int(r['quantity'])
                pivoted[day]['Total_Sales'] += int(r['quantity'])
        data['sales'] = sorted(pivoted.values(), key=lambda x: x['Day'])       

    query = con.execute("SELECT * FROM Sales WHERE Id_Site = %s AND DATE_FORMAT(Month, '%%Y-%%m') = %s", site, month)
    sales = query.fetchone()
    data['total'] = dict(sales) if sales != None else {}
    return data

def getIndicators(site, month):
    con = db.pool.connect()
    query = con.execute("SELECT * FROM Indicators WHERE Id_Site = %s AND DATE_FORMAT(Month, '%%Y-%%m') = %s", site, month)
    data = query.fetchone()
    lastDayOfPreviousMonth = (datetime.strptime(month, '%Y-%m') - relativedelta(days=1)).strftime('%Y-%m-%d')
    lastDayOfMonth = (datetime.strptime(month, '%Y-%m') + relativedelta(months=1)).strftime('%Y-%m-%d')
    query = con.execute("SELECT DATE_FORMAT(date, '%%Y-%%m-%%d') as date, value FROM water_meters WHERE site = %s AND date > %s AND date < %s ORDER BY date ASC", site, lastDayOfPreviousMonth, lastDayOfMonth)
    data = dict(data) if data is not None else {}
    data['water_meters'] = [dict(row) for row in query.fetchall()]
    query = con.execute("SELECT DATE_FORMAT(date, '%%Y-%%m-%%d') as date, value FROM water_meters WHERE site = %s AND date <= %s ORDER BY date DESC LIMIT 1", site, lastDayOfPreviousMonth)
    prev_row = query.fetchone()
    # Si pas de valeur la semaine d'avant on prend la valeur la plus récente
    if prev_row is not None:
        data['water_meters'].insert(0, {'date': lastDayOfPreviousMonth, 'value': prev_row['value']})
    else:
        # Si toujours rien, on prend la valeur la plus recente de Indicators
        query = con.execute("SELECT * FROM Indicators WHERE Id_Site = %s AND DATE_FORMAT(Month, '%%Y-%%m') <= %s ORDER BY Month DESC LIMIT 1", site, month)
        prev_row = query.fetchone()
        data['water_meters'].insert(0, {'date': (prev_row['Month'] + relativedelta(months=1) - relativedelta(days=1)).strftime('%Y-%m-%d'), 'value': prev_row['Water_end']})
    return data

def getPicture(path):
    pathInjected = path[:8] + "jonathan.faucher@gmail.com:commjohn1@" + path[8:]
    response = simple_requests.get(pathInjected)
    content = response.content
    
    # Check if the image is HEIF/HEIC format and convert it to jpeg
    if path.lower().endswith(('.heic', '.heif')):
        try:
            pillow_heif.register_heif_opener()
            image_bytes = io.BytesIO(content)
            image = Image.open(image_bytes)
            output = io.BytesIO()
            image.convert('RGB').save(output, format='JPEG', quality=90)
            content = output.getvalue()
        except Exception as e:
            print(f"Error converting HEIF/HEIC to JPEG: {e}")
    
    return content

def getExpenses(site, month):
    con = db.pool.connect()
    data = {}
    query = con.execute("SELECT * FROM Expenses WHERE Id_Site = %s AND DATE_FORMAT(Month, '%%Y-%%m') = %s AND Ref_expenses <> 'WinS_invoice' AND Ref_expenses <> 'debt' AND Ref_expenses <> 'withdrawal' ORDER BY Code_expenses ASC", site, month)
    data['expenses'] = [dict(row) for row in query.fetchall()]
    return data

def getCommcarePictures(site, month):
    images = {}
    results = getCommcareImages(month, site)
    for pivot in results:
        data = json.loads(pivot['data'])
        images[pivot['form']] = data['attachments']

    # get cashier app images
    month = (datetime.strptime(month, '%m-%Y')).strftime('%Y-%m')
    con = db.pool.connect()
    query = con.execute("SELECT id, name, path, miniature_path, type FROM files WHERE site = %s AND DATE_FORMAT(related_date, '%%Y-%%m') = %s ORDER BY related_date ASC", site, month)
    images['cashier_app'] = [dict(row) for row in query.fetchall()]

    return images

def getCommcareQualityResults(site, month):
    con = db.pool.connect()
    query = con.execute("SELECT * FROM samples WHERE site = %s AND DATE_FORMAT(sample_date, '%%Y-%%m') = %s ORDER BY analysis_date ASC", site, month)
    return [dict(row) for row in query.fetchall()]

def getClosures(month):
    con = db.pool.connect()
    Date = datetime.strptime(month,'%m-%Y')+relativedelta(months=+1)
    query = con.execute("SELECT * FROM Closure WHERE (reopening_date IS null OR reopening_date >= %s) AND Closing_date<=%s ",(Date,Date+relativedelta(months=+1)))
    return [dict(row) for row in query.fetchall()]

def getClosuresForSite(site):
    con = db.pool.connect()
    data = {}
    query = con.execute("SELECT * FROM Closure WHERE Id_Site=%s ORDER BY Closing_date DESC", site)
    data['closures'] = [dict(row) for row in query.fetchall()]
    return data

@cache.memoize()
def getCommcareImages(month, site):
    query = get_datastore_client().query(kind="Pivot")
    query.add_filter('month', '=', month)
    query.add_filter('site', '=', site)
    results = list(query.fetch())
    print("getCommcareImages has been cached")
    return results

@cache.memoize()
def getSubmittedForm(month):
    query = get_datastore_client().query(kind="Pivot")
    query.projection = ['site', 'form']
    query.add_filter('month', '=', month)
    pivots = list(query.fetch())
    print("getSubmittedForm has been cached")
    return pivots

@cache.memoize()
def getActiveSites():
    query = get_datastore_client().query(kind="Site")
    query.order = ["site"]
    query.projection = ['platform', 'site']
    query.add_filter('inactive', '=', 'no')
    pivots = list(query.fetch())
    print("getActiveSites has been cached")
    return pivots

@cache.memoize()
def getValidatedForms(month):
    query = get_datastore_client().query(kind="Pivot")
    query.add_filter('month', '=', month)
    query.add_filter('isValidated', '=', '1')
    query.keys_only()
    pivots = list(query.fetch())
    print("getValidatedForms has been cached")
    return pivots

@cache.memoize()
def getFinanceValidatedForms(month):
    query = get_datastore_client().query(kind="Pivot")
    query.add_filter('month', '=', month)
    query.add_filter('isFinanceValidated', '=', '1')
    query.keys_only()
    pivots = list(query.fetch())
    print("getFinanceValidatedForms has been cached")
    return pivots

def getCommcareMonthlyReport(month):
    pivots = []
    result = {}
    formsMap = {}

    # get active sites list
    pivots = getActiveSites()
    for site in pivots:
        result[site.get('site')] = {
            'site' : site.get('site'),
            'platform' : site.get('platform'),
            # 'office': site.get('office'),
            'closed': 0,
            'closedReason': {},
            'forms' : [],
            'isValidated' : 0,
            'isFinanceValidated' : 0,
            'nop' : 0,
        }

    # get never opened sites
    con = db.pool.connect()
    Date = datetime.strptime(month,'%m-%Y')+relativedelta(months=+1)
    query = con.execute("SELECT Id_Site FROM Sites WHERE Id_Site NOT IN (SELECT Id_Site FROM Sales WHERE Month < %s)",Date)
    neverOpenedSites = [dict(row) for row in query.fetchall()]
    for nos in neverOpenedSites:
        if nos['Id_Site'] in result:
            result[nos['Id_Site']]['nop'] = 1

    # get closures
    closures = getClosures(month)
    for closure in closures:
        if closure['Id_Site'] in result:
            result[closure['Id_Site']]['closed'] = 1
            result[closure['Id_Site']]['closedReason'] = closure

    # get submitted forms
    pivots = getSubmittedForm(month)
    for pivot in pivots:
        if pivot.get('site') in result:
            result[pivot.get('site')]['forms'].append(pivot.get('form'))
            formsMap[str(pivot.id)] = pivot.get('site')

    # Get sales from cashier app
    monthSQL = datetime.strptime(month,'%m-%Y').strftime('%Y-%m')
    query = con.execute("SELECT DISTINCT(site) FROM cashier_sales WHERE sale_date LIKE %s", monthSQL+'%')
    cashierSales = [dict(row) for row in query.fetchall()]
    for cs in cashierSales:
        if cs['site'] in result:
            result[cs['site']]['forms'].append('1. Register Sales')

    # Get expenses from cashier app
    query = con.execute("SELECT DISTINCT(Id_Site) FROM Expenses WHERE Month LIKE %s AND Ref_expenses <> %s AND Amount_expenses>0", (monthSQL+'%', 'debt'))
    cashierExpenses = [dict(row) for row in query.fetchall()]
    for ce in cashierExpenses:
        if ce['Id_Site'] in result:
            result[ce['Id_Site']]['forms'].append('2. Register Expenses')

    # Get settled invoices from cashier app
    query = con.execute("SELECT DISTINCT(site) FROM invoices WHERE Month LIKE %s AND status = %s", (monthSQL+'%', 'settle'))
    cashierSettlements = [dict(row) for row in query.fetchall()]
    for settledInvoice in cashierSettlements:
        if settledInvoice['site'] in result:
            result[settledInvoice['site']]['forms'].append('3. Settle Invoices')

    # get validated forms
    pivots = getValidatedForms(month)
    for pivot in pivots:
        result[formsMap[str(pivot.id)]]["isValidated"] = 1


    # get finance validated forms
    pivots = getFinanceValidatedForms(month)
    for pivot in pivots:
        result[formsMap[str(pivot.id)]]["isFinanceValidated"] = 1

    return list(result.values())

def validateReport(site, month):
    service_account_info = json.load(open(flask.current_app.root_path+'/certs/datastore_writer_appengine.json'))
    credentials = Credentials.from_service_account_info(service_account_info)
    datastore_client = datastore.Client(project="sims-2-140009", credentials=credentials)
    query = datastore_client.query(kind="Pivot")
    query = query.add_filter('form', '=','1. Register Sales')
    query = query.add_filter('month', '=', month)
    query = query.add_filter('site', '=', site)
    query.order = ["-integration_date"]
    pivots = list(query.fetch())
    update = 'error'
    for pivot in pivots:
        if not 'isValidated' in pivot:
            pivot['isValidated'] = "1"
            update = '1'
        elif pivot['isValidated'] == "1" or pivot['isValidated'] == 1:
            pivot['isValidated'] = "0"
            update = '0'
        else:
            pivot['isValidated'] = "1"
            update = '1'
        datastore_client.put(pivot)
    return update

def closeSiteApi(site, reason, closureDate, description,nameUser=0):
    reasons = reason.split('-')
    closeSite(site, closureDate, reasons[1], reasons[0], description)
    # if 'email' in session:
    #     SendMailSiteClosure(site, session['email'], closureDate, reason, description)
    # else:
    #     SendMailSiteClosure(site, nameUser, closureDate, reason, description)
    # return "ok"

def reopenSiteApi(site, reopeningDate,nameUser=0):
    reopenSite(site, reopeningDate)
    # if 'email' in session:
    #     SendMailSiteReopen(site, reopeningDate, session['email'])
    return "ok"

def getRequests(month):
    datastore_client = datastore.Client.from_service_account_json(flask.current_app.root_path+'/certs/client_secret_appengine.json')
    query = datastore_client.query(kind="Pivot")
    query = query.add_filter('month', '=', month)
    query = query.add_filter('form', '=', '7. Request Form')
    query.order = ["integration_date"]
    requests = list(query.fetch())
    results = []
    for request in requests:
        data = json.loads(request['data'])
        catalogue = data['form']['price_list']['item']
        if 'isLogisticValidated' in request:
            validatedOrder = json.loads(request['isLogisticValidated'])
        else:
            validatedOrder = []
        for index in range(1,5):
            if 'site_confirmed' in data['form']:
                for item_code in data['form']['site_confirmed']['category'+str(index)]:
                    if item_code.startswith("IT") and data['form']['site_confirmed']['category'+str(index)][item_code] != "":
                        catalogue_item = next(item for item in catalogue if item["@id"] == item_code)
                        results.append({
                            "id": request.id,
                            "site": request['site'],
                            "advisor": data['metadata']['username'],
                            "date": data['metadata']['timeStart'],
                            "item_code": item_code,
                            "item_name": catalogue_item["eng"],
                            "item_name_kh": catalogue_item["kh"],
                            "unit": catalogue_item["unit"],
                            "quantity": data['form']['site_confirmed']['category'+str(index)][item_code],
                            "price": data['form']['site_confirmed']['category'+str(index)]["price_"+item_code],
                            "validated": (item_code in validatedOrder)
                        })


    data = {"results" : results}
    return data

def validateRequest(id, item_code):
    service_account_info = json.load(open('certs/datastore_writer_appengine.json'))
    credentials = Credentials.from_service_account_info(service_account_info)
    datastore_client = datastore.Client(project="sims-2-140009", credentials=credentials)
    key = datastore_client.key('Pivot', id)
    request = datastore_client.get(key)
    if 'isLogisticValidated' in request:
        validatedRequests = json.loads(request['isLogisticValidated'])
        if item_code in validatedRequests:
            validatedRequests.remove(item_code)
        else:
            validatedRequests.append(item_code)
    else:
        validatedRequests = [item_code]
    request['isLogisticValidated'] = json.dumps(validatedRequests)
    datastore_client.put(request)
    return request['isLogisticValidated']

def getDashboardSims2(month):
    response = simple_requests.get("https://sims-2-140009.appspot.com/commcare/dashboard.php?index="+month)
    return response.content


def insertOTTData(data):
    site = ""
    con = db.pool.connect()
    for line in data.splitlines():
        if line.startswith("<STATION>"):
            site = line[9:19].lstrip('0')
            sensor = line[37:41].lstrip('0')
        elif site != "":
            dateReleve = line[0:4] + "-" + line[4:6] + "-" + line[6:8] + " " + line[9:11] + ":" + line[11:13] + ":" + line[13:15]
            value = line[16:]
            con.execute("INSERT INTO ott (site, sensor, date, value) VALUES (%s, %s, %s, %s)",site, sensor, dateReleve, value)
    return "ok"

def downloadOTTData(month):
    con = db.pool.connect()
    data = {}
    query = con.execute("SELECT site, sensor, date, value FROM ott WHERE `date` like %s", month+'%')
    data = query.fetchall()
    df = pd.DataFrame((tuple(t) for t in data), columns=('site', 'sensor', 'date', 'value'))
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine='xlsxwriter')
    df.to_excel(excel_writer=writer, index=False, sheet_name='OTT')
    writer.sheets["OTT"].set_column(2, 2, 20)
    writer.close()
    r = make_response(out.getvalue())
    r.headers["Content-Disposition"] = "attachment; filename=export_ott_"+month+".xlsx"
    r.headers["Content-type"] = "application/x-xls"
    return r