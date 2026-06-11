<template>
  <div v-if="programs">
    <div v-for="(program, index) in programs" :key="index" class="a4-page">
      <div class="certificate">
        <!-- Header Section -->
        <header class="certificate-header">
          <!-- Top Header Text -->
          <div class="header-top" style="font-family:'Khmer OS Muol Light', sans-serif;font-size: 13px;">
            <h5>ព្រះរាជាណាចក្រកម្ពុជា</h5>
            <h5>ជាតិ សាសនា ព្រះមហាក្សត្រ</h5>
          </div>
          <!-- Organization Info and Logo -->
          <div class="header-content">
            <div class="header-left">
              <img src="img/logo.png" alt="Teuk Saat 1001 Logo" class="logo" />
            </div>
            <br> <br><br><br>
            <div v-if="program.platform == 'PP' || program.platform == 'KSP'" class="header-right"
              style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
              <h3>អង្គការទឹកស្អាត ១០០១ / <span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                  1001 Organization</span></h3>
              <br>
              <p>អាស័យដ្ឋាន : ផ្ទះលេខ 100 ផ្លូវ 95 សង្កាត់បឹងត្របែក ខណ្ឌចម្ការមន ក្រុងភ្នំពេញ</p>
              <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : No 100, Street 95,
                Sangkat Boeung Trabek, Khan Chamkarmon, Phnom Penh</p>
              <p>លេខទូរស័ព្ទ (Tel) : +855 (0)23 215 427 អ៊ីំម៉ែល (Email) :<span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                  <a href="info@teuksaat1001.com">info@teuksaat1001.com</a></span></p>
              <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
                1pm-5pm)</p>
            </div>

            <div v-if="program.platform == 'KC'" class="header-right"
              style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
              <h3>អង្គការទឹកស្អាត ១០០១ / <span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                  1001 Organization</span></h3>
              <br>
              <p>អាស័យដ្ឋាន : ភូមិទី ២ សង្កាត់វាល​វង់ ក្រុងកំពង់ចាម ខេត្តកំពង់ចាម</p>
              <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : Ti 2 Village, Sangkat
                Veal Vong, Kampong Cham City, Cambodia</p>
              <p>លេខទូរស័ព្ទ (Tel) : +855 (0) 42 210 898 អ៊ីំម៉ែល (Email) : <span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                  <a href="info@teuksaat1001.com">info@teuksaat1001.com</a></span></p>
              <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
                1pm-5pm)</p>
            </div>

            <div v-if="program.platform == 'BTB'" class="header-right"
              style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
              <h3>អង្គការទឹកស្អាត ១០០១ / <span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                  1001 Organization</span></h3>
              <br>
              <p>អាស័យដ្ឋាន : អាស័យដ្ឋាន : ផ្ទះលេខ ៦៧៦​ ក្រុមទី ១៥​ ភូមិអូរតាគាំ១ សង្កាត់ទួលតាឯក ក្រុងបាត់ដំបង</p>
              <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : #676, Group15, St 15, O
                Takam Village, Tuol Ta Ek Commune, Battambang City</p>
              <p>លេខទូរស័ព្ទ (Tel) : +855 (0)53 953 161 អ៊ីំម៉ែល (Email) : <span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                  <a href="info@teuksaat1001.com">info@teuksaat1001.com</a></span></p>
              <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
                1pm-5pm)</p>
            </div>
            <div v-if="program.platform == 'SR'" class="header-right"
              style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
              <h3>អង្គការទឹកស្អាត ១០០១ / <span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                  1001 Organization</span></h3>
              <br>
              <p>អាស័យដ្ឋាន : ភូមិកសិកម្ម សង្កាត់ស្រង៉ែ ក្រុងសៀមរាប ខេត្តសៀមរាប</p>
              <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : Kasekam Village,
                Sangkat Sragne, Siem Reap City</p>
              <p>លេខទូរស័ព្ទ (Tel) : +855 (0)63 218 298 អ៊ីំម៉ែល (Email) : <span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                  <a href="info@teuksaat1001.com">info@teuksaat1001.com</a></span></p>
              <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
                1pm-5pm)</p>
            </div>
          </div>
        </header>

        <!-- Body Section -->
        <section class="certificate-body">
          <h2 style="font-size: 12px; font-family:'Khmer OS Battambang', sans-serif;"><strong>វិញ្ញាបនបត្រវិភាគ /
              <span
                style="font-family:'Times New Roman', Times, serif; font-size: 14px; display: inline-block">Certificate
                of Analysis </span></strong></h2>
          <br>
          <table class="certificate-table" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
            <tr>
              <td v-if="program.site=='A5' || program.site=='A6'" colspan="2"><strong>ឈ្មោះផលិតផល</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Brand):</span> ទឹកពិសា</td>
              <td v-else colspan="2"><strong>ឈ្មោះផលិតផល</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Brand):</span> ទឹកពិសា អូ វី</td>
              <td></td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <td><strong>ប្រភពទឹក</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Raw Water Source):&nbsp; {{ program.water_source }} /</span> {{ program.kh_water_source }} </td>
            </tr>
            <tr>
              <td v-if="program.site=='A5'" colspan="2"><strong>ឈ្មោះអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Organization):</span> Happy Chandara Primary School</td>
              <td v-else-if="program.site=='A6'" colspan="2"><strong>ឈ្មោះអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Organization):</span> Happy Chandara Secondary School</td>
              <td v-else colspan="2"><strong>ឈ្មោះអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Organization):</span> សហគមន៍ផលិតទឹកពិសា</td>
              <td></td>
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <td><strong>លេខកូដស្ថានីយ៍</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Site Code):&nbsp; {{ program.site }}</span></td>
            </tr>
            <tr>
              <td v-if="program.site =='A5'|| program.site =='A6'" colspan="4"><strong>អាស័យដ្ឋានអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Address of Organization):</span>&nbsp; ឃុំ{{ program.commune_khmer }} &nbsp; &nbsp; ស្រុក{{
                    program.District_khmer }}
                &nbsp; &nbsp; {{ program.Province_khmer }}</td>
              <td v-else colspan="4"><strong>អាស័យដ្ឋានអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Address of Organization):</span>&nbsp; ឃុំ{{ program.commune_khmer }} &nbsp; &nbsp; ស្រុក{{
                    program.District_khmer }}
                &nbsp; &nbsp; ខេត្ត{{ program.Province_khmer }}</td>
              
              <!-- <td colspan="3">ឃុំរវៀង ស្រុកសំរោង ខេត្តតាកែវ ឃុំរវៀង ស្រុកសំរោង ខេត្តតាកែវ</td> -->
            </tr>
            <tr>
              <td colspan="2"><strong>ឈ្មោះអ្នកផ្តល់សំណាក</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Sample Submitted by)</span> : &nbsp;{{ program.kh_advisor }}</td>
              <td></td>
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <td><strong>ថ្ងៃយកសំណាក</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Sampling Date):</span>&nbsp;{{ program.sample_date }}</td>
            </tr>
            <tr>
              <td colspan="2"><strong>ថ្ងៃទទួលសំណាក</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Sample Received Date):</span>&nbsp;{{ program.received_date }}</td>
              <td></td>
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              <td><strong>ថ្ងៃវិភាគសំណាក</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Analysis Date):</span>&nbsp;{{ program.analysis_date }}</td>
            </tr>
          </table>

          <!-- Biological Analysis Table -->
          <div v-if="program.chlorine || program.hardness || program.manganese || program.calcium || program.nitrate || program.nitrite || program.sulfates || program.alkalinity
            || program.chloride || program.amonia || program.iron || program.fluoride || program.total_chlore || program.arsenic || program.ph || program.tds
            || program.turbidity || program.conductivity || program.aluminium">
            <h2 style="font-size: 12px; font-family:'Khmer OS Battambang', sans-serif;"><strong>ការវិភាគលក្ខណៈរូប គីមី /
                <span style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  PHYSICO-CHEMICAL ANALYSIS</span></strong></h2>
            <table class="biological-analysis" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
              <tr>
                <!-- <th text-alige="center">ល.រ <br> No</th> -->
                <th text-alige="center">លក្ខណៈរូប - គីមី <br> Physico-Chemical</th>
                <th>វិធីសាស្រ្តវិភាគ <br> Reference Methods</th>
                <th>ស្តង់ដារទឹកស្អាត <br> CDWQS</th>
                <th>លទ្ធផល <br> Result</th>
              </tr>
              <tr v-if="program.ph">
                <td>ប៉េហាស (pH)</td>
                <td><strong>Hanna HI9811-5</strong> <br>
                  Accuracy: ±2% (at 20°C)</td>
                <td>6.5 - 8.5</td>
                <td>{{ program.ph }} </td>
              </tr>
              <tr v-if="program.turbidity">
                <td>ភាពល្អក់ (Turbidity)</td>
                <td><strong>Hach Turbidimeter 2100Q</strong> <br>
                  Accuracy:±2% of reading plus from 0-1000NTU</td>
                <td>≤ 5 NTU</td>
                <td>{{ program.turbidity }} &nbsp;NTU</td>
              </tr>
              <tr v-if="program.tds">
                <td>អង្គធាតុរលាយសរុប (TDS)</td>
                <td><strong>Hanna HI9811-5</strong> <br>
                  Accuracy: ±2% (at 20°C)</td>
                <td>≤ 800 mg/l</td>
                <td>{{ program.tds }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.conductivity">
                <td>ភាពចម្លងអគ្គិសនី (Cond)</td>
                <td><strong>Hanna HI9811-5 </strong><br>
                  Accuracy: ±2% (at 20°C)</td>
                <td>≤ 1500 µS/cm</td>
                <td>{{ program.conductivity }}&nbsp;µS/cm</td>
              </tr>
              <tr v-if="program.aluminium">

                <td>អាលុយមីញ៉ូម (Aluminium)</td>
                <td><strong>Hach DR3900 ( Aluminium )</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 0.2 mg/l</td>
                <td>{{ program.aluminium }} &nbsp;mg/l</td>
              </tr>
              <!-- More Parameter -->
              <tr v-if="program.chlorine">

                <td>ក្លរសេរី (Free Clorine)</td>
                <td><strong>Hach DR3900 (Clorine, Free)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>0.2 - 0.5 mg/l</td>
                <td>{{ program.chlorine }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.hardness">

                <td>សារធាតុរឹងរលាយ (T.Hardness)</td>
                <td><strong>Hach DR3900 (Hardness, Calcium and Magnesium)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 300 mg/l</td>
                <td>{{ program.hardness }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.iron">

                <td>ដែក (Iron)</td>
                <td><strong>Hach DR3900 (Iron, Total)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 0.3 mg/l</td>
                <td>{{ program.iron }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.manganese">

                <td>ម៉ង់កាណេស (Manganess)</td>
                <td><strong>Hach DR3900 (Manganese, LR)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 0.1 mg/l</td>
                <td>{{ program.manganese }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.calcium">

                <td>កាល់ស្យូម (Calcium)</td>
                <td><strong>Hach DR3900 (Hardness, Calcium and Magnesium)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td></td>
                <td>{{ program.calcium }}</td>
              </tr>
              <tr v-if="program.nitrate">

                <td>នីត្រាត (Nitrate)</td>
                <td><strong>Hach DR3900 (Nitrate)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 50 mg/l</td>
                <td>{{ program.nitrate }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.nitrite">

                <td>នីទ្រីត (Nitrite)</td>
                <td><strong>Hach DR3900 (Nitrite)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 3 mg/l</td>
                <td>{{ program.nitrite }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.sulfates">

                <td>ស៊ុលផាត (Sulfate)</td>
                <td><strong>Hach DR39000 (Sulfate )</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 250 mg/l</td>
                <td>{{ program.sulfates }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.alkalinity">

                <td>អាល់កាឡាំង (Alkalinity)</td>
                <td><strong>Hach DR39000 (Alkalinity total )</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>--</td>
                <td>{{ program.alkalinity }} </td>
              </tr>
              <tr v-if="program.chloride">

                <td>ក្លរ៉ាយ​ (Cloride)</td>
                <td><strong>Hach DR39000 (Chloride )</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>≤ 250 mg/l</td>
                <td>{{ program.chloride }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.amonia">

                <td>អាម៉ូនីញ៉ាក់ (Ammonia)</td>
                <td><strong>Hach DR39000 (Ammonia )</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td> ≤ 1.5 mg/l</td>
                <td>{{ program.amonia }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.fluoride">

                <td>ភ្លុយអរ (Fluoride)</td>
                <td><strong>Hach DR3900 ( Fluoride)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td> ≤ 1.5 mg/l</td>
                <td>{{ program.fluoride }} &nbsp;mg/l</td>
              </tr>
              <tr v-if="program.total_chlore">

                <td>ក្លរសរុប​ (Total Clorine)</td>
                <td><strong>Hach DR3900 (Total Clorine)</strong><br>
                  Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
                <td>--</td>
                <td>{{ program.total_chlore }} </td>
              </tr>
              <tr v-if="program.arsenic">

                <td>អាសេនិច (Arsenic)</td>
                <td><strong>Merc Arsenic Test Kit</strong></td>
                <td>≤ 0.05 mg/l</td>
                <td>{{ program.arsenic }} &nbsp;mg/l</td>
              </tr>
            </table>
          </div>
          <div v-if="program.coli_machine || program.coli_bottle || program.el_machine || program.coli_machine">
            <h2 style="font-size: 12px; font-family:'Khmer OS Battambang', sans-serif;">
              <strong>ការវិភាគលក្ខណៈជីវសាស្រ្ត/
                <span style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  BIOLOGICAL ANALYSIS</span></strong>
            </h2>
            <table class="biological-analysis" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
              <tr>
                <!-- <th>ល.រ <br> No</th> -->
                <th>លក្ខណៈជីវសាស្រ្ត <br> Biological Analysis</th>
                <th>វិធីសាស្រ្តវិភាគ <br> Reference Methods</th>
                <th>ស្តង់ដារទឹកស្អាត <br> CDWQS</th>
                <th v-if="program.coli_machine || program.el_machine">លទ្ធផលម៉ាស៊ីន<br> Machine</th>
                <th v-if="program.coli_bottle || program.el_bottle">លទ្ធផលប៊ីដុង<br> Bottle</th>
              </tr>
              <tr>
                <td style="padding-top: 10px;">កូលីហ្វម (Total Coliform)</td>
                <td style="padding-top: 10px;"><strong>NF EN ISO 9308-1 2000</strong></td>
                <td style="padding-top: 10px;">0 CFU / 100 ml</td>
                <td style="padding-top: 10px;"
                  v-if="(program.coli_machine) && (program.coli_machine > 0 || program.coli_machine == 'TNTC')"
                  class="bad_phisic_color">{{ program.coli_machine }}</td>
                <td style="padding-top: 10px;" v-if="program.coli_machine && program.coli_machine == 0"
                  class="good_phisic_color">{{ program.coli_machine }}</td>
                <td style="padding-top: 10px;"
                  v-if="(program.coli_bottle) && (program.coli_bottle > 0 || program.coli_bottle == 'TNTC')"
                  class="bad_phisic_color">{{ program.coli_bottle }}</td>
                <td style="padding-top: 10px;" v-if="program.coli_bottle && program.coli_bottle == 0"
                  class="good_phisic_color">{{ program.coli_bottle }}</td>
              </tr>
              <tr>
                <td style="padding-top: 10px;">អឺកូលី (E.Coli)</td>
                <td style="padding-top: 10px;"><strong>NF EN ISO 9308-1 2000</strong></td>
                <td style="padding-top: 10px;">0 CFU / 100 ml</td>
                <td style="padding-top: 10px;"
                  v-if="(program.el_machine) && (program.el_machine > 0 || program.el_machine == 'TNTC')"
                  class="bad_phisic_color">{{ program.el_machine }}</td>
                <td style="padding-top: 10px;" v-if="program.el_machine && program.el_machine == 0"
                  class="good_phisic_color">{{ program.el_machine }}</td>

                <td style="padding-top: 10px;"
                  v-if="(program.el_bottle) && (program.el_bottle > 0 || program.el_bottle == 'TNTC')"
                  class="bad_phisic_color">{{ program.el_bottle }}</td>
                <td style="padding-top: 10px;" v-if="program.el_bottle && program.el_bottle == 0"
                  class="good_phisic_color">{{ program.el_bottle }}</td>
              </tr>
            </table>
          </div>
        </section>
        <br>
        <!-- Notes Section -->
        <p class="note" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
          <strong>ចំណាំ / Note: TNTC:</strong><span
            style="font-family:'Times New Roman', Times, serif; font-size: 12px">&nbsp;
            Too Numerous To Count</span> (ចំនួនមេរោគច្រើនមិនអាចរាប់បាន) | <strong> CDWQS: </strong>
          <span style="font-family:'Times New Roman', Times, serif; font-size: 12px">&nbsp;
            Cambodian Drinking Water Quality Standard </span>(ស្តង់ដារគុណភាពទឹកពិសាកម្ពុជា)
        </p>
        <br>
        <!-- Conclusion Section -->
        <h5 style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">ការសន្និដ្ឋាន / CONCLUSION</h5>
        <p class="conclusion" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">{{ program.comment
          }}</p>


        <!-- Footer Section -->
        <footer class="certificate-footer" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
          <div>
            <p>វិភាគដោយ / Analysis by</p><br><br><br>
            <p>អ្នកត្រួតពិនិត្យគុណភាពទឹក : {{ program.labOfficerNameKh }}</p>
            <p>Lab Officer: {{ program.labOfficerNameEng }} </p>
            <p>Tel: {{ program.labOfficerPh }}</p>
          </div>
          <div>
            <p>ទទួលស្គាល់ដោយ / Acknowledge by</p><br><br><br>
            <p>ប្រធានផ្នែកប្រតិបត្តិការប្រចាំតំបន់ : {{ program.ROMKh }}</p>
            <p>Regional Operation Manager: {{ program.ROMEng }} </p>
            <p>Tel: {{ program.ROMPh }}</p>
          </div>
        </footer>
      </div>
    </div>
  </div>

  <div v-if="dataOneRecord">
    <div class="certificate">
      <!-- Header Section -->
      <header class="certificate-header">
        <!-- Top Header Text -->
        <div class="header-top" style="font-family:'Khmer OS Muol Light', sans-serif;font-size: 13px;">
          <h5>ព្រះរាជាណាចក្រកម្ពុជា</h5>
          <h5>ជាតិ សាសនា ព្រះមហាក្សត្រ</h5>
        </div>
        <!-- Organization Info and Logo -->
        <div class="header-content">
          <div class="header-left">
            <img src="img/logo.png" alt="Teuk Saat 1001 Logo" class="logo" />
          </div>
          <br> <br><br><br>
          <div v-if="dataOneRecord.platform == 'PP' || dataOneRecord.platform == 'KSP'" class="header-right"
            style="font-size: 10px; font-family:'Khmer OS Battambang';">
            <h3>អង្គការទឹកស្អាត ១០០១ / <span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                1001 Organization</span></h3>
            <br>
            <p>អាស័យដ្ឋាន : ផ្ទះលេខ 100 ផ្លូវ 95 សង្កាត់បឹងត្របែក ខណ្ឌចម្ការមន ក្រុងភ្នំពេញ</p>
            <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : No 100, Street 95,
              Sangkat Boeung Trabek, Khan Chamkarmon, Phnom Penh</p>
            <p>លេខទូរស័ព្ទ (Tel) : +855 (0)23 215 427 អ៊ីំម៉ែល (Email) : <a href="info@teuksaat1001.com">
                <span style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                  info@teuksaat1001.com</span></a></p>
            <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
              1pm-5pm)</p>
          </div>

          <div v-if="dataOneRecord.platform == 'KC'" class="header-right"
            style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
            <h3>អង្គការទឹកស្អាត ១០០១ / <span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                1001 Organization</span></h3>
            <br>
            <p>អាស័យដ្ឋាន : ភូមិទី ២ សង្កាត់វាល​វង់ ក្រុងកំពង់ចាម ខេត្តកំពង់ចាម</p>
            <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : Ti 2 Village, Sangkat
              Veal Vong, Kampong Cham City, Cambodia</p>
            <p>លេខទូរស័ព្ទ (Tel) : +855 (0) 42 210 898 អ៊ីំម៉ែល (Email) : <span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                <a href="info@teuksaat1001.com">info@teuksaat1001.com</a></span></p>
            <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
              1pm-5pm)</p>
          </div>

          <div v-if="dataOneRecord.platform == 'BTB'" class="header-right"
            style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
            <h3>អង្គការទឹកស្អាត ១០០១ / <span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                1001 Organization</span></h3>
            <br>
            <p>អាស័យដ្ឋាន : អាស័យដ្ឋាន : ផ្ទះលេខ ៦៧៦​ ក្រុមទី ១៥​ ភូមិអូរតាគាំ១ សង្កាត់ទួលតាឯក ក្រុងបាត់ដំបង</p>
            <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : #676, Group15, St 15, O
              Takam Village, Tuol Ta Ek Commune, Battambang City</p>
            <p>លេខទូរស័ព្ទ (Tel) : +855 (0)53 953 161 អ៊ីំម៉ែល (Email) : <span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                <a href="info@teuksaat1001.com">info@teuksaat1001.com</a></span></p>
            <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
              1pm-5pm)</p>
          </div>
          <div v-if="dataOneRecord.platform == 'SR'" class="header-right"
            style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
            <h3>អង្គការទឹកស្អាត ១០០១ / <span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px;display: inline-block"> Teuk Saat
                1001 Organization</span></h3>
            <br>
            <p>អាស័យដ្ឋាន : ភូមិកសិកម្ម សង្កាត់ស្រង៉ែ ក្រុងសៀមរាប ខេត្តសៀមរាប</p>
            <p style="font-family:'Times New Roman', Times, serif; font-size: 12px;">Address : Kasekam Village, Sangkat
              Sragne, Siem Reap City, Cambodi</p>
            <p>លេខទូរស័ព្ទ (Tel) : +855 (0)63 218 298 អ៊ីំម៉ែល (Email) : <span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px;">
                <a href="info@teuksaat1001.com">info@teuksaat1001.com</a></span></p>
            <p>ធ្វើការពីថ្ងៃ ចន្ទ-សុក្រ ព្រឹក 8:00-12:00 ល្ងាច 1:00-5:00 (Time and date opening: Mon-Fri 8am-12am
              1pm-5pm)</p>
          </div>
        </div>
      </header>

      <!-- Body Section -->
      <section class="certificate-body">
        <h2 style="font-size: 12px; font-family:'Khmer OS Battambang', sans-serif;"><strong>វិញ្ញាបនបត្រវិភាគ /
            <span
              style="font-family:'Times New Roman', Times, serif; font-size: 14px; display: inline-block">Certificate of
              Analysis </span></strong></h2>
        <br>
        <table class="certificate-table" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
          <tr>
            <td v-if="dataOneRecord.site=='A5' || dataOneRecord.site=='A6'" colspan="2"><strong>ឈ្មោះផលិតផល</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Brand):</span> ទឹកពិសា</td>
              <td v-else colspan="2"><strong>ឈ្មោះផលិតផល</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Brand):</span> ទឹកពិសា អូ វី</td>
            <td></td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <td><strong>ប្រភពទឹក</strong><span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                (Raw Water Source):&nbsp; {{ dataOneRecord.water_source }} /</span> {{ dataOneRecord.kh_water_source }}
            </td>
          </tr>
          <tr>
            <td v-if="dataOneRecord.site=='A5'" colspan="2"><strong>ឈ្មោះអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Organization):</span> Happy Chandara Primary School</td>
              <td v-else-if="dataOneRecord.site=='A6'" colspan="2"><strong>ឈ្មោះអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Organization):</span> Happy Chandara Secondary School</td>
              <td v-else colspan="2"><strong>ឈ្មោះអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Name of Organization):</span> សហគមន៍ផលិតទឹកពិសា</td>
            <td></td>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <td><strong>លេខកូដស្ថានីយ៍</strong><span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                (Site Code):&nbsp; {{ dataOneRecord.site }}</span></td>
          </tr>
          <tr>
            <td v-if="dataOneRecord.site =='A5'|| dataOneRecord.site =='A6'" colspan="4"><strong>អាស័យដ្ឋានអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Address of Organization):</span>&nbsp; ឃុំ{{ dataOneRecord.commune_khmer }} &nbsp; &nbsp; ស្រុក{{
                    dataOneRecord.District_khmer }}
                &nbsp; &nbsp; {{ dataOneRecord.Province_khmer }}</td>
              <td v-else colspan="4"><strong>អាស័យដ្ឋានអង្គភាព</strong><span
                  style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                  (Address of Organization):</span>&nbsp; ឃុំ{{ dataOneRecord.commune_khmer }} &nbsp; &nbsp; ស្រុក{{
                    dataOneRecord.District_khmer }}
                &nbsp; &nbsp; ខេត្ត{{ dataOneRecord.Province_khmer }}</td>
            <!-- <td colspan="3">ឃុំរវៀង ស្រុកសំរោង ខេត្តតាកែវ ឃុំរវៀង ស្រុកសំរោង ខេត្តតាកែវ</td> -->
          </tr>
          <tr>
            <td colspan="2"><strong>ឈ្មោះអ្នកផ្តល់សំណាក</strong><span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                (Sample Submitted by)</span> : &nbsp;{{ dataOneRecord.kh_advisor }}</td>
            <td></td>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <td><strong>ថ្ងៃយកសំណាក</strong><span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                (Sampling Date):</span>&nbsp;{{ dataOneRecord.sample_date }}</td>
          </tr>
          <tr>
            <td colspan="2"><strong>ថ្ងៃទទួលសំណាក</strong><span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                (Sample Received Date):</span>&nbsp;{{ dataOneRecord.received_date }}</td>
            <td></td>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            <td><strong>ថ្ងៃវិភាគសំណាក</strong><span
                style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                (Analysis Date):</span>&nbsp;{{ dataOneRecord.analysis_date }}</td>
          </tr>
        </table>

        <!-- Biological Analysis Table -->
        <div v-if="dataOneRecord.chlorine || dataOneRecord.hardness || dataOneRecord.manganese || dataOneRecord.calcium || dataOneRecord.nitrate || dataOneRecord.nitrite || dataOneRecord.sulfates || dataOneRecord.alkalinity
          || dataOneRecord.chloride || dataOneRecord.amonia || dataOneRecord.iron || dataOneRecord.fluoride || dataOneRecord.total_chlore || dataOneRecord.arsenic || dataOneRecord.ph || dataOneRecord.tds
          || dataOneRecord.turbidity || dataOneRecord.conductivity || dataOneRecord.aluminium">
          <h2 style="font-size: 12px; font-family:'Khmer OS Battambang', sans-serif;"><strong>ការវិភាគលក្ខណៈរូប គីមី /
              <span style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                PHYSICO-CHEMICAL ANALYSIS</span></strong></h2>
          <table class="biological-analysis" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
            <tr>
              <!-- <th text-alige="center">ល.រ <br> No</th> -->
              <th text-alige="center">លក្ខណៈរូប - គីមី <br> Physico-Chemical</th>
              <th>វិធីសាស្រ្តវិភាគ <br> Reference Methods</th>
              <th>ស្តង់ដារទឹកស្អាត <br> CDWQS</th>
              <th>លទ្ធផល <br> Result</th>
            </tr>
            <tr v-if="dataOneRecord.ph">
              <td>ប៉េហាស (pH)</td>
              <td><strong>Hanna HI9811-5</strong> <br>
                Accuracy: ±2% (at 20°C)</td>
              <td>6.5 - 8.5</td>
              <td>{{ dataOneRecord.ph }} </td>
            </tr>
            <tr v-if="dataOneRecord.turbidity">
              <td>ភាពល្អក់ (Turbidity)</td>
              <td><strong>Hach Turbidimeter 2100Q</strong> <br>
                Accuracy:±2% of reading plus from 0-1000NTU</td>
              <td>≤ 5 NTU</td>
              <td>{{ dataOneRecord.turbidity }} &nbsp;NTU</td>
            </tr>
            <tr v-if="dataOneRecord.tds">
              <td>អង្គធាតុរលាយសរុប (TDS)</td>
              <td><strong>Hanna HI9811-5</strong> <br>
                Accuracy: ±2% (at 20°C)</td>
              <td>≤ 800 mg/l</td>
              <td>{{ dataOneRecord.tds }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.conductivity">
              <td>ភាពចម្លងអគ្គិសនី (Cond)</td>
              <td><strong>Hanna HI9811-5 </strong><br>
                Accuracy: ±2% (at 20°C)</td>
              <td>≤ 1500 µS/cm</td>
              <td>{{ dataOneRecord.conductivity }}&nbsp;µS/cm</td>
            </tr>
            <tr v-if="dataOneRecord.aluminium">

              <td>អាលុយមីញ៉ូម (Aluminium)</td>
              <td><strong>Hach DR3900 ( Aluminium )</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 0.2 mg/l</td>
              <td>{{ dataOneRecord.aluminium }} &nbsp;mg/l</td>
            </tr>
            <!-- More Parameter -->
            <tr v-if="dataOneRecord.chlorine">

              <td>ក្លរសេរី (Free Clorine)</td>
              <td><strong>Hach DR3900 (Clorine, Free)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>0.2 - 0.5 mg/l</td>
              <td>{{ dataOneRecord.chlorine }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.hardness">

              <td>សារធាតុរឹងរលាយ (T.Hardness)</td>
              <td><strong>Hach DR3900 (Hardness, Calcium and Magnesium)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 300 mg/l</td>
              <td>{{ dataOneRecord.hardness }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.iron">

              <td>ដែក (Iron)</td>
              <td><strong>Hach DR3900 (Iron, Total)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 0.3 mg/l</td>
              <td>{{ dataOneRecord.iron }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.manganese">

              <td>ម៉ង់កាណេស (Manganess)</td>
              <td><strong>Hach DR3900 (Manganese, LR)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 0.1 mg/l</td>
              <td>{{ dataOneRecord.manganese }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.calcium">

              <td>កាល់ស្យូម (Calcium)</td>
              <td><strong>Hach DR3900 (Hardness, Calcium and Magnesium)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td></td>
              <td>{{ dataOneRecord.calcium }}</td>
            </tr>
            <tr v-if="dataOneRecord.nitrate">

              <td>នីត្រាត (Nitrate)</td>
              <td><strong>Hach DR3900 (Nitrate)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 50 mg/l</td>
              <td>{{ dataOneRecord.nitrate }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.nitrite">

              <td>នីទ្រីត (Nitrite)</td>
              <td><strong>Hach DR3900 (Nitrite)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 3 mg/l</td>
              <td>{{ dataOneRecord.nitrite }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.sulfates">

              <td>ស៊ុលផាត (Sulfate)</td>
              <td><strong>Hach DR39000 (Sulfate )</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 250 mg/l</td>
              <td>{{ dataOneRecord.sulfates }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.alkalinity">

              <td>អាល់កាឡាំង (Alkalinity)</td>
              <td><strong>Hach DR39000 (Alkalinity total )</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>--</td>
              <td>{{ dataOneRecord.alkalinity }} </td>
            </tr>
            <tr v-if="dataOneRecord.chloride">

              <td>ក្លរ៉ាយ​ (Cloride)</td>
              <td><strong>Hach DR39000 (Chloride )</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>≤ 250 mg/l</td>
              <td>{{ dataOneRecord.chloride }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.amonia">

              <td>អាម៉ូនីញ៉ាក់ (Ammonia)</td>
              <td><strong>Hach DR39000 (Ammonia )</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td> ≤ 1.5 mg/l</td>
              <td>{{ dataOneRecord.amonia }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.fluoride">

              <td>ភ្លុយអរ (Fluoride)</td>
              <td><strong>Hach DR3900 ( Fluoride)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td> ≤ 1.5 mg/l</td>
              <td>{{ dataOneRecord.fluoride }} &nbsp;mg/l</td>
            </tr>
            <tr v-if="dataOneRecord.total_chlore">

              <td>ក្លរសរុប​ (Total Clorine)</td>
              <td><strong>Hach DR3900 (Total Clorine)</strong><br>
                Wavelenght accuracy:±1.5nm;Photometric accuracy:±1%</td>
              <td>--</td>
              <td>{{ dataOneRecord.total_chlore }} </td>
            </tr>
            <tr v-if="dataOneRecord.arsenic">

              <td>អាសេនិច (Arsenic)</td>
              <td><strong>Merc Arsenic Test Kit</strong></td>
              <td>≤ 0.05 mg/l</td>
              <td>{{ dataOneRecord.arsenic }} &nbsp;mg/l</td>
            </tr>
          </table>
        </div>
        <div
          v-if="dataOneRecord.coli_machine || dataOneRecord.coli_bottle || dataOneRecord.el_machine || dataOneRecord.coli_machine">
          <h2 style="font-size: 12px; font-family:'Khmer OS Battambang', sans-serif;"><strong>ការវិភាគលក្ខណៈជីវសាស្រ្ត/
              <span style="font-family:'Times New Roman', Times, serif; font-size: 12px; display: inline-block">&nbsp;
                BIOLOGICAL ANALYSIS</span></strong></h2>
          <table class="biological-analysis" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
            <tr>
              <!-- <th>ល.រ <br> No</th> -->
              <th>លក្ខណៈជីវសាស្រ្ត <br> Biological Analysis</th>
              <th>វិធីសាស្រ្តវិភាគ <br> Reference Methods</th>
              <th>ស្តង់ដារទឹកស្អាត <br> CDWQS</th>
              <th v-if="dataOneRecord.coli_machine || dataOneRecord.el_machine">លទ្ធផលម៉ាស៊ីន<br> Machine</th>
              <th v-if="dataOneRecord.coli_bottle || dataOneRecord.el_bottle">លទ្ធផលប៊ីដុង<br> Bottle</th>
            </tr>
            <tr>
              <td style="padding-top: 10px;">កូលីហ្វម (Total Coliform)</td>
              <td style="padding-top: 10px;"><strong>NF EN ISO 9308-1 2000</strong></td>
              <td style="padding-top: 10px;">0 CFU / 100 ml</td>
              <td style="padding-top: 10px;"
                v-if="(dataOneRecord.coli_machine) && (dataOneRecord.coli_machine > 0 || dataOneRecord.coli_machine == 'TNTC')"
                class="bad_phisic_color">{{ dataOneRecord.coli_machine }}</td>
              <td style="padding-top: 10px;" v-if="dataOneRecord.coli_machine && dataOneRecord.coli_machine == 0"
                class="good_phisic_color">{{ dataOneRecord.coli_machine }}</td>
              <td style="padding-top: 10px;"
                v-if="(dataOneRecord.coli_bottle) && (dataOneRecord.coli_bottle > 0 || dataOneRecord.coli_bottle == 'TNTC')"
                class="bad_phisic_color">{{ dataOneRecord.coli_bottle }}</td>
              <td style="padding-top: 10px;" v-if="dataOneRecord.coli_bottle && dataOneRecord.coli_bottle == 0"
                class="good_phisic_color">{{ dataOneRecord.coli_bottle }}</td>
            </tr>
            <tr>
              <td style="padding-top: 10px;">អឺកូលី (E.Coli)</td>
              <td style="padding-top: 10px;"><strong>NF EN ISO 9308-1 2000</strong></td>
              <td style="padding-top: 10px;">0 CFU / 100 ml</td>
              <td style="padding-top: 10px;"
                v-if="(dataOneRecord.el_machine) && (dataOneRecord.el_machine > 0 || dataOneRecord.el_machine == 'TNTC')"
                class="bad_phisic_color">{{ dataOneRecord.el_machine }}</td>
              <td style="padding-top: 10px;" v-if="dataOneRecord.el_machine && dataOneRecord.el_machine == 0"
                class="good_phisic_color">{{ dataOneRecord.el_machine }}</td>

              <td style="padding-top: 10px;"
                v-if="(dataOneRecord.el_bottle) && (dataOneRecord.el_bottle > 0 || dataOneRecord.el_bottle == 'TNTC')"
                class="bad_phisic_color">{{ dataOneRecord.el_bottle }}</td>
              <td style="padding-top: 10px;" v-if="dataOneRecord.el_bottle && dataOneRecord.el_bottle == 0"
                class="good_phisic_color">{{ dataOneRecord.el_bottle }}</td>
            </tr>
          </table>
        </div>
      </section>
      <br>
      <!-- Notes Section -->
      <p class="note" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
        <strong>ចំណាំ / Note: TNTC:</strong><span
          style="font-family:'Times New Roman', Times, serif; font-size: 12px">&nbsp;
          Too Numerous To Count</span> (ចំនួនមេរោគច្រើនមិនអាចរាប់បាន) | <strong> CDWQS: </strong>
        <span style="font-family:'Times New Roman', Times, serif; font-size: 12px">&nbsp;
          Cambodian Drinking Water Quality Standard </span>(ស្តង់ដារគុណភាពទឹកពិសាកម្ពុជា).
      </p>
      <br>
      <!-- Conclusion Section -->
      <h5 style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">ការសន្និដ្ឋាន / CONCLUSION</h5>
      <p class="conclusion" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">{{
        dataOneRecord.comment }}</p>


      <!-- Footer Section -->
      <footer class="certificate-footer" style="font-size: 10px; font-family:'Khmer OS Battambang', sans-serif;">
        <div>
          <p>វិភាគដោយ / Analysis by</p><br><br><br>
          <p>អ្នកត្រួតពិនិត្យគុណភាពទឹក : {{ dataOneRecord.labOfficerNameKh }}</p>
          <p>Lab Officer: {{ dataOneRecord.labOfficerNameEng }} </p>
          <p>Tel: {{ dataOneRecord.labOfficerPh }}</p>
        </div>
        <div>
          <p>ទទួលស្គាល់ដោយ / Acknowledge by</p><br><br><br>
          <p>ប្រធានផ្នែកប្រតិបត្តិការប្រចាំតំបន់ : {{ dataOneRecord.ROMKh }}</p>
          <p>Regional Operation Manager: {{ dataOneRecord.ROMEng }} </p>
          <p>Tel: {{ dataOneRecord.ROMPh }}</p>
        </div>
      </footer>
    </div>
  </div>

</template>

<script>
export default {
  name: "CertificateOfAnalysis",
  data() {
    return {
      programs: [], // Store fetched data here
      dataOneRecord: null
    };
  },
  mounted() {
    const id = this.$route.query.id
    const plat = this.$route.query.platform
    // console.log(id)
    if (id) {
      axios.get('/api/pr?id=' + id)
        .then(response => {
          this.dataOneRecord = response.data; // Populate the programs data
          console.log(this.programs)
        })
        .catch(error => {
          console.log(error);
        });
    }
    if (plat) {
      const d = this.$route.query.date
      const re = this.$route.query.labreportType
      const tn = this.$route.query.testNumber
      const lab = this.$route.query.labName
      axios.get('/api/pr?platform=' + plat + "&d=" + d + "&re=" + re + "&tn=" + tn+ "&labName=" + lab)
        .then(response => {
          this.programs = response.data; // Populate the programs data
          console.log(this.programs)
        })
        .catch(error => {
          console.log(error);
        });
    }
  },
  methods: {
    printPage() {
      alert("print here")
      //window.print();
    }
  }
};
</script>

<style scoped>
.certificate {
  font-family: Arial, sans-serif;
  color: #000;
  max-width: 1000px;
  margin: auto;
  padding: 20px;
  border: 0px solid #ccc;
}

#a4-page {
  width: 210mm;
  text-align: justify;
  height: 297mm;
  margin: 20px auto;
  padding: 20mm;
  border: 1px solid #ddd;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  background-color: white;
  page-break-after: always;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

/* Header Section */
.certificate-header {
  border-bottom: 0px solid #ccc;
  margin-bottom: 10px;
}

.good_phisic_color {
  color: blue;
}

.bad_phisic_color {
  color: red;
}

.header-top {
  text-align: center;
  margin-bottom: 10px;
}

.header-top h2,
.header-top h3 {
  margin: 0;
}

.header-content {
  display: flex;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 0.6;
}

.logo {
  width: 80px;
  height: auto;
}

.header-right {
  flex: 2;
  font-size: 0.9em;
  line-height: 1.4em;
}

.header-right p {
  margin: 2px 0;
}

/* Body Section */
.certificate-body h2,
.certificate-body h3 {
  text-align: center;
  margin-top: 10px;
}

.certificate-table,
.biological-analysis {
  width: 100%;
  border-collapse: collapse;
  margin: 0px 0;
}

.certificate-table td,
.biological-analysis1 th,
.biological-analysis1 td {
  border: 0px solid #000;
  padding: 1px;
  font-size: 10px;
  text-align: left;
}

.biological-analysis th,
.biological-analysis td {
  border: 1px solid #000;
  padding: 1px;
  font-size: 10px;
  text-align: center;
}

.note {
  margin-left: 0;
  font-style: italic;
  font-size: 10px;
}

.conclusion {
  font-size: 10px;
  text-align: left;
  margin-top: 10px;
  font-weight: bold;
}

/* Footer Section */
.certificate-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

.certificate-footer div {
  text-align: center;
  font-size: 10px;
}

.certificate-footer p {
  margin: 2px 0;
}

@media print {
  .a4-page {
    width: 100%;
    height: auto;
    page-break-after: always;
  }

  .a4-page:last-child {
    page-break-after: auto;
    /* Prevent extra blank page at the end */
  }



  .print-button,
  .v-navigation-drawer,
  .v-app-bar,
  .app-toolbar {
    display: none;
    /* Hide unwanted elements */
  }

  

  
}
</style>
