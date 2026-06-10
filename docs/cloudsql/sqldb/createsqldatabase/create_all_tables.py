import db
def create_database_struct():
    con = db.pool.connect()

    # Create database has to be done manually using google cloud console

    con.execute("CREATE TABLE Sites("
                "Id_Site VARCHAR(255) PRIMARY KEY,"
                "Platform VARCHAR(255),"
                "Old_Platform VARCHAR(255),"
                "Province VARCHAR(255),"
                "Advisor VARCHAR(255),"
                "Business_Manager VARCHAR(255),"
                "Wave VARCHAR(255),"
                "Population FLOAT(15),"
                "Family FLOAT(15),"
                "Longi FLOAT(15),"
                "Lati FLOAT(15),"
                "Code_Province VARCHAR(255),"
                "Advisor_first_semester VARCHAR(255),"
                "Advisor_second_semester VARCHAR(255),"
                "Last_Tier VARCHAR(255),"
                "Population5km FLOAT(15),"
                "Opened_month_last_12months FLOAT(15),"
                "Opened_day_this_year FLOAT(15),"
                "Debt FLOAT(15),"
                "SchoolSalesBudget FLOAT(15),"
                "SalesPrevision FLOAT(15),"
                "NumberStudentsWinS FLOAT(15),"
                "NumberSchoolsWinS FLOAT(15),"
                "Commune Varchar(255),"
                "District Varchar(255),"
                "Village Varchar(255),"
                "Sale_Starting_Date FLOAT(15),"
                "Building_cost FLOAT(15),"
                "Number_Village FLOAT(15),"
                "Households FLOAT(15),"
                "Female FLOAT(15),"
                "Migration FLOAT(15),"
                "Primary_School FLOAT(15),"
                "Classroom FLOAT(15),"
                "Water_Source VARCHAR(255),"
                "Land_of_kiosk VARCHAR(255),"
                "District_khmer VARCHAR(255),"
                "Commune_khmer VARCHAR(255),"
                "Province_khmer VARCHAR(255),"
                "Number_Village_5km FLOAT(15))")

    con.execute("CREATE TABLE PrevisionsSales("
                    "Code_Previsions INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Month DATETIME,"
                    "PrevisionsSalesTot FLOAT(10))")

    con.execute("CREATE TABLE Sales ("
                    "Code_Sales INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Month DATETIME,"
                    "Total_Sales FLOAT(10),"
                    "Total_Income FLOAT(10),"
                    "Total_Price_Average FLOAT(10),"
                    "Hod_Sales FLOAT(10),"
                    "Hod_Income FLOAT(10),"
                    "Hod_Price FLOAT(10),"
                    "Shopkeeper_Sales FLOAT(10),"
                    "Shopkeeper_Income FLOAT(10),"
                    "Shopkeeper_Price FLOAT(10),"
                    "WiS_Sales FLOAT(10),"
                    "WiS_Income FLOAT(10),"
                    "WiS_Price FLOAT(10),"
                    "Onsite_Sales FLOAT(10),"
                    "Onsite_Income FLOAT(10),"
                    "Onsite_Price FLOAT(10),"
                    "Free_Sales FLOAT(10),"
                    "Bottle_Sales FLOAT(10),"
                    "Bottle_Income FLOAT(10),"
                    "Bottle_Price FLOAT(10),"
                    "Number_Open_Days INT,"
                    "Other_Price FLOAT(10),"
                    "Other_Income FLOAT(10),"
                    "Other_Sales FLOAT(10),"
                    "Tier VARCHAR(255),"
                    "Project Boolean,"
                    "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE TABLE Beneficiaries("
                   "Code_Beneficiaries INT AUTO_INCREMENT PRIMARY KEY,"
                   "Id_Site VARCHAR(255),"
                   "Month DATETIME,"
                   "Beneficiaries FLOAT(10),"
                   "Beneficiaries12months FLOAT(10),"
                   "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE TABLE Expenses("
                    "Code_expenses INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Month DATETIME,"
                    "Ref_expenses VARCHAR(255),"
                    "Amount_expenses FLOAT(10),"
                    "Paid FLOAT(10),"
                    "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE TABLE Indicators("
                    "Code_Indicator INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Month DATETIME,"
                    "Number_of_Operator INT,"
                    "Number_Bottles_in_Operation INT,"
                    "Number_Bottles_in_Stock INT,"
                    "Number_Bottles_Broken_Lost INT,"
                    "Number_of_disinfection INT,"
                    "Number_of_delivery INT,"
                    "Water_Consume FLOAT(10),"
                    "Number_of_Vehicle INT,"
                    "Water_begining INT,"
                    "Water_end INT,"
                    "Machine_begining INT,"
                    "Saving_outside_TS INT,"
                    "Machine_end INT,"
                    "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE TABLE DailySales("
                    "Code_Daily INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Month DATETIME,"
                    "Day DATETIME,"
                    "Total_Sales FLOAT(10),"
                    "Hod_Sales FLOAT(10),"
                    "Shopkeeper_Sales FLOAT(10),"
                    "WiS_Sales FLOAT(10),"
                    "Onsite_Sales FLOAT(10),"
                    "Free_Sales FLOAT(10),"
                    "Bottle_Sales FLOAT(10),"
                    "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE TABLE FlashReport("
                    "Code_Flash_report INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Month DATETIME,"
                    "Number_jugs_village FLOAT(15),"
                    "Number_jugs_school FLOAT(15),"
                    "Open_days FLOAT(15),"
                    "Comment VARCHAR(255),"
                    "Number_of_delivery FLOAT(15),"
                    "Number_of_deinfection FLOAT(15),"
                    "Moto_cart FLOAT(15),"
                    "Kuyon FLOAT(15),"
                    "Car FLOAT(15),"
                    "Staff FLOAT(15),"
                    "Change_entrepreneur VARCHAR(255),"
                    "Entrepreneur_name VARCHAR(255),"
                    "Entrepreneur_ID VARCHAR(255),"
                    "Phone_Number VARCHAR(255),"
                    "Car FLOAT(15),"
                    "Reason_leaving VARCHAR(255),"
                    "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")
    
    con.execute("CREATE TABLE WeeklyFlashReport("
                    "Code_Flash_report INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Month DATETIME,"
                    "Week INT,"
                    "Number_jugs_village FLOAT(15),"
                    "Number_jugs_school FLOAT(15),"
                    "Open_days FLOAT(15),"
                    "Comment VARCHAR(255),"
                    "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE TABLE Entrepreneurs("
                    "Code_Entrepreneur INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Entrepreneur_Name VARCHAR(255),"
                    "Generation VARCHAR(255),"
                    "Sex VARCHAR(255),"
                    "Date_of_Birth DATETIME,"
                    "Marriage_Status VARCHAR(255),"
                    "Age INT,"
                    "Contact VARCHAR(255),"
                    "Position VARCHAR(255),"
                    "Part_Time_Job VARCHAR(255),"
                    "Previous_Job VARCHAR(255),"
                    "Starting_Date VARCHAR(255),"
                    "Reading VARCHAR(255),"
                    "Writing VARCHAR(255),"
                    "Calculating VARCHAR(255),"
                    "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE TABLE NewEntrepreneur("
                    "Code_Entrepreneur INT AUTO_INCREMENT PRIMARY KEY,"
                    "Id_Site VARCHAR(255),"
                    "Entrepreneur_English_name VARCHAR(255),"
                    "Entrepreneur_Khmer_name VARCHAR(255),"
                    "Resignation Boolean,"
                    "Reason_leaving VARCHAR(255),"
                    "Resignation_date DATETIME,"
                    "Commune VARCHAR(255),"
                    "Date_start_working DATETIME,"
                    "Date_of_birth DATETIME,"
                    "Phone_number INT,"
                    "Second_phone_number INT,"
                    "Province VARCHAR(255),"
                    "Sex VARCHAR(255),"
                    "Education VARCHAR(255),"
                    "Previous_job VARCHAR(255))")

    con.execute("CREATE TABLE users("
                    "email VARCHAR(255) PRIMARY KEY,"
                    "permissions JSON")

    con.execute("CREATE TABLE Consumable ("
                "Code_Consumable INT AUTO_INCREMENT PRIMARY KEY,"
                "Id_Site VARCHAR(255),"
                "Month DATETIME,"
                "Date_submission DATETIME,"
                "Category INT,"
                "Item VARCHAR(255),"
                "Number_Item INT,"
                "Price_Item INT,"
                "Khmer_name VARCHAR(255),"
                "English_name VARCHAR(255),"
                "Validate Boolean,"
                "Unit VARCHAR(255),"
                "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE Table Closure("
                "Code_Closure PRIMARY KEY AUTO_INCREMENT,"
                "Id_Site VARCHAR(255),"
                "Closed Boolean,"
                "Closing_date DATETIME,"
                "Reopening_date DATETIME,"
                "Closing_reason_khmer VARCHAR(255),"
                "Closing_reason_khmer VARCHAR(255),"
                "Description VARCHAR(255),"
                "Description_english VARCHAR(255),"
                "FOREIGN KEY (Id_Site) REFERENCES Sites(Id_Site))")

    con.execute("CREATE Table Platform("
                "Code_Platform VARCHAR(255) PRIMARY KEY,"
                "Latitude FLOAT(15),"
                "Longitude FLOAT(15),"
                "Cashier VARCHAR(255),"
                "Mail_ROM VARCHAR(255))")

    con.execute("CREATE Table Quality("
                "Code_Sample INT PRIMARY KEY AUTO_INCREMENT,"
                "Id_Site VARCHAR(255),"
                "Month DATETIME,"
                "Coliform_bottle FLOAT(15),"
                "Coliform_Machine FLOAT(15),"
                "Escherichia_Bottle FLOAT(15),"
                "Escherichia_Machine FLOAT(15),"
                "Sample_source VARCHAR(255)),"
                "Safe VARCHAR(255))")

    con.execute("CREATE Table Technical("
                "Code_Intervention INT PRIMARY KEY AUTO_INCREMENT,"
                "Id_Site VARCHAR(255),"
                "Month DATETIME,"
                "Start_date DATETIME,"
                "Stop_date DATETIME,"
                "Technician_Name VARCHAR(255),"
                "Reported_by VARCHAR(255),"
                "Problem_Status VARCHAR(255),"
                "Site_problem_description VARCHAR(255),"
                "Sub_Site_problem_description VARCHAR(255),"
                "Comment VARCHAR(255),"
                "Comment_problem VARCHAR(255),"
                "Status VARCHAR(255))")
    
    con.execute("CREATE TABLE `ott` ("
                "`id` INT NOT NULL AUTO_INCREMENT ,"
                "`site` VARCHAR(10) NOT NULL ,"
                "`sensor` VARCHAR(10) NOT NULL ,"
                "`date` DATETIME NOT NULL , "
                "`value` DOUBLE NOT NULL , "
                "PRIMARY KEY (`id`))")

    con.execute("CREATE TABLE `sensors` "
                "( `id` INT NOT NULL AUTO_INCREMENT , `sensor_id` INT NOT NULL , `water` DOUBLE NOT NULL ,"
                " `electricity` DOUBLE NOT NULL , `current` DOUBLE NOT NULL , `voltage` DOUBLE NOT NULL ,"
                " `d1` BOOLEAN, `d2` BOOLEAN, `d3` BOOLEAN, "
                " `flowrate` DOUBLE NOT NULL , `received_date` DATETIME NOT NULL , PRIMARY KEY (`id`)) ENGINE = InnoDB;")

if __name__ == '__main__':
    con = db.pool.connect()

    # con.execute(ALTER TABLE sites
    #             ADD COLUMN Site_Name Varchar(255),
    #             ADD COLUMN Site_Name_Khmer Varchar(255),
    #             ADD COLUMN Longitude FLOAT(15),
    #             ADD COLUMN Latitude FLOAT(15),
    #             ADD COLUMN Village Varchar(255),
    #             ADD COLUMN Village_khmer Varchar(255),
    #             ADD COLUMN Code_Village INT,
    #             ADD COLUMN Commune Varchar(255),
    #             ADD COLUMN Commune_khmer VARCHAR(255),
    #             ADD COLUMN Code_Commune INT,
    #             ADD COLUMN District Varchar(255),
    #             ADD COLUMN District_khmer VARCHAR(255),
    #             ADD COLUMN Code_District VARCHAR(255),
    #             ADD COLUMN Province VARCHAR(255),
    #             ADD COLUMN Province_khmer VARCHAR(255),
    #             ADD COLUMN Code_Province INT,
    #             ADD COLUMN ProjectAgreement INT,
    #             ADD COLUMN Wave VARCHAR(255),
    #             ADD COLUMN Sale_Starting_Date INT,
    #             ADD COLUMN Funder_1 VARCHAR(255),
    #             ADD COLUMN Funder_2 VARCHAR(255),
    #             ADD COLUMN Funder_3 VARCHAR(255),
    #             ADD COLUMN Building_cost FLOAT(15),
    #             ADD COLUMN Number_Village FLOAT(15),
    #             ADD COLUMN Number_Family FLOAT(15),
    #             ADD COLUMN Number_Households FLOAT(15),
    #             ADD COLUMN Number_Population FLOAT(15),
    #             ADD COLUMN Number_Women FLOAT(15),
    #             ADD COLUMN Number_Migration FLOAT(15),
    #             ADD COLUMN Number_Village_5km FLOAT(15),
    #             ADD COLUMN Number_Family_5km FLOAT(15),
    #             ADD COLUMN Number_Households_5km FLOAT(15),
    #             ADD COLUMN Number_Population_5km FLOAT(15),
    #             ADD COLUMN Number_Women_5km FLOAT(15),
    #             ADD COLUMN Number_Migration_5km FLOAT(15),
    #             ADD COLUMN Number_Pagoda FLOAT(15),
    #             ADD COLUMN Number_Primary_School FLOAT(15),
    #             ADD COLUMN Land_of_kiosk VARCHAR(255),
    #             ADD COLUMN Road_Leading_to_Kiosk VARCHAR(255),
    #             ADD COLUMN Paved_Asphalt_Road FLOAT(15),
    #             ADD COLUMN Concrete_Road FLOAT(15),
    #             ADD COLUMN Laterite_Road FLOAT(15),
    #             ADD COLUMN White_Soiled_Road FLOAT(15),
    #             ADD COLUMN Water_Source VARCHAR(255),
    #             ADD COLUMN Well_Pond_Ownership VARCHAR(255),
    #             ADD COLUMN Depth_Well_Pond VARCHAR(255),
    #             ADD COLUMN Water_Source_Distance_From_Kiosk VARCHAR(255),
    #             ADD COLUMN Second_Water_Source VARCHAR(255),
    #             ADD COLUMN Well_Pond_Ownership_Second_Source VARCHAR(255),
    #             ADD COLUMN Depth_Well_Pond_Second_Source VARCHAR(255),
    #             ADD COLUMN Water_Source_Distance_From_Kiosk_Second_Source FLOAT(15),
    #             ADD COLUMN Main_Power_Source VARCHAR(255),
    #             ADD COLUMN Second_Power_Source VARCHAR(255),
    #             ADD COLUMN Type_of_Water_Tank VARCHAR(255),
    #             ADD COLUMN Monthly_Income_Average_per_Person VARCHAR(255),
    #             ADD COLUMN Labour_Market VARCHAR(255),
    #             ADD COLUMN Monthly_Income_Average_per_Worker VARCHAR(255))

    con.execute("CREATE TABLE Sites2("
                "Id_Site VARCHAR(255) PRIMARY KEY,"
                "Platform VARCHAR(255),"
                "Old_Platform VARCHAR(255),"
                "Advisor VARCHAR(255),"
                "Advisor_first_semester VARCHAR(255),"
                "Advisor_second_semester VARCHAR(255),"
                "Last_Tier VARCHAR(255),"
                "SchoolSalesBudget FLOAT(15),"
                "NumberStudentsWinS FLOAT(15),"
                "NumberSchoolsWinS FLOAT(15),"
                "Classroom FLOAT(15),"
                "Opened_month_last_12months FLOAT(15),"
                "Opened_day_this_year FLOAT(15),"
                "Site_Name Varchar(255),"
                "Site_Name_Khmer Varchar(255),"
                "Longi FLOAT(15),"
                "Lati FLOAT(15),"
                "Village Varchar(255),"
                "Village_khmer Varchar(255),"
                "Code_Village INT,"
                "Commune Varchar(255),"
                "Commune_khmer VARCHAR(255),"
                "Code_Commune INT,"
                "District Varchar(255),"
                "District_khmer VARCHAR(255),"
                "Code_District VARCHAR(255),"
                "Province VARCHAR(255),"
                "Province_khmer VARCHAR(255),"
                "Code_Province INT,"
                "ProjectAgreement INT,"
                "Wave VARCHAR(255),"
                "Sale_Starting_Date INT,"
                "Funder_1 VARCHAR(255),"
                "Funder_2 VARCHAR(255),"
                "Funder_3 VARCHAR(255),"
                "Building_cost FLOAT(15),"
                "Number_Village FLOAT(15),"
                "Number_Family FLOAT(15),"
                "Number_Households FLOAT(15),"
                "Number_Population FLOAT(15),"
                "Number_Women FLOAT(15),"
                "Number_Migration FLOAT(15),"
                "Number_Village_5km FLOAT(15),"
                "Number_Family_5km FLOAT(15),"
                "Number_Households_5km FLOAT(15),"
                "Number_Population_5km FLOAT(15),"
                "Number_Women_5km FLOAT(15),"
                "Number_Migration_5km FLOAT(15),"
                "Number_Pagoda FLOAT(15),"
                "Number_Primary_School FLOAT(15),"
                "Land_of_kiosk VARCHAR(255),"
                "Road_Leading_to_Kiosk VARCHAR(255),"
                "Paved_Asphalt_Road FLOAT(15),"
                "Concrete_Road FLOAT(15),"
                "Laterite_Road FLOAT(15),"
                "White_Soiled_Road FLOAT(15),"
                "Water_Source VARCHAR(255),"
                "Well_Pond_Ownership VARCHAR(255),"
                "Depth_Well_Pond VARCHAR(255),"
                "Water_Source_Distance_From_Kiosk VARCHAR(255),"
                "Second_Water_Source VARCHAR(255),"
                "Well_Pond_Ownership_Second_Source VARCHAR(255),"
                "Depth_Well_Pond_Second_Source VARCHAR(255),"
                "Water_Source_Distance_From_Kiosk_Second_Source FLOAT(15),"
                "Main_Power_Source VARCHAR(255),"
                "Second_Power_Source VARCHAR(255),"
                "Type_of_Water_Tank VARCHAR(255),"
                "Monthly_Income_Average_per_Person VARCHAR(255),"
                "Labour_Market VARCHAR(255),"
                "Monthly_Income_Average_per_Worker VARCHAR(255))")


