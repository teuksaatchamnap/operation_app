import db
from sqldb.Script_Get_Data import get_data_site, get_data_entrepreneurs
from monthlyreport.Functionutils import listSite
import pandas as pd
import os
from google.cloud import datastore
import json
import datetime
from datetime import date
from tools.ROMInfo import ROMinfo
import flask
import os
import sqlalchemy
from pymysql.constants import CLIENT

con = db.pool.connect()

def UpdateSite():
    ListSite = listSite()
    for sitename in ListSite:
        Querytest = con.execute("SELECT Id_Site FROM Sites WHERE Id_Site = %s", sitename)
        Test = Querytest.fetchall()
        print(sitename)
        data = get_data_site(sitename[0])
        if not Test:
            query = ("INSERT INTO Sites (Id_Site, Platform, Project, Office, Province, Code_Province, Wave, Longitude, Latitude, Village, Commune, District,Village_khmer,Commune_khmer,District_khmer=%s,Province_khmer, Sale_Starting_Date, Building_cost, Number_Village, Family, Households, Population, Female, Migration, Population5km,Number_Village_5km, Primary_School, Classroom, Water_Source)"
                    "VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s)")
            con.execute(query,data)
            con.execute("UPDATE Sites SET Old_Platform = %s WHERE Id_Site = %s",(data[1],data[0]))
        elif Test:
            query = con.execute("SELECT Last_Tier FROM Sites WHERE Id_Site = %s", sitename)
            Tier = query.fetchone()
            query = con.execute("SELECT Wave FROM Sites WHERE Id_Site = %s",data[0]).fetchone()
            if Tier and Tier [0]!= 'Closed':
                if not data[1] or (data[1]).lower() == 'stop':
                    print(data[0],data[5])
                    con.execute("UPDATE Sites SET Platform = 'Dead', Office = 'Dead',Province = %s,Code_Province=%s,Longitude = %s, Latitude = %s, Village = %s, Commune = %s, District = %s,Village_khmer = %s,Commune_khmer=%s,District_khmer=%s,Province_khmer=%s, Sale_Starting_Date = %s, Building_cost = %s, Number_Village = %s, Family = %s, Households = %s, Population = %s, Female = %s, Migration = %s, Population5km = %s,Number_Village_5km = %s, Primary_School = %s, Classroom = %s, Water_Source = %s,Land_of_kiosk = %s WHERE Id_Site = %s", (data[4],data[5],data[7],data[8],data[9],data[10],data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],data[20],data[21],data[22],data[23],data[24],data[25],data[26],data[27],data[28],data[29],data[0]))
                    if not query or not query[0]:
                        con.execute("UPDATE Sites SET Wave = %s WHERE Id_Site = %s",(data[6],data[0]))
                else:
                    con.execute("UPDATE Sites SET Platform = %s, Old_Platform = %s, Project = %s, Office = %s,Province = %s,Code_Province=%s,Longitude = %s, Latitude = %s, Village = %s, Commune = %s, District = %s,Village_khmer = %s,Commune_khmer=%s,District_khmer=%s,Province_khmer=%s, Sale_Starting_Date = %s, Building_cost = %s, Number_Village = %s, Family = %s, Households = %s, Population = %s, Female = %s, Migration = %s, Population5km = %s,Number_Village_5km = %s, Primary_School = %s, Classroom = %s, Water_Source = %s,Land_of_kiosk = %s WHERE Id_Site = %s", (data[1],data[1],data[2],data[3],data[4],data[5],data[7],data[8],data[9],data[10],data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],data[20],data[21],data[22],data[23],data[24],data[25],data[26],data[27],data[28],data[29],data[0]))
                    if not query or not query[0]:
                        con.execute("UPDATE Sites SET Wave = %s WHERE Id_Site = %s",(data[6],data[0]))
            elif Tier and Tier[0] == 'Closed':
                #print(data)
                if not data[1] or (data[1]).lower() == 'stop' or (data[1]).lower() == 'dead':
                    print(data[0],data[5])
                    con.execute("UPDATE Sites SET Platform = 'Dead', Office = 'Dead',Province = %s,Code_Province=%s,Longitude = %s, Latitude = %s, Village = %s, Commune = %s, District = %s,Village_khmer = %s,Commune_khmer=%s,District_khmer=%s,Province_khmer=%s, Sale_Starting_Date = %s, Building_cost = %s, Number_Village = %s, Family = %s, Households = %s, Population = %s, Female = %s, Migration = %s, Population5km = %s,Number_Village_5km = %s, Primary_School = %s, Classroom = %s, Water_Source = %s,Land_of_kiosk = %s WHERE Id_Site = %s", (data[4],data[5],data[7],data[8],data[9],data[10],data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],data[20],data[21],data[22],data[23],data[24],data[25],data[26],data[27],data[28],data[29],data[0]))
                    if not query or not query[0]:
                        con.execute("UPDATE Sites SET Wave = %s WHERE Id_Site = %s",(data[6],data[0]))
                else:
                    con.execute("UPDATE Sites SET Platform = %s,Old_Platform = %s, Project = %s, Province = %s,Code_Province=%s, Village = %s, Commune = %s, District = %s,Village_khmer = %s,Commune_khmer=%s,District_khmer=%s,Province_khmer=%s,Sale_Starting_Date = %s, Building_cost = %s, Number_Village = %s, Family = %s, Households = %s, Population = %s, Female = %s, Migration = %s, Population5km = %s,Number_Village_5km = %s, Primary_School = %s, Classroom = %s, Water_Source = %s,Land_of_kiosk = %s WHERE Id_Site = %s", (data[1],data[1],data[2],data[4],data[5],data[9],data[10],data[11],data[12],data[13],data[14],data[15],data[16],data[17],data[18],data[19],data[20],data[21],data[22],data[23],data[24],data[25],data[26],data[27],data[28],data[29],data[0]))
                    if not query or not query[0]:
                        con.execute("UPDATE Sites SET Wave = %s WHERE Id_Site = %s",(data[6],data[0]))

    return("ok")

def UpdateEntrepreneurs():
    ListSite = listSite()
    for sitename in ListSite:
        query = con.execute("SELECT Id_Site FROM Entrepreneurs WHERE Id_Site = %s", sitename)
        Test_entrepreneur = query.fetchall()
        data_entrepreneur = get_data_entrepreneurs(sitename[0])
        print(sitename)
        if not Test_entrepreneur:
            query = ("INSERT INTO Entrepreneurs(Id_Site,Entrepreneur_Name,Generation,Sex,Marriage_Status,Age,Contact,Part_time_job,Previous_Job,Reading,Writing,Calculating,Starting_Date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
            con.execute(query,data_entrepreneur)

        elif Test_entrepreneur:
            con.execute("UPDATE Entrepreneurs SET Id_Site = %s, Entrepreneur_Name = %s, Generation = %s, Sex = %s, Marriage_Status = %s, Age = %s, Contact = %s, Part_time_job = %s, Previous_Job = %s, Reading = %s, Writing = %s, Calculating = %s,Starting_Date = %s WHERE Id_Site = %s",(data_entrepreneur+[sitename[0]]))
    return("ok")

def UpdatePlatform():
    con.execute("DELETE FROM Platform")
    
    # Name_platform = list(data_dict)
    # for i in range(len(data_dict)):
    #     con.execute("INSERT INTO Platform(Code_Platform,Cashier) VALUES (%s,%s)",(Name_platform[i]),data_dict[Name_platform[i]])
    #     #con.execute("UPDATE Platform SET Cashier = %s WHERE Code_Platform = %s",data_dict[Name_platform[i]],Name_platform[i])

    ROM_info = [
        ['SR', 'kimhong.p@teuksaat1001.com'],
        ['PP', 'lim.t@teuksaat1001.com'],
        ['BTB', 'yet.y@teuksaat1001.com'],
        ['BTB', 'vanra.p@teuksaat1001.com'],
        ['KC', 'bun.ph@teuksaat1001.com'],
        ['KSP', 'rethy.m@teuksaat1001.com']
    ]
    for code_platform, mail_rom in ROM_info:
        con.execute("INSERT INTO Platform (Code_Platform, Mail_ROM) VALUES (%s, %s)", (code_platform, mail_rom))
        print((code_platform, mail_rom))
    
    datastore_client = datastore.Client.from_service_account_json(flask.current_app.root_path+'/certs/client_secret_appengine.json')
    query_platform = datastore_client.query(kind="Configuration")
    query_platform.add_filter("name","=","cashiers")
    query_entity_platform = list(query_platform.fetch())
    data_dict = json.loads(query_entity_platform[0]["value"])
    Name_Platform = con.execute("SELECT DISTINCT Code_Platform FROM Platform").fetchall()
    for i in range(len(Name_Platform)):
        con.execute("UPDATE Platform SET Cashier = %s WHERE Code_Platform = %s",data_dict[Name_Platform[i][0]],Name_Platform[i][0])


    con.execute("""UPDATE Sites SET Old_platform = Platform WHERE Platform <> 'Dead' AND Platform <> ''""")
    return("ok")

def ImportSiteProfile(doc):
    df = pd.read_excel(doc,skiprows=2)
    SiteExisting = con.execute("SELECT Id_Site FROM Sites").fetchall()
    ListSiteInDB = [i[0] for i in SiteExisting]
    # ListColumn = ['Site_Name','Site_Name_Khmer','Platform','Code_Village','Code_Commune','Code_District','Code_Province',
    #                 'Village_khmer','Commune_khmer','District_khmer','Province_khmer','Village','District','Commune','Province','Lati','Longi',
    #                 'ProjectAgreement','Wave','Sale_Starting_Date','Funder_1','Funder_2','Funder_3','Building_cost',
    #                 'Number_Village','Number_Family','Number_Households','Number_Population','Number_Women','Number_Migration',
    #                 'Number_Village_5km','Number_Family_5km','Number_Households_5km','Number_Population_5km','Number_Women_5km','Number_Migration_5km',
    #                 'Number_Pagoda','Number_Primary_School','Land_of_kiosk','Paved_Asphalt_Road','Concrete_Road','Laterite_Road','White_Soiled_Road','Road_Leading_to_Kiosk',
    #                 'Monthly_Income_Average_per_Person','Labour_Market','Monthly_Income_Average_per_Worker','Water_Source','Well_Pond_Ownership',
    #                 'Depth_Well_Pond','Water_Source_Distance_From_Kiosk','Second_Water_Source','Well_Pond_Ownership_Second_Source','Depth_Well_Pond_Second_Source',
    #                 'Water_Source_Distance_From_Kiosk_Second_Source','Main_Power_Source','Second_Power_Source','Type_of_Water_Tank']

    ListColumn = ['Site Name','Site Name Khmer','Platform','Code Village','Code Commune','Code District','Code Province','Village Khmer','Commune Khmer',
                        'District Khmer','Province Khmer','Village','Commune','District','Province','Latitude','Longitude',
                        'Project Agreement','Batch','Sale Starting Date','Funder 1','Funder 2','Funder 3','Construction Cost',
                        '#Villages','#Families','#Households','#Population','#Women','#Migration','#Villages <5km','#Families <5km',
                        '#Households <5km','#Population <5km','#Women <5km','#Migration <5km','#Pagodas','#Primary School',
                        'Land of Kiosk','% of Paved Asphalt Road','% Concrete Road','% Laterite Road','% White-Soiled Road'
                        ,'Road Leading to Kiosk','Monthly Avg Inc/Pers','Labour Market','Monthly Avg Inc/Worker','Main Water Source',
                        'Well or Pond Ownership','Depth of Well or Pond','Water Source distance from Kiosk','Second Water Source',
                        'Well or Pond Ownership (second source)','Depth of Well or Pond (second source)','Water Source distance from Kiosk (second source)',
                        'Main power source','Second power source','Type of water tank']

    # # SELECT ONLY THE COLUMN WANTED
    # df = df[ListColumn]
    # print(df)

    # # Create the SQLAlchemy engine
    
    # engine = db.pool

    # # Write to SQL
    # df.set_index('Id_Site', inplace=True)
    # df.to_sql('sites2', engine, if_exists='replace')
    for index,row in df.iterrows():
        if row[0] != 0 and row[0] != "Code_Site":
            ListData = []
            if row[0] not in ListSiteInDB and not pd.isnull(row[0]):
                con.execute("INSERT INTO Sites(Id_Site) VALUES (%s)",row[0])
            for i in ListColumn:
                # if i != row['Code_Site'] and i != row['Advisor'] and i != row['Tier'] and i != row['Code'] and i != row['Khmer'] and i != row['English'] and i != row['GPS'] and i != row['Project'] and i != row['Total'] and i != row['<5km'] and i != row['>5km'] and i != row['Land'] and i != row['Road'] and i != row['Economic'] and i != row['1st Water Source'] and i != row['2nd Water Source'] and i != row['Power Source'] and i != row['General'] and i != row['Education'] and i != row['Adress'] and i != row['Other'] and i != row['#Villages >5km'] and i != row['#Families >5km'] and i != row['#Households >5km'] and i != row['#Population >5km'] and i != row['#Women >5km'] and i != row['#Migration >5km']:
                #     print(i)
                if pd.isnull(row[i]):
                    ListData.append(None)
                else:
                    ListData.append(row[i])
            ListData.append(row[0])
            con.execute("""UPDATE Sites SET 
                        Site_Name = %s,
                        Site_Name_Khmer = %s,
                        Platform = %s,
                        Code_Village = %s,
                        Code_Commune = %s,
                        Code_District = %s,
                        Code_Province_INT = %s,
                        Village_khmer = %s,
                        Commune_khmer = %s,
                        District_khmer = %s,
                        Province_khmer = %s,
                        Village = %s,
                        Commune = %s,
                        District = %s,
                        Province = %s,
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
                        Paved_Asphalt_Road = %s,
                        Concrete_Road = %s,
                        Laterite_Road = %s,
                        White_Soiled_Road = %s,
                        Road_Leading_to_Kiosk = %s,
                        Monthly_Income_Average_per_Person = %s,
                        Labour_Market = %s,
                        Monthly_Income_Average_per_Worker = %s, 
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
                        Type_of_Water_Tank = %s
                        WHERE Id_Site = %s""",ListData)
    return("ok")

def getSites():
    sitesQuery = con.execute("SELECT Id_Site FROM Sites ORDER BY Id_Site")
    sitesIterator = sitesQuery.fetchall()
    sites = []
    for site in sitesIterator:
        sites.append(site.Id_Site)
    return sites

def getprevisionsales(doc):
    df = pd.read_excel(doc)
    Year = int(datetime.datetime.today().year)
    print(Year)
    allTest = con.execute("SELECT Code_Previsions,Id_Site,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales WHERE Year(Month) = %s",Year).fetchall()
    for index,row in df.iterrows():
        Test_site = list(filter(lambda row: row[1] == row[0], allTest))
        if row[0] != 'Code':
            print(row[0])
            for i in range(1,13):
                Test_date = list(filter(lambda row: row[2] == str(date(Year,i,1)), Test_site))
                if row[i] and not pd.isna(row[i]):
                    if Test_date:
                        con.execute("UPDATE PrevisionsSales SET PrevisionsSalesTot = %s WHERE Id_Site = %s AND Month = %s",(row[i],row[0],datetime.date(Year,i,1)))
                    else:
                        query = ("INSERT INTO PrevisionsSales(Id_Site,Month,PrevisionsSalesTot) VALUES(%s,%s,%s)")
                        con.execute(query,(row[0],date(Year,i,1),row[i]))
                else:
                    if Test_date:
                        con.execute("UPDATE PrevisionsSales SET PrevisionsSalesTot = %s WHERE Id_Site = %s AND Month = %s",(0,row[0],datetime.date(Year,i,1)))
                    else:
                        query = ("INSERT INTO PrevisionsSales(Id_Site,Month,PrevisionsSalesTot) VALUES(%s,%s,%s)")
                        con.execute(query,(row[0],date(Year,i,1),0))

    return("ok")

def getprevisionschool(doc):
    df = pd.read_excel(doc)
    for index,row in df.iterrows():
        print(row[0])
        if row[1] and not pd.isna(row[1]):
            con.execute("UPDATE Sites SET SchoolSalesBudget = %s WHERE Id_Site = %s",(row[1],row[0]))
        else:
            con.execute("UPDATE Sites SET SchoolSalesBudget = %s WHERE Id_Site = %s",(0,row[0]))
        if row[2] and not pd.isna(row[2]):
            con.execute("UPDATE Sites SET NumberSchoolsWinS = %s WHERE Id_Site = %s",(row[2],row[0]))
        else:
            con.execute("UPDATE Sites SET NumberSchoolsWinS = %s WHERE Id_Site = %s",(0,row[0]))
        if row[3] and not pd.isna(row[3]):
            con.execute("UPDATE Sites SET NumberStudentsWinS = %s WHERE Id_Site = %s",(row[3],row[0]))
        else:
            con.execute("UPDATE Sites SET NumberStudentsWinS = %s WHERE Id_Site = %s",(0,row[0]))
    return("ok")

def getlonglatwavefromGoogleMap(doc): #wait the excel exctracted from the map of the Cambodia site
    df = pd.read_excel(doc)
    sep = ' '
    for index,row in df.iterrows():
        Site = str(row['Site_Code']).split(sep, 1)[0]
        con.execute("UPDATE Sites SET Longitude = %s, Latitude = %s, Wave = %s WHERE Id_Site = %s",(row[0],row[1],str(row[6]),Site))

if __name__ == '__main__':
    UpdatePlatform()
