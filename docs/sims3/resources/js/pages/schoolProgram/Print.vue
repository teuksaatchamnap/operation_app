<template>
  <div>
    <!-- Print Button -->
    <!-- <button @click="printPage" class="print-button">Print Document</button> -->

    <!-- Printable Content -->
    <div id="printable">
      <div v-for="(program, index) in programs" :key="index" class="a4-page">
        <!-- Header Section -->
        <div class="page-header">
          <div class="logo-left">
            <img src="img/logo.png" alt="Teuksaat1001 logo" width="200"> <!-- Left Logo -->
          </div>
          <div class="header-text">
            កិច្ចព្រមព្រៀងកម្មវិធីទឹកសាលារៀន ២០២៥-២០២៦
          </div>
          <div class="logo-right">
            <img src="img/owe.png" alt="Owe Logo" width="200"> <!-- Right Logo -->
          </div>
        </div>
        <!-- Body Section -->
        <div class="page-content">
          <h2>កិច្ចព្រមព្រៀងនេះត្រូវបានធ្វើឡើងរវាង៖</h2>
          <p>
            អង្គការទឹកស្អាត១០០១ ជាអង្គការមិនមែនរដ្ឋាភិបាលកម្ពុជាដែលបានចុះបញ្ជីនៅថ្ងៃទី២៥ ខែកក្កដា ឆ្នាំ២០០៧ ជាមួយក្រសួងមហាផ្ទៃ(លេខ៨៧១ សជណ)ដែលមានទីតាំងនៅផ្ទះលេខ១០០ ផ្លូវលេខ៩៥ សង្កាត់បឹងត្របែក
             ខណ្ឌចំការមន រាជធានីភ្នំពេញ ប្រទេសកម្ពុជា តំណាងដោយលោកស្រី អាម៉ង់ឌីន ឆូស៊ីណង នាយិកាគ្រប់គ្រងហើយរួមជាមួយនឹងសហគ្រិនឈ្មោះ {{program.school.en_name_khmer}}
             ទទួលបន្ទុកលើទីតាំងស្ថានីយផលិតទឹក <b>{{ program.school.Id_Site }}</b>
          </p>
          <h2>និង</h2>
          <p>
            ឈ្មោះសាលារៀន<b>{{ program.school.school_name_khmer}}</b>  ឈ្មោះនាយកសាលារៀន <b>{{ program.school.school_director_name_khmer}}</b> កូដសាលារៀន <b>{{ program.code }}</b>
            ភូមិ <b>{{ program.school.village_khmer }}</b> ឃុំ <b>{{ program.school.commune_khmer }}</b> ខេត្ត <b>{{ program.province_show }}</b> ចំនួនថ្នាក់រៀន  <b>{{ program.classes }}</b>
            ពីថ្នាក់ទី {{program.s_grade}} ដល់ថ្នាក់ទី {{program.e_grade}} ចំនួនសិស្សសរុប: {{program.khmer_total_student}} ចំនួនសិស្សប្រុស: {{program.boys}}
            ចំនួនសិស្សស្រី: <b>{{program.girls}}</b> ឆ្នាំសិក្សា ២០២៥-២០២៦ ចាប់ផ្តើមនៅថ្ងៃ <b>{{program.start}}</b> និងបញ្ចប់់នៅថ្ងៃទី <b>{{program.end}}</b>&nbsp;&nbsp;
            ចំនួនប៊ីដុងដែលបានយល់ព្រមក្នុងការចែកចាយក្នុងមួយថ្ងៃ៖ <b>{{program.b_approved}}</b>
          </p>
          <h2>១ - កម្មវិធីទឹកសាលារៀន</h2>
          <p>
            កម្មវិធីទឹកសាលារៀន (WinS) គឺជាកម្មវិធីសង្គមមួយដែលបង្កើតឡើងដោយអង្គការទឹកស្អាត១០០១ ដោយមានការគាំទ្រពី ១០០១ ហ្វង់តែន ចាប់តាំងពីឆ្នាំ២០០៨ មកកម្មវិធីទឹកសាលារៀនបានផ្តល់ទឹកស្អាតសុវត្តិភាព
            ដល់កុមារច្រើនជាង ៣៧២០០០​​​ នាក់ នៅក្នុងសាលា បឋមសិក្សាចំនួន១០០០សាលា សូមអរគុណបណ្តាញស្ថានីយទឹកចំនួន ៣៧៨ ស្ថានីយដែលមានទីតាំងនៅក្នុងខេត្តចំនួន១៨។ តាមរយៈកម្មវិធីនេះ អង្គការទឹកស្អាត ១០០១ 
            មានគោលបំណងការពារជនងាយរងគ្រោះបំផុតពីជម្ងឺដែលបណ្តាលមកពីទឹកលើកុមារ។ នៅក្នុងឆ្នាំ ២០០៨ ដើម្បីផ្តល់លទ្ធភាពដល់កុមារមកពីសាលារៀនដែលមានមូលដ្ឋាននៅតំបន់ជនបទ ទទួលបានដោយឥតគិតថ្លៃ 
            និងរៀងរាល់ថ្ងៃសិក្សា (ផ្អែកលើកាលវិភាគសាលារដ្ឋនៅកម្ពុជា) ទឹកពិសារសុវត្តិភាព ចំនួនទឹក២០លីត្រក្នុងមួយប៊ីដុង ក្នុងមួយថ្នាក់ ដើម្បីផលប្រយោជន៍របស់សិស្សានុសិស្ស។ ទឹកនេះនឹង ត្រូវបានផ្តល់ដោយ 
            អង្គការទឹកស្អាត១០០១ /សហគ្រិនតាមស្ថានីយអូវី (ដែលបានរៀបរាប់ខាងលើ) ឬដោយប្រតិបត្តិកររបស់គាត់ម្នាក់។
          </p>
          <h2>២- អង្គការទឹកស្អាត១០០១ និងការប្តេជ្ញាចិត្តរបស់សហគ្រិន</h2>
          <p>
            សហគ្រិនអូវី ប្ដេជ្ញាធ្វើឱ្យអស់ពីសមត្ថភាពរបស់គាត់/នាង ដើម្បីធានាបាននូវរាល់ការដឹកចែកចាយប្រចាំថ្ងៃរបស់សាលារៀន។ ប្រសិនបើ សាលារៀននៅឆ្ងាយពីទីតាំងស្ថានីយផលិតទឹក សហគ្រិនហើយនិងសាលារៀនត្រូវបាន
            អនុញ្ញាតឱ្យស្វែងរកកិច្ចព្រមព្រៀងនៅថ្ងៃដឹកចែក ចាយដោយក្នុងលក្ខខណ្ឌថាចំនួនប៊ីដុងដែលត្រូវបានប្រគល់គោរពតាមកិច្ចសន្យាយ៉ាងត្រឹមត្រូវ។
          </p>
          <h2>៣ - ការប្តេជ្ញាចិត្តរបស់សាលារៀន</h2>
          <p>
            នៅពេលចុះហត្ថលេខាលើកិច្ចសន្យានេះ សាលារៀននឹងត្រូវបានផ្តល់ជូននូវបញ្ជីទឹកសាលារៀន ដើម្បីតាមដានដើម្បីកត់ត្រារាល់ការដឹក  ជញ្ជូន។ ក្រុមការងាររបស់អង្គការទឹកស្អាត១០០១នឹងត្រូវបានអនុញ្ញាតឱ្យធ្វើសវនកម្ម
            សាលារៀននិងពិនិត្យរាល់ការកត់ត្រា។ ការកត់ត្រា ត្រូវតែបំពេញរាល់ការដឹកជញ្ជូន។ ប្រសិនបើការកត់ត្រាមិនពិត ឬមិនពេញលេញ អង្គការទឹកស្អាត១០០១ រក្សាសិទ្ធិក្នុងការបញ្ឈប់ ឬមិន បន្តកិច្ចព្រមព្រៀងបច្ចុប្បន្ន។ 
            អង្គការទឹកស្អាត១០០១ រក្សាសិទ្ធិធ្វើសវនកម្មសាលារៀនដោយមិនចាំបាច់ជូនដំណឹងជាមុន។ សាលារៀន នឹងមិនមានសិទ្ធិទាមទារសំណងណាមួយសម្រាប់ការខ្វះខាតនៃការផ្តល់ជូននោះទេ។ទោះជាយ៉ាងនេះក្តីអង្គការទឹកស្អាត
            ១០០១សូមលើក ទឹកចិត្តយ៉ាងមុតមាំឱ្យសាលារៀនទាក់ទងមក អង្គការទឹកស្អាត១០០១ អំពីសេវាកម្មណាមួយប្រសិនបើមានបញ្ហាដឹកជញ្ជូនកើត​ឡើង តាមរយៈលេខទូរស័ព្ទខាងក្រោម ០២៣​ ២១៥ ​៤២៧
             ឬតាមអាស័យដ្ឋានអ៊ីម៉េលខាងក្រោម៖ <a href="info@teuksaat1001.com">info@teuksaat1001.com</a> ដោយបញ្ជាក់អោយច្បាស់លាស់អំពីបញ្ហាដែលបានជួបប្រទះ។
          </p>
          <p>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            
            ធ្វើនៅ.....................ថ្ងៃទី...............ខែ...........ឆ្នាំ២០..... </p>
        </div>
        <!-- Footer Section -->
        <!-- <div class="page-footer">
          <p>ហត្ថលេខា</p>
        </div> -->
        <div class="signature">
          <p>នាយិកាអង្គការទឹកស្អាត១០០១&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;មេឃុំ / ប្រធានសហគមន៍
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;នាយកសាលា&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            សហគ្រិន </p> <br>
          <p><img src="img/MD1.jpg" width="160" height="110" /><br>&nbsp;&nbsp;អាម៉ង់ឌីន ឆូស៊ីណង&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            ______________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
            &nbsp;&nbsp;&nbsp;
           ______________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
           &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;______________

          </p>
        </div>
      </div>
    </div>
  </div>
</template>
<!-- <v-btn  prepend-icon="mdi-check-circle" color="blue" class="ma-4"  @click="$router.push({ path: '/schoolsContractPrint', query:{platform:platformSelect} })">
  Print
</v-btn> -->
<script>
import axios from 'axios';

export default {
  data() {
    return {
      programs: [] // Store fetched data here
    };
  },
  mounted() {
   
    let parameter = this.$route.query.platform;
    let year = this.$route.query.year;
    // Fetch data from Laravel backend
    axios.get('/api/schoolsContractPrint/'+ parameter + '?year=' + year) // Adjust the API endpoint as needed
      .then(response => {
        this.programs = response.data; // Populate the programs data
      })
      .catch(error => {
        console.log(error);
      });
  },
  methods: {
    printPage() {
      alert("print here")
      //window.print();
    }
  }
}
</script>
<style scoped>
/* Print button styling */
.print-button {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  margin-bottom: 20px;
  border: none;
  cursor: pointer;
  font-size: 16px;
}

.print-button:hover {
  background-color: #45a049;
}

/* A4 Page Layout */
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
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 2px;
  padding: 10px 0;
  margin-bottom: 20px;
  /* margin-left: 50px;
  margin-right: 50px; */
  position: relative;
}
.page-header .logo-left,
.page-header .logo-right {
  max-width: 80px;
  /* Ensures the image fits without being too large */
  height: auto;
  /* Keeps the image's original aspect ratio */
  display: block;
}
.page-header .header-text {
  flex-grow: 1;
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 0 20px;
  font-family: Khmer OS Battambang;
  /* Adds space between the text and logos */
}
.page-header .logo-left img,
.page-header .logo-right img {
  width: 100%;
  /* Ensures the image takes up full space of the container */
  height: auto;
  /* Keeps the aspect ratio */
}
.page-content {
  flex-grow: 1;
  font-size: 12px;
  line-height: 1.6;
  text-align: justify;
  color: #333;
}
.page-content h2 {
  font-size: 13px;
  text-align: justify;
  color: #080808;
  font-weight: bold;
  margin-bottom: 10px;
  font-family: Khmer OS Battambang;
}
.page-content p {
  font-size: 11px;
  margin: 5px 0;
  font-family: Khmer OS Battambang;
  justify-content: center
}

.page-content p strong {
  color: #333;
}

.page-footer {
  text-align: center;
  font-size: 14px;
  padding-top: 10px;
  border-top: 1px ;
  color: #0e0d0d;
  font-family: Khmer OS Battambang;
}
.signature {
  margin-left: 10px;
  text-align: left;
  font-size: 12px;
  padding-top: 10px;
  border-top: 1px ;
  color: #111111;
  font-family: Khmer OS Battambang;
}

/* Responsive print styling */
@media print {
  .print-button {
    display: none;
    /* Hide the print button when printing */
  }

  .v-navigation-drawer {
    display: none;
  }

  .v-app-bar {
    display: none;
  }

  .app-toolbar {
    display: none;
  }

  .a4-page {
    width: 100%;
    height: 100%;
    page-break-after: always;
    /* Ensure each program prints on a new page */
  }
}
</style>
