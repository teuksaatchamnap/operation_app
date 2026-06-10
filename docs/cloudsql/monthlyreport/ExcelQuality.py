from re import L
import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta, datetime
from calendar import monthrange
import calendar
import db
import tempfile
from dateutil.relativedelta import *
from monthlyreport.Functionutils import NewCalculTier
from monthlyreport.Functionutils import isFloat
from monthlyreport.Graph import DataForGraphQuality,GraphEcoliColiform,GraphAluTurb,GraphTestResults

con = db.pool.connect()
#############CHANGE TO ADD "type" IN THE SQL REQUEST########
def RawQuality(Current_date,Date_janv,workbook,FirstTest):
	if FirstTest == "First":
		Name_worksheet = "First Test"
	elif FirstTest == "Second":
		Name_worksheet = "Second Test"
	elif FirstTest == "All":
		Name_worksheet = "Raw data"
	worksheet = workbook.add_worksheet(Name_worksheet)
	Site_format = workbook.add_format({'bg_color':"#DAEEF3",'bold': True,'valign':'vcenter','center_across':True})
	Data_Ecoli_coliform = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
	Data_physicochimie = workbook.add_format({'bg_color':"#00B050",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
	Date_format = workbook.add_format({'num_format':'yyyy-mm-dd'})
	Number_format = workbook.add_format({'num_format':'# ##0'})
	Decimal_format = workbook.add_format({'num_format':'# ##0.0'})
	Title_format = workbook.add_format({'bold':True,"font_size":18,"center_across":True,'bg_color':'#FFFF00'})

##############EXTRACT DATA###############
	if FirstTest == "First" :
		AllDataQuality = con.execute("""SELECT site, sample_date,analysis_date, total_coliform, total_coliform_bottle, escherichia, escherichia_bottle, ph,
												turbidity, conductivity, tds, nitrate, nitrite, arsenic, fluoride, iron, manganese, hardness,
												calcium, alkalinity, aluminium, type FROM samples WHERE sample_date >= %s AND sample_date <= %s AND type = 'Monthly Test'
												ORDER BY sample_date DESC,site""",Date_janv, Current_date + relativedelta(months=+1)).fetchall()
	elif FirstTest == "Second":
		AllDataQuality = con.execute("""SELECT site, sample_date,analysis_date, total_coliform, total_coliform_bottle, escherichia, escherichia_bottle, ph,
												turbidity, conductivity, tds, nitrate, nitrite, arsenic, fluoride, iron, manganese, hardness,
												calcium, alkalinity, aluminium, type FROM samples WHERE sample_date >= %s AND sample_date <= %s AND type = 'WQ Alert'
												ORDER BY sample_date DESC,site""",Date_janv, Current_date + relativedelta(months=+1)).fetchall()
	elif FirstTest == "All":
		AllDataQuality = con.execute("""SELECT site, sample_date,analysis_date, total_coliform, total_coliform_bottle, escherichia, escherichia_bottle, ph,
												turbidity, conductivity, tds, nitrate, nitrite, arsenic, fluoride, iron, manganese, hardness,
												calcium, alkalinity, aluminium, type FROM samples WHERE sample_date >= %s AND sample_date <= %s
												ORDER BY sample_date DESC,site""",Date_janv, Current_date + relativedelta(months=+1)).fetchall()
	AllSite = con.execute("""SELECT Id_Site, Platform FROM Sites""").fetchall()

#############WRITE TITLE##############


	ColumnTitle = 0
	worksheet.write(2,ColumnTitle,"Type",Site_format)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Technicians    "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Site",Site_format)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Technicians"))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Platform",Site_format)
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Sample Collection Date",Data_Ecoli_coliform)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Sample Test Date",Data_Ecoli_coliform)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Delay in testing (days",Data_Ecoli_coliform)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Total Coliforms - Treatment System (CFU/100mL)",Data_Ecoli_coliform)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Total Coliforms - Bottle (CFU/100mL)",Data_Ecoli_coliform)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"E. coli Treatment System (CFU/100mL)",Data_Ecoli_coliform)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnENDYTD = ColumnTitle
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"E. coli Bottle (CFU/100mL) ",Data_Ecoli_coliform)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"pH",Data_physicochimie)
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Turbidity (NTU)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Conductivity (μS/cm)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"TDS (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Nitrate (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Nitrite (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnENDMonthly = ColumnTitle
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Arsenic (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Fluoride (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Iron (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Manganese (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Total Hardness (mg/L as CaCO3)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Calcium (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnENDMonthly = ColumnTitle
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Alkalinity (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1
	worksheet.write(2,ColumnTitle,"Aluminium (mg/L)",Data_physicochimie)
	worksheet.set_column(ColumnTitle,ColumnTitle,len("#Intervention < 1 "))
	ColumnTitle+=1

	worksheet.autofilter(2,0,len(AllDataQuality),ColumnTitle-1)
	worksheet.freeze_panes(3,2)

##############WRITE DATA####################


	for i in range(len(AllDataQuality)):
		Column = 0
		Platform = list(filter(lambda row: row[0] == AllDataQuality[i][0], AllSite)) or [["",""]]
		worksheet.write(i+3,Column,AllDataQuality[i][21])
		Column+=1
		worksheet.write(i+3,Column,AllDataQuality[i][0])
		Column+=1
		worksheet.write(i+3,Column,Platform[0][1])
		Column+=1
		worksheet.write(i+3,Column,AllDataQuality[i][1],Date_format)
		ColumnSampleDate = Column
		Column+=1
		worksheet.write(i+3,Column,AllDataQuality[i][2],Date_format)
		ColumnAnalysisDate = Column
		Column+=1
		worksheet.write_formula(i+3,Column,"=%s-%s"%(xl_rowcol_to_cell(i+3,ColumnAnalysisDate),xl_rowcol_to_cell(i+3,ColumnSampleDate)))
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][3]),Number_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][4]),Number_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][5]),Number_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][6]),Number_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][7]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][8]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][9]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][10]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][11]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][12]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][13]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][14]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][15]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][16]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][17]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][18]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][19]),Decimal_format)
		Column+=1
		worksheet.write(i+3,Column,isFloat(AllDataQuality[i][20]),Decimal_format)
		Column+=1

def DashboardWaterQualityPlatform(Current_date,workbook):
	worksheet = workbook.add_worksheet("Platform WQ Results")
	worksheet.set_zoom(70)

	BigTitle_format = workbook.add_format({'bg_color':"#4472C4",'bold': True,'valign':'vcenter','center_across':True})
	Title_format = workbook.add_format({'bold': True,'valign':'vcenter','center_across':True})
	Sub_Title_format = workbook.add_format({'italic': True,'valign':'vcenter','center_across':True})

	Number_format = workbook.add_format({'num_format':'# ##0','valign':'vcenter','center_across':True})
	Percentage_format = workbook.add_format({'num_format':'0.0%','valign':'vcenter','center_across':True})

	yellow_percentage_dot_format = workbook.add_format({'bg_color':"#FFFF00",'num_format':'0.0%','valign':'vcenter','center_across':True})
	yellow_percentage_format = workbook.add_format({'bg_color':"#FFFF00",'num_format':'0%','valign':'vcenter','center_across':True})

	red_percentage_dot_format = workbook.add_format({'bg_color':"#C0504D",'num_format':'0.0%','valign':'vcenter','center_across':True})
	red_percentage_format = workbook.add_format({'bg_color':"#C0504D",'num_format':'0%','valign':'vcenter','center_across':True})

	green_percentage_dot_format = workbook.add_format({'bg_color':"#92D050",'num_format':'0.0%','valign':'vcenter','center_across':True})
	green_percentage_format = workbook.add_format({'bg_color':"#92D050",'num_format':'0%','valign':'vcenter','center_across':True})
	
	grey_format = workbook.add_format({'bg_color':"#F2F2F2",'font_color':'#F2F2F2','valign':'vcenter','center_across':True})

########### WRITE LINE TITLE############
	worksheet.merge_range(0,0,1,6,"Water Quality Results per Platform",BigTitle_format)
	LineTotal = 2
	worksheet.write(LineTotal,0,"Microbiological parameters",Title_format)
	LineTotal+=1

	ListPlatform = con.execute("""SELECT DISTINCT Code_Platform FROM Platform ORDER BY Code_Platform""").fetchall()

	#FIRST TEST
	worksheet.merge_range(LineTotal,0,LineTotal,len(ListPlatform)+1,"Monthly sampling by advisor",Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"#Sites tested",Title_format)
	LineTotal+=1
	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%WHO compliance E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%WHO compliance Coliforms & E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"#Level 1 Alert",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1
	worksheet.write(LineTotal,0,"#Level 2 Alert",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1
	worksheet.write(LineTotal,0,"#Level 3 Alert",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1
	

	worksheet.write(LineTotal,0,"Site tested under 24h",Title_format)
	LineTotal+=1


	#AFTER SECOND TEST
	worksheet.merge_range(LineTotal,0,LineTotal,len(ListPlatform)+1,"Sampling after technician interventions",Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"#Sites re-tested after technician interventions",Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"%WHO compliance E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on re-tested sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1
	

	worksheet.write(LineTotal,0,"%WHO compliance Coliforms & E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on re-tested sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	#ALL SITES	
	worksheet.merge_range(LineTotal,0,LineTotal,len(ListPlatform)+1,"Global view after technician interventions",Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"%WHO compliance E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on ALL sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"%WHO compliance Coliforms & E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on ALL sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	worksheet.set_column('A:A',len("%WHO compliance Coliforms & E. Coli - 0 CFU/100mL  "))
	worksheet.set_column('B:B',len("Treatment system "))


#########DATA SELECTION############
	

	InfoDashboardMonthly = con.execute("""SELECT COUNT(DISTINCT s1.site),
									COUNT(CASE 
												WHEN total_coliform > 0 OR total_coliform = 'TNTC' THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE 
												WHEN total_coliform_bottle > 0 OR total_coliform_bottle = 'TNTC' THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE 
												WHEN escherichia > 0 OR escherichia = 'TNTC' THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE 
												WHEN escherichia_bottle > 0 OR escherichia_bottle = 'TNTC' THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE
												WHEN DATEDIFF(analysis_date, sample_date)>1 THEN 1
												ELSE NULL
											END),
									Platform,
									COUNT(CASE 
												WHEN contamination_level_machine = 1 THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE 
												WHEN contamination_level_machine = 2 THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE 
												WHEN contamination_level_machine = 3 THEN 1 
												ELSE NULL 
											END)
									FROM samples s1
												INNER JOIN Sites ON site = Id_Site
												INNER JOIN (
													SELECT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'Monthly Test')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
									WHERE (type = 'Monthly Test') 
									GROUP BY Platform ORDER BY Platform"""
									 ,(Current_date,Current_date+relativedelta(months=+1))).fetchall()


	InfoDashboardMonthly_Total = con.execute("""
												SELECT 
										  			COUNT(DISTINCT s1.site),
													SUM(CASE WHEN s1.total_coliform > 0 OR s1.total_coliform = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.total_coliform_bottle > 0 OR s1.total_coliform_bottle = "TNTC"  THEN 1 ELSE 0 END),
										  			SUM(CASE WHEN s1.escherichia > 0 OR s1.escherichia = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.escherichia_bottle > 0 OR s1.escherichia_bottle = "TNTC" THEN 1 ELSE 0 END),
													Platform
												FROM samples s1
											   	INNER JOIN Sites ON site = Id_Site
												INNER JOIN (
													SELECT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'WQ Alert' OR type = 'Monthly Test')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
										  		WHERE (type = 'WQ Alert' OR type = 'Monthly Test')
												GROUP BY Platform ORDER BY Platform	
										  		""", (Current_date,Current_date+relativedelta(months=+1))).fetchall()

	InfoDashboardMonthly_SecondTest = con.execute("""
												SELECT 
													COUNT(DISTINCT s1.site),
													SUM(CASE WHEN s1.escherichia > 0 OR s1.escherichia = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.escherichia_bottle > 0 OR s1.escherichia_bottle = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.total_coliform > 0 OR s1.total_coliform = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.total_coliform_bottle > 0 OR s1.total_coliform_bottle = "TNTC"  THEN 1 ELSE 0 END),
											   		Platform
												FROM samples s1
											   	INNER JOIN Sites ON site = Id_Site
												INNER JOIN (
													SELECT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'WQ Alert')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
												WHERE (type = 'WQ Alert')
											   	GROUP BY Platform ORDER BY Platform
												""", (Current_date,Current_date+relativedelta(months=+1))).fetchall()
		
	for i in range(len(ListPlatform)):

		FirstTest = list(filter(lambda row: row[6] == ListPlatform[i][0], InfoDashboardMonthly)) or [[0,0,0,0,0,0]]
		SecondTest = list(filter(lambda row: row[5] == ListPlatform[i][0], InfoDashboardMonthly_SecondTest)) or [[0,0,0,0,0,0]]
		TotalTest = list(filter(lambda row: row[5] == ListPlatform[i][0], InfoDashboardMonthly_Total)) or [[0,0,0,0,0,0]]

##########WRITE DATA############

		Line = 2
		worksheet.write(Line,i+2,ListPlatform[i][0],Title_format)
		Line +=1
		Line+=1
		worksheet.write(Line,i+2,FirstTest[0][0],Number_format)
		Line +=1
		#FIRST TEST
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(FirstTest[0][0],FirstTest[0][3],FirstTest[0][0]),Percentage_format)
		Line +=1

		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(FirstTest[0][0],FirstTest[0][4] or 0,FirstTest[0][0]),Percentage_format)
		Line +=1

		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(FirstTest[0][0],FirstTest[0][1],FirstTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(FirstTest[0][0],FirstTest[0][2],FirstTest[0][0]),Percentage_format)
		Line +=1

		worksheet.write(Line,i+2,FirstTest[0][7],Number_format)
		Line +=1
		worksheet.write(Line,i+2,FirstTest[0][8],Number_format)
		Line +=1
		worksheet.write(Line,i+2,FirstTest[0][9],Number_format)
		Line +=1

		worksheet.write_formula(Line,i+2,"=1-%s/%s"%(FirstTest[0][5],FirstTest[0][0]),Percentage_format)
		Line +=1

		#SECOND TEST
		Line+=1
		worksheet.write(Line,i+2,SecondTest[0][0],Number_format)
		Line +=1

		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(SecondTest[0][0],SecondTest[0][1],SecondTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(SecondTest[0][0],SecondTest[0][2],SecondTest[0][0]),Percentage_format)
		Line +=1

		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(SecondTest[0][0],SecondTest[0][3],SecondTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(SecondTest[0][0],SecondTest[0][4],SecondTest[0][0]),Percentage_format)
		Line +=1

		#ALL Sites
		Line+=1
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(TotalTest[0][0],TotalTest[0][3],TotalTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(TotalTest[0][0],TotalTest[0][4],TotalTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(TotalTest[0][0],TotalTest[0][1],TotalTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+2,"=(%s-%s)/%s"%(TotalTest[0][0],TotalTest[0][2],TotalTest[0][0]),Percentage_format)
		Line +=1
		
		ListLineWithFormating = [6,7,8,9,13,14,18,19,20,21]
		ColStart = 2
		worksheet.conditional_format('C6:%s18'%(xl_col_to_name(len(ListPlatform)+1)),{"type" : "formula", "criteria" : 'OR(C6=0,C6="")', "format" : grey_format})
		
		for Line in ListLineWithFormating:
			worksheet.conditional_format('%s%s:%s%s'%(xl_col_to_name(ColStart),Line,xl_col_to_name(len(ListPlatform)+1),Line),{"type" : "formula", "criteria" : "AND(%s>=0.98,%s<0.995)"%(xl_col_to_name(ColStart)+str(Line),xl_col_to_name(ColStart)+str(Line)), "format" : yellow_percentage_dot_format})
			worksheet.conditional_format('%s%s:%s%s'%(xl_col_to_name(ColStart),Line,xl_col_to_name(len(ListPlatform)+1),Line),{"type" : "formula", "criteria" : "%s<0.98"%(xl_col_to_name(ColStart)+str(Line)), "format" : red_percentage_dot_format})
			worksheet.conditional_format('%s%s:%s%s'%(xl_col_to_name(ColStart),Line,xl_col_to_name(len(ListPlatform)+1),Line),{"type" : "formula", "criteria" : "%s>0.995"%(xl_col_to_name(ColStart)+str(Line)), "format" : green_percentage_dot_format})

		GraphTestResults(workbook,worksheet,"Platform WQ Results",Line +4 ,i*5,0,30+i*2,Current_date,'First',ListPlatform[i][0])
		GraphTestResults(workbook,worksheet,"Platform WQ Results",Line +17,i*5,7,30+i*2,Current_date,'Second',ListPlatform[i][0])
	
def DashboardWaterQuality(Current_date,workbook):
	worksheet = workbook.add_worksheet("Annual WQ Results")
	worksheet.set_zoom(70)

	BigTitle_format = workbook.add_format({'bg_color':"#4472C4",'border':2,'bold': True,'valign':'vcenter','center_across':True})
	Title_format = workbook.add_format({'bold': True,'valign':'vcenter','center_across':True})
	Sub_Title_format = workbook.add_format({'italic': True,'valign':'vcenter','center_across':True})


	Number_format = workbook.add_format({'num_format':'# ##0','valign':'vcenter','center_across':True})
	Percentage_format = workbook.add_format({'num_format':'0.0%','valign':'vcenter','center_across':True})

	yellow_percentage_dot_format = workbook.add_format({'bg_color':"#FFFF00",'num_format':'0.0%','valign':'vcenter','center_across':True})
	yellow_percentage_format = workbook.add_format({'bg_color':"#FFFF00",'num_format':'0%','valign':'vcenter','center_across':True})

	red_percentage_dot_format = workbook.add_format({'bg_color':"#C0504D",'num_format':'0.0%','valign':'vcenter','center_across':True})
	red_percentage_format = workbook.add_format({'bg_color':"#C0504D",'num_format':'0%','valign':'vcenter','center_across':True})

	green_percentage_dot_format = workbook.add_format({'bg_color':"#92D050",'num_format':'0.0%','valign':'vcenter','center_across':True})
	green_percentage_format = workbook.add_format({'bg_color':"#92D050",'num_format':'0%','valign':'vcenter','center_across':True})

	grey_format = workbook.add_format({'bg_color':"#F2F2F2",'font_color':'#F2F2F2','valign':'vcenter','center_across':True})

########### WRITE LINE TITLE############
	worksheet.merge_range(0,0,1,Current_date.month+1,"Water Quality Results Summary %s"%(Current_date.year),BigTitle_format)
	LineTotal = 2
	worksheet.write(LineTotal,0,"Microbiological parameters",Title_format)
	LineTotal+=1

	#FIRST TEST
	worksheet.merge_range(LineTotal,0,LineTotal,Current_date.month+1,"Monthly sampling by advisor",Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"#Sites tested",Title_format)
	LineTotal+=1
	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%WHO compliance E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"%WHO compliance E. Coli YTD - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"all",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%WHO compliance E. Coli & Coliform YTD - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"%WHO compliance E. Coli YTD - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"bottle",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1
	

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%WHO compliance Coliforms & E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"#Level 1 Alert",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1
	worksheet.write(LineTotal,0,"#Level 2 Alert",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1
	worksheet.write(LineTotal,0,"#Level 3 Alert",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	worksheet.set_row(LineTotal, None, None, {'level': 1, 'hidden': True})
	LineTotal+=1

	worksheet.write(LineTotal,0,"Site tested under 24h",Title_format)
	LineTotal+=1


	#AFTER SECOND TEST
	worksheet.merge_range(LineTotal,0,LineTotal,Current_date.month+1,"Sampling after technician interventions",Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"#Sites re-tested after technician interventions",Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"%WHO compliance E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on re-tested sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"%WHO compliance Coliforms & E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on re-tested sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1
	
	#ALL SITES
	worksheet.merge_range(LineTotal,0,LineTotal,Current_date.month+1,"Global view after technician interventions",Title_format)
	LineTotal+=1
	
	worksheet.write(LineTotal,0,"%WHO compliance E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on ALL sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	worksheet.write(LineTotal,0,"%WHO compliance Coliforms & E. Coli - 0 CFU/100mL",Title_format)
	worksheet.write(LineTotal,1,"Treatment system",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,0,"Calculated on ALL sites",Sub_Title_format)
	worksheet.write(LineTotal,1,"Bottle",Sub_Title_format)
	LineTotal+=1

	LineTotal+=1

	worksheet.write(LineTotal,0,"Physical and chemical parameters",Title_format)
	LineTotal+=1
	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on pH - 6.5<pH<8.5",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)	
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)	
	LineTotal+=1
	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on turbidity - 2 NTU",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)	
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)	
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on TDS - 250 mg/L",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on Nitrate - 50 mg/L",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on Nitrite - 50 mg/L",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on Iron - 0.05 mg/L",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on Manganese - 0.05 mg/L",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)
	LineTotal+=1

	worksheet.merge_range(LineTotal,0,LineTotal+1,0,"%Compliance on Aluminium - 0.2 mg/L",Title_format)
	worksheet.write(LineTotal,1,"#Sites tested",Sub_Title_format)
	LineTotal+=1
	worksheet.write(LineTotal,1,"%",Sub_Title_format)
	LineTotal+=1


	worksheet.set_column('A:A',len("%WHO compliance Coliforms & E. Coli - 0 CFU/100mL  "))
	worksheet.set_column('B:B',len("Treatment system "))

	for i in range(1,Current_date.month+1):

#########DATA SELECTION############
		InfoDashboardMonthly = con.execute("""SELECT COUNT(DISTINCT s1.site),
									COUNT(IF(total_coliform>0 OR total_coliform='TNTC',1,NULL)),
									COUNT(IF(total_coliform_bottle>0 OR total_coliform_bottle='TNTC',1,NULL)),
									COUNT(IF(escherichia>0 OR escherichia='TNTC',1,NULL)),
									COUNT(IF(escherichia_bottle>0 OR escherichia_bottle='TNTC',1,NULL)),
									COUNT(IF(DATEDIFF(analysis_date, sample_date)>1,1,Null)),
									COUNT(IF(turbidity>2,1,NULL)),
									COUNT(IF(turbidity IS NOT NULL, 1, NULL)),
									COUNT(IF(tds>250,1,NULL)),
									COUNT(IF(tds IS NOT NULL, 1, NULL)),
									COUNT(IF(nitrate>50,1,NULL)),
									COUNT(IF(nitrate IS NOT NULL, 1, NULL)),
									COUNT(IF(nitrite>50,1,NULL)),
									COUNT(IF(nitrite IS NOT NULL, 1, NULL)),
									COUNT(IF(iron > 0.05,1,NULL)),
									COUNT(IF(iron IS NOT NULL,1,NULL)),
									COUNT(IF(manganese>0.05,1,NULL)),
									COUNT(IF(manganese IS NOT NULL ,1,NULL)),
									COUNT(IF(aluminium>0.2,1,NULL)),
									COUNT(IF(aluminium IS NOT NULL,1,NULL)),
									SUM(CASE WHEN ph >= 6.5 AND ph <= 8.5 THEN 1 ELSE 0 END),
									COUNT(IF(ph IS NOT NULL,1,NULL)),
									COUNT(CASE 
												WHEN contamination_level_machine = 1 THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE 
												WHEN contamination_level_machine = 2 THEN 1 
												ELSE NULL 
											END),
									COUNT(CASE 
												WHEN contamination_level_machine = 3 THEN 1 
												ELSE NULL 
											END)
									FROM samples s1
												INNER JOIN (
													SELECT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'Monthly Test')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
									 WHERE (type = 'Monthly Test') """
									 ,(date(Current_date.year,i,1),date(Current_date.year,i,1)+relativedelta(months=+1))).fetchall()

		InfoDashboardMonthly_Total = con.execute("""
												SELECT 
													COUNT(DISTINCT s1.site),
													SUM(CASE WHEN s1.total_coliform > 0 OR s1.total_coliform = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.total_coliform_bottle > 0 OR s1.total_coliform_bottle = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.escherichia > 0 OR s1.escherichia = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.escherichia_bottle > 0 OR s1.escherichia_bottle = "TNTC" THEN 1 ELSE 0 END)
										   		FROM samples s1
												INNER JOIN (
													SELECT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'WQ Alert' OR type = 'Monthly Test')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
												WHERE (type = 'WQ Alert' OR type = 'Monthly Test')
										   		""", (date(Current_date.year, i, 1), date(Current_date.year, i, 1) + relativedelta(months=+1))).fetchall()

		InfoDashboardMonthly_SecondTest = con.execute("""
												SELECT 
													COUNT(DISTINCT s1.site),
													SUM(CASE WHEN s1.escherichia > 0 OR s1.escherichia = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.escherichia_bottle > 0 OR s1.escherichia_bottle = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.total_coliform > 0 OR s1.total_coliform = "TNTC" THEN 1 ELSE 0 END),
													SUM(CASE WHEN s1.total_coliform_bottle > 0 OR s1.total_coliform_bottle = "TNTC"  THEN 1 ELSE 0 END)
												FROM samples s1
												INNER JOIN (
													SELECT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'WQ Alert')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
												WHERE (type = 'WQ Alert')""", (date(Current_date.year, i, 1), date(Current_date.year, i, 1) + relativedelta(months=+1))).fetchall()
		
		InfoDashboardYTD = con.execute("""SELECT COUNT(IF(type="Monthly Test",1,Null)),
								COUNT(IF(total_coliform>0 OR total_coliform='TNTC',1,NULL)),
								COUNT(CASE WHEN escherichia>0 OR escherichia='TNTC' OR escherichia_bottle>0 OR escherichia_bottle='TNTC' THEN 1 ELSE NULL END),
								COUNT(IF(total_coliform_bottle>0 OR total_coliform_bottle='TNTC',1,NULL))
								FROM samples WHERE sample_date>=%s AND sample_date < %s
								AND type = 'Monthly Test'""",(date(Current_date.year,1,1),date(Current_date.year,i,1)+relativedelta(months=+1))).fetchall()

##########WRITE DATA############
		Line = 2
		worksheet.write(Line,i+1,i,Title_format)
		Line +=1
		Line+=1
		worksheet.write(Line,i+1,InfoDashboardMonthly[0][0],Number_format)
		Line +=1
		#FIRST TEST
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly[0][0],InfoDashboardMonthly[0][3],InfoDashboardMonthly[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly[0][0],InfoDashboardMonthly[0][4],InfoDashboardMonthly[0][0]),Percentage_format)
		Line +=1

		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardYTD[0][0],InfoDashboardYTD[0][2],InfoDashboardYTD[0][0]),Percentage_format)
		Line +=1

		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardYTD[0][0],InfoDashboardYTD[0][1],InfoDashboardYTD[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardYTD[0][0],InfoDashboardYTD[0][3],InfoDashboardYTD[0][0]),Percentage_format)
		Line +=1

		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly[0][0],InfoDashboardMonthly[0][1],InfoDashboardMonthly[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly[0][0],InfoDashboardMonthly[0][2],InfoDashboardMonthly[0][0]),Percentage_format)
		Line +=1

		worksheet.write(Line,i+1,InfoDashboardMonthly[0][22],Number_format)
		Line +=1
		worksheet.write(Line,i+1,InfoDashboardMonthly[0][23],Number_format)
		Line +=1
		worksheet.write(Line,i+1,InfoDashboardMonthly[0][24],Number_format)
		Line +=1

		worksheet.write_formula(Line,i+1,"=1-%s/%s"%(InfoDashboardMonthly[0][5],InfoDashboardMonthly[0][0]),Percentage_format)
		Line +=1

		#SECOND TEST
		Line+=1
		worksheet.write(Line,i+1,InfoDashboardMonthly_SecondTest[0][0],Number_format)
		Line +=1

		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_SecondTest[0][0],InfoDashboardMonthly_SecondTest[0][1],InfoDashboardMonthly_SecondTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_SecondTest[0][0],InfoDashboardMonthly_SecondTest[0][2],InfoDashboardMonthly_SecondTest[0][0]),Percentage_format)
		Line +=1

		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_SecondTest[0][0],InfoDashboardMonthly_SecondTest[0][3],InfoDashboardMonthly_SecondTest[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_SecondTest[0][0],InfoDashboardMonthly_SecondTest[0][4],InfoDashboardMonthly_SecondTest[0][0]),Percentage_format)
		Line +=1

		#All sites
		Line+=1
		
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_Total[0][0],InfoDashboardMonthly_Total[0][3],InfoDashboardMonthly_Total[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_Total[0][0],InfoDashboardMonthly_Total[0][4],InfoDashboardMonthly_Total[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_Total[0][0],InfoDashboardMonthly_Total[0][1],InfoDashboardMonthly_Total[0][0]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"=(%s-%s)/%s"%(InfoDashboardMonthly_Total[0][0],InfoDashboardMonthly_Total[0][2],InfoDashboardMonthly_Total[0][0]),Percentage_format)
		Line +=1

		######Physical and chemical
		Line+=1
		worksheet.write(Line,i+1,i,Title_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][21]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(%s/%s,"")'%(InfoDashboardMonthly[0][20],InfoDashboardMonthly[0][7]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][7]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(1-%s/%s,"")'%(InfoDashboardMonthly[0][6],InfoDashboardMonthly[0][7]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][9]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(1-%s/%s,"")'%(InfoDashboardMonthly[0][8],InfoDashboardMonthly[0][9]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][11]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(1-%s/%s,"")'%(InfoDashboardMonthly[0][10],InfoDashboardMonthly[0][11]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][13]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(1-%s/%s,"")'%(InfoDashboardMonthly[0][12],InfoDashboardMonthly[0][13]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][15]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(1-%s/%s,"")'%(InfoDashboardMonthly[0][14],InfoDashboardMonthly[0][15]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][17]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(1-%s/%s,"")'%(InfoDashboardMonthly[0][16],InfoDashboardMonthly[0][17]),Percentage_format)
		Line +=1
		worksheet.write_formula(Line,i+1,"%s"%(InfoDashboardMonthly[0][19]),Number_format)
		Line +=1
		worksheet.write_formula(Line,i+1,'=IFERROR(1-%s/%s,"")'%(InfoDashboardMonthly[0][18],InfoDashboardMonthly[0][19]),Percentage_format)
		Line +=1


	ListLineWithFormating = [6,7,9,10,11,12,19,20,21,22,24,25,26,27,31,33,35,37,39,41,43,45]
	ColStart = 2
	worksheet.conditional_format('C6:%s42'%(xl_col_to_name(Current_date.month+1)),{"type" : "formula", "criteria" : 'OR(C6=0,C6="")', "format" : grey_format})
	
	for Line in ListLineWithFormating:
		worksheet.conditional_format('%s%s:%s%s'%(xl_col_to_name(ColStart),Line,xl_col_to_name(Current_date.month+1),Line),{"type" : "formula", "criteria" : "AND(%s>=0.98,%s<0.995)"%(xl_col_to_name(ColStart)+str(Line),xl_col_to_name(ColStart)+str(Line)), "format" : yellow_percentage_dot_format})
		worksheet.conditional_format('%s%s:%s%s'%(xl_col_to_name(ColStart),Line,xl_col_to_name(Current_date.month+1),Line),{"type" : "formula", "criteria" : "%s<0.98"%(xl_col_to_name(ColStart)+str(Line)), "format" : red_percentage_dot_format})
		worksheet.conditional_format('%s%s:%s%s'%(xl_col_to_name(ColStart),Line,xl_col_to_name(Current_date.month+1),Line),{"type" : "formula", "criteria" : "%s>0.995"%(xl_col_to_name(ColStart)+str(Line)), "format" : green_percentage_dot_format})
	
	#######GRAPH########
	GraphTestResults(workbook,worksheet,"Annual WQ Results",Line+5,0,0,30,Current_date,'First')
	GraphTestResults(workbook,worksheet,"Annual WQ Results",Line+5,4,0,33,Current_date,'Second')

def AlertPerSiteChemical(Current_date,workbook):

	worksheet = workbook.add_worksheet("Failures Physical Chemical")
	Title_format = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})

########DATA SELECTION##########

	ListSite = con.execute("""SELECT Id_Site,Platform FROM Sites WHERE Platform <> 'Dead'""").fetchall()
	allInfoDashboardYTD = con.execute("""SELECT Platform, site,
								   					COUNT(IF(ph>8.5 OR ph<6.5,1,NULL)),
								   					COUNT(IF(turbidity>1,1,NULL)),
										   			COUNT(IF(tds>250,1,NULL)),
										   			COUNT(IF(nitrate>50,1,NULL)),
										   			COUNT(IF(nitrite>3,1,NULL)),
										   			COUNT(IF(nitrate/50+nitrite/3>1,1,NULL)),
										   			COUNT(IF(arsenic>0.01,1,NULL)),
										   			COUNT(IF(fluoride>1.5,1,NULL)),
										   			COUNT(IF(iron>0.05,1,NULL)),
										   			COUNT(IF(manganese>0.05,1,NULL)),
										   			COUNT(IF(hardness>80,1,NULL)),
										   			COUNT(IF(aluminium>0.2,1,NULL))
													FROM samples INNER JOIN Sites ON site = Id_Site
													WHERE sample_date>=%s AND sample_date < %s AND type = 'Monthly Test'
													GROUP BY PLatform,site ORDER BY Platform,site""",(date(Current_date.year,1,1),Current_date+relativedelta(months=+1))).fetchall()

########WRITE TITLE#############
	Column = 0
	worksheet.merge_range(1,Column,2,Column,"Site",Title_format)
	Column += 1
	worksheet.merge_range(1,Column,2,Column,"Platform",Title_format)
	Column += 1
	worksheet.write(2,Column,"pH",Title_format)
	worksheet.write(1,Column,"6.5-8.5",Title_format)
	Column += 1
	worksheet.write(2,Column,"Turbidity (NTU)",Title_format)
	worksheet.write(1,Column,"1",Title_format)
	Column += 1
	worksheet.write(2,Column,"TDS (mg/L)",Title_format)
	worksheet.write(1,Column,"250",Title_format)
	Column += 1
	worksheet.write(2,Column,"Nitrate (mg/L)",Title_format)
	worksheet.write(1,Column,"50",Title_format)
	Column += 1
	worksheet.write(2,Column,"Nitrite (mg/L)",Title_format)
	worksheet.write(1,Column,"3",Title_format)
	Column += 1
	worksheet.write(2,Column,"NO3/NO2",Title_format)
	worksheet.write(1,Column,"1",Title_format)
	Column += 1
	worksheet.write(2,Column,"Arsenic (mg/L)",Title_format)
	worksheet.write(1,Column,"0.01",Title_format)
	Column += 1
	worksheet.write(2,Column,"Fluoride (mg/L)",Title_format)
	worksheet.write(1,Column,"1.5",Title_format)
	Column += 1
	worksheet.write(2,Column,"Iron (mg/L)",Title_format)
	worksheet.write(1,Column,"0.05",Title_format)
	Column += 1
	worksheet.write(2,Column,"Manganese (mg/L)",Title_format)
	worksheet.write(1,Column,"0.05",Title_format)
	Column += 1
	worksheet.write(2,Column,"Total Hardness (mg/L as CaCO3)",Title_format)
	worksheet.write(1,Column,"80",Title_format)
	Column += 1
	worksheet.write(2,Column,"Aluminium (mg/L)",Title_format)
	worksheet.write(1,Column,"0.2",Title_format)

	worksheet.merge_range(0,0,0,Column,"SUMMARY 2024 PHYSICAL AND CHEMICAL FAILURES",Title_format)
	worksheet.set_column(2,Column,len("Nitrate (mg/L) "))
	worksheet.autofilter(2,0,2,Column)
	worksheet.freeze_panes(2,2)

######WRITE DATA#####
	for i in range(len(ListSite)):
		Column =0
		InfoDashboardYTD= list(filter(lambda row: row[1] == ListSite[i][0], allInfoDashboardYTD)) or [["","","","","","","","","","","","","","","","","","","","",""]]
		worksheet.write(i+3,Column,ListSite[i][0])
		Column +=1
		worksheet.write(i+3,Column,ListSite[i][1])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][2])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][3])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][4])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][5])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][6])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][7])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][8])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][9])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][10])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][11])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][12])
		Column +=1
		worksheet.write(i+3,Column,InfoDashboardYTD[0][13])
		Column +=1

def AlertPerSiteMicro(Current_date,workbook):

	worksheet = workbook.add_worksheet("Failure Micro-biological")
	Title_format = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})

########DATA SELECTION##########

	ListSite = con.execute("""SELECT Id_Site,Platform FROM Sites WHERE Platform <> 'Dead'""").fetchall()
	allInfoDashboardlast6months = con.execute("""SELECT COUNT(IF(total_coliform_bottle>0 OR total_coliform_bottle='TNTC',1,NULL)),
										   			COUNT(IF(total_coliform>0 OR total_coliform='TNTC',1,NULL)),
										   			COUNT(IF(aluminium >= 0.2,1,NULL)),
													Platform, site
													FROM samples INNER JOIN Sites ON site = Id_Site
													WHERE sample_date>=%s AND sample_date < %s AND type = 'Monthly Test'
													GROUP BY PLatform,site ORDER BY Platform,site""",(Current_date-relativedelta(months=+5),Current_date+relativedelta(months=+1))).fetchall()

	allInfoDashboardYTD = con.execute("""SELECT COUNT(IF(total_coliform_bottle>0 OR total_coliform_bottle='TNTC',1,NULL)),
								   					COUNT(IF(total_coliform>0 OR total_coliform='TNTC',1,NULL)),
										   			COUNT(IF(aluminium >= 0.2,1,NULL)),
													Platform, site
													FROM samples INNER JOIN Sites ON site = Id_Site
													WHERE sample_date>=%s AND sample_date < %s AND type = 'Monthly Test'
													GROUP BY PLatform,site ORDER BY Platform,site""",(date(Current_date.year,1,1),Current_date+relativedelta(months=+1))).fetchall()

########WRITE TITLE#############
	Column = 0
	worksheet.write(1,Column,"Site",Title_format)
	Column += 1
	worksheet.write(1,Column,"Platform",Title_format)
	Column += 1
	worksheet.write(1,Column,"#Micro failures at Treatment system >0 CFU/100mL YTD",Title_format)
	Column += 1
	worksheet.write(1,Column,"#Micro failures Bottle 20L >0 CFU/100mL YTD",Title_format)
	Column += 1
	worksheet.write(1,Column,"#Micro failures at Treatment system past >0 CFU/100mL 6 months",Title_format)
	Column += 1
	worksheet.write(1,Column,"#Micro failures Bottle 20L past >0 CFU/100mL 6 months",Title_format)
	Column += 1
	worksheet.set_column('C:H',len("#Micro failures at Treatment system past 6 mo"))
	worksheet.autofilter(1,0,1,7)
	worksheet.freeze_panes(1,2)
	worksheet.merge_range(0,0,0,Column,"SUMMARY 2024 MICROBIOLOGICAL FAILURES",Title_format)

######WRITE DATA#####
	for i in range(len(ListSite)):
		Column =0
		InfoDashboard6months = list(filter(lambda row: row[4] == ListSite[i][0], allInfoDashboardlast6months)) or [["","",""]]
		InfoDashboardYTD= list(filter(lambda row: row[4] == ListSite[i][0], allInfoDashboardYTD)) or [["","",""]]
		worksheet.write(i+2,Column,ListSite[i][0])
		Column +=1
		worksheet.write(i+2,Column,ListSite[i][1])
		Column +=1
		worksheet.write(i+2,Column,InfoDashboardYTD[0][1])
		Column +=1
		worksheet.write(i+2,Column,InfoDashboardYTD[0][0])
		Column +=1
		worksheet.write(i+2,Column,InfoDashboard6months[0][1])
		Column +=1
		worksheet.write(i+2,Column,InfoDashboard6months[0][0])
		Column +=1

def GraphQuality(Current_date,workbook):
	Name_worksheet_Data = "Data for Charts"
	worksheet_data = workbook.add_worksheet(Name_worksheet_Data)
	worksheet_data.hide()
	Name_worksheet_Chart = "Charts"
	worksheet_graph = workbook.add_worksheet(Name_worksheet_Chart)
	DataForGraphQuality(Current_date,workbook,worksheet_data,Name_worksheet_Data,worksheet_graph,Name_worksheet_Chart,3,25,0,0)
	GraphEcoliColiform(workbook,worksheet_graph,Name_worksheet_Chart,2,2,3,25,Current_date)
	GraphAluTurb(workbook,worksheet_graph,Name_worksheet_Chart,23,2,3,25,Current_date)

def LaunchExcelCreationQuality(Current_date):
	Date_janv = date(Current_date.year,1,1)
	Month = Current_date.month
	if Month < 10:
		Month = '0' + str(Month)
	else:
		Month = str(Month)
	Year = str(Current_date.year)
	filepath = tempfile.gettempdir()+'/Quality Dashboard ' + Year + '-' + Month + '.xlsx'
	workbook = xlsxwriter.Workbook(filepath)
	ListTier = NewCalculTier(Current_date)[0]
	ListPlatform = con.execute("SELECT DISTINCT Code_Platform FROM Platform").fetchall()
	Platform = [i[0] for i in ListPlatform]
	
	RawQuality(Current_date,Date_janv,workbook,"All")
	RawQuality(Current_date,Date_janv,workbook,"First")
	RawQuality(Current_date,Date_janv,workbook,"Second")
	DashboardWaterQualityPlatform(Current_date,workbook)
	DashboardWaterQuality(Current_date,workbook)
	AlertPerSiteChemical(Current_date,workbook)
	AlertPerSiteMicro(Current_date,workbook)
	GraphQuality(Current_date,workbook)
	workbook.close()

if __name__ == '__main__':
	Current_date = date(2023,8,1)
	LaunchExcelCreationTechnical(Current_date)
