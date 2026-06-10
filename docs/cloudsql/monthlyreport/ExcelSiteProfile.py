import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta, datetime
from calendar import monthrange
import db
import tempfile
from dateutil.relativedelta import *
from monthlyreport.Functionutils import listSite,listDate, listSiteStillActive

def SiteProfileDatabase(workbook):
    con = db.pool.connect()
    worksheet = workbook.add_worksheet("Site Profile Database")
    grey_format = workbook.add_format({'bg_color' : "#C0C0C0"})
    Site_format = workbook.add_format({'bg_color': "#DCE6F1",'bold':True})
    Adress1_format = workbook.add_format({'bg_color': "#C4D79B",'bold':True})
    Adress2_format = workbook.add_format({'bg_color': "#76933C",'bold':True})
    Construction_format = workbook.add_format({'bg_color': "#B7DEE8",'bold':True})
    Population1_format = workbook.add_format({'bg_color': "#FABF8F",'bold':True})
    Population2_format = workbook.add_format({'bg_color': "#E26B0A",'bold':True})
    Population3_format = workbook.add_format({'bg_color': "#974706",'bold':True})
    Construction_format = workbook.add_format({'bg_color': "#B7DEE8",'bold':True})
    Merge_column_title = workbook.add_format({'bg_color': "#F2F2F2",'bold':True,'valign':'top','align':'center'})
    Merge_column_text = workbook.add_format({'bg_color': "#F2F2F2",'font_color':"#F2F2F2"})
    White_format = workbook.add_format({'font_color':"#FFFFFF"})

    data = {}
    query = con.execute("SELECT * FROM Sites")
    data = [dict(row) for row in query.fetchall()]
    print(data)
    query = con.execute("SELECT * FROM NewEntrepreneur WHERE Resignation = %s",(False))
    dataEntrepreneur = [dict(row) for row in query.fetchall()]
    Boucle = 0
    BoucleEntrepreneur = 0
    for i in range(len(data)):
        Column = 0
        worksheet.write(2,Column,"Code_Site",Site_format)
        worksheet.write(i+3,Column,data[i]['Id_Site'])
        Column +=1

        worksheet.write(2,Column,"Site Name",Site_format)
        worksheet.write(i+3,Column,"")
        Column +=1

        worksheet.write(2,Column,"Site Name Khmer",Site_format)
        worksheet.write(i+3,Column,"")
        Column +=1

        worksheet.write(2,Column,"Platform",Site_format)
        worksheet.write(i+3,Column,data[i]['Platform'])
        Column +=1

        worksheet.write(2,Column,"Advisor",Site_format)
        worksheet.write(i+3,Column,data[i]['Advisor'])
        Column +=1

        worksheet.write(2,Column,"Tier",Site_format)
        worksheet.write(i+3,Column,data[i]['Last_Tier'])
        Column +=1
####################################START ADRESS################################
############ START CODE############ 

        if Boucle ==0:
            worksheet.write(2,Column,"Code Village",Adress1_format)
            ColumnStartCode = Column 
            ColumnStartAdress = Column
            worksheet.set_column(Column,Column,len("Code Village"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Code_Village'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Code Commune",Adress1_format)
            worksheet.set_column(Column,Column,len("Code Commune"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Code_Commune'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Code District",Adress1_format)
            worksheet.set_column(Column,Column,len("Code District"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Code_District'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Code Province",Adress1_format)
            worksheet.set_column(Column,Column,len("Code Province"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Code_Province_INT'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Code"))
            worksheet.merge_range(1,ColumnStartCode,1,Column,"Code",Merge_column_title)
            worksheet.write(2,Column,"Code",White_format)
        worksheet.write(i+3,Column,"Code",Merge_column_text)
        Column+=1

############START KHMER ADRESS############

        if Boucle == 0:
            worksheet.write(2,Column,"Village Khmer",Adress1_format)
            ColumnStartKhmer = Column
            worksheet.set_column(Column,Column,len("Village Khmer"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Village_khmer'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Commune Khmer",Adress1_format)
            worksheet.set_column(Column,Column,len("Commune Khmer"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Commune_khmer'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"District Khmer",Adress1_format)
            worksheet.set_column(Column,Column,len("District Khmer"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['District_khmer'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Province Khmer",Adress1_format)
            worksheet.set_column(Column,Column,len("Province Khmer"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Province_khmer'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Khmer"))
            worksheet.merge_range(1,ColumnStartKhmer,1,Column,"Khmer",Merge_column_title)
            worksheet.write(2,Column,"Khmer",White_format)
        worksheet.write(i+3,Column,"Khmer ",Merge_column_text)
        Column+=1

############START ENGLISH ADRESS############

        if Boucle == 0:
            worksheet.write(2,Column,"Village",Adress1_format)
            ColumnStartEnglish = Column
            worksheet.set_column(Column,Column,len("Village"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Village'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Commune",Adress1_format)
            worksheet.set_column(Column,Column,len("Commune"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Commune'])
        Column +=1
       
        if Boucle ==0:
            worksheet.write(2,Column,"District",Adress1_format)
            worksheet.set_column(Column,Column,len("District"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['District'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Province",Adress1_format)
            worksheet.set_column(Column,Column,len("Province"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Province'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("English"))
            worksheet.merge_range(1,ColumnStartEnglish,1,Column,"English",Merge_column_title)
            worksheet.write(2,Column,"English",White_format)
        worksheet.write(i+3,Column,"English",Merge_column_text)
        Column+=1

############START GPS############
        if Boucle == 0:
            worksheet.write(2,Column,"Latitude",Adress2_format)
            ColumnStartGPS = Column
            worksheet.set_column(Column,Column,len("Latitude"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Latitude'])
        Column +=1

        if Boucle ==0:
            worksheet.write(2,Column,"Longitude",Adress2_format)
            worksheet.set_column(Column,Column,len("Longitude"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Longitude'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("GPS "))
            worksheet.merge_range(1,ColumnStartGPS,1,Column,"GPS",Merge_column_title)
            worksheet.write(2,Column,"GPS",White_format)
            worksheet.merge_range(0,ColumnStartAdress,0,Column,"Adress",Merge_column_title)
        worksheet.write(i+3,Column,"GPS",Merge_column_text)
        Column+=1

####################################PROJECT & FINANCEMENT################

        if Boucle == 0:
            worksheet.write(2,Column,"Project Agreement",Construction_format)
            ColumnStartPandF = Column
            worksheet.set_column(Column,Column,len("Project Agreement"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['ProjectAgreement'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Batch",Construction_format)
            worksheet.set_column(Column,Column,len("Batch"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Wave'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Sale Starting Date",Construction_format)
            worksheet.set_column(Column,Column,len("Sale Starting Date"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Sale_Starting_Date'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Funder 1",Construction_format)
            worksheet.set_column(Column,Column,len("Funder 1"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Funder_1'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Funder 2",Construction_format)
            worksheet.set_column(Column,Column,len("Funder 2"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Funder_2'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Funder 3",Construction_format)
            worksheet.set_column(Column,Column,len("Funder 3"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Funder_3'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Construction Cost",Construction_format)
            worksheet.set_column(Column,Column,len("Construction Cost"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Building_cost'])
        Column +=1

        if Boucle ==0 :
            worksheet.merge_range(0,ColumnStartPandF,1,Column,"Project",Merge_column_title)
            worksheet.write(2,Column,"Project",White_format)
            worksheet.set_column(Column,Column,len("Project "))
        worksheet.write(i+3,Column,"P&F",Merge_column_text)
        Column +=1

####################################START DEMOGRAPHY##########################
############START DEMOGRAPHY TOTAL############
        if Boucle ==0 :
            worksheet.write(2,Column,"#Villages",Population1_format)
            ColumnStartDemoTotal = Column
            ColumnStartDemo = Column
            worksheet.set_column(Column,Column,len("#Villages"),None,{'level':1,'hidden':True})
            ColumnTotalVillage = Column 
        worksheet.write(i+3,Column,data[i]['Number_Village'])
        Column +=1

        if Boucle ==0 :
            worksheet.write(2,Column,"#Families",Population1_format)
            worksheet.set_column(Column,Column,len("#Families"),None,{'level':1,'hidden':True})
            ColumnTotalFamilies = Column 
        worksheet.write(i+3,Column,data[i]['Number_Family'])
        Column +=1

        if Boucle ==0 :
            worksheet.write(2,Column,"#Households",Population1_format)
            worksheet.set_column(Column,Column,len("#Households"),None,{'level':1,'hidden':True})
            ColumnTotalHouseholds = Column 
        worksheet.write(i+3,Column,data[i]['Number_Households'])
        Column +=1

        if Boucle ==0 :
            worksheet.write(2,Column,"#Population",Population1_format)
            worksheet.set_column(Column,Column,len("#Population"),None,{'level':1,'hidden':True})
            ColumnTotalPopulation = Column 
        worksheet.write(i+3,Column,data[i]['Number_Population'])
        Column +=1

        if Boucle ==0 :
            worksheet.write(2,Column,"#Women",Population1_format)
            worksheet.set_column(Column,Column,len("#Women"),None,{'level':1,'hidden':True})
            ColumnTotalWomen = Column 
        worksheet.write(i+3,Column,data[i]['Number_Women'])
        Column +=1

        if Boucle ==0 :
            worksheet.write(2,Column,"#Migration",Population1_format)
            worksheet.set_column(Column,Column,len("#Migration"),None,{'level':1,'hidden':True})
            ColumnTotalMigration = Column 
        worksheet.write(i+3,Column,data[i]['Number_Migration'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Total"))
            worksheet.merge_range(1,ColumnStartDemoTotal,1,Column,"Total",Merge_column_title)
            worksheet.write(2,Column,"Total",White_format)
        worksheet.write(i+3,Column,"Total",Merge_column_text)
        Column+=1

############START DEMO < 5KM############

        if Boucle == 0:
            worksheet.write(2,Column,"#Villages <5km",Population2_format)
            ColumnStartDemoinf5km = Column
            worksheet.set_column(Column,Column,len("#Villages <5km"),None,{'level':1,'hidden':True})
            ColumnTotalVillage_inf5km = Column 
        worksheet.write(i+3,Column,data[i]['Number_Village_5km'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Families <5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Families <5km"),None,{'level':1,'hidden':True})
            ColumnTotalFamilies_inf5km = Column 
        worksheet.write(i+3,Column,data[i]['Number_Family_5km'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Households <5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Households <5km"),None,{'level':1,'hidden':True})
            ColumnTotalHouseholds_inf5km = Column 
        worksheet.write(i+3,Column,data[i]['Number_Households_5km'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Population <5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Population <5km"),None,{'level':1,'hidden':True})
            ColumnTotalPopulation_inf5km = Column 
        worksheet.write(i+3,Column,data[i]['Number_Population_5km'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Women <5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Women <5km"),None,{'level':1,'hidden':True})
            ColumnTotalWomen_inf5km = Column 
        worksheet.write(i+3,Column,data[i]['Number_Women_5km'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Migration <5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Migration <5km"),None,{'level':1,'hidden':True})
            ColumnTotalMigration_inf5km = Column 
        worksheet.write(i+3,Column,data[i]['Number_Migration_5km'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("<5km"))
            worksheet.merge_range(1,ColumnStartDemoinf5km,1,Column,"<5km",Merge_column_title)
            worksheet.write(2,Column,"<5km",White_format)
        worksheet.write(i+3,Column,"<5km",Merge_column_text)
        Column+=1

############START DEMO > 5KM############

        if Boucle == 0:
            worksheet.write(2,Column,"#Villages >5km",Population2_format)
            ColumnStartDemosup5km = Column
            worksheet.set_column(Column,Column,len("#Villages >5km"),None,{'level':1,'hidden':True})
            ColumnTotalVillage_sup5km = Column 
        worksheet.write_formula(i+3,Column,"=%s-%s"%(xl_rowcol_to_cell(i+3,ColumnTotalVillage),xl_rowcol_to_cell(i+3,ColumnTotalVillage_inf5km)))
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Families >5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Families >5km"),None,{'level':1,'hidden':True})
            ColumnTotalFamilies_sup5km = Column 
        worksheet.write_formula(i+3,Column,"=%s-%s"%(xl_rowcol_to_cell(i+3,ColumnTotalFamilies),xl_rowcol_to_cell(i+3,ColumnTotalFamilies_inf5km)))
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Households >5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Households >5km"),None,{'level':1,'hidden':True})
            ColumnTotalHouseholds_sup5km = Column 
        worksheet.write_formula(i+3,Column,"=%s-%s"%(xl_rowcol_to_cell(i+3,ColumnTotalHouseholds),xl_rowcol_to_cell(i+3,ColumnTotalHouseholds_inf5km)))
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Population >5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Population >5km"),None,{'level':1,'hidden':True})
            ColumnTotalPopulation_sup5km = Column 
        worksheet.write_formula(i+3,Column,"=%s-%s"%(xl_rowcol_to_cell(i+3,ColumnTotalPopulation),xl_rowcol_to_cell(i+3,ColumnTotalPopulation_inf5km)))
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Women >5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Women >5km"),None,{'level':1,'hidden':True})
            ColumnTotalWomen_sup5km = Column 
        worksheet.write_formula(i+3,Column,"=%s-%s"%(xl_rowcol_to_cell(i+3,ColumnTotalWomen),xl_rowcol_to_cell(i+3,ColumnTotalWomen_inf5km)))
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Migration >5km",Population2_format)
            worksheet.set_column(Column,Column,len("#Migration >5km"),None,{'level':1,'hidden':True})
            ColumnTotalMigration_sup5km = Column 
        worksheet.write_formula(i+3,Column,"=%s-%s"%(xl_rowcol_to_cell(i+3,ColumnTotalMigration),xl_rowcol_to_cell(i+3,ColumnTotalMigration_inf5km)))
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len(">5km"))
            worksheet.merge_range(1,ColumnStartDemosup5km,1,Column,">5km",Merge_column_title)
            worksheet.write(2,Column,">5km",White_format)
            worksheet.merge_range(0,ColumnStartDemo,0,Column,"Demography",Merge_column_title)
        worksheet.write(i+3,Column,">5km",Merge_column_text)
        Column+=1

####################################START INFRASTRUCTURE###############################
############START LAND############
        if Boucle == 0:
            worksheet.write(2,Column,"#Pagodas",Population3_format)
            ColumnStartInfrastructure = Column 
            ColumnStartLand = Column 
            worksheet.set_column(Column,Column,len("#Pagodas"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Number_Pagoda'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"#Primary School",Population3_format)
            worksheet.set_column(Column,Column,len("#Primary School"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Number_Primary_School'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Land of Kiosk")
            worksheet.set_column(Column,Column,len("Land of Kiosk"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Land_of_kiosk'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Land "))
            worksheet.merge_range(1,ColumnStartLand,1,Column,"Land",Merge_column_title)
            worksheet.write(2,Column,"Land",White_format)
        worksheet.write(i+3,Column,"Land",Merge_column_text)
        Column+=1

############START ROAD############

        if Boucle == 0:
            worksheet.write(2,Column,"% of Paved Asphalt Road")
            ColumnStartRoad = Column
            worksheet.set_column(Column,Column,len("% of Paved Asphalt Road"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Paved_Asphalt_Road'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"% Concrete Road")
            worksheet.set_column(Column,Column,len("% of Concrete Road"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Concrete_Road'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"% Laterite Road")
            worksheet.set_column(Column,Column,len("% of Laterite Road"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Laterite_Road'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"% White-Soiled Road")
            worksheet.set_column(Column,Column,len("% of White-Soiled Road"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['White_Soiled_Road'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Road Leading to Kiosk")
            worksheet.set_column(Column,Column,len("Road Leading to Kiosk"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Road_Leading_to_Kiosk'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Road "))
            worksheet.merge_range(1,ColumnStartRoad,1,Column,"Road",Merge_column_title)
            worksheet.write(2,Column,"Road",White_format)
            worksheet.merge_range(0,ColumnStartInfrastructure,0,Column,"Infrastructure",Merge_column_title)
        worksheet.write(i+3,Column,"Road",Merge_column_text)
        Column+=1

####################################START ECONOMIC PART################################

        if Boucle == 0:
            worksheet.write(2,Column,"Monthly Avg Inc/Pers")
            ColumnStartEconomic = Column 
            worksheet.set_column(Column,Column,len("Monthly Avg Inc/Pers"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Monthly_Income_Average_per_Person'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Labour Market")
            worksheet.set_column(Column,Column,len("Labour Market"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Labour_Market'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Monthly Avg Inc/Worker")
            worksheet.set_column(Column,Column,len("Monthly Avg Inc/Worker"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Monthly_Income_Average_per_Worker'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Economic"))
            worksheet.merge_range(0,ColumnStartEconomic,1,Column,"Economic",Merge_column_title)
            worksheet.write(2,Column,"Economic",White_format)
        worksheet.write(i+3,Column,"Economic",Merge_column_text)
        Column+=1

####################################START TECHNICAL PART###############################"""
############START FIRST WATER SOURCE############
        if Boucle == 0:
            worksheet.write(2,Column,"Main Water Source")
            ColumnStartTechnical = Column 
            ColumnStart1stWaterSource = Column
            worksheet.set_column(Column,Column,len("Main Water Source"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Water_Source'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Well or Pond Ownership")
            worksheet.set_column(Column,Column,len("Well or Pond Ownership"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Well_Pond_Ownership'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Depth of Well or Pond")
            worksheet.set_column(Column,Column,len("Depth of Well or Pond"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Depth_Well_Pond'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Water Source distance from Kiosk")
            worksheet.set_column(Column,Column,len("Water Source distance from Kiosk"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Water_Source_Distance_From_Kiosk'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Main Water Source"))
            worksheet.merge_range(1,ColumnStart1stWaterSource,1,Column,"Main Water Source",Merge_column_title)
            worksheet.write(2,Column,"1st Water Source",White_format)
        worksheet.write(i+3,Column,"1st Water Source",Merge_column_text)
        Column+=1

############START SECOND WATER SOURCE############

        if Boucle == 0:
            worksheet.write(2,Column,"Second Water Source")
            ColumnStart2ndWaterSource = Column 
            worksheet.set_column(Column,Column,len("Second Water Source"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Second_Water_Source'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Well or Pond Ownership (second source)")
            worksheet.set_column(Column,Column,len("Well or Pond Ownership (second source)"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Well_Pond_Ownership_Second_Source'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Depth of Well or Pond (second source)")
            worksheet.set_column(Column,Column,len("Depth of Well or Pond (second source)"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Depth_Well_Pond_Second_Source'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Water Source distance from Kiosk (second source)")
            worksheet.set_column(Column,Column,len("Water Source distance from Kiosk (second source)"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Water_Source_Distance_From_Kiosk_Second_Source'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Second Water Source"))
            worksheet.merge_range(1,ColumnStart2ndWaterSource,1,Column,"Second Water Source",Merge_column_title)
            worksheet.write(2,Column,"2nd Water Source",White_format)
        worksheet.write(i+3,Column,"2nd Water Source",Merge_column_text)
        Column+=1

############START POWER SOURCE############
        if Boucle == 0:
            worksheet.write(2,Column,"Main power source")
            ColumnStartPowerSource = Column 
            worksheet.set_column(Column,Column,len("Main power source"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Main_Power_Source'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Second power source")
            worksheet.set_column(Column,Column,len("Second power source"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Second_Power_Source'])
        Column +=1

        if Boucle == 0:
            worksheet.write(2,Column,"Type of water tank")
            worksheet.set_column(Column,Column,len("Type of water tank"),None,{'level':1,'hidden':True})
        worksheet.write(i+3,Column,data[i]['Type_of_Water_Tank'])
        Column +=1

        if Boucle ==0:
            worksheet.set_column(Column,Column,len("Power source"))
            worksheet.merge_range(1,ColumnStartPowerSource,1,Column,"Power source",Merge_column_title)
            worksheet.write(2,Column,"Power Source",White_format)
            worksheet.merge_range(0,ColumnStartTechnical,0,Column,"Techincal",Merge_column_title)
        worksheet.write(i+3,Column,"Power source",Merge_column_text)
        Column+=1

####################################START ENTREPRENEUR####################################
        

        Entrepreneur = list(filter(lambda row: row['Id_Site'] == data[i]['Id_Site'], dataEntrepreneur))
        if Entrepreneur:

############START GENERAL############
            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Entrepreneur Name Khmer")
                ColumnStartEntrepreneur = Column 
                ColumnStartGeneral = Column 
                worksheet.set_column(Column,Column,len("Entrepreneur Name Khmer"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Entrepreneur_Khmer_name'])
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Entrepreneur Name English")
                worksheet.set_column(Column,Column,len("Entrepreneur Name English"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Entrepreneur_English_name'])
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Generation")
                worksheet.set_column(Column,Column,len("Generation"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Sex")
                worksheet.set_column(Column,Column,len("Sex"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Sex'])
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Date of Birth")
                worksheet.set_column(Column,Column,len("Date of Birth"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Date_of_birth'])
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Entrepreneur Contact")
                worksheet.set_column(Column,Column,len("Entrepreneur Contact"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Phone_number'])
            Column +=1

            if BoucleEntrepreneur ==0:
                worksheet.set_column(Column,Column,len("General"))
                worksheet.merge_range(1,ColumnStartGeneral,1,Column,"General",Merge_column_title)
                worksheet.write(2,Column,"General",White_format)
            worksheet.write(i+3,Column,"General",Merge_column_text)
            Column+=1

############START EDUCATION/JOB############

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Education Background")
                ColumnStartEducation = Column 
                worksheet.set_column(Column,Column,len("Education Background"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Education'])
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Part-time Job")
                worksheet.set_column(Column,Column,len("Part-time job"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Previous Job")
                worksheet.set_column(Column,Column,len("Previous job"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Previous_job'])
            Column +=1

            if BoucleEntrepreneur ==0:
                worksheet.set_column(Column,Column,len("Education"))
                worksheet.merge_range(1,ColumnStartEducation,1,Column,"Education",Merge_column_title)
                worksheet.write(2,Column,"Education",White_format)
            worksheet.write(i+3,Column,"Education",Merge_column_text)
            Column+=1

############ADRESS############
            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Current Village")
                ColumnStartAdress = Column 
                worksheet.set_column(Column,Column,len("Current Village"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"") # We have only commune in form
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Village Code of Birth")
                worksheet.set_column(Column,Column,len("Village Code of Birth"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Village of Birth")
                worksheet.set_column(Column,Column,len("Village of Birth"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Commune of Birth")
                worksheet.set_column(Column,Column,len("Commune of Birth"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"District of Birth")
                worksheet.set_column(Column,Column,len("District of Birth"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Province of Birth")
                worksheet.set_column(Column,Column,len("Province of Birth"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0:
                worksheet.set_column(Column,Column,len("Adress"))
                worksheet.merge_range(1,ColumnStartAdress,1,Column,"Adress",Merge_column_title)
                worksheet.write(2,Column,"Adress",White_format)
            worksheet.write(i+3,Column,"Adress",Merge_column_text)
            Column+=1

############START OTHER INFO############

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"ID Number")
                ColumnStartOther = Column
                worksheet.set_column(Column,Column,len("ID Number"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Starting Date")
                worksheet.set_column(Column,Column,len("Starting Date"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,Entrepreneur[0]['Date_start_working'])
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Reading")
                worksheet.set_column(Column,Column,len("Reading"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Writing")
                worksheet.set_column(Column,Column,len("Writing"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Calculating")
                worksheet.set_column(Column,Column,len("Calculating"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Why work as entrepreneur")
                worksheet.set_column(Column,Column,len("Why work as entrepreneur"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0: 
                worksheet.write(2,Column,"Remark")
                worksheet.set_column(Column,Column,len("Remark"),None,{'level':1,'hidden':True})
            worksheet.write(i+3,Column,"")
            Column +=1

            if BoucleEntrepreneur ==0:
                worksheet.set_column(Column,Column,len("Other"))
                worksheet.merge_range(1,ColumnStartOther,1,Column,"Other",Merge_column_title)
                worksheet.write(2,Column,"Other",White_format)
                worksheet.merge_range(0,ColumnStartEntrepreneur,0,Column,"Entrepreneur",Merge_column_title)
            worksheet.write(i+3,Column,"Other",Merge_column_text)
            Column+=1

            BoucleEntrepreneur =1


        Boucle =1


    worksheet.conditional_format(3,0,len(data)+2,Column-1,{"type" : "formula", "criteria" : "A4=\"\"", "format" : grey_format})
def LaunchExcelCreationSiteProfile():
    filepath = tempfile.gettempdir()+'/Sites Profile Database.xlsx'
    workbook = xlsxwriter.Workbook(filepath)

    SiteProfileDatabase(workbook)

    workbook.close()
    

if __name__ == '__main__':
    LaunchExcelCreationCollectionRate(2021)
