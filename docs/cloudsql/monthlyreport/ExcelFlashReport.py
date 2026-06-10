import xlsxwriter
from xlsxwriter.utility import xl_range, xl_rowcol_to_cell, xl_col_to_name
import datetime
import os
from datetime import date,timedelta, datetime
from dateutil.relativedelta import *
from calendar import monthrange
import calendar
import db
import tempfile
from monthlyreport.Functionutils import translate_text


def CreatefileFlashReport(Current_date,Period):
    global workbook, worksheet_flash_report, worksheet_recap_platform
    Month = Current_date.month
    if Month < 10:
        Month = '0' + str(Month)
    else:
        Month = str(Month)
    Year = str(Current_date.year)
    if Period == "EndMonth":
        filepath = tempfile.gettempdir()+'/Flash report '+Year+'-'+Month+'.xlsx'
    else:
        filepath = tempfile.gettempdir()+'/Mid Flash report '+Year+'-'+Month+'-15'+'.xlsx'
    if os.path.exists(filepath):
       os.remove(filepath)
    workbook = xlsxwriter.Workbook(filepath)


def WriteFlashReport(Current_date,Date_likeforlike,Period):

    con = db.pool.connect()
    worksheet_flash_report = workbook.add_worksheet("FlashReport")
    worksheet_flash_report.set_zoom(70)
    worksheet_flash_report.freeze_panes(4,5)
    Comment_format = workbook.add_format({'text_wrap' : True})
    Sales_format = workbook.add_format({'num_format' : '# ##0'})
    Sales_Percentage_format = workbook.add_format({'num_format' : '+0%;-0%'})
    Site_format = workbook.add_format({'bg_color' : '#DCE6F1', 'border' : 3})

    Sales_Title_format = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    Indicator_Title_format = workbook.add_format({'bg_color':"#00B050",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    Comment_Title_format = workbook.add_format({'bg_color':"#C4E59F",'bold': True, 'text_wrap' : True,'valign':'vcenter','center_across':True})
    Sales_bold_format = workbook.add_format({'num_format' : '# ##0', 'bold' : True})
    Sales_Percentage_bold_format = workbook.add_format({'num_format' : '+0%;-0%', 'bold' : True})
    Decimal_bold_format = workbook.add_format({'num_format' : '# ##0.00', 'bold' : True})

##########SELECT DATA#########
    ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor,Sites.Last_Tier FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Platform <> 'Dead'
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(Date_likeforlike)).fetchall()
    ListOnlysiteLikeforLike = [i[0] for i in ListSite_LikeforLike]
    ListSite_notLikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor,Sites.Last_Tier
                                                FROM Sites
                                                WHERE 1 = %s AND Sites.Id_Site NOT IN %s AND Platform <> 'Dead'
                                                ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(1,ListOnlysiteLikeforLike)).fetchall()
    ListSiteActive = ListSite_LikeforLike + ListSite_notLikeforLike
    
    query = con.execute("SELECT Id_Site,Number_jugs_school, Number_jugs_village,Comment,Open_days,Number_bot_displace_people FROM FlashReport WHERE Month = %s AND Period = %s",(Current_date,Period))
    allFlashReport = query.fetchall()
    # query = con.execute("SELECT Platform, Advisor, Population, Family,Last_Tier, Id_Site,Project FROM Sites")
    # allSiteInfo = query.fetchall()
    query = con.execute("SELECT Total_Sales - Bottle_Sales, Number_open_days,Id_Site, Total_Sales - Bottle_Sales - WiS_Sales FROM Sales WHERE Month = %s",(Current_date-relativedelta(months=+ 12)))
    allSales_N_1 = query.fetchall()
    query = con.execute("SELECT Total_Sales - Bottle_Sales, Number_open_days,Id_Site, Total_Sales - Bottle_Sales - WiS_Sales FROM Sales WHERE Month = %s",(Current_date-relativedelta(months=+ 24)))
    allSales_N_2 = query.fetchall()

##########WRITE TITLE########
    ColumnTitle=0
    worksheet_flash_report.write(3,ColumnTitle,"LfL",Site_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Site",Site_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,9)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Platform",Site_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Advisor",Site_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Tier",Site_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,12)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Sales (bot) exc. WinS",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Sales (bot) exc. WinS N-1",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20,None,{'level':1,'hidden':True})
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"vs N-1",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Sales (bot) WinS",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20,None,{'level':1,'hidden':True})
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Sales (bot) inc. WinS",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20,None,{'level':1,'hidden':True})
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Bot/day inc. WinS",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Bot/day inc. WinS N-1",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20,None,{'level':1,'hidden':True})
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Bot/day inc. WinS N-2",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20,None,{'level':1,'hidden':True})
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"vs N-1",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Bot/day exc. WinS",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Bot/day exc. WinS N-1",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20,None,{'level':1,'hidden':True})
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Bot/day exc. WinS N-2",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20,None,{'level':1,'hidden':True})
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"vs N-1",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Nb working day",Indicator_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,20)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Bot displace people",Sales_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,30)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Comments",Comment_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,30)
    ColumnTitle +=1
    worksheet_flash_report.write(3,ColumnTitle,"Comments (english only)",Comment_Title_format)
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,30)
    ColumnTitle +=1
    worksheet_flash_report.set_column(ColumnTitle,ColumnTitle,None,None,{'hidden':True})

    worksheet_flash_report.autofilter(3,0,len(ListSiteActive)+4,ColumnTitle)
    worksheet_flash_report.write(0,3,'Like for Like',Sales_bold_format)
    worksheet_flash_report.write(1,3,'Others',Sales_bold_format)
    worksheet_flash_report.write(2,3,'Total',Sales_bold_format)

#########WRITE DATA########
    for i in range(len(ListSiteActive)):
        Column =0
        if Period == "MidMonth":
            CoefficientPeriod = 30/14
        else:
            CoefficientPeriod = 1
        # Get FlashReport data for the current site, or default to zeros
        FlashReport = next((row for row in allFlashReport if row[0] == ListSiteActive[i][0]), (0, 0, 0, 0, 0, 0))
        # Get Sales_N_1 and Sales_N_2 data for the current site, or default to zeros
        Sales_N_1 = next((row for row in allSales_N_1 if row[2] == ListSiteActive[i][0]), (0, 0, 0, 0))
        Sales_N_2 = next((row for row in allSales_N_2 if row[2] == ListSiteActive[i][0]), (0, 0, 0, 0))
        Number_days = monthrange(Current_date.year, Current_date.month)[1]

        if i < len(ListSite_LikeforLike):
            worksheet_flash_report.write(i+4,Column,"Like for Like",Sales_bold_format)
            Column +=1
        else:
            worksheet_flash_report.write(i+4,Column,"Others",Sales_bold_format)
            Column +=1
        worksheet_flash_report.write(4+i,Column,ListSiteActive[i][0])
        Column+=1
        worksheet_flash_report.write(4+i,Column,ListSiteActive[i][1])
        Column+=1
        worksheet_flash_report.write(4+i,Column,ListSiteActive[i][2])
        Column+=1
        worksheet_flash_report.write(4+i,Column,(ListSiteActive[i][3]))
        if ListSiteActive[i][3] == 'Closed' and FlashReport and FlashReport[1]:
            #worksheet_flash_report.write(4+i,1,"Project",Site_format)
            worksheet_flash_report.write(4+i,Column,"New/Reopen")
        Column+=1
        worksheet_flash_report.write(4+i,Column,FlashReport[2],Sales_format)
        ColumnSalesexcWinS = Column
        Column+=1
        worksheet_flash_report.write(4+i,Column,Sales_N_1[3]/CoefficientPeriod,Sales_format)
        ColumnSalesexcWinS_lastyear = Column
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,'IFERROR((%s%s/%s%s)-1,"")'%(xl_col_to_name(ColumnSalesexcWinS),5+i,xl_col_to_name(ColumnSalesexcWinS_lastyear),5+i),Sales_Percentage_format)
        Column+=1
        worksheet_flash_report.write(4+i,Column,FlashReport[1],Sales_format)
        Column+=1
        worksheet_flash_report.write(4+i,Column,FlashReport[1]+FlashReport[2],Sales_format)
        ColumnSalesincWinS = Column
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,"=IFERROR((%s+%s)/%s,\"\")"%(FlashReport[1],FlashReport[2],FlashReport[4]),Sales_format)
        ColumnbotdayincWinS = Column
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,"=IFERROR(%s/%s,\"\")"%(Sales_N_1[0],Sales_N_1[1]),Sales_format)
        ColumnbotdayincWinS_lastyear = Column
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,"=IFERROR(%s/%s,\"\")"%(Sales_N_2[0],Sales_N_2[1]),Sales_format)
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,'IFERROR((%s%s/%s%s)-1,"")'%(xl_col_to_name(ColumnbotdayincWinS),5+i,xl_col_to_name(ColumnbotdayincWinS_lastyear),5+i),Sales_Percentage_format)
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,"=IFERROR(%s/%s,\"\")"%(FlashReport[2],FlashReport[4]),Sales_format)
        ColumnbotdayexcWinS = Column
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,"=IFERROR(%s/%s,\"\")"%(Sales_N_1[3],Sales_N_1[1]),Sales_format)
        ColumnbotdayexcWinS_lastyear = Column
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,"=IFERROR(%s/%s,\"\")"%(Sales_N_2[3],Sales_N_2[1]),Sales_format)
        Column+=1
        worksheet_flash_report.write_formula(4+i,Column,'IFERROR((%s/%s)-1,"")'%(xl_rowcol_to_cell(4+i,ColumnbotdayexcWinS),xl_rowcol_to_cell(4+i,ColumnbotdayexcWinS_lastyear)),Sales_Percentage_format)
        Column+=1
        worksheet_flash_report.write(4+i,Column,FlashReport[4])
        Column+=1
        worksheet_flash_report.write(4+i,Column,FlashReport[5])
        Column+=1
        if FlashReport[3] and FlashReport[3] != '0':
            worksheet_flash_report.write(4+i,Column,FlashReport[3],Comment_format)
            Column+=1
            # worksheet_flash_report.write(4+i,Column,translate_text("en",FlashReport[3]),Comment_format)
            Column+=1
        else:
            Column+=1
            Column+=1

        worksheet_flash_report.write_formula(i+4,Column,"SUBTOTAL(3,A%s)"%(i+(8)))
        LastColumnforFormula = Column
        Column +=1

    

    ColumnSum = 5

    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Others")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(9,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Others")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(9,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(%s1/%s1-1,0)'%(xl_col_to_name(ColumnSalesexcWinS),xl_col_to_name(ColumnSalesexcWinS_lastyear)),Sales_Percentage_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(%s2/%s2-1,0)'%(xl_col_to_name(ColumnSalesexcWinS),xl_col_to_name(ColumnSalesexcWinS_lastyear)),Sales_Percentage_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnSalesexcWinS),xl_col_to_name(ColumnSalesexcWinS_lastyear)),Sales_Percentage_bold_format)
    ColumnSum +=1
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Others")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(9,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Others")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(9,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Like for Like",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Others",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(1,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Like for Like",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Others",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(1,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Like for Like",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Others",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(1,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(%s1/%s1-1,0)'%(xl_col_to_name(ColumnbotdayincWinS),xl_col_to_name(ColumnbotdayincWinS_lastyear)),Sales_Percentage_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(%s2/%s2-1,0)'%(xl_col_to_name(ColumnbotdayincWinS),xl_col_to_name(ColumnbotdayincWinS_lastyear)),Sales_Percentage_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnbotdayincWinS),xl_col_to_name(ColumnbotdayincWinS_lastyear)),Sales_Percentage_bold_format)
    ColumnSum +=1
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Like for Like",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Others",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(1,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Like for Like",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Others",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(1,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Like for Like",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(AVERAGEIFS(%s5:%s%s,A5:A%s,"Others",%s5:%s%s,1),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(LastColumnforFormula),xl_col_to_name(LastColumnforFormula),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(1,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(%s1/%s1-1,0)'%(xl_col_to_name(ColumnbotdayexcWinS),xl_col_to_name(ColumnbotdayexcWinS_lastyear)),Sales_Percentage_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(%s2/%s2-1,0)'%(xl_col_to_name(ColumnbotdayexcWinS),xl_col_to_name(ColumnbotdayexcWinS_lastyear)),Sales_Percentage_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(%s3/%s3-1,0)'%(xl_col_to_name(ColumnbotdayexcWinS),xl_col_to_name(ColumnbotdayexcWinS_lastyear)),Sales_Percentage_bold_format)
    ColumnSum +=1
    ColumnSum +=1
    worksheet_flash_report.write_formula(0,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Like for Like")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(1,ColumnSum,'=IFERROR(SUMPRODUCT((A5:A%s="Others")*(SUBTOTAL(9,OFFSET(%s5,ROW(%s5:%s%s)-MIN(ROW(%s5:%s%s)),0)))),0)'%(4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike),xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    worksheet_flash_report.write_formula(2,ColumnSum,'=IFERROR(SUBTOTAL(9,%s5:%s%s),0)'%(xl_col_to_name(ColumnSum),xl_col_to_name(ColumnSum),4+len(ListSite_LikeforLike)+len(ListSite_notLikeforLike)),Sales_bold_format)
    ColumnSum +=1 

def KPIFlashReport(Current_date,Date_likeforlike,Period,Column,worksheet_recap_platform,FlashReport,Title = False,hidden=False):
    con = db.pool.connect()
    Platform_format = workbook.add_format({'bold' : True, 'border' : 1, 'center_across': True})

    Sales_Title_format = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    Indicator_Title_format = workbook.add_format({'bg_color':"#00B050",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    
    Percentage_format = workbook.add_format({'num_format' : '+0%;-0%', 'border' : 1, 'italic': True})
    Dec_format = workbook.add_format({'num_format' : '# ##0.00', 'border' : 1})
    Sales_format = workbook.add_format({'num_format' : '# ##0', 'border' : 1})

    Positive_format = workbook.add_format({'num_format': '+ 0.0%', 'font_color' : '#00B050'})
    Negative_format = workbook.add_format({'num_format': '0.0%', 'font_color' : '#FF0000'})

    Sales_bold_format = workbook.add_format({'num_format' : '# ##0', 'border' : 1, 'bold' : 1})
    Dec_bold_format = workbook.add_format({'num_format' : '# ##0.00', 'border' : 1, 'bold' : 1})
    Sales_Percentage_bold_format = workbook.add_format({'num_format' : '+0%;-0%', 'border' : 1,'bold' : True})

    Date_format = workbook.add_format({'num_format' : 'mmm-yyyy', 'border' : 1, 'bold' : 1})


###########DATA SELECTION############
    if Period == "MidMonth":
        CoefficientPeriod = 2
    else:
        CoefficientPeriod = 1

    Date_janv = date(Current_date.year,1,1)


    ListPlatform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform IS NOT NULL AND Platform <> 'Dead'""").fetchall()
    ListPlatform = [i[0] for i in ListPlatform] + ["Total"]

    ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor,Sites.Last_Tier FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Platform <> 'Dead'
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(Date_likeforlike)).fetchall()
    ListOnlysiteLikeforLike = [i[0] for i in ListSite_LikeforLike]

    if FlashReport == True: #Check if we take data from Flash Report or from monthly report
        
        #Total data
        allSales = con.execute("""SELECT Platform,COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s
                                    GROUP BY Platform""",(Current_date,Period)).fetchall()
        allSales_Total = con.execute("""SELECT DISTINCT "Total",COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s
                                    """,(Current_date,Period)).fetchall()
        allSales = allSales + allSales_Total

        #Like for like data
        allSales_LfL = con.execute("""SELECT Platform,COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s AND FlashReport.Id_Site IN %s
                                    GROUP BY Platform""",(Current_date,Period,ListOnlysiteLikeforLike)).fetchall()

        allSales_Total_LfL = con.execute("""SELECT DISTINCT "Total",COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s AND FlashReport.Id_Site IN %s
                                    """,(Current_date,Period,ListOnlysiteLikeforLike)).fetchall()
        allSales_LfL = allSales_LfL + allSales_Total_LfL

    else:
        #Total data
        allSales = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s
                                    GROUP BY Platform""",(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date)).fetchall()

        allSales_Total = con.execute("""SELECT DISTINCT "Total",COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s
                                    """,(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date)).fetchall()
        allSales = allSales + allSales_Total

        #Like for like data
        allSales_LfL = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s AND Sales.Id_Site IN %s
                                    GROUP BY Platform""",(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date,ListOnlysiteLikeforLike)).fetchall()

        allSales_Total_LfL = con.execute("""SELECT DISTINCT "Total",COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s AND Sales.Id_Site IN %s
                                    """,(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date,ListOnlysiteLikeforLike)).fetchall()

        allSales_LfL = allSales_LfL + allSales_Total_LfL

    #Total Data rest of the other month of the year
    allSales_restYTD = con.execute("""SELECT Platform,IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s 
                                        GROUP BY Platform""",(Date_janv,Current_date)).fetchall()
    allSales_restYTD_Total = con.execute("""SELECT "Total",IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s""",(Date_janv,Current_date)).fetchall()

    allSales_restYTD = allSales_restYTD + allSales_restYTD_Total

    #Like for like data
    allSales_restYTD_LfL = con.execute("""SELECT Platform,IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s AND Sales.Id_Site IN %s
                                        GROUP BY Platform""",(Date_janv,Current_date,ListOnlysiteLikeforLike)).fetchall()

    allSales_restYTD_Total_LfL = con.execute("""SELECT "Total",IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s AND Sales.Id_Site IN %s
                                        """,(Date_janv,Current_date,ListOnlysiteLikeforLike)).fetchall()
    

    allSales_restYTD_LfL = allSales_restYTD_LfL + allSales_restYTD_Total_LfL

########WRITE TITLE##########
    if Title == True:
        worksheet_recap_platform.set_column('A:A',37.44)
        
        LineTitle =2
        worksheet_recap_platform.write(LineTitle,Column,'Nb Sites Opened',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles - inc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Average Bottles/day - inc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Average Bottles/day - exc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles - exc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles LfL - exc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles YTD - exc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles YTD LfL - exc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Average nb Working Days',Indicator_Title_format)
        LineTitle +=1
    worksheet_recap_platform.merge_range(0,Column+1,0,Column+len(ListPlatform),Current_date.year,Sales_Title_format)
    if hidden:
        worksheet_recap_platform.set_column(Column+1,Column+len(ListPlatform)-1,None,None,{'level':1,'hidden':True})

########WRITE DATA#########
    for i in range(len(ListPlatform)):

        if ListPlatform[i] == "Total":
            Sales_format = workbook.add_format({'num_format' : '# ##0', 'border' : 1, 'bold' : 1})
            Dec_format = workbook.add_format({'num_format' : '# ##0.00', 'border' : 1, 'bold' : 1})
            Percentage_format = workbook.add_format({'num_format' : '+0%;-0%', 'border' : 1,'bold' : True})

        Sales = list(filter(lambda row: row[0] == ListPlatform[i], allSales)) or [(0,0,0,0,0)]
        Sales_LfL = list(filter(lambda row: row[0] == ListPlatform[i], allSales_LfL)) or [(0,0,0,0,0)]
        Sales_restYTD = list(filter(lambda row: row[0] == ListPlatform[i], allSales_restYTD)) or [(0,0,0,0,0)]
        Sales_restYTD_LfL = list(filter(lambda row: row[0] == ListPlatform[i], allSales_restYTD_LfL)) or [(0,0,0,0,0)]


        cellplatform = xl_rowcol_to_cell(1,i+1)
        Line = 1
        worksheet_recap_platform.write(Line,i+1+Column,ListPlatform[i],Platform_format)
        LineTitle = Line
        Line+=1
        worksheet_recap_platform.write(Line,i+1+Column,Sales[0][1],Sales_format)
        LineSiteOpen = Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=%s+%s"%(Sales[0][2],Sales[0][3]),Sales_format)
        LineBotSold = Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR((%s+%s)/(%s),\"\")"%(Sales[0][2],Sales[0][3],Sales[0][4]),Sales_format)
        LineAvgBotDay= Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR(%s/(%s),\"\")"%(Sales[0][2],Sales[0][4]),Sales_format)
        LineAvgBotDay_NoWinS= Line
        Line+=1
        worksheet_recap_platform.write(Line,i+1+Column,Sales[0][2],Sales_format)
        LineBotSold_WinS = Line
        Line+=1
        worksheet_recap_platform.write(Line,i+1+Column,Sales_LfL[0][2],Sales_format)
        LineBotSold_WinS = Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=%s+%s"%(Sales[0][2],Sales_restYTD[0][1]),Sales_format)
        LineBotSold_WinS = Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=%s+%s"%(Sales_LfL[0][2],Sales_restYTD_LfL[0][1]),Sales_format)
        LineBotSold_WinS = Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR(%s/(%s),\"\")"%(Sales[0][4],Sales[0][1]),Dec_format)
        LineAvgBotDay_NoWinS= Line
        Line+=1

def KPIEvolFlashReport(Current_date,Date_likeforlike,Period,Column,worksheet_recap_platform,FlashReport,Title = False,hidden=False):
    con = db.pool.connect()
    Platform_format = workbook.add_format({'bold' : True, 'border' : 1, 'center_across': True})

    Sales_Title_format = workbook.add_format({'bg_color':"#0070C0",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    Indicator_Title_format = workbook.add_format({'bg_color':"#00B050",'bold': True, 'text_wrap' : True,'font_color':'white','valign':'vcenter','center_across':True})
    
    Percentage_format = workbook.add_format({'num_format' : '+0%;-0%', 'border' : 1, 'italic': True})
    Dec_format = workbook.add_format({'num_format' : '# ##0.00', 'border' : 1})
    Sales_format = workbook.add_format({'num_format' : '# ##0', 'border' : 1})

    Positive_format = workbook.add_format({'num_format': '+ 0.0%', 'font_color' : '#00B050'})
    Negative_format = workbook.add_format({'num_format': '0.0%', 'font_color' : '#FF0000'})

    Sales_bold_format = workbook.add_format({'num_format' : '# ##0', 'border' : 1, 'bold' : 1})
    Dec_bold_format = workbook.add_format({'num_format' : '# ##0.00', 'border' : 1, 'bold' : 1})
    Sales_Percentage_bold_format = workbook.add_format({'num_format' : '+0%;-0%', 'border' : 1,'bold' : True})

    Date_format = workbook.add_format({'num_format' : 'mmm-yyyy', 'border' : 1, 'bold' : 1})


###########DATA SELECTION############
    if Period == "MidMonth":
        CoefficientPeriod = 2
    else:
        CoefficientPeriod = 1

    Date_janv = date(Current_date.year,1,1)

    ListPlatform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform IS NOT NULL AND Platform <> 'Dead'""").fetchall()
    ListPlatform = [i[0] for i in ListPlatform] + ["Total"]

    ListSite_LikeforLike = con.execute("""SELECT DISTINCT Sites.Id_Site,Sites.Old_Platform,Sites.Advisor,Sites.Last_Tier FROM Sites 
                                            WHERE Sites.Id_Site IN 
                                                (SELECT DISTINCT Id_Site FROM Sales WHERE Month = %s AND Total_Sales IS NOT NULL) 
                                            AND Platform <> 'Dead'
                                            ORDER BY Left(Sites.Id_Site,1),LENGTH(Sites.Id_Site),Sites.Id_Site""",(Date_likeforlike)).fetchall()
    ListOnlysiteLikeforLike = [i[0] for i in ListSite_LikeforLike]

    if FlashReport == True: #Check if we take data from Flash Report or from monthly report

        #Total data
        allSales = con.execute("""SELECT Platform,COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s
                                    GROUP BY Platform""",(Current_date,Period)).fetchall()
        allSales_Total = con.execute("""SELECT DISTINCT "Total",COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s
                                    """,(Current_date,Period)).fetchall()
        allSales = allSales + allSales_Total

        #Like for like data
        allSales_LfL = con.execute("""SELECT Platform,COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s AND FlashReport.Id_Site IN %s
                                    GROUP BY Platform""",(Current_date,Period,ListOnlysiteLikeforLike)).fetchall()

        allSales_Total_LfL = con.execute("""SELECT DISTINCT "Total",COUNT(FlashReport.Id_Site),SUM(Number_jugs_village),SUM(Number_jugs_school),SUM(Open_days)
                                    FROM FlashReport INNER JOIN Sites ON Sites.Id_Site = FlashReport.Id_Site
                                    WHERE Month = %s AND Period = %s AND FlashReport.Id_Site IN %s
                                    """,(Current_date,Period,ListOnlysiteLikeforLike)).fetchall()
        allSales_LfL = allSales_LfL + allSales_Total_LfL

    else:
        #Total data
        allSales = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s
                                    GROUP BY Platform""",(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date)).fetchall()

        allSales_Total = con.execute("""SELECT DISTINCT "Total",COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s
                                    """,(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date)).fetchall()
        allSales = allSales + allSales_Total

        #Like for like data
        allSales_LfL = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s AND Sales.Id_Site IN %s
                                    GROUP BY Platform""",(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date,ListOnlysiteLikeforLike)).fetchall()

        allSales_Total_LfL = con.execute("""SELECT DISTINCT "Total",COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s AND Sales.Id_Site IN %s
                                    """,(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Current_date,ListOnlysiteLikeforLike)).fetchall()

        allSales_LfL = allSales_LfL + allSales_Total_LfL

    #Total Data rest of the other month of the year
    allSales_restYTD = con.execute("""SELECT Platform,IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s 
                                        GROUP BY Platform""",(Date_janv,Current_date)).fetchall()
    allSales_restYTD_Total = con.execute("""SELECT "Total",IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s""",(Date_janv,Current_date)).fetchall()

    allSales_restYTD = allSales_restYTD + allSales_restYTD_Total

    #Like for like data
    allSales_restYTD_LfL = con.execute("""SELECT Platform,IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s AND Sales.Id_Site IN %s
                                        GROUP BY Platform""",(Date_janv,Current_date,ListOnlysiteLikeforLike)).fetchall()

    allSales_restYTD_Total_LfL = con.execute("""SELECT "Total",IFNULL(SUM(Total_Sales-Bottle_Sales-WiS_Sales),0),SUM(Total_Sales-Bottle_Sales)
                                        FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                        WHERE Month >= %s AND Month < %s AND Sales.Id_Site IN %s
                                        """,(Date_janv,Current_date,ListOnlysiteLikeforLike)).fetchall()
    

    allSales_restYTD_LfL = allSales_restYTD_LfL + allSales_restYTD_Total_LfL


    #DATA LAST YEAR 
    Date_N_1 = Current_date - relativedelta(months=+12)
    Date_janv_N_1 = Date_janv - relativedelta(months=+12)

    #Date per platform
    allSales_N_1 = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s
                                    GROUP BY Platform""",(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Date_N_1)).fetchall()
    
    allSales_N_1_restYTD = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),IFNULL(SUM(Total_Sales - Bottle_Sales-WiS_Sales),0),SUM(WiS_Sales),SUM(Number_Open_Days)
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month >= %s AND Month < %s
                                    GROUP BY Platform""",(Date_janv_N_1,Date_N_1)).fetchall()
    
    allSales_N_1_LfL = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),IFNULL(SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,0),SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s AND Sales.Id_Site IN %s
                                    GROUP BY Platform""",(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Date_N_1,ListOnlysiteLikeforLike)).fetchall()

    allSales_N_1_LfL_YTD = con.execute("""SELECT Platform,COUNT(Sales.Id_Site),IFNULL(SUM(Total_Sales - Bottle_Sales-WiS_Sales),0),SUM(WiS_Sales),SUM(Number_Open_Days)
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month >= %s AND Month < %s AND Sales.Id_Site IN %s
                                    GROUP BY Platform""",(Date_janv_N_1,Date_N_1,ListOnlysiteLikeforLike)).fetchall()

    #Data total
    allSales_N_1_Total = con.execute("""SELECT "Total",COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s
                                    """,(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Date_N_1)).fetchall()
    
    allSales_N_1_restYTD_Total = con.execute("""SELECT "Total",COUNT(Sales.Id_Site),IFNULL(SUM(Total_Sales - Bottle_Sales-WiS_Sales),0),SUM(WiS_Sales),SUM(Number_Open_Days)
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month >= %s AND Month < %s
                                    """,(Date_janv_N_1,Date_N_1)).fetchall()
    
    allSales_N_1_LfL_Total = con.execute("""SELECT "Total",COUNT(Sales.Id_Site),SUM(Total_Sales - Bottle_Sales-WiS_Sales)/%s,SUM(WiS_Sales)/%s,SUM(Number_Open_Days)/%s
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month = %s AND Sales.Id_Site IN %s
                                    """,(CoefficientPeriod,CoefficientPeriod,CoefficientPeriod,Date_N_1,ListOnlysiteLikeforLike)).fetchall()

    allSales_N_1_LfL_YTD_Total = con.execute("""SELECT "Total",COUNT(Sales.Id_Site),IFNULL(SUM(Total_Sales - Bottle_Sales-WiS_Sales),0),SUM(WiS_Sales),SUM(Number_Open_Days)
                                    FROM Sales INNER JOIN Sites ON Sites.Id_Site = Sales.Id_Site 
                                    WHERE Month >= %s AND Month < %s AND Sales.Id_Site IN %s
                                    """,(Date_janv_N_1,Date_N_1,ListOnlysiteLikeforLike)).fetchall()

    allSales_N_1 = allSales_N_1 + allSales_N_1_Total
    allSales_N_1_restYTD = allSales_N_1_restYTD + allSales_N_1_restYTD_Total
    allSales_N_1_LfL = allSales_N_1_LfL + allSales_N_1_LfL_Total
    allSales_N_1_LfL_YTD = allSales_N_1_LfL_YTD + allSales_N_1_LfL_YTD_Total

########WRITE TITLE##########
    if Title == True:
        worksheet_recap_platform.set_column('A:A',37.44)
        
        LineTitle =2
        worksheet_recap_platform.write(LineTitle,Column,'Nb Sites Opened',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles - inc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles - WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Total Bottles - exc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Average Bottles/day - inc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Average Bottles/day - exc. WinS',Sales_Title_format)
        LineTitle +=1
        worksheet_recap_platform.write(LineTitle,Column,'Average nb Working Days',Indicator_Title_format)
        LineTitle +=1
    worksheet_recap_platform.merge_range(0,Column+1,0,Column+len(ListPlatform),"%s vs %s"%((Current_date - relativedelta(months=+12)).year,Current_date.year),Indicator_Title_format)
    if hidden:
        worksheet_recap_platform.set_column(Column+1,Column+len(ListPlatform)-1,None,None,{'level':1,'hidden':True})

########WRITE DATA#########
    for i in range(len(ListPlatform)):

        if ListPlatform[i] == "Total":
            Sales_format = workbook.add_format({'num_format' : '# ##0', 'border' : 1, 'bold' : 1})
            Dec_format = workbook.add_format({'num_format' : '# ##0.00', 'border' : 1, 'bold' : 1})
            Percentage_format = workbook.add_format({'num_format' : '+0%;-0%', 'border' : 1,'bold' : True})

        Sales = list(filter(lambda row: row[0] == ListPlatform[i], allSales)) or [(0,0,0,0,0)]
        Sales_LfL = list(filter(lambda row: row[0] == ListPlatform[i], allSales_LfL)) or [(0,0,0,0,0)]
        Sales_restYTD = list(filter(lambda row: row[0] == ListPlatform[i], allSales_restYTD)) or [(0,0,0,0,0)]
        Sales_restYTD_LfL = list(filter(lambda row: row[0] == ListPlatform[i], allSales_restYTD_LfL)) or [(0,0,0,0,0)]

        Sales_N_1 = list(filter(lambda row: row[0] == ListPlatform[i], allSales_N_1)) or [(0,0,0,0,0)]
        Sales_N_1_restYTD = list(filter(lambda row: row[0] == ListPlatform[i], allSales_N_1_restYTD)) or [(0,0,0,0,0)]
        Sales_N_1_LfL = list(filter(lambda row: row[0] == ListPlatform[i], allSales_N_1_LfL)) or [(0,0,0,0,0)]
        Sales_N_1_LfL_YTD = list(filter(lambda row: row[0] == ListPlatform[i], allSales_N_1_LfL_YTD)) or [(0,0,0,0,0)]

        cellplatform = xl_rowcol_to_cell(1,i+1)
        Line = 1
        worksheet_recap_platform.write(Line,i+1+Column,ListPlatform[i],Platform_format)
        LineTitle = Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR(%s-%s,\"\")"%(Sales[0][1],Sales_N_1[0][1]),Sales_format)
        LineSiteOpen = Line
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR((%s+%s)/%s-1,\"\")"%(Sales[0][2],Sales[0][3],Sales_N_1[0][2]+Sales_N_1[0][3]),Percentage_format)
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR(((%s+%s)/%s)/((%s+%s)/%s)-1,\"\")"%(Sales[0][2],Sales[0][3],Sales[0][4],Sales_N_1[0][2],Sales_N_1[0][3],Sales_N_1[0][4]),Percentage_format)
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR((%s/%s)/(%s/%s)-1,\"\")"%(Sales[0][2],Sales[0][4],Sales_N_1[0][2],Sales_N_1[0][4]),Percentage_format)
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR(%s/%s-1,\"\")"%(Sales[0][2],Sales_N_1[0][2]),Percentage_format)
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR(%s/%s-1,\"\")"%(Sales_LfL[0][2],Sales_N_1_LfL[0][2]),Percentage_format)
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR((%s+%s)/%s-1,\"\")"%(Sales[0][2],Sales_restYTD[0][1],Sales_N_1[0][2]+Sales_N_1_restYTD[0][2]),Percentage_format)
        Line+=1
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR((%s+%s)/%s-1,\"\")"%(Sales_LfL[0][2],Sales_restYTD_LfL[0][1],Sales_N_1_LfL[0][2]+Sales_N_1_LfL_YTD[0][2]),Percentage_format)
        Line+=1        
        worksheet_recap_platform.write_formula(Line,i+1+Column,"=IFERROR((%s/%s)/(%s/%s)-1,\"\")"%(Sales[0][4],Sales[0][1],Sales_N_1[0][4],Sales_N_1[0][1]),Percentage_format)
        Line+=1

def LaunchExcelCreationFlashReport(Current_date,Period):
    con = db.pool.connect()
    Date_janv = date(Current_date.year,1,1)
    Date_likeforlike = date(Current_date.year-1,1,1)

    CreatefileFlashReport(Current_date,Period)
    WriteFlashReport(Current_date,Date_likeforlike,Period)
    worksheet = workbook.add_worksheet("Recap")
    ListPlatform = con.execute("""SELECT DISTINCT Platform FROM Sites WHERE Platform IS NOT NULL AND Platform <> 'Dead'""").fetchall()
    KPIFlashReport(Current_date,Date_likeforlike,Period,0,worksheet,True,True,False)
    KPIFlashReport(Current_date-relativedelta(months=+12),Date_likeforlike,Period,len(ListPlatform)+2,worksheet,False,False,True)
    #KPIFlashReport(Current_date-relativedelta(months=+24),Date_likeforlike,Period,(len(ListPlatform)+2)*2,worksheet,False,False,True)
    KPIEvolFlashReport(Current_date,Date_likeforlike,Period,(len(ListPlatform)+2)*2,worksheet,True,False,True)
    #KPIEvolFlashReport(Current_date-relativedelta(months=+12),Date_likeforlike,Period,(len(ListPlatform)+2)*4+1,worksheet,False,False,True)
    
    workbook.close()
