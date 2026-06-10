from google.cloud import datastore
import os
import json
import datetime
from datetime import date,timedelta
from calendar import monthrange
import db
from dateutil.relativedelta import *
import json
import flask

con = db.pool.connect()

datastore_client = datastore.Client.from_service_account_json('certs/client_secret_appengine.json')

def getCommcareMonthlyReport(month):
    pivots = []
    result = {}
    formsMap = {}

    # get active sites list
    query = datastore_client.query(kind="Site")
    query.order = ["site"]
    query.projection = ['platform', 'site']
    query.add_filter('inactive', '=', 'no')
    pivots = list(query.fetch())
    for site in pivots:
        result[site.get('site')] = {
            'site' : site.get('site'),
            'platform' : site.get('platform'),
            'forms' : [],
            'isValidated' : 0,
            'isFinanceValidated' : 0
        }

    # get submitted forms
    query = datastore_client.query(kind="Pivot")
    query.projection = ['site', 'form']
    query.add_filter('month', '=', month)
    pivots = list(query.fetch())
    for pivot in pivots:
        if pivot.get('site') in result:
            result[pivot.get('site')]['forms'].append(pivot.get('form'))
            formsMap[str(pivot.id)] = pivot.get('site')

    # get validated forms
    query = datastore_client.query(kind="Pivot")
    query.add_filter('month', '=', month)
    query.add_filter('isValidated', '=', '1')
    query.keys_only()
    pivots = list(query.fetch())
    for pivot in pivots:
        result[formsMap[str(pivot.id)]]["isValidated"] = 1

    # get finance validated forms
    query = datastore_client.query(kind="Pivot")
    query.add_filter('month', '=', month)
    query.add_filter('isFinanceValidated', '=', '1')
    query.keys_only()
    pivots = list(query.fetch())
    for pivot in pivots:
        result[formsMap[str(pivot.id)]]["isFinanceValidated"] = 1

    return list(result.values())

def listsite(): #create the list of site
    Listsite = []
    query = datastore_client.query(kind="Site")
    query.order = ["site"]
    BDD = list(query.fetch())
    for i in range (len(BDD)):
        Listsite.append(BDD[i]["site"])
    return(Listsite)

def get_data_daily_sales(Data_dict, day):
    if Data_dict["form"]["site_confirmed"].get("sales_text") and Data_dict["form"]["site_confirmed"]["sales_text"]:
        Tab_channel = Data_dict["form"]["site_confirmed"]["sales_text"]
        Listsales = str.split(Tab_channel)
        Listchannel = ["hod", "shopkeeper","school", "onsite","free", "bottle"]
        ListOther = []

        channel = Data_dict["form"]["site_confirmed"]["sale-channel"]
        #print(channel)
        if isinstance(channel,list):
            for i in range(len(Data_dict["form"]["site_confirmed"]["sale-channel"])):
                try:
                    Name_channel = channel[i]["enforce-repeats"]["channel-list"]["channel"]
                except:
                    print(channel[i])
                if Name_channel not in Listchannel:
                        ListOther.append(Name_channel)
            #print("here")
        else:
            if Data_dict["form"]["site_confirmed"]["sale-channel"]["enforce-repeats"]["channel-list"]["channel"] not in Listchannel:
                ListOther.append(Data_dict["form"]["site_confirmed"]["sale-channel"]["enforce-repeats"]["channel-list"]["channel"])
        Site = Data_dict["form"]["site_name"]
        Month = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
        Day = datetime.datetime.strptime(str(day) + "-" + Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%d-%m-%Y')
        L=[Site,Month,Day,0,0,0,0,0,0,0,0]
        for k in range(len(Listsales)):
            if Listsales[k] in Listchannel:
                i = Listchannel.index(Listsales[k])
                try:
                    L[i+4] += int(Listsales[k+day+1])
                    L[3] += int(Listsales[k+day+1])
                except:
                    pass
            elif Listsales[k] in ListOther:
                L[10] += int(Listsales[k+day+1])
                L[3] += int(Listsales[k+day+1])
        #L.append(L[3]-L[4]-L[5]-L[6]-L[7]-L[8]-L[9])


    else:
        Site = Data_dict["form"]["site_name"]
        Month = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
        Day = datetime.datetime.strptime(str(day) + "-" + Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%d-%m-%Y')
        print("error dailysales")
        print(Site,Day)
        L=[Site,Month,Day,0,0,0,0,0,0,0,0]
    return(L)

def get_data_beneficiaries(Data_dict): #extract site, month and number of beneficiaries for one request. argument = dictionnaries of the data from 1. Register Sales
    if Data_dict["form"]["site_confirmed"].get("sales_text"):
        Tab_channel = Data_dict["form"]["site_confirmed"]["sales_text"]
        Listsales = str.split(Tab_channel)
        Listchannel = ["hod","free","shopkeeper","onsite"]
        Beneficiariesday = [0] * int(Listsales[1])
        Site = Data_dict["form"]["site_name"]
        Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
        for k in range(len(Listsales)):
            if Listsales and Listsales[k] in Listchannel:
                day = 0
                for i in range(k+2,k+int(Listsales[1])+2):
                    try:
                        Beneficiariesday[day] += int(Listsales[i])
                        day +=1
                    except:
                        break

        k = 0
        beneficiaries = 0
        while k < len(Beneficiariesday)-2:
            beneficiaries = max(beneficiaries,(Beneficiariesday[k]+Beneficiariesday[k+1]+Beneficiariesday[k+2])/3)
            k+=1
        L = [Site, Date, beneficiaries*20/1.5]

    else:
        Site = Data_dict["form"]["site_name"]
        Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
        print("error")
        print(Site,Date)
        L=[Site,Date,0]
    return(L)

def get_data_open_days(Data_dict): #Calculate the number of open days for one site this month. argument = dictionnaries of the data from 1. Register Sales
    if Data_dict["form"]["site_confirmed"].get("sales_text") and Data_dict["form"]["site_confirmed"]["sales_text"]:
        Tab_channel = Data_dict["form"]["site_confirmed"]["sales_text"]
        Listsales = str.split(Tab_channel)
        Listchannel = ["hod","free","shopkeeper","onsite","school"]
        Beneficiariesday = [0] * int(Listsales[1])
        Site = Data_dict["form"]["site_name"]
        Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
        for k in range(len(Listsales)):
            if Listsales and Listsales[k] in Listchannel:
                day = 0
                for i in range(k+2,k+int(Listsales[1])+2):
                    if len(Listsales) > i:
                        Beneficiariesday[day] += int(Listsales[i])
                        day +=1
                    else:
                        pass
        days = 0
        Number_open_days = 0
        for i in Beneficiariesday:
            if i and i != 0:
                Number_open_days += 1
        return (Number_open_days)
    else:
        return(0)

def get_data_site(sitename):
    query_site = datastore_client.query(kind="Site")
    query_site.add_filter("site","=",sitename)
    query_entity_site = list(query_site.fetch())
    Alphabet =['B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    if query_entity_site:
        if not ('province_code' in query_entity_site[0]):
            code_province = None
        else:
            code_province = query_entity_site[0]['province_code']

        if not ('office' in query_entity_site[0]):
            platform = None
        else:
            platform = query_entity_site[0]['office']

        if not ('platform' in query_entity_site[0]):
            project = None
        elif query_entity_site[0]['platform'] == 'Project':
            project = True
            office = "Project"
        else:
            project = None
            office = platform


        if not ('province' in query_entity_site[0]):
            province =  None
        else :
            province = query_entity_site[0]['province']

        if not ('wave' in query_entity_site[0]) or not query_entity_site[0]["wave"]:
            if sitename[0] == 'A':
                wave = '2005.0'

            elif sitename[0] in Alphabet:
                wave = str(2007 + Alphabet.index(sitename[0])) + '.0'
        else:
            wave = query_entity_site[0]["wave"]
    #print(query_entity_site[0]["wave"])
        if not ('longitude' in query_entity_site[0]) or (query_entity_site[0]["longitude"] == 0):
            if 'site_profile' in query_entity_site[0] and query_entity_site[0]["site_profile"] and 'gps' in query_entity_site[0]["site_profile"]:
                Site_Profile = json.loads(query_entity_site[0]["site_profile"])
                query_entity_site[0]["longitude"] = Site_Profile['gps']['longitude']
            else:
                query_entity_site[0]["longitude"] = None
        if not ('latitude' in query_entity_site[0]) or (query_entity_site[0]["latitude"] == 0):
            if 'site_profile' in query_entity_site[0] and query_entity_site[0]["site_profile"] and 'gps' in query_entity_site[0]["site_profile"]:
                Site_Profile = json.loads(query_entity_site[0]["site_profile"])
                query_entity_site[0]["latitude"] = Site_Profile['gps']['latitude']
            else:
                query_entity_site[0]["latitude"] = None
        L = [sitename,platform,project,office,province,code_province,wave,query_entity_site[0]["longitude"],query_entity_site[0]["latitude"]]

        if 'site_profile' in query_entity_site[0] and query_entity_site[0]["site_profile"]:
            Site_profile = json.loads(query_entity_site[0]["site_profile"])
            if 'address' in Site_profile:
                if 'english_village' in Site_profile['address']:
                    L.append(Site_profile['address']['english_village'])
                else:
                    L.append(0)

                if 'english_commune' in Site_profile['address']:
                    L.append(Site_profile['address']['english_commune'])
                else:
                    L.append(0)

                if 'english_district' in Site_profile['address']:
                    L.append(Site_profile['address']['english_district'])
                else:
                    L.append(0)
            else:
                L.extend([0,0,0])

            if 'project_part' in Site_profile:
                if 'sale_starting_date' in Site_profile['project_part']:
                    try:
                        L.append(float(Site_profile['project_part']['sale_starting_date']))
                    except:
                        L.append(0)
                else:
                    L.append(0)

                if 'construction_cost' in Site_profile['project_part']:
                    try:
                        L.append(float(Site_profile['project_part']['building_cost']))
                    except:
                        L.append(0)
                else:
                    L.append(0)
            else:
                L.extend([0,0])

            if'tot' in Site_profile:
                if 'village_tot' in Site_profile['tot']:
                    try:
                        L.append(float(Site_profile['tot']['village_tot']))
                    except:
                        L.append(0)
                else:
                    L.append(0)

                if 'families_tot' in Site_profile['tot']:
                    try:
                        L.append(float(Site_profile['tot']['families_tot']))
                    except:
                        L.append(0)
                else:
                    L.append(0)

                if 'households_tot' in Site_profile['tot']:
                    try:
                        L.append(int(Site_profile['tot']['households_tot']))
                    except:
                        L.append(0)
                else:
                    L.append(0)

                if 'population_tot' in Site_profile['tot']:
                    try:
                        L.append(float(Site_profile['tot']['population_tot']))
                    except:
                        L.append(0)
                else:
                    L.append(0)

                if 'female_tot' in Site_profile['tot']:
                    try:
                        L.append(float(Site_profile['tot']['female_tot']))
                    except:
                        L.append(0)
                else:
                    L.append(0)

                if 'migration_tot' in Site_profile['tot']:
                    try:
                        L.append(float(Site_profile['tot']['migration_<5km']))
                    except:
                        L.append(0)
                else:
                    L.append(0)
            else:
                L.extend([0,0,0,0,0,0])

            if 'less_than_5_km_around_both_in_and_out_commune' in Site_profile and 'population_<5km' in Site_profile['less_than_5_km_around_both_in_and_out_commune']:
                try:
                    L.append(float(Site_profile['less_than_5_km_around_both_in_and_out_commune']['population_<5km']))
                except:
                    L.append(0)
            else:
                L.append(0)

            if 'less_than_5_km_around_both_in_and_out_commune' in Site_profile and 'village_<5km' in Site_profile['less_than_5_km_around_both_in_and_out_commune']:
                try:
                    L.append(float(Site_profile['less_than_5_km_around_both_in_and_out_commune']['village_<5km']))
                except:
                    L.append(0)
            else:
                L.append(0)

            if 'infrastructure_part' in Site_profile and 'primary_school' in Site_profile['infrastructure_part']:
                try:
                    L.append(float(Site_profile['infrastructure_part']['primary_school']))
                except:
                    L.append(0)
            else:
                L.append(0)


            if 'infrastructure_part' in Site_profile and 'classroom(_primary_school)' in Site_profile['infrastructure_part']:
                try:
                    L.append(float(Site_profile['infrastructure_part']['classroom(_primary_school)']))
                except:
                    L.append(0)
            else:
                L.append(0)

            if 'technical_part' in Site_profile and'water_source' in Site_profile['technical_part']:
                L.append(Site_profile['technical_part']['water_source'])
            else:
                L.append(0)

            if 'infrastructure_part' in Site_profile and 'land_of_kiosk' in Site_profile['infrastructure_part']:
                try:
                    L.append(Site_profile['infrastructure_part']['land_of_kiosk'])
                except:
                    L.append(0)
            else:
                L.append(0)

        else:
            for i in range(17):
                L.append(0)

    else:
        if sitename[0] == 'A':
            wave = '2005.0'

        elif sitename[0] in Alphabet:
            wave = str(2007 + Alphabet.index(sitename[0])) + '.0'
        L=[sitename,None,None,None,None,wave,None,None]
        for i in range(17):
            L.append(0)
    print(L)
    return(L)

def get_data_entrepreneurs(sitename):
    query_site = datastore_client.query(kind="Site")
    query_site.add_filter("site","=",sitename)
    query_entity_site = list(query_site.fetch())
    if query_entity_site:
        if 'site_profile' in query_entity_site[0] and 'entrepreneur_information' in query_entity_site[0]['site_profile']:
            Site_profile = json.loads(query_entity_site[0]["site_profile"])
            if 'entrepreneur_name_english' in Site_profile['entrepreneur_information']:
                Name = Site_profile['entrepreneur_information']['entrepreneur_name_english']
            else:
                Name = 0
            if 'generation' in Site_profile['entrepreneur_information']:
                Generation = Site_profile['entrepreneur_information']['generation']
            else:
                Generation = 0
            if 'sex' in Site_profile['entrepreneur_information']:
                Sex = Site_profile['entrepreneur_information']['sex']
            else:
                Sex = 0
            if 'marriage_status' in Site_profile['entrepreneur_information']:
                Marriage_Status = Site_profile['entrepreneur_information']['marriage_status']
            else:
                Marriage_Status = 0
            if 'age' in Site_profile['entrepreneur_information']:
                Age = Site_profile['entrepreneur_information']['age']
            else:
                Age = 0
            if 'entrepreneur_contact' in Site_profile['entrepreneur_information']:
                Contact = Site_profile['entrepreneur_information']['entrepreneur_contact']
            else:
                Contact = 0
            if 'part-time_job' in Site_profile['entrepreneur_information']:
                Part_time_job = Site_profile['entrepreneur_information']['part-time_job']
            else:
                Part_time_job = 0
            if 'previous_job' in Site_profile['entrepreneur_information']:
                Previous_job = Site_profile['entrepreneur_information']['previous_job']
            else:
                Previous_job = 0
            if 'reading' in Site_profile['entrepreneur_information']:
                Reading = Site_profile['entrepreneur_information']['reading']
            else:
                Reading = 0
            if 'writing' in Site_profile['entrepreneur_information']:
                Writing = Site_profile['entrepreneur_information']['writing']
            else:
                Writing = 0
            if 'calculating' in Site_profile['entrepreneur_information']:
                Calculating = Site_profile['entrepreneur_information']['calculating']
            else:
                Calculating = 0
            if 'starting_date' in Site_profile['entrepreneur_information'] and isinstance(Site_profile['entrepreneur_information']['starting_date'],int):
                Starting_date =  Site_profile['entrepreneur_information']['starting_date']
            else:
                Starting_date = 0
            L = [sitename,Name,Generation,Sex,Marriage_Status,Age,Contact,Part_time_job,Previous_job,Reading,Writing,Calculating,Starting_date]
        else:
            L = [sitename] + [0] * 12
    else:
        L = [sitename] + [0] * 12
    print(L)
    return(L)

def get_data_expenses(Data_dict,j): #extract the site, date, expenses reference and expenses amount for one request. argument = dictionnaries of the data from 3. Register Expenses
                                    #and the number of the expense inside this dictionnary (in Data_dict["form"]["site_confirmed"]["display_expense"]["loop"])

    Site = Data_dict["form"]["site_name"]
    Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    try:
        Expenses_ref = Data_dict["form"]["site_confirmed"]["display_expense"]["loop"][j]["enforce_number"]["expense"]
        if not Expenses_ref:
            Expenses_ref = 'unknown_code'
        Expenses_amount = Data_dict["form"]["site_confirmed"]["display_expense"]["loop"][j]["enforce_number"]["amount"]
    except:
        print("error site :" + Site)
        return(Site,Date,None,None)
    return(Site,Date,Expenses_ref,Expenses_amount)

def get_data_ts_expenses(Data_dict): #extract the site, date, expenses reference and expenses amount for one request for the teuk saat fee.
                                     #argument = dictionnaries of the data from 2. Settle Invoices

    Site = Data_dict["form"]["site_name"]
    Assistant_fee_amount = 0
    Expenses_ref = 'entrepreneur_contribution'
    try:
       Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
       return("no date")
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return([Site,Date,Expenses_ref,Assistant_fee_amount])
    if isinstance(item,list):
        for i in range(len(Data_dict["form"]["invoice"]["item"])):
            if item[i].get("name") and item[i]["name"] == "Assistant fee":
                Assistant_fee_amount += int(item[i]["original-amount-owed-to-teuk-saat"])
            elif item[i].get("name") and item[i]["name"] == "Entrepreneur Contribution" and item[i]["original-amount-owed-to-teuk-saat"]:
                Assistant_fee_amount += int(item[i]["original-amount-owed-to-teuk-saat"])
    else:
        if item.get("name") and item["name"] == "Assistant fee":
            Assistant_fee_amount += int(item["original-amount-owed-to-teuk-saat"])
        elif item.get("name") and item["name"] == "Entrepreneur Contribution" and item["original-amount-owed-to-teuk-saat"]:
            Assistant_fee_amount += int(item["original-amount-owed-to-teuk-saat"])
    return([Site, Date, Expenses_ref, Assistant_fee_amount])

def get_data_stock_ts(Data_dict):
    Site = Data_dict["form"]["site_name"]
    Stock_TS_amount = 0
    Expenses_ref = 'stock_ts'
    try:
       Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
       return("no date")
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return([Site,Date,Expenses_ref,Stock_TS_amount])
    if isinstance(item,list):
        for i in range(len(Data_dict["form"]["invoice"]["item"])):
            if item[i].get("name") and item[i]["name"] == "Stock Invoice":
                Stock_TS_amount = item[i]["original-amount-owed-to-teuk-saat"]
    else:
        if item.get("name") and item["name"] == "Stock Invoice":
            Stock_TS_amount = item["original-amount-owed-to-teuk-saat"]
    return([Site, Date, Expenses_ref, Stock_TS_amount])

def get_data_bottle_invoice(Data_dict):
    Site = Data_dict["form"]["site_name"]
    Bottle_amount = 0
    Expenses_ref = 'bottle_invoice'
    try:
       Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
       return("no date")
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return([Site,Date,Expenses_ref,Bottle_amount])
    if isinstance(item,list):
        for i in range(len(Data_dict["form"]["invoice"]["item"])):
            if item[i].get("name") and item[i]["name"] == "Consumable Bottle":
                Bottle_amount = item[i]["original-amount-owed-to-teuk-saat"]
    else:
        if item.get("name") and item["name"] == "Consumable Bottle":
            Bottle_amount = item["original-amount-owed-to-teuk-saat"]
    return([Site, Date, Expenses_ref, Bottle_amount])

def get_data_wins_invoice(Data_dict):
    Site = Data_dict["form"]["site_name"]
    WinS_Amount = 0
    Expenses_ref = 'WinS_invoice'
    try:
       Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
       return("no date")
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return([Site,Date,Expenses_ref,WinS_Amount])
    if isinstance(item,list):
        for i in range(len(Data_dict["form"]["invoice"]["item"])):
            if item[i].get("name") and item[i]["name"] == "school-program":
                WinS_Amount = - int(item[i]["amount-owed-to-entrepreneur"])
    else:
        if item.get("name") and item["name"] == "school-program":
            WinS_Amount = - int(item["amount-owed-to-entrepreneur"])
    return([Site, Date, Expenses_ref, WinS_Amount])

def get_data_debt(Data_dict): #not used as of
    Site = Data_dict["form"]["site_name"]
    Debt = 0
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return([Site,0])
    var = 0
    if isinstance(item,list):
        for i in range(len(Data_dict["form"]["invoice"]["item"])):
            if item[i].get("name") and item[i]["name"] == "debts":
                Debt = - float(item[i]["original-amount-owed-to-teuk-saat"])
                var = 1
    else:
        if item.get("name") and item["name"] == "debts":
            Debt = - float(item["original-amount-owed-to-teuk-saat"])

    if var == 0:
        if Data_dict["form"]["site_confirmed"]["transaction-summary"].get("savings"):
            Debt = Data_dict["form"]["site_confirmed"]["transaction-summary"]["savings"]
    print(Site,Debt)
    return([Site, Debt])

def get_data_technical_intervention_item(Data_dict):
    Site = Data_dict["form"]["site_name"]
    Technical_amount = 0
    Technical_ref = 'technical intervention'
    try:
       Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
       return("no date")
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return([Site,Date,Technical_ref,Technical_amount])
    if isinstance(item,list):
        for i in range(len(Data_dict["form"]["invoice"]["item"])):
            if item[i].get("name") and item[i]["name"].lower() == "technical intervention" or item[i]["name"].lower() == "technical service":
                Technical_amount = item[i]["original-amount-owed-to-teuk-saat"]
    else:
        if item.get("name") and item["name"].lower() == "technical intervention":
            Technical_amount = item["original-amount-owed-to-teuk-saat"]
    return([Site,Date,Technical_ref,Technical_amount])

def get_data_water_alert(Data_dict):
    Site = Data_dict["form"]["site_name"]
    Water_qual_amount = 0
    Water_qual_ref ='water quality alert'
    try:
       Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
       return("no date")
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return([Site,Date,Water_qual_ref,Water_qual_amount])
    if isinstance(item,list):
        for i in range(len(item)):
            if item[i].get("name") and item[i]["name"].lower() == "water quality alert" or item[i]["name"].lower() == "water quality":
                Water_qual_amount = item[i]["original-amount-owed-to-teuk-saat"]
    else:
        if item.get("name") and item["name"].lower() == "water quality alert":
            Water_qual_amount = item["original-amount-owed-to-teuk-saat"]
    return([Site,Date,Water_qual_ref,Water_qual_amount])

def get_data_withdrawal(Data_dict):
    sitename = Data_dict["form"]["site_name"]
    Withdrawal = 0
    Withdrawal_ref = 'withdrawal'
    try:
        Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
        return("no date")
    try:
        Info = Data_dict["form"]["site_confirmed"]
    except:
        return([Site,Date,Water_qual_ref,Water_qual_amount])
    if Info["activity"]["activity"] == 'deposit':
        if Info.get("deposit"):
            if Info["deposit"].get("deposit"):
                Withdrawal = - int(Info["deposit"]["deposit"]["deposit_amount"])
            else:
                Withdrawal = - int(Info["deposit"]["deposit_amount"])
        else:
            return("no date")
    elif Info["activity"]["activity"] == "withdraw":
        if Info.get("withdraw"):
            if Info["withdraw"].get("withdraw"):
                Withdrawal = Info["withdraw"]["withdraw"]["withdraw_amount"]
            else:
                Withdrawal = Info["withdraw"]["withdraw_amount"]
        else:
            return("no date")
    return([sitename,Date,Withdrawal_ref,Withdrawal])


def get_data_partially_paid(Data_dict):
    Site = Data_dict["form"]["site_name"]

    List_invoice= []
    try:
       Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
       return("no data")
    try:
       item = Data_dict["form"]["invoice"]["item"]
    except:
       return("no data")
    if isinstance(item,list):

        for i in range(len(item)):
            Amount_paid = 0
            Invoice_ref = ""
            if item[i]["paid"]==str(1):
                Amount_paid = item[i]["original-amount-owed-to-teuk-saat"]
            elif item[i]["partially-paid"] ==str(1):
                Amount_paid = item[i]["partially-pay"]["amount-paid"]
            if item[i]["name"] == "Assistant fee" or item[i]["name"] == "Entrepreneur Contribution":
                Invoice_ref = "entrepreneur_contribution"
                List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
            elif item[i]["name"] == "Stock Invoice":
                Invoice_ref = "stock_ts"
                List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
            elif item[i]["name"] == "Technical intervention":
                Invoice_ref = "technical intervention"
                List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
            elif item[i]["name"] == "Water Quality Alert":
                Invoice_ref = "water quality alert"
                List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
            elif item[i]["name"] == "Consumable Bottle":
                Invoice_ref = "bottle_invoice"
                List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
            elif item[i]["name"] == "school-program":
                if item[i]["paid"] == str(1):
                    Amount_paid = - int(item[i]["amount-owed-to-entrepreneur"])
                Invoice_ref = "WinS_invoice"
                List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
            elif item[i]["name"] == "debts":
                Invoice_ref = "debt"
                List_invoice.append([Site,Date,Invoice_ref,Amount_paid])

    else:
        Amount_paid = 0
        Invoice_ref = ""
        if item["paid"]==1:
            Amount_paid = item["original-amount-owed-to-teuk-saat"]
        elif item["partially-paid"] == 0:
            Amount_paid = item["partially-pay"]["amount-paid"]
        if item["name"] == "Assistant fee" or item["name"] == "Entrepreneur Contribution":
            Invoice_ref = "entrepreneur_contribution"
            List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
        elif item["name"] == "Stock Invoice":
            Invoice_ref = "stock_ts"
            List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
        elif item["name"] == "Technical intervention":
            Invoice_ref = "technical intervention"
            List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
        elif item["name"] == "Water Quality Alert":
            Invoice_ref = "water quality alert"
            List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
        elif item["name"] == "Consumable Bottle":
            Invoice_ref = "bottle_invoice"
            List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
        elif item["name"] == "school-program":
            if item["paid"] == str(1):
                Amount_paid = - int(item["amount-owed-to-entrepreneur"])
            Invoice_ref = "WinS_invoice"
            List_invoice.append([Site,Date,Invoice_ref,Amount_paid])
        elif item["name"] == "debts":
            Invoice_ref = "debt"
            List_invoice.append([Site,Date,Invoice_ref,Amount_paid])

    return(List_invoice)


def get_data_sale(Data_dict):

    """
    Create a list with all the data (jugs sold, income, price) for one site and one month for the distrubtion channel :
    - Home delivery
    - Shopkeeper
    - On site
    - School
    - Free
    - Bottle
    - Other (total sales - le reste)
    + number of open days this month
    Taking in parameters :  dictionnaries of the data from 1. Register Sales
    """

    Site = Data_dict["form"]["site_name"]
    Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    Total_jugs_sold = Total_income = Total_price_average= 0
    if Data_dict["form"]["site_confirmed"].get("display"):
       try:
           Total_jugs_sold = int(Data_dict["form"]["site_confirmed"]["display"]["total-sales-all-channels"])
           Total_income =  int(Data_dict["form"]["site_confirmed"]["display"]["total-cash-all-channels"])
           Total_price_average = Total_income/Total_jugs_sold
       except:
           pass
    if Data_dict["form"]["site_confirmed"].get("sale-channel"):
        Tab_channel = Data_dict["form"]["site_confirmed"]["sale-channel"]
        Free_jugs_sold=Hod_jugs_sold=Hod_jugs_price=Hod_income=Shopkeeper_jugs_sold=Shopkeeper_jugs_price=Shopkeeper_income= 0
        Onsite_jugs_sold=Onsite_jugs_price=Onsite_income=School_income=School_jugs_sold=School_jugs_price=Bottle_jugs_price= 0
        Bottle_jugs_sold=Bottle_income= Other_jugs_sold = Other_income = Other_price = 0
        for j in range(len(Tab_channel)):
            if not isinstance(Tab_channel,list):
               Tab_channel = [Tab_channel]
            if Tab_channel[j]: #checking if the list is empty
                if Tab_channel[j]["enforce-repeats"]["channel-list"]["channel-text"]=="free":
                   try :
                       Free_jugs_sold += int((Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"]))
                   except:
                       pass

                elif Tab_channel[j]["enforce-repeats"]["channel-list"]["channel-text"]=="hod":
                   try:
                       Hod_jugs_sold += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])
                       Hod_income += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])*int(Tab_channel[j]["enforce-repeats"]["channel-list"]["price"])
                       if Hod_jugs_sold != 0:
                           Hod_jugs_price = Hod_income/Hod_jugs_sold
                   except:
                       pass

                elif Tab_channel[j]["enforce-repeats"]["channel-list"]["channel-text"]=="shopkeeper":
                    try:
                       Shopkeeper_jugs_sold += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])
                       Shopkeeper_income += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])*int(Tab_channel[j]["enforce-repeats"]["channel-list"]["price"])
                       if Shopkeeper_jugs_sold != 0:
                           Shopkeeper_jugs_price = Shopkeeper_income/Shopkeeper_jugs_sold
                    except:
                       pass

                elif Tab_channel[j]["enforce-repeats"]["channel-list"]["channel-text"]=="onsite":
                    try:
                        Onsite_jugs_sold += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])
                        Onsite_income += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])*int(Tab_channel[j]["enforce-repeats"]["channel-list"]["price"])
                        if Onsite_jugs_sold != 0:
                            Onsite_jugs_price = Onsite_income/Onsite_jugs_sold
                    except:
                        pass

                elif Tab_channel[j]["enforce-repeats"]["channel-list"]["channel-text"]=="school":
                    try:
                       School_jugs_sold += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])
                       School_income += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])*int(Tab_channel[j]["enforce-repeats"]["channel-list"]["price"])
                       if School_jugs_sold != 0:
                          School_jugs_price = School_income/School_jugs_sold
                    except:
                          pass

                elif Tab_channel[j]["enforce-repeats"]["channel-list"]["channel-text"]=="bottle" or  Tab_channel[j]["enforce-repeats"]["channel-list"]["channel-text"]=="other-bottles":
                    try:
                        Bottle_jugs_sold += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])
                        Bottle_income += int(Tab_channel[j]["enforce-repeats"]["display"]["total-sales-for-channel"])*int(Tab_channel[j]["enforce-repeats"]["channel-list"]["price"])
                        if Bottle_jugs_sold != 0:
                            Bottle_jugs_price = Bottle_income/Bottle_jugs_sold
                    except:
                        pass
        Other_jugs_sold = Total_jugs_sold - Free_jugs_sold - Hod_jugs_sold - Shopkeeper_jugs_sold - Onsite_jugs_sold - School_jugs_sold - Bottle_jugs_sold
        Other_income = Total_income - Hod_income - Shopkeeper_income - Onsite_income - School_income - Bottle_income
        if Other_jugs_sold > 0:
            Other_price = Other_income / Other_jugs_sold

        Number_open_days = get_data_open_days(Data_dict)
        L = [Site, Date, Total_jugs_sold, Total_income, Total_price_average, Hod_jugs_sold,
             Hod_income,Hod_jugs_price,Shopkeeper_jugs_sold, Shopkeeper_income, Shopkeeper_jugs_price,
             School_jugs_sold,School_income,School_jugs_price,
             Onsite_jugs_sold,Onsite_income,Onsite_jugs_price, Free_jugs_sold,
             Bottle_jugs_sold,Bottle_income,Bottle_jugs_price,
             Other_jugs_sold, Other_income, Other_price, Number_open_days]
    else :
        L=[Site, Date,Total_jugs_sold,Total_income,Total_price_average] + [0]*20
    return(L)

def get_data_indicators(Data_dict):
    Site = Data_dict["form"]["site_name"]
    try:
        Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
        return("no date")
    try:
        Number_Operators = Data_dict["form"]["site_confirmed"]["operators"]["operators_number"]
    except:
        Number_Operators = 0
    try:
        Number_Bottles_in_Operation = Data_dict["form"]["site_confirmed"]["bottles"]["bottles_operation"]
    except:
        Number_Bottles_in_Operation = 0
    try:
        Number_Bottles_in_Stock = Data_dict["form"]["site_confirmed"]["bottles"]["bottles_stock"]
    except:
        Number_Bottles_in_Stock = 0
    try:
        Number_Bottles_Broken_Lost = Data_dict["form"]["site_confirmed"]["bottles"]["bottles_broken_lost"]
    except:
        Number_Bottles_Broken_Lost=0
    if not Data_dict["form"]["site_confirmed"]["loss"]["water_consumed"]== '' and int(Data_dict["form"]["site_confirmed"]["loss"]["water_consumed"].split('.',1)[0]) > 0:
            Water_Consume = Data_dict["form"]["site_confirmed"]["loss"]["water_consumed"].split('.',1)[0]
    else:
            Water_Consume = 0

    if not Data_dict["form"]["machine_begining"] == '' and int(Data_dict["form"]["machine_begining"].split('.',1)[0]) > 0:
            Machine_begining = Data_dict["form"]["machine_begining"].split('.',1)[0]
    else:
        Machine_begining = 0
    try:
        if not Data_dict["form"]["site_confirmed"]["production"]["machine_end"] == '' and int(Data_dict["form"]["site_confirmed"]["production"]["machine_end"].split('.',1)[0]) > 0:
            Machine_end = Data_dict["form"]["site_confirmed"]["production"]["machine_end"].split('.',1)[0]
        else :
            Machine_end = 0
    except:
        Machine_end = 0
    try:
        if not Data_dict["form"]["water_begining"] == '' and int(Data_dict["form"]["water_begining"].split('.',1)[0]) > 0:
            Water_begining = Data_dict["form"]["water_begining"].split('.',1)[0]
        else :
            Water_begining = 0
    except:
        Water_begining = 0
    try:
        if not Data_dict["form"]["site_confirmed"]["production"]["water_end"] == '' and int(Data_dict["form"]["site_confirmed"]["production"]["water_end"].split('.',1)[0]) > 0:
            Water_end = Data_dict["form"]["site_confirmed"]["production"]["water_end"].split('.',1)[0]
        else :
            Water_end = 0
    except:
        Water_end = 0
    try:
        if not Data_dict["form"]["site_confirmed"]["operators"]["how_much_money_does_entrepreneur_save_outside_ts"] == '' and int(Data_dict["form"]["site_confirmed"]["operators"]["how_much_money_does_entrepreneur_save_outside_ts"].split('.',1)[0]) > 0:
            Saving_outsidets = Data_dict["form"]["site_confirmed"]["operators"]["how_much_money_does_entrepreneur_save_outside_ts"]
        else :
            Saving_outsidets = 0
    except:
        Saving_outsidets = 0
    L = [Site, Date, Number_Operators, Number_Bottles_in_Operation, Number_Bottles_in_Stock, Number_Bottles_Broken_Lost, Water_Consume,Machine_begining,Machine_end,Water_begining,Water_end,Saving_outsidets]
    #print(L)
    return(L)

def get_data_vehicles(Data_dict):
    Site = Data_dict["form"]["site_name"]
    try:
        Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    except:
        return("no date")
    try:
        if Data_dict['form']['site_confirmed']['station_mgmt_sales']['transportation']['transportation']:
            Delivery_vehicle = Data_dict['form']['site_confirmed']['station_mgmt_sales']['transportation']['transportation']
        else:
            Delivery_vehicle = 0
    except:
        Delivery_vehicle = 0
    try:
        if Data_dict['form']['site_confirmed']['station_mgmt_sales']['deliveries']['"total_number_of_disinfection_per_month": ']:
            Disinfection = Data_dict['form']['site_confirmed']['station_mgmt_sales']['deliveries']['"total_number_of_disinfection_per_month": ']
        else:
            Disinfection = 0
    except:
        Disinfection = 0

    try:
        if Data_dict['form']['site_confirmed']['station_mgmt_sales']['deliveries']['deliveries']:
            Deliveries = Data_dict['form']['site_confirmed']['station_mgmt_sales']['deliveries']['deliveries']
        else:
            Deliveries = 0
    except:
        Deliveries = 0

    return([Site,Date,Delivery_vehicle,Disinfection,Deliveries])

def get_tier(Sitename,Current_date,Total_sales_this_month):

    mostRecentDate = Current_date #- relativedelta(months=+1)
    Date2 = Current_date - relativedelta(months=+12)
    query = con.execute("SELECT SUM(Total_Sales),Id_Site FROM Sales WHERE Month <= %s AND Month > %s AND Id_Site = %s", (Date2, date(2016,1,1),Sitename))
    SalesM1 = query.fetchall()
    query = con.execute("SELECT SUM(Total_Sales - Bottle_Sales),Id_Site FROM Sales Where Month <= %s AND Month > %s AND Id_Site = %s", (mostRecentDate,Date2,Sitename))
    List_volumeM1 = query.fetchall()
    Date_minus_4_month = Current_date - relativedelta(months=+4)
    query = con.execute("SELECT Sum(Total_Sales),Id_Site FROM Sales WHERE Month <= %s AND Month > %s AND Id_Site = %s", (mostRecentDate,Date_minus_4_month,Sitename))
    Sales_inactiveM1 = query.fetchall()
    Opened_month = CalculNombreMoisOuverture(Sitename,mostRecentDate,Date2)
    Opened_day = Numberdaysopeningyear(Sitename,mostRecentDate,Date2,Opened_month)
    if not SalesM1 or not SalesM1[0][0]:
        SalesM1 = [(0,)]
    if not List_volumeM1 or not List_volumeM1[0][0]:
        List_volumeM1 = [(0,)]
    if not Sales_inactiveM1 or not Sales_inactiveM1[0][0]:
        Sales_inactiveM1 = [(0,)]

    Salestot = SalesM1[0][0]
    List_volumetot = List_volumeM1[0][0] + Total_sales_this_month
    Sales_inactivetot = Sales_inactiveM1[0][0] + Total_sales_this_month

    if (not Salestot or Salestot == 0) and (List_volumetot and List_volumetot > 0):
        Tier = "New"
    elif Opened_month < 9 and (List_volumetot and List_volumetot > 0):
        if not Sales_inactivetot or not Sales_inactivetot or Sales_inactivetot==0:
            Tier = "Inactive"
        else:
            Tier = "Reopen"
    else:
        if Opened_month != 0 and (List_volumetot)*20/Opened_day > 1700:
            Tier = "1"
        elif Opened_month != 0 and  List_volumetot*20/Opened_day > 1200:
            Tier = "2"
        elif Opened_month != 0 and List_volumetot*20/Opened_day > 0:
            Tier = "3"
        else:
            Tier = "Closed"
    return(Tier)

def CalculNombreMoisOuverture(Sitename,mostRecentDate,Date2):
    query = con.execute("SELECT Number_open_days,Id_SIte FROM Sales WHERE Month <= %s AND Month > %s AND Id_Site = %s", [mostRecentDate,Date2,Sitename])
    OpenDays = query.fetchall()
    Open_Month = 0
    for k in range(len(OpenDays)):
        if OpenDays[k][0] and OpenDays[k][0] > 0:
            Open_Month += 1
    return(Open_Month)

def Numberdaysopeningyear(Sitename,mostRecentDate,Date2,Open_month):
    query = con.execute("SELECT Number_open_days,Month,Id_Site FROM Sales Where Month <= %s AND Month > %s AND Id_Site = %s", (mostRecentDate,Date2,Sitename))
    L_open_days = query.fetchall()
    Nb_days_this_year = 0
    for i in range(len(L_open_days)):
        if L_open_days[i][0] < 20:
            Nb_days_this_year += L_open_days[i][0]
        else:
            Nb_days_this_year += timedelta(monthrange(L_open_days[i][1].year,L_open_days[i][1].month)[1]).days
    return(Nb_days_this_year)

def get_data_flash_report(Data_dict):
    Site = Data_dict["form"]["site_name"]
    Date = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y')
    if 'copy-1-of-site_name' in Data_dict["form"]:
        if 'number_of_villager' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_villager']:
            Number_jugs_village = Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_villager']
        else:
            Number_jugs_village = 0

        if 'number_of_school' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_school']:
            Number_jugs_school = Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_school']
        else:
            Number_jugs_school = 0

        if 'total_number_of_working_day' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['total_number_of_working_day']:
            Open_days = Data_dict["form"]['copy-1-of-site_name']['flash_report']['total_number_of_working_day']
        else:
            Open_days = 0

        if 'comment' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['comment']:
            Comment = Data_dict["form"]['copy-1-of-site_name']['flash_report']['comment']
        else:
            Comment = 0

        # if 'number_of_delivery' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_delivery']:
        #     Number_of_delivery = Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_delivery']
        # else:
        #     Number_of_delivery = 0

        # if 'number_of_villager' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_villager']:
        #     Number_of_deinfection =  Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_denifectionmonth']
        # else:
        #     Number_of_deinfection = 0

        # if 'moto_cart' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['moto_cart']:
        #     Moto_cart = Data_dict["form"]['copy-1-of-site_name']['flash_report']['moto_cart']
        # else:
        #     Moto_cart = 0
        #
        # if 'by_koyon' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['by_koyon']:
        #     Kuyon = Data_dict["form"]['copy-1-of-site_name']['flash_report']['by_koyon']
        # else:
        #     Kuyon = 0
        #
        # if 'by_car' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['by_car']:
        #     Car  = Data_dict["form"]['copy-1-of-site_name']['flash_report']['by_car']
        # else:
        #     Car = 0
        #
        # if 'number_of_working_staff' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_working_staff']:
        #     Staff = Data_dict["form"]['copy-1-of-site_name']['flash_report']['number_of_working_staff']
        # else:
        #     Staff = 0
        #
        # if 'does_entrepreneur_change_recently' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['does_entrepreneur_change_recently']:
        #     Change_entrepreneur = Data_dict["form"]['copy-1-of-site_name']['flash_report']['does_entrepreneur_change_recently']
        # else:
        #     Change_entrepreneur = "no"
        #
        # print(Data_dict["form"]['copy-1-of-site_name']['flash_report']['entrepreneur_name'])
        # if 'entrepreneur_name' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['entrepreneur_name']:
        #     Entrepreneur_name = Data_dict["form"]['copy-1-of-site_name']['flash_report']['entrepreneur_name']
        # else:
        #     Entrepreneur_name = 0
        #
        # if 'phone_number' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['phone_number']:
        #     Phone_number = Data_dict["form"]['copy-1-of-site_name']['flash_report']['phone_number']
        # else:
        #     Phone_number = 0
        #
        # if 'what_is_old_entrepreneur_name' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['what_is_old_entrepreneur_name']:
        #     Old_name = Data_dict["form"]['copy-1-of-site_name']['flash_report']['what_is_old_entrepreneur_name']
        # else:
        #     Old_name = 0
        #
        # if 'what_was_the_reason_he_left' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['what_was_the_reason_he_left']:
        #     Reason_for_leaving = Data_dict["form"]['copy-1-of-site_name']['flash_report']['what_was_the_reason_he_left']
        # else:
        #     Reason_for_leaving = 0
        #
        # if 'entrepreneur_id' in Data_dict["form"]['copy-1-of-site_name']['flash_report'] and Data_dict["form"]['copy-1-of-site_name']['flash_report']['entrepreneur_id']:
        #     Entrepreneur_ID = Data_dict["form"]['copy-1-of-site_name']['flash_report']['entrepreneur_id']
        # else:
        #     Entrepreneur_ID = 0


        L = [Site,Date,Number_jugs_village,Number_jugs_school, Open_days, Comment]
    else:
        L=[Site,Date,0,0,0,0]
    return(L)

def get_data_consumable(Data_dict,item,i): #i number of the item in the list

    sitename = Data_dict["form"]["site_name"]
    if "please_select_date_you_want_to_order" in Data_dict["form"]:
        #print("here")
        month_intermediary = datetime.datetime.strptime(Data_dict["form"]["please_select_date_you_want_to_order"],'%Y-%m-%d')
        month = date(month_intermediary.year,month_intermediary.month,1)
    elif 'month' in Data_dict["form"] and 'year' in Data_dict["form"]:
        month = datetime.datetime.strptime(Data_dict["form"]["month"] + "-" + Data_dict["form"]["year"], '%m-%Y') + relativedelta(months=+1)
    else:
        return([0,0,0,0,0,0,0,0,0])
    if 'date' in Data_dict["form"]:
        submitted_date = datetime.datetime.strptime(Data_dict["form"]["date"],'%Y-%m-%d')
    else:
        submitted_date = 0
    category_number = item[2]
    Number_item = Price_item = 0
    Khmer_name_item = English_name_item = Unit = ''
    #print(Data_dict["form"]["site_confirmed"]["category" + str(category_number)])
    if Data_dict["form"].get("site_confirmed"):
        if Data_dict["form"]["site_confirmed"]["category" + str(category_number)].get(str(item)) and Data_dict["form"]["site_confirmed"]["category" + str(category_number)].get(str(item)).isdigit():
            Number_item = int(Data_dict["form"]["site_confirmed"]["category" + str(category_number)][item])
        if Data_dict["form"]["site_confirmed"]["category" + str(category_number)].get('price_' + str(item)) and Data_dict["form"]["site_confirmed"]["category" + str(category_number)].get('price_' + str(item)).isdigit():
            Price_item = int(Data_dict["form"]["site_confirmed"]["category" + str(category_number)]['price_' + str(item)])
            # if int(Price_item)=0:
            #     return("No request")
        if isinstance(Data_dict["form"]["price_list"]["item"],list):
            Khmer_name_item = Data_dict["form"]["price_list"]["item"][i]["kh"]
            English_name_item = Data_dict["form"]["price_list"]["item"][i]["eng"]
            Unit = Data_dict["form"]["price_list"]["item"][i]["unit"]
    #print([sitename,month,submitted_date,category_number,item,Number_item,Price_item,Khmer_name_item,English_name_item,Unit])
    return([sitename,month,submitted_date,category_number,item,Number_item,Price_item,Khmer_name_item,English_name_item,Unit])


def get_data_Entrepreneur_resignation(Data_dict):
    Data_resignation = []
    Data_new_ent = []
    if Data_dict["form"].get("site_confirmed"):
        Site_name = Data_dict["form"]["site_name"]
        if Data_dict["form"]["site_confirmed"].get("entrepreneur_resignation"):
            Ent_english_name = Data_dict["form"]["site_confirmed"]["entrepreneur_resignation"]["entrepreneur_english_name"]
            Ent_khmer_name = Data_dict["form"]["site_confirmed"]["entrepreneur_resignation"]["entrepreneur_khmer_name"]
            Reason_for_leaving = Data_dict["form"]["site_confirmed"]["entrepreneur_resignation"]["reason_for_leaving"]
            Sex = Data_dict["form"]["site_confirmed"]["entrepreneur_resignation"]["sex"]
            Site_status = Data_dict["form"]["site_confirmed"]["entrepreneur_resignation"]["site_status"]
            Resignation_date = Data_dict["form"]["site_confirmed"]["entrepreneur_resignation"]["when_did_heshe_resign"]

            Data_resignation = [Site_name,Ent_english_name,Ent_khmer_name,Reason_for_leaving,Sex,Site_status,Resignation_date]

        if Data_dict["form"]["site_confirmed"].get("new_entrepreneur_recruitment"):
            Ent_english_name = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["entrepreneur_name_english"]
            Ent_khmer_name = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["entrepreneur_khmer_name"]
            Date_start_working = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["date_start_working_in_station"]
            Education = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["education"]
            Sex = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["sex"]
            Phone_number = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["first_phone_number"]
            Second_phone_number = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["second_phone_number"]
            Commune_village = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["commune__village"]
            Date_of_birth = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["date_of_birth"]
            Province = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["province"]
            Previous_job = Data_dict["form"]["site_confirmed"]["new_entrepreneur_recruitment"]["what_does_he_do_before_joining_ts"]

            Data_new_ent = [Site_name,Ent_english_name,Ent_khmer_name,Date_start_working,Education,Sex,Phone_number,Second_phone_number,Commune_village,Date_of_birth,Province,Previous_job]

    return(Data_resignation,Data_new_ent)




if __name__ == '__main__':
    #print(get_tier('H4',date(2019,9,1),0))
    pass
