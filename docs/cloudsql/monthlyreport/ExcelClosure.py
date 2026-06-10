import db
from datetime import date
from dateutil.relativedelta import *
import xlsxwriter
from monthlyreport.Functionutils import translate_text
import tempfile


def ExcelClosure(Current_date):
    con = db.pool.connect()
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    filepath = tempfile.gettempdir()+'/Site Closing Report '+Year+'-'+Month+'.xlsx'
    workbook = xlsxwriter.Workbook(filepath)
    query = con.execute("SELECT Id_Site, Closing_date, Closing_reason_english, Description,Description_english,Reopening_date FROM Closure ORDER BY Id_Site,Closing_date")
    Closing = query.fetchall()
    query = con.execute("SELECT Id_Site, Closing_date, Closing_reason_english, Description,Description_english,Reopening_date FROM Closure WHERE Closing_date >= %s ORDER BY Id_Site,Closing_date",(date(2020,10,1)))
    Closing_12months = query.fetchall()
    query = con.execute("SELECT Id_Site,Old_Platform,Province,Advisor FROM Sites")
    Info_Site = query.fetchall()
    worksheet_closed12months = workbook.add_worksheet("Closing last 12 months")
    worksheet_closed = workbook.add_worksheet("Closing History")
    #worksheet_changeEntrepreneur = workbook.add_worksheet("Change in entrepreneur")
    date_format = workbook.add_format({'num_format': 'yyyy/mm/dd'})
    text_format = workbook.add_format({'text_wrap' : True})
    worksheet_closed.set_column('E:G',30)
    worksheet_closed.set_column('C:C',len('yan_chansophea'))
    worksheet_closed.set_column('D:D',len('Reopening_date'))
    worksheet_closed.set_column('H:H',len('Reopening_date  '))
    worksheet_closed.set_column('I:I',len('Reopening_date         '))
    worksheet_closed12months.set_column('E:G',30)
    worksheet_closed12months.set_column('C:C',len('yan_chansophea'))
    worksheet_closed12months.set_column('D:D',len('Reopening_date'))
    worksheet_closed12months.set_column('H:H',len('Reopening_date  '))
    worksheet_closed12months.set_column('I:I',len('Reopening_date         '))

    #worksheet_changeEntrepreneur.set_column('B:E',26.22)
    #worksheet_changeEntrepreneur.set_column('F:F',31.33)
    worksheet_closed.add_table(0,0,len(Closing),9,{'name':'TableClosing',
                                                        'columns' : [{'header' : 'Site'},
                                                                    {'header' : 'Platform'},
                                                                    {'header' : 'Advisor'},
                                                                    {'header' : 'Closing Date'},
                                                                    {'header' : 'Reason'},
                                                                    {'header' : 'Description'},
                                                                    {'header' : 'Description english'},
                                                                    {'header' : 'Reopening date'},
                                                                    {'header' : 'Closing duration'},
                                                                    {'header' : 'Entrepreneur Name'}]})
    worksheet_closed12months.add_table(0,0,len(Closing_12months),8,{'name':'TableClosing12months',
                                                        'columns' : [{'header' : 'Site'},
                                                                    {'header' : 'Platform'},
                                                                    {'header' : 'Advisor'},
                                                                    {'header' : 'Closing Date'},
                                                                    {'header' : 'Reason'},
                                                                    {'header' : 'Description'},
                                                                    {'header' : 'Description english'},
                                                                    {'header' : 'Reopening date'},
                                                                    {'header' : 'Entrepreneur Name'}]})

    # worksheet_changeEntrepreneur.add_table(0,0,len(ChangeEntrepreneur),5,{'name':'TableChangeEntrepreneur',
    #                                                     'columns' : [{'header' : 'Site'},
    #                                                                 {'header' : 'Old Entrepreneur Name'},
    #                                                                 {'header' : 'Reason for departure'},
    #                                                                 {'header' : 'New Enptreneur Name'},
    #                                                                 {'header' : 'New Entrepreneur ID'},
    #                                                                 {'header' : 'New Entrepreneur Phone Number'}]})
#TAB SITE CLOSED

    for i in range(len(Closing)):
        Site = list(filter(lambda row: row[0] == Closing[i][0], Info_Site))
        Entrepreneur_Flash = None
        Entrepreneur_Profile = None
        worksheet_closed.write(i+1,0,Closing[i][0])
        worksheet_closed.write(i+1,1,Site[0][1])
        worksheet_closed.write(i+1,2,Site[0][3])
        worksheet_closed.write(i+1,3,Closing[i][1],date_format)
        worksheet_closed.write(i+1,4,Closing[i][2],text_format)
        worksheet_closed.write(i+1,5,Closing[i][3],text_format)
        worksheet_closed.write(i+1,6,Closing[i][4],text_format)
        worksheet_closed.write(i+1,7,Closing[i][5],date_format)
        if Entrepreneur_Flash and Entrepreneur_Flash[0][0]:
            worksheet_closed.write(i+1,9,Entrepreneur_Flash[0][0])
        elif Entrepreneur_Profile and Entrepreneur_Profile[0][0] != '0' and Entrepreneur_Profile[0][0]:
            worksheet_closed.write(i+1,9,Entrepreneur_Profile[0][0])
        if Closing[i][5]:
            Closing_time = (Closing[i][5].year - Closing[i][1].year) * 12 + Closing[i][5].month - Closing[i][1].month
            worksheet_closed.write_formula(i+1,8,'= %s & " Months"'%(Closing_time))
        else:
            Closing_time = (Current_date.year - Closing[i][1].year) * 12 + Current_date.month - Closing[i][1].month
            worksheet_closed.write_formula(i+1,8,'= %s & " Months"'%(Closing_time))
    for j in range(len(Closing_12months)):
        Site_12months = list(filter(lambda row: row[0] == Closing_12months[j][0], Info_Site))
        Entrepreneur_Flash = None
        Entrepreneur_Profile = None
        worksheet_closed12months.write(j+1,0,Closing_12months[j][0])
        worksheet_closed12months.write(j+1,1,Site_12months[0][1])
        worksheet_closed12months.write(j+1,2,Site_12months[0][3])
        worksheet_closed12months.write(j+1,3,Closing_12months[j][1],date_format)
        worksheet_closed12months.write(j+1,4,Closing_12months[j][2],text_format)
        worksheet_closed12months.write(j+1,5,Closing_12months[j][3],text_format)
        worksheet_closed12months.write(j+1,6,Closing_12months[j][4],text_format)
        worksheet_closed12months.write(j+1,7,Closing_12months[j][5],date_format)
        if Entrepreneur_Flash and Entrepreneur_Flash[0][0]:
            worksheet_closed12months.write(j+1,8,Entrepreneur_Flash[0][0])
        elif Entrepreneur_Profile and Entrepreneur_Profile[0][0] != '0' and Entrepreneur_Profile[0][0]:
            worksheet_closed12months.write(j+1,8,Entrepreneur_Profile[0][0])

#TAB ENTREPRENEUR CHANGING

    # for k in range(len(ChangeEntrepreneur)):
    #     worksheet_changeEntrepreneur.write(k+1,0,ChangeEntrepreneur[k][0])
    #     worksheet_changeEntrepreneur.write(k+1,1,ChangeEntrepreneur[k][1])
    #     worksheet_changeEntrepreneur.write(k+1,2,ChangeEntrepreneur[k][2])
    #     worksheet_changeEntrepreneur.write(k+1,3,ChangeEntrepreneur[k][3])
    #     worksheet_changeEntrepreneur.write(k+1,4,ChangeEntrepreneur[k][4])
    #     worksheet_changeEntrepreneur.write(k+1,5,ChangeEntrepreneur[k][5])

    workbook.close()

def LaunchExcelCreationClosure(Current_date):
    ExcelClosure(Current_date)

if __name__ == '__main__':
    ExcelClosure(date(2021,10,1))
