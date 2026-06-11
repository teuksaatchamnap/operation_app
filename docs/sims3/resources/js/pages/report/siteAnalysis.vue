<template>
    <v-container fluid class="pa-6 report-container" :class="{ 'khmer-mode': currentLanguage === 'km' }">
        <!-- Site Select -->
        <div class="d-flex justify-space-between align-center mb-2 no-print">
            <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
            <v-autocomplete v-model="selectedSite" :items="sites" label="Select Site" item-title="Id_Site"
                item-value="Id_Site" density="compact" outlined
                style="max-width: 180px; font-size: 0.9rem;"></v-autocomplete>

            <v-select v-model="selectedLanguage" :items="languages" item-title="text" item-value="value"
                density="compact" style="max-width: 150px; margin-bottom: 10px;" label="Language"></v-select>
            <v-btn color="primary" @click="printReport" small>
                <v-icon left small>mdi-printer</v-icon>
                Print
            </v-btn>
        </div>

        <!-- SECTION 2: Site Info -->
        <v-row justify="center" dense>
            <v-col cols="12" md="8" lg="8">
                <v-card class="pa-2 mb-2" style="border-radius: 12px; box-shadow: 0 3px 6px rgba(0,0,0,0.1);">
                    <h3 class="mb-3 text-center " style="font-size: 1.2rem; color: blue;">{{ currentText.siteAnalysis }}
                    </h3>

                    <v-table density="compact"
                        style="width: 100%; border-radius: 8px; overflow: hidden; text-align: left; ">
                        <tbody>
                            <tr style="background-color: #f5f5f5;text-align: left;">
                                <td> <span class="font-title-container"> {{ currentText.site }} : </span> {{
                                    report.siteDetails.Id_Site }}</td>
                                <td>
                                    <span class="font-title-container">{{ currentText.month }} : </span>
                                    <strong>{{ report.month ? (/^\d{4}-\d{2}/.test(report.month) ?
                                        report.month.substr(0, 7) : (!isNaN(Date.parse(report.month))
                                            ? (new Date(report.month).getFullYear() + '-' + String(new
                                                Date(report.month).getMonth() + 1).padStart(2, '0'))
                                            : (String(report.month).length >= 7 ? String(report.month).substr(0, 7) :
                                                report.month)
                                        )
                                    )
                                        : ''
                                    }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.entrepreneurName }} : </span>
                                    <strong>{{ report.siteDetails.Entrepreneur_English_Name }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.workingDate }} : </span>
                                    <strong>{{ report.siteDetails.Date_start_working }}</strong>
                                </td>
                            </tr>

                            <tr style="background-color: #e3f2fd;">
                                <td><span class="font-title-container">{{ currentText.bottleDayExcWinSYTD }} : </span>
                                    <strong>{{ report.saleBottleYTD?.toFixed(0) || 0 }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.totalSalesBottle }} : </span>
                                    <strong>{{ report.total_exc_bottle?.toFixed(0) || 0 }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.overWaste }} : </span> <strong> {{
                                    report.water_lost?.toFixed(0) }} %</strong></td>
                                <td><span class="font-title-container">{{ currentText.penetration }} : </span>
                                    <strong>{{ (Number(report.siteDetails?.Number_Population) > 0) ?
                                        (((Number(report.beneficiaries) || 0) /
                                            Number(report.siteDetails.Number_Population)) * 100).toFixed(1) : '0'
                                    }}%</strong>
                                </td>
                            </tr>

                            <tr style="background-color: #fce4ec;">
                                <td><span class="font-title-container">{{ currentText.bottleDayExcWinS }} : </span>
                                    <strong>{{ report.saleBottleMonthly?.toFixed(0) || 0 }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.tier }} : </span> <strong>{{ tier
                                }}</strong></td>
                                <td><span class="font-title-container">{{ currentText.nbOfOperator }} : </span>
                                    <strong>{{ report.operators?.toFixed(0) || 0 }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.popCommune }} : </span> <strong>{{
                                    report.siteDetails.Number_Population || 0 }}</strong></td>
                            </tr>
                            <tr style="background-color: #e8f5e9;">
                                <td><span class="font-title-container">{{ currentText.bottleDay }} : </span> <strong>{{
                                    report.bottlePerDay?.toFixed(0) || 0 }}</strong></td>
                                <td><span class="font-title-container">{{ currentText.dayOpen }} : </span> <strong>{{
                                    report.openDays?.toFixed(0) || 0 }}</strong></td>
                                <td><span class="font-title-container">{{ currentText.beneficiaries }} : </span>
                                    <strong>{{ (Number(report.beneficiaries) || 0).toFixed(0) }}</strong>
                                </td>
                                <td><span class="font-title-container">{{ currentText.houseHold }} : </span> <strong>{{
                                    report.siteDetails.Number_Households || 0 }}</strong></td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-card>
            </v-col>
        </v-row>


        <!-- Historic Chart -->
        <!-- <v-card class="pa-3 mb-4 mx-auto" style="max-width: 700px;" v-if="report.historicSales.length"></v-card> -->
        <v-card class="pa-3 mb-4 mx-auto" style="max-width: 1000px;">
            <h3 class="mb-2" style="font-size: 1.2rem; text-align: center;">Historic Sales</h3>
            <div style="display: flex; justify-content: center; width: 100%;">
                <canvas ref="historicChart" style="width: 90%; max-width: 1000px; height: 270px;"></canvas>
            </div>
        </v-card>

        <!-- SECTION 3: Charts -->
        <!-- SECTION 3: Charts -->
        <v-row justify="center" dense class="print-row">
            <v-col cols="12" md="8">
                <v-row dense>
                    <!-- Sales Distribution -->
                    <v-col cols="12" md="6" class="print-half">
                        <v-card class="pa-3 mb-3"
                            style="width: 100%; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #1565c0;">
                                Sales Distribution
                            </h3>
                            <div
                                style="display: flex; justify-content: center; align-items: center; height: 300px; width: 100%;">
                                <canvas ref="pieChart" width="400" height="300"
                                    style="max-width: 100%; max-height: 100%;"></canvas>
                            </div>
                        </v-card>
                    </v-col>

                    <!-- P&L Revenue -->
                    <v-col cols="12" md="6" class="print-half">
                        <v-card class="pa-3 mb-3"
                            style="width: 100%; border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                            <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #2e7d32;">
                                Expense
                            </h3>
                            <!-- <div style="display: flex; justify-content: center; align-items: center; height: 190px;">
                                <canvas ref="pillarChart" width="250" height="250"
                                    style="max-width: 250px; max-height: 250px;"></canvas>
                            </div> -->
                            <div
                                style="display: flex; justify-content: center; align-items: center; height: 300px; width: 100%;">
                                <canvas ref="pillarChart" width="400" height="300"
                                    style="max-width: 100%; max-height: 100%;"></canvas>
                            </div>
                        </v-card>
                    </v-col>
                </v-row>
            </v-col>
        </v-row>



        <!-- SECTION 4: P&L and Price/Balance -->
        <v-row dense justify="center" class="report-section" style="max-width: 1100px; margin: 0 auto;">
            <!-- Profit & Loss -->
            <v-col cols="12" md="9" class="print-half1">
                <v-card class="pa-2 mb-2"
                    style="border-radius: 12px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); font-size: 0.8rem;">
                    <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #1565c0;">
                        Profit & Loss
                    </h3>
                    <v-table density="compact" class="pl-table">
                        <thead>
                            <tr>
                                <th
                                    style="text-align: center;background-color: darkkhaki;font-weight: bold;border-radius: 10%;">
                                    Category</th>
                                <th
                                    style="text-align: center;background-color: darkkhaki;font-weight: bold;border-radius: 10%;">
                                    P&L</th>
                                <th
                                    style="text-align: center;background-color: darkkhaki;font-weight: bold;border-radius: 10%;">
                                    {{ report.month ? (isNaN(Date.parse(report.month))
                                        ? (report.month.length >= 7 ? report.month.substr(0, 7) : report.month)
                                        : (new Date(report.month).getFullYear() + '-' + String(new
                                            Date(report.month).getMonth() + 1).padStart(2, '0')))
                                        : 'Month' }}
                                </th>
                                <th
                                    style="text-align: center;background-color: darkkhaki;font-weight: bold;border-radius: 10%;">
                                    M-1</th>
                                <th
                                    style="text-align: center;background-color: darkkhaki;font-weight: bold;border-radius: 10%;">
                                    YTD</th>
                                <th
                                    style="text-align: center;background-color: darkkhaki;font-weight: bold;border-radius: 10%;">
                                    Y-1</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td rowspan="3" style="font-size: 18px; font-weight: bold; color: darkgreen;">Revenue
                                </td>
                                <td class="font-title-container">Sale</td>
                                <td>{{ ((report.sales?.Total_Income || 0) - (report.sales?.WiS_Income ||
                                    0)).toLocaleString() }}</td>
                                <td>{{ ((report.salesM1?.Total_Income || 0) - (report.salesM1?.WiS_Income ||
                                    0)).toLocaleString() }}</td>
                                <td>{{ ((report.salesYtd?.Total_Income || 0) - (report.salesYtd?.WiS_Income ||
                                    0)).toLocaleString() }}</td>
                                <td>{{ ((report.salesYtdN1?.Total_Income || 0) - (report.salesYtdN1?.WiS_Income ||
                                    0)).toLocaleString() }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">WinS</td>
                                <td>{{ report.sales?.WiS_Income?.toLocaleString() || 0 }}</td>
                                <td>{{ report.salesM1?.WiS_Income?.toLocaleString() || 0 }}</td>
                                <td>{{ report.salesYtd?.WiS_Income?.toLocaleString() || 0 }}</td>
                                <td>{{ report.salesYtdN1?.WiS_Income?.toLocaleString() || 0 }}</td>
                            </tr>
                            <tr>
                                <td style="color: red; font-size: 15px; font-weight: bold;">Total</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ report.sales?.Total_Income?.toLocaleString() || 0 }}</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ report.salesM1?.Total_Income?.toLocaleString() || 0 }}</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ report.salesYtd?.Total_Income?.toLocaleString() || 0 }}</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ report.salesYtdN1?.Total_Income?.toLocaleString() || 0 }}</td>
                            </tr>

                            <!-- Expenses -->
                            <tr>
                                <td rowspan="6" style="font-size: 18px; font-weight: bold; color: darkred;">Expenses
                                </td>
                                <td class="font-title-container">Salary</td>
                                <td>{{ report.expenses.salary_total?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesM1.salary_total?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtd.salary_total?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtdN1.salary_total?.toLocaleString() || 0 }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">Production</td>
                                <td>{{ report.expenses.production?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesM1.production?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtd.production?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtdN1.production?.toLocaleString() || 0 }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">Delivery</td>
                                <td>{{ report.expenses.delivery?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesM1.delivery?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtd.delivery?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtdN1.delivery?.toLocaleString() || 0 }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">Contribution</td>
                                <td>{{ report.expenses.contribution?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesM1.contribution?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtd.contribution?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtdN1.contribution?.toLocaleString() || 0 }}</td>
                            </tr>
                            <!-- <tr>
                                <td class="font-title-container">Other</td>
                                <td>{{ report.expenses?.Other?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesM1?.Other?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtd?.Other?.toLocaleString() || 0 }}</td>
                                <td>{{ report.expensesYtdN1?.Other?.toLocaleString() || 0 }}</td>
                            </tr> -->
                            <tr>
                                <td class="font-title-container">Other</td>
                                <td>{{ (Number(report.expenses?.technical || 0) + Number(report.expenses?.Other || 0) 
                                 + Number(report.expenses?.investment || 0)).toLocaleString() }}</td>
                                <td>{{ (Number(report.expensesM1?.technical || 0) + Number(report.expensesM1?.Other || 0) 
                                 + Number(report.expensesM1?.investment || 0)).toLocaleString() }}</td>
                                <td>{{ (Number(report.expensesYtd?.technical || 0) + Number(report.expensesYtd?.Other || 0) 
                                 + Number(report.expensesYtd?.investment || 0)).toLocaleString() }}</td>
                                <td>{{ (Number(report.expensesYtdN1?.technical || 0) + Number(report.expensesYtdN1?.Other || 0) 
                                 + Number(report.expensesYtdN1?.investment || 0)).toLocaleString() }}</td>
                            </tr>
                            <tr>
                                <td style="color: red; font-size: 15px; font-weight: bold;">Total</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ (Number(report.expenses.total_selected) || 0).toLocaleString() }}</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ (Number(report.expensesM1.total_selected) || 0).toLocaleString() }}</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ (Number(report.expensesYtd.total_selected) || 0).toLocaleString() }}</td>
                                <td style="background-color: greenyellow;font-weight: bold;">
                                    {{ (Number(report.expensesYtdN1.total_selected) || 0).toLocaleString() }}</td>
                            </tr>

                            <tr style="background-color: #e6e6fa;">
                                <td style="font-size: 16px; font-weight: bold; color: black;" colspan="2">Result</td>
                                <!-- <td class="font-title-container">Result</td> -->
                                <td><strong @click="showTotalIncome(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">
                                        {{ ((report.sales?.Total_Income || 0) -
                                            (report.expenses?.total_selected||0)).toLocaleString() }} </strong></td>
                                <td><strong @click="showTotalIncome(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">
                                    {{ ((report.salesM1?.Total_Income || 0) -
                                    (report.expensesM1?.total_selected || 0)).toLocaleString() }}</strong></td>
                                <td><strong @click="showTotalIncome(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">
                                    {{ ((report.salesYtd?.Total_Income || 0) -
                                    (report.expensesYtd?.total_selected || 0)).toLocaleString() }} </strong></td>
                                <td><strong @click="showTotalIncome(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">
                                    {{ ((report.salesYtdN1?.Total_Income || 0) -
                                    (report.expensesYtdN1?.total_selected || 0)).toLocaleString() }}</strong></td>
                            </tr>

                            <tr style="background-color: chocolate;">
                                <td style="font-size: 16px; font-weight: bold; color: black;" colspan="2">Inc Ent(Sal+Profit)</td> 
                                <!-- <td class="font-title-container">Result</td> -->
                                <td><strong @click="showTotalIncomeEntrepreneur(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">
                                    {{ ((report.sales?.Total_Income || 0) - (report.expenses?.total_selected ||
                                    0) + (report.expenses?.salary_entrepreneur || 0)).toLocaleString() }}</strong>
                                </td>
                                <td><strong @click="showTotalIncomeEntrepreneur(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">{{ ((report.salesM1?.Total_Income || 0) - (report.expensesM1?.total_selected
                                    || 0) + (report.expensesM1?.salary_entrepreneur || 0)).toLocaleString()
                                        }}</strong></td>
                                <td><strong @click="showTotalIncomeEntrepreneur(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">{{ ((report.salesYtd?.Total_Income || 0) - (report.expensesYtd?.total_selected
                                    || 0) + (report.expensesYtd?.salary_entrepreneur || 0)).toLocaleString()
                                        }}</strong></td>
                                <td><strong @click="showTotalIncomeEntrepreneur(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">{{ ((report.salesYtdN1?.Total_Income || 0) -
                                    (report.expensesYtdN1?.total_selected || 0) +
                                        (report.expensesYtdN1?.salary_entrepreneur || 0)).toLocaleString() }}</strong>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-card>
            </v-col>

            <!-- Price & Balance -->
            <v-col cols="12" md="3" class="print-half2">
                <v-card class="pa-2 mb-2"
                    style="border-radius: 12px;box-shadow: 0 2px 5px rgba(0,0,0,0.1);font-size: 0.8rem;">
                    <h3 class="mb-2" style="font-size: 1rem; text-align: center; color: #2e7d32;">
                        Price & Balance
                    </h3>
                    <v-table density="compact">
                        <thead>
                            <tr>
                                <th style="text-align: center; font-size: 13px; font-weight: bold; color: darkorchid;">
                                    Price</th>
                                <th style="text-align: center; font-size: 13px; font-weight: bold; color: darkorchid;">
                                    Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td class="font-title-container">Hod Price (៛) :</td>
                                <td>{{ Math.round(report.sales?.Hod_Price) || 0 }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">Shopkeeper (៛)</td>
                                <td>{{ Math.round(report.sales?.Shopkeeper_Price) || 0 }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">On Site (៛)</td>
                                <td>{{ Math.round(report.sales?.Onsite_Price) || 0 }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">WinS (៛)</td>
                                <td>{{ Math.round(report.sales?.WiS_Price) || 0 }}</td>
                            </tr>
                            <tr>
                                <td colspan="2" style="background-color: #e0f7fa;"></td>
                            </tr>
                            <tr>
                                <td class="font-title-container">Nb Bot YTD</td>
                                <td>{{ Number(report.nb_bottles_ytd).toFixed(0) || 0 }}</td>
                            </tr>
                            <tr>
                                <td class="font-title-container">Nb Bot Y-1</td>
                                <td>{{ Number(report.nb_bottles_ytd_n1).toFixed(0) || 0 }}</td>
                            </tr>
                            <tr>
                                <td colspan="2" style="background-color: #e0f7fa;"></td>
                            </tr>
                            <tr>
                                <td class="font-title-container" v-if="report.debtOrSave.Total_Net_Amount < 0">Savings
                                    ($)</td>
                                <td class="font-title-container" v-else>Debt ($)</td>
                                <td><strong @click="showDebtPopup(report.siteDetails.Id_Site)"
                                        style="cursor: pointer; text-decoration: underline; color: blue;">
                                        {{ Math.round((report.debtOrSave.Total_Net_Amount < 0 ?
                                            -report.debtOrSave.Total_Net_Amount :
                                            report.debtOrSave.Total_Net_Amount)/4070).toLocaleString() || 0 }} $
                                            </strong>
                                </td>
                            </tr>
                        </tbody>
                    </v-table>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import { Chart, registerables } from "chart.js";
import axios from "axios";
import Swal from "sweetalert2";

Chart.register(...registerables);

export default {
    data() {
        return {
            sites: [],
            selectedSite: null,
            currentLanguage: 'en',
            report: {
                site: null,
                sales: {},
                salesM1: {},
                salesYtd: {},
                salesYtdN1: {},
                expenses: {},
                expensesM1: {},
                expensesYtd: {},
                expensesYtdN1: {},
                historicSales: [],
                siteDetails: {},
                month: '',
                saleBottleYTD: 0,
                saleBottleMonthly: 0,
                bottlePerDay: 0,
                openDays: 0,
                total_exc_bottle: 0,
                beneficiaries: 0,
                operators: 0,
                debtOrSave: 0,
                nb_bottles_ytd: 0,
                nb_bottles_ytd_n1: 0,
                water_lost: 0,
                water_consumption: 0,
                currentMonthExpenses: [],
                averageByCategory: []
            },
            tier: null,
            chart: null,
            pieChart: null,
            pillarChart: null,
            languages: [
                { text: 'English', value: 'en' },
                { text: 'French', value: 'fr' },
                { text: 'Khmer', value: 'km' },
            ],
            selectedLanguage: 'en',
            translations: {
                en: {
                    site: 'Site',
                    month: 'Month',
                    entrepreneurName: 'Ent.Name',
                    workingDate: 'Working Date',
                    siteAnalysis: 'Site Analysis',
                    bottleDayExcWinS: 'Bottle/day exc WinS',
                    bottleDayExcWinSYTD: 'Bottle/day exc WinS YTD',
                    totalSalesBottle: 'Total Sales(Bottle)',
                    overWaste: 'Over Waste',
                    penetration: 'Penetration',
                    tier: 'Tier',
                    nbOfOperator: 'Nb of operator',
                    popCommune: 'Pop Commune',
                    bottleDay: 'Bottle/day',
                    dayOpen: 'Day Open',
                    beneficiaries: 'Beneficiaries',
                    houseHold: 'HouseHold'
                },
                fr: {
                    site: 'Site',
                    month: 'Mois',
                    entrepreneurName: 'Nom Ent.',
                    workingDate: 'Date de travail',
                    siteAnalysis: 'Analyse du site',
                    bottleDayExcWinS: 'Bouteille/jour exc WinS',
                    bottleDayExcWinSYTD: 'Bouteille/jour exc WinS YTD',
                    totalSalesBottle: 'Ventes totales (Bouteille)',
                    overWaste: 'Sur gaspillage',
                    penetration: 'Pénétration',
                    tier: 'Niveau',
                    nbOfOperator: 'Nb d\'opérateur',
                    popCommune: 'Pop Commune',
                    bottleDay: 'Bouteille/jour',
                    dayOpen: 'Jour ouvert',
                    beneficiaries: 'Bénéficiaires',
                    houseHold: 'Ménage'
                },
                km: {
                    site: 'ទីតាំង',
                    month: 'ខែ',
                    entrepreneurName: 'ឈ្មោះសហគ្រិន',
                    workingDate: 'កាលបរិច្ឆេទធ្វើការ',
                    siteAnalysis: 'ការវិភាគ',
                    bottleDayExcWinS: 'ប៊ីដុង/ថ្ងៃ អត់គិត WinS',
                    bottleDayExcWinSYTD: 'ប៊ីដុង/ថ្ងៃ អត់គិត WinS YTD',
                    totalSalesBottle: 'ការលក់សរុប(ប៊ីដុង)',
                    overWaste: 'បាត់ទឹក',
                    penetration: 'ការជ្រាបចូលទីផ្សារ',
                    tier: 'កម្រិត',
                    nbOfOperator: 'ចំនួនប្រតិបត្តិករ',
                    popCommune: 'ប្រជាជនក្នុងឃុំ',
                    bottleDay: 'ប៊ីដុង/ថ្ងៃ',
                    dayOpen: 'ចំនួនថ្ងៃបើក',
                    beneficiaries: 'អ្នកទទួលផល',
                    houseHold: 'ចំនួនគ្រួសារ'
                }
            },
            selectedDate: null,
        };
    },
    computed: {
        currentText() {
            return this.translations[this.selectedLanguage];
        }
    },
    watch: {
        selectedSite(newSite) {
            if (newSite) {
                this.fetchReport(newSite);
                this.fetchTier(newSite);
            }
        },
        selectedDate(newDate) {
            if (newDate) {
                this.fetchReport(this.selectedSite);
                this.fetchTier(this.selectedSite);
            }
        }
    },

    mounted() {
        this.fetchSites();
        const currentDate = new Date();
        currentDate.setMonth(currentDate.getMonth() - 1);
        this.selectedDate = currentDate.toISOString().slice(0, 7); // "YYYY-MM"
    },

    methods: {
        async showDebtPopup(siteId) {
            const response = await axios.get(`/api/debt-details/${siteId}`);
            const debtData = response.data;

            const DIVISOR = 4070;
            const monthOrder = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const years = Object.keys(debtData).sort((a, b) => b - a);

            let tableHtml = `
        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif; font-size: 14px;">
                <thead>
                    <tr>
                        <th style="padding: 10px; border: 1px solid #ccc; background: #2c3e50; color: white; text-align: center;">Year</th>
    `;

            // Month headers
            monthOrder.forEach(month => {
                tableHtml += `<th style="padding: 10px; border: 1px solid #ccc; background: #2c3e50; color: white; text-align: center;">${month}</th>`;
            });

            tableHtml += `</tr></thead><tbody>`;

            // Data rows
            years.forEach((year, index) => {
                const rowBgColor = index % 2 === 0 ? '#f8f9fa' : '#ffffff';

                tableHtml += `<tr style="background-color: ${rowBgColor};">`;
                tableHtml += `<td style="padding: 10px; border: 1px solid #ddd; font-weight: bold; text-align: center;">${year}</td>`;

                monthOrder.forEach(month => {
                    const originalAmount = debtData[year][month] || 0;
                    const dividedAmount = (originalAmount / DIVISOR) * -1;

                    // Remove the * -1 if you don't want to invert signs
                    const displayValue = originalAmount !== 0 ?
                        Math.round(dividedAmount).toLocaleString() : '-';

                    // Color coding: negative in red, positive in green
                    const color = dividedAmount < 0 ? 'red' : (dividedAmount > 0 ? 'green' : '#666');

                    tableHtml += `
                <td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: ${color}; font-weight: normal; font-size: 14px;">
                    ${displayValue} $
                </td>
            `;
                });

                tableHtml += `</tr>`;
            });

            tableHtml += `</tbody></table></div>`;

            Swal.fire({
                title: `<span style="font-family: Arial, sans-serif; font-size: 18px;">Balance Site ${siteId}</span>`,
                html: tableHtml,
                width: '1000px',
                showConfirmButton: false,
                showCloseButton: true,
                customClass: {
                    popup: 'debt-popup-normal-font',
                    htmlContainer: 'debt-popup-html-container'
                }
            });
        },
        async showTotalIncome(siteId) {
            try {
                const response = await axios.get(`/api/income-details/${siteId}`);
                const data = response.data.data; // your year => [months] structure

                // Months in calendar order
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

                // Start building table HTML
                let tableHtml = '<table border="1" cellspacing="0" cellpadding="5" style="width:100%; text-align:center; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif; font-size: 14px;">';

                // Header row: Year + all months
                tableHtml += '<thead><tr><th style="padding: 10px; border: 1px solid #ccc; background: #2c3e50; color: white; text-align: center;">Year</th>';
                monthNames.forEach(m => {
                    tableHtml += `<th style="padding: 10px; border: 1px solid #ccc; background: #2c3e50; color: white; text-align: center;">${m}</th>`;
                });
                tableHtml += '</tr></thead><tbody>';

                // For each year, create a row with pnl for each month
                for (const year in data) {
                    tableHtml += `<tr><td>${year}</td>`;

                    // months is an array [{month:"Jan", pnl:...}, ...]
                    const months = data[year];

                    // Create a map monthName => pnl for fast lookup
                    const pnlMap = {};
                    months.forEach(m => {
                        pnlMap[m.month] = m.pnl;
                    });

                    // For each month, output pnl or 0 if missing
                    monthNames.forEach(m => {
                        const pnlValue = pnlMap[m] ?? 0;
                        const displayValue = Math.round(pnlValue / 4070);
                        const color = displayValue < 0 ? 'red' : (displayValue > 0 ? 'green' : '#666');
                        tableHtml += `<td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: ${color}; font-weight: normal; font-size: 14px;">${displayValue.toLocaleString()} $</td>`;
                    });

                    tableHtml += '</tr>';
                }

                tableHtml += '</tbody></table>';

                Swal.fire({
                    title: 'P&L Summary',
                    html: tableHtml,
                    width: '70%',
                    confirmButtonText: 'Close',
                    scrollbarPadding: false,
                    customClass: { popup: 'swal2-scrollbar' },
                });

            } catch (error) {
                console.error('Error fetching income data:', error);
                Swal.fire('Error', 'Failed to load income data', 'error');
            }
        },
        async showTotalIncomeEntrepreneur(siteId) {
            try {
                const response = await axios.get(`/api/income-details/${siteId}`);
                const data = response.data.data; // your year => [months] structure

                // Months in calendar order
                const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

                // Start building table HTML
                let tableHtml = '<table border="1" cellspacing="0" cellpadding="5" style="width:100%; text-align:center; border-collapse: collapse; margin: 10px 0; font-family: Arial, sans-serif; font-size: 14px;">';

                // Header row: Year + all months
                tableHtml += '<thead><tr><th style="padding: 10px; border: 1px solid #ccc; background: #2c3e50; color: white; text-align: center;">Year</th>';
                monthNames.forEach(m => {
                    tableHtml += `<th style="padding: 10px; border: 1px solid #ccc; background: #2c3e50; color: white; text-align: center;">${m}</th>`;
                });
                tableHtml += '</tr></thead><tbody>';

                // For each year, create a row with pnl for each month
                for (const year in data) {
                    tableHtml += `<tr><td>${year}</td>`;

                    // months is an array [{month:"Jan", pnl:...}, ...]
                    const months = data[year];

                    // Create a map monthName => pnl for fast lookup
                    const pnlMap = {};
                    months.forEach(m => {
                        pnlMap[m.month] = m.pnl_plus_entre_salary;
                    });

                    // For each month, output pnl or 0 if missing
                    monthNames.forEach(m => {
                        const pnlValue = pnlMap[m] ?? 0;
                        const displayValue = Math.round(pnlValue / 4070);
                        const color = displayValue < 0 ? 'red' : (displayValue > 0 ? 'green' : '#666');
                        tableHtml += `<td style="padding: 10px; border: 1px solid #ddd; text-align: center; color: ${color}; font-weight: normal; font-size: 14px;">${displayValue.toLocaleString()} $</td>`;
                    });

                    tableHtml += '</tr>';
                }

                tableHtml += '</tbody></table>';

                Swal.fire({
                    title: 'Total Entrepreneur Income Summary',
                    html: tableHtml,
                    width: '70%',
                    confirmButtonText: 'Close',
                    scrollbarPadding: false,
                    customClass: { popup: 'swal2-scrollbar' },
                });

            } catch (error) {
                console.error('Error fetching income data:', error);
                Swal.fire('Error', 'Failed to load income data', 'error');
            }
        },
        async fetchTier(siteId) {
            // Prevent API call if siteId is not valid
            if (!siteId) {
                this.tier = null;
                return;
            }

            // Smart month logic: 
            // - If day >= 15 → use last month
            // - If day < 15 → use 2 months ago
            const now = this.selectedDate
                ? (typeof this.selectedDate === 'string' ? new Date(this.selectedDate + '-01') : new Date(this.selectedDate))
                : new Date();
            const currentDay = now.getDate();
            // const now = new Date();
            // const currentDay = now.getDate();

            let targetMonthOffset = currentDay >= 15 ? 1 : 2;
            const targetDate = new Date(now.getFullYear(), now.getMonth() - targetMonthOffset, 1); // 1st of target month

            const year = targetDate.getFullYear();
            const month = String(targetDate.getMonth() + 1).padStart(2, '0');
            const targetMonth = `${year}-${month}`;

            try {
                const response = await axios.get(
                    `https://dashboard.teuksaat1001.com/api/tier?site=${siteId}&month=${targetMonth}`,
                    {
                        withCredentials: false
                    }
                );

                this.tier = response.data.tier;
                console.log('Tier Data:', this.tier);
            } catch (err) {
                this.error = err.response?.data?.message || err.message || 'Failed to fetch data';
                console.error('API Error:', err);
                this.tier = null; // Optional: reset on error
            } finally {
                this.loading = false;
            }
        },
        printReport() {
            window.print();
        },

        async fetchSites() {
            try {
                const { data } = await axios.get("/api/sites");
                this.sites = data;
            } catch (err) {
                console.error("Failed to fetch sites", err);
                this.sites = [];
            }
        },
        arrayToObject(arr) {
            const obj = {};
            let totalSelected = 0; // total of selected categories

            if (Array.isArray(arr)) {
                arr.forEach(e => {
                    const key = e.expense_category?.toLowerCase() || 'unknown';
                    const value = e.total_expenses || 0;

                    obj[key] = (obj[key] || 0) + value;

                    // sum only specific categories
                    if (['salary_total', 'production', 'contribution', 'delivery'].includes(key)) {
                        totalSelected += value;
                    }
                });
            }
            // attach the total to the object
            obj.total_selected = totalSelected;

            return obj;
        },
        async fetchReport(siteId) {

            try {
                Swal.fire({
                    title: "Loading data...",
                    allowOutsideClick: false,
                    didOpen: () => Swal.showLoading(),
                });
                const { data } = await axios.get(`/api/reports/${siteId}?month=${this.selectedDate}`);
                Swal.close();

                if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
                    Swal.fire("No data", "No report data available for this site", "info");
                    return;
                }
                const expensesObj = {};
                if (Array.isArray(data.expenses)) {
                    data.expenses.forEach(e => {
                        const key = e.expense_category?.toLowerCase() || 'unknown';
                        expensesObj[key] = e.total_expenses || 0;
                    });
                }
                this.report = {
                    site: data.site || null,
                    sales: data.sales || {},
                    salesM1: data.salesM1 || {},
                    salesYtd: data.salesYtd || {},
                    salesYtdN1: data.salesYtdN1 || {},
                    expenses: this.arrayToObject(data.expenses),
                    expensesM1: this.arrayToObject(data.expensesM1),
                    expensesYtd: this.arrayToObject(data.expensesYTD),
                    expensesYtdN1: this.arrayToObject(data.expensesYTD_N1),
                    historicSales: Array.isArray(data.historicSales) ? data.historicSales : [],
                    siteDetails: data.siteDetails || {},
                    month: data.month || '',
                    saleBottleYTD: data.salesYtd?.avg_sales_per_day || 0,
                    saleBottleMonthly: data.sales?.monthly_avg_non_wis_sales_per_day || 0,
                    bottlePerDay: data.sales?.monthly_avg_sales_per_day || 0,
                    openDays: data.sales?.Number_open_days || 0,
                    total_exc_bottle: data.sales?.total_excluding_bottles || 0,
                    beneficiaries: (data.beneficiaries && (data.beneficiaries.Beneficiaries || (Array.isArray(data.beneficiaries) && data.beneficiaries[0]?.Beneficiaries))) || 0,
                    operators: data.indicatorsOp?.Number_of_Operator || 0,
                    debtOrSave: data.debt || 0,
                    nb_bottles_ytd: data.bottlesYtd?.total_bottles || 0,
                    nb_bottles_ytd_n1: data.bottlesN1?.total_bottles || 0,
                    water_consumtion: data.indicatorsOp?.Water_Consume || 0,
                    currentMonthExpenses: Array.isArray(data.currentMonthExpenses) ? data.currentMonthExpenses : [],
                    averageByCategory: Array.isArray(data.averageByCategory) ? data.averageByCategory : [],
                };
                this.report.water_lost = ((this.report.water_consumtion / (this.report.total_exc_bottle * 20)) - 1) * 100 || 0;
                this.$nextTick(() => {
                    this.renderHistoricChart();
                    this.renderPieChart();
                    this.renderPillarChart();
                });
            } catch (err) {
                Swal.close();
                Swal.fire("Error", "Failed to load report data", "error");
            }
        },

        renderHistoricChart() {
            const chartRef = this.$refs.historicChart;
            if (!chartRef || !Array.isArray(this.report.historicSales) || !this.report.historicSales.length) {
                console.warn("No historic sales data found or ref missing");
                return;
            }

            const ctx = chartRef.getContext("2d");
            if (this.chart) this.chart.destroy();

            // Prepare month labels
            const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            const salesByYear = {};

            this.report.historicSales.forEach(item => {
                // Ensure valid date
                const parsedDate = new Date(item.Month);
                if (isNaN(parsedDate)) {
                    console.warn("Invalid Month format:", item.Month);
                    return;
                }

                const year = parsedDate.getFullYear();
                const monthIndex = parsedDate.getMonth();

                if (!salesByYear[year]) salesByYear[year] = Array(12).fill(null);
                salesByYear[year][monthIndex] = item.net_sales || 0;
            });

            const colors = ["#42A5F5", "#66BB6A", "#FFA726", "#AB47BC"];
            const datasets = Object.keys(salesByYear).map((year, i) => ({
                label: year,
                data: salesByYear[year],
                borderColor: colors[i % colors.length],
                backgroundColor: colors[i % colors.length],
                fill: false,
                tension: 0.3,
                pointRadius: 3,
                spanGaps: false
            }));

            this.chart = new Chart(ctx, {
                type: "line",
                data: {
                    labels: months,
                    datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            labels: { font: { size: 10 } }
                        }
                    },
                    scales: {
                        x: { title: { display: true, text: "" } },
                        y: { beginAtZero: true, title: { display: true, text: "Bot/day Exc Wins" } }
                    }
                }
            });
        },

        renderPieChart() {
            if (!this.$refs.pieChart || !this.report.sales) return;
            const ctx = this.$refs.pieChart.getContext("2d");
            if (this.pieChart) this.pieChart.destroy();

            // Convert values safely (handles "1,234", null, undefined)
            const toNumber = v => Number(String(v ?? 0).replace(/,/g, '')) || 0;

            const labels = ["Free", "HOD", "Onsite", "Shopkeeper", "WinS"];
            const colors = ["#42A5F5", "#66BB6A", "#FFA726", "#AB47BC", "#EF5350"];

            const values = [
                toNumber(this.report.sales.Free_Sales),
                toNumber(this.report.sales.Hod_Sales),
                toNumber(this.report.sales.Onsite_Sales),
                toNumber(this.report.sales.Shopkeeper_Sales),
                toNumber(this.report.sales.WiS_Sales),
            ];

            const total = values.reduce((a, b) => a + b, 0);

            try {
                this.pieChart = new Chart(ctx, {
                    type: "doughnut",
                    data: {
                        labels,
                        datasets: [{
                            data: values,
                            backgroundColor: colors,
                            borderColor: "#fff",
                            borderWidth: 1,
                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: "50%",
                        animation: false,
                        plugins: {
                            legend: {
                                position: "bottom",
                                labels: {
                                    font: { size: 10 },

                                    // 👇 Fade legend for zero values (optional but nice)
                                    generateLabels(chart) {
                                        const data = chart.data;
                                        return data.labels.map((label, i) => {
                                            const value = data.datasets[0].data[i];
                                            return {
                                                text: label,
                                                fillStyle: data.datasets[0].backgroundColor[i],
                                                hidden: false,
                                                strokeStyle: "#fff",
                                                lineWidth: 1,
                                                fontColor: value === 0 ? "#bbb" : "#000"
                                            };
                                        });
                                    }
                                }
                            },
                            tooltip: { enabled: false },
                        },
                        animation: {
                            onComplete: function () {
                                if (!total) return;

                                const chart = this;
                                const { ctx } = chart;
                                ctx.save();
                                ctx.font = "bold 10px Arial";
                                ctx.fillStyle = "#fff";
                                ctx.textAlign = "center";
                                ctx.textBaseline = "middle";

                                chart.data.datasets[0].data.forEach((val, index) => {
                                    if (val <= 0) return;

                                    const meta = chart.getDatasetMeta(0);
                                    const element = meta.data[index];
                                    const percent = ((val / total) * 100).toFixed(1);
                                    const center = element.getCenterPoint();

                                    ctx.fillText(`${percent}%`, center.x, center.y);
                                });

                                ctx.restore();
                            }
                        }
                    }
                });
            } catch (err) {
                console.error("Failed to render pie chart:", err);
            }
        },

        renderPillarChart() {
            if (!this.$refs.pillarChart) {
                console.warn("Pillar chart ref missing");
                return;
            }

            if (!this.report.currentMonthExpenses || !this.report.averageByCategory ||
                this.report.currentMonthExpenses.length === 0 || this.report.averageByCategory.length === 0) {
                console.warn("Expense data missing or empty");
                return;
            }

            const ctx = this.$refs.pillarChart.getContext("2d");
            if (this.pillarChart) this.pillarChart.destroy();

            // Define the specific categories we want to show
            const targetCategories = ['salary', 'delivery', 'production', 'contribution'];

            // Filter and prepare data only for target categories
            const categories = [];
            const siteExpenses = [];
            const averageExpenses = [];

            targetCategories.forEach(targetCategory => {
                // Find current site expense for this category (with null check)
                const siteExpense = this.report.currentMonthExpenses.find(exp =>
                    exp.Category_expenses && exp.Category_expenses.toLowerCase() === targetCategory.toLowerCase()
                );

                // Find average expense for this category (with null check)
                const avgExpense = this.report.averageByCategory.find(exp =>
                    exp.Category_expenses && exp.Category_expenses.toLowerCase() === targetCategory.toLowerCase()
                );

                // Only add if we have data for at least one of them
                if (siteExpense || avgExpense) {
                    categories.push(targetCategory.charAt(0).toUpperCase() + targetCategory.slice(1)); // Capitalize
                    siteExpenses.push(siteExpense ? Number(siteExpense.total_expenses) : 0);
                    averageExpenses.push(avgExpense ? Number(avgExpense.average_expenses) : 0);
                }
            });

            // If no data found for any target categories, show message
            if (categories.length === 0) {
                console.warn("No data found for target categories");
                return;
            }

            console.log('Filtered Categories:', categories);
            console.log('Site Expenses:', siteExpenses);
            console.log('Average Expenses:', averageExpenses);

            try {
                this.pillarChart = new Chart(ctx, {
                    type: "bar",
                    data: {
                        labels: categories,
                        datasets: [
                            {
                                label: "Average",
                                data: siteExpenses,
                                backgroundColor: "#42A5F5",
                                borderColor: "#1E88E5",
                                borderWidth: 1,
                                barPercentage: 0.6, // Make bars wider
                                categoryPercentage: 0.8,
                            },
                            {
                                label: "Kiosk",
                                data: averageExpenses,
                                backgroundColor: "#66BB6A",
                                borderColor: "#43A047",
                                borderWidth: 1,
                                barPercentage: 0.6, // Make bars wider
                                categoryPercentage: 0.8,
                            }
                        ],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: "Amount ($)",
                                    font: { size: 12 }
                                },
                                ticks: {
                                    font: { size: 11 },
                                    callback: function (value) {
                                        return '$' + value.toLocaleString();
                                    }
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    // text: "Expense Category", 
                                    text: "",
                                    font: { size: 12 }
                                },
                                ticks: {
                                    font: { size: 11 }
                                }
                            },
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: {
                                    font: { size: 12 },
                                    boxWidth: 12
                                }
                            },
                            tooltip: {
                                enabled: true,
                                callbacks: {
                                    label: function (context) {
                                        return `${context.dataset.label}: $${context.parsed.y.toLocaleString()}`;
                                    }
                                }
                            }
                        },
                        layout: {
                            padding: {
                                left: 10,
                                right: 10,
                                top: 10,
                                bottom: 10
                            }
                        }
                    },
                });
                console.log('Chart rendered successfully with categories:', categories);
            } catch (err) {
                console.error("Failed to render pillar chart:", err);
            }
        },
    }
};
</script>

<style scoped>
/* ==============================
   General Table and Layout Styles
   ============================== */
.pl-table th,
.pl-table td,
.v-table th,
.v-table td {
    padding: 2px 4px !important;
    text-align: center;
    font-size: 9pt;

}

.debt-popup-normal-font {
    font-family: Arial, sans-serif !important;
}

.debt-popup-normal-font table {
    font-family: Arial, sans-serif !important;
    font-size: 14px !important;
}

.debt-popup-normal-font td,
.debt-popup-normal-font th {
    font-family: Arial, sans-serif !important;
    font-size: 14px !important;
}

.debt-popup-html-container {
    font-family: Arial, sans-serif !important;
}

.report-container {
    padding: 8px !important;
}

.report-container canvas {
    max-width: 100%;
    height: auto;
}

.khmer-mode {
    font-size: 105%;
    line-height: 1.4;
}

.khmer-mode .v-table,
.khmer-mode .v-card,
.khmer-mode .v-btn {
    font-size: 1.05em;
}

.khmer-mode h3 {
    font-size: 1.25rem;
}

.font-title-container {
    font-size: 12.5px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 12px;
    color: #333;
    font-family: 'Arial', sans-serif;
}

.khmer-mode .pl-table th,
.khmer-mode .pl-table td,
.khmer-mode .v-table th,
.khmer-mode .v-table td {
    font-size: 9.5pt;
    /* Slightly larger for Khmer */
}

/* ==============================
   Print Styling
   ============================== */
@media print {

    /* -------- Page Setup -------- */
    @page {
        size: A4 portrait;
        margin: 0.5cm;
    }

    html,
    body {
        margin: 0 !important;
        padding: 0 !important;
        zoom: 0.85;
        /* Scales everything to fit one page */
    }

    /* -------- Container -------- */
    .report-container {
        padding: 2mm !important;
        font-size: 7pt !important;
        transform: scale(0.95);
        transform-origin: top left;
    }

    /* -------- No-print elements -------- */
    .no-print {
        display: none !important;
    }

    /* -------- Cards -------- */
    .v-card {
        margin-bottom: 1mm !important;
        padding: 1mm !important;
        page-break-inside: avoid !important;
        box-shadow: none !important;
        border: 0.2mm solid #ccc !important;
    }

    /* -------- Headings -------- */
    h3 {
        font-size: 7pt !important;
        margin-bottom: 1mm !important;
        text-align: center !important;
    }

    /* -------- Layout (columns) -------- */
    .v-row {
        display: flex !important;
        flex-wrap: nowrap !important;
        justify-content: space-between !important;
        align-items: flex-start !important;
    }

    /* Equal column layout */
    .print-half {
        flex: 1 0 50% !important;
        max-width: 50% !important;
        box-sizing: border-box;
        padding: 0 1mm !important;
    }

    /* 70-30 split layout */
    .print-half1 {
        flex: 0 0 70% !important;
        max-width: 70% !important;
        box-sizing: border-box;
        padding: 0 1mm !important;
    }

    .print-half2 {
        flex: 0 0 30% !important;
        max-width: 30% !important;
        box-sizing: border-box;
        padding: 0 1mm !important;
    }

    /* -------- Tables -------- */
    .v-table {
        font-size: 6pt !important;
        width: 100% !important;
        border-collapse: collapse !important;
    }

    .v-table td,
    .v-table th {
        padding: 1px !important;
    }

    /* -------- Charts -------- */
    canvas {
        max-height: 60mm !important;
        /* reduced to ensure fits in one page */
        width: 100% !important;
        height: auto !important;
    }

    .historic-chart-canvas {
        max-height: 55mm !important;
        width: 100% !important;
        height: auto !important;
    }

    /* -------- Prevent breaks -------- */
    .v-card,
    .v-table,
    .v-row {
        page-break-before: avoid !important;
        page-break-after: avoid !important;
        page-break-inside: avoid !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* -------- Scale all content to one page -------- */
    body {
        transform: scale(0.9);
        transform-origin: top center;
    }
}
</style>
