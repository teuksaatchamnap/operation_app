import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta
from calendar import monthrange
import calendar
from monthlyreport.Functionutils import CalculTier, Numberdaysopeningyear, CalculNombreMoisOuverture, listAdvisorPerPlatform
import db
import tempfile



def CreatefileAdvisor(ListSiteActive,ListPlatform):
    global workbook, worksheet_bonus, worksheet_data_1_semester,worksheet_data_2_semester,worksheet_data_analyse_customer,worksheet_analyse,worksheet_data_analyse_wins,worksheet_data_analyse_total
    Year = str(Current_date.year)
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    filepath = tempfile.gettempdir()+'/Advisor '+Year+'-'+Month+'.xlsx'
    workbook = xlsxwriter.Workbook(filepath)

    bold_title = workbook.add_format({'border':1,'bold':True})

    Title_format = workbook.add_format({'bold' : True, 'center_across' : True, 'bg_color' : '#DCE6F1'})

    if Current_date < date(int(Year),7,1):
        ListAdvisor1stSemester = listAdvisorPerPlatform(Current_date)
        worksheet_bonus = workbook.add_worksheet("Bonus")
        worksheet_bonus.set_column('A:A', len('chansarey_lorm'))
        worksheet_bonus.set_column('B:C', len('Sales ($) 1st semester 20'))
        worksheet_bonus.set_column('D:E', len('Assigned site'))
        worksheet_bonus.set_column('G:G', len('% of ref salary'))
        worksheet_bonus.write('B1', "Sales ($) 1st semester %s"%str(Year),bold_title)
        worksheet_bonus.write('C1', "Sales ($) 1st semester %s"%str(int(Year)-1),bold_title)
        worksheet_bonus.write('D1', "%% %s/%s"%(str(Year),str(int(Year)-1)),bold_title)
        worksheet_bonus.write('E1', "Assigned site",bold_title)
        worksheet_bonus.write("G1", "% of salary",bold_title)
        worksheet_bonus.write("H1", "Bonus",bold_title)
    elif Current_date >= date(int(Year),7,1):
        ListAdvisor1stSemester = listAdvisorPerPlatform(date(int(Year),6,1))
        ListAdvisor2ndSemester = listAdvisorPerPlatform(Current_date)
        print(ListAdvisor2ndSemester)
        decal = len(ListPlatform)+len(ListAdvisor2ndSemester) +2
        worksheet_bonus = workbook.add_worksheet("Bonus")
        worksheet_bonus.set_column('A:A', len('chansarey_lorm'))
        worksheet_bonus.set_column('B:C', len('Sales ($) 1st semester 20'))
        worksheet_bonus.set_column('D:E', len('Assigned site'))
        worksheet_bonus.set_column('G:G', len('% of ref salary'))
        worksheet_bonus.write('B1', "Sales ($) 2nd semester %s"%str(Year),bold_title)
        worksheet_bonus.write('C1', "Sales ($) 2nd semester %s"%str(int(Year)-1),bold_title)
        worksheet_bonus.write('D1', "%% %s/%s"%(str(Year),str(int(Year)-1)),bold_title)
        worksheet_bonus.write('E1', "Assigned site",bold_title)
        worksheet_bonus.write("G1", "% of salary",bold_title)
        worksheet_bonus.write("H1", "Bonus",bold_title)

        worksheet_bonus.write('B%s'%(decal+4), "Sales ($) 1st semester %s"%str(Year),bold_title)
        worksheet_bonus.write('C%s'%(decal+4), "Sales ($) 1st semester %s"%str(int(Year)-1),bold_title)
        worksheet_bonus.write('D%s'%(decal+4), "%% %s/%s"%(str(Year),str(int(Year)-1)),bold_title)
        worksheet_bonus.write('E%s'%(decal+4), "Assigned site",bold_title)
        worksheet_bonus.write("G%s"%(decal+4), "% of salary",bold_title)
        worksheet_bonus.write("H%s"%(decal+4), "Bonus",bold_title)



    worksheet_data_1_semester = workbook.add_worksheet("Sales ($) 1st semester")
    worksheet_data_1_semester.autofilter(0,0,len(ListSiteActive),15)

    worksheet_data_1_semester.write(0,0,"Site",Title_format)
    worksheet_data_1_semester.write(0,1,"Advisor",Title_format)
    worksheet_data_1_semester.write(0,2,"Platform",Title_format)

    worksheet_data_1_semester.set_column('D:I',len('Janvier 2021'))
    worksheet_data_1_semester.set_column('K:P',len('Janvier 2021'))
    worksheet_data_1_semester.write(0,3,"January %s"%(Year),bold_title)
    worksheet_data_1_semester.write(0,4,"February %s"%(Year),bold_title)
    worksheet_data_1_semester.write(0,5,"Mars %s"%(Year),bold_title)
    worksheet_data_1_semester.write(0,6,"April %s"%(Year),bold_title)
    worksheet_data_1_semester.write(0,7,"May %s"%(Year),bold_title)
    worksheet_data_1_semester.write(0,8,"June %s"%(Year),bold_title)

    worksheet_data_1_semester.write(0,10,"January %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_1_semester.write(0,11,"February %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_1_semester.write(0,12,"Mars %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_1_semester.write(0,13,"April %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_1_semester.write(0,14,"May %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_1_semester.write(0,15,"June %s"%(str(int(Year)-1)),bold_title)

    worksheet_data_2_semester = workbook.add_worksheet("Sales ($) 2nd semester")
    worksheet_data_2_semester.autofilter(0,0,len(ListSiteActive),15)
    worksheet_data_2_semester.write(0,0,"Site",Title_format)
    worksheet_data_2_semester.write(0,1,"Advisor",Title_format)
    worksheet_data_2_semester.write(0,2,"Platform",Title_format)

    # worksheet_data_2_semester.add_table(0,0,len(ListSiteActive),2, {'name' : 'Datasecondsemester',
    #                                                                             'columns' : [{'header' : 'Site'},
    #                                                                             {'header' : 'Advisor'},
    #                                                                             {'header' : 'Platform'}]})
    worksheet_data_2_semester.set_column('D:I',len('Décembre 2021'))
    worksheet_data_2_semester.set_column('K:P',len('Décembre 2021'))
    worksheet_data_2_semester.write(0,3,"July %s"%(Year),bold_title)
    worksheet_data_2_semester.write(0,4,"August %s"%(Year),bold_title)
    worksheet_data_2_semester.write(0,5,"September %s"%(Year),bold_title)
    worksheet_data_2_semester.write(0,6,"October %s"%(Year),bold_title)
    worksheet_data_2_semester.write(0,7,"November %s"%(Year),bold_title)
    worksheet_data_2_semester.write(0,8,"December %s"%(Year),bold_title)

    worksheet_data_2_semester.write(0,10,"July %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_2_semester.write(0,11,"August %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_2_semester.write(0,12,"September %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_2_semester.write(0,13,"October %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_2_semester.write(0,14,"November %s"%(str(int(Year)-1)),bold_title)
    worksheet_data_2_semester.write(0,15,"December %s"%(str(int(Year)-1)),bold_title)

def WriteBonus(ListSiteActive,ListTierThisYear, exchange_rate,ListPlatform, Year):
    con = db.pool.connect()
    grey_format = workbook.add_format({'bg_color' : "#C0C0C0",'top':2,'bottom':2})
    green_format = workbook.add_format({'bg_color' : "#C6EFCE"})
    Sales_format = workbook.add_format({'num_format' : '# ### ##0', 'border' : 1})
    Percentage_format = workbook.add_format({'num_format' : '0%', 'border' : 1})
    Title_format = workbook.add_format({'bold' : True, 'bg_color' : '#DCE6F1'})
    queryL = con.execute("SELECT Platform, Code_Province, Advisor_first_semester, Advisor_second_semester, Id_Site FROM Sites")
    grey_case_format =  workbook.add_format({'bg_color' : "#C0C0C0",'border':1})
    allL = queryL.fetchall()

    if Current_date < date(Year,7,1):
        start_date = date(Year,1,1)
        start_date_last_year = date(Year-1,1,1)
        date_mid = Current_date + timedelta(monthrange(Current_date.year,Current_date.month)[1])
        date_mid_last_year = Date_N_1 + timedelta(monthrange(Date_N_1.year,Date_N_1.month)[1])

        Opened_month = CalculNombreMoisOuverture(start_date,start_date_last_year,ListSiteActive)
        ListOpenDayThisYear = Numberdaysopeningyear(start_date,start_date_last_year,ListSiteActive,Opened_month)
        ListTierBeginningYear = CalculTier(start_date,start_date_last_year,Opened_month,ListSiteActive,ListOpenDayThisYear)
    else:
        date_end = Current_date
        date_end_last_year = Date_N_1
        date_mid = date(Year,7,1)
        date_mid_last_year = date(Year-1,7,1)
        start_date = date(Year,1,1)
        start_date_last_year = date(Year-1,1,1)

        Opened_month = CalculNombreMoisOuverture(start_date,start_date_last_year,ListSiteActive)
        ListOpenDayThisYear = Numberdaysopeningyear(start_date,start_date_last_year,ListSiteActive,Opened_month)
        ListTierBeginningYear = CalculTier(start_date,start_date,Opened_month,ListSiteActive,ListOpenDayThisYear)

        Opened_month = CalculNombreMoisOuverture(date_mid,date_mid_last_year,ListSiteActive)
        ListOpenDayThisYear = Numberdaysopeningyear(date_mid,date_mid_last_year,ListSiteActive,Opened_month)
        ListTierEndYear = CalculTier(date_mid,date_mid_last_year,Opened_month,ListSiteActive,ListOpenDayThisYear)

    for k in range(len(ListSiteActive)):
        L = list(filter(lambda row: row[4] == ListSiteActive[k][0], allL))
        worksheet_data_1_semester.write(k+1,0,ListSiteActive[k][0],Title_format)
        worksheet_data_1_semester.write(k+1,1,L[0][2],Title_format)
        worksheet_data_1_semester.write(k+1,2,L[0][0],Title_format)

        if Current_date < date(Year,7,1):
            start_date = date(Year,1,1)
            start_date_last_year = date(Year-1,1,1)
            date_mid = Current_date + timedelta(monthrange(Current_date.year,Current_date.month)[1])
            date_mid_last_year = Date_N_1 + timedelta(monthrange(Date_N_1.year,Date_N_1.month)[1])

        else:
            date_end = Current_date
            date_end_last_year = Date_N_1
            date_mid = date(Year,7,1)
            date_mid_last_year = date(Year-1,7,1)
            start_date = date(Year,1,1)
            start_date_last_year = date(Year-1,1,1)


        query = con.execute("SELECT Total_Income, DATE_FORMAT(Month, '%%Y-%%m-%%d') FROM Sales WHERE Id_Site = %s", (ListSiteActive[k][0]))
        allSale = query.fetchall()

        i=0
        if Current_date < date(Year,7,1):
            ListAdvisor1stSemester = listAdvisorPerPlatform(Current_date)
            while start_date < date_mid:
                Sale = list(filter(lambda row: row[1] == str(start_date), allSale))
                Sale_l_year = list(filter(lambda row: row[1] == str(start_date_last_year), allSale))
                if Sale and Sale[0][0]:
                    worksheet_data_1_semester.write(k+1,i+3,Sale[0][0]/exchange_rate,Sales_format)
                else:
                    worksheet_data_1_semester.write(k+1,i+3,None,grey_case_format)
                if Sale_l_year and Sale_l_year[0][0]:
                    worksheet_data_1_semester.write(k+1,i+10,Sale_l_year[0][0]/exchange_rate,Sales_format)
                elif ListTierBeginningYear[k]=="New" and Sale and Sale[0][0]:
                    worksheet_data_1_semester.write(k+1,i+10,Sale[0][0]/(1.2*exchange_rate),Sales_format)
                else:
                    worksheet_data_1_semester.write(k+1,i+10,None,grey_case_format)

                start_date += timedelta(monthrange(start_date.year,start_date.month)[1])
                start_date_last_year += timedelta(monthrange(start_date_last_year.year,start_date_last_year.month)[1])
                i+=1
            i=0
            total_row = 0
            for n in range(len(ListPlatform)):
                worksheet_bonus.write(2+total_row,0,ListPlatform[n],grey_format)
                for l in range(1,8):
                    worksheet_bonus.write(2+total_row,l,None,grey_format)
                for j in range(len(ListAdvisor1stSemester)):
                    if ListAdvisor1stSemester[j][0] == ListPlatform[n]:
                        worksheet_bonus.write(3+total_row,0,ListAdvisor1stSemester[j][1],Sales_format)
                        worksheet_bonus.write(3+total_row,4,ListAdvisor1stSemester[j][2],Sales_format)
                        worksheet_bonus.write_formula(3+total_row,1,"=SUMPRODUCT(SUMIF('Sales ($) 1st semester'!B2:B%s,Bonus!A%s,OFFSET('Sales ($) 1st semester'!D2:D%s,,{0;1;2;3;4;5})))"%(len(ListSiteActive)+1,4+total_row,len(ListSiteActive)+1),Sales_format)
                        worksheet_bonus.write_formula(3+total_row,2,"=SUMPRODUCT(SUMIF('Sales ($) 1st semester'!B2:B%s,Bonus!A%s,OFFSET('Sales ($) 1st semester'!K2:K%s,,{0;1;2;3;4;5})))"%(len(ListSiteActive)+1,4+total_row,len(ListSiteActive)+1),Sales_format)
                        worksheet_bonus.write_formula(3+total_row,3,"=B%s/C%s"%(4+total_row,4+total_row),Percentage_format)
                        worksheet_bonus.write_formula(3+total_row,6,"=IF(D%s<1,0,(MIN(D%s,120%%)-1)/0.2)"%(4+total_row,4+total_row),Percentage_format)
                        worksheet_bonus.write_formula(3+total_row,7,"G%s*400"%(4+total_row),Sales_format)
                        total_row+=1
                total_row+=1
            total_row_max = total_row


        elif Current_date >= date(Year,7,1):
            ListAdvisor1stSemester = listAdvisorPerPlatform(date(Year,6,1))
            ListAdvisor2ndSemester = listAdvisorPerPlatform(Current_date)
            print(ListAdvisor2ndSemester)
            while start_date < date_mid:
                Sale = list(filter(lambda row: row[1] == str(start_date), allSale))
                Sale_l_year = list(filter(lambda row: row[1] == str(start_date_last_year), allSale))
                if Sale and Sale[0][0]:
                    worksheet_data_1_semester.write(k+1,i+3,Sale[0][0]/exchange_rate,Sales_format)
                else:
                    worksheet_data_1_semester.write(k+1,i+3,None,grey_case_format)
                if Sale_l_year and Sale_l_year[0][0]:
                    worksheet_data_1_semester.write(k+1,i+10,Sale_l_year[0][0]/exchange_rate,Sales_format)
                elif ListTierBeginningYear[k]=="New" and Sale and Sale[0][0]:
                    worksheet_data_1_semester.write(k+1,i+10,Sale[0][0]/(1.2*exchange_rate),Sales_format)
                else:
                    worksheet_data_1_semester.write(k+1,i+10,None,grey_case_format)

                start_date += timedelta(monthrange(start_date.year,start_date.month)[1])
                start_date_last_year += timedelta(monthrange(start_date_last_year.year,start_date_last_year.month)[1])
                i+=1
            i=0
            worksheet_data_2_semester.write(k+1,0,ListSiteActive[k][0],Title_format)
            worksheet_data_2_semester.write(k+1,1,L[0][3],Title_format)
            worksheet_data_2_semester.write(k+1,2,L[0][0],Title_format)
            while date_mid <= date_end:
                Sale = list(filter(lambda row: row[1] == str(date_mid), allSale))
                Sale_l_year = list(filter(lambda row: row[1] == str(date_mid_last_year), allSale))
                if Sale and Sale[0][0]:
                    worksheet_data_2_semester.write(k+1,i+3,Sale[0][0]/exchange_rate,Sales_format)
                else:
                    worksheet_data_2_semester.write(k+1,i+3,None,grey_case_format)
                if Sale_l_year and Sale_l_year[0][0]:
                    worksheet_data_2_semester.write(k+1,i+10,Sale_l_year[0][0]/exchange_rate,Sales_format)
                elif ListTierEndYear[k]=="New" and Sale and Sale[0][0]:
                    worksheet_data_2_semester.write(k+1,i+10,Sale[0][0]/(1.2*exchange_rate),Sales_format)
                else:
                    worksheet_data_2_semester.write(k+1,i+10,None,grey_case_format)

                date_mid += timedelta(monthrange(date_mid.year,date_mid.month)[1])
                date_mid_last_year += timedelta(monthrange(date_mid_last_year.year,date_mid_last_year.month)[1])
                i+=1

            total_row = 0
            decal = len(ListPlatform)+len(ListAdvisor2ndSemester) +2 

            #print(ListAdvisor1stSemester)
            for n in range(len(ListPlatform)):
                worksheet_bonus.write(2+total_row,0,ListPlatform[n],grey_format)
                worksheet_bonus.write(2+total_row+decal+2,0,ListPlatform[n],grey_format)
                for l in range(1,8):
                    worksheet_bonus.write(2+total_row,l,None,grey_format)
                    worksheet_bonus.write(2+total_row+decal+2,l,None,grey_format)
                total_row_n = total_row
                for j in range(len(ListAdvisor2ndSemester)):
                    if ListAdvisor2ndSemester[j][0] == ListPlatform[n]:
                        #print(ListAdvisor2ndSemester[j][1],ListPlatform[n])
                        worksheet_bonus.write(3+total_row,0,ListAdvisor2ndSemester[j][1],Sales_format)
                        worksheet_bonus.write(3+total_row,4,ListAdvisor2ndSemester[j][2],Sales_format)
                        worksheet_bonus.write_formula(3+total_row,1,"=SUMPRODUCT(SUMIF('Sales ($) 2nd semester'!B2:B%s,Bonus!A%s,OFFSET('Sales ($) 2nd semester'!D2:D%s,,{0;1;2;3;4;5})))"%(len(ListSiteActive)+1,4+total_row,len(ListSiteActive)+1),Sales_format)
                        worksheet_bonus.write_formula(3+total_row,2,"=SUMPRODUCT(SUMIF('Sales ($) 2nd semester'!B2:B%s,Bonus!A%s,OFFSET('Sales ($) 2nd semester'!K2:K%s,,{0;1;2;3;4;5})))"%(len(ListSiteActive)+1,4+total_row,len(ListSiteActive)+1),Sales_format)
                        worksheet_bonus.write_formula(3+total_row,3,"=B%s/C%s"%(4+total_row,4+total_row),Percentage_format)
                        worksheet_bonus.write_formula(3+total_row,6,"=IF(D%s<1,0,(MIN(D%s,120%%)-1)/0.2)"%(4+total_row,4+total_row),Percentage_format)
                        worksheet_bonus.write_formula(3+total_row,7,"G%s*400"%(4+total_row),Sales_format)
                        total_row+=1
                total_row = total_row_n
                for m in range(len(ListAdvisor1stSemester)):
                    if ListAdvisor1stSemester[m][0] == ListPlatform[n]:
                        worksheet_bonus.write(3+total_row+decal+2,0,ListAdvisor1stSemester[m][1],Sales_format)
                        worksheet_bonus.write(3+total_row+decal+2,4,ListAdvisor1stSemester[m][2],Sales_format)
                        worksheet_bonus.write_formula(3+total_row+decal+2,1,"=SUMPRODUCT(SUMIF('Sales ($) 1st semester'!B2:B%s,Bonus!A%s,OFFSET('Sales ($) 1st semester'!D2:D%s,,{0;1;2;3;4;5})))"%(len(ListSiteActive)+1,4+total_row+decal+2,len(ListSiteActive)+1),Sales_format)
                        worksheet_bonus.write_formula(3+total_row+decal+2,2,"=SUMPRODUCT(SUMIF('Sales ($) 1st semester'!B2:B%s,Bonus!A%s,OFFSET('Sales ($) 1st semester'!K2:K%s,,{0;1;2;3;4;5})))"%(len(ListSiteActive)+1,4+total_row+decal+2,len(ListSiteActive)+1),Sales_format)
                        worksheet_bonus.write_formula(3+total_row+decal+2,3,"=B%s/C%s"%(4+total_row+decal+2,4+total_row+decal+2),Percentage_format)
                        worksheet_bonus.write_formula(3+total_row+decal+2,6,"=IF(D%s<1,0,(MIN(D%s,120%%)-1)/0.2)"%(4+total_row+decal+2,4+total_row+decal+2),Percentage_format)
                        worksheet_bonus.write_formula(3+total_row+decal+2,7,"G%s*400"%(4+total_row+decal+2),Sales_format)
                        total_row+=1
                total_row+=1
            total_row_max =total_row + decal +2
            worksheet_bonus.conditional_format('H%s:H%s'%(total_row+6,total_row+4+decal),{"type" : "formula", "criteria" : "H%s>0"%(total_row+6), "format" : green_format})
            worksheet_bonus.conditional_format('D%s:D%s'%(total_row+6,total_row+4+decal),{"type" : "formula", "criteria" : "D%s>=100%%"%(total_row+6), "format" : green_format})
    worksheet_bonus.conditional_format('H4:H%s'%(total_row+2),{"type" : "formula", "criteria" : "G4>0", "format" : green_format})
    worksheet_bonus.conditional_format('D4:D%s'%(total_row+2),{"type" : "formula", "criteria" : "D4>=100%", "format" : green_format})

def WriteAnalyseCroissance(ListSiteActive,ListPlatform):
    con = db.pool.connect()
    Number_grey_format_right = workbook.add_format({"num_format": '# ##0','bg_color' : "#FDE9D9",'border':1,'right' : 2})
    Number_grey_format = workbook.add_format({"num_format": '# ##0','bg_color' : "#FDE9D9",'border':1})
    Number_format_right = workbook.add_format({"num_format": '# ##0','border':1,'bg_color' : "#DCE6F1",'right' : 2})
    Number_format = workbook.add_format({"num_format": '# ##0','border':1,'bg_color' : "#DCE6F1"})
    Title_format_white = workbook.add_format({"num_format": '# ##0','bottom':1,'left':1,'right':1,'bold' : True,'center_across' : True,"font_color":'#FFFFFF'})
    Title_format = workbook.add_format({"num_format": '###0','top':1,'left':1,'right':1,'bold' : True,'center_across' : True,'bg_color':'#F2F2F2'})
    Empty_format_right = workbook.add_format({'bg_color' : '#C0C0C0','border' : 1,'right' : 2})
    Empty_format = workbook.add_format({'bg_color' : '#C0C0C0','border' : 1})
    Title_format_Jugs = workbook.add_format({"bold" : True,'bg_color' : '#FFFF00'})
    Bold_format = workbook.add_format({"bold" : True, "num_format" : '# ##0'})
    Percentage_format = workbook.add_format({"num_format" : '0.0%','border' : 1,'bold' : True})
    query = con.execute("SELECT (Total_Sales-WiS_Sales-Bottle_Sales),WiS_Sales,DATE_FORMAT(Month, '%%Y-%%m-%%d'),Id_Site FROM Sales WHERE Month <= %s AND Month >= %s",(Current_date,date(Date_N_2.year,1,1)))
    allSales = query.fetchall()
    query = con.execute("SELECT Platform,Advisor,Id_Site FROM Sites")
    allSite_Info = query.fetchall()
    worksheet_data_analyse_customer.write(0,0,"IN JUGS",Title_format_Jugs)
    worksheet_data_analyse_customer.set_column('C:C',len('leanghong_chea  '))
    worksheet_data_analyse_customer.set_column('D:F',len('Customer Sales'))
    worksheet_data_analyse_customer.write(1,0,"Sites",Title_format)
    worksheet_data_analyse_customer.write(1,1,"Platform",Title_format)
    worksheet_data_analyse_customer.write(1,2,"Advisor",Title_format)
    worksheet_data_analyse_customer.write(1,3,"YTD %s"%(Current_date.year),Title_format)
    worksheet_data_analyse_customer.write(1,4,"YTD %s"%(Date_N_1.year),Title_format)
    worksheet_data_analyse_customer.write(1,5,"YTD %s"%(Date_N_2.year),Title_format)
    worksheet_data_analyse_customer.autofilter(1,0,len(ListSiteActive)+2,int(Current_date.month)*3+5)
    worksheet_data_analyse_customer.write_formula(0,4,"=SUBTOTAL(9,D3:D300)/SUBTOTAL(9,E3:E300)",Percentage_format)
    worksheet_data_analyse_customer.write_formula(0,5,"=SUBTOTAL(9,D3:D300)/SUBTOTAL(9,F3:F300)",Percentage_format)

    worksheet_data_analyse_wins.write(0,0,"IN JUGS",Title_format_Jugs)
    worksheet_data_analyse_wins.set_column('C:C',len('leanghong_chea  '))
    worksheet_data_analyse_wins.set_column('D:F',len('Customer Sales'))
    worksheet_data_analyse_wins.write(1,0,"Sites",Title_format)
    worksheet_data_analyse_wins.write(1,1,"Platform",Title_format)
    worksheet_data_analyse_wins.write(1,2,"Advisor",Title_format)
    worksheet_data_analyse_wins.write(1,3,"YTD %s"%(Current_date.year),Title_format)
    worksheet_data_analyse_wins.write(1,4,"YTD %s"%(Date_N_1.year),Title_format)
    worksheet_data_analyse_wins.write(1,5,"YTD %s"%(Date_N_2.year),Title_format)
    worksheet_data_analyse_wins.autofilter(1,0,len(ListSiteActive)+2,int(Current_date.month)*3+5)
    worksheet_data_analyse_wins.write_formula(0,4,"=SUBTOTAL(9,D3:D300)/SUBTOTAL(9,E3:E300)",Percentage_format)
    worksheet_data_analyse_wins.write_formula(0,5,"=SUBTOTAL(9,D3:D300)/SUBTOTAL(9,F3:F300)",Percentage_format)

    worksheet_data_analyse_total.write(0,0,"IN JUGS",Title_format_Jugs)
    worksheet_data_analyse_total.set_column('C:C',len('leanghong_chea  '))
    worksheet_data_analyse_total.set_column('D:F',len('Customer Sales'))
    worksheet_data_analyse_total.write(1,0,"Sites",Title_format)
    worksheet_data_analyse_total.write(1,1,"Platform",Title_format)
    worksheet_data_analyse_total.write(1,2,"Advisor",Title_format)
    worksheet_data_analyse_total.write(1,3,"YTD %s"%(Current_date.year),Title_format)
    worksheet_data_analyse_total.write(1,4,"YTD %s"%(Date_N_1.year),Title_format)
    worksheet_data_analyse_total.write(1,5,"YTD %s"%(Date_N_2.year),Title_format)
    worksheet_data_analyse_total.autofilter(1,0,len(ListSiteActive)+2,int(Current_date.month)*3+5)
    worksheet_data_analyse_total.write_formula(0,4,"=SUBTOTAL(9,D3:D300)/SUBTOTAL(9,E3:E300)",Percentage_format)
    worksheet_data_analyse_total.write_formula(0,5,"=SUBTOTAL(9,D3:D300)/SUBTOTAL(9,F3:F300)",Percentage_format)
    for i in range(1,Current_date.month+1):
        Name_month = calendar.month_name[i]
        worksheet_data_analyse_customer.merge_range(0,3*i+3,0,3*i+5,str(Name_month),Title_format)
        worksheet_data_analyse_customer.write(1,3*i+3,'%s'%(Current_date.year),Title_format)
        worksheet_data_analyse_customer.write(1,3*i+4,'%s'%(Date_N_1.year),Title_format)
        worksheet_data_analyse_customer.write(1,3*i+5,'%s'%(Date_N_2.year),Title_format)
        worksheet_data_analyse_wins.merge_range(0,3*i+3,0,3*i+5,str(Name_month),Title_format)
        worksheet_data_analyse_wins.write(1,3*i+3,'%s'%(Current_date.year),Title_format)
        worksheet_data_analyse_wins.write(1,3*i+4,'%s'%(Date_N_1.year),Title_format)
        worksheet_data_analyse_wins.write(1,3*i+5,'%s'%(Date_N_2.year),Title_format)
        worksheet_data_analyse_total.merge_range(0,3*i+3,0,3*i+5,str(Name_month),Title_format)
        worksheet_data_analyse_total.write(1,3*i+3,'%s'%(Current_date.year),Title_format)
        worksheet_data_analyse_total.write(1,3*i+4,'%s'%(Date_N_1.year),Title_format)
        worksheet_data_analyse_total.write(1,3*i+5,'%s'%(Date_N_2.year),Title_format)
    for j in range(len(ListSiteActive)):
        allSales_Site = list(filter(lambda row: row[3] == ListSiteActive[j][0], allSales))
        Site_Info = list(filter(lambda row: row[2] == ListSiteActive[j][0], allSite_Info))
        worksheet_data_analyse_customer.write(j+2,0,ListSiteActive[j][0],Title_format)
        worksheet_data_analyse_customer.write(j+2,1,Site_Info[0][0],Title_format)
        worksheet_data_analyse_customer.write(j+2,2,Site_Info[0][1],Title_format)
        worksheet_data_analyse_wins.write(j+2,0,ListSiteActive[j][0],Title_format)
        worksheet_data_analyse_wins.write(j+2,1,Site_Info[0][0],Title_format)
        worksheet_data_analyse_wins.write(j+2,2,Site_Info[0][1],Title_format)
        worksheet_data_analyse_total.write(j+2,0,ListSiteActive[j][0],Title_format)
        worksheet_data_analyse_total.write(j+2,1,Site_Info[0][0],Title_format)
        worksheet_data_analyse_total.write(j+2,2,Site_Info[0][1],Title_format)
        #worksheet_data_analyse_customer.write(j+2,3,"Customer Sales",Number_grey_format)
        Sales_cust_ytd = Sales_wins_ytd = Sales_tot_ytd = 0
        Sales_cust_ytd_lastyear = Sales_wins_ytd_lastyear = Sales_tot_ytd_lastyear = 0
        Sales_cust_ytd_last2year = Sales_wins_ytd_last2year = Sales_tot_ytd_last2year = 0
        for i in range(1,Current_date.month+1):
            Date_now = date(Current_date.year,i,1)
            Date_lastyear = date(Date_N_1.year,i,1)
            Date_last2year = date(Date_N_2.year,i,1)
            Sale_now = list(filter(lambda row: row[2] == str(Date_now), allSales_Site))
            Sale_lastyear = list(filter(lambda row: row[2] == str(Date_lastyear), allSales_Site))
            Sale_last2year = list(filter(lambda row: row[2] == str(Date_last2year), allSales_Site))
            Tot_now = Tot_lastyear = Tot_last2year = 0

            # Customer Sales
            if Sale_now and Sale_now[0][0]>0:
                worksheet_data_analyse_customer.write(j+2,3*i+3,Sale_now[0][0],Number_grey_format)
                Tot_now += Sale_now[0][0]
                Sales_cust_ytd += Sale_now[0][0]
            else:
                worksheet_data_analyse_customer.write(j+2,3*i+3,None,Empty_format)

            if Sale_lastyear and Sale_lastyear[0][0]>0:
                worksheet_data_analyse_customer.write(j+2,3*i+4,Sale_lastyear[0][0],Number_grey_format)
                Tot_lastyear += Sale_lastyear[0][0]
                Sales_cust_ytd_lastyear += Sale_lastyear[0][0]
            else:
                worksheet_data_analyse_customer.write(j+2,3*i+4,None,Empty_format)

            if Sale_last2year and Sale_last2year[0][0]>0:
                worksheet_data_analyse_customer.write(j+2,3*i+5,Sale_last2year[0][0],Number_grey_format_right)
                Tot_last2year += Sale_last2year[0][0]
                Sales_cust_ytd_last2year += Sale_last2year[0][0]
            else:
                worksheet_data_analyse_customer.write(j+2,3*i+5,None,Empty_format_right)

            # WINS Sales
            if Sale_now and Sale_now[0][1]>0:
                worksheet_data_analyse_wins.write(j+2,3*i+3,Sale_now[0][1],Number_format)
                Tot_now += Sale_now[0][1]
                Sales_wins_ytd += Sale_now[0][1]
            else:
                worksheet_data_analyse_wins.write(j+2,3*i+3,None,Empty_format)


            if Sale_lastyear and Sale_lastyear[0][1]>0:
                worksheet_data_analyse_wins.write(j+2,3*i+4,Sale_lastyear[0][1],Number_format)
                Tot_lastyear += Sale_lastyear[0][1]
                Sales_wins_ytd_lastyear += Sale_lastyear[0][1]
            else:
                worksheet_data_analyse_wins.write(j+2,3*i+4,None,Empty_format)


            if Sale_last2year and Sale_last2year[0][1]>0:
                worksheet_data_analyse_wins.write(j+2,3*i+5,Sale_last2year[0][1],Number_format_right)
                Tot_last2year += Sale_last2year[0][1]
                Sales_wins_ytd_last2year += Sale_last2year[0][1]
            else:
                worksheet_data_analyse_wins.write(j+2,3*i+5,None,Empty_format_right)

            # Tot Sales
            if Tot_now>0:
                worksheet_data_analyse_total.write(j+2,3*i+3,Tot_now,Number_format)
                Sales_tot_ytd += Tot_now
            else:
                worksheet_data_analyse_total.write(j+2,3*i+3,None,Empty_format)


            if Tot_lastyear>0:
                worksheet_data_analyse_total.write(j+2,3*i+4,Tot_lastyear,Number_format)
                Sales_tot_ytd_lastyear += Tot_lastyear
            else:
                worksheet_data_analyse_total.write(j+2,3*i+4,None,Empty_format)


            if Tot_last2year>0:
                worksheet_data_analyse_total.write(j+2,3*i+5,Tot_last2year,Number_format_right)
                Sales_tot_ytd_last2year += Tot_last2year
            else:
                worksheet_data_analyse_total.write(j+2,3*i+5,None,Empty_format_right)
        if Sales_cust_ytd:
            worksheet_data_analyse_customer.write(j+2,3,Sales_cust_ytd,Bold_format)
        else:
            worksheet_data_analyse_customer.write(j+2,3,None,Bold_format)
        if Sales_cust_ytd_lastyear:
            worksheet_data_analyse_customer.write(j+2,4,Sales_cust_ytd_lastyear,Bold_format)
        else:
            worksheet_data_analyse_customer.write(j+2,4,None,Bold_format)
        if Sales_cust_ytd_last2year:
            worksheet_data_analyse_customer.write(j+2,5,Sales_cust_ytd_last2year,Bold_format)
        else:
            worksheet_data_analyse_customer.write(j+2,5,None,Bold_format)
        if Sales_wins_ytd:
            worksheet_data_analyse_wins.write(j+2,3,Sales_wins_ytd,Bold_format)
        else:
            worksheet_data_analyse_wins.write(j+2,3,None,Bold_format)
        if Sales_wins_ytd_lastyear:
            worksheet_data_analyse_wins.write(j+2,4,Sales_wins_ytd_lastyear,Bold_format)
        else:
            worksheet_data_analyse_wins.write(j+2,4,None,Bold_format)
        if Sales_wins_ytd_last2year:
            worksheet_data_analyse_wins.write(j+2,5,Sales_wins_ytd_last2year,Bold_format)
        else:
            worksheet_data_analyse_wins.write(j+2,5,None,Bold_format)
        if Sales_tot_ytd:
            worksheet_data_analyse_total.write(j+2,3,Sales_tot_ytd,Bold_format)
        else:
            worksheet_data_analyse_total.write(j+2,3,None,Bold_format)
        if Sales_tot_ytd_lastyear:
            worksheet_data_analyse_total.write(j+2,4,Sales_tot_ytd_lastyear,Bold_format)
        else:
            worksheet_data_analyse_total.write(j+2,4,None,Bold_format)
        if Sales_tot_ytd_last2year:
            worksheet_data_analyse_total.write(j+2,5,Sales_tot_ytd_last2year,Bold_format)
        else:
            worksheet_data_analyse_total.write(j+2,5,None,Bold_format)



    allListAdvisor = con.execute("SELECT Distinct Advisor,Platform FROM Sites JOIN Sales ON Sales.Id_Site = Sites.Id_Site WHERE Total_Sales>0 ORDER BY Platform").fetchall()
    total_row = 0

    worksheet_analyse.set_column('A:A',len('leanghong_chea  '))
    Number_format_green = workbook.add_format({"num_format": '# ##0','bg_color' : "#EBF1DE",'border':1})
    Percentage_format_green = workbook.add_format({"num_format" : '0.0%','bg_color': "#EBF1DE",'border':1})
    Number_format_orange = workbook.add_format({"num_format": '# ##0','bg_color' : "#FDE9D9",'border':1})
    Percentage_format_orange = workbook.add_format({"num_format" : '0.0%','bg_color': "#FDE9D9",'border':1})
    Number_format_blue = workbook.add_format({"num_format": '# ##0','bg_color' : "#DCE6F1",'border':1})
    Percentage_format_blue = workbook.add_format({"num_format" : '0.0%','bg_color': "#DCE6F1",'border':1})
    Number_format_blue_platform = workbook.add_format({"num_format": '# ##0','bg_color' : "#538DD5",'border':1})
    Percentage_format_blue_platform = workbook.add_format({"num_format" : '0.0%','bg_color': "#538DD5",'border':1})
    Number_format_orange_platform = workbook.add_format({"num_format": '# ##0','bg_color' : "#E26B0A",'border':1})
    Percentage_format_orange_platform = workbook.add_format({"num_format" : '0.0%','bg_color': "#E26B0A",'border':1})
    Number_format_green_platform = workbook.add_format({"num_format": '# ##0','bg_color' : "#76933C",'border':1})
    Percentage_format_green_platform = workbook.add_format({"num_format" : '0.0%','bg_color': "#76933C",'border':1})
    Title_format = workbook.add_format({"bold" : True})
    Title_format_platform = workbook.add_format({"bold" : True, 'font_color' : '#FF0000', 'center_across' : True})


    worksheet_analyse.write(0,0,"IN JUGS",Title_format_Jugs)
    worksheet_analyse.merge_range(0,1,0,3,'Customer Sales',Title_format_platform)
    worksheet_analyse.merge_range(0,5,0,7,'WinS Sales',Title_format_platform)
    worksheet_analyse.merge_range(0,9,0,11,'Total Sales',Title_format_platform)
    worksheet_analyse.write(1,1,"YTD %s"%(Date_N_1.year),Title_format)
    worksheet_analyse.write(1,2,"YTD %s"%(Current_date.year),Title_format)
    worksheet_analyse.write(1,3,"%% %s/%s"%(str(Current_date.year)[2:4],str(Date_N_1.year)[2:4]),Title_format)
    worksheet_analyse.write(1,5,"YTD %s"%(Date_N_1.year),Title_format)
    worksheet_analyse.write(1,6,"YTD %s"%(Current_date.year),Title_format)
    worksheet_analyse.write(1,7,"%% %s/%s"%(str(Current_date.year)[2:4],str(Date_N_1.year)[2:4]),Title_format)
    worksheet_analyse.write(1,9,"YTD %s"%(Date_N_1.year),Title_format)
    worksheet_analyse.write(1,10,"YTD %s"%(Current_date.year),Title_format)
    worksheet_analyse.write(1,11,"%% %s/%s"%(str(Current_date.year)[2:4],str(Date_N_1.year)[2:4]),Title_format)
    for n in range(len(ListPlatform)):
        ListAdvisor = list(filter(lambda row: row[1] == ListPlatform[n], allListAdvisor))
        worksheet_analyse.write(2+total_row,0,ListPlatform[n],Title_format_platform)
        worksheet_analyse.write_formula(2+total_row,1,"=SUMPRODUCT(('Customer Sales'!G2:%s2=\"%s\")*('Customer Sales'!B3:B%s=\"%s\"),'Customer Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Date_N_1.year),len(ListSiteActive)*2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)*2),Number_format_blue_platform)
        worksheet_analyse.write_formula(2+total_row,2,"=SUMPRODUCT(('Customer Sales'!G2:%s2=\"%s\")*('Customer Sales'!B3:B%s=\"%s\"),'Customer Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Current_date.year),len(ListSiteActive)+2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)+2),Number_format_blue_platform)
        worksheet_analyse.write_formula(2+total_row,3,"=IFERROR(C%s/B%s,0)"%(3+total_row,3+total_row),Percentage_format_blue_platform)

        worksheet_analyse.write_formula(2+total_row,5,"=SUMPRODUCT(('WinS Sales'!G2:%s2=\"%s\")*('WinS Sales'!B3:B%s=\"%s\"),'WinS Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Date_N_1.year),len(ListSiteActive)*2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)*2),Number_format_orange_platform)
        worksheet_analyse.write_formula(2+total_row,6,"=SUMPRODUCT(('WinS Sales'!G2:%s2=\"%s\")*('WinS Sales'!B3:B%s=\"%s\"),'WinS Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Current_date.year),len(ListSiteActive)+2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)+2),Number_format_orange_platform)
        worksheet_analyse.write_formula(2+total_row,7,"=IFERROR(G%s/F%s,0)"%(3+total_row,3+total_row),Percentage_format_orange_platform)

        worksheet_analyse.write_formula(2+total_row,9,"=B%s+F%s"%(3+total_row,3+total_row),Number_format_green_platform)
        worksheet_analyse.write_formula(2+total_row,10,"=C%s+G%s"%(3+total_row,3+total_row),Number_format_green_platform)
        worksheet_analyse.write_formula(2+total_row,11,"=IFERROR(K%s/J%s,0)"%(3+total_row,3+total_row),Percentage_format_green_platform)

        for j in range(len(ListAdvisor)):
            if ListAdvisor[j] != 'Stop' and ListAdvisor[j][0]:
                worksheet_analyse.write(3+total_row,0,ListAdvisor[j][0],Title_format)
                worksheet_analyse.write_formula(3+total_row,1,"=SUMPRODUCT(('Customer Sales'!G2:%s2=\"%s\")*('Customer Sales'!C3:C%s=\"%s\")*('Customer Sales'!B3:B%s=\"%s\"),'Customer Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Date_N_1.year),len(ListSiteActive)+2,ListAdvisor[j][0],len(ListSiteActive)+2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)+2),Number_format_blue)
                worksheet_analyse.write_formula(3+total_row,2,"=SUMPRODUCT(('Customer Sales'!G2:%s2=\"%s\")*('Customer Sales'!C3:C%s=\"%s\")*('Customer Sales'!B3:B%s=\"%s\"),'Customer Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Current_date.year),len(ListSiteActive)+2,ListAdvisor[j][0],len(ListSiteActive)+2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)+2),Number_format_blue)
                worksheet_analyse.write_formula(3+total_row,3,"=IFERROR(C%s/B%s,0)"%(4+total_row,4+total_row),Percentage_format_blue)

                worksheet_analyse.write_formula(3+total_row,5,"=SUMPRODUCT(('WinS Sales'!G2:%s2=\"%s\")*('WinS Sales'!C3:C%s=\"%s\")*('WinS Sales'!B3:B%s=\"%s\"),'WinS Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Date_N_1.year),len(ListSiteActive)+2,ListAdvisor[j][0],len(ListSiteActive)+2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)+2),Number_format_orange)
                worksheet_analyse.write_formula(3+total_row,6,"=SUMPRODUCT(('WinS Sales'!G2:%s2=\"%s\")*('WinS Sales'!C3:C%s=\"%s\")*('WinS Sales'!B3:B%s=\"%s\"),'WinS Sales'!G3:%s%s)"%(xl_col_to_name(int(Current_date.month)*3+5),int(Current_date.year),len(ListSiteActive)+2,ListAdvisor[j][0],len(ListSiteActive)+2,ListPlatform[n],xl_col_to_name(int(Current_date.month)*3+5),len(ListSiteActive)+2),Number_format_orange)
                worksheet_analyse.write_formula(3+total_row,7,"=IFERROR(G%s/F%s,0)"%(4+total_row,4+total_row),Percentage_format_orange)

                worksheet_analyse.write_formula(3+total_row,9,"=B%s+F%s"%(4+total_row,4+total_row),Number_format_green)
                worksheet_analyse.write_formula(3+total_row,10,"=C%s+G%s"%(4+total_row,4+total_row),Number_format_green)
                worksheet_analyse.write_formula(3+total_row,11,"=IFERROR(K%s/J%s,0)"%(4+total_row,4+total_row),Percentage_format_green)
                total_row+=1
        total_row+=2


def LaunchExcelCreationAdvisor(ListDate,ListSiteActive,ListTierThisYear,ListProvPlat,exchange_rate):
    global Current_date, Date_N_1, Date_N_2
    Current_date = ListDate[-1]
    Date_N_1 = ListDate[-13]
    Date_N_2 = ListDate[-25]
    ListPlatform = ListProvPlat[0]
    CreatefileAdvisor(ListSiteActive,ListPlatform)
    WriteBonus(ListSiteActive,ListTierThisYear,exchange_rate,ListPlatform,Current_date.year)
    workbook.close()

if __name__ == '__main__':
    global Current_date, Date_N_1, Date_N_2
