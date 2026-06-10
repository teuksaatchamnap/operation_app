import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
from datetime import date,timedelta, datetime
from calendar import monthrange
import db
import tempfile
from dateutil.relativedelta import *
import calendar
from Functionutils import translate_text
import flask
import os



def ProvinceReport(Current_date,exchange_rate):
    con = db.pool.connect()
    Year = str(Current_date.year)
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    filepath = tempfile.gettempdir()+'/Province Report ' + Year + '-' + Month +'.xlsm'
    if os.path.exists(filepath):
            os.remove(filepath)
    workbook = xlsxwriter.Workbook(filepath)

    workbook.add_vba_project(flask.current_app.root_path+'/static/VBA/vbaProjectProvinceReport.bin')

    List_Name_Province = [
                ["Kandal","កណ្តាល"],
                ["Kratie","ក្រចេះ"],
                ["Kampong Cham ","កំពង់ចាម"],
                ["Kampong Chhnang","កំពង់ឆ្នាំង"],
                ["Kampong Thom","កំពង់ធំ"],
                ["Kampong Speu","កំពង់ស្ពឺ"],
                ["Kampot","កំពត"],
                ["Takeo","តាកែវ"],
                ["Tbong Khmum","ត្បូងឃ្មុំ"],
                ["Banteay Meanchey","បន្ទាយមានជ័យ"],
                ["Pailin ","ប៉ៃលិន"],
                ["Battambang","បាត់ដំបង"],
                ["Pursat ","ពោធិ៍សាត់"],
                ["Prey Veng","ព្រៃវែង"],
                ["Preah Vihear","ព្រះវិហារ"],
                ["Siem Reap","សៀមរាប"],
                ["Svay Rieng","ស្វាយរៀង"],
                ["Oddar Meanchey ","ឧត្តរមានជ័យ"]]

    Title_format = workbook.add_format({'center_across':True,'font_color':'#00B0F0','font':'Khmer OS Muol Light','font_size':8})
    Title_nocenter_format = workbook.add_format({'font_color':'#00B0F0','font':'Khmer OS Muol Light','font_size':8})
    Title_nocenter_format_SR = workbook.add_format({'font_color':'#00B0F0','font':'Khmer OS Siemreap','text_wrap':True,'top':1,'border_color':'#00B0F0','font_size':8})
    Bold_format_SR = workbook.add_format({'center_across':True,'bold':True,'font':'Khmer OS Siemreap','font_size':8})
    Bold_format_ML = workbook.add_format({'center_across':True,'bold':True,'font':'Khmer OS Muol Light','font_size':8})
    Bold_Underline_format_SR = workbook.add_format({'underline':True,'bold':True,'text_wrap':True,'valign':'vtop','font_size':8,'font':'Khmer OS Siemreap'})
    Bold_Underline_format_ML = workbook.add_format({'underline':True,'bold':True,'text_wrap':True,'valign':'vtop','font_size':8,'font':'Khmer OS Muol Light'})
    Normal_format_SR = workbook.add_format({'text_wrap':True,'valign':'vtop','font_size':8,'font':'Khmer OS Siemreap','align':'top'})
    Normal_format_ML = workbook.add_format({'text_wrap':True,'valign':'vtop','font_size':8,'font':'Khmer OS Siemreap','align':'top'})
    Left_to_right_format = workbook.add_format({'reading_order':2,'align':'right','font_size':8,'font':'Khmer OS Siemreap'})
    Bold_border_format_ML = workbook.add_format({'center_across':True,'bold':True,'border':1,'font':'Khmer OS Muol Light','font_size':8})
    Bold_border_bg_format_SR = workbook.add_format({'center_across':True,'bold':True,'border':1,"bg_color":"#FCD5B4","text_wrap":True,'font':'Khmer OS Siemreap','font_size':8})
    Percentage_format = workbook.add_format({'num_format':"0.0%",'border':1,'font_size':8,'font':'Khmer OS Muol Light'})
    Normal_table_format = workbook.add_format({'text_wrap':True,'border':1,'font_size':8,'font':'Khmer OS Siemreap'})
    Number_table_format = workbook.add_format({'text_wrap':True,'border':1,'font_size':8,'font':'Khmer OS Siemreap','num_format':"# ##0"})
    Date_table_format = workbook.add_format({'text_wrap':True,'border':1,'font_size':8,'font':'Khmer OS Siemreap','num_format':'mm-yyyy'})

    ListProvince = con.execute("SELECT DISTINCT Province FROM Sites JOIN Sales ON Sites.Id_Site = Sales.Id_Site WHERE Month = %s AND Total_Sales > 0 AND Province <>'Dead' AND Province <> '' AND Province <> 'Stop'",(Current_date)).fetchall()
    Info_end_year = con.execute("""SELECT COUNT(DISTINCT Sales.Id_Site),COUNT(DISTINCT CONCAT(Code_District, District))
                                  FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                                  WHERE Month = %s AND Total_Sales >0
                                """,(date(Current_date.year-1,12,1))).fetchall()
    
    try:
        year_previous = translate_text("km",str(Current_date.year-1))
    except:
        year_previous = str(Current_date.year-1)
    try:
        Total_Number_site_active = translate_text("km",str(int(Info_end_year[0][0])))
    except:
        Total_Number_site_active = str(int(Info_end_year[0][0]))
    try:
        Total_Number_District = translate_text("km",str(int(Info_end_year[0][1])))
    except:
        Total_Number_District = str(int(Info_end_year[0][1]))    
    for i in range(len(ListProvince)):
        Sales_Total = con.execute("""SELECT SUM(Total_Sales-Bottle_Sales),COUNT(Total_Sales),SUM(WiS_Sales),SUM(WiS_Income),
                                  AVG((Total_Sales-Bottle_Sales)/Number_Open_Days)*20 
                                  FROM Sales JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                                  WHERE Month = %s AND Province = %s"""
                                  ,(Current_date,ListProvince[i][0])).fetchall()
        Beneficiaries_Total = con.execute("""SELECT SUM(Beneficiaries) FROM Beneficiaries 
                                          JOIN Sites ON Beneficiaries.Id_Site = Sites.Id_Site 
                                          WHERE Month = %s AND Province = %s""",(Current_date,ListProvince[i][0])).fetchall()
        
        Sales = con.execute("""SELECT Sites.Id_Site,Total_Sales-Bottle_Sales FROM Sites 
                            JOIN Sales ON Sites.Id_Site = Sales.Id_Site 
                            WHERE Month = %s AND Province = %s""",(Current_date,ListProvince[i][0])).fetchall()
        
        Sites = con.execute("""SELECT DISTINCT Sites.Id_Site,Commune,District,Commune_khmer,District_khmer,
                            Sale_Starting_Date,Land_of_kiosk,Number_Population,NumberSchoolsWinS,NumberStudentsWinS,
                            SUM(Total_Sales-Bottle_Sales) FROM Sites 
                            JOIN Sales ON Sites.Id_Site = Sales.Id_Site 
                            WHERE Month <= %s AND Month > %s AND Province = %s GROUP BY Sales.Id_Site""",
                            (Current_date,Current_date-relativedelta(months=+12),ListProvince[i][0])).fetchall()
        
        allStarting_date = con.execute("""SELECT MIN(Month),Sales.Id_Site FROM Sales 
                                       JOIN Sites ON Sales.Id_Site = Sites.Id_Site 
                                       WHERE Province = %s GROUP BY Id_Site""",ListProvince[i][0]).fetchall()
        
        allOperator = con.execute("""SELECT Id_Site,Number_of_Operator FROM Indicators 
                                  WHERE Month = %s""",Current_date).fetchall()
        
        allBeneficiaries = con.execute("""SELECT Id_Site,IFNULL(Beneficiaries,0) 
                                       FROM Beneficiaries WHERE Month = %s""",Current_date).fetchall()
        worksheet = workbook.add_worksheet('%s'%(ListProvince[i][0]))
        worksheet.hide_gridlines(2)

        try:
            Province_name = list(filter(lambda row: row[0] == ListProvince[i][0], List_Name_Province))[0][1]
        except:
            Province_name = ListProvince[i][0]
        print(Province_name)

        worksheet.insert_button('N4', {'macro':   'ThisWorkbook.PrintAll',
                                   'caption': 'Print All',
                                   'width':   80,
                                   'height':  30})
        worksheet.insert_button('N7', {'macro':   'ThisWorkbook.PrintThisProvince',
                                   'caption': 'Print This Province',
                                   'width':   80,
                                   'height':  30})
        
        try:
            Number_site_active = translate_text("km",str(int(Sales_Total[0][1])))
        except:
            Number_site_active = int(Sales_Total[0][1])
        try:
            SalesTotal = translate_text("km",str(int(Sales_Total[0][0])))
        except:
            SalesTotal= int(Sales_Total[0][0])
        try:
            formatted_number = "{:,}".format(round(float(Sales_Total[0][4]))).replace(",", " ")
            Lday = translate_text("km", formatted_number)
        except:
            Lday= str(round(float(Sales_Total[0][4])))
        try:
            SalesWinS = translate_text("km",str(int(Sales_Total[0][2])))
        except:
            SalesWinS= int(Sales_Total[0][2])
        try:
            PriceWinS = translate_text("km",str(int(Sales_Total[0][3]/exchange_rate)))
        except:
            PriceWinS= str(int(Sales_Total[0][2]/exchange_rate))
        try:
            Number_site = translate_text("km",str(int(len(Sites))))
        except:
            Number_site = str(int(len(Sites)))
        try:
            Number_site_inactive = translate_text("km",str(int(len(Sites))-int(Sales_Total[0][1])))
        except:
            Number_site_inactive = str(int(len(Sites))-int(Sales_Total[0][1]))
        try:
            Beneficiaries = translate_text("km",str(int(Beneficiaries_Total[0][0])))
        except:
            if Beneficiaries_Total[0][0]:
                Beneficiaries = int(Beneficiaries_Total[0][0])
            else:
                Beneficiaries = 0
        ListMonth = ["មករា","កុម្ភះ","មិនា","មេសា","ឧសភា","មិថុនា"
                    ,"កក្កដា","សីហា","កញ្ញា","តុលា","វិច្ឆកា","ធ្នូ"]
        try:
            year = translate_text("km",str(Current_date.year))
            month = ListMonth[Current_date.month-1]
        except:
            year = str(Current_date.year)
            month = Current_date.month

        worksheet.merge_range(0,0,0,11,"ព្រះរាជាណាចក្រកម្ពុជា",Title_format)
        worksheet.merge_range(1,0,1,11,"ជាតិ សាសនា ព្រះមហាក្សត្រ",Title_format)
        worksheet.insert_image('A1', 'static/LogoTS.png', {'x_scale': 0.03, 'y_scale': 0.03})
        worksheet.write("A5","អង្គការទឹកស្អាត ១០០១ ",Title_nocenter_format)
        worksheet.write("A6","លេខ៖........................./ទស១០០១",Title_nocenter_format)
        if i ==0:
            worksheet.write("L7","",Left_to_right_format)
            worksheet.write("L8","",Left_to_right_format)
        else:
            worksheet.write_formula("L7","='%s'!L7"%(ListProvince[0][0]),Left_to_right_format)
            worksheet.write_formula("L8","='%s'!L8"%(ListProvince[0][0]),Left_to_right_format)
        worksheet.merge_range(8,0,8,11,"សូមគោរពជូន",Bold_format_ML)
        worksheet.merge_range(9,0,9,11,"ឯកឧត្តមអភិបាលនៃគណៈអភិបាលខេត្ត%s"%(Province_name),Bold_format_ML)

        worksheet.merge_range("A12:L12","",Normal_format_SR)
        worksheet.write_rich_string('A12',
                            Bold_Underline_format_ML,
                            'កម្មវត្ថុ៖ ',Normal_format_SR,
                            'របាយការណ៍រីកចម្រើនស្តីពីការអនុវត្តគម្រោងផ្គត់ផ្គង់ទឹកពិសាអូវី នៅទីជនបទក្នុងខេត្ត%s'%(Province_name),Normal_format_SR)

        worksheet.merge_range("A13:L17","",Normal_format_SR)
        worksheet.write_rich_string('A13',Bold_Underline_format_ML,"យោង៖ \n",Normal_format_SR,"          - លិខិតលេខ ៣២៩៧ ស.ជ.ណ ចុះថ្ងៃទី២២ ខែវិច្ឆិកា ឆ្នាំ២០២៣ របស់ក្រសួងមហាផ្ទៃ  ស្តីពីការទទួលស្គាល់លទ្ធផលអង្គសន្និបាតវិសាមញ្ញដោយអនុម័តសម្រេច ផ្លាស់ប្តូរលក្ខន្តិកៈ ផ្លាស់ប្តូរសមាសភាពថ្មីនៃរចនាសម្ព័ន្ធអង្គការទឹកស្អាត១០០១ ។ \n          - កិច្ចព្រមព្រៀងសហប្រតិបត្តិការរវាងក្រសួងអភិវឌ្ឍន៍ជនបទ និងអង្គការទឹកស្អាត១០០១ ចុះថ្ងៃទី១៩ ខែមិថុនា ឆ្នាំ២០២៣។ ",Normal_format_SR)

        worksheet.merge_range('A18:L25', "",Normal_format_SR)
        worksheet.write_rich_string('A18',Bold_Underline_format_ML,"១. សាវតាអង្គការ \n", Normal_format_SR, "          អង្គការទឹកស្អាត១០០១ គឺជាអង្គការក្រៅរដ្ឋាភិបាលក្នុងស្រុកមួយដែលបានអនុវត្តសកម្មភាពផ្គត់ផ្គង់ទឹកសុវត្ថិភាពសម្រាប់បរិភោគដល់ប្រជាពលរដ្ឋនៅជនបទនៃប្រទេសកម្ពុជាចាប់តាំងពីឆ្នាំ២០០៥ បានចុះបញ្ជីជាផ្លូវការជាមួយក្រសួងមហាផ្ទៃក្នុងឆ្នាំ២០០៧ និងបានចុះកិច្ចព្រមព្រៀងសហប្រតិបត្តិការជាមួយក្រសួងអភិវឌ្ឍន៍ជនបទចាប់តាំងពីឆ្នាំ២០០៩។ បច្ចុប្បន្នអង្គការទឹកស្អាត១០០១ មានការិយាល័យតំណាងចំនួនប្រាំរួមមាន៖ ការិយាល័យកណ្តាលនៅរាជធានីភ្នំពេញ ការិយាល័យតំណាងនៅខេត្តបាត់ដំបង ការិយាល័យតំណាងខេត្តសៀមរាប ការិយាល័យតំណាងខេត្តកំពង់ចាម និងការិយាល័យតំណាងខេត្តកំពង់ស្ពឺ។ ចាប់តាំងពីការបង្កើតដំបូងរហូតមកដល់ឆ្នាំ%s អង្គការទឹកស្អាត១០០១ បានសាងសង់ និងដាក់ឱ្យដំណើរការស្ថានីយផលិតទឹកពិសាចំនួន%s ក្នុងឃុំគោលដៅចំនួន%s ក្នុងស្រុកចំនួន%s នៅក្នុងខេត្តគោលដៅចំនួន១៨ នៃប្រទេសកម្ពុជា។ "%(year_previous,Total_Number_site_active,Total_Number_site_active,Total_Number_District),Normal_format_SR)

        worksheet.merge_range('A26:L33',"",Normal_format_SR)
        worksheet.write_rich_string('A26',Bold_Underline_format_ML,"២. សកម្មភាពសំខាន់ៗក្នុងការគាំទ្រដល់សហគ្រិន \n", Normal_format_SR,"សកម្មភាពគាំទ្ររបស់អង្គការទឹកស្អាត១០០១ ដល់សហគ្រិនដើម្បីឱ្យស្ថានីយទឹកមាននិរន្តរភាព រួមមាន  \n            ២.១. ការបណ្តុះបណ្តាលសហគ្រិន និងប្រតិបត្តិករ ការគ្រប់គ្រងហិរញ្ញវត្ថុ ការរៀបចំរបាយការណ៍វឌ្ឍនភាព \n            ២.២. ការផ្តល់ការប្រឹក្សាយោបល់ផ្នែកទីផ្សារ ការគ្រប់គ្រងប្រតិបត្តិការ \n            ២.៣. ការដោះស្រាយការងារបច្ចេកទេស ការធ្វើការគាំទ្រទីផ្សារតាមរយៈការប្រើស្លាកសញ្ញាអូវី។ \n            ២.៤. ការផ្គត់ផ្គង់វត្ថុធាតុដើម និងឧបករណ៍សម្ភារៈ  \n            ២.៥. ការប្រមូលសំណាកគុណភាពទឹក ការត្រួតពិនិត្យទៅលើបទដ្ឋានអនាម័យ  \n",Normal_format_SR)

        worksheet.merge_range('A34:L51',"",Normal_format_SR)
       

        KhmerMonth = translate_text("km",str(calendar.month_name[Current_date.month]))
        KhmerYear = translate_text("km",str(Current_date.year))

        worksheet.write_rich_string('A34',Bold_Underline_format_ML,"៣. លទ្ធផលសម្រេចបាន \n\n",Normal_format_SR,"            គិតត្រឹមខែ%sឆ្នាំ%sនេះ នៅក្នុងខេត្ត%s អង្គការទឹកស្អាត១០០១ បានសាងសង់ស្ថានីយផលិតទឹកសហគមន៍អូវីចំនួន"%(KhmerMonth,KhmerYear,Province_name),Bold_format_SR," %s"%(Number_site),Normal_format_SR," ស្ថានីយ ក្នុងនោះមាន",Bold_format_SR," %s"%(Number_site_inactive),Normal_format_SR,"ស្ថានីយ អសកម្មមិនដំណើរការ មានស្ថានីយចំនួន",Bold_format_SR," %s"%(Number_site_active),Normal_format_SR,"ស្ថានីយ កំពុងដំណើរការ ក្នុងការផលិត និងផ្គត់ផ្គង់ទឹកសុវត្ថិភាពជូនដល់ប្រជាពលរដ្ឋចំនួន",Bold_format_SR,"%s"%(Beneficiaries),Normal_format_SR,"នាក់។ ចំនួនបរិមាណនៃការផលិតទឹកក្នុងមួយស្ថានីយជាមធ្យមប្រមាណ",Bold_format_SR,"%s"%(Lday),Normal_format_SR,"លីត្រ/ថ្ងៃ។  \n \n            ស្ថានីយទឹកសហគមន៍អូវីទាំងអស់បានផលិតទឹកសរុបចំនួន",Bold_format_SR,"%s"%(SalesTotal),Normal_format_SR,"ប៊ីដុង សម្រាប់ផ្គត់ផ្គង់ជូនប្រជាពលរដ្ឋ លើសពីនេះ អង្គការទឹកស្អាត១០០១ ក៏បានឧបត្ថម្ភទឹក ចំនួន",Bold_format_SR,"%s"%(SalesWinS),Normal_format_SR,"ប៊ីដុង ដែលស្មើនឹងទឹកប្រាក់",Bold_format_SR," %s"%(PriceWinS),Normal_format_SR,"ដុល្លារសហរដ្ឋអាមេរិក សម្រាប់ចែកជូនដោយឥតគិតថ្លៃដល់សិស្សសាលាបឋមសិក្សាក្នុងឃុំគោលដៅទាំងអស់នៅក្នុងខេត្ត។ ទិន្នន័យដូចបានបង្ហាញជូនភ្ជាប់ក្នុងតារាង លទ្ធផលសម្រេចបានរបស់អង្គការទឹកស្អាត១០០១។  \n \n            អាស្រ័យដូចបានគោរពជម្រាបជូនខាងលើ  សូម ",Bold_format_ML,"ឯកឧត្តមអភិបាលនៃគណៈអភិបាលខេត្ត",Normal_format_SR," មេត្តាជ្រាបជាសេចក្តីរាយការណ៍ និងបន្តការគាំទ្រដល់បេសកកម្ម ក៏ដូចជាសកម្មភាពរបស់អង្គការទឹកស្អាត១០០១ ស្របទៅនឹងផែនការយុទ្ធសាស្រ្តជាតិស្តីពីការផ្គត់ផ្គង់ទឹកស្អាត និងលើកកម្ពស់អនាម័យជនបទឆ្នាំ២០១៤-២០២៥ របស់ក្រសួងអភិវឌ្ឍន៍ជនបទ និងស្របតាមគោលដៅអភិវឌ្ឍន៍ប្រកបដោយចីរភាពរបស់រាជរដ្ឋាភិបាលកម្ពុជា ឆ្នាំ២០១៦-២០៣០ ដោយសេចក្តីអនុគ្រោះ។  \n \n            សូម ",Bold_format_ML,"ឯកឧត្តមអភិបាល",Normal_format_SR," មេត្តាទទួលនូវការគោរពដ៏ស្មោះស្ម័គ្រអំពីនាងខ្ញុំ។ ",Normal_format_SR)
        worksheet.write("I52","នាយិកាប្រតិបត្តិ",Bold_format_ML)
        worksheet.write("I55","អាម៉ង់ឌីន ឆូស៊ីណង",Bold_format_ML)
        worksheet.write("A52","ចម្លងជូន៖",Bold_format_ML)
        worksheet.merge_range("A54:E54","១. រដ្ឋបាលស្រុកគោលដៅទាំងអស់់",Normal_format_SR)
        worksheet.merge_range("A55:E55","២. រដ្ឋបាលឃុំ សង្កាត់គោលដៅទាំងអស់",Normal_format_SR)

        worksheet.merge_range("A56:L56","ការិយាល័យភ្នំពេញ៖ ផ្ទះលេខ១០០ ផ្លូវ ៩៥ សង្កាតបឹងត្របែក ខណ្ឌចំការមន រាជធានីភ្នំពេញ ព្រះរាជាណាចក្រកម្ពុជា។  ប្រអប់សំបុត្រលេខ ១៤៧២ \nទូរស័ព្ទលេខ៖ ០២៣ ២១៥ ៤២៧ អ៊ីម៉ែលៈ info@teuksaat1001.com, គេហទំព័រ www.teuksaat1001.com.។",Title_nocenter_format_SR)
        worksheet.set_row(55,38)

        worksheet.merge_range("A59:L59","ស្ថានីយផលិតទឹកសហគមន៍ខេត្ត%s"%(Province_name),Bold_border_format_ML)
        worksheet.merge_range("A60:L60","លទ្ធផលប្រចាំខែ %s %s"%(month,year),Bold_border_format_ML)
        worksheet.merge_range("A61:A62","លរ.",Bold_border_bg_format_SR)
        worksheet.merge_range("B61:B62","កូដទីតាំង",Bold_border_bg_format_SR)
        worksheet.merge_range("C61:C62","ឃុំ ",Bold_border_bg_format_SR)
        worksheet.merge_range("D61:D62","ស្រុក",Bold_border_bg_format_SR)
        worksheet.merge_range("E61:E62","កាលបរិច្ឆេទ",Bold_border_bg_format_SR)
        worksheet.merge_range("F61:F62","ទីតាំងសំណង់",Bold_border_bg_format_SR)
        worksheet.merge_range("G61:H61","អ្នកទទួលផល",Bold_border_bg_format_SR)
        worksheet.write("G62","ចំនួន",Bold_border_bg_format_SR)
        worksheet.write("H62","ភាគរយ",Bold_border_bg_format_SR)
        worksheet.merge_range("I61:I62","ចំនួនប្រតិបត្តិករ",Bold_border_bg_format_SR)
        worksheet.merge_range("J61:K61","កម្មវិធីទឹកសាលារៀន",Bold_border_bg_format_SR)
        worksheet.write("J62","ចំនួនសាលា",Bold_border_bg_format_SR)
        worksheet.write("K62","ចំនួនសិស្ស",Bold_border_bg_format_SR)
        worksheet.merge_range("L61:L62","ស្ថានីយសកម្ម",Bold_border_bg_format_SR)


        for i in range(len(Sites)):
            Operator = list(filter(lambda row: row[0] == Sites[i][0], allOperator)) or [(0,0)]
            Beneficiaries = list(filter(lambda row: row[0] == Sites[i][0], allBeneficiaries)) or [(0,0)]
            Starting_date = list(filter(lambda row: row[1] == Sites[i][0], allStarting_date)) or [(0,0)]
            Sales_tot = list(filter(lambda row: row[0] == Sites[i][0], Sales)) or [(0,0)]

            worksheet.write(62+i,0,i+1,Normal_table_format)
            worksheet.write(62+i,1,Sites[i][0],Normal_table_format)
            try:
                worksheet.write(62+i,2,Sites[i][3],Normal_table_format)
            except:
                worksheet.write(62+i,2,Sites[i][1],Normal_table_format)
            try:
                worksheet.write(62+i,3,Sites[i][4],Normal_table_format)
            except:
                worksheet.write(62+i,3,Sites[i][2],Normal_table_format)
            worksheet.write(62+i,4,Starting_date[0][0],Date_table_format)
            try:
                worksheet.write(62+i,5,translate_text("km",str(Sites[i][6])),Normal_table_format)
            except:
                worksheet.write(62+i,5,"",Normal_table_format)
            if Sales_tot[0][1] > 0:
                worksheet.write(62+i,6,Beneficiaries[0][1],Number_table_format)
            else:
                worksheet.write(62+i,6,None,Number_table_format)
            if Sales_tot[0][1] > 0:
                worksheet.write_formula(62+i,7,"=IFERROR(%s/%s,0)"%(Beneficiaries[0][1],Sites[i][7]),Percentage_format)
            else:
                worksheet.write(62+i,7,None,Percentage_format)
            worksheet.write(62+i,8,Operator[0][1],Normal_table_format)
            if Sales_tot[0][1] > 0:
                worksheet.write(62+i,9,Sites[i][8],Normal_table_format)
            else:
                worksheet.write(62+i,9,None,Normal_table_format)
            if Sales_tot[0][1] > 0 and Sites[i][9]!=0:
                worksheet.write(62+i,10,Sites[i][9],Normal_table_format)
            else:
                worksheet.write(62+i,10,None,Normal_table_format)
            if Sales_tot[0][1] > 0:
                try:
                    worksheet.write(62+i,11,translate_text("km","Active"),Normal_table_format)
                except:
                    worksheet.write(62+i,11,"Active",Normal_table_format)
            else:
                try:
                    worksheet.write(62+i,11,translate_text("km","Inactive"),Normal_table_format)
                except:
                    worksheet.write(62+i,11,"Inactive",Normal_table_format)

        worksheet.merge_range(102,0,102,11,"ការិយាល័យភ្នំពេញ៖ ផ្ទះលេខ១០០ ផ្លូវ ៩៥ សង្កាតបឹងត្របែក ខណ្ឌចំការមន រាជធានីភ្នំពេញ ព្រះរាជាណាចក្រកម្ពុជា។  ប្រអប់សំបុត្រលេខ ១៤៧២ \nទូរស័ព្ទលេខ៖ ០២៣ ២១៥ ៤២៧ អ៊ីម៉ែលៈ info@teuksaat1001.com, គេហទំព័រ www.teuksaat1001.com.។",Title_nocenter_format_SR)
        worksheet.set_row(102,38)
    workbook.close()

if __name__ == '__main__':
    global Current_date
    Current_date = date(2022,6,1)
    exchange_rate = 4068
    ProvinceReport(Current_date,exchange_rate)
