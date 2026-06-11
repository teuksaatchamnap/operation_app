<?php

namespace App\Console\Commands;

use App\Models\Configuration;
use Illuminate\Console\Command;

class problemList extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'config:problem-list';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Command description';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        Configuration::create([
            "app" => "technical",
            "name" => "rtlist",
            "value" => '[
              {
                       "problem": "Power Failure",
                       "sub_problem": [
                           { "name": "Repair or replace battery" },
                           { "name": "Repair or replace inverter DC to AC" },
                       ],
                       "solution_list":[
                           {"solution":"Repair or replace battery "},
                           {"solution":"Repair or replace inverter DC to AC"},	 
                     ]
                },
 {
                       "problem": "Solar Failure",
                       "sub_problem": [
                           { "name": "Cabling connection" },
                           { "name": "Charge or replace controller" },
                           { "name": "Solar panel cleaning" }
                       ],
                       "solution_list":[
                           {"solution":"Repair or replace battery "},
                           {"solution":"Repair or replace inverter DC to AC"},
                           {"solution":"Solar panel cleaning"},	 
                     ]
                },
 {
                       "problem": "RT_plan",
                       "sub_problem": [
                           { "name": "Routing plan" },
                       ],
                       "solution_list":[
                           {"solution":"Routing plan "},	 
                     ]
                },	
 {
                       "problem": "Alert_WQ",
                       "sub_problem": [
                           { "name": "Alert_WQ" },
                       ],
                       "solution_list":[
                           {"solution":"Alert_WQ"},	 
                     ]
                }, 
 {
                       "problem": "Other",
                       "sub_problem": [
                           { "name": "Other" },
                       ],
                       "solution_list":[
                           {"solution":"Other"},	 
                     ]
                }, 
 {
                       "problem": "Machine_Not_Work",
                       "sub_problem": [
                           { "name": "Repair or replacement raw water pump" },
                           { "name": "Repair or replace Micro-filter pump" },
                           { "name": "UV lamp replacement" },
                           { "name": "UV quartz sleeve replacement" },
                           { "name": "UV control box repair" },
                           { "name": "Repair or replace UV ballast" }
                       ],
                       "solution_list":[
                           {"solution":"Repair or replacement raw water pump"},
                           {"solution":"Repair or replace Micro-filter pump"},
                           {"solution":"UV lamp replacement"},
                           {"solution":"UV quartz sleeve replacement"},
                           {"solution":"UV control box repair"},
                           {"solution":"Repair or replace UV ballast"}	 
                     ]
                },
 {
                       "problem": "Water_Quality",
                       "sub_problem": [
                           { "name": "Re-adjustment the flocculation" },
                           { "name": "Resin or activated carbon regeneration" },
                           { "name": "Add resin or activated carbon" },
                           { "name": "Pre-filtration flow rate adjustment" },
                           { "name": "Backwashing sand, resin, activated carbon filter" },
                           { "name": "Technical and WQ training" },
                       ],
                       "solution_list":[
                           {"solution":"Re-adjustment the flocculation"},
                           {"solution":"Resin or activated carbon regeneration"},
                           {"solution":"Add resin or activated carbon"},
                           {"solution":"Pre-filtration flow rate adjustment"},
                           {"solution":"Backwashing sand, resin, activated carbon filter"},
                           {"solution":"Technical and WQ training"}	 
                     ]
                },
 {
                       "problem": "បញ្ហាប្រភពទឹក/Water Source",
                       "sub_problem": [
                           { "name": "កង្វះប្រភពទឹក/Water scarcity" },
                           { "name": "ប្រភពទឹកប្រែប្រួល" },
                           { "name": "ម៉ូទ័របូមទឹកឆៅខូច/Raw Water Pump Broken" }  
                       ],
                       "solution_list":[
                           {"solution":"ស្វែងរកប្រភពទឹកថ្មី/Find New Water Source"},
                           {"solution":"កែប្រែគុណភាពទឹក/Improve Water Quality"},
                           {"solution":"ដូរប្រភពទឹកថ្មី/Change New Water Source"}, 
                           {"solution":"ជួសជុល/Repair"}, 
                           {"solution":"ដូរថ្មី/Change New One"}
                     ]
                },
 {
                       "problem": "បញ្ហាចម្រោះបឋម/Pre-treatment Problem",
                       "sub_problem": [
                           { "name": "ទឹកល្អក់" },
                           { "name": "ចម្រោះខ្សាច់មិនស្អាត/Sand Filter Unclean" },
                           { "name": "ចម្រោះធ្យូងមិនស្អាត/Activated Carbon Filter Unclean" },  
                           { "name": "ចម្រោះខ្សាច់មិនស្អាត/Resin Filter Unclean" },
                           { "name": "ចម្រោះរ៉េស៊ីនមិនដំណើរការ/Sand Filter Unclean" },
                           { "name": "មានការចម្លងមេរោគ/Bacteria Contaminated" } 
                       ],
                       "solution_list":[
                           {"solution":"ធ្វើ Jar តេស្ត និងកូរពង្រងទឹក/Jar Test, Flocculation and Coagulation Process"},
                           {"solution":"លាងសម្អាតធ្យូង/Backwash Activated Carbon"},
                           {"solution":"លាងសម្អាតធ្យូង/Backwash Activated Carbon"}, 
                           {"solution":"លាងសម្អាតរ៉េស៊ីន/Backwash Resin Filter"}, 
                           {"solution":"លាងរ៉េស៊ីនអោយសកម្មឡើងវិញ/Regenerate Resin"},     
                           {"solution":"លាងសម្អាតនិងសម្លាប់មេរោគប្រព័ន្ធទាំងមូលCleaning and Disinfection the Whole System"}    
                     ]
                },
 {
                       "problem": "បញ្ហាប្រភពអគ្គិសនី&ប្រភពទឹក/Electricity and Water Source",
                       "sub_problem": [
                           { "name": "បញ្ហាផ្ទាំងសូឡារ/Solar Panel Problem" },
                           { "name": "ឧបករណ៍សាកភ្លើងសូឡារគាំង/Solar Charge Controller Error" },
                           { "name": "ឧបករណ៍បម្លែងភ្លើងមិនដំណើរការ/Inverter Error" },  
                           { "name": "ខូចដុំបញ្ជាសូឡាបូមទឹក/Solar Pump Controller Broken" },
                           { "name": "ម៉ូទ័របូមទឹកសូឡាខូច/Solar Motor Pump Broken" },
                           { "name": "អាគុយមានបញ្ហា/Battery Problem" }, 
                           { "name": "បញ្ហាភ្លើងរដ្ឋ/Electricity power supply problem" },  
                           { "name": "កង្វះប្រភពទឹក/Water scarcity" },
                           { "name": "ប្រភពទឹកប្រែប្រួល" },
                           { "name": "ម៉ូទ័របូមទឹកឆៅខូច/Raw Water Pump Broken" }
                       ],
                       "solution_list":[
                           {"solution":"សម្អាតផ្ទាំងសូឡារ/Clean Solar Panel"},
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ដូរថ្មី/Change New One"}, 
                           {"solution":"កែប្រែការកំណត់ឡើងវិញ/Reset"}, 
                           {"solution":"ជួសជុល/Repair"},     
                           {"solution":"ដូរថ្មី/Change New One"}, 
                           {"solution":"កែប្រែការកំណត់ឡើងវិញ/Reset"}, 
                           {"solution":"ជួសជុល/Repair"},     
                           {"solution":"ដូរថ្មី/Change New One"}, 
                           {"solution":"ជួសជុល/Repair"},     
                           {"solution":"ដូរថ្មី/Change New One"},
                           {"solution":"ជួសជុល/Repair"},     
                           {"solution":"ដូរថ្មី/Change New One"}, 
                           {"solution":"សម្អាតក្បាលអាគុយ/Clean Battery Lead"},
                           {"solution":"ជួសជុល/Repair"},     
                           {"solution":"ដូរថ្មី/Change New One"},  
                           {"solution":"ពិនិត្យខ្សែបណ្តាញនិងឧបករណ៍ភ្ជាប់ភ្លើង/Check electricity supply and Breaker"},
                           {"solution":"ស្វែងរកប្រភពទឹកថ្មី/Find New Water Source"},     
                           {"solution":"ដូរប្រភពទឹកថ្មី/Change New Water Source"},  
                           {"solution":"កែប្រែគុណភាពទឹក/Improve Water Quality"},     
                           {"solution":"ដូរប្រភពទឹកថ្មី/Change New Water Source"},
                           {"solution":"ជួសជុល/Repair"},     
                           {"solution":"ដូរថ្មី/Change New One"}                 
                     ]
                },
 {
                       "problem": "បញ្ហាប្រព័ន្ធយូវី/UV System Problem",
                       "sub_problem": [
                           { "name": "មិនមានភ្លើងចូល/No Power Supply" },
                           { "name": "ខូចឧបករណ៍ចាប់សញ្ញា/Sensor Broken" },
                           { "name": "ដាច់អំពូល/UV Lamp Broken" },  
                           { "name": "កែវស្រោបអំពូលស្រអាប់/UV Quartz Sleeve Stained" },
                           { "name": "បែកកែវស្រោបអំពូលយូវី/UV Quartz Sleeve Broken" },
                           { "name": "ខូចប្រអប់បញ្ជា/Control Box Broken" }, 
                           { "name": "ខូចបាឡាស់/Ballas Broken" }, 
                           { "name": "ខូចឧបករណ៍បម្លែងភ្លើង/Inverter Broken" }
                       ],
                       "solution_list":[
                           {"solution":"ពិនិត្យការតភ្ជាប់ភ្លើងចូល/Check the power supply connection"},
                           {"solution":"ដូរថ្មី/Change New One"},
                           {"solution":"ដូរថ្មី/Change New One"}, 
                           {"solution":"លាងសម្អាតកែវស្រោបអំពូលយូវី/Clean the UV Quartz Sleeve"}, 
                           {"solution":"ដូរថ្មី/Change New One"},     
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ជួសជុល/Repair"}, 
                           {"solution":"កែឆ្នៃ/Modified"},     
                           {"solution":"ដូរថ្មី/Change New One"},  
                           {"solution":"ដូរថ្មី/Change New One"},     
                           {"solution":"កែបាឡាស់ថ្មី/Modify New Ballas"},     
                           {"solution":"ជួសជុល/Repair"}, 
                           {"solution":"កែឆ្នៃ/Modified"},       
                           {"solution":"ដូរថ្មី/Change New One"}   
                     ]
                },
 {
                       "problem": "ត្រួតពិនិត្យស្ថានីយ/Site Inspection",
                       "sub_problem": [
                           { "name": "ការពិនិត្យស្ថានីយប្រចាំខែ/Regular Site Check List" },
                           { "name": "ការពិនិត្យវាយតម្លៃស្ថានីយ/Site Assessment" },
                           { "name": "បើកស្ថានីយ៍ឡើងវិញ/Site reopening" }
                       ],
                       "solution_list":[
                           {"solution":"កាពន្យល់ណែនាំសហគ្រិនឡើងវិញ/Instruction and Correction"},
                           {"solution":"ពិនិត្យសម្ភារក្នុងស្ថានីយទាំងមូល/Check and assess all the materials at the Kiosk"},
                           {"solution":"បង្រៀនសហគ្រិនថ្មី/Training new entrepreneur"}	 
                     ]
                },
 {
                       "problem": "ប្រព័ន្ធសូឡារ/Solar System",
                       "sub_problem": [
                           { "name": "បញ្ហាផ្ទាំងសូឡារ/Solar Panel Problem" },
                           { "name": "ឧបករណ៍សាកភ្លើងសូឡារគាំង/Solar Charge Controller Error" },
                           { "name": "ឧបករណ៍សាកភ្លើងសូឡារខូច/Solar Charge Controller Broken" },
                           { "name": "ឧបករណ៍បម្លែងភ្លើងមិនដំណើរការ/Inverter Error" },
                           { "name": "ខូចដុំបញ្ជាសូឡាបូមទឹក/Solar Pump Controller Broken" },
                           { "name": "ម៉ូទ័របូមទឹកសូឡាខូច/Solar Motor Pump Broken" },
                           { "name": "អាគុយមានបញ្ហា/Battery Problem" },
                       ],
                       "solution_list":[
                           {"solution":"សម្អាតផ្ទាំងសូឡារ/Clean Solar Panel"},
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ដូរថ្មី/Change New One"},
                           {"solution":"កែប្រែការកំណត់ឡើងវិញ/Reset"},
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ដូរថ្មី/Change New One"},
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ដូរថ្មី/Change New One"},
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ដូរថ្មី/Change New One"},
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ដូរថ្មី/Change New One"},
                           {"solution":"ជួសជុល/Repair"},
                           {"solution":"ដូរថ្មី/Change New One"},	
                           {"solution":"សម្អាតក្បាលអាគុយ/Clean Battery Lead"},
                           {"solution":"ដូរថ្មី/Change New One"}	 
                     ]
                },
               ]'
            ]);
    }
}
