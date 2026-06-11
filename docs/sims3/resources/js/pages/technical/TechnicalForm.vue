<template>
    <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
        <v-progress-circular :size="50" color="primary" indeterminate></v-progress-circular>
    </div>

    <v-form v-if="!loading" @submit.prevent="saveTechnicalForm">
        <h3 class="mb-4">
            <v-btn v-if="receivedId == 'getDialog'" color="primary" class="mx-5" icon="mdi-arrow-left"
                @click="$emit('cancel-modal')" />
            <!-- <v-btn v-if="receivedId =='getParam'" color="primary" class="mx-5" icon="mdi-arrow-left" @click="$router.go(-1)" /> -->
        </h3>
        <v-card prepend-icon="mdi-card-account-details-outline" title="Site_Problem" class="mb-6 rounded-lg">
            <v-card-text>
                <v-row>
                    <v-col cols="12" md="2">
                        <v-autocomplete v-model="technical.site" label="Site" density="compact"
                            :items="Object.keys(sites)" :readonly="edit" :rules="required" />
                    </v-col>
                    <v-col cols="12" md="2">
                        <!-- problem-date -->
                        <v-text-field v-model="technical.problem_date" type="date" density="compact"
                            label="Problem Date" hide-details="auto" :readonly="edit" :rules="required" />
                    </v-col>
                    <v-col cols="12" md="2">
                        <v-select v-model="technical.site_problem_description" label="Probley type" density="compact"
                            hide-details="auto" :items="problem_list" item-title="problem_category"
                            @update:model-value="technical.sub_problem_description = '';" :readonly="edit"
                            :rules="required" />
                    </v-col>
                    <v-col cols="12" md="2">
                        <v-select v-if="technical.site_problem_description" v-model="technical.sub_problem_description"
                            label="sub_problem" density="compact" hide-details="auto"
                            :items="problem_list.find((el) => el.problem_category === technical.site_problem_description)?.sub_problem ?? []"
                            item-title="name" />
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-text-field v-model="technical.comment_problem" density="compact" label="Detail problem"
                            hide-details="auto" :readonly="edit" :rules="required" />
                    </v-col>
                </v-row>
            </v-card-text>
            <v-card-text>
                <v-row>
                    <v-col cols="12" md="3">
                        <v-text-field v-model="technical.report_by" density="compact" label="Report By"
                            hide-details="auto" :readonly="true" :rules="required" />
                    </v-col>
                    <v-col cols="12" md="2">
                        <v-text-field v-model="technical.phone_number" density="compact" label="Phone Number"
                            type="number" hide-details="auto" />
                    </v-col>
                    <v-col cols="12" md="2">
                        <v-select v-model="technical.problem_status" label="Status" density="compact"
                            hide-details="auto" :items="['Can Produce', 'Can Not Produce']" :readonly="edit"
                            :rules="required" />
                    </v-col>
                    <v-col cols="12" md="2">
                        <v-select v-model="technical.stop_work" v-if="technical.problem_status == 'Can Not Produce'"
                            label="Stop operation day" density="compact" hide-details="auto"
                            :items="['0.5', '1', '2', '3', '4', '5', '6', '7', 'More than a week']" :readonly="edit" />
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
        <div v-if="edit">
            <v-card prepend-icon="mdi-card-account-details-outline" title="Intervention Description"
                class="mb-6 rounded-lg">
                <v-card-text>
                    <v-row>
                        <v-col cols="12" md="2">
                            <v-select v-model="technical.technician" label="Technician" density="compact"
                                hide-details="auto"
                                :items="['Ros Veasna', 'Pin Phalla', 'Morn Phanith', 'Pech Odom', 'Touch Bros',
                                'Neang Vuthy', 'Men Pisak', 'Sok Dara', 'Sok Darith','Khy Sopheap','Houl Vicheat','Leak Leab']"
                                :rules="required" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field v-model="technical.start_intervention" type="date" density="compact"
                                label="Start Intervention" hide-details="auto" :rules="required" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field v-model="technical.end_intervention" type="date" density="compact"
                                label="End Intervention" hide-details="auto" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select v-model="technical.reporting" label="Solutin Type" density="compact"
                                hide-details="auto"
                                :items="['Solved by Call center', 'ON-SITE(Routine)', 'ON-SITE (unplanned)']" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select v-model="technical.technician2" label="Supporting staff" density="compact"
                                hide-details="auto"
                                :items="['Ros Veasna', 'Pin Phalla', 'Morn Phanith', 'Pech Odom',
                                 'Touch Bros', 'Neang Vuthy', 'Men Pisak', 'Sok Dara', 'Sok Darith', 'Sen Sak', 'Min Theary', 'Khy Sopheap',
                                 'Andreaandrea Delsoldato','Ty Borin','Pich Sarady','Sol Visal','Moung Chanthan','Houl Vicheat','Leak Leab'
                                 ]" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select v-model="technical.Fixed" label="Fixed" density="compact" hide-details="auto"
                                :items="['', 'Fixed']" />
                        </v-col>


                    </v-row>
                    <v-row>
                        <v-col cols="12" md="3">
                            <v-btn color="success" @click="showAddSolution = true">Add</v-btn>
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-card class="mb-1 rounded-lg">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="12" md="12">
                                        <v-table density="compact">
                                            <thead>
                                                <tr>
                                                    <th class="text-left">Problem</th>
                                                    <th class="text-left">Sub Problem</th>
                                                    <th class="text-left">Solution</th>
                                                    <th class="text-left">Detail Solution</th>
                                                    <th class="text-left"></th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr v-for="item in technical.allRTProblem"
                                                    :key="item.rt_site_problem_description">
                                                    <td>{{ item.rt_problem }}</td>
                                                    <td>{{ item.rt_sub_problem }}</td>
                                                    <td>{{ item.rt_new_solution }}</td>
                                                    <td>{{ item.rt_comment }}</td>
                                                    <td>
                                                        <v-btn icon="mdi-trash-can" density="compact" color="black"
                                                            @click="deleteSolution($event, index)" />
                                                    </td>
                                                </tr>

                                            </tbody>
                                        </v-table>
                                    </v-col>

                                </v-row>
                            </v-card-text>
                        </v-card>


                    </v-row>

                </v-card-text>
            </v-card>
            <v-card prepend-icon="mdi-card-account-details-outline" title="Distance Calculation"
                class="mb-6 rounded-lg">
                <v-card-text>
                    <v-row>
                        <v-col cols="12" md="2">

                            <v-autocomplete v-model="technical.start_point" label="Start Point" density="compact"
                                :items="Object.keys(location)" />
                            <!-- append-inner-icon="mdi-microphone"
                                    auto-select-first
                                    class="flex-full-width"
                                    item-props
                                    menu-icon=""
                                    placeholder="Search Google or type a URL"
                                    prepend-inner-icon="mdi-magnify"
                                    rounded
                                    theme="light"
                                    variant="solo" -->

                        </v-col>
                        <v-col cols="12" md="2">

                            <v-autocomplete v-model="technical.end_point" label="End Point" density="compact"
                                :items="Object.keys(location)" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field v-model="technical.distance" label="Distance calculate" solo
                                density="compact" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field v-model="technical.gasoline" label="Pay $$ Gasoline" solo density="compact" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select v-model="technical.checkPrice" label="Negotiation" density="compact"
                                hide-details="auto" :items="['','Agree by entre', 'Not Agree by entre']" />
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12" md="2">
                            <v-select v-model="technical.rt_request_stock" label="Stock Need or Not" density="compact"
                                hide-details="auto" :items="['no_need', 'stock_need']" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select v-if="technical.rt_request_stock == 'stock_need'"
                                v-model="technical.item_platform" label="Technician Platform" density="compact"
                                hide-details="auto" :items="['', 'PP', 'KSP', 'BTB', 'KC', 'SR']" :rules="required" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="technical.date_need" type="date" density="compact"
                                label="Stock_Need_Date" hide-details="auto" />
                        </v-col>

                        <v-col cols="12" md="2">
                            <v-select v-model="technical.stock_type" label="Stock Type" density="compact"
                                hide-details="auto" :items="['', 'minimum_stock', 'request_stock']" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-text-field v-model="technical.item_receiver" label="Receiver" solo density="compact" />
                        </v-col>

                    </v-row>
                    <div
                        v-if=" $store.state.user.permissions.includes('edit_technical')">
                        <v-row>
                            <v-col cols="12" md="12">
                                <v-select v-model="technical.managerValidateItem" label="Validate Item"
                                    density="compact" hide-details="auto" :items="[' ', 'validated_item']" />
                            </v-col>
                        </v-row>
                    </div>
                </v-card-text>
            </v-card>
        </div>
        <!-- show intervention item -->
        <div v-if="technical.rt_request_stock == 'stock_need'">
            <v-card prepend-icon="mdi-currency-usd" title="Item Request" class="mb-3 rounded-lg">
                <v-card-text>
                    <v-row>
                        <v-col cols="12" md="12">
                            <v-table density="compact">
                                <thead>
                                    <tr>
                                        <th class="text-left">Eng Item Name</th>
                                        <th class="text-left">Kh Item Name</th>
                                        <th class="text-left">Comment</th>
                                        <th class="text-left">Month</th>
                                        <th class="text-left">Code</th>
                                        <th class="text-left">QTY</th>
                                        <th class="text-left">Price</th>
                                        <th class="text-left">Unit</th>
                                        <th class="text-left">Total</th>
                                        <th class="text-left">Who Pay</th>
                                        <th class="text-left"></th>
                                    </tr>
                                </thead>
                                <tbody>

                                    <tr v-for="item in technical.quotation" :key="item.quotation_intervention">
                                        <td>{{ item.intervention_category }}</td>
                                        <td>{{ item.intervention_subcategory }}</td>
                                        <td>{{ item.comment }}</td>
                                        <td>{{ item.send_month }}</td>
                                        <td>{{ item.item_ref }}</td>
                                        <td>{{ item.quantity }}</td>
                                        <td>{{ item.unit_price }}</td>
                                        <td>{{ item.unit }}</td>
                                        <td>{{ item.total }}</td>
                                        <td>{{ item.who_pay }}</td>
                                        <td>
                                            <v-btn icon="mdi-trash-can" density="compact" color="black"
                                                @click="deleteItem($event, index)" />
                                        </td>
                                    </tr>
                                    <tr class="text-h6">
                                        <td colspan="7" class="text-right">
                                            Total
                                        </td>
                                        <td>
                                            {{ technical.totalPriceAllItem }}
                                        </td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-col>
                        <v-col cols="12" md="4" class="d-flex flex-row align-end">
                            <v-btn v-if="technical.managerValidateItem != 'validated_item'" color="deep-orange"
                                prepend-icon="mdi-cash-plus" size="small" @click="showAddItemForm = true">
                                Request Item
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-card-text>
            </v-card>
        </div>
        <v-row class="ma-2" justify="center">

            <v-btn v-if="addForm != 'NoData'" prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4"
                size="large" @click="$emit('cancel-modal')">
                Cancel
            </v-btn>
            <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large" type="submit">
                Save
            </v-btn>
            <!-- <v-btn  prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large" type="submit" @click="validateItem()" >
                    Validate Item
                </v-btn> -->
        </v-row>

    </v-form>
    <!-- show item form -->
    <v-dialog v-model="showAddItemForm" transition="dialog-bottom-transition" width="900">
        <v-card>
            <v-card-text>
                <v-form v-if="!loading" @submit.prevent="addQuotation">
                    <v-row>
                        <v-col cols="12" md="5">
                            <v-select v-model="quoteItem.intervention_category" label="Kh_Item_Name" density="compact"
                                hide-details="auto" :items="rt_problem_list" item-title="khmer_item"
                                :rules="required" />
                        </v-col>
                        <v-col cols="12" md="5">
                            <v-select v-if="quoteItem.intervention_category"
                                v-model="quoteItem.intervention_subcategory" label="Eng_Item_Name" density="compact"
                                hide-details="auto"
                                :items="rt_problem_list.find((el) => el.khmer_item === quoteItem.intervention_category).english_item"
                                item-title="name" :rules="required" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select v-if="quoteItem.intervention_category" v-model="quoteItem.item_ref" label="Code"
                                density="compact" hide-details="auto"
                                :items="rt_problem_list.find((el) => el.khmer_item === quoteItem.intervention_category).code"
                                item-title="item_ref" :rules="required" />
                        </v-col>

                    </v-row>
                    <v-row>
                        <v-col cols="12" md="4">
                            <v-text-field v-model="quoteItem.send_month" type="month" density="compact"
                                label="Stock_Need_Date" hide-details="auto" :rules="required" />
                        </v-col>
                        <v-col cols="12" md="8">
                            <v-text-field v-model="quoteItem.comment" type="text" density="compact" label="Comment..."
                                hide-details="auto" :rules="required" />
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12" md="2">
                            <v-text-field v-model="quoteItem.quantity" type="number" density="compact" label="Quantity"
                                :rules="required" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-select v-if="quoteItem.intervention_category" v-model="quoteItem.unit_price"
                                label="Unit price" density="compact" hide-details="auto"
                                :items="rt_problem_list.find((el) => el.khmer_item === quoteItem.intervention_category).item_list"
                                item-title="unit_price" :rules="required" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-select v-if="quoteItem.intervention_category" v-model="quoteItem.unit" label="Unit"
                                density="compact" hide-details="auto"
                                :items="rt_problem_list.find((el) => el.khmer_item === quoteItem.intervention_category).units"
                                item-title="unit" :rules="required" />
                        </v-col>
                        <v-col cols="12" md="2">
                            <v-text-field v-model="quoteItem.total" density="compact" label="Total" type="number" />
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-select v-model="quoteItem.who_pay" label="Who Pay" density="compact" hide-details="auto"
                                :items="['entrepreneur_pay', 'ts_pay']" />
                        </v-col>

                    </v-row>
                    <v-row class="ma-2" justify="center">
                        <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4"
                            @click="showAddItemForm = false">
                            Cancel
                        </v-btn>
                        <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" type="submit">
                            Add Item
                        </v-btn>

                    </v-row>
                </v-form>
            </v-card-text>
        </v-card>
    </v-dialog>

    <!-- dialog for add solution -->
    <v-dialog v-model="showAddSolution" transition="dialog-bottom-transition" width="900">
        <v-card>
            <v-card-text>
                <v-form v-if="!loading" @submit.prevent="addSolution">
                    <v-row>
                        <v-col cols="12" md="4">
                            <v-select v-if="problemCategories.length > 0" v-model="newRTSolution.rt_problem"
                                label="Problem Type" density="compact" hide-details="auto" :items="problemCategories"
                                item-text="problem_category" item-value="problem_category" :rules="required" chips
                                :menu-props="{ auto: true }" />
                        </v-col>
                        <v-col cols="12" md="4">
                            <v-select v-model="newRTSolution.rt_sub_problem" label="Sub_problem" density="compact"
                                hide-details="auto" :items="filteredSubProblem" item-text="sub_problem"
                                item-value="sub_problem" item-title="sub_problem" :rules="required" chips
                                :menu-props="{ auto: true }" />

                        </v-col>
                        <v-col cols="12" md="4">
                            <v-select v-model="newRTSolution.rt_new_solution" label="Solution" density="compact"
                                hide-details="auto" :items="filteredSolution" item-text="solution" item-value="solution"
                                item-title="name" :rules="required" chips :menu-props="{ auto: true }" />
                        </v-col>
                    </v-row>
                    <v-row>
                        <v-col cols="12" md="10">
                            <v-text-field v-model="newRTSolution.rt_comment" type="text" density="compact"
                                label="Comment..." hide-details="auto" :rules="required" />
                        </v-col>
                    </v-row>
                    <v-row class="ma-2" justify="center">
                        <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4"
                            @click="showAddSolution = false">
                            Cancel
                        </v-btn>
                        <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" type="submit">
                            Save
                        </v-btn>
                    </v-row>
                </v-form>
            </v-card-text>
        </v-card>
    </v-dialog>

</template>

<script>
import axios from 'axios';
import Swal from 'sweetalert2';
export default {
    name: 'TechnicalForm',
    props: {
        getDataToForm: {
            type: Number,
            default: 0 // Or any default value you prefer
        }
    },
    emits: ['site-saved', 'cancel-modal'],
    components: {
        vSelect: window["vue-select"]
    },
    data: function () {
        return {
            id: '',
            addForm: null,
            location: [],
            sites: [],
            show: false,
            sendQuotation: [],
            dateSend: '',
            email: '',
            receivedId: '',
            edit: false,
            loading: true,
            showAddItemForm: false,
            showAddSolution: false,
            operation_stop: false,
            configurations: {},
            siteQuotation: '',
            problem_list:
                [
                    {
                        "problem": "Technical Issue",
                        "problem_category": "ការវាយតំលៃស្ថានីយ៏/Site Assessment",
                        "sub_problem": [
                            { "name": "ការវាយតំលៃស្ថានីយ៏/Site Assessment" },

                        ],
                        "solution_list": [
                            { "solution": "ការវាយតំលៃស្ថានីយ៏/Site Assessment" },

                        ]
                    },
                    {
                        "problem": "Technical Issue",
                        "problem_category": "ការឆែកស្ថានីយ័/Site Routine",
                        "sub_problem": [
                            { "name": "ការឆែកស្ថានីយ័/Site Routine" },

                        ],
                        "solution_list": [
                            { "solution": "ការឆែកស្ថានីយ័/Site Routine" },

                        ]
                    },
                    //
                    {
                        "problem": "Technical Issue",
                        "problem_category": "ប្រពន្ធភ្លើង/Grid",
                        "sub_problem": [
                            { "name": "តង់ស្យុសខ្សោយ/Voltage Drop Down" },
                            { "name": "ដាច់ភ្លើង/Electricity Cut Off" },
                            { "name": "ប្រព័ន្ធភ្លើងមិនមានសុវត្ថិភាព/Electricity System Unsafe" },
                            { "name": "អ៊ីនវើតទ័រ​ ខូចគ្នានគុណភាព/Defective quality inverter" },
                            { "name": "ឌីសុងទ័រ កុងតាក់ព្រី ខូច/Damaged outlet switch" },
                            { "name": "ខ្សែភ្លើង មិនរៀបរយ/Irregular line" },
                            { "name": "Amm តូច/Small Amm" },
                            { "name": "តំណ/Link" },
                            { "name": "ការភ្ជាប់ភ្លើង/Power connection" },
                            { "name": "ឆ្លងចរន្ត/Transmission" },
                            { "name": "ចរន្តមិនចេះថេ/Unstable current" },
                            { "name": "Dosing Pump/Dosing Pump" },
                        ],
                        "solution_list": [
                            { "solution": "ដំឡើងអូតូវុល/Install Auto Voltage Stabilizer" },
                            { "solution": "ដំឡើងអំពែរ/Increase Amperage" },
                            { "solution": "ដំឡើងទំហ៊ំខ្សែរ/Increase the cable size" },
                            { "solution": "តខ្សែរឡើងវិញ/Reconnect electrical wiring" },
                            { "solution": "ដូរថ្មីរ​ ឬ​ រៀបចំឡើងវិញ/New exchange" },
                            { "solution": "ដូរឌីសង់ទ័រថ្មី/Change a new breaker" },
                            { "solution": "ដូរថ្មីរ/New exchange" },
                            { "solution": "ដួរថ្មីរ/New exchange" },
                            { "solution": "រៀបចំ/Prepare" },
                            { "solution": "Am តាមឧបកណ៏/Am by device" },
                            { "solution": "តតំណរអោយល្អ/Check links well" },
                            { "solution": "តភ្ជាបភ្លើង​ពីបង្គោលចូលទៅស្ថានីយ័/Power connection from training school" },
                            { "solution": "វ៉ាសវ៉ុលប្រើឧបកណ៏វ៉ាស/Washer Volt Uses Washer Tool" },
                            { "solution": "តំឡើង StabiliZer​​/ Auto voltage" },
                            { "solution": "តំឡើងឬជួលជុលនឹងផ្លាស់ប្តូរ Dosing Pump​​/ Install and change dosing pump" },
                        ]
                    },

                    {
                        "problem": "Technical Issue",
                        "problem_category": "បញ្ហាម៉ូទ័រ/Motor",
                        "sub_problem": [
                            { "name": "ខ្សោយ , ខូច/Weak, broken" },
                            { "name": "ម៉ូទ័រ(AC)/Motor (AC)" },
                            { "name": "ម៉ូទ័រលឿនពេក/Motor too fast" },
                            { "name": "ពុកផុយ/Decay" }
                        ],
                        "solution_list": [
                            { "solution": "ជួសជុលដុំភ្លើង បាដាង ហ្វឺត ប្តូរថ្មីរ កង់ដង់/Repairing the light bulb, replacing the wheelbarrow" },
                            { "solution": "ជួសជុល , ប្តូរហ្វឺត, បាដាង,​ធ្យូង, ប្តូថ្មី/Repair, replace furs, badges, charcoal, replace" },
                            { "solution": "ដូ កែលំហូរទឹកត្រឡប់/Return flow water flow" },
                            { "solution": "ដូរ/Exchange" }
                        ]
                    },
                    {
                        "problem": "Technical Issue",
                        "problem_category": "សូឡា/Sola",
                        "sub_problem": [
                            { "name": "តំណរខ្សែ , ពុកផុយ (ជាន់)/Cable link, corruption (floor)" },
                            { "name": "ខ្សែដី/Ground wire" },
                            { "name": "អាគុយ/Battery" },
                            { "name": "ឆ្នាំសូឡា/Solar year" },
                            { "name": "ខ្សែ/Cable" },
                            { "name": "កូស/Kos" },
                            { "name": "ផ្ទាំងសូឡា/Solar panels" },
                            { "name": "ការថែទាំ/Maintenance" },
                        ],
                        "solution_list": [
                            { "solution": "ជួសជុល ដូរខ្សែរ/Cable replacement" },
                            { "solution": "តរខ្សែរដី/Ground wire" },
                            { "solution": "វ៉ាស់វ៉ូល/Waswol​, ជួសជុល ដូរ/Repair" },
                            { "solution": "ដូរថ្នី/New exchange, ជួសជុល ដួរ/Repair" },
                            { "solution": "តរខ្សែរដី/Ground wire" },
                            { "solution": "ឆែកតំណ/Check link" },
                            { "solution": "ដូរថ្នី/New exchange" },
                            { "solution": "ឆែកតំណ/Check link" },
                            { "solution": "សំអាត/Cleaning" },
                            { "solution": "១ សប្តាហ៏ម្តង/Once a week" },
                            { "solution": "ភ្ជាប់ឡើងវិញ/Reconnect" },
                        ]
                    },
                    {
                        "problem": "Technical Issue",
                        "problem_category": "យូវី/UV",
                        "sub_problem": [
                            { "name": "អំពូលយូវី =ខ្មៅខ្លាំង , ជើងអំពូលរលាង មិនអាចសម្លាប់មេរោកបាន (អាំងតង់ស៊ីតេពន្លីអំពូលខ្សោយ)/UV lamp = very black, light bulb leg can not kill germs (light intensity, low light bulb" },
                            { "name": "បែកកែវស្រោប ស្រអាប់/Broken glass" },
                            { "name": "បាលាស់ ខូច ស្មិមជើង/Broken foot ball" },
                            { "name": "O-Ring លេច, ជ្រាប បាត់ (Cheek the blues)/O-Ring appears, disappears (Cheek the blues)" },
                            { "name": "ខ្សែពុកផុយ ដំណរខ្សែចម្លងចរន្តមិនល្អ/Corrupt cable, bad current connection" },
                            { "name": "Sense, ខូច, បែកបាក់ ,ស្រអាប់/Sense, broken, broken, dim" },
                            { "name": "ប្រអប់បញ្ហា Error System/ Error System Error Box" },
                            { "name": "ខូចកុងទ័/The counter is broken." },

                        ],
                        "solution_list": [
                            { "solution": "ដូរអំពូល​UV, ប្រៀបធៀបសមត្តភាពUV ថ្មី និងចាស់/Replace UV lamps, compare new and old UV capabilities" },
                            { "solution": "ដូរកែវស្រោបថ្មី, លាងអោយថ្លាវិញ/Replace the glass, wash it again." },
                            { "solution": "ជួសជុល ,ដូរថ្មី (Comap-AC-DC12v)/Repair, replace (Comap-AC-DC12v)" },
                            { "solution": "ដូរ O-ring/Exchange O-ring" },
                            { "solution": "ផ្លាស់ប្តូរ, ជួសជុល/Change, repair" },
                            { "solution": "កែឆ្នៃ, ផ្លាស់ប្តូរ/Recycle, change" },
                            { "solution": "ជួសជុស, ផ្លាស់ប្តូរ/Repair, change" },
                            { "solution": "ដូរកុងទ័រ/Change counter" },
                        ]
                    },
                    {
                        "problem": "Water Quality Issue",
                        "problem_category": "បញ្ហាប្រភពទឹក/Water Source",
                        "sub_problem": [
                            { "name": "ប្រភពទឹក​ប្រែប្រួល(ល្អក, ថ្លា)/Variable water source (clear, transparent)" },
                            { "name": "សំបូរសត្វគោនិងក្របី.មនុស្ស/Abundant cattle and buffalo. People" },
                            { "name": "ប្រភពទឹកមានក្លិន, ភូក,ស្លែរ/Scented water source, mud, slime" },
                        ],
                        "solution_list": [
                            { "solution": "យ៉ាតេស្ត/Yate Test" },
                            { "solution": "ធ្វើបង ដាក់សំរាម់ រឺប្តូរប្រភពទឹក/Make a fence or change the water source" },
                            { "solution": "កូរក្លូរ. បន្សាចទឹក. ថែមធ្យូងប្តូរAE/Chloride. Drain the water. Add AE Charcoal" },
                        ]
                    },
                    {
                        "problem": "Water Quality Issue",
                        "problem_category": "ការសំអាត/Pre-treatment",
                        "sub_problem": [
                            { "name": "អាងស្តុកទឹកឆៅ/Raw Water Tanks" },
                            { "name": "ចម្រោះខ្សាច់ /Sand Filter Tank" },
                            { "name": "ចម្រោះធ្យូង /AC Filter Tank" },
                            { "name": "ចម្រោះរ៉េស៊ីន /Resin Filter Tank" },
                            { "name": "អាងស្តុកទឹកថ្លា/Storage Tank" },
                            { "name": "ភ្ជាប់ទឹកបណ្តាញ/Pipe work" },
                            { "name": "ROស្ទះ" },
                        ],
                        "solution_list": [
                            { "solution": "លាងសម្អាត់ជាមួយសាប៊ូរ/ ក្លរ/Wash with soap / chlorine" },
                            { "solution": "លាងសម្អាត់ជាមួយក្លរ/Wash with chlorine" },
                            { "solution": "ស្ងោរធ្យូង/ប្តូរធ្យូងថ្មី/Charcoal Boiler / Charcoal Replacement" },
                            { "solution": "លាងជាមួយអំបិល/Wash with salt " },
                            { "solution": "លាងជាមួយសាប៊ូរ៊/ ក្លរ/Wash with soap / chlorine " },
                            { "solution": "តរទុយោរនិងរៀបចំប្រព័ន្ធទុយោរ/Plumbing and piping system" },
                            { "solution": "លាងRo, ប្តូរRo, Main Brand/Replacement, Main Brand " },
                        ]
                    },
                    {
                        "problem": "Water Quality Issue",
                        "problem_category": "ប្រពន្ធ័ចំរោះ/Micro filter",
                        "sub_problem": [
                            { "name": "បែកបំពង់តំរង់ (សម្ពាធទឹក)/Straight pipe break (water pressure)" },
                        ],
                        "solution_list": [
                            { "solution": "ប្តូរបំពង់តំរងថ្មី/change new filter" },
                        ]
                    },
                    {
                        "problem": "Water Quality Issue",
                        "problem_category": "ប្រពន្ធ័សំលាប់មេរោគ/Treated Water",
                        "sub_problem": [
                            { "name": "ប្រភពទឹកមានក្លិន, ភូក,ស្លែរ/Scented water source, mud, slime" },
                            { "name": "ទឹកមានរស់ជាតិសាប/Fresh water" },
                            { "name": "ទឹកមានPH ទាប(រសជាតិជូរ)Water with low PH (sour taste)" },
                            { "name": "ទឹកកំបោរច្រើន/Lime juice" },
                            { "name": "ទឹកប្រៃ/Salt water" },
                            { "name": "ទឹកមានជាតិដែក(ច្រេះ)និងម៉ងកាណេស/Water contains iron (rust) and manganese" },
                            { "name": "ទឹកមានកករ(សរ, Biofilm )/Frozen water (white, Biofilm)" },
                            { "name": "មីក្រូជីរសាស /Alert micro" },
                        ],
                        "solution_list": [
                            { "solution": "យកសំណាក់ទឹកមកតេស្ត/Take a water sample to test" },
                            { "solution": "ប្រើកំបោររឺ សូដាដើម្បីបង្កើនPHទឹក/Use lime or soda to increase water PH" },
                            { "solution": "ប្រើកំបោររឺ សូដាដើម្បីបង្កើនPHទឹក/Use lime or soda to increase water PH" },
                            { "solution": "ថែមរ៉េស៊ីនដើម្បីដកកំបោរ/Add resin to remove lime" },
                            { "solution": "ប្រើប្រព័ន្ធ Ro/use RO" },
                            { "solution": "ប្រើ green sand/ Use green sand " },
                            { "solution": "ស្ងោធ្យូង,លាងប្រព័ន្ធចម្រោប្រើCL ប្រព័ន្ធចម្រោះUF,ប្តូរប្រភពទឹក" },
                            { "solution": "មីក្រូជីរសាស /Alert micro" },
                        ]
                    },
                    {
                        "problem": "Entrepreneur Training",
                        "problem_category": "បណ្តុះបណ្តាល/Training",
                        "sub_problem": [
                            { "name": "ដូរសហគ្រិន/Change Entrepreneur" },
                            { "name": "បញ្ហារផ្សេងៗ/Other issues" },
                        ],
                        "solution_list": [
                            { "solution": "បង្រៀនសហគ្រិនថ្មី/Teaching new entrepreneur" },
                            { "solution": "ត្រូវការសេសេរបន្ថែមនៅអ្វីដែរថ្មី/Need to write more on something new." },
                        ]
                    }
                ],
            rt_problem_list: [
                {
                    "khmer_item": "Braided hose SS304 - 1.0m - 1 Female threaded",
                    "english_item":
                        [
                            { "name": "Braided hose SS304 - 1.0m - 1 Female threaded" },
                        ],
                    "code": [{ "item_ref": "201203" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "40700" }
                    ]
                },
                {
                    "khmer_item": "Gel battery solar 12V 200AHGel battery solar 12V 200AH",
                    "english_item":
                        [
                            { "name": "Gel battery solar 12V 200AH" },
                        ],
                    "code": [{ "item_ref": "113003" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "1118700" }
                    ]
                },
                {
                    "khmer_item": "Stainless Steel tank horizontal - 2000L",
                    "english_item":
                        [
                            { "name": "Stainless Steel tank horizontal - 2000L" },
                        ],
                    "code": [{ "item_ref": "215012" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "849700" }
                    ]
                },
                {
                    "khmer_item": "AguaTapone UV sensor SUV-G4HV05IS-SW3",
                    "english_item":
                        [
                            { "name": "AguaTapone UV sensor SUV-G4HV05IS-SW3" },
                        ],
                    "code": [{ "item_ref": "208017" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "397700" }
                    ]
                },
                {
                    "khmer_item": "Potassium Iodide Solution, 20% (Hach)",
                    "english_item":
                        [
                            { "name": "Potassium Iodide Solution, 20% (Hach)" },
                        ],
                    "code": [{ "item_ref": "502069" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "16300" }
                    ]
                },
                {
                    "khmer_item": "AguaTopone Ballast model ZUM1A-800-120",
                    "english_item":
                        [
                            { "name": "AguaTopone Ballast model ZUM1A-800-120" },
                        ],
                    "code": [{ "item_ref": "208015" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "339845" }
                    ]
                },

                {
                    "khmer_item": "AguaTopone ST08-T575",
                    "english_item":
                        [
                            { "name": "AguaTopone ST08-T575" },
                        ],
                    "code": [{ "item_ref": "208001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "875050" }
                    ]
                },
                {
                    "khmer_item": "អំពូល UV ម៉ាក Aquatopone",
                    "english_item":
                        [
                            { "name": "AguaTopone UV lamp model Philips TUV 36T5 HP 4P SE" },
                        ],
                    "code": [{ "item_ref": "208013" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "120000" }
                    ]
                },
                {
                    "khmer_item": "ឧបករណ៍ការពារលើសតង់ស្យុង",
                    "english_item":
                        [
                            { "name": "Voltage Protector 1A-63A" },
                        ],
                    "code": [{ "item_ref": "105008" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "32800" }
                    ]
                },
                {
                    "khmer_item": "Autovoltage stabilizer 1000VA",
                    "english_item":
                        [
                            { "name": "Autovoltage stabilizer 1000VA" },
                        ],
                    "code": [{ "item_ref": "208008" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "161000" }
                    ]
                },
                {
                    "khmer_item": "TRS Refined Salt, 50KG/Bag",
                    "english_item":
                        [
                            { "name": "TRS Refined Salt, 50KG/Bag" },
                        ],
                    "code": [{ "item_ref": "501009" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "800" }
                    ]
                },
                {
                    "khmer_item": "ម៉ាស៊ីនUV VIQUA VH410M",
                    "english_item":
                        [
                            { "name": "VIQUA VH410M" },
                        ],
                    "code": [{ "item_ref": "208002" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "4627400" }
                    ]
                },
                {
                    "khmer_item": "Braided hose PVC - 1.5m - 1/2' Female threaded",
                    "english_item":
                        [
                            { "name": "Braided hose PVC - 1.5m - 1/2' Female threaded" },
                        ],
                    "code": [{ "item_ref": "201205" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "21800" }
                    ]
                },
                {
                    "khmer_item": "Auto-stop valve SS304 1/2' Male threaded",
                    "english_item":
                        [
                            { "name": "Auto-stop valve SS304 1/2' Male threaded" },
                        ],
                    "code": [{ "item_ref": "207301" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "38500" }
                    ]
                },
                {
                    "khmer_item": "Dosing Pump",
                    "english_item":
                        [
                            { "name": "Dosing Pump" },
                        ],
                    "code": [{ "item_ref": "212017" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "415668" }
                    ]
                },
                {
                    "khmer_item": "តម្រងសំឡី 1µm ខ្នាតធំ ប្រវែង 20/1µm big",
                    "english_item":
                        [
                            { "name": " filter fitting with 20 length house" },
                        ],
                    "code": [{ "item_ref": "211007" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "35000" }
                    ]
                },
                {
                    "khmer_item": "តម្រងសំឡី 1µm ប្រវែង20",
                    "english_item":
                        [
                            { "name": "1µm filter fitting with 20 length house" },
                        ],
                    "code": [{ "item_ref": "211005" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "6200" }
                    ]
                },
                {
                    "khmer_item": "តម្រងសំឡី 5µm ប្រវែង20",
                    "english_item":
                        [
                            { "name": "5µm filter fitting with 20 length house" },
                        ],
                    "code": [{ "item_ref": "211006" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "6200" }
                    ]
                },


                {
                    "khmer_item": "បំពង់កែវ មីក្រូហ្វីលធ័រ",
                    "english_item":
                        [
                            { "name": "10 cartridge filter housing fitting with Ø27 (3/4)" },
                        ],
                    "code": [{ "item_ref": "209002" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "91600" }
                    ]
                },

                {
                    "khmer_item": "នាឡិកាទឹក",
                    "english_item":
                        [
                            { "name": "Mechanical Water meter" },
                        ],
                    "code": [{ "item_ref": "213004" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "91600" }
                    ]
                },
                {
                    "khmer_item": "Antiscalant",
                    "english_item":
                        [
                            { "name": "Antiscalant" },
                        ],
                    "code": [{ "item_ref": "501006" }],
                    "units": [{ "unit": "Liter(s)" }],
                    "item_list": [
                        { "unit_price": "55600" }
                    ]
                },
                {
                    "khmer_item": "Citric Acid",
                    "english_item":
                        [
                            { "name": "Citric Acid" },
                        ],
                    "code": [{ "item_ref": "501008" }],
                    "units": [{ "unit": "kg" }],
                    "item_list": [
                        { "unit_price": "8500" }
                    ]
                },
                {
                    "khmer_item": "Granular Sodium Hydroxide (NaOH)",
                    "english_item":
                        [
                            { "name": "Granular Sodium Hydroxide (NaOH)" },
                        ],
                    "code": [{ "item_ref": "501005" }],
                    "units": [{ "unit": "kg" }],
                    "item_list": [
                        { "unit_price": "9800" }
                    ]
                },
                {
                    "khmer_item": "ឧបករណ៍ទប់លំនឹងភ្លើង ២២០ វ៉ុល",
                    "english_item":
                        [
                            { "name": "Auto Voltage Stabilizer" },
                        ],
                    "code": [{ "item_ref": "208009" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "0" }
                    ]
                },
                {
                    "khmer_item": "Hydrochloric acid 35%",
                    "english_item":
                        [
                            { "name": "Hydrochloric acid 35%" },
                        ],
                    "code": [{ "item_ref": "501007" }],
                    "units": [{ "unit": "lites" }],
                    "item_list": [
                        { "unit_price": "2500" }
                    ]
                },
                {
                    "khmer_item": "ឆ្នាំងសាក / ឧបករណ៍បញ្ជា ",
                    "english_item":
                        [
                            { "name": "Charger/controller" },
                        ],
                    "code": [{ "item_ref": "113001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "180900" }
                    ]
                },
                {
                    "khmer_item": "ឆ្នាំងសាក / ឧបករណ៍បញ្ជា ",
                    "english_item":
                        [
                            { "name": "Solar charger controller MPPT 40A" },
                        ],
                    "code": [{ "item_ref": "113002" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "284800" }
                    ]
                },
                {
                    "khmer_item": "ម៉ាស៊ីនបូមទឹកឆៅ (Gazoil) - ក្រុមហ៊ុន Honda",
                    "english_item":
                        [
                            { "name": "Honda pump SEH-50X" },
                        ],
                    "code": [{ "item_ref": "212007" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "1128900" }
                    ]
                },
                {
                    "khmer_item": "DC pump 12V type SEAFLO - 18.9LPM",
                    "english_item":
                        [
                            { "name": "DC pump 12V type SEAFLO - 18.9LPM" },
                        ],
                    "code": [{ "item_ref": "212010" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "432300" }
                    ]
                },
                {
                    "khmer_item": "DC pump 12V type impeller - 23 LPM",
                    "english_item":
                        [
                            { "name": "DC pump 12V type impeller - 23 LPM" },
                        ],
                    "code": [{ "item_ref": "212015" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "457700" }
                    ]
                },
                {
                    "khmer_item": "COMAP UV lamp model Philips 36W",
                    "english_item":
                        [
                            { "name": "COMAP UV lamp model Philips 36W" },
                        ],
                    "code": [{ "item_ref": "208011" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "190400" }
                    ]
                },
                {
                    "khmer_item": "រិញ VIQUA",
                    "english_item":
                        [
                            { "name": "VIQUA Oring MODEL: 410867" },
                        ],
                    "code": [{ "item_ref": "213004" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "12500" }
                    ]
                },
                {
                    "khmer_item": "VIQUA Quartz sleeve model QSO-410",
                    "english_item":
                        [
                            { "name": "VIQUA quart sleeve MODEL: QSO-410" },
                        ],
                    "code": [{ "item_ref": "208004" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "335700" }
                    ]
                },
                {
                    "khmer_item": "VIQUA Controller model BA-ICE-CM",
                    "english_item":
                        [
                            { "name": "VIQUA Controller model BA-ICE-CM" },
                        ],
                    "code": [{ "item_ref": "208006" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "2201900" }
                    ]
                },
                {
                    "khmer_item": "Vertical water level controller float switch",
                    "english_item":
                        [
                            { "name": "Vertical water level controller float switch" },
                        ],
                    "code": [{ "item_ref": "105001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "0" }
                    ]
                },
                {
                    "khmer_item": "Inverter 600W type Pure sine wave",
                    "english_item":
                        [
                            { "name": "Inverter 600W type Pure sine wave" },
                        ],
                    "code": [{ "item_ref": "112001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "24500" }
                    ]
                },
                {
                    "khmer_item": "COMAP Quartz sleeve",
                    "english_item":
                        [
                            { "name": "COMAP Quartz sleeve" },
                        ],
                    "code": [{ "item_ref": "208012" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "280900" }
                    ]
                },
                {
                    "khmer_item": "PAC (ពហុអាលុយមីញ៉ូមក្ល) ពណ៏លឿង",
                    "english_item":
                        [
                            { "name": "PAC (Poly Aluminum Chloride) - Yellow" },
                        ],
                    "code": [{ "item_ref": "501003" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "84700" }
                    ]
                },
                {
                    "khmer_item": "កំបោរ",
                    "english_item":
                        [
                            { "name": "Lime" },
                        ],
                    "code": [{ "item_ref": "501002" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "69200" }
                    ]
                },
                {
                    "khmer_item": "ម្សៅក្លរីន",
                    "english_item":
                        [
                            { "name": "Chlorine powder" },
                        ],
                    "code": [{ "item_ref": "501001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "10000" }
                    ]
                },
                {
                    "khmer_item": "កាបូនបានធ្វើឱ្យសកម្ម",
                    "english_item":
                        [
                            { "name": "Activated Carbon (AC)" },
                        ],
                    "code": [{ "item_ref": "210001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "336200" }
                    ]
                },
                {
                    "khmer_item": "ជ័រ",
                    "english_item":
                        [
                            { "name": "Resin" },
                        ],
                    "code": [{ "item_ref": "210006" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "317400" }
                    ]
                },
                {
                    "khmer_item": "ខ្សាច់ (ទំហំ 1)",
                    "english_item":
                        [
                            { "name": "Sand 0.2/0.5mm" },
                        ],
                    "code": [{ "item_ref": "210003" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "45000" }
                    ]
                },
                {
                    "khmer_item": "ខ្សាច់ (ទំហំ 2)",
                    "english_item":
                        [
                            { "name": "Sand 0.5/2mm" },
                        ],
                    "code": [{ "item_ref": "210004" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "45000" }
                    ]
                },
                {
                    "khmer_item": "ខ្សាច់ (ទំហំ 3)",
                    "english_item":
                        [
                            { "name": "Filter gravel 3/5 mm" },
                        ],
                    "code": [{ "item_ref": "210005" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "25300" }
                    ]
                },
                {
                    "khmer_item": "តម្រង 1 មីក្រុង",
                    "english_item":
                        [
                            { "name": "1µm filter fitting with 10 length house" },
                        ],
                    "code": [{ "item_ref": "211001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "8000" }
                    ]
                },
                {
                    "khmer_item": "តម្រង 5 មីក្រុង",
                    "english_item":
                        [
                            { "name": "5µm filter fitting with 10 length house" },
                        ],
                    "code": [{ "item_ref": "211002" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "8000" }
                    ]
                },
                {
                    "khmer_item": "តម្រង 10 មីក្រុង",
                    "english_item":
                        [
                            { "name": "10µm filter fitting with 10 length house" },
                        ],
                    "code": [{ "item_ref": "211003" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "8000" }
                    ]
                },
                {
                    "khmer_item": "តម្រង 50 មីក្រុង",
                    "english_item":
                        [
                            { "name": "50µm filter fitting with 10 length house" },
                        ],
                    "code": [{ "item_ref": "211004" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "10600" }
                    ]
                },

                {
                    "khmer_item": "Inverter (Mean well S-360-12)",
                    "english_item":
                        [
                            { "name": "Converter 350W type Mean well" },
                        ],
                    "code": [{ "item_ref": "112002" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "127200" }
                    ]
                },
                {
                    "khmer_item": "បាឡស់ (Comap) ",
                    "english_item":
                        [
                            { "name": "UV Ballast" },
                        ],
                    "code": [{ "item_ref": "208009" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "101700" }
                    ]
                },
                {
                    "khmer_item": "បាឡាស (VIQUA) ",
                    "english_item":
                        [
                            { "name": "Germicidal Lamp Eletronic Ballast" },
                        ],
                    "code": [{ "item_ref": "208009" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "101700" }
                    ]
                },
                {
                    "khmer_item": "VIQUA O-Ring model 410867 ",
                    "english_item":
                        [
                            { "name": "VIQUA Oring MODEL: 410867" },
                        ],
                    "code": [{ "item_ref": "208003" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "12500" }
                    ]
                },
                {
                    "khmer_item": "VIQUA UV lamp model S410RL-HO",
                    "english_item":
                        [
                            { "name": "VIQUA UV lamp model S410RL-HO" },
                        ],
                    "code": [{ "item_ref": "208005" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "559400" }
                    ]
                },
                {
                    "khmer_item": "VIQUA UV sensor model 254-NM-C1",
                    "english_item":
                        [
                            { "name": "VIQUA UV sensor model 254-NM-C1" },
                        ],
                    "code": [{ "item_ref": "208007" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "1957800" }
                    ]
                },
                {
                    "khmer_item": "Ballast DC 12V - 40W",
                    "english_item":
                        [
                            { "name": "Ballast DC 12V - 40W" },
                        ],
                    "code": [{ "item_ref": "208010" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "81700" }
                    ]
                },
                {
                    "khmer_item": "Inverter 600W type Pure sine wave",
                    "english_item":
                        [
                            { "name": "Inverter 600W type Pure sine wave" },
                        ],
                    "code": [{ "item_ref": "112001" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "28500" }
                    ]
                },
                {
                    "khmer_item": "COMAP Quartz sleeve",
                    "english_item":
                        [
                            { "name": "COMAP Quartz sleeve" },
                        ],
                    "code": [{ "item_ref": "208012" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "280900" }
                    ]
                },
                {
                    "khmer_item": "DC pump 12V type SEAFLO - 4.51LPM",
                    "english_item":
                        [
                            { "name": "DC pump 12V type SEAFLO - 4.51LPM" },
                        ],
                    "code": [{ "item_ref": "212014" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "0" }
                    ]
                },
                {
                    "khmer_item": "O-ring for microfilter housing",
                    "english_item":
                        [
                            { "name": "O-ring for microfilter housing" },
                        ],
                    "code": [{ "item_ref": "209009" }],
                    "units": [{ "unit": "Pc(s)" }],
                    "item_list": [
                        { "unit_price": "2000" }
                    ]
                },
                // {
                //     "khmer_item": "Other",
                //     "english_item":
                //         [
                //             { "name": "Other" },
                //         ],
                //     "code": [{ "item_ref": "000000" }],
                //     "units": [{ "unit": "Pc(s)" }],
                //     "item_list": [
                //         { "unit_price": "0" }
                //     ]
                // },

            ],
            required: [
                value => {
                    if (value) return true
                    return 'This field is required.'
                },
            ],
            check: false,
            quoteItem: {
                send_month: new Date().toJSON().slice(0, 7),
                // who_pay:'ts_pay'
            },
            newRTSolution: {
                rt_problem: null,
                rt_sub_problem: null,
                rt_new_solution: null,
                rt_comment: null,
                rt_id: null,
            },
            technical: {
                id: '',
                site: '',
                problem_date: new Date().toJSON().slice(0, 10),
                site_problem_description: null,
                sub_problem_description: null,
                comment_problem: '',
                report_by: '',
                phone_number: '',
                problem_status: '',
                stop_work: '',
                start_intervention: new Date().toJSON().slice(0, 10),
                end_intervention: new Date().toJSON().slice(0, 10),
                Fixed: '',
                item_platform: '',
                rt_comment: '',
                rt_site_problem_description: [],
                rt_sub_problem_description: [],
                reporting: '',
                rt_solution: [],
                technician: '',
                technician2: '',
                rt_advisor: '',
                managerValidateItem: '',
                start_point: '',
                end_point: '',
                distance: 0,
                gasoline: 0,
                date_need: new Date().toJSON().slice(0, 10),
                rt_request_stock: '',
                item_receiver: '',
                stock_type: '',
                totalPriceAllItem: 0,
                comment_other: '',
                quotation: [],
                allRTProblem: [],
                checkPrice:''
            },
        }
    },

    computed: {
        problemCategories() {
            return this.problem_list.map((item) => item.problem_category || "");
        },
        filteredSubProblem() {
            if (!this.newRTSolution.rt_problem || this.newRTSolution.rt_problem.length == 0) return [];
            return this.problem_list
                .filter((item) => this.newRTSolution.rt_problem.includes(item.problem_category))
                .flatMap((item) => (item.sub_problem || []).map((s) => s.name || ""));
        },
        filteredSolution() {
            if (!this.newRTSolution.rt_problem || this.newRTSolution.rt_problem.length == 0) return [];
            return this.problem_list
                .filter((item) => this.newRTSolution.rt_problem.includes(item.problem_category))
                .flatMap((item) => (item.solution_list || []).map((s) => s.solution || ""));
        }
    },
    mounted() {
        if (this.$route.params.id) {
            this.id = this.$route.params.id
            this.receivedId = "getParam"
        }
        else {
            this.id = this.getDataToForm
            this.receivedId = "getDialog"
        }
        if (this.id) {
            axios.get("/api/technical/" + this.id).then(response => {
                this.loading = false
                this.technical = response.data;
                this.email = response.data.email;
                this.edit = true;
                this.technical.quotation = JSON.parse(this.technical.quotation);
                if (!this.technical.quotation) {
                    this.technical.quotation = [];
                }
                try {
                    this.technical.allRTProblem = JSON.parse(this.technical.allRTProblem);
                    if (!this.technical.allRTProblem) {
                        this.technical.allRTProblem = [];
                    }
                } catch (e) {
                    this.technical.allRTProblem = [];
                }
                this.technical.site_problem_description = response.data.site_problem_description;
                this.technical.sub_problem_description = response.data.sub_problem_description;
            })
        }
        else {
            axios.get("/api/getMail").then(response => {
                this.technical.report_by = response.data
                this.edit = false;
                this.loading = false
            })
        }
        axios.get("/api/sites").then(response => {
            this.sites = response.data.reduce(function (map, obj) {
                map[obj.Id_Site] = obj.Advisor;
                return map;
            }, {});

        });
        axios.get("/api/sites").then(response => {
            this.location = response.data.reduce(function (map, obj) {
                map['PP_Office'] = 'PP_Office';
                map['BTB_Office'] = 'BTB_Office';
                map['KC_Office'] = 'KC_Office';
                map['SR_Office'] = 'SR_Office';
                map[obj.Id_Site] = obj.Advisor;
                return map;
            }, {});
            console.log
        });
        axios.get("/api/configurations?app=technical").then(response => {
            this.configurations = response.data.reduce(function (map, c) {
                map[c.name] = JSON.parse(c.value);
                return map;
            }, {});
        });
    },
    methods: {
        async saveTechnicalForm(validationEvent) {
            this.loading = true; // Set loading at the beginning
            try {
                const result = await validationEvent; // Use await to wait for validation to complete
                if (result.valid) {
                    if (this.id) {
                        if (this.technical.rt_request_stock === "stock_need" && !this.technical.stock_type) {
                            // More concise check
                            this.loading = false; // Stop loading on error
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'Please select a stock type.',
                                customClass: {
                                    container: 'swal-zindex' // Apply the custom class
                                }
                            });
                            return; // Important: Stop execution here
                        }
                        else {
                            try {
                                await axios.put("/api/technical/update/" + this.id, this.technical);
                                this.$emit('cancel-modal')
                                this.loading = false;
                                this.$emit('site-saved')
                            } catch (error) {
                                this.loading = false;
                                console.error("Error updating technical:", error); // Log the error for debugging
                                Swal.fire({
                                    icon: 'error',
                                    title: 'Error',
                                    text: 'An error occurred while updating the form.',
                                    customClass: {
                                        container: 'swal-zindex' // Apply the custom class
                                    }
                                });
                            }
                        }
                    }
                    else {
                        try {
                            await axios.post('/api/technical/store', this.technical);
                            this.loading = false;
                            this.$router.go(-1);
                        } catch (error) {
                            this.loading = false;
                            console.error("Error saving technical:", error); // Log the error for debugging
                            Swal.fire({
                                icon: 'error',
                                title: 'Error',
                                text: 'An error occurred while saving the form.',
                                customClass: {
                                    container: 'swal-zindex' // Apply the custom class
                                }
                            });
                        }
                    }
                }
                else {
                    this.loading = false; // Stop loading if validation fails
                }
            } catch (error) {
                this.loading = false;  // Important: handle potential errors in validationEvent
                console.error("Validation Error:", error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'An error occurred during validation.',
                    customClass: {
                        container: 'swal-zindex' // Apply the custom class
                    }
                });
            }
        },
        calculateDistance() {
            if (this.technical.start_point && this.technical.end_point != '' || this.technical.start_point && this.technical.end_point != null) {
                axios.get('/api/getDistance?startPoint=' + this.technical.start_point + '&endPoint=' + this.technical.end_point).then((response) => {
                    this.technical.distance = response.data;
                    if (parseInt(response.data) > 37) {
                        this.technical.gasoline = ((response.data / 37) * 1.13).toFixed(2);
                    }
                    else {
                        this.technical.gasoline = 1;
                    }
                })
            }
            else {
                console.log("can't access map");
            }
        },
        addRTSolution() {
            alert("This is your addRTSolution button")
            // this.technical.rt_solution.push(this.newRTSolution);
            // this.newRTSolution = {};
        },
        addQuotation(validationEvent) {
            validationEvent.then(result => {
                if (result.valid === true) {
                    this.quoteItem.total = isNaN(this.quoteItem.quantity * this.quoteItem.unit_price) ? 0 : this.quoteItem.quantity * this.quoteItem.unit_price
                    this.quoteItem.dateSend = this.technical.date_need;
                    this.quoteItem.siteQuotation = this.technical.site;
                    console.log(this.technical.totalPriceAllItem)
                    this.technical.quotation.push(this.quoteItem)
                    this.quoteItem = {}
                    this.calculateTotal()
                    this.showAddItemForm = false
                }
            })
        },
        addSolution(validationEvent) {
            validationEvent.then(result => {
                if (result.valid === true) {
                    // Ensure `this.technical` is defined
                    if (!this.technical) {
                        console.error("Technical data is not defined.");
                        return;
                    }
                    // Ensure `this.technical.allData` is defined, if technical.allData is null, set it to array to add item in.
                    if (!this.technical.allRTProblem) {
                        this.technical.allRTProblem = [];
                    }
                    this.newRTSolution.rt_id = this.technical.id;
                    //console.log(this.newRTSolution);
                    this.technical.allRTProblem.push(this.newRTSolution);
                    this.newRTSolution = {};
                    this.showAddSolution = false;
                }
            });
        },
        validateItem() {
            if (this.$route.params.id) {
                axios.put("/api/technical/confirmItem/" + this.$route.params.id, this.technical).then(() => {
                    this.$router.go(-1)
                })
            }
        },
        calculateTotal() {
            this.technical.totalPriceAllItem = 0;
            for (var items in this.technical.quotation) {
                var item = this.technical.quotation[items];
                this.technical.totalPriceAllItem += Number.parseFloat(item.total);
            }
        },
        deleteItem(index) {
            this.technical.quotation.splice(index, 1);
            this.calculateTotal();
        },
        deleteSolution(index) {
            this.technical.allRTProblem.splice(index, 1);
        },
        checkButton() {
            console.log("This is your check button")
        },
    },
    watch: {
        "technical.start_point": function () {
            this.calculateDistance();
        },
        "technical.managerValidateItem": function () {
            if (this.technical.managerValidateItem == 'validated_item') {
                this.show = true;
            }
            else {
                this.show = false;
            }
        },
        "technical.end_point": function () {
            this.calculateDistance();
        },

        "technical.intervention_category": function () {
            this.technical.intervention_subcategory = '';
            this.technical.item_ref = '';
            this.technical.unit_price = '';
            this.technical.unit = '';
        },
        "quoteItem.unit_price": function () {
            this.quoteItem.total = isNaN(this.quoteItem.quantity * this.quoteItem.unit_price) ? 0 : this.quoteItem.quantity * this.quoteItem.unit_price
        },
        "quoteItem.quantity": function () {
            this.quoteItem.total = isNaN(this.quoteItem.quantity * this.quoteItem.unit_price) ? 0 : this.quoteItem.quantity * this.quoteItem.unit_price
        }
    }
}
</script>
<style>
.text {
    text-transform: uppercase;
    color: #4CAF50;
}

.swal-zindex {
    z-index: 10000 !important;
    /* Ensure this is higher than the z-index of v-dialog */
}
</style>
