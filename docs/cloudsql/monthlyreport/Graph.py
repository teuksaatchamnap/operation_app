from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
from datetime import date
from calendar import monthrange
import db
from dateutil.relativedelta import *
from monthlyreport.Functionutils import QualityFailure, exchange_rate_year,isFloat


def GraphInterventionResponsiveness(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,TypeIntervention,Name):
	con = db.pool.connect()
	Date_format = workbook.add_format({'num_format':'mmm-yyyy'})
	Date_janv = date(Current_date.year,1,1)
	allIntervention_monthly = con.execute("""SELECT site, problem_date, 
								start_intervention, DATE_FORMAT(problem_date, '%%Y-%%m')
    							FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s AND site_problem_description IN %s""",(Date_janv,Current_date+relativedelta(months=+1),TypeIntervention)).fetchall()

	worksheet.write(lineData,colData+1,"%s int. < 1 day" %(Name))
	worksheet.set_column(colData+1,colData+1,len("Technical int. < 1 day"))
	worksheet.write(lineData,colData+2,"%s int. > 1 day" %(Name))
	worksheet.set_column(colData+2,colData+2,len("Technical int. > 1 day"))
	for i in range(1,Current_date.month+1):
		Intervention = list(filter(lambda row: row[3] == "%s-%s"%(Current_date.year,str(i).zfill(2)), allIntervention_monthly)) or [(0,0,0,0,0)]
		worksheet.write(lineData+i,colData,date(Current_date.year,i,1),Date_format)
		InterventionLess1day = 0
		for j in range(len(Intervention)):
			if Intervention[j][2] and Intervention[j][1] and (Intervention[j][2] - Intervention[j][1]).days <=1:
				InterventionLess1day += 1
		worksheet.write(lineData+i,colData+1,InterventionLess1day)
		worksheet.write(lineData+i,colData+2,len(Intervention)-InterventionLess1day)

	chart = workbook.add_chart({'type' : 'column', 'subtype': 'percent_stacked'})
	chart.add_series({
	'name' :     "<1 day",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+Current_date.month,colData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+1),xl_rowcol_to_cell(lineData+Current_date.month,colData+1)),
	'data_labels': {'value': False},
	})

	chart.add_series({
	'name' :     ">1 day",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+Current_date.month,colData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+2),xl_rowcol_to_cell(lineData+Current_date.month,colData+2)),
	'data_labels': {'value': False},
	})

	chart.set_y_axis({'name': '#Intervention','min':0})
	chart.set_x_axis({'name': 'Months'})
	chart.set_size({'width': 450,'height':280})
	chart.set_style(11)
	chart.set_title({'name': '%s Intervention Responsiveness'%(Name)})
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphInterventionEfficiency(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,TypeIntervention,Name):
	con = db.pool.connect()
	Date_format = workbook.add_format({'num_format':'mmm-yyyy'})
	Date_janv = date(Current_date.year,1,1)
	allIntervention_monthly = con.execute("""SELECT site, problem_date, 
								end_intervention, DATE_FORMAT(problem_date, '%%Y-%%m')
    							FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s AND site_problem_description IN %s""",(Date_janv,Current_date+relativedelta(months=+1),TypeIntervention)).fetchall()

	worksheet.write(lineData,colData+1,"%s int. < 1 day" %(Name))
	worksheet.set_column(colData+1,colData+1,len("Technical int. < 1 day"))
	worksheet.write(lineData,colData+2,"%s int. > 1 day" %(Name))
	worksheet.set_column(colData+2,colData+2,len("Technical int. > 1 day"))
	for i in range(1,Current_date.month+1):
		Intervention = list(filter(lambda row: row[3] == "%s-%s"%(Current_date.year,str(i).zfill(2)), allIntervention_monthly)) or [(0,0,0,0,0)]
		worksheet.write(lineData+i,colData,date(Current_date.year,i,1),Date_format)
		InterventionLess1day = 0
		for j in range(len(Intervention)):
			if Intervention[j][2] and Intervention[j][1] and (Intervention[j][2] - Intervention[j][1]).days <=1:
				InterventionLess1day += 1
		worksheet.write(lineData+i,colData+1,InterventionLess1day)
		worksheet.write(lineData+i,colData+2,len(Intervention)-InterventionLess1day)

	chart = workbook.add_chart({'type' : 'column', 'subtype': 'percent_stacked'})
	chart.add_series({
	'name' :     "<1 day",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+Current_date.month,colData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+1),xl_rowcol_to_cell(lineData+Current_date.month,colData+1)),
	'data_labels': {'value': False},
	})

	chart.add_series({
	'name' :     ">1 day",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+Current_date.month,colData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+2),xl_rowcol_to_cell(lineData+Current_date.month,colData+2)),
	'data_labels': {'value': False},
	})

	chart.set_y_axis({'name': '#Intervention','min':0})
	chart.set_x_axis({'name': 'Months'})
	chart.set_size({'width': 450,'height':280})
	chart.set_style(11)
	chart.set_title({'name': '%s Intervention Efficiency'%(Name)})
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphInterventionType(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Technical,Quality):
	con = db.pool.connect()
	Date_format = workbook.add_format({'num_format':'mmm-yyyy'})
	Date_janv = date(Current_date.year,1,1)
	allIntervention_technical = con.execute("""SELECT count(id), DATE_FORMAT(problem_date, '%%Y-%%m')
    							FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s AND site_problem_description IN %s
    							GROUP BY DATE_FORMAT(problem_date, '%%Y-%%m')""",(Date_janv,Current_date+relativedelta(months=+1),Technical)).fetchall()

	allIntervention_quality = con.execute("""SELECT count(id), DATE_FORMAT(problem_date, '%%Y-%%m')
    							FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s AND site_problem_description IN %s
    							GROUP BY DATE_FORMAT(problem_date, '%%Y-%%m')""",(Date_janv,Current_date+relativedelta(months=+1),Quality)).fetchall()

	worksheet.write(lineData,colData+1,"Technical int.")
	worksheet.write(lineData,colData+2,"Quality int.")

	for i in range(1,Current_date.month+1):
		InterventionTechnical = list(filter(lambda row: row[1] == "%s-%s"%(Current_date.year,str(i).zfill(2)), allIntervention_technical)) or [(0,0,0,0,0)]
		InterventionQuality = list(filter(lambda row: row[1] == "%s-%s"%(Current_date.year,str(i).zfill(2)), allIntervention_quality)) or [(0,0,0,0,0)]
		worksheet.write(lineData+i,colData,date(Current_date.year,i,1),Date_format)
		worksheet.write(lineData+i,colData+1,InterventionTechnical[0][0])
		worksheet.write(lineData+i,colData+2,InterventionQuality[0][0])

	chart = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
	chart.add_series({
	'name' :     "Tech. int.",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+Current_date.month,colData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+1),xl_rowcol_to_cell(lineData+Current_date.month,colData+1)),
	'data_labels': {'value': False},
	})

	chart.add_series({
	'name' :     "Qual. int.",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+Current_date.month,colData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+2),xl_rowcol_to_cell(lineData+Current_date.month,colData+2)),
	'data_labels': {'value': False},
	})

	chart.set_y_axis({'name': '#Intervention'})
	chart.set_x_axis({'name': 'Months'})
	chart.set_size({'width': 450,'height':280})
	chart.set_style(11)
	chart.set_title({'name': 'Intervention Type'})
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphInterventionList(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Technical,Quality):
	con = db.pool.connect()
	Date_format = workbook.add_format({'num_format':'mmm-yyyy'})
	Date_janv = date(Current_date.year,1,1)
	allIntervention = con.execute("""SELECT count(id), DATE_FORMAT(problem_date, '%%Y-%%m'),site_problem_description
    							FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s
    							GROUP BY DATE_FORMAT(problem_date, '%%Y-%%m'),site_problem_description""",(Date_janv,Current_date+relativedelta(months=+1))).fetchall()

	allProblemName = con.execute("""SELECT DISTINCT site_problem_description FROM technicals 
							WHERE site_problem_description IS NOT NULL """).fetchall()

	for j in range(len(allProblemName)):
		InterventionProblem = list(filter(lambda row: row[2] == allProblemName[j][0], allIntervention)) or [(0,0,0,0,0)]
		worksheet.write(lineData,colData+1+j,allProblemName[j][0])
		for i in range(1,Current_date.month+1):
			Intervention = list(filter(lambda row: row[1] == "%s-%s"%(Current_date.year,str(i).zfill(2)), InterventionProblem)) or [(0,0,0,0,0)]
			worksheet.write(lineData+i,colData,date(Current_date.year,i,1),Date_format)
			worksheet.write(lineData+i,colData+1+j,Intervention[0][0])

	chart = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
	for j in range(len(allProblemName)):
		chart.add_series({
		'name' :     "%s"%(allProblemName[j][0]),
		'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+Current_date.month,colData)),
		'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+1+j),xl_rowcol_to_cell(lineData+Current_date.month,colData+1+j)),
		'data_labels': {'value': False},
		})

	chart.set_y_axis({'name': '#Intervention'})
	chart.set_x_axis({'name': 'Months'})
	chart.set_size({'width': 1000,'height':600})
	#chart.set_style(11)
	chart.set_title({'name': 'Intervention Type'})
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphInterventionPerTechnicians(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Technical,Quality):
	con = db.pool.connect()
	Date_format = workbook.add_format({'num_format':'mmm-yyyy'})
	Title_format = workbook.add_format({'bold':True,"font_size":18,"center_across":True,'bg_color':'#FFFF00'})
	Date_janv = date(Current_date.year,1,1)
	allIntervention_technical = con.execute("""SELECT technician,count(id), DATE_FORMAT(problem_date, '%%Y-%%m')
    							FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s AND site_problem_description IN %s
    							GROUP BY DATE_FORMAT(problem_date, '%%Y-%%m'),technician""",(Date_janv,Current_date+relativedelta(months=+1),Technical)).fetchall()

	allIntervention_quality = con.execute("""SELECT technician,count(id), DATE_FORMAT(problem_date, '%%Y-%%m')
    							FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s AND site_problem_description IN %s
    							GROUP BY DATE_FORMAT(problem_date, '%%Y-%%m'),technician""",(Date_janv,Current_date+relativedelta(months=+1),Quality)).fetchall()

	allNameTechnician = con.execute("""SELECT DISTINCT technician FROM technicals WHERE start_intervention >= %s 
    							AND start_intervention < %s""",(Date_janv,Current_date+relativedelta(months=+1))).fetchall()

	# worksheet.write(lineData,colData+1,"Technical int.")
	# worksheet.write(lineData,colData+2,"Quality int.")

	for j in range(len(allNameTechnician)):
		InterventionTechnicalDate = list(filter(lambda row: row[0] == allNameTechnician[j][0], allIntervention_technical)) or [(0,0,0,0,0)]
		InterventionQualityDate = list(filter(lambda row: row[0] == allNameTechnician[j][0], allIntervention_quality)) or [(0,0,0,0,0)]
		worksheet.write(lineData,colData+j+1,allNameTechnician[j][0])
		worksheet.write(lineData,colData+j+1+len(allNameTechnician),allNameTechnician[j][0])
		for i in range(1,Current_date.month+1):
			InterventionTechnical = list(filter(lambda row: row[2] == "%s-%s"%(Current_date.year,str(i).zfill(2)), InterventionTechnicalDate)) or [(0,0,0,0,0)]
			InterventionQuality = list(filter(lambda row: row[2] == "%s-%s"%(Current_date.year,str(i).zfill(2)), InterventionQualityDate)) or [(0,0,0,0,0)]
			worksheet.write(lineData+i,colData,date(Current_date.year,i,1),Date_format)
			worksheet.write(lineData+i,colData+1+j,InterventionTechnical[0][1])
			worksheet.write(lineData+i,colData+1+j+len(allNameTechnician),InterventionQuality[0][1])

	lineSelectData = lineGraph
	colSelectData = colGraph +8
	worksheet.data_validation("%s"%(xl_rowcol_to_cell(lineSelectData,colSelectData+1)),{'validate' : 'list',
                                    'source' : "%s:%s"%(xl_rowcol_to_cell(lineData,colData+1),xl_rowcol_to_cell(lineData,colData+1+len(allNameTechnician)))})
	worksheet.merge_range(lineSelectData,colSelectData+1,lineSelectData,colSelectData+2,"Enter Technicians name",Title_format)

	worksheet.write(lineSelectData+1,colSelectData+1,"Technical")
	worksheet.write(lineSelectData+1,colSelectData+2,"Graph")
	for i in range(1,Current_date.month+1):
		worksheet.write(lineSelectData+i+1,colSelectData,date(Current_date.year,i,1),Date_format)
		worksheet.write_formula(lineSelectData+i+1,colSelectData+1,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(xl_rowcol_to_cell(lineData+i,colData+1),xl_rowcol_to_cell(lineData+i,colData+1+len(allNameTechnician)),xl_rowcol_to_cell(lineSelectData,colSelectData+1),xl_rowcol_to_cell(lineData,colData+1),xl_rowcol_to_cell(lineData,colData+1+len(allNameTechnician))))
		worksheet.write_formula(lineSelectData+i+1,colSelectData+2,"=INDEX(%s:%s,MATCH(%s,%s:%s,0))"%(xl_rowcol_to_cell(lineData+i,colData+1+len(allNameTechnician)),xl_rowcol_to_cell(lineData+i,colData+1+len(allNameTechnician)*2),xl_rowcol_to_cell(lineSelectData,colSelectData+1),xl_rowcol_to_cell(lineData,colData+1+len(allNameTechnician)),xl_rowcol_to_cell(lineData,colData+1+len(allNameTechnician)*2)))

	chart = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
	chart.add_series({
	'name' :     "Tech. int.",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineSelectData+2,colSelectData),xl_rowcol_to_cell(lineSelectData+Current_date.month+1,colSelectData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineSelectData+2,colSelectData+1),xl_rowcol_to_cell(lineSelectData+Current_date.month+1,colSelectData+1)),
	'data_labels': {'value': False},
	})

	chart.add_series({
	'name' :     "Qual. int.",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineSelectData+2,colSelectData),xl_rowcol_to_cell(lineSelectData+Current_date.month+1,colSelectData)),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineSelectData+2,colSelectData+2),xl_rowcol_to_cell(lineSelectData+Current_date.month+1,colSelectData+2)),
	'data_labels': {'value': False},
	})

	chart.set_y_axis({'name': '#Intervention'})
	chart.set_x_axis({'name': 'Months'})
	chart.set_size({'width': 450,'height':280})
	chart.set_style(11)
	chart.set_title({'name': 'Intervention Type'})
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphDebtEvolution(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Platform):
	con = db.pool.connect()
	start_date = date(Current_date.year-1,1,1)
	Number_format = workbook.add_format({'num_format':'# ### ##0'})

#############DATA SELECTION#############
	if Platform == "Total":
		query = con.execute("""SELECT SUM(Amount_expenses),DATE_FORMAT(Month, '%%Y-%%m-%%d')
							FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
							WHERE Month >= %s AND Month <= %s AND Ref_expenses = 'debt' AND Amount_expenses > 0
							GROUP BY DATE_FORMAT(Month, '%%Y-%%m-%%d')""",(start_date,Current_date+relativedelta(months=+1)))
		debt = query.fetchall()

		query = con.execute("""SELECT SUM(Amount_expenses),DATE_FORMAT(Month, '%%Y-%%m-%%d')
							FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
							WHERE Month >= %s AND Month <= %s AND Ref_expenses = 'debt' AND Amount_expenses < 0
							GROUP BY DATE_FORMAT(Month, '%%Y-%%m-%%d')""",(start_date,Current_date+relativedelta(months=+1)))
		saving = query.fetchall()

	else:
		query = con.execute("""SELECT SUM(Amount_expenses),DATE_FORMAT(Month, '%%Y-%%m-%%d')
							FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
							WHERE Month >= %s AND Month <= %s AND Ref_expenses = 'debt' AND Amount_expenses > 0 AND Platform = %s
							GROUP BY DATE_FORMAT(Month, '%%Y-%%m-%%d')""",(start_date,Current_date+relativedelta(months=+1),Platform))
		debt = query.fetchall()

		query = con.execute("""SELECT SUM(Amount_expenses),DATE_FORMAT(Month, '%%Y-%%m-%%d')
							FROM Expenses JOIN Sites ON Sites.Id_Site = Expenses.Id_Site 
							WHERE Month >= %s AND Month <= %s AND Ref_expenses = 'debt' AND Amount_expenses < 0 AND Platform = %s
							GROUP BY DATE_FORMAT(Month, '%%Y-%%m-%%d')""",(start_date,Current_date+relativedelta(months=+1),Platform))
		saving = query.fetchall()

############WRITE DATA###############
	Loop = 0
	while start_date < Current_date + relativedelta(months=+1):
		debtSituation = list(filter(lambda row: row[1] == str(start_date + relativedelta(months=+1)), debt)) or [(0, 0)]
		savingSituation = list(filter(lambda row: row[1] == str(start_date + relativedelta(months=+1)), saving)) or [(0, 0)]
		worksheet.write(lineData, colData + Loop, "%s-%s" % (start_date.year, start_date.month))
		worksheet.write(lineData + 1, colData + Loop, debtSituation[0][0] / exchange_rate_year(start_date), Number_format)
		worksheet.write(lineData + 2, colData + Loop, abs(savingSituation[0][0]) / exchange_rate_year(start_date), Number_format)
		start_date += relativedelta(months=+1)
		Loop += 1

#############WRITE GRAPH############
	chart = workbook.add_chart({'type': 'column'})
	chart.add_series({
		'name': "Debt",
		'categories': '=\'%s\'!%s:%s' % (Name_worksheet, xl_rowcol_to_cell(lineData, colData), xl_rowcol_to_cell(lineData, colData + Loop - 1)),
		'values': '=\'%s\'!%s:%s' % (Name_worksheet, xl_rowcol_to_cell(lineData + 1, colData), xl_rowcol_to_cell(lineData + 1, colData + Loop - 1)),
		'data_labels': {'value': False},
		'fill': {'color': '#B4C7E7'},
		'border': False,
		'gap': 33,
	})

	line_chart = workbook.add_chart({'type': 'line'})
	line_chart.add_series({
		'name': "Saving",
		'categories': '=\'%s\'!%s:%s' % (Name_worksheet, xl_rowcol_to_cell(lineData, colData), xl_rowcol_to_cell(lineData, colData + Loop - 1)),
		'values': '=\'%s\'!%s:%s' % (Name_worksheet, xl_rowcol_to_cell(lineData + 2, colData), xl_rowcol_to_cell(lineData + 2, colData + Loop - 1)),
		'data_labels': {'value': False},
		'line': {'color': '#FF0000'},
	})

	chart.combine(line_chart)

	if Platform != "Total":
		chart.set_y_axis({'max': 25000})
	chart.set_legend({'position': 'bottom'})
	chart.set_size({'width': 500, 'height': 310})
	chart.set_title({'name': 'Debt Situation %s in $' % (Platform)})
	worksheet.insert_chart('%s' % (xl_rowcol_to_cell(lineGraph, colGraph)), chart)

def GraphBotDay(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Platform,WithSchool):
	con = db.pool.connect()
	
	NbYear = 2
	start_date = date(Current_date.year-NbYear,1,1)

#########SELECTION DATA########
	Total_Sales = con.execute("""SELECT AVG((Total_Sales-Bottle_Sales)/Number_Open_Days),
									AVG((Total_Sales-Bottle_Sales-WiS_Sales)/Number_Open_Days),DATE_FORMAT(Month, '%%Y-%%m-%%d') 
									FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
									WHERE Month <= %s AND Month >= %s AND Platform IN %s 
									GROUP BY Month ORDER BY Month""",(Current_date,start_date,Platform)).fetchall()

	Total_Objective = con.execute("""SELECT AVG(PrevisionsSalesTot/DAYOFMONTH(LAST_DAY(Month))),DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales
	                                        INNER JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site 
	                                        WHERE Month <= %s AND Month >= %s AND PrevisionsSalesTot > 0 AND  Platform IN %s 
	                                        GROUP BY Month ORDER BY Month
	                                        """,(date(Current_date.year,12,1),date(Current_date.year,1,1),Platform)).fetchall()  

##############WRITE DATA###############
	Loop = 0
	while start_date<=date(Current_date.year,12,1):
		if WithSchool:
			NumberSchool = 0
		else:
			NumberSchool = 1
		Sales = list(filter(lambda row: row[2] == str(start_date), Total_Sales)) or [(0,0)]
		Objective = list(filter(lambda row: row[1] == str(start_date), Total_Objective)) or [(0,0)]
		if start_date<= Current_date:
			worksheet.write(lineData,colData+Loop,start_date.month)
			worksheet.write(lineData+1,colData+Loop,Sales[0][NumberSchool])
		if WithSchool == False and start_date.year == Current_date.year:
			worksheet.write(lineData+2,colData+Loop,Objective[0][0])
		start_date+= relativedelta(months=+1)
		Loop += 1

############WRITE GRAPH###############
	chart = workbook.add_chart({'type' : 'line'})
	for i in range(0,NbYear+1):
		chart.add_series({
		'name' :     "%s"%(Current_date.year-NbYear+i),
		'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData,colData+12*i),xl_rowcol_to_cell(lineData,colData+12*(i+1))),
		'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+1,colData+12*i),xl_rowcol_to_cell(lineData+1,colData+12*(i+1))),
		'data_labels': {'value': False},
		'marker': {'type': 'diamond'},
		})

	chart.add_series({
	'name' :     "Objective",
	'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData,colData+12*NbYear),xl_rowcol_to_cell(lineData,colData+12*(NbYear+1))),
	'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+2,colData+12*NbYear),xl_rowcol_to_cell(lineData+2,colData+12*(NbYear+1))),
	'data_labels': {'value': False},
	'marker': {'type': 'diamond'},
	})


	chart.set_y_axis({'min':50,'max':140})
	chart.set_size({'width': 425,'height':265})
	if WithSchool:
		chart.set_title({'name': 'Bot/day %s inc. WinS'%(Platform[-1])})
	else:
		chart.set_title({'name': 'Bot/day %s exc. WinS'%(Platform[-1])})
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphMonthlyAdvisor(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,lineList,colList,Current_date):
	con = db.pool.connect()
	
	NbYear = 2
	start_date = date(Current_date.year-NbYear,1,1)
	Number_format = workbook.add_format({'num_format':'# ### ##0'})

#########DATA SELECTION#########
	Advisor = con.execute("""SELECT DISTINCT Advisor FROM Sites 
							WHERE Platform <> 'Dead' AND Advisor <> ''""").fetchall()
	Platform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform <> 'Dead'""").fetchall()
	Platform = [i[0] for i in Platform]
	ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Old_Platform IN %s 
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(date(Current_date.year-1,1,1),Platform)).fetchall()
	ListSite_LikeforLike = [i[0] for i in ListSite_LikeforLike]

	allSales_LfL = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') 
    												FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    												WHERE Month <=%s AND Month >= %s AND Sales.Id_Site IN %s 
    												GROUP BY Advisor,Month""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike)).fetchall()
	
	allSales_Other = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') 
    										FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    										WHERE Month <=%s AND Month >= %s AND Sales.Id_Site NOT IN %s 
    										GROUP BY Advisor,Month""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike)).fetchall()
	allSales_N_1 = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') 
    											FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    											WHERE Month <=%s AND Month >= %s 
    											GROUP BY Advisor,Month""",(date(Current_date.year-1,12,1),date(Current_date.year-1,1,1))).fetchall()

	allObjectives_LfL = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month >= %s AND PrevisionsSales.Id_Site IN %s 
                                            GROUP BY Advisor,Month""",(date(Current_date.year,12,1),date(Current_date.year,1,1),ListSite_LikeforLike)).fetchall()
    
	allObjectives_Other = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor,DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month >= %s AND PrevisionsSales.Id_Site NOT IN %s 
                                            GROUP BY Advisor,Month""",(date(Current_date.year,12,1),date(Current_date.year,1,1),ListSite_LikeforLike)).fetchall()

############WRITE DATA############
	VarWriteTitle = False
	for j in range(1,13):
		Sales_LfL_Advisor = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), allSales_LfL)) or [(0,0)]
		Sales_Other_Advisor = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), allSales_Other)) or [(0,0)]
		Sales_all_N_1_Advisor = list(filter(lambda row: row[2] == str(date(Current_date.year-1,j,1)), allSales_N_1)) or [(0,0)]
		Objective_LfL_Advisor = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), allObjectives_LfL)) or [(0,0)]
		Objective_Other_Advisor = list(filter(lambda row: row[2] == str(date(Current_date.year,j,1)), allObjectives_Other)) or [(0,0)]

		for i in range(len(Advisor)):
			Sales_LfL = list(filter(lambda row: row[1] == Advisor[i][0], Sales_LfL_Advisor)) or [(0,0)]
			Sales_Other = list(filter(lambda row: row[1] == Advisor[i][0], Sales_Other_Advisor)) or [(0,0)]
			Sales_all_N_1 = list(filter(lambda row: row[1] == Advisor[i][0], Sales_all_N_1_Advisor)) or [(0,0)]
			Objective_LfL = list(filter(lambda row: row[1] == Advisor[i][0], Objective_LfL_Advisor)) or [(0,0)]
			Objective_Other = list(filter(lambda row: row[1] == Advisor[i][0], Objective_Other_Advisor)) or [(0,0)]

			if not VarWriteTitle:
				worksheet.write(lineData,colData+(i+1)*5+1,"%s-%s-Other"%(Advisor[i][0],Current_date.year))
				worksheet.write(lineData,colData+(i+1)*5+2,"%s-%s-LfL"%(Advisor[i][0],Current_date.year))
				worksheet.write(lineData,colData+(i+1)*5+3,"%s-Objective-Other"%(Advisor[i][0]))
				worksheet.write(lineData,colData+(i+1)*5+4,"%s-Objective-LfL"%(Advisor[i][0]))
				worksheet.write(lineData,colData+(i+1)*5+5,"%s-%s"%(Advisor[i][0],Current_date.year-1))
				worksheet.merge_range(lineData+1,colData+(i+1)*5+1,lineData+1,colData+(i+1)*5+5,Advisor[i][0])
			
	    	

			worksheet.write(lineData+j*3,colData+(i+1)*5+1,Sales_Other[0][0],Number_format)
			worksheet.write(lineData+j*3,colData+(i+1)*5+2,Sales_LfL[0][0],Number_format)
			worksheet.write(lineData+j*3+1,colData+(i+1)*5+3,Objective_Other[0][0],Number_format)
			worksheet.write(lineData+j*3+1,colData+(i+1)*5+4,Objective_LfL[0][0],Number_format)
			worksheet.write(lineData+j*3+2,colData+(i+1)*5+5,Sales_all_N_1[0][0],Number_format)
		VarWriteTitle = True
		
		worksheet.write(lineData+j*3,colData,j,Number_format)
		worksheet.write_formula(lineData+j*3,colData+1,"=INDEX(%s:%s,MATCH(CONCATENATE(%s,\"-\",%s,\"-Other\"),%s:%s,0))"%(xl_rowcol_to_cell(lineData+j*3,colData+5),xl_rowcol_to_cell(lineData+j*3,colData+5+5*len(Advisor)),xl_rowcol_to_cell(lineList,colList),str(Current_date.year),xl_rowcol_to_cell(lineData,colData+5),xl_rowcol_to_cell(lineData,colData+5+5*len(Advisor))),Number_format)
		worksheet.write_formula(lineData+j*3,colData+2,"=INDEX(%s:%s,MATCH(CONCATENATE(%s,\"-\",%s,\"-LfL\"),%s:%s,0))"%(xl_rowcol_to_cell(lineData+j*3,colData+5),xl_rowcol_to_cell(lineData+j*3,colData+5+5*len(Advisor)),xl_rowcol_to_cell(lineList,colList),str(Current_date.year),xl_rowcol_to_cell(lineData,colData+5),xl_rowcol_to_cell(lineData,colData+5+5*len(Advisor))),Number_format)
		worksheet.write_formula(lineData+j*3+1,colData+3,"=INDEX(%s:%s,MATCH(CONCATENATE(%s,\"-Objective-Other\"),%s:%s,0))"%(xl_rowcol_to_cell(lineData+j*3+1,colData+5),xl_rowcol_to_cell(lineData+j*3+1,colData+5+5*len(Advisor)),xl_rowcol_to_cell(lineList,colList),xl_rowcol_to_cell(lineData,colData+5),xl_rowcol_to_cell(lineData,colData+5+4*len(Advisor))),Number_format)
		worksheet.write_formula(lineData+j*3+1,colData+4,"=INDEX(%s:%s,MATCH(CONCATENATE(%s,\"-Objective-LfL\"),%s:%s,0))"%(xl_rowcol_to_cell(lineData+j*3+1,colData+5),xl_rowcol_to_cell(lineData+j*3+1,colData+5+5*len(Advisor)),xl_rowcol_to_cell(lineList,colList),xl_rowcol_to_cell(lineData,colData+5),xl_rowcol_to_cell(lineData,colData+5+4*len(Advisor))),Number_format)
		worksheet.write_formula(lineData+j*3+2,colData+5,"=INDEX(%s:%s,MATCH(CONCATENATE(%s,\"-\",%s),%s:%s,0))"%(xl_rowcol_to_cell(lineData+j*3+2,colData+5),xl_rowcol_to_cell(lineData+j*3+2,colData+5+5*len(Advisor)),xl_rowcol_to_cell(lineList,colList),str(Current_date.year-1),xl_rowcol_to_cell(lineData,colData+5),xl_rowcol_to_cell(lineData,colData+5+4*len(Advisor))),Number_format)

	worksheet.data_validation('%s'%xl_rowcol_to_cell(lineList,colList),{'validate' : 'list',
                                    'source' : "%s:%s"%(xl_rowcol_to_cell(lineData+1,colData+5),xl_rowcol_to_cell(lineData+1,colData+(len(Advisor)+1)*5+5))})
	worksheet.write_formula("%s"%xl_rowcol_to_cell(lineList,colList),"=%s"%(xl_rowcol_to_cell(lineData+1,colData+6)))

###########WRITE GRAPH##########

	chart_sales_advisor = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
	Legend = ["%s Other"%(Current_date.year),"%s LfL"%(Current_date.year),"Objective Other","Objective LfL",str(Current_date.year-1)]
	Style = ["#B9CDE5","#376092","#93CDDD","#215968","#4F81BD"]
	for i in range(1,6):
	    chart_sales_advisor.add_series({
	    'name' :     Legend[5-i],
	    'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+3,colData),xl_rowcol_to_cell(lineData+12*3+2,colData)),
	    'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+3,colData+6-i),xl_rowcol_to_cell(lineData+12*3+2,colData+6-i)),
	    'data_labels': {'value': False},
	    'gap':0,
	    'fill' : {'color': '%s'%(Style[i-1])},
	    })
    

	chart_sales_advisor.set_title({
	'name': '#Bot sold YTD - Advisor',
	'name_font': {
	    'name': 'Calibri',
		'size': 12,
		'color': 'black',
	},
	})

	chart_sales_advisor.set_size({'width': 1400, 'height': 400})
	chart_sales_advisor.set_x_axis({'num_font': {'size': 8, 'bold': False}})
	chart_sales_advisor.set_legend({'font' : {'size' : 8}})
	chart_sales_advisor.show_hidden_data()
	chart_sales_advisor.set_table({'vertical':False,'font':{'size' : 5}})
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart_sales_advisor)

def GraphMonthlyPlatform(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Platform):
	con = db.pool.connect()
	
	NbYear = 2
	start_date = date(Current_date.year-NbYear,1,1)
	Number_format = workbook.add_format({'num_format':'# ### ##0'})

#########DATA SELECTION#########

	ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Old_Platform IN %s 
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(date(Current_date.year-1,1,1),Platform)).fetchall()

	ListSite_LikeforLike = [i[0] for i in ListSite_LikeforLike]

	allSales_LfL = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),DATE_FORMAT(Month, '%%Y-%%m-%%d') 
    												FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    												WHERE Month <=%s AND Month >= %s AND Sales.Id_Site IN %s AND Platform IN %s
    												GROUP BY Month""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()

	allSales_Other = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),DATE_FORMAT(Month, '%%Y-%%m-%%d') 
    										FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    										WHERE Month <=%s AND Month >= %s AND Sales.Id_Site NOT IN %s AND Platform IN %s 
    										GROUP BY Month""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()
	
	allSales_N_1 = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),DATE_FORMAT(Month, '%%Y-%%m-%%d') 
    											FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    											WHERE Month <=%s AND Month >= %s AND Platform IN %s 
    											GROUP BY Month""",(date(Current_date.year-1,12,1),date(Current_date.year-1,1,1),Platform)).fetchall()

	
	allObjectives_LfL = con.execute("""SELECT SUM(PrevisionsSalesTot),DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month >= %s AND PrevisionsSales.Id_Site IN %s AND Platform IN %s 
                                            GROUP BY Month""",(date(Current_date.year,12,1),date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()
    
	
	allObjectives_Other = con.execute("""SELECT SUM(PrevisionsSalesTot),DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month >= %s AND PrevisionsSales.Id_Site NOT IN %s AND Platform IN %s 
                                            GROUP BY Month""",(date(Current_date.year,12,1),date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()

############WRITE DATA############
	worksheet.write(lineData,colData+1,"%s-%s-LfL"%(Platform[-1],Current_date.year))
	worksheet.write(lineData,colData+2,"%s-%s-Other"%(Platform[-1],Current_date.year))
	worksheet.write(lineData,colData+3,"%s-Objective-LfL"%(Platform[-1]))
	worksheet.write(lineData,colData+4,"%s-Objective-Other"%(Platform[-1]))
	worksheet.write(lineData,colData+5,"%s-%s"%(Platform[-1],Current_date.year-1))
	worksheet.merge_range(lineData+1,colData+1,lineData+1,colData+5,Platform[-1])
	for j in range(1,13):
		Sales_LfL = list(filter(lambda row: row[1] == str(date(Current_date.year,j,1)), allSales_LfL)) or [(0,0)]
		Sales_Other = list(filter(lambda row: row[1] == str(date(Current_date.year,j,1)), allSales_Other)) or [(0,0)]
		Sales_all_N_1 = list(filter(lambda row: row[1] == str(date(Current_date.year-1,j,1)), allSales_N_1)) or [(0,0)]
		Objective_LfL= list(filter(lambda row: row[1] == str(date(Current_date.year,j,1)), allObjectives_LfL)) or [(0,0)]
		Objective_Other = list(filter(lambda row: row[1] == str(date(Current_date.year,j,1)), allObjectives_Other)) or [(0,0)]

		worksheet.write(lineData+j*3,colData,j,Number_format)
		worksheet.write(lineData+j*3,colData+1,Sales_LfL[0][0],Number_format)
		worksheet.write(lineData+j*3,colData+2,Sales_Other[0][0],Number_format)
		worksheet.write(lineData+j*3+1,colData+3,Objective_LfL[0][0],Number_format)
		worksheet.write(lineData+j*3+1,colData+4,Objective_Other[0][0],Number_format)
		worksheet.write(lineData+j*3+2,colData+5,Sales_all_N_1[0][0],Number_format)

###########WRITE GRAPH##########

	chart = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
	Legend = ["%s LfL"%(Current_date.year),"%s Other"%(Current_date.year),"Objective LfL","Objective Other",str(Current_date.year-1)]
	for i in range(1,6):
	    chart.add_series({
	    'name' :     Legend[5-i],
	    'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+3,colData),xl_rowcol_to_cell(lineData+12*3+2,colData)),
	    'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData+3,colData+6-i),xl_rowcol_to_cell(lineData+12*3+2,colData+6-i)),
	    'data_labels': {'value': False},
	    'gap':0,
	    })
    

	chart.set_title({
	'name': '#Bot sold exc. WinS %s'%(Platform[-1]),
	'name_font': {
	    'name': 'Calibri',
		'size': 12,
		'color': 'black',
	},
	})

	chart.set_size({'width': 425, 'height': 250})
	chart.set_x_axis({'num_font': {'size': 8, 'bold': False}})
	chart.set_legend({'font' : {'size' : 8}})
	chart.show_hidden_data()
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphAdvisorperPlatform(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Platform):
	con=db.pool.connect()
#########DATA SELECTION########
	
	ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Old_Platform IN %s 
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(date(Current_date.year-1,1,1),Platform)).fetchall()

	ListSite_LikeforLike = [i[0] for i in ListSite_LikeforLike]

	Advisor = con.execute("""SELECT DISTINCT Advisor FROM Sites WHERE 1 = %s AND Platform IN %s AND Advisor <> '' AND Advisor <> 'Stop'""",(1,Platform)).fetchall()
	allSales_LfL = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor
    												FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    												WHERE Month <=%s AND Month >= %s AND Sales.Id_Site IN %s AND Platform IN %s
    												GROUP BY Advisor""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()


	allSales_Other = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor
    										FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    										WHERE Month <=%s AND Month >= %s AND Sales.Id_Site NOT IN %s AND Platform IN %s 
    										GROUP BY Advisor""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()


	allSales_N_1 = con.execute("""SELECT SUM(Total_sales - Bottle_Sales - WiS_Sales),Advisor
    											FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
    											WHERE Month <=%s AND Month >= %s AND Platform IN %s 
    											GROUP BY Advisor""",(Current_date-relativedelta(months=+12),date(Current_date.year-1,1,1),Platform)).fetchall()

	
	allObjectives_LfL = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month >= %s AND PrevisionsSales.Id_Site IN %s AND Platform IN %s 
                                            GROUP BY Advisor""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()
    
	
	allObjectives_Other = con.execute("""SELECT SUM(PrevisionsSalesTot),Advisor FROM PrevisionsSales 
                                            JOIN Sites ON Sites.Id_Site = PrevisionsSales.Id_Site
                                            WHERE Month <=%s AND Month >= %s AND PrevisionsSales.Id_Site NOT IN %s AND Platform IN %s 
                                            GROUP BY Advisor""",(Current_date,date(Current_date.year,1,1),ListSite_LikeforLike,Platform)).fetchall()

########WRITE DATA######
	
	for i in range(len(Advisor)):

		Sales_LfL = list(filter(lambda row: row[1] == Advisor[i][0], allSales_LfL)) or [(0,0)]
		Sales_Other = list(filter(lambda row: row[1] == Advisor[i][0], allSales_Other)) or [(0,0)]
		Sales_all_N_1 = list(filter(lambda row: row[1] == Advisor[i][0], allSales_N_1)) or [(0,0)]
		Objective_LfL= list(filter(lambda row: row[1] == Advisor[i][0], allObjectives_LfL)) or [(0,0)]
		Objective_Other = list(filter(lambda row: row[1] == Advisor[i][0], allObjectives_Other)) or [(0,0)]

		worksheet.write(lineData+3*i,colData,Advisor[i][0])
		worksheet.write(lineData+3*i,colData+1,Sales_LfL[0][0])
		worksheet.write(lineData+3*i,colData+2,Sales_Other[0][0])
		worksheet.write(lineData+3*i+1,colData+3,Objective_LfL[0][0])
		worksheet.write(lineData+3*i+1,colData+4,Objective_Other[0][0])
		worksheet.write(lineData+3*i+2,colData+5,Sales_all_N_1[0][0])


	chart = workbook.add_chart({'type' : 'column', 'subtype': 'stacked'})
	Legend = ["%s LfL"%(Current_date.year),"%s Other"%(Current_date.year),"Objective LfL","Objective Other",str(Current_date.year-1)]
	Style = ["#B9CDE5","#376092","#93CDDD","#215968","#4F81BD"]

	for i in range(1,6):
		if i==1:
			valgap=15
		else:
			valgap=0
		chart.add_series({
	    'name' :     Legend[5-i],
	    'categories': '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData,colData),xl_rowcol_to_cell(lineData+len(Advisor)*3,colData)),
	    'values':     '=\'%s\'!%s:%s'%(Name_worksheet,xl_rowcol_to_cell(lineData,colData+6-i),xl_rowcol_to_cell(lineData+len(Advisor)*3-1,colData+6-i)),
	    'data_labels': {'value': False},
	    'gap':valgap,
	    'fill' : {'color': '%s'%(Style[i-1])},
	    })
    

	chart.set_title({
	'name': '#Bot sold exc. WinS YTD %s'%(Platform[-1]),
	'name_font': {
	    'name': 'Calibri',
		'size': 12,
		'color': 'black',
	},
	})

	chart.set_size({'width': 1400, 'height': 400})
	chart.set_x_axis({'num_font': {'size': 8, 'bold': False}})
	chart.set_legend({'font' : {'size' : 8}})
	chart.show_hidden_data()
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def DataForGraphQuality(Current_date,workbook,worksheet_data,Name_workhsheet_data,worksheet_graph,Name_workhsheet_graph,lineData,colData,lineSite,colSite):
	con = db.pool.connect()
	date_format = workbook.add_format({'num_format':'mmm-yy'})
	all_DataColiformEcoli = con.execute("""SELECT site,DATE_FORMAT(analysis_date, '%%Y-%%m'),escherichia,
								 		escherichia_bottle,total_coliform,
								 		total_coliform_bottle,aluminium,turbidity,manganese,iron
								 		FROM samples WHERE analysis_date >= %s ORDER BY site""",date(Current_date.year-1,1,1)).fetchall()
	
	DataSite = con.execute("""SELECT DISTINCT site FROM samples ORDER BY site""").fetchall()
	
	for i in range(len(DataSite)):
		DataColiformEcoli_site = list(filter(lambda row: row[0] == DataSite[i][0], all_DataColiformEcoli)) or [(0,"","","","","","","","","","","","")]
		worksheet_data.write(i+1,0,DataSite[i][0])
		start_date = date(Current_date.year-1,1,1)
		Column = 0
		while start_date <= Current_date:
			DataColiformEcoli = list(filter(lambda row: row[1] == "%s-%s"%(start_date.year,str(start_date.month).zfill(2)), DataColiformEcoli_site)) or [(0,"","","","","","","","","","","","")]
			worksheet_data.write(i+1,Column*6+1,QualityFailure(DataColiformEcoli[0][2],DataColiformEcoli[0][4]))
			worksheet_data.write(i+1,Column*6+2,QualityFailure(DataColiformEcoli[0][3],DataColiformEcoli[0][5]))
			worksheet_data.write(i+1,Column*6+3,isFloat(DataColiformEcoli[0][6]))
			worksheet_data.write(i+1,Column*6+4,isFloat(DataColiformEcoli[0][7]))
			worksheet_data.write(i+1,Column*6+5,isFloat(DataColiformEcoli[0][8]))
			worksheet_data.write(i+1,Column*6+6,isFloat(DataColiformEcoli[0][9]))
			worksheet_data.write(0,Column*6+1,start_date,date_format)
			start_date += relativedelta(months=+1)
			Column +=1
	
	worksheet_graph.data_validation('A1',{'validate' : 'list',
                                    'source' : "'%s'!A2:A%s"%(Name_workhsheet_data,len(DataSite)+2)})
	Select_format = workbook.add_format({'bg_color':'#FFFF00','bold':True,'font_size':15})
	worksheet_graph.write("A1",DataSite[10][0],Select_format)
	start_date = date(Current_date.year-1,1,1)
	Column = 0
	while start_date <= Current_date:
		worksheet_graph.write(lineData,colData+Column,start_date,date_format)
		worksheet_graph.write_formula(lineData+1,colData+Column,"=INDEX('%s'!%s:%s,MATCH(%s,'%s'!%s:%s,0))"%(Name_workhsheet_data,xl_rowcol_to_cell(1,Column*6+1),xl_rowcol_to_cell(len(DataSite)+1,Column*6+1),xl_rowcol_to_cell(lineSite,colSite),Name_workhsheet_data,xl_rowcol_to_cell(1,0),xl_rowcol_to_cell(len(DataSite)+1,0)))
		worksheet_graph.write_formula(lineData+2,colData+Column,"=INDEX('%s'!%s:%s,MATCH(%s,'%s'!%s:%s,0))"%(Name_workhsheet_data,xl_rowcol_to_cell(1,Column*6+2),xl_rowcol_to_cell(len(DataSite)+1,Column*6+2),xl_rowcol_to_cell(lineSite,colSite),Name_workhsheet_data,xl_rowcol_to_cell(1,0),xl_rowcol_to_cell(len(DataSite)+1,0)))
		worksheet_graph.write_formula(lineData+3,colData+Column,"=INDEX('%s'!%s:%s,MATCH(%s,'%s'!%s:%s,0))"%(Name_workhsheet_data,xl_rowcol_to_cell(1,Column*6+3),xl_rowcol_to_cell(len(DataSite)+1,Column*6+3),xl_rowcol_to_cell(lineSite,colSite),Name_workhsheet_data,xl_rowcol_to_cell(1,0),xl_rowcol_to_cell(len(DataSite)+1,0)))
		worksheet_graph.write_formula(lineData+4,colData+Column,"=INDEX('%s'!%s:%s,MATCH(%s,'%s'!%s:%s,0))"%(Name_workhsheet_data,xl_rowcol_to_cell(1,Column*6+4),xl_rowcol_to_cell(len(DataSite)+1,Column*6+4),xl_rowcol_to_cell(lineSite,colSite),Name_workhsheet_data,xl_rowcol_to_cell(1,0),xl_rowcol_to_cell(len(DataSite)+1,0)))
		worksheet_graph.write_formula(lineData+5,colData+Column,"=INDEX('%s'!%s:%s,MATCH(%s,'%s'!%s:%s,0))"%(Name_workhsheet_data,xl_rowcol_to_cell(1,Column*6+5),xl_rowcol_to_cell(len(DataSite)+1,Column*6+5),xl_rowcol_to_cell(lineSite,colSite),Name_workhsheet_data,xl_rowcol_to_cell(1,0),xl_rowcol_to_cell(len(DataSite)+1,0)))
		worksheet_graph.write_formula(lineData+6,colData+Column,"=INDEX('%s'!%s:%s,MATCH(%s,'%s'!%s:%s,0))"%(Name_workhsheet_data,xl_rowcol_to_cell(1,Column*6+6),xl_rowcol_to_cell(len(DataSite)+1,Column*6+6),xl_rowcol_to_cell(lineSite,colSite),Name_workhsheet_data,xl_rowcol_to_cell(1,0),xl_rowcol_to_cell(len(DataSite)+1,0)))
		start_date += relativedelta(months=+1)
		Column+=1

def GraphEcoliColiform(workbook,worksheet,Name_workhsheet_Graph,lineGraph,colGraph,lineData,colData,Current_date):
	chart = workbook.add_chart({'type' : 'column'})
	#Legend = ["%s LfL"%(Current_date.year),"%s Other"%(Current_date.year),"Objective LfL","Objective Other",str(Current_date.year-1)]
	#Style = ["#B9CDE5","#376092","#93CDDD","#215968","#4F81BD"]

	chart.add_series({
	    'name' :     "Treatment System",
	    'categories': '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData,colData),xl_rowcol_to_cell(lineData,colData+11+Current_date.month)),
	    'values':     '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData+1,colData),xl_rowcol_to_cell(lineData+1,colData+11+Current_date.month)),
	    'data_labels': {'value': False},
	    })
	
	chart.add_series({
	    'name' :     "Bottle",
	    'categories': '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData,colData),xl_rowcol_to_cell(lineData,colData+11+Current_date.month)),
	    'values':     '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData+2,colData),xl_rowcol_to_cell(lineData+2,colData+11+Current_date.month)),
	    'data_labels': {'value': False},
	    })
    

	chart.set_title({
	'name': 'Failures Ecoli/Coliform',
	'name_font': {
	    'name': 'Calibri',
		'size': 12,
		'color': 'black',
	},
	})

	chart.set_size({'width': 1400, 'height': 400})
	chart.set_x_axis({'num_font': {'size': 8, 'bold': False}})
	chart.set_legend({'font' : {'size' : 8}})
	chart.show_hidden_data()
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphAluTurb(workbook,worksheet,Name_workhsheet_Graph,lineGraph,colGraph,lineData,colData,Current_date):
	chart = workbook.add_chart({'type' : 'column'})
	#Legend = ["%s LfL"%(Current_date.year),"%s Other"%(Current_date.year),"Objective LfL","Objective Other",str(Current_date.year-1)]
	#Style = ["#B9CDE5","#376092","#93CDDD","#215968","#4F81BD"]

	chart.add_series({
	    'name' :     "Aluminium",
	    'categories': '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData,colData),xl_rowcol_to_cell(lineData,colData+11+Current_date.month)),
	    'values':     '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData+3,colData),xl_rowcol_to_cell(lineData+3,colData+11+Current_date.month)),
	    'data_labels': {'value': False},
	    })
	
	line_chart1 = workbook.add_chart({"type": "line"})

	line_chart1.add_series({
    	'name' :     "Turbidity",
	    'categories': '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData,colData),xl_rowcol_to_cell(lineData,colData+11+Current_date.month)),
	    'values':     '=\'%s\'!%s:%s'%(Name_workhsheet_Graph,xl_rowcol_to_cell(lineData+4,colData),xl_rowcol_to_cell(lineData+4,colData+11+Current_date.month)),
	    'data_labels': {'value': False},
		"y2_axis": True,
	    })

	chart.combine(line_chart1)
	chart.set_x_axis({"name": "Month"})
	chart.set_y_axis({"name": "Aluminium mg/L"})
	line_chart1.set_y2_axis({"name":"Turbidity mg/L"})

	chart.set_title({
	'name': 'Aluminium/Turbidity',
	'name_font': {
	    'name': 'Calibri',
		'size': 12,
		'color': 'black',
	},
	})

	chart.set_size({'width': 1400, 'height': 400})
	chart.set_x_axis({'num_font': {'size': 8, 'bold': False}})
	chart.set_legend({'font' : {'size' : 8}})
	chart.show_hidden_data()
	worksheet.insert_chart('%s'%(xl_rowcol_to_cell(lineGraph,colGraph)),chart)

def GraphTestResults(workbook,worksheet,Name_worksheet,lineGraph,colGraph,lineData,colData,Current_date,Test,NamePlatform = True):
	con = db.pool.connect()

	if Test == "First":
		TestResults = con.execute("""
												SELECT 
													DISTINCT s1.site, s1.contamination_level_machine, s1.contamination_level_bottle
												FROM samples s1
												INNER JOIN Sites ON site = Id_Site
												INNER JOIN (
													SELECT DISTINCT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'Monthly Test')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
												WHERE (Platform = %s OR True = %s) AND type = "Monthly Test"
												ORDER BY site,s1.contamination_level_machine, s1.contamination_level_bottle
											""", (date(Current_date.year, Current_date.month, 1), 
				 								date(Current_date.year, Current_date.month, 1)+relativedelta(months=+1),
												NamePlatform,NamePlatform)).fetchall()
		print(TestResults)
	elif Test == "Second":
		TestResults = con.execute("""
												SELECT 
													s1.site, s1.contamination_level_machine, s1.contamination_level_bottle
												FROM samples s1
												INNER JOIN Sites ON site = Id_Site
												INNER JOIN (
													SELECT site, MAX(sample_date) AS max_sample_date
													FROM samples
													WHERE sample_date >= %s AND sample_date < %s
													AND (type = 'WQ Alert' OR type = 'Monthly Test')
													GROUP BY site
												) s2 ON s1.site = s2.site AND s1.sample_date = s2.max_sample_date
												WHERE (Platform = %s OR True = %s ) AND (type = 'WQ Alert' OR type = 'Monthly Test')
											""", (date(Current_date.year, Current_date.month, 1), 
				 								date(Current_date.year, Current_date.month, 1)+relativedelta(months=+1),
												NamePlatform,NamePlatform)).fetchall()
		
		
	NameContamination = ['level 0','level 1 - machine','level 1 - bottle ','level 2 - machine',
						'level 2 - bottle ','level 3 - machine','level 3 - bottle ']
	ListContamination = [0,0,0,0,0,0,0] 
	for i in range(len(TestResults)):
		if TestResults[i][1] == 3:
			ListContamination[5] += 1
		elif TestResults[i][2] == 3: 
			ListContamination[6] += 1
		elif TestResults[i][1] == 2: 
			ListContamination[3] += 1
		elif TestResults[i][2] == 2:
			ListContamination[4] += 1
		elif TestResults[i][1] == 1:
			ListContamination[1] += 1
		elif TestResults[i][2] == 1:
			ListContamination[2] += 1
		else:
			ListContamination[0] += 1
	
	for i in range(len(NameContamination)):
		worksheet.write(lineData+i,colData,NameContamination[i])
		worksheet.write(lineData+i,colData+1,ListContamination[i])

	# Create a pie chart
	chart_pie = workbook.add_chart({'type': 'pie'})

	# Configure the series of the pie chart
	chart_pie.add_series({
		'name': 'Contamination Levels',
		'categories': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineData, colData), xl_rowcol_to_cell(lineData+len(NameContamination)-1, colData)),
		'values': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineData, colData+1), xl_rowcol_to_cell(lineData+len(NameContamination)-1, colData+1)),
		'data_labels': {'percentage': True},
	})

	# Set the title of the pie chart
	if NamePlatform == True:
		if Test == "First":
			chart_pie.set_title({'name': 'Monthly Test'})
		elif Test == "Second":
			chart_pie.set_title({'name': 'After technicians intervention'})
	else:
		if Test == "First":
			chart_pie.set_title({'name': 'Monthly Test - %s'%(NamePlatform)})
		elif Test == "Second":
			chart_pie.set_title({'name': 'After tech int - %s'%(NamePlatform)})

	# Set the size of the pie chart
	chart_pie.set_size({'width': 340, 'height': 250})

	# Insert the pie chart into the worksheet
	worksheet.insert_chart(xl_rowcol_to_cell(lineGraph, colGraph), chart_pie)

def GraphWaterSource(workbook,worksheet,Name_worksheet,lineGraph,colGraph,sizelineGraph,sizecolGraph,Current_date):
	con = db.pool.connect()
	
	Water_source = con.execute("""SELECT site,MAX(date_form),main_source_of_water FROM assessments WHERE date_form<=%s GROUP BY site""",(Current_date)).fetchall()
	water_source_dict = {'ទឹកក្រោមដី/Ground water':0,'ទឹករដ្ឋាករ/Piped water':0,'ទឹកលើដី/Surface water':0,'Others':0}
	
	for i in range(len(Water_source)):
		for idx, key in enumerate(water_source_dict.keys()):
			if Water_source[i][2] == key:
				water_source_dict[key] += 1
				break
			if idx == len(water_source_dict.keys())-1:
				water_source_dict['Others'] += 1

	for idx, key in enumerate(water_source_dict.keys()):
		worksheet.write(lineGraph+sizelineGraph+idx,colGraph,key)
		worksheet.write(lineGraph+sizelineGraph+idx,colGraph+1,water_source_dict[key])
	
	# Create a pie chart
	chart_pie = workbook.add_chart({'type': 'pie'})
	# Configure the series of the pie chart
	chart_pie.add_series({
		'name': 'Water Sources',
		'categories': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph, colGraph), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(water_source_dict)-1, colGraph)),
		'values': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph, colGraph+1), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(water_source_dict)-1, colGraph+1)),
		'data_labels': {'percentage': True},
	})

	# Set the title of the pie chart
	chart_pie.set_title({
		'name': 'Water Sources',
		'name_font': {
			'name': 'Calibri',
			'size': 10,
			'bold': True,
		}
	})

	# Set the size of the pie chart based on row height and column width
	chart_pie.set_size({'width': sizecolGraph * 145, 'height': sizelineGraph * 20})  # Adjust the multipliers as needed

	# Insert the pie chart into the worksheet
	worksheet.insert_chart(xl_rowcol_to_cell(lineGraph, colGraph), chart_pie)

def GraphElectricitySource(workbook,worksheet,Name_worksheet,lineGraph,colGraph,sizelineGraph,sizecolGraph,Current_date):
	con = db.pool.connect()

	Electricity_source = con.execute("""SELECT site,MAX(date_form),main_source_of_electricity FROM assessments WHERE date_form<=%s GROUP BY site""",(Current_date)).fetchall()
	electricity_source_dict = {'both_sola_and_grid':0,'grid':0,'solar':0,'Others':0}
	
	for i in range(len(Electricity_source)):
		for idx, key in enumerate(electricity_source_dict.keys()):
			if Electricity_source[i][2] == key:
				electricity_source_dict[key] += 1
				break
			if idx == len(electricity_source_dict.keys())-1:
				electricity_source_dict['Others'] += 1

	for idx, key in enumerate(electricity_source_dict.keys()):
		worksheet.write(lineGraph+sizelineGraph+idx,colGraph,key)
		worksheet.write(lineGraph+sizelineGraph+idx,colGraph+1,electricity_source_dict[key])
	
	# Create a pie chart
	chart_pie = workbook.add_chart({'type': 'pie'})
	# Configure the series of the pie chart
	chart_pie.add_series({
		'name': 'Electricity Sources',
		'categories': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph, colGraph), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(electricity_source_dict)-1, colGraph)),
		'values': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph, colGraph+1), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(electricity_source_dict)-1, colGraph+1)),
		'data_labels': {'percentage': True},
	})

	chart_pie.set_title({
		'name': 'Electricity Sources',
		'name_font': {
			'name': 'Calibri',
			'size': 10,
			'bold': True,
		}
	})

	# Set the size of the pie chart based on row height and column width
	chart_pie.set_size({'width': sizecolGraph * 145, 'height': sizelineGraph * 20})  # Adjust the multipliers as needed

	# Insert the pie chart into the worksheet
	worksheet.insert_chart(xl_rowcol_to_cell(lineGraph, colGraph), chart_pie)

def GraphPump(workbook,worksheet,Name_worksheet,lineGraph,colGraph,sizelineGraph,sizecolGraph,Current_date):
	con = db.pool.connect()

	Electricity_source = con.execute("""SELECT site,MAX(date_form),main_source_of_electricity,micro_filter_pump FROM assessments WHERE date_form<=%s GROUP BY site""",(Current_date)).fetchall()
	electricity_source_dict = {'both_sola_and_grid':[['ម៉ូទ័រ AC/AC pump',0],['ម៉ូទ័រ DC/DC pump',0],['ទេ/No',0]],
							'grid':[['ម៉ូទ័រ AC/AC pump',0],['ម៉ូទ័រ DC/DC pump',0],['ទេ/No',0]],
							'solar':[['ម៉ូទ័រ AC/AC pump',0],['ម៉ូទ័រ DC/DC pump',0],['ទេ/No',0]]}
	
	for i in range(len(Electricity_source)):
		for idx, key in enumerate(electricity_source_dict.keys()):
			if Electricity_source[i][2] == key:
				for j in range(len(electricity_source_dict[key])):
					if Electricity_source[i][3] == electricity_source_dict[key][j][0]:
						electricity_source_dict[key][j][1] += 1
						break
				break
	
	for idx, key in enumerate(electricity_source_dict.keys()):
		worksheet.write(lineGraph+sizelineGraph+idx+1,colGraph,key)
		for j in range(len(electricity_source_dict[key])):
			worksheet.write(lineGraph+sizelineGraph,colGraph+j+1,electricity_source_dict[key][j][0])
			worksheet.write(lineGraph+sizelineGraph+idx+1,colGraph+j+1,electricity_source_dict[key][j][1])
	
	#Create a stacked column chart
	chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
	# Configure the series of the stacked column chart
	for j in range(len(electricity_source_dict['both_sola_and_grid'])):
		chart.add_series({
			'name': electricity_source_dict['both_sola_and_grid'][j][0],
			'categories': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph+1, colGraph), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(electricity_source_dict), colGraph)),
			'values': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph+1, colGraph+j+1), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(electricity_source_dict), colGraph+j+1)),
			'data_labels': {'value': False},
		})
	chart.set_x_axis({'num_font': {'size': 8}})  # Reduce the font size of the categories in the x-axis

	# Set the title of the stacked column chart
	chart.set_title({
		'name': 'Pump Types by Electricity Source',
		'name_font': {
			'name': 'Calibri',
			'size': 10,
			'bold': True,
		}
	})

	# Set the size of the stacked column chart based on row height and column width
	chart.set_size({'width': sizecolGraph * 145, 'height': sizelineGraph * 20})  # Adjust the multipliers as needed

	# Insert the stacked column chart into the worksheet
	worksheet.insert_chart(xl_rowcol_to_cell(lineGraph, colGraph), chart)

def UvLampPerYearGraph(workbook,worksheet,Name_worksheet,lineGraph,colGraph,sizelineGraph,sizecolGraph,Current_date):
	con = db.pool.connect()
	
	YearOfActivity = con.execute("""SELECT DISTINCT YEAR(Month) FROM Sales ORDER BY Month""").fetchall()
	Uv_Lamp = con.execute("""SELECT site,MAX(date_form),uv_lamp,YEAR(Min(Month)) FROM assessments Join Sales ON Id_Site = site 
							WHERE date_form<=%s GROUP BY site""",(Current_date)).fetchall()
	
	uv_lamp_per_year_dict = {YearOfActivity[i][0]: [["COMAP", 0], ["VIQUA", 0], ["Aguatapone", 0], ["ម៉ាកផ្សេង/Other brand", 0]] for i in range(len(YearOfActivity))}

	
	for i in range(len(Uv_Lamp)):
		for idx, key in enumerate(uv_lamp_per_year_dict.keys()):
			if Uv_Lamp[i][3] == key:
				for j in range(len(uv_lamp_per_year_dict[key])):
					if Uv_Lamp[i][2] == uv_lamp_per_year_dict[key][j][0]:
						uv_lamp_per_year_dict[key][j][1] += 1
						break
				break
	
	for idx, key in enumerate(uv_lamp_per_year_dict.keys()):
		worksheet.write(lineGraph+sizelineGraph+idx+1,colGraph,key)
		for j in range(len(uv_lamp_per_year_dict[key])):
			worksheet.write(lineGraph+sizelineGraph,colGraph+j+1,uv_lamp_per_year_dict[key][j][0])
			worksheet.write(lineGraph+sizelineGraph+idx+1,colGraph+j+1,uv_lamp_per_year_dict[key][j][1])
	
	#Create a stacked column chart
	chart = workbook.add_chart({'type': 'column', 'subtype': 'stacked'})
	# Configure the series of the stacked column chart
	for j in range(len(uv_lamp_per_year_dict[YearOfActivity[0][0]])):
		chart.add_series({
			'name': uv_lamp_per_year_dict[YearOfActivity[0][0]][j][0],
			'categories': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph+1, colGraph), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(uv_lamp_per_year_dict), colGraph)),
			'values': "='%s'!%s:%s" % (Name_worksheet, xl_rowcol_to_cell(lineGraph+sizelineGraph+1, colGraph+j+1), xl_rowcol_to_cell(lineGraph+sizelineGraph+len(uv_lamp_per_year_dict), colGraph+j+1)),
			'data_labels': {'value': False},
		})
	chart.set_x_axis({'num_font': {'size': 8}})  # Reduce the font size of the categories in the x-axis

	# Set the title of the stacked column chart
	chart.set_title({
		'name': 'UV Lamp Brands by Year of Installation',
		'name_font': {
			'name': 'Calibri',
			'size': 10,
			'bold': True,
		}
	})

	# Set the size of the stacked column chart based on row height and column width
	chart.set_size({'width': sizecolGraph * 400, 'height': sizelineGraph * 20})  # Adjust the multipliers as needed

	# Insert the stacked column chart into the worksheet
	worksheet.insert_chart(xl_rowcol_to_cell(lineGraph, colGraph), chart)	
				

	