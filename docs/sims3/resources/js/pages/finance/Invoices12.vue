<template>
    <div>
        <!-- Filter & Table as before -->
        <div v-if="!loading" class="d-flex pa-4">
            <v-text-field v-model="selectedDate" class="flex-grow-0 mr-5" label="Month" type="month" />
            <v-select v-model="selectedPlatform" label="Platform" :items="platformFilterItems" class="mr-4"
                density="compact" />
            <v-text-field v-model="search" label="Search Site" density="compact" />
            <!-- <v-btn color="primary" size="small" class="ml-auto" @click="depositAndwithdraw()">
                <v-icon start>mdi-refresh</v-icon>
                Receipt
            </v-btn> -->
            <v-btn color="primary" size="small" class="ml-auto" @click="depositAndwithdraw()">
                <v-icon start>mdi-currency-usd</v-icon>
                Balance
            </v-btn>
            <v-btn color="green" size="small" class="ml-2" to="/dashboardCashier">
                <v-icon start>mdi-file-excel</v-icon>
                Excel
            </v-btn>
        </div>

        <v-table v-if="!loading">
            <thead>
                <tr>
                    <th></th>
                    <th v-for="(sites, platform) in platformsToDisplay" :key="platform" class="text-center">
                        {{ platform }}
                    </th>
                </tr>
            </thead>

            <tbody>
                <!-- Pending -->
                <tr>
                    <th class="text-center">Invoices</th>

                    <td v-for="(sites, platform) in platformsToDisplay" :key="platform">
                        <div class="d-flex flex-wrap justify-center">
                            <v-chip v-for="site in pendingSites(sites)" :key="site.Id_Site" size="small" class="ma-1"
                                :class="{ highlighted: search && site.Id_Site.toLowerCase().includes(search.toLowerCase()) }"
                                @click="openInvoice(site)">
                                {{ site.Id_Site }}
                            </v-chip>
                        </div>
                    </td>
                </tr>

                <!-- Sent -->
                <tr>
                    <th class="text-center">Sent Ent</th>
                    <td v-for="(sites, platform) in platformsToDisplay" :key="platform">
                        <div class="d-flex flex-wrap justify-center">
                            <v-chip v-for="site in sentSites(sites)" :key="site.Id_Site" size="small"
                                class="ma-1 sent-chip-sending"
                                :class="{ highlighted: search && site.Id_Site.toLowerCase().includes(search.toLowerCase()) }"
                                @click="settleInvoice(site.Id_Site)">
                                {{ site.Id_Site }}
                            </v-chip>

                        </div>
                    </td>
                </tr>
                <tr>
                    <th class="text-center">Settle</th>
                    <td v-for="(sites, platform) in platformsToDisplay" :key="platform">
                        <div class="d-flex flex-wrap justify-center">
                            <v-chip v-for="site in settleSites(sites)" :key="site.Id_Site" size="small"
                                class="ma-1 sent-chip"
                                :class="{ highlighted: search && site.Id_Site.toLowerCase().includes(search.toLowerCase()) }"
                                @click="viewInvoice(site)">
                                {{ site.Id_Site }}
                            </v-chip>

                        </div>
                    </td>
                </tr>
            </tbody>
        </v-table>

        <div v-if="loading" class="d-flex justify-center mt-10">
            <v-progress-circular indeterminate size="60" />
        </div>

        <!-- Invoice Modal (Send Invoice) -->
        <v-dialog v-model="invoiceDialog" max-width="700">
            <v-card>
                <v-card-title>
                    <span class="text-primary font-weight-bold text-center d-block">Invoices Site : {{
                        selectedSite?.Id_Site }}</span>
                </v-card-title>

                <v-card-text>
                    <!-- ========== NORMAL INVOICES TABLE ========== -->
                    <h4 class="mb-2 text-center d-block">Invoices</h4>

                    <v-table density="compact">
                        <thead style="background-color: #f0f0f0;">
                            <tr>
                                <th style="color: #007bff; font-weight: bold;">Month</th>
                                <th style="color: #007bff; font-weight: bold;">Type</th>
                                <!-- <th style="color: #007bff; font-weight: bold;">Status</th> -->
                                <th class="text-right" style="color: #007bff; font-weight: bold;">Amount</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="inv in normalInvoices" :key="inv.id">
                                <td>{{ inv.month?.substring(0, 7) ?? inv.month }}</td>
                                <td>{{ inv.invoice_type }}</td>
                                <!-- <td>{{ inv.status }}</td> -->
                                <td class="text-right">{{ Number(inv.beginning_balance).toLocaleString() }}</td>
                            </tr>

                            <!-- TOTAL ROW -->
                            <tr class="font-weight-bold">
                                <td colspan="2" class="text-right">Total Invoices Amount:</td>
                                <td class="text-right">
                                    {{ totalNormalInvoices.toLocaleString() }}
                                </td>
                            </tr>
                        </tbody>
                    </v-table>

                    <!-- ========== SCHOOL PROGRAM SUMMARY ROW ========== -->

                    <h4 class="mt-6 mb-2 text-center d-block">School Program</h4>

                    <v-table density="compact">
                        <thead style="background-color: #f0f0f0;">
                            <tr>
                                <th style="color: #007bff; font-weight: bold;">Month</th>
                                <th style="color: #007bff; font-weight: bold;">Type</th>
                                <!-- <th style="color: #007bff; font-weight: bold;">Status</th> -->
                                <th class="text-right" style="color: #007bff; font-weight: bold;">Amount</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="inv in schoolInvoices" :key="inv.id">
                                <!-- <td>{{ inv.month?.substring(0, 7) ?? inv.month }}</td> -->
                                <td>{{ formatDateMinusOneMonth(inv.month) }}</td>
                                <td>{{ inv.invoice_type }}</td>
                                <!-- <td>{{ inv.status }}</td> -->
                                <td class="text-right">{{ Number(inv.beginning_balance).toLocaleString() }}</td>
                                
                            </tr>
                            <br>

                            <!-- REMAINING AMOUNT ROW -->
                            <tr class="font-weight-bold"
                                    :class="{ 'text-green-darken-2': remainingAmount > 0, 'text-red-darken-2': remainingAmount < 0 }">
                                    <td :colspan="remainingAmount > 0 ? 5 : 5" 
                                        class="text-center py-3"
                                        style="font-size: 20px; font-weight: bold; letter-spacing: 0.5px;">
                                        <v-icon v-if="remainingAmount > 0" small class="mr-2">mdi-plus-circle</v-icon>
                                        <v-icon v-else small class="mr-2">mdi-minus-circle</v-icon>
                                        
                                        <span v-if="remainingAmount > 0">
                                            Remaining Amount: {{ remainingAmount.toLocaleString() }}
                                        </span>
                                        <span v-else>
                                            School Amount Remaining: {{ remainingAmount.toLocaleString() }}
                                        </span>
                                    </td>
                                </tr>
                        </tbody>
                    </v-table>
                </v-card-text>
                <v-card-actions>
                    <!-- <v-btn color="primary" @click="sendInvoicePDF" :loading="sending" :disabled="sending">
                        Send Invoice
                    </v-btn> -->
                    <!-- Green download button -->
                    <v-btn color="success" @click="downloadInvoice"  variant="elevated">
                        Download Invoice
                    </v-btn>
                    <v-spacer />
                    <!-- Red send button -->
                    <v-btn color="error" @click="sendInvoiceAsImage" :loading="sending" :disabled="sending" variant="elevated" class="mr-2">
                        Send Invoice
                    </v-btn>
                    <v-btn @click="invoiceDialog = false" :disabled="sending">
                        Close
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- View Invoice Modal (Detailed View) -->
        <v-dialog v-model="viewInvoiceDialog" max-width="900">
            <v-card>
                <v-card-title class="bg-primary text-white">
                    <v-icon start>mdi-file-document-multiple</v-icon>
                    Invoice Details - {{ viewSelectedSite?.Id_Site }}
                    <v-chip class="ml-2" color="white" text-color="primary">
                        {{ viewSelectedSite?.Platform }}
                    </v-chip>
                    <v-spacer />
                </v-card-title>

                <v-card-subtitle class="pa-4">
                    <div class="d-flex align-center">
                        <v-icon start size="small">mdi-account</v-icon>
                        <span class="font-weight-bold mr-2">Advisor:</span> {{ viewSelectedSite?.Advisor }}
                        <v-divider vertical class="mx-4"></v-divider>
                        <v-icon start size="small">mdi-calendar</v-icon>
                        <span class="font-weight-bold mr-2">Month:</span> {{
                            formatMonth(viewSelectedSite?.latest_invoice?.month) }}
                    </div>
                </v-card-subtitle>

                <v-card-text>
                    <!-- Summary Cards -->
                    <!-- <v-row class="mb-6">
                        <v-col cols="12" sm="3">
                            <v-card color="blue-lighten-5" flat>
                                <v-card-text class="text-center">
                                    <div class="text-subtitle-1">Total Amount</div>
                                    <div class="text-h5 font-weight-bold text-primary">
                                        ៛ {{ formatNumber(viewTotalBeginningBalance) }}
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-col>
                        <v-col cols="12" sm="3">
                            <v-card color="green-lighten-5" flat>
                                <v-card-text class="text-center">
                                    <div class="text-subtitle-1">Total Received</div>
                                    <div class="text-h5 font-weight-bold text-green">
                                        ៛ {{ formatNumber(viewTotalTransactionAmount) }}
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-col>
                        <v-col cols="12" sm="3">
                            <v-card color="orange-lighten-5" flat>
                                <v-card-text class="text-center">
                                    <div class="text-subtitle-1">Total Remain</div>
                                    <div class="text-h5 font-weight-bold text-orange">
                                        ៛ {{ formatNumber(viewTotalRemainAmount) }}
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-col>
                        <v-col cols="12" sm="3">
                            <v-card :color="viewPaymentStatusColor" flat>
                                <v-card-text class="text-center">
                                    <div class="text-subtitle-1">Payment Status</div>
                                    <div class="text-h5 font-weight-bold">
                                        {{ viewPaymentStatus }}
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-col>
                    </v-row> -->

                    <!-- Normal Invoices Table -->
                    <!-- <v-card class="mb-6" v-if="viewNormalInvoices.length > 0">
                        <v-card-title class="bg-blue-lighten-5">
                            <v-icon start color="blue">mdi-receipt</v-icon>
                            Invoices

                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <thead>
                                    <tr>
                                        <th>Month</th>
                                        <th>Invoice Type</th>
                                        <th class="text-right">Beginning Balance</th>
                                        <th class="text-right">Transaction Amount</th>
                                        <th class="text-right">Remain Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="inv in viewNormalInvoices.filter(i => i.invoice_type !== 'withdraw')"
                                        :key="'normal-' + inv.id">
                                        <td>{{ inv.month?.substring(0, 7) ?? inv.month }}</td>
                                        <td>
                                            <v-chip size="small" color="blue" variant="flat">
                                                {{ inv.invoice_type }}
                                            </v-chip>
                                        </td>
                                        <td class="text-right font-weight-bold">
                                            ៛ {{ formatNumber(inv.beginning_balance) }}
                                        </td>
                                        <td class="text-right">
                                            <span :class="{
                                                'text-green': inv.transaction_amount > 0,
                                                'text-grey': inv.transaction_amount == 0
                                            }">
                                                ៛ {{ formatNumber(inv.transaction_amount) }}
                                            </span>
                                        </td>
                                        <td class="text-right">
                                            <v-chip :color="getRemainAmountColor(inv.remain_amount)" size="small">
                                                ៛ {{ formatNumber(inv.remain_amount) }}
                                            </v-chip>
                                        </td>
                                    </tr>
                                </tbody>
                                <tfoot>
                                    <tr class="bg-grey-lighten-4">
                                        <td colspan="4" class="text-right font-weight-bold">Total :</td>
                                        <td class="text-right font-weight-bold">
                                            ៛ {{ formatNumber(viewTotalNormalRemainAmount) }}
                                        </td>
                                    </tr>
                                </tfoot>
                            </v-table>
                        </v-card-text>
                    </v-card> -->

                    <!-- <v-card class="mb-6" v-if="viewNormalInvoices.length > 0">
                        <v-card-title class="bg-blue-lighten-5">
                            <v-icon start color="blue">mdi-currency-usd</v-icon>
                            Withdrawal Balance
                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <thead>
                                    <tr>
                                        <th>Month</th>
                                        <th>Invoice Type</th>
                                        <th class="text-right">Beginning Balance</th>
                                        <th class="text-right">Transaction Amount</th>
                                        <th class="text-right">Remain Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="inv in viewNormalInvoices.filter(i => i.invoice_type === 'withdraw')"
                                        :key="'normal-' + inv.id">
                                        <td>{{ inv.month?.substring(0, 7) ?? inv.month }}</td>
                                        <td>
                                            <v-chip size="small" color="blue" variant="flat">
                                                {{ inv.invoice_type }}
                                            </v-chip>
                                        </td>
                                        <td class="text-right font-weight-bold">
                                            ៛ {{ formatNumber(inv.beginning_balance) }}
                                        </td>
                                        <td class="text-right">
                                            <span :class="{
                                                'text-green': inv.transaction_amount > 0,
                                                'text-grey': inv.transaction_amount == 0
                                            }">
                                                ៛ {{ formatNumber(inv.transaction_amount) }}
                                            </span>
                                        </td>
                                        <td class="text-right">
                                            <v-chip :color="getRemainAmountColor(inv.remain_amount)" size="small">
                                                ៛ {{ formatNumber(inv.remain_amount) }}
                                            </v-chip>
                                        </td>
                                    </tr>
                                </tbody>

                            </v-table>
                        </v-card-text>
                    </v-card> -->

                    <!-- School Program Invoices Table -->
                    <!-- <v-card v-if="viewSchoolInvoices.length > 0">
                        <v-card-title class="bg-orange-lighten-5">
                            <v-icon start color="orange-darken-2">mdi-school</v-icon>
                            School Program
                        </v-card-title>
                        <v-card-text>
                            <v-table density="compact">
                                <thead>
                                    <tr>
                                        <th>Month</th>
                                        <th>Invoice Type</th>
                                        <th class="text-right">Beginning Balance</th>
                                        <th class="text-right">Transaction Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr v-for="inv in viewSchoolInvoices" :key="'school-' + inv.id">
                                        <td>{{ inv.month?.substring(0, 7) ?? inv.month }}</td>
                                        <td>
                                            <v-chip size="small" color="orange" variant="flat">
                                                {{ inv.invoice_type }}
                                            </v-chip>
                                        </td>
                                        <td class="text-right font-weight-bold">
                                            {{ formatNumber(inv.beginning_balance) }}
                                        </td>
                                        <td class="text-right">
                                            <span :class="{
                                                'text-green': inv.transaction_amount > 0,
                                                'text-grey': inv.transaction_amount == 0
                                            }">
                                                {{ formatNumber(inv.transaction_amount) }}
                                            </span>
                                        </td>
                                    </tr>
                                </tbody>
                            </v-table>
                        </v-card-text>
                    </v-card> -->

                    <!-- QR Code Display Section -->
                    <v-card class="mt-6" v-if="hasQRCode">
                        <v-card-title class="bg-grey-lighten-4">
                            <v-icon start>mdi-qrcode</v-icon>
                            Payment QR Code
                        </v-card-title>
                        <v-card-text>
                            <v-row align="center">
                                <!-- QR Code Image -->
                                <v-col cols="12" md="6" class="text-center">
                                    <div class="qr-container pa-4">
                                        <v-img :src="qrCodeUrl" :alt="'QR Code for ' + viewSelectedSite?.Id_Site"
                                            max-width="300" max-height="300" class="mx-auto qr-image" contain>
                                            <template v-slot:placeholder>
                                                <v-row class="fill-height ma-0" align="center" justify="center">
                                                    <v-progress-circular indeterminate
                                                        color="primary"></v-progress-circular>
                                                </v-row>
                                            </template>
                                        </v-img>
                                        <div class="mt-4 text-caption text-grey">
                                            Payment QR Code
                                        </div>
                                    </div>
                                </v-col>

                                <!-- QR Code Details -->
                                <!-- QR Code Details - Simple Row & Column Layout -->
                                <v-col cols="12" md="6">
                                    <div class="qr-details pa-4">
                                        <h4 class="mb-4 d-flex align-center">
                                            <v-icon color="primary" class="mr-2">mdi-information</v-icon>
                                            QR Code Information
                                        </h4>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Site:</v-col>
                                            <v-col cols="6" class="text-right">{{ viewSelectedSite?.Id_Site }}</v-col>
                                        </v-row>

                                        <v-divider class="my-2"></v-divider>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Platform:</v-col>
                                            <v-col cols="6" class="text-right">{{ viewSelectedSite?.Platform }}</v-col>
                                        </v-row>

                                        <v-divider class="my-2"></v-divider>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Month:</v-col>
                                            <v-col cols="6" class="text-right">{{
                                                formatMonth(viewSelectedSite?.latest_invoice?.month) }}</v-col>
                                        </v-row>

                                        <v-divider class="my-2"></v-divider>

                                        <!-- <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Total Paid:</v-col>
                                            <v-col cols="6" class="text-right text-green font-weight-bold">
                                                {{ formatNumber(viewTotalTransactionAmount) }}
                                            </v-col>
                                        </v-row>

                                        <v-divider class="my-2"></v-divider>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Payment Date:</v-col>
                                            <v-col cols="6" class="text-right">{{ getPaymentDate }}</v-col>
                                        </v-row> -->

                                        <!-- Download QR Code Button -->
                                        <div class="mt-6 text-center">
                                            <v-btn color="primary" variant="outlined" @click="downloadQRCode"
                                                :loading="downloadingQR">
                                                <v-icon start>mdi-download</v-icon>
                                                Download QR Code
                                            </v-btn>
                                        </div>
                                    </div>
                                </v-col>
                            </v-row>
                        </v-card-text>
                    </v-card>

                    <!-- Message when no QR Code -->
                    <v-alert v-if="viewNormalInvoices.length > 0 && !hasQRCode" type="info" class="mt-6"
                        variant="tonal">
                        <v-icon start>mdi-qrcode-remove</v-icon>
                        No QR code available for this payment.
                    </v-alert>

                    <!-- No Data Message -->
                    <v-alert v-if="viewNormalInvoices.length === 0 && viewSchoolInvoices.length === 0" type="info"
                        class="mt-4">
                        No invoice details available for this site.
                    </v-alert>
                </v-card-text>

                <v-card-actions>
                    <v-spacer />
                    <v-btn color="red" @click="viewInvoiceDialog = false">Close</v-btn>
                    <!-- <v-btn color="primary" @click="printViewInvoice">
                        <v-icon start>mdi-printer</v-icon>
                        Print
                    </v-btn> -->
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- Load settle invoice form -->
        <div class="text-center">
            <v-dialog v-model="dialog" persistent max-width="100%" content-class="custom-dialog">
                <v-card>
                    <settleInvoice :invoiceSite="{ site: selectedItem, month: selectedDate }"
                        @cancel-modal="dialog = false" @close-dialog="dialog = false"></settleInvoice>
                </v-card>
            </v-dialog>
        </div>

        <!-- // show deposit and withdrawal  -->
        <v-dialog v-model="depositAndWithdrawalDialog" max-width="500" persistent>
            <v-card class="elevation-6 rounded-lg">
                <!-- Header with icon -->
                <v-card-title class="primary white--text d-flex align-center">
                    <v-btn icon small @click="depositAndWithdrawalDialog = false" class="white--text">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </v-card-title>

                <!-- Balance Summary Section -->
                <v-card-text class="pt-4 pb-0">
                    <v-row class="mb-4" align="center">
                        <!-- v-select - wider with full width -->
                        <v-col cols="12" md="12" class="pr-md-2">
                            <v-autocomplete v-model="selectedSiteForBalance" :items="siteOptions" label="Select Site"
                                item-title="name" item-value="id" density="compact" outlined
                                style="max-width: 180px; font-size: 0.9rem;"></v-autocomplete>
                        </v-col>
                    </v-row>
                    <v-divider class="mb-4"></v-divider>
                    <div v-if="loadingBalance" class="d-flex align-center">
                        <v-progress-circular indeterminate size="20" width="2" color="green"
                            class="mr-2"></v-progress-circular>
                        <span class="text-caption text-grey">Loading...</span>
                    </div>
                    <!-- Balance Cards -->
                    <div v-else class="text-caption text-grey mb-2">
                        <v-row dense class="mb-6" v-if="selectedSiteForBalance">
                            <v-col cols="12">
                                <v-card outlined class="rounded-lg pa-3"
                                    style="border-color: #4caf50; border-width: 2px;">
                                    <div class="d-flex align-center">
                                        <v-icon left color="green" class="mr-2">mdi-cash-multiple</v-icon>
                                        <div class="text-body-2 text-grey-darken-3">Total Balance</div>
                                        <v-spacer></v-spacer>
                                        <div class="text-h6 font-weight-bold green--text">៛ {{ formatNumber(siteBalance)
                                        }}
                                        </div>
                                    </div>
                                </v-card>
                            </v-col>
                        </v-row>

                        <!-- Transaction Input Row -->
                        <v-row class="mb-4" align="center" v-if="selectedSiteForBalance && siteBalance >= 0">
                            <!-- v-select - wider with full width -->
                            <v-col cols="12" md="6" class="pr-md-2">
                                <v-select v-model="transactionType" :items="['Deposit', 'Withdrawal']"
                                    label="Transaction Type" variant="outlined" density="comfortable" class="mb-0"
                                    :style="{ 'font-size': '16px', 'min-width': '200px' }" hide-details>
                                    <template v-slot:prepend-inner>
                                        <v-icon :color="transactionType === 'Deposit' ? 'green' : 'red'" class="mr-3">
                                            {{ transactionType === 'Deposit' ? 'mdi-plus-circle' : 'mdi-minus-circle' }}
                                        </v-icon>
                                    </template>
                                </v-select>
                            </v-col>

                            <!-- v-text-field - wider with full width -->
                            <v-col cols="12" md="6" class="pl-md-2" v-if="transactionType !== ''">
                                <v-text-field v-model="formattedAmount" label="Amount" type="text" prefix="៛"
                                    placeholder="0.00" class="text-h6 font-weight-bold green--text"
                                    density="comfortable" hide-details @input="formatAndValidateAmount" />
                            </v-col>
                        </v-row>
                    </div>
                </v-card-text>

                <!-- Action Buttons -->
                <v-card-actions class="pa-4 pt-0" v-if="siteBalance >= 0">
                    <v-btn :color="transactionType === 'Deposit' ? 'success' : 'warning'" @click="openConfirmDialog()"
                        :disabled="!formattedAmount || parseFloat(this.formattedAmount) <= 0" class="text-capitalize"
                        variant="flat">
                        <v-icon left small>mdi-check</v-icon>
                        Confirm {{ transactionType }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
        <!-- show confirm deposit and withdrawal dialog -->
        <v-dialog v-model="confirmDialog" max-width="400">
            <v-card class="elevation-8">
                <!-- Title with color -->
                <v-card-title class="text-h5 font-weight-bold primary white--text py-4">
                    <v-icon left color="white">mdi-alert-circle-outline</v-icon>
                    Confirm Update
                </v-card-title>

                <!-- Card content with better spacing -->
                <v-card-text class="pa-6">
                    <div class="d-flex align-start mb-4">
                        <v-icon color="info" class="mr-3 mt-1">mdi-help-circle-outline</v-icon>
                        <div>
                            <p class="text-body-1 mb-2">
                                Are you sure you want to update the balance
                            </p>
                        </div>
                    </div>
                </v-card-text>

                <!-- Buttons with blue styling -->
                <v-card-actions class="pa-4 bg-grey-lighten-4">
                    <v-spacer></v-spacer>

                    <!-- Cancel button -->
                    <v-btn @click="confirmDialog = false" variant="outlined" class="mr-3" size="small">
                        Cancel
                    </v-btn>

                    <!-- Confirm button with blue styling -->
                    <v-btn color="blue-darken-2" @click="saveTransaction" variant="elevated" size="small" class="px-6">
                        <v-icon left>mdi-check-circle-outline</v-icon>
                        Confirm
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
            {{ snackbar.message }}
        </v-snackbar>
        <!-- Snackbar -->
        <v-snackbar v-model="snackbarWithdrawal.show" :timeout="snackbar.timeout" color="red" top right>
            {{ snackbar.message }}
            <template v-slot:action="{ attrs }">
                <v-btn color="white" text v-bind="attrs" @click="snackbar.show = false">
                    Close
                </v-btn>
            </template>
        </v-snackbar>
    </div>

    <!-- show image here -->

    <div id="invoice-to-capture" ref="invoice"
        style="width: 800px; padding: 20px; background: white; font-family: 'Khmer OS System', sans-serif; display: none;">
        <!-- Top header: logo left + company name centered -->
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <!-- Logo -->
            <img src="/img/logo.png" alt="Logo" style="width: 80px; height: auto;" />

            <!-- Spacer flex to push company name center -->
            <div style="flex-grow: 1;"></div>

            <!-- Company Name centered (with fixed width container) -->
            <div style="width: 400px; text-align: center; font-size: 24px; font-weight: bold; user-select: none;">
                អង្គការទឹកស្អាត១០០១
            </div>

            <!-- Spacer flex to keep company name centered -->
            <div style="flex-grow: 1;"></div>
        </div>

        <!-- Office info table: office name row + office address row -->
        <table
            style="width: 100%; margin-bottom: 20px; border-collapse: collapse; font-size: 14px; border: 1px solid black;">
            <tbody>
                <tr>
                    <td v-if="selectedSite?.Platform === 'PP' || selectedSite?.Platform === 'KSP'"
                        style="width: 700px; border: 1px; text-align: center; font-size: 18px; font-weight: bold; user-select: none;">
                        ការិយាលយ័ភ្នំពេញ</td>
                    <td v-if="selectedSite?.Platform === 'BTB'"
                        style="width: 700px; text-align: center; border: 1px;font-size: 18px; font-weight: bold; user-select: none;">
                        ការិយាល័យបាត់ដំបង</td>
                    <td v-if="selectedSite?.Platform === 'KC'"
                        style="width: 700px; text-align: center;border: 1px; font-size: 18px; font-weight: bold; user-select: none;">
                        ការិយាល័យកំពង់ចាម</td>
                    <td v-if="selectedSite?.Platform === 'SR'"
                        style="width: 700px; text-align: center; border: 1px;font-size: 18px; font-weight: bold; user-select: none;">
                        ការិយាល័យសៀមរាប</td>
                </tr>
                <tr>
                    <td v-if="selectedSite?.Platform === 'PP' || selectedSite?.Platform === 'KSP'"
                        style="border: 1px;font-weight: bold; padding: 4px 0;font-size: 14px;">ផ្ទះលេខ 100 ផ្លូវ 95
                        សង្កាត់បឹងត្របែក ខណ្ឌចំការមន ភ្នំពេញ ទូរសព្ទទំនាក់ទំនង ០២៣ ២១៥ ៤២៧ </td>
                    <td v-if="selectedSite?.Platform === 'BTB'"
                        style="font-weight: bold;border: 1px; padding: 4px 0;font-size: 14px;">ផ្ទះលេខ៦៧៦ ផ្លូវ/ ក្រុង១៥
                        ភូមិអូរ តាគាំ១​ សង្កាត់ទួលតាឯក ក្រុងបាត់ដំបង ខេត្តបាត់ដំបង ទូរសព្ទទំនាក់ទំនង ០៥៣ ៩៥៣ ១៦១ </td>
                    <td v-if="selectedSite?.Platform === 'KC'"
                        style="font-weight: bold;border: 1px; padding: 4px 0;font-size: 14px;">ភូមិទី២ សង្កាត់វាងវង់
                        ក្រុងកំពង់ចាម ខេត្តកំពង់ចាម </td>
                    <td v-if="selectedSite?.Platform === 'SR'"
                        style="font-weight: bold;border: 1px; padding: 4px 0;font-size: 14px;">ភូមិកសិកម្ម សង្កាត់ស្រងែ
                        ក្រុងសៀមរាប ខេត្តសៀមរាប </td>
                </tr>
            </tbody>
        </table>

        <!-- Invoice basic info -->
        <!-- Info table with 3 rows and 2 columns -->
        <table style="width: 100%; margin-bottom: 28px; border-collapse: collapse; font-size: 14px;">
            <tbody>
                <tr>
                    <td style="font-weight: bold; padding: 4px 8px; width: 50%;">ថ្ងៃទី / Date:
                        {{ selectedSite?.latest_invoice?.date || selectedDate || '' }}</td>
                    <td style="font-weight: bold; padding: 4px 8px;">សហគ្រិន / Entrepreneur: {{
                        selectedSite?.Entrepreneur
                    }}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; padding: 4px 8px;">ផ្ញើរ / To: {{ selectedSite?.Id_Site || 'N/A' }}
                    </td>
                    <td style="font-weight: bold; padding: 4px 8px;">អ្នកប្រឹក្សាយោបល់ / Advisor: {{
                        selectedSite?.Advisor
                        || 'N/A' }}</td>
                </tr>
                <tr>
                    <td v-if="selectedSite?.Platform === 'PP'" style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ / Platform: ភ្នំពេញ</td>
                    <td v-if="selectedSite?.Platform === 'KSP'"
                        style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ / Platform: កំពង់ស្ពឺ</td>
                    <td v-if="selectedSite?.Platform === 'BTB'"
                        style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ / Platform: បាត់ដំបង</td>
                    <td v-if="selectedSite?.Platform === 'KC'" style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ / Platform: កំពង់ចាម</td>
                    <td v-if="selectedSite?.Platform === 'SR'" style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ / Platform: សៀមរាប</td>
                    <td v-if="selectedSite?.Platform === 'PP' || selectedSite?.Platform === 'KSP'"
                        style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ / Cashier : មន​ សោវី</td>
                    <td v-if="selectedSite?.Platform === 'BTB'" style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ
                        /
                        Cashier : នូ ចំរើន</td>
                    <td v-if="selectedSite?.Platform === 'KC'" style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ
                        /
                        Cashier : ហ៊ាង ប៉ោឡេង</td>
                    <td v-if="selectedSite?.Platform === 'SR'" style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ
                        /
                        Cashier : ហ៊ន ស្រីរត្ន័</td>
                </tr>
            </tbody>
        </table>
        <!-- SUMMARY section -->
        <div style="width: 800px; text-align: center; font-size: 18px; font-weight: bold; user-select: none;">
            <h4>សង្ខេប / Summary</h4>
        </div>
        <br>
        <p class="text-center py-3 amount-to-pay" 
                v-if="(totalNormalInvoices - totalSchoolProgram) > 0">
                <strong>ចំនួនទឹកលុយបង់ / Amount to Pay: ៛ {{ formatNumber(totalNormalInvoices - totalSchoolProgram) }}</strong>
                </p>
        
        <p class="text-center py-3" style="font-size: 30px; font-weight: bold; letter-spacing: 0.5px; color: rebeccapurple" v-else><strong>ចំនួននៅសល់ / Remaining Amount: ៛ {{ formatNumber(totalNormalInvoices - totalSchoolProgram)}}
        <br>
        លុយនៅសល់នឹងដាក់ចូលក្នុងគណនីយសន្សំ</strong></p>
        <br><br>
        <!-- INVOICES section -->
        <div style="width: 800px; text-align: center; font-size: 18px; font-weight: bold; user-select: none;">
            <h4>វិកយ័បត្រ័ / Invoices</h4>
        </div>
        <table border="1" cellspacing="0" cellpadding="5"
            style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <thead>
                <tr style="background-color: #4CAF50; color: white; font-size: 14px;">
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        ល.រ</th>
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        លេខវិកយ័បត្រ័​ / Invoice</th>
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        បរិយាយ / Description</th>
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        តម្លៃ / Price</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(inv, index) in normalInvoices" :key="index">
                    <td style="text-align: center;">{{ index + 1 }}</td>
                    <td
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        {{ inv.invoice_code || inv.invoice_type }}
                    </td>
                    <td
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        {{ inv.invoice_type_khmer_name }}
                    </td>
                    <td style="text-align: center;">៛ {{ formatNumberComma(inv.beginning_balance) }}</td>
                </tr>
                <tr>
                    <td colspan="3" style="text-align: right; font-weight: bold; font-size: 14px;">
                        <strong>Total</strong>
                    </td>
                    <td style="text-align: center;"><strong>៛ {{ formatNumberComma(totalNormalInvoices) }}</strong></td>
                </tr>
            </tbody>
        </table>
        <br><br>
        <!-- SCHOOL PROGRAM INVOICES section -->
        <div style="width: 800px; text-align: center; font-size: 18px; font-weight: bold; user-select: none;">
            <h4>ទឹកសាលា / School Program</h4>
        </div>
        <table border="1" cellspacing="0" cellpadding="5"
            style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <thead>
                <tr style="background-color: blue; color: white; font-size: 14px;">
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 16px; padding: 6px 8px;">
                        បរិយាយ / Description</th>
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 16px; padding: 6px 8px;">
                        តំលៃ / Price</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(inv, index) in schoolInvoices" :key="index">
                    <td
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        {{ inv.invoice_type_khmer_name || 0 }}
                    </td>
                    <td
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        ៛ {{ formatNumberComma(inv.beginning_balance) || 0 }}</td>
                </tr>
            </tbody>
        </table>
        <br>
        
        <!-- Signature lines -->
        <div style="margin-top: 40px; display: flex; justify-content: space-around;">
            <div style="text-align: center;">
                <p>អ្នកទិញ</p>
                <br><br><br>
                <hr style="width: 250px;" />
            </div>
            <div style="text-align: center;">
                <p v-if="selectedSite?.Platform === 'PP' || selectedSite?.Platform === 'KSP'"
                    style="font-weight: bold; padding: 4px 8px;">រៀបចំដោយ​ : មន​ សោវី <br>
                    <img src="/img/pp.png" alt="Logo" style="height: 50px; width: 50px; margin-right: 10px;">
                </p>
                <p v-if="selectedSite?.Platform === 'BTB'" style="font-weight: bold; padding: 4px 8px;">រៀបចំដោយ : នូ
                    ចំរើន
                    <br>
                    <img src="/img/btb.png" alt="Logo" style="height: 50px; width: 50px; margin-right: 10px;">
                </p>
                <p v-if="selectedSite?.Platform === 'KC'" style="font-weight: bold; padding: 4px 8px;">រៀបចំដោយ : ហ៊ន ស្រីរត្ន័ <br>
                    <img src="/img/kc.png" alt="Logo" style="height: 50px; width: 50px; margin-right: 10px;">
                </p>
                <p v-if="selectedSite?.Platform === 'SR'" style="font-weight: bold; padding: 4px 8px;">រៀបចំដោយ : ហ៊ាង ប៉ោឡេង <br>
                    <img src="/img/sr.png" alt="Logo" style="height: 30px; margin-right: 10px;">
                </p>
                <hr style="width: 250px;" />
            </div>
        </div>
    </div>
</template>

<script>
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'
import settleInvoice from './SettleInvoice.vue'
import html2canvas from 'html2canvas';

export default {
    name: 'InvoiceDashboard',
    components: {
        settleInvoice
    },
    data() {
        const today = new Date()
        return {
            balanceWithdraw: 0,
            siteBalance: 0,
            siteOptions: [],
            loading: true,
            sending: false,
            samples: [],
            selectedPlatform: 'All',
            search: '',
            invoiceDialog: false,
            viewInvoiceDialog: false,
            selectedSite: null,
            selectedSiteForBalance: null,
            viewSelectedSite: null,
            selectedDate: new Date(today.getFullYear(), today.getMonth() - 0, 1).toISOString().substr(0, 7),
            dialog: false,
            sending: false,
            selectedItem: '',
            depositAndWithdrawalDialog: false,
            transactionType: '',
            amount: "",
            formattedAmount: "",
            downloadExcel: false,
            loadingBalance: false,
            snackbar: {
                show: false,
                message: '',
                color: 'success',
            },
            snackbarWithdrawal: {
                show: false,
                message: '',
                timeout: 5000, // 3 seconds
            },
            confirmDialog: false,
            downloadingQR: false,
        }
    },
    watch: {
        selectedDate: {
            handler() {
                this.getDataInvoices()
            },
            immediate: false,
        },
        selectedSiteForBalance: {
            async handler(newSiteId) {
                if (!newSiteId) {
                    this.siteBalance = 0;
                    return;
                }
                this.loadingBalance = true;
                try {
                    const response = await axios.get(`/api/getSiteBalance/${newSiteId}`);

                    // Your Laravel returns: { success: true, data: { balance: X } }
                    if (response.data.success && response.data.data) {
                        this.siteBalance = response.data.data.balance;

                    } else {
                        this.siteBalance = 0;
                    }
                } catch (error) {
                    console.error("Error:", error.response?.data || error.message);
                    this.siteBalance = 0;
                } finally {
                    this.loadingBalance = false;
                }
            },
            immediate: false
        },
    },
    computed: {
        withdrawalExceedsBalance() {
            if (this.transactionType !== 'Withdrawal') return false;
            const amount = parseFloat(this.formattedAmount.replace(/,/g, '')) || 0;
            return amount > this.siteBalance;
        },
        qrCodePath() {
            if (!this.viewSelectedSite || !this.viewSelectedSite.invoices) return null;

            // Find first invoice with pictureQR
            const invoiceWithQR = this.viewSelectedSite.invoices.find(inv =>
                inv.pictureQR && inv.pictureQR.trim() !== ''
            );

            return invoiceWithQR ? invoiceWithQR.pictureQR : null;
        },
        qrCodeUrl() {
            if (!this.qrCodePath) return '';

            // Assuming your storage is linked to /storage
            // Adjust the base URL as needed
            const baseUrl = window.location.origin;
            return `${baseUrl}/storage/${this.qrCodePath}`;
        },
        hasQRCode() {
            return !!this.qrCodePath;
        },
        getPaymentDate() {
            if (!this.viewSelectedSite || !this.viewSelectedSite.invoices) return 'N/A';

            // Find invoice with transaction amount > 0
            const paidInvoice = this.viewSelectedSite.invoices.find(inv =>
                parseFloat(inv.transaction_amount || 0) > 0
            );

            if (paidInvoice && paidInvoice.updated_at) {
                return new Date(paidInvoice.updated_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
            }

            return 'N/A';
        },
        normalInvoices() {
            if (!this.selectedSite || !this.selectedSite.invoices) return [];
            return this.selectedSite.invoices.filter(i => i.invoice_type !== 'school-program');
        },
        schoolInvoices() {
            if (!this.selectedSite || !this.selectedSite.invoices) return [];
            return this.selectedSite.invoices.filter(i => i.invoice_type === 'school-program');
        },
        totalNormalInvoices() {
            return this.normalInvoices.reduce((sum, i) => sum + Number(i.beginning_balance || 0), 0);
        },
        totalSchoolProgram() {
            return this.schoolInvoices.reduce((sum, i) => sum + Number(i.beginning_balance || 0), 0);
        },
        remainingAmount() {
            return this.totalNormalInvoices - this.totalSchoolProgram;
        },

        // View Invoice Computed Properties
        viewNormalInvoices() {
            if (!this.viewSelectedSite || !this.viewSelectedSite.invoices) return [];
            return this.viewSelectedSite.invoices.filter(i => i.invoice_type !== 'school-program');
        },
        viewSchoolInvoices() {
            if (!this.viewSelectedSite || !this.viewSelectedSite.invoices) return [];
            return this.viewSelectedSite.invoices.filter(i => i.invoice_type === 'school-program');
        },
        viewTotalNormalBeginningBalance() {
            return this.viewNormalInvoices.reduce((sum, inv) => {
                if (inv.invoice_type === 'withdraw') return sum;
                return sum + parseFloat(inv.beginning_balance || 0);
            }, 0);
        },
        viewTotalNormalTransactionAmount() {
            return this.viewNormalInvoices.reduce((sum, inv) => {
                if (inv.invoice_type === 'withdraw') return sum;
                return sum + parseFloat(inv.transaction_amount || 0);
            }, 0);
        },
        viewTotalNormalRemainAmount() {
            return this.viewNormalInvoices.reduce((sum, inv) => {
                if (inv.invoice_type === 'withdraw') return sum;
                return sum + parseFloat(inv.remain_amount || 0);
            }, 0);
        },
        viewTotalSchoolBeginningBalance() {
            return this.viewSchoolInvoices.reduce((sum, inv) =>
                sum + parseFloat(inv.beginning_balance || 0), 0
            );
        },
        viewTotalSchoolTransactionAmount() {
            return this.viewSchoolInvoices.reduce((sum, inv) =>
                sum + parseFloat(inv.transaction_amount || 0), 0
            );
        },
        viewTotalSchoolRemainAmount() {
            return this.viewSchoolInvoices.reduce((sum, inv) =>
                sum + parseFloat(inv.remain_amount || 0), 0
            );
        },
        viewTotalBeginningBalance() {
            return this.viewTotalNormalBeginningBalance - this.viewTotalSchoolBeginningBalance;
        },
        viewTotalTransactionAmount() {
            return this.viewTotalNormalTransactionAmount - this.viewTotalSchoolTransactionAmount;
        },
        viewTotalRemainAmount() {
            return this.viewTotalNormalRemainAmount + this.viewTotalSchoolRemainAmount;
        },
        viewNetAmount() {
            return this.viewTotalNormalBeginningBalance - this.viewTotalSchoolBeginningBalance;
        },
        viewPaymentStatus() {
            if (this.viewTotalRemainAmount === 0) return 'Fully Paid';
            if (this.viewTotalTransactionAmount > 0 && this.viewTotalRemainAmount > 0) return 'Partially Paid';
            return 'Unpaid';
        },
        viewPaymentStatusColor() {
            if (this.viewTotalRemainAmount === 0) return 'green-lighten-5';
            if (this.viewTotalTransactionAmount > 0 && this.viewTotalRemainAmount > 0) return 'orange-lighten-5';
            return 'red-lighten-5';
        },

        groupedByPlatform() {
            return this.samples.reduce((acc, site) => {
                if (!acc[site.Platform]) acc[site.Platform] = []
                acc[site.Platform].push(site)
                return acc
            }, {})
        },
        platformsToDisplay() {
            if (this.selectedPlatform === 'All') {
                return this.groupedByPlatform
            }
            return {
                [this.selectedPlatform]: this.groupedByPlatform[this.selectedPlatform] || []
            }
        },
        platformFilterItems() {
            return ['All', ...Object.keys(this.groupedByPlatform)]
        },
        pendingSites() {
            return (sites) => {
                const searchLower = this.search.toLowerCase()
                return sites.filter(site =>
                    site.latest_invoice?.status === 'pending' &&
                    (!this.search || site.Id_Site.toLowerCase().includes(searchLower))
                )
            }
        },
        sentSites() {
            return (sites) => {
                const searchLower = this.search.toLowerCase();
                return sites.filter(site => {
                    const status = site.latest_invoice?.status || '';
                    return status.toLowerCase() == 'sending' &&
                        (!this.search || site.Id_Site.toLowerCase().includes(searchLower));
                });
            };
        },
        settleSites() {
            return (sites) => {
                const searchLower = this.search.toLowerCase();
                return sites.filter(site => {
                    const status = site.latest_invoice?.status || '';
                    const invoiceType = site.latest_invoice?.invoice_type || '';
                    return invoiceType !== 'withdraw' && status.toLowerCase() == 'settle' &&
                        (!this.search || site.Id_Site.toLowerCase().includes(searchLower));
                });
            };
        }
    },
    methods: {
        formatNumberComma(value) {
        if (!value && value !== 0) return '';
        return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        },
        downloadCashierReport() {
            alert("Excel download functionality is in progress. Thank you for your patience!")
        },
        formatDateMinusOneMonth(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        date.setMonth(date.getMonth() - 1);
        
        // Format as YYYY-MM
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        return `${year}-${month}`;
        },
        downloadInvoice(){
            alert ("Download Invoice functionality is in progress. Thank you for your patience!")
        },
        formatAndValidateAmount() {
            let value = this.formattedAmount || '';
            value = value.toString();
            // Remove non-digit except dot
            let numeric = value.replace(/[^\d.]/g, '');
            let amount = parseFloat(numeric) || 0;

            // If Withdrawal and exceeds siteBalance
            if (this.transactionType === 'Withdrawal' && amount > this.siteBalance) {
                this.snackbar.message = `Amount cannot exceed site balance: ៛${this.siteBalance}`;
                this.snackbar.show = true;

                amount = this.siteBalance; // limit to max
            }
            // Format number with commas
            this.formattedAmount = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(amount);
        },
        openConfirmDialog() {
            this.confirmDialog = true;
        },
        formatAmount(event, field) {
            let value = event.target.value || "";

            // Remove all commas first
            value = value.replace(/,/g, "");

            // Allow only digits (prevent letters & symbols)
            value = value.replace(/[^\d]/g, "");

            // Save raw amount
            this.amount = value;

            // Format 1,000,000 style
            this[field] = value.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        },
        formatNumber(number) {
            return new Intl.NumberFormat().format(number);
        },
        async saveTransaction() {
            this.confirmDialog = false;
            try {
                const response = await axios.post('/api/updateBalance', {
                    site: this.selectedSiteForBalance,
                    amount: this.formattedAmount.replace(/,/g, ''), // send raw number without commas
                    invoice_type: this.transactionType,
                    month: this.selectedDate
                });

                this.snackbar = {
                    show: true,
                    message: 'Balance updated successfully!',
                    color: 'success',
                };
                this.depositAndWithdrawalDialog = false;
                this.selectedSiteForBalance = '';
                this.transactionType = '';
                this.amount = '';
                this.formattedAmount = '';
                this.balance = '';
            } catch (error) {
                console.error('Error updating balance:', error);
                this.snackbar = {
                    show: true,
                    message: 'Failed to update balance.',
                    color: 'error',
                };
            }
        },
        async depositAndwithdraw() {
            this.depositAndWithdrawalDialog = true;
            try {
                const response = await axios.get(`/api/getSite`);
                // Assuming response.data.sites is an array of site objects
                this.siteOptions = response.data.sites.map(site => ({
                    id: site.Id_Site,
                    name: site.Name || site.Id_Site // Use site name if available
                }));

            } catch (error) {

            }
        },
        async downloadQRCode() {
            if (!this.qrCodeUrl) return;

            this.downloadingQR = true;
            try {
                const response = await fetch(this.qrCodeUrl);
                const blob = await response.blob();

                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;

                // Extract filename from path
                const fileName = this.qrCodePath.split('/').pop() || `QR_${this.viewSelectedSite?.Id_Site}.jpg`;
                a.download = fileName;

                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } catch (error) {
                console.error('Error downloading QR code:', error);
                // Fallback: open in new tab
                window.open(this.qrCodeUrl, '_blank');
            } finally {
                this.downloadingQR = false;
            }
        },
        settleInvoice(Id_Site) {
            this.selectedItem = Id_Site;
            this.dialog = true;
        },
        viewInvoice(site) {
            this.viewSelectedSite = site;
            this.viewInvoiceDialog = true;
        },
        openInvoice(site) {
            this.selectedSite = site
            this.invoiceDialog = true
        },
        formatNumber(num) {
            if (num === null || num === undefined || isNaN(num)) return '0'
            const numStr = num.toString()
            return numStr.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
        },
        formatMonth(monthString) {
            if (!monthString) return 'N/A';
            const date = new Date(monthString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long'
            });
        },
        getStatusColor(status) {
            switch (status?.toLowerCase()) {
                case 'settle': return 'green'
                case 'paid': return 'green'
                case 'pending': return 'orange'
                case 'sending': return 'blue'
                case 'overdue': return 'red'
                case 'partial': return 'blue'
                default: return 'grey'
            }
        },
        getRemainAmountColor(amount) {
            const num = parseFloat(amount || 0)
            if (num === 0) return 'green'
            if (num > 0) return 'orange'
            return 'grey'
        },
        getDataInvoices() {
            this.loading = true
            const month = this.selectedDate ? this.selectedDate : null

            axios.get('/api/allInvoices', {
                params: {
                    month
                }
            }).then(res => {
                this.samples = res.data.data
                this.loading = false
            }).catch(() => {
                this.loading = false
            })
        },
        sendInvoicePDF1() {
            if (!this.selectedSite) return;
            this.sending = true;
            const month = this.selectedDate || (this.selectedSite.latest_invoice?.month ?
                new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7) : null);
            axios.post('/api/invoices/update-status-by-site-month', {
                Id_Site: this.selectedSite.Id_Site,
                month: month
            })
                .then(() => {
                    const siteIndex = this.samples.findIndex(s => s.Id_Site === this.selectedSite.Id_Site);
                    if (siteIndex !== -1) {
                        this.samples[siteIndex].latest_invoice.status = this.samples[siteIndex].latest_invoice.status === 'pending' ? 'sending' : 'settle';
                        this.samples[siteIndex].invoices = this.samples[siteIndex].invoices.map(inv => {
                            if (inv.status === 'pending') inv.status = 'sending';
                            else if (inv.status === 'sending') inv.status = 'settle';
                            return inv;
                        });

                        this.selectedSite = { ...this.samples[siteIndex] };
                    }

                    const normalInvoices = this.selectedSite.invoices.filter(inv =>
                        inv.invoice_type !== 'school-program'
                    );
                    const schoolInvoices = this.selectedSite.invoices.filter(inv =>
                        inv.invoice_type === 'school-program'
                    );

                    const totalNormalAmount = normalInvoices.reduce((sum, inv) =>
                        sum + (parseFloat(inv.beginning_balance) || 0), 0
                    );
                    const totalSchoolAmount = schoolInvoices.reduce((sum, inv) =>
                        sum + (parseFloat(inv.beginning_balance) || 0), 0
                    );
                    const netAmount = totalNormalAmount - totalSchoolAmount;

                    const doc = new jsPDF();

                    doc.setFontSize(16);
                    doc.text(`Invoices for site ${this.selectedSite.Id_Site}`, 14, 15);

                    doc.setFontSize(12);
                    doc.text('Normal Invoices', 14, 30);

                    const normalRows = normalInvoices.map(inv => ([
                        inv.month || '',
                        inv.invoice_type || '',
                        inv.status || '',
                        this.formatNumber(parseFloat(inv.beginning_balance) || 0)
                    ]));

                    normalRows.push([
                        'TOTAL',
                        '',
                        '',
                        this.formatNumber(totalNormalAmount)
                    ]);

                    autoTable(doc, {
                        head: [['Month', 'Type', 'Status', 'Amount']],
                        body: normalRows,
                        startY: 35,
                        styles: { fontSize: 10 },
                        headStyles: { fillColor: [66, 133, 244] },
                        didDrawPage: function (data) {
                            data.settings.margin.top = data.cursor.y + 15;
                        }
                    });

                    const currentY = doc.lastAutoTable.finalY || 35;

                    doc.setFontSize(12);
                    doc.text('School Program Invoices', 14, currentY + 10);

                    const schoolRows = schoolInvoices.map(inv => ([
                        inv.month || '',
                        inv.invoice_type || '',
                        inv.status || '',
                        this.formatNumber(parseFloat(inv.beginning_balance) || 0)
                    ]));

                    schoolRows.push([
                        'TOTAL',
                        '',
                        '',
                        this.formatNumber(totalSchoolAmount)
                    ]);

                    autoTable(doc, {
                        head: [['Month', 'Type', 'Status', 'Amount']],
                        body: schoolRows,
                        startY: currentY + 15,
                        styles: { fontSize: 10 },
                        headStyles: { fillColor: [76, 175, 80] },
                        didDrawPage: function (data) {
                            data.settings.margin.top = data.cursor.y + 15;
                        }
                    });

                    const finalY = doc.lastAutoTable.finalY || currentY + 15;

                    doc.setFontSize(12);
                    doc.setFont(undefined, 'bold');
                    doc.text('Summary', 14, finalY + 15);

                    doc.setFont(undefined, 'normal');
                    doc.setFontSize(10);

                    let yPos = finalY + 25;
                    doc.text(`Total Normal Invoices: ${this.formatNumber(totalNormalAmount)}`, 20, yPos);
                    yPos += 7;
                    doc.text(`Total School Program: ${this.formatNumber(totalSchoolAmount)}`, 20, yPos);
                    yPos += 10;

                    doc.setFont(undefined, 'bold');
                    doc.setFontSize(11);
                    const netText = `Net Amount (Normal - School Program): ${this.formatNumber(netAmount)}`;
                    doc.text(netText, 20, yPos);

                    if (netAmount > 0) {
                        doc.setTextColor(0, 128, 0);
                    } else if (netAmount < 0) {
                        doc.setTextColor(255, 0, 0);
                    } else {
                        doc.setTextColor(0, 0, 0);
                    }

                    doc.setTextColor(0, 0, 0);

                    const pdfBlob = doc.output('blob');

                    const formData = new FormData();
                    formData.append('file', pdfBlob, `${this.selectedSite.Id_Site}_invoice.pdf`);
                    formData.append('chat_id', '7359315398');

                    return axios.post('/api/send-invoice-telegram', formData);
                })
                .then(() => {
                    this.invoiceDialog = false;
                })
                .catch(err => {
                    console.error('Error sending invoice:', err);
                })
                .finally(() => {
                    this.sending = false;
                });
        },
        async sendInvoicePDF() {
            if (!this.selectedSite) return;
            this.sending = true;

            try {
                // Update status on server
                const month = this.selectedDate || (this.selectedSite.latest_invoice?.month
                    ? new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7)
                    : null);

                await axios.post('/api/invoices/update-status-by-site-month', {
                    Id_Site: this.selectedSite.Id_Site,
                    month: month
                });

                // Update local samples status
                const siteIndex = this.samples.findIndex(s => s.Id_Site === this.selectedSite.Id_Site);
                if (siteIndex !== -1) {
                    this.samples[siteIndex].latest_invoice.status =
                        this.samples[siteIndex].latest_invoice.status === 'pending' ? 'sending' : 'settle';

                    this.samples[siteIndex].invoices = this.samples[siteIndex].invoices.map(inv => {
                        if (inv.status === 'pending') return { ...inv, status: 'sending' };
                        if (inv.status === 'sending') return { ...inv, status: 'settle' };
                        return inv;
                    });

                    this.selectedSite = { ...this.samples[siteIndex] };
                }

                // Separate invoices by type
                const normalInvoices = this.selectedSite.invoices.filter(inv => inv.invoice_type !== 'school-program');
                const schoolInvoices = this.selectedSite.invoices.filter(inv => inv.invoice_type === 'school-program');

                // Prepare rows for tables
                const normalRows = normalInvoices.map((inv, idx) => ({
                    no: idx + 1,
                    itemCode: inv.invoice_code || inv.invoice_type || '',
                    price: parseFloat(inv.beginning_balance) || 0,
                    totalPrice: parseFloat(inv.beginning_balance) || 0,
                }));

                const totalNormal = normalRows.reduce((sum, item) => sum + item.totalPrice, 0);

                const schoolRows = schoolInvoices.map((inv, idx) => ({
                    no: idx + 1,
                    itemCode: inv.invoice_code || inv.invoice_type || '',
                    price: parseFloat(inv.beginning_balance) || 0,
                    totalPrice: parseFloat(inv.beginning_balance) || 0,
                }));

                const totalSchool = schoolRows.reduce((sum, item) => sum + item.totalPrice, 0);

                // Initialize jsPDF
                const doc = new jsPDF();

                // Render Khmer header text as image using canvas
                const khmerText = 'អង្គការទឹកស្អាត១០០១';
                const khmerTextImage = await this.renderKhmerTextToImage(khmerText);

                // Add logo image (optional)
                const logoDataUrl = await this.loadImageAsDataURL('/img/logo.png');
                if (logoDataUrl) {
                    doc.addImage(logoDataUrl, 'PNG', 14, 10, 20, 15);
                }

                // Add Khmer text image header
                doc.addImage(khmerTextImage, 'PNG', 50, 20, 100, 20);

                // Other header text in default font
                doc.setFont('helvetica', 'normal');
                doc.setFontSize(16);
                doc.text(this.selectedSite.platform || 'BTB', doc.internal.pageSize.getWidth() / 2, 45, { align: 'center' });

                const leftX = 14;
                const rightX = doc.internal.pageSize.getWidth() - 60;
                let startY = 55;

                doc.setFontSize(12);
                doc.text(`Date: ${this.selectedSite.latest_invoice?.date || month || ''}`, leftX, startY);
                doc.text(`To: ${this.selectedSite.Id_Site || 'N/A'}`, leftX, startY + 7);
                doc.text(`Platform: ${this.selectedSite.platform || 'BTB'}`, leftX, startY + 14);

                doc.text(`No: ${this.selectedSite.latest_invoice?.invoice_no || 'N/A'}`, rightX, startY);
                doc.text(`Advisor: ${this.selectedSite.Advisor || 'N/A'}`, rightX, startY + 7);
                doc.text(`Cashier: ${this.selectedSite.cashier || 'N/A'}`, rightX, startY + 14);

                doc.setFontSize(16);
                doc.text('INVOICES', doc.internal.pageSize.getWidth() / 2, startY + 30, { align: 'center' });

                // Columns definition for autoTable
                const columns = [
                    { header: 'No', dataKey: 'no' },
                    { header: 'Item Name', dataKey: 'itemCode' },
                    { header: 'Price', dataKey: 'price' },
                    { header: 'Total Price', dataKey: 'totalPrice' },
                ];

                // Format normal invoices rows
                const normalRowsFormatted = normalRows.map(i => ({
                    no: i.no,
                    itemCode: i.itemCode,
                    price: this.formatNumber(i.price),
                    totalPrice: this.formatNumber(i.totalPrice),
                }));
                normalRowsFormatted.push({
                    no: '',
                    itemCode: '',
                    price: 'Total',
                    totalPrice: this.formatNumber(totalNormal),
                });

                // Add normal invoices table
                autoTable(doc, {
                    startY: startY + 35,
                    head: [columns.map(c => c.header)],
                    body: normalRowsFormatted.map(r => columns.map(c => r[c.dataKey])),
                    styles: { fontSize: 10, halign: 'center', valign: 'middle', cellPadding: 2 },
                    headStyles: { fillColor: [240, 240, 240], textColor: 0 },
                    footStyles: { fillColor: [220, 220, 220], textColor: 0, fontStyle: 'bold' },
                    theme: 'grid',
                });

                // School program invoices table startY
                const startY2 = doc.lastAutoTable.finalY + 15;
                doc.setFontSize(16);
                doc.text('SCHOOL PROGRAM INVOICES', doc.internal.pageSize.getWidth() / 2, startY2 - 5, { align: 'center' });

                // Format school invoices rows
                const schoolRowsFormatted = schoolRows.map(i => ({
                    no: i.no,
                    itemCode: i.itemCode,
                    price: this.formatNumber(i.price),
                    totalPrice: this.formatNumber(i.totalPrice),
                }));
                schoolRowsFormatted.push({
                    no: '',
                    itemCode: '',
                    price: 'Total',
                    totalPrice: this.formatNumber(totalSchool),
                });

                // Add school program invoices table
                autoTable(doc, {
                    startY: startY2,
                    head: [columns.map(c => c.header)],
                    body: schoolRowsFormatted.map(r => columns.map(c => r[c.dataKey])),
                    styles: { fontSize: 10, halign: 'center', valign: 'middle', cellPadding: 2 },
                    headStyles: { fillColor: [200, 230, 201], textColor: 0 },
                    footStyles: { fillColor: [176, 190, 197], textColor: 0, fontStyle: 'bold' },
                    theme: 'grid',
                });

                // Summary section
                const finalY = doc.lastAutoTable.finalY + 20;
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text('SUMMARY', doc.internal.pageSize.getWidth() / 2, finalY, { align: 'center' });

                doc.setFontSize(12);
                const netAmount = totalNormal - totalSchool;
                const summaryY = finalY + 10;

                doc.setFont('helvetica', 'normal');
                doc.text(`Total Normal Invoices: ${this.formatNumber(totalNormal)}`, leftX, summaryY);
                doc.text(`Total School Program: ${this.formatNumber(totalSchool)}`, leftX, summaryY + 8);

                doc.setFont('helvetica', 'bold');
                doc.text(`Remaining Amount to Pay: ${this.formatNumber(netAmount)}`, leftX, summaryY + 18);

                // Footer signatures
                const pageWidth = doc.internal.pageSize.getWidth();
                const colWidth = 50;
                const spacing = (pageWidth - colWidth * 3) / 4;
                const sigY = summaryY + 50;
                const sigLabels = ['Buyer', 'Seller', 'Staff'];

                sigLabels.forEach((label, i) => {
                    const x = spacing + (colWidth + spacing) * i;
                    doc.setFontSize(12);
                    doc.setFont('helvetica', 'normal');
                    doc.text(label, x + colWidth / 2, sigY, { align: 'center' });
                    doc.line(x, sigY + 10, x + colWidth, sigY + 10);
                });

                // Export PDF blob
                const pdfBlob = doc.output('blob');

                // Send PDF via axios (Telegram API as example)
                const formData = new FormData();
                formData.append('file', pdfBlob, `${this.selectedSite.Id_Site}_invoice.pdf`);
                formData.append('chat_id', '7359315398');

                await axios.post('/api/send-invoice-telegram', formData);

                this.invoiceDialog = false;

            } catch (err) {
                console.error('Error sending invoice:', err);
            } finally {
                this.sending = false;
            }
        },
        async sendInvoiceAsImage1() {
            if (!this.selectedSite) return;
            this.sending = true;
            let chatID = '7359315398';
            try {
                // Safely get month string
                const month = this.selectedDate || (
                    this.selectedSite?.latest_invoice?.month
                        ? new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7)
                        : null
                );

                // 1. Update invoice status on server
                await axios.post('/api/invoices/update-status-by-site-month', {
                    Id_Site: this.selectedSite.Id_Site,
                    month: month
                });
                // 3. Fetch invoice data from API to update the view
                const response = await axios.get(`/api/getChatID/${this.selectedSite.Id_Site}`);

                if (response.data.success) {
                    chatID = response.data.data.chat_id;


                    // Optional: Store in selectedSite for UI
                    this.selectedSite = {
                        ...this.selectedSite,
                        telegram_chat_id: chatID,
                        has_telegram_group: response.data.data.found || response.data.data.has_groups
                    };
                } else {
                    console.warn('⚠️ Using default chat ID:', response.data.message);
                }

                // 2. Update local status in samples array safely
                const siteIndex = this.samples.findIndex(s => s.Id_Site === this.selectedSite.Id_Site);
                if (siteIndex !== -1) {
                    const site = this.samples[siteIndex];
                    if (site.latest_invoice) {
                        site.latest_invoice.status =
                            site.latest_invoice.status === 'pending' ? 'sending' : 'settle';
                    }

                    site.invoices = site.invoices.map(inv => {
                        if (inv.status === 'pending') return { ...inv, status: 'sending' };
                        if (inv.status === 'sending') return { ...inv, status: 'settle' };
                        return inv;
                    });

                    // Update selectedSite reactive copy
                    this.selectedSite = { ...site };
                }

                // 3. Prepare invoice div and show it for capture
                const invoiceEl = this.$refs.invoice;
                if (!invoiceEl) throw new Error('Invoice element not found');

                invoiceEl.style.display = 'block';  // Show for capture

                // 4. Capture with html2canvas
                const canvas = await html2canvas(invoiceEl, {
                    scale: 2,
                    backgroundColor: '#fff',
                    useCORS: true,
                });

                // Hide again after capture
                invoiceEl.style.display = 'none';

                // 5. Convert to blob and upload
                canvas.toBlob(async (blob) => {
                    if (!blob) {
                        console.error('Failed to generate image blob');
                        this.sending = false;
                        return;
                    }

                    const formData = new FormData();
                    formData.append('file', blob, `${this.selectedSite.Id_Site}_invoice.png`);
                    formData.append('chat_id', chatID);

                    await axios.post('/api/send-invoice-telegram', formData);

                    this.invoiceDialog = false;
                    this.sending = false;
                });

            } catch (err) {
                console.error('Error sending invoice as image:', err);
                this.sending = false;
            }
        },
        async sendInvoiceAsImage() {
            if (!this.selectedSite) return;
            this.sending = true;
            
            let chatID = '7359315398';

            try {
                const month = this.selectedDate || (
                    this.selectedSite?.latest_invoice?.month
                        ? new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7)
                        : null
                );

                // 1. Update invoice status
                await axios.post('/api/invoices/update-status-by-site-month', {
                    Id_Site: this.selectedSite.Id_Site,
                    month: month
                });

                // 2. Get chat ID
                const response = await axios.get(`/api/getChatID/${this.selectedSite.Id_Site}`);
                if (response.data.success) {
                    chatID = response.data.data.chat_id;
                }
                const siteIndex = this.samples.findIndex(s => s.Id_Site === this.selectedSite.Id_Site);
                if (siteIndex !== -1) {
                    const site = this.samples[siteIndex];
                    if (site.latest_invoice) {
                        site.latest_invoice.status =
                            site.latest_invoice.status === 'pending' ? 'sending' : 'settle';
                    }

                    site.invoices = site.invoices.map(inv => {
                        if (inv.status === 'pending') return { ...inv, status: 'sending' };
                        if (inv.status === 'sending') return { ...inv, status: 'settle' };
                        return inv;
                    });

                    // Update selectedSite reactive copy
                    this.selectedSite = { ...site };
                }
                // 3. Capture invoice
                const invoiceEl = this.$refs.invoice;
                invoiceEl.style.display = 'block';

                const canvas = await html2canvas(invoiceEl, {
                    scale: 2,
                    backgroundColor: '#fff',
                    useCORS: true,
                });

                invoiceEl.style.display = 'none';
                const amount = this.totalNormalInvoices - this.totalSchoolProgram;
                // 4. Convert to blob & send
                canvas.toBlob(async (blob) => {
                    const formData = new FormData();
                    formData.append('file', blob, `${this.selectedSite.Id_Site}_invoice.png`);
                    formData.append('chat_id', chatID);
                    formData.append('amount', amount);

                    await axios.post('/api/send-invoice-telegram', formData);

                    this.invoiceDialog = false;
                    this.sending = false;
                });

            } catch (err) {
                console.error(err);
                this.sending = false;
            }
        },
        // Helper method to load image as base64 data URL
        async loadImageAsDataURL(url) {
            return new Promise((resolve, reject) => {
                const img = new Image();
                img.crossOrigin = "Anonymous";
                img.onload = function () {
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    resolve(canvas.toDataURL('image/png'));
                };
                img.onerror = reject;
                img.src = url;
            });
        },
        async renderKhmerTextToImage(text, font = 'Khmer OS System', fontSize = 28) {
            return new Promise((resolve) => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                canvas.width = 600;
                canvas.height = 80;

                // Clear canvas
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Set font with Khmer font-family loaded by CSS
                ctx.font = `${fontSize}px "${font}", sans-serif`;
                ctx.fillStyle = '#000';
                ctx.textBaseline = 'top';

                // Draw the Khmer text
                ctx.fillText(text, 10, 10);

                // Convert canvas to DataURL (base64 PNG)
                const dataUrl = canvas.toDataURL('image/png');

                resolve(dataUrl);
            });
        },
        formatNumber(value) {
            return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        },
        printViewInvoice() {
            window.print();
        }
    },
    mounted() {
        this.getDataInvoices()
    }
}
</script>
<style scoped>
.site {
    position: relative;
}

@font-face {
    font-family: 'Khmer OS System';
    src: url('/font/Khmer OS System Regular.ttf') format('truetype');
    font-weight: normal;
    font-style: normal;
}

body,
#invoice-to-capture {
    font-family: 'Khmer OS System', sans-serif !important;
}

.amount-input input {
    font-weight: bold !important;
    font-size: 18px !important;
}

th.text-center {
    padding: 12px 0;
    color: #2c3e50;
    font-weight: 700;
    border-bottom: 2px solid #ddd;
    background: #f9fafb;
}
.amount-to-pay {
  font-size: 30px !important;
  font-weight: bold;
  letter-spacing: 0.5px;
  color: #d32f2f !important; /* Darker red */
  border: 3px solid #d32f2f;
  padding: 15px;
  border-radius: 10px;
  background-color: #ffcdd2; /* Light red background */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Optional shadow for better visibility */
}
/* Platform colors - assign colors for each platform */
th.text-center:nth-child(2) {
    background-color: #d0e7ff;
    color: #064273;
}

/* Platform 1 */
th.text-center:nth-child(3) {
    background-color: #ffdede;
    color: #7a1f1f;
}

.qr-container {
    border: 2px dashed #e0e0e0;
    border-radius: 8px;
    background-color: #fafafa;
}

.qr-image {
    border: 1px solid #ddd;
    border-radius: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* For print view */
@media print {

    .v-btn,
    .v-card-actions {
        display: none !important;
    }

    .qr-container {
        border: 1px solid #000;
        page-break-inside: avoid;
    }
}

/* Platform 2 */
th.text-center:nth-child(4) {
    background-color: #dfffd6;
    color: #2d5800;
}

/* Platform 3 */
th.text-center:nth-child(5) {
    background-color: #fff4d1;
    color: #705800;
}

/* Platform 4 */
th.text-center:nth-child(6) {
    background-color: #e8d6ff;
    color: #3a0f6f;
}

/* Platform 5 */
.v-chip {
    border-radius: 40% !important;
    border: 1px solid #6c757d;
    background-color: #f0f3f5 !important;
    color: #2c3e50 !important;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 48px;
    justify-content: center;
}

.v-chip:hover {
    background-color: #d9e9ff !important;
    border-color: #1a73e8;
    color: #1a3c7c !important;
    box-shadow: 0 4px 8px rgba(26, 115, 232, 0.3);
}

/* Highlight animation on search */
.highlighted {
    animation: blinking 0.8s infinite alternate;
    border-color: #1a73e8 !important;
    box-shadow: 0 0 12px 2px rgba(26, 115, 232, 0.8);
}

.sent-chip {
    background-color: #a5d6a7 !important;
    /* light green */
    border-color: #4caf50 !important;
    /* darker green border */
    color: #1b5e20 !important;
    /* dark green text */
}
.sent-chip-sending {
    background-color: #FFE082 !important;  /* vibrant light yellow */
    border-color: #FFA000 !important;      /* darker gold border */
    color: #3E2723 !important;             /* almost black brown */
}
tbody tr th {
    font-weight: 600;
    color: #2c3e50;
    background-color: #f7f9fb;
    border-right: 1px solid #ddd;
    vertical-align: middle;
}

/* Table cell style */
tbody td {
    padding: 12px 8px;
    vertical-align: middle;
}

/* Light background for table */
.v-table {
    background-color: #ffffff;
    box-shadow: 0 2px 10px rgb(0 0 0 / 0.1);
    border-radius: 8px;
}

/* Loading spinner container */
.d-flex.justify-center.mt-10 {
    margin-top: 3rem;
    margin-bottom: 3rem;
}

/* Filter bar spacing */
.d-flex.pa-4 {
    background-color: #f7f9fb;
    border-radius: 8px;
    margin-bottom: 1.5rem;
}

/* v-select and v-text-field consistent widths */
.v-select,
.v-text-field {
    max-width: 200px;
}

.badge {
    position: absolute;
    top: -4px;
    right: -6px;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: #000;
    color: #fff;
    font-size: 10px;
    text-align: center;
    line-height: 16px;
}

.highlighted {
    animation: blink 0.5s infinite alternate;
}

@keyframes blink {
    from {
        box-shadow: 0 0 2px #2196f3;
    }

    to {
        box-shadow: 0 0 10px #2196f3;
    }
}
</style>
