<template>
  <div>
    <b-tabs v-if="total.Total_Sales > 0">
      <b-tab title="Summary" active>
        <table class="text-center table table-striped table-sm mt-2">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom"><h4 class="summary-title">
                SALES
              </h4></th>
              <td scope="col" class="align-bottom">Free</td>
              <td scope="col" class="align-bottom">Home delivery</td>
              <td scope="col" class="align-bottom">School</td>
              <td scope="col" class="align-bottom">On-Site</td>
              <td scope="col" class="align-bottom">Shopkeeper</td>
              <td scope="col" class="align-bottom">Emergency</td>
              <td scope="col" class="align-bottom">Bottle</td>
              <td scope="col" class="align-bottom">Other</td>
              <td scope="col"></td>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="col">Unit price</th>
              <td scope="col">0</td>
              <td scope="col">{{ total.Hod_Price }}</td>
              <td scope="col">{{ total.WiS_Price }}</td>
              <td scope="col">{{ total.Onsite_Price }}</td>
              <td scope="col">{{ total.Shopkeeper_Price }}</td>
              <td scope="col">{{ total.Emergency_Price || 0 }}</td>
              <td scope="col">{{ total.Bottle_Price }}</td>
              <td scope="col">{{ total.Others_Price }}</td>
              <td scope="col"></td>
            </tr>
            <tr>
              <th>Total units sold</th>
              <td>{{ total.Free_Sales }}</td>
              <td>{{ total.Hod_Sales }}</td>
              <td>{{ total.WiS_Sales }}</td>
              <td>{{ total.Onsite_Sales }}</td>
              <td>{{ total.Shopkeeper_Sales }}</td>
              <td>{{ total.Emergency_Sales || 0 }}</td>
              <td>{{ total.Bottle_Sales }}</td>
              <td>{{ total.Others_Sales }}</td>
              <td>{{ total.Total_Sales }}</td>
            </tr>
            <tr>
              <th>Total KHR</th>
              <th>0</th>
              <th>{{ total.Hod_Income | numberFormat }}</th>
              <th>{{ total.WiS_Income | numberFormat }}</th>
              <th>{{ total.Onsite_Income | numberFormat }}</th>
              <th>{{ total.Shopkeeper_Income | numberFormat }}</th>
              <th>{{ total.Emergency_Income | numberFormat }}</th>
              <th>{{ total.Bottle_Income | numberFormat }}</th>
              <th>{{ total.Others_Income | numberFormat }}</th>
              <th>{{ total.Total_Income | numberFormat }}</th>
            </tr>
            <tr class="table-primary">
              <td colspan="1" class="align-bottom">
                <h4 class="summary-title">EXPENSES</h4>
              </td>
              <td colspan="9"></td>
            </tr>
            <!-- <tr>
              <td colspan="9" class="text-right">
                Salaries :
              </td>
              <td colspan="1">
                <b>{{ totalSalary | numberFormat }}</b>
              </td>
            </tr>
            <tr>
              <td colspan="9" class="text-right">
                Others costs:
              </td>
              <td colspan="1">
                <b>{{ totalOthers | numberFormat }}</b>
              </td>
            </tr> -->
            <tr>
              <td colspan="9" class="text-right">
                Total expenses:
              </td>
              <td colspan="1">
                <b>{{ totalExpenses | numberFormat }}</b>
              </td>
            </tr>
            <tr class="table-primary">
              <td class="align-bottom">
                <h4 class="summary-title">PRODUCTION</h4>
              </td>
              <td colspan="9"></td>
            </tr>
            <tr class="savings-row">
              <td colspan="1"></td>
              <td colspan="9" class="text-left">
                <span class="production-field">Savings outside TS: <b>{{indicators.Saving_outside_TS}}</b></span>
              </td>
            </tr>
            <tr>
              <td colspan="1"></td>
              <td colspan="9" class="text-left">
                <span class="production-field">Bottles in operation: <b>{{indicators.Number_Bottles_in_Operation}}</b></span>
                <span class="production-field">Bottles in stock: <b>{{indicators.Number_Bottles_in_Stock}}</b></span>
                <span class="production-field">Bottles broken or lost: <b>{{indicators.Number_Bottles_Broken_Lost}}</b></span>
              </td>
            </tr><tr>
              <td colspan="1"></td>
              <td colspan="9" class="text-left">
                <span class="production-field">Days open : <b>{{ total.Number_Open_Days }} / {{ numberOfDays }}</b></span>
                <span class="production-field">Number of operators: <b>{{indicators.Number_of_Operator}}</b></span>
              </td>
            </tr><tr>
              <td colspan="1"></td>
              <td colspan="1" class="text-left">Water meters</td>
              <td v-if="indicators.water_meters && indicators.water_meters.length > 1" colspan="8" class="text-left">
                <table class="table table-sm table-bordered text-right">
                  <thead>
                    <tr class="text-small">
                      <th></th>
                      <th><small>Start</small></th>
                      <th><small>End</small></th>
                      <th><small>Consumed (L)</small></th>
                      <th><small>Sold (L)</small></th>
                      <th><small>Lost (L)</small></th>
                      <th><small>Lost (%)</small></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(waterMeter, index) in water_meters" :key="index">
                      <td>
                        <small v-if="index > 0">{{ waterMeter.startDate }} - {{ waterMeter.endDate }}</small>
                        <small v-else>{{ new Date(new Date(waterMeter.startDate).getTime() + 86400000).toISOString().split('T')[0] }} - {{ waterMeter.endDate }}</small>
                      </td>
                      <td>{{ waterMeter.start }}</td>
                      <td>{{ waterMeter.end }}</td>
                      <td>{{ waterMeter.consumed | numberFormat }}</td>
                      <td>{{ waterMeter.sold | numberFormat }}</td>
                      <td>{{ waterMeter.loss | numberFormat }}</td>
                      <td>{{ waterMeter.loss_percent | percentFormat }}</td>
                    </tr>
                    <tr>
                      <th colspan="3">Total</th>
                      <td>{{ water_meters.reduce((acc, meter) => acc + meter.consumed, 0) | numberFormat }}</td>
                      <td>{{ water_meters.reduce((acc, meter) => acc + meter.sold, 0) | numberFormat }}</td>
                      <td>{{ water_meters.reduce((acc, meter) => acc + meter.loss, 0) | numberFormat }}</td>
                      <td>{{ (water_meters.reduce((acc, meter) => acc + meter.consumed, 0) - water_meters.reduce((acc, meter) => acc + meter.sold, 0)) / water_meters.reduce((acc, meter) => acc + meter.consumed, 0) * 100 | percentFormat }}</td>
                    </tr>
                  </tbody>
                </table>
              </td>
              <td v-else colspan="9" class="text-left">
                <span class="production-field">Water consumed: <b>{{indicators.Water_Consume}}</b></span>
                <span class="production-field">Water sold: <b>{{total.Total_Sales * 20}}</b></span>
                <span class="production-field">Water lost:
                  <b>{{indicators.Water_Consume - (total.Total_Sales * 20)}}</b>
                   ({{(indicators.Water_Consume - (total.Total_Sales * 20))*100 / indicators.Water_Consume | numberFormat}}%)
                </span>
                <span class="production-field">Water start: <b>{{indicators.Water_begining}}</b></span>
                <span class="production-field">Water end: <b>{{indicators.Water_end}}</b></span>
              </td>
            </tr><tr>
              <td colspan="1"></td>
              <td colspan="9" class="text-left">
                <span class="production-field">Machine consumption: <b>{{indicators.Machine_end - indicators.Machine_begining}}</b></span>
                <span class="production-field">Machine start: <b>{{indicators.Machine_begining}}</b></span>
                <span class="production-field">Machine end: <b>{{indicators.Machine_end}}</b></span>
              </td>
            </tr>
            <tr class="table-primary">
              <td class="align-bottom">
                <h4 class="summary-title">QUALITY</h4>
              </td>
              <td colspan="9"></td>
            </tr>
            <tr>
              <th>Sample date</th>
              <th>Coliform</th>
              <th>Ecoli</th>
              <th>Safe</th>
              <th>Root cause</th>
              <th colspan="3">Comment</th>
              <th colspan="2">Action</th>
            </tr>
            <tr v-for="(result, index) in qualityResults" :key="'qualr'+index">
              <td>{{ result.sample_date.substr(5,11) }}</td>
              <td>{{ result.total_coliform }}</td>
              <td>{{ result.escherichia }}</td>
              <td>{{ result.safe }}</td>
              <td>{{ result.root_cause }}</td>
              <td colspan="3">
                <b-icon v-if="result.comment" icon="bell" v-b-popover.hover.top="result.comment" aria-hidden="true"></b-icon>
              </td>
              <td colspan="2">{{ result.action_done }}</td>
            </tr>
          </tbody>
        </table>
        <div class="d-flex flex-row">
          <div v-for="(picture,index) in summaryPictures" :key="'picButton'+index" class="d-flex flex-column text-center">
            <a
              :href="picture.id ? '/static/' + picture.path : '/api/getPicture?path='+picture.url"
              target="blank"
              class="pic-sales">
              <img width="70px" :src="picture.id ? '/static/' + (picture.miniature_path ? picture.miniature_path : picture.path) : '/api/getPicture?path='+picture.url" />
            </a>
            <span v-if="picture.type"><small>{{ picture.type }}</small></span>
          </div>
        </div>
      </b-tab>
      <b-tab title="Sales">
        <div class='indicator'>Days open : <b>{{ total.Number_Open_Days }} / {{ numberOfDays }}</b></div>
        <table class="text-center table table-striped table-sm table-borderless">
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Free<BR/>0</th>
              <th scope="col">Home delivery<BR/>{{ total.Hod_Price }}</th>
              <th scope="col">School<BR/>{{ total.WiS_Price }}</th>
              <th scope="col">On-Site<BR/>{{ total.Onsite_Price }}</th>
              <th scope="col">Shopkeeper<BR/>{{ total.Shopkeeper_Price }}</th>
              <th scope="col">Emergency<BR/>{{ total.Emergency_Price || 0 }}</th>
              <th scope="col">Bottle<BR/>{{ total.Bottle_Price }}</th>
              <th scope="col">Others<BR/>{{ total.Others_Price}}</th>
              <th scope="col">TOTAL</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sale in sales" :key="sale.Code_Daily" class="xs-row">
              <td>{{sale.Day.substr(5, 11)}}</td>
              <td>{{sale.Free_Sales}}</td>
              <td>{{sale.Hod_Sales}}</td>
              <td>{{sale.WiS_Sales}}</td>
              <td>{{sale.Onsite_Sales}}</td>
              <td>{{sale.Shopkeeper_Sales}}</td>
              <td>{{sale.Emergency_Sales || 0}}</td>
              <td>{{sale.Bottle_Sales}}</td>
              <td>{{sale.Others_Sales}}</td>
              <td>{{sale.Total_Sales}}</td>
            </tr>
            <tr class="table-primary">
              <th> TOTAL </th>
              <th>{{ total.Free_Sales }}</th>
              <th>{{ total.Hod_Sales }}</th>
              <th>{{ total.WiS_Sales }}</th>
              <th>{{ total.Onsite_Sales }}</th>
              <th>{{ total.Shopkeeper_Sales }}</th>
              <th>{{ total.Emergency_Sales || 0 }}</th>
              <th>{{ total.Bottle_Sales }}</th>
              <th>{{ total.Others_Sales }}</th>
              <th>{{ total.Total_Sales }}</th>
            </tr>
            <tr class="table-secondary">
              <th>TOTAL KHR</th>
              <th>0</th>
              <th>{{ total.Hod_Income | numberFormat }}</th>
              <th>{{ total.WiS_Income | numberFormat }}</th>
              <th>{{ total.Onsite_Income | numberFormat }}</th>
              <th>{{ total.Shopkeeper_Income | numberFormat }}</th>
              <th>{{ total.Emergency_Income || 0 | numberFormat }}</th>
              <th>{{ total.Bottle_Income | numberFormat }}</th>
              <th>{{ total.Others_Income | numberFormat }}</th>
              <th>{{ total.Total_Income | numberFormat }}</th>
            </tr>
          </tbody>
        </table>
      </b-tab>
      <b-tab title="P&L">
        <table class="text-right table table-sm table-x-sm">
          <thead>
            <tr class="table-primary">
              <th scope="col" colspan="3" class="text-center">Income</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="total.Hod_Income>0">
              <td colspan="2">HOD</td>
              <td>{{ total.Hod_Income | numberFormat }}</td>
            </tr>
            <tr v-if="total.WiS_Income>0">
              <td colspan="2">Water in School</td>
              <td>{{ total.WiS_Income | numberFormat }}</td>
            </tr>
            <tr v-if="total.Onsite_Income>0">
              <td colspan="2">On-Site</td>
              <td>{{ total.Onsite_Income | numberFormat }}</td>
            </tr>
            <tr v-if="total.Shopkeeper_Income>0">
              <td colspan="2">Shopkeeper</td>
              <td>{{ total.Shopkeeper_Income | numberFormat }}</td>
            </tr>
            <tr v-if="total.Emergency_Income>0">
              <td colspan="2">Emergency</td>
              <td>{{ total.Emergency_Income | numberFormat }}</td>
            </tr>
            <tr v-if="total.Bottle_Income>0">
              <td colspan="2">Bottles</td>
              <td>{{ total.Bottle_Income | numberFormat }}</td>
            </tr>
            <tr v-if="total.Others_Income>0">
              <td colspan="2">Others</td>
              <td>{{ total.Others_Income | numberFormat }}</td>
            </tr>
            <tr class="table-secondary">
              <th colspan="2"> TOTAL INCOME </th>
              <th>{{ total.Total_Income | numberFormat }}</th>
            </tr>
          </tbody>
          <thead>
            <tr class="table-primary">
              <th scope="col" colspan="3" class="text-center">Expenses</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="type in Object.keys(groupedExpenses)" class="xs-row">
              <tr :key="type">
                <td :rowspan="groupedExpenses[type].length+1" style="vertical-align: middle; background-color: white;">{{ type }}</td>
                <td>{{groupedExpenses[type][0].Ref_expenses}}</td>
                <td>{{groupedExpenses[type][0].Amount_expenses | numberFormat}}</td>
              </tr>
              <tr v-for="expense in groupedExpenses[type].slice(1)" :key="type+expense.Ref_expenses">
                <td>{{expense.Ref_expenses }}</td>
                <td>{{expense.Amount_expenses | numberFormat}}</td>
              </tr>
              <tr style="background-color: beige; font-size: 0.7rem; font-weight: bold;" :key="'total'+type">
                <td>Total {{ type }}</td>
                <td>{{ groupedExpenses[type].reduce((sum, expense) => sum + Number(expense.Amount_expenses), 0) | numberFormat}}</td>
              </tr>
            </template>
            <tr class="table-secondary">
              <th colspan="2"> TOTAL EXPENSES </th>
              <th>{{ totalExpenses | numberFormat}}</th>
            </tr>
            <tr :class="(total.Total_Income - totalExpenses > 0 ) ? 'table-success' : 'table-danger'">
              <th colspan="2"> NET RESULT </th>
              <th>{{ total.Total_Income - totalExpenses | numberFormat}}</th>
            </tr>
          </tbody>
        </table>
      </b-tab>
      <b-tab title="Checklist">
        <div v-if="!pictureViewAll" class="row mt-2">
          <div class="col-12 text-center">
            <img v-if="pictures.length>0" v-show="imageLoaded" class="checklist-image" :src="'/api/getPicture?path='+pictures[selectedPicture].url" @load="onImageLoaded(selectedPicture)">
            <b-spinner v-if="!imageLoaded" variant="primary" label="Spinning" class="m-5"></b-spinner>
          </div>
        </div>
        <div v-if="!pictureViewAll" class="row mt-1">
          <div class="col-12 text-center">
            <button v-for="(picture,index) in picturesNoXml" class="btn btn-primary ml-1" 
              :key="'picButton'+index"
              @click="loadImage(index)">
              {{ index+1 }}
            </button>
            <button class="btn btn-secondary ml-1" @click="pictureViewAll=true">View all</button>
          </div>
        </div>
        <div v-if="pictureViewAll" class="row mt-2">
          <div  v-for="(picture,index) in picturesNoXml" :key="'pic'+index" class="col-4 mb-2">
            <a :href="'/api/getPicture?path='+picture.url" target="_blank">
              <img width="100%"                
                :src="'/api/getPicture?path='+picture.url">
            </a>
          </div>
        </div>
        <div v-if="pictureViewAll" class="row text-right">
          <div class="col-12">
            <button class="btn btn-secondary ml-1" @click="pictureViewAll=false">View one by one</button>
          </div>            
        </div>  
      </b-tab>
      <b-tab title="Closures">
        <table class="text-center table table-striped table-sm mt-2">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom" colspan="3"><h4 class="summary-title">
                CLOSURES
              </h4></th>
            </tr>
            <tr><th>Closure date</th><th>Reopening date</th><th>Reason for closure</th></tr>
          </thead>
          <tbody>
            <tr v-if="closures.length === 0">
              <th>This site never had a closure</th>
            </tr>
            <tr v-for="closure in closures" :key="'closure'+closure.Code_Closure">
              <td>{{ closure.Closing_date | dateFormat}}</td>
              <td>{{ closure.Reopening_date | dateFormat}}</td>
              <td>{{ closure.Description }}<BR/>{{ closure.Description_english }}</td>
            </tr>
          </tbody>
        </table>
      </b-tab>
       <!-- Alert Tab -->
      <b-tab title="Alert">
        <table class="text-center table table-striped table-sm mt-2">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom" colspan="3"><h4 class="summary-title">
                Warning
              </h4></th>
            </tr>       
          </thead>
          <tbody>
            <!-- <tr v-if="!comment_me.length">
              <th>There is no alert</th>
            </tr> -->
            <!-- <tr v-for="(value, name) in comment_me" :key="'warning'+value">
              <td>{{ name }}: {{ value }}</td>
            </tr> -->
            <tr v-for="value in comment_me" :key="'warning'+value">
              <td> {{ value }}</td>
            </tr> 
          </tbody>
        </table>
      </b-tab>
      <!-- Aler Site profile -->
      <b-tab title="Site_Profile">
        <table class="text-center table table-striped table-sm mt-2" border="1">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom" colspan="10"><h4 class="summary-site-profile">
                Site Information
              </h4></th>
            </tr>       
          </thead>
          <tbody>
            <tr v-for="value in site_profile" :key="'site_profile'+value">            
              <td class="text-left">
                <span class="production-field">Site : <b>{{value.Id_Site}}</b></span>
              </td>
              <td class="text-left">
                <span class="production-field">Platform : <b>{{value.Platform}}</b></span> </td>
                <td class="text-left">
                  <span class="production-field">Advisor : <b>{{value.Advisor}}</b></span> </td>
                <td class="text-left">
                  <span class="production-field">Longi : <b>{{value.Longi}}</b></span> </td>
                <td class="text-left">
                  <span class="production-field">Lati : <b>{{value.Lati}}</b></span> </td>
                <td class="text-left">
                  <span class="production-field">Village : <b>{{value.Village}}</b> </span></td>
                <td class="text-left">
                  <span class="production-field">Commune : <b>{{value.Commune}}</b></span> </td>
                <td class="text-left">
                  <span class="production-field">District : <b>{{value.District}}</b></span> </td>
                <td class="text-left">
                  <span class="production-field">Province : <b>{{value.Province}}</b></span> </td>       
            </tr> 
          </tbody>
        </table>
        <table class="text-center table table-striped table-sm mt-2" border="1">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom" colspan="3"><h4 class="summary-site-profile">
                Project Agreement
              </h4></th>
            </tr>       
          </thead>
          <tbody>
            <tr v-for="value1 in site_profile" :key="'site_profile1'+value1" > 
              <td class="text-left">
                <span v-if="value1.ProjectAgreement ==null || value1.ProjectAgreement =='null'" class="production-field">Date : <b>No date |</b></span>
                <span v-else class="production-field">Date : <b>{{ value1.ProjectAgreement.substr(5, 11) }} |</b></span>
                <span class="production-field">Wave : <b>{{value1.Wave}} |</b></span>
                <span v-if="value1.Sale_Starting_Date ==null || value1.Sale_Starting_Date =='null'" class="production-field">Sale_Date : <b>No date |</b></span>
                <span v-else class="production-field">Sale_Date : <b>{{ value1.Sale_Starting_Date.substr(5, 11) }} |</b></span>
                <span class="production-field">First_Funder : <b>{{value1.Funder_1}} |</b></span>
                <span class="production-field">Second_Funder : <b>{{value1.Funder_2}} |</b></span>
                <span class="production-field">Third_Funder : <b>{{value1.Funder_3}} </b></span>
              </td>           
            </tr>
          </tbody>
        </table>
        <table class="text-center table table-striped table-sm mt-2" border="1">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom" colspan="3"><h4 class="summary-site-profile" >
                Population
              </h4></th>
            </tr>       
          </thead>
          <tbody>
            <tr v-for="value2 in site_profile" :key="'site_profile2'+value2" > 
              <td class="text-left">
                <span class="production-field">Number_Village : <b>{{value2.Number_Village}} </b></span>
                <span class="production-field">Number_Family : <b>{{value2.Number_Family}} |</b></span>
                <span class="production-field">Number_Households : <b>{{value2.Number_Households}} |</b></span>
                <span class="production-field">Population_Number : <b>{{value2.Number_Population}} |</b></span>
                <span class="production-field">Number_Women : <b>{{value2.Number_Women}} </b></span> 
                <span class="production-field">Number_Migration : <b>{{value2.Number_Migration}} |</b></span>
                <span class="production-field">Number_Village_5km : <b>{{value2.Number_Village_5km}} |</b></span>
                <span class="production-field">Number_Family_5km : <b>{{value2.Number_Family_5km}} </b></span>           
              </td>           
            </tr>
            <br /> 
            <tr v-for="value3 in site_profile" :key="'site_profile3'+value3" > 
              <td class="text-left">
                
                <span class="production-field">Number_Households_5km : <b>{{value3.Number_Households_5km}} |</b></span>
                <span class="production-field">Population_5km : <b>{{value3.Number_Population_5km}} |</b></span>
                <span class="production-field">Number_Women_5km : <b>{{value3.Number_Women_5km}} |</b></span>
                <span class="production-field">Number_Migration_5km : <b>{{value3.Number_Migration_5km}} |</b></span>
                <span class="production-field">Number_Pagoda : <b>{{value3.Number_Pagoda}} </b></span>
                <span class="production-field">Number_Primary_School : <b>{{value3.Number_Primary_School}}</b></span>
                
              </td>           
            </tr> 
          </tbody>
        </table>
        <table class="text-center table table-striped table-sm mt-2" border="1">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom" colspan="3"><h4 class="summary-site-profile">
                Infrastructure
              </h4></th>
            </tr>       
          </thead>
          <tbody>
            <tr v-for="value4 in site_profile" :key="'site_profile4'+value4" > 
              <td class="text-left">             
                <span class="production-field">Land_of_kiosk : <b>{{value4.Land_of_kiosk}} |</b></span>
                <span class="production-field">Road_Leading_to_Kiosk : <b>{{value4.Road_Leading_to_Kiosk}} |</b></span>
                <span class="production-field">Paved_Asphalt_Road : <b>{{value4.Paved_Asphalt_Road}} |</b></span>
                <span class="production-field">Concrete_Road : <b>{{value4.Concrete_Road}} |</b></span>
                <span class="production-field">Laterite_Road : <b>{{value4.Laterite_Road}} </b></span>
                <span class="production-field">White_Soiled_Road : <b>{{value4.White_Soiled_Road}} |</b></span>
                <span class="production-field">Water_Source : <b>{{value4.Water_Source}} |</b></span>
                <span class="production-field">Well_Pond_Ownership : <b>{{value4.Well_Pond_Ownership}} |</b></span>
                <span class="production-field">Depth_Well_Pond : <b>{{value4.Depth_Well_Pond}} </b></span>
              </td>           
            </tr> 
            <br/>
            <tr v-for="value5 in site_profile" :key="'site_profile5'+value5" > 
              <td class="text-left">                     
                <span class="production-field">Water_Source_Distance_From_Kiosk : <b>{{value5.Water_Source_Distance_From_Kiosk}} |</b></span>
                <span class="production-field">Second_Water_Source : <b>{{value5.Second_Water_Source}} |</b></span>
                <span class="production-field">Well_Pond_Ownership_Second_Source : <b>{{value5.Well_Pond_Ownership_Second_Source}} |</b></span>
                <span class="production-field">Depth_Well_Pond_Second_Source : <b>{{value5.Depth_Well_Pond_Second_Source}} |</b></span>
                <span class="production-field">Water_Source_Distance_From_Kiosk_Second_Source : <b>{{value5.Water_Source_Distance_From_Kiosk_Second_Source}} |</b></span>
              </td>           
            </tr>
          </tbody>
        </table>
        <table class="text-center table table-striped table-sm mt-2" border="1">
          <thead>
            <tr class="table-primary">
              <th scope="col" class="align-bottom" colspan="3"><h4 class="summary-site-profile">
                Technical Aspect
              </h4></th>
            </tr>       
          </thead>
          <tbody>
            <tr v-for="value6 in site_profile" :key="'site_profile6'+value6" > 
              <td class="text-left">                     
                <span class="production-field">Main_Power_Source : <b>{{value6.Main_Power_Source}} |</b></span>
                <span class="production-field">Second_Power_Source : <b>{{value6.Second_Power_Source}} |</b></span>
                <span class="production-field">Type_of_Water_Tank : <b>{{value6.Type_of_Water_Tank}} </b></span>
              </td>           
            </tr>
          </tbody>
        </table>
        <!-- <b-button            
        variant="success"
            class="ml-1 btn-sm"
            v-b-modal.edit-order
        >Download Site Profile
        </b-button>
        <b-button            
        variant="danger"
            class="ml-1 btn-sm"
            v-b-modal.edit-order
        >Edit Site Profile
        </b-button> -->
      </b-tab>
      <b-tab title="Settle Invoice" v-if="user && user.permissions && user.permissions.includes('view_finance_invoice')">
        <div v-if="settle_invoice.length === 0" class="mt-2">
          <p>No invoice settled</p>
        </div>
        <div v-else class="row mt-2">
          <div  v-for="(picture,index) in summarySettleInvoicePicture" :key="'pic'+index" class="col-4 mb-2">
            <a :href="'/api/getPicture?path='+picture.url" target="_blank">
              <img width="100%"                
                :src="'/api/getPicture?path='+picture.url">
            </a>
          </div>
        </div>
        </b-tab>
      </b-tabs>
    <div v-else-if="noData">
      <p>Incomplete data</p>
      <SiteClosureForm :selectedSite="siteObject" @close="$emit('close')"/>
    </div>
    <div v-else>
      <b-spinner variant="primary" label="Spinning"></b-spinner>
    </div>
  </div>
</template>

<script>
import SiteClosureForm from './SiteClosureForm'

export default {
  components: {
    SiteClosureForm
  },
  props: {
    site: {
      type: String,
    },
    month: {
      type: String
    },
    siteObject: {
      type: Object
    }
  },
  watch : {
  },
  data: function() {
    return {
      noData: false,
      sales: [],
      total: {},
      expenses: [],
      indicators: {},
      pictures:[],
      settle_invoice:[],
      qualityResults: [],
      selectedPicture:0,
      imageLoaded: false,
      objImage: {},
      pictureViewAll: false,
      salesPictures: [],
      expensesPictures: [],
      productionPictures: [],
      closures: [],
      water_meters: [],
      comment_me: {},
      site_profile :{},
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    picturesNoXml() {
      return this.pictures.filter(e => { return e['content_type'] == "image/jpeg" || e['url'].endsWith("heif") })
    },
    groupedExpenses() {
      return this.expensesNoTotal.reduce((acc, expense) => {
        const category = expense.Category_expenses;
        if (!acc[category]) {
          acc[category] = [];
        }
        acc[category].push(expense);
        return acc;
      }, {});
    },
    summaryPictures() {
      let ret = []
      ret = ret.concat(this.salesPictures.filter(e => { return e['content_type'] == "image/jpeg" || e.id }));
      ret = ret.concat(this.expensesPictures.filter(e => { return e['content_type'] == "image/jpeg" || e.id}));
      ret = ret.concat(this.productionPictures.filter(e => { return e['content_type'] == "image/jpeg" || e.id}));
      return ret;
    },
    summarySettleInvoicePicture() {
      let ret = []
      ret = ret.concat(this.settle_invoice.filter(e => { return e['content_type'] == "image/jpeg" }))
      return ret
    },
    totalSalary() {
      let total = this.expenses.find(e => { return e.Ref_expenses === "total-salary" })
      if (total)
        return total.Amount_expenses;
      return 0
    },
    totalOthers() {
      let total = this.expenses.find(e => { return e.Ref_expenses === "total-other-cost" })
      if (total)
        return total.Amount_expenses;
      return 0
    },
    expensesNoTotal() {
      return this.expenses.filter(e => { return e.Ref_expenses != "total-other-cost" && e.Ref_expenses != "total-salary" && e.Amount_expenses != 0 })
    },
    totalExpenses() {
      let total = 0;
      this.expensesNoTotal.forEach(e => { total += e.Amount_expenses });
      return total;
    },
    numberOfDays() {
      const arr = this.month.split('-');
      return new Date(parseInt(arr[0]), parseInt(arr[1]), 0).getDate();
    },
  },
  filters: {
    numberFormat(val){
      return new Intl.NumberFormat('km-KH', { maximumFractionDigits: 0 }).format(val);
    },
    percentFormat(val){
      return new Intl.NumberFormat('km-KH', { maximumFractionDigits: 2 }).format(val) + " %";
    },
    dateFormat(val){
      if(val){
        let d = new Date(val)
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
      }
      return ""
    }
  },
  methods: {
    calculateWaterLoss() {
      if(this.indicators && this.sales && this.indicators.water_meters && this.indicators.water_meters.length > 1 && this.sales.length > 0) {
        for (let index = 1; index < this.indicators.water_meters.length; index++) {
          let consumed = 1000 * (this.indicators.water_meters[index].value - this.indicators.water_meters[index-1].value);
          let sold = 20 * this.sales.filter(e => { return e.Code_Daily.slice(0,10) > this.indicators.water_meters[index-1].date && e.Code_Daily.slice(0,10) <= this.indicators.water_meters[index].date })
              .reduce((acc, sale) => acc + sale.Total_Sales, 0)
          const element = {
            startDate: this.indicators.water_meters[index-1].date,
            endDate: this.indicators.water_meters[index].date,
            start: this.indicators.water_meters[index-1].value,
            end: this.indicators.water_meters[index].value,
            consumed: consumed,
            sold: sold,
            loss: consumed - sold,
            loss_percent: (consumed - sold) / consumed * 100
          };
          this.water_meters.push(element);
        }
      }
    },
    onImageLoaded(index) {
      if(this.selectedPicture == index) {
        this.imageLoaded = true;
      }
    },
    loadImage(index) {
      if(this.selectedPicture != index) {
        this.imageLoaded = false;
        this.selectedPicture = index;
      }
    },
    monthToText(month) {
      const arr = month.split('-');
      return parseInt(arr[1])+ "-"+parseInt(arr[0]);
    },
  },
  mounted() {
    this.sales = [];
    this.axios.get("/api/getSales?month="+this.month+"&site="+this.site).then(response => {
      this.sales = response.data.sales;
      this.sales.forEach(sale => {
        sale.Others_Sales = sale.Total_Sales - sale.Shopkeeper_Sales - sale.WiS_Sales - sale.Onsite_Sales - sale.Hod_Sales - sale.Free_Sales - sale.Bottle_Sales - (sale.Emergency_Sales || 0)
      })
      this.total = response.data.total;
      this.total.Others_Sales = this.total.Total_Sales - this.total.Shopkeeper_Sales - this.total.WiS_Sales - this.total.Onsite_Sales - this.total.Hod_Sales - this.total.Bottle_Sales - this.total.Free_Sales - (this.total.Emergency_Sales || 0)
      this.total.Others_Income = this.total.Total_Income - this.total.Shopkeeper_Income - this.total.WiS_Income - this.total.Onsite_Income - this.total.Hod_Income - this.total.Bottle_Income - (this.total.Free_Income || 0) - (this.total.Emergency_Income || 0)
      this.total.Others_Price = this.total.Others_Sales > 0 ? Math.round(this.total.Others_Income/this.total.Others_Sales) : 0
      if (this.sales.length === 0) {
        this.noData = true
      }
      this.calculateWaterLoss();
    });
    this.axios.get("/api/getExpenses?month="+this.month+"&site="+this.site).then(response => {
      this.expenses = response.data.expenses;
    });
    this.axios.get("/api/getPictures?month="+this.monthToText(this.month)+"&site="+this.site).then(response => {
      if(response.data['6. Site Checklist']) {
        this.pictures = Object.values(response.data['6. Site Checklist']);
      }
      if(response.data['1. Register Sales']){
        this.salesPictures = Object.values(response.data['1. Register Sales']);
      }
      if(response.data['2. Register Expenses'] || response.data['3. Register Expenses']){
        this.expensesPictures = Object.values(response.data['2. Register Expenses'] || response.data['3. Register Expenses']);
      }
      if(response.data['5. Production Report']){
        this.productionPictures = Object.values(response.data['5. Production Report']);
      }
      if(response.data['3. Settle Invoices']){
        this.settle_invoice = Object.values(response.data['3. Settle Invoices']);
      }
      if(response.data['cashier_app']){
        this.salesPictures.push(...response.data['cashier_app'].filter(e => e.type == 'sales'));
        this.productionPictures.push(...response.data['cashier_app'].filter(e => e.type == 'water_meter'));
        this.expensesPictures.push(...response.data['cashier_app'].filter(e => e.type == 'expenses'));
      }
    });
    this.axios.get("/api/getIndicators?month="+this.month+"&site="+this.site).then(response => {
      this.indicators = response.data;
      this.calculateWaterLoss();
    });
    this.axios.get("/api/getQualityResults?month="+this.month+"&site="+this.site).then(response => {
      this.qualityResults = response.data;
    });
    this.axios.get("/api/getClosures?site="+this.site).then(response => {
      this.closures = response.data.closures;
      //console.log(response.data);
    });
    this.axios.get("/api/GetWarning?site="+this.site+"&month="+this.month).then(response => {
      this.comment_me = response.data;
      //console.log(this.comment_me);
    });
    this.axios.get("/api/getSiteProfile?site="+this.site).then(response => {
      this.site_profile = response.data.Site_Profile;
      console.log(this.site_profile);
    });
  }
}
</script>

<style>
.title1{
  color: aqua;
}
.xs-row>td {
  padding: 0 !important;
  font-size: 0.9rem;
}
.checklist-image{
  max-height: 70vh;
  max-width: 100%;
}
.separator-row {
  border-top:1px solid gray;
}
.separator-row td {
  padding-top:10px !important;
}
.production-field {
  padding-right: 20px;
}
.summary-title {
  font-size: 1.2rem;
  padding-bottom: 0px;
  margin-bottom: 0px;
  
}
.summary-site-profile {
  font-size: 1.2rem;
  padding-bottom: 0px;
  margin-bottom: 0px;
  color: blue;
}
.pic-sales > img {
  border: 1px solid #7abaff;
  padding: 2px;
}
.pic-sales {
  padding: 5px 5px 0px 5px;
}
.savings-row {
  font-weight: bold;
  background-color: #b8daff44 !important;
}
.td {
        border: 1px solid black;
        text-align: center;
    }
.table-x-sm td {
  padding:0px !important;
}
</style>