<template>

    <div>
        <v-table v-if="!loading" density="compact">
            <thead>
                <tr>
                    <th></th>
                    <th v-for="(sites, platform) in platformsToDisplay" :key="platform" class="text-center"
                        :class="platform + '-header'">
                        {{ platform }}
                    </th>
                </tr>
            </thead>

            <tbody>
                <!-- Settled -->
                <tr>
                    <th class="text-center">{{ $t('invoices.status_settle') }}</th>
                    <td v-for="(sites, platform) in platformsToDisplay" :key="platform">
                        <div class="d-flex flex-wrap justify-center">
                            <v-chip v-for="site in settleSites(sites)" :key="site.Id_Site" size="small"
                                color="green-lighten-2" variant="elevated" class="ma-1"
                                :class="{ highlighted: searchQuery && site.Id_Site.toLowerCase().includes(searchQuery.toLowerCase()) }"
                                @click="viewInvoice(site)">
                                {{ site.Id_Site }}
                            </v-chip>
                        </div>
                    </td>
                </tr>
                <!-- Sent -->
                <tr>
                    <th class="text-center">{{ $t('invoices.status_sending') }}</th>
                    <td v-for="(sites, platform) in platformsToDisplay" :key="platform">
                        <div class="d-flex flex-wrap justify-center">
                            <v-chip v-for="site in sentSites(sites)" :key="site.Id_Site" size="small"
                                color="yellow-lighten-2" variant="elevated" class="ma-1"
                                :class="{ highlighted: searchQuery && site.Id_Site.toLowerCase().includes(searchQuery.toLowerCase()) }"
                                @click="settleInvoice(site.Id_Site)">
                                {{ site.Id_Site }}
                            </v-chip>

                        </div>
                    </td>
                </tr>
                <!-- Pending -->
                <tr>
                    <th class="text-center">{{ $t('invoices.status_pending') }}</th>

                    <td v-for="(sites, platform) in platformsToDisplay" :key="platform">
                        <div class="d-flex flex-wrap justify-center">
                            <v-chip v-for="site in pendingSites(sites)" :key="site.Id_Site" size="small"
                                color="orange-lighten-2" variant="elevated" class="ma-1"
                                :class="{ highlighted: searchQuery && site.Id_Site.toLowerCase().includes(searchQuery.toLowerCase()) }"
                                @click="openInvoice(site)">
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
                    <span class="text-primary font-weight-bold text-center d-block">{{ $t('invoices.site_title') }} {{
                        selectedSite?.Id_Site }}</span>
                </v-card-title>

                <v-card-text>
                    <!-- ========== NORMAL INVOICES TABLE ========== -->
                    <h4 class="mb-2 text-center d-block">{{ $t('invoices.section_invoices') }}</h4>

                    <v-table density="compact">
                        <thead style="background-color: #f0f0f0;">
                            <tr>
                                <th style="color: #007bff; font-weight: bold;">{{ $t('invoices.table_month') }}</th>
                                <th style="color: #007bff; font-weight: bold;">{{ $t('invoices.table_type') }}</th>
                                <!-- <th style="color: #007bff; font-weight: bold;">Status</th> -->
                                <th class="text-right" style="color: #007bff; font-weight: bold;">{{
                                    $t('invoices.table_amount') }}</th>
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
                                <td colspan="2" class="text-right">{{ $t('invoices.total_invoices') }}</td>
                                <td class="text-right">
                                    {{ totalNormalInvoices.toLocaleString() }}
                                </td>
                            </tr>
                        </tbody>
                    </v-table>

                    <!-- ========== SCHOOL PROGRAM SUMMARY ROW ========== -->

                    <h4 class="mt-6 mb-2 text-center d-block">{{ $t('invoices.section_school_program') }}</h4>

                    <v-table density="compact">
                        <thead style="background-color: #f0f0f0;">
                            <tr>
                                <th style="color: #007bff; font-weight: bold;">{{ $t('invoices.table_month') }}</th>
                                <th style="color: #007bff; font-weight: bold;">{{ $t('invoices.table_type') }}</th>
                                <!-- <th style="color: #007bff; font-weight: bold;">Status</th> -->
                                <th class="text-right" style="color: #007bff; font-weight: bold;">{{
                                    $t('invoices.table_amount') }}</th>
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

                            <!-- REMAINING AMOUNT ROW -->
                            <tr class="font-weight-bold"
                                :class="{ 'text-green-darken-2': remainingAmount > 0, 'text-red-darken-2': remainingAmount < 0 }">
                                <td :colspan="remainingAmount > 0 ? 5 : 5" class="text-center py-3"
                                    style="font-size: 20px; font-weight: bold; letter-spacing: 0.5px;">
                                    <v-icon v-if="remainingAmount > 0" small class="mr-2">mdi-plus-circle</v-icon>
                                    <v-icon v-else small class="mr-2">mdi-minus-circle</v-icon>

                                    <span v-if="remainingAmount > 0">
                                        {{ $t('invoices.remaining_amount') }} {{ remainingAmount.toLocaleString() }}
                                    </span>
                                    <span v-else>
                                        {{ $t('invoices.school_amount_remaining') }} {{ remainingAmount.toLocaleString()
                                        }}
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
                    <v-btn color="success" @click="downloadInvoice" variant="elevated">
                        {{ $t('invoices.download_invoice') }}
                    </v-btn>
                    <v-spacer />
                    <!-- Red send button -->
                    <v-btn color="error" @click="sendInvoiceAsImage" :loading="sending" :disabled="sending"
                        variant="elevated" class="mr-2">
                        {{ $t('invoices.send_invoice') }}
                    </v-btn>
                    <v-btn @click="invoiceDialog = false" :disabled="sending">
                        {{ $t('invoices.close') }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- View Invoice Modal (Detailed View) -->
        <v-dialog v-model="viewInvoiceDialog" max-width="600">
            <v-card>
                <v-card-title class="bg-primary text-white">
                    <v-icon start>mdi-file-document-multiple</v-icon>
                    {{ $t('invoices.details_title') }} {{ viewSelectedSite?.Id_Site }}
                    <v-chip class="ml-2" color="white" text-color="primary">
                        {{ viewSelectedSite?.Platform }}
                    </v-chip>
                    <v-spacer />
                </v-card-title>

                <v-card-subtitle class="pa-4">
                    <div class="d-flex align-center">
                        <v-icon start size="small">mdi-account</v-icon>
                        <span class="font-weight-bold mr-2">{{ $t('invoices.advisor') }}</span> {{
                        viewSelectedSite?.Advisor }}
                        <v-divider vertical class="mx-4"></v-divider>
                        <v-icon start size="small">mdi-calendar</v-icon>
                        <span class="font-weight-bold mr-2">{{ $t('invoices.month_label') }}</span> {{
                            formatMonth(viewSelectedSite?.latest_invoice?.month) }}
                    </div>
                </v-card-subtitle>

                <v-card-text >
                    <!-- QR Code Display Section -->
                    <v-card class="mt-6"  >
                        <v-card-title class="bg-grey-lighten-4">
                            <v-icon start>mdi-qrcode</v-icon>
                            Detail Information
                        </v-card-title>
                        <v-card-text>
                            <v-row align="center">
                                <!-- QR Code Image -->
                                <v-col cols="12" md="12" >
                                    <div class="qr-details pa-4">
                                        <h4 class="mb-4 d-flex align-center">
                                            <v-icon color="primary" class="mr-2">mdi-information</v-icon>
                                            {{ $t('invoices.qr_code_info') }}
                                        </h4>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">{{ $t('invoices.site') }} : {{ viewSelectedSite?.Id_Site }}</v-col>

                                        </v-row>

                                        <v-divider class="my-2"></v-divider>

                                        <v-divider class="my-2"></v-divider>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Received Amount : ៛ {{ viewSelectedSite?.invoices[0]?.aba_amount }}</v-col>
                                        </v-row>

                                        <v-divider class="my-2"></v-divider>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Transaction Date : {{ viewSelectedSite?.invoices[0]?.aba_date }}</v-col>

                                        </v-row>

                                        <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Transaction ID : {{ viewSelectedSite?.invoices[0]?.aba_transaction_id }}</v-col>

                                        </v-row>
                                         <v-row dense class="mb-1">
                                            <v-col cols="6" class="font-weight-medium">Status : {{ viewSelectedSite?.invoices[0]?.aba_status_code }}</v-col>
                                        </v-row>
                                        <v-divider class="my-2"></v-divider>
                                        <!-- Download QR Code Button -->
                                        <!-- <div class="mt-6 text-center">
                                            <v-btn color="primary" variant="outlined" @click="downloadQRCode"
                                                :loading="downloadingQR">
                                                <v-icon start>mdi-download</v-icon>
                                                {{ $t('invoices.download_qr') }}
                                            </v-btn>
                                        </div> -->
                                    </div>
                                </v-col>
                                <!-- <v-col cols="12" md="6" class="text-center">
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
                                </v-col> -->

                                <!-- QR Code Details -->
                                <!-- QR Code Details - Simple Row & Column Layout -->

                            </v-row>
                        </v-card-text>
                    </v-card>

                    <!-- Message when no QR Code -->
                    <!-- <v-alert v-if="viewNormalInvoices.length > 0 && !hasQRCode" type="info" class="mt-6"
                        variant="tonal">
                        <v-icon start>mdi-qrcode-remove</v-icon>
                        {{ $t('invoices.no_qr_code') }}
                    </v-alert>


                    <v-alert v-if="viewNormalInvoices.length === 0 && viewSchoolInvoices.length === 0" type="info"
                        class="mt-4">
                        {{ $t('invoices.no_invoice_details') }}
                    </v-alert> -->
                </v-card-text>

                <v-card-actions>
                    <v-spacer />
                    <v-btn color="red" @click="viewInvoiceDialog = false">{{ $t('invoices.close') }}</v-btn>
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
                    <settleInvoice :invoiceSite="{ site: selectedItem, month: month }" @cancel-modal="dialog = false"
                        @close-dialog="dialog = false"></settleInvoice>
                </v-card>
            </v-dialog>
        </div>

        <!-- Deposit / Withdrawal Dialog -->
        <v-dialog v-model="depositAndWithdrawalDialog" max-width="460" persistent>
            <v-card rounded="xl" class="overflow-hidden" elevation="6">
                <!-- Gradient Header -->
                <div class="deposit-header pa-4 d-flex align-center justify-space-between">
                    <div class="d-flex align-center ga-3">
                        <v-avatar color="white" size="38">
                            <v-icon color="primary" size="22">mdi-bank-transfer</v-icon>
                        </v-avatar>
                        <div>
                            <div class="text-subtitle-1 font-weight-bold text-white">
                                {{ $t('invoices.deposit') }} / {{ $t('invoices.withdrawal') }}
                            </div>
                            <div class="text-caption text-white opacity-80">Manage site balance</div>
                        </div>
                    </div>
                    <v-btn icon size="small" variant="text" color="white" @click="depositAndWithdrawalDialog = false">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </div>

                <v-card-text class="pa-4">
                    <!-- Site Selector -->
                    <v-autocomplete
                        v-model="selectedSiteForBalance"
                        :items="siteOptions"
                        :label="$t('invoices.select_site')"
                        item-title="name"
                        item-value="id"
                        density="compact"
                        variant="outlined"
                        prepend-inner-icon="mdi-map-marker"
                        hide-details
                        autocomplete="off"
                        class="mb-4"
                    />

                    <!-- Loading -->
                    <div v-if="loadingBalance" class="d-flex align-center justify-center py-4 ga-2">
                        <v-progress-circular indeterminate size="20" width="2" color="primary" />
                        <span class="text-caption text-grey">{{ $t('invoices.loading') }}</span>
                    </div>

                    <template v-else-if="selectedSiteForBalance">
                        <!-- Balance Card -->
                        <v-card variant="tonal" color="success" rounded="lg" class="pa-3 mb-4">
                            <div class="d-flex align-center justify-space-between">
                                <div class="d-flex align-center ga-2">
                                    <v-icon color="success" size="20">mdi-cash-multiple</v-icon>
                                    <span class="text-body-2 font-weight-medium">{{ $t('invoices.total_balance') }}</span>
                                </div>
                                <span class="text-subtitle-1 font-weight-bold text-success">
                                    ៛ {{ formatNumber(siteBalance) }}
                                </span>
                            </div>
                        </v-card>

                        <!-- Transaction Fields -->
                        <v-row dense v-if="siteBalance >= 0">
                            <v-col cols="12" sm="6">
                                <v-select
                                    v-model="transactionType"
                                    :items="[
                                        { value: 'Deposit', title: $t('invoices.deposit') },
                                        { value: 'Withdrawal', title: $t('invoices.withdrawal') }
                                    ]"
                                    :label="$t('invoices.transaction_type')"
                                    variant="outlined"
                                    density="compact"
                                    hide-details
                                    item-title="title"
                                    item-value="value"
                                    autocomplete="off"
                                >
                                    <template #prepend-inner>
                                        <v-icon
                                            size="18"
                                            :color="transactionType === 'Deposit' ? 'success' : 'error'"
                                            class="mr-1"
                                        >
                                            {{ transactionType === 'Deposit' ? 'mdi-plus-circle' : 'mdi-minus-circle' }}
                                        </v-icon>
                                    </template>
                                </v-select>
                            </v-col>

                            <v-col cols="12" sm="6" v-if="transactionType">
                                <v-text-field
                                    v-model="formattedAmount"
                                    :label="$t('invoices.amount')"
                                    type="text"
                                    prefix="៛"
                                    placeholder="0"
                                    variant="outlined"
                                    density="compact"
                                    hide-details
                                    autocomplete="off"
                                    @input="formatAndValidateAmount"
                                />
                            </v-col>
                        </v-row>
                    </template>
                </v-card-text>

                <!-- Action Buttons -->
                <v-card-actions class="pa-4 pt-0" v-if="siteBalance >= 0">
                    <v-btn variant="text" class="text-none" @click="depositAndWithdrawalDialog = false">
                        Cancel
                    </v-btn>
                    <v-spacer />
                    <v-btn
                        :color="transactionType === 'Deposit' ? 'success' : 'warning'"
                        variant="flat"
                        rounded="lg"
                        class="text-none font-weight-bold px-5"
                        :prepend-icon="transactionType === 'Deposit' ? 'mdi-plus-circle' : 'mdi-minus-circle'"
                        :disabled="!formattedAmount || parseFloat(formattedAmount) <= 0"
                        @click="openConfirmDialog()"
                    >
                        {{ transactionType === 'Deposit' ? $t('invoices.confirm_deposit') : $t('invoices.confirm_withdrawal') }}
                    </v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>

        <!-- show geneerate QR -->
        <v-dialog v-model="cashierGenerateQRDialog" max-width="480" persistent>
            <v-card class="rounded-xl overflow-hidden" elevation="12">

                <!-- Gradient Header -->
                <div class="bg-gradient-header pa-5 d-flex align-center justify-space-between">
                    <div class="d-flex align-center gap-3">
                        <v-avatar color="white" size="42" class="elevation-2">
                            <v-icon color="primary" size="24">mdi-qrcode-scan</v-icon>
                        </v-avatar>
                        <div>
                            <div class="text-h6 font-weight-bold text-white">Generate QR</div>
                            <div class="text-caption text-white" style="opacity:0.8">Fill in details to generate QR code</div>
                        </div>
                    </div>
                    <v-btn icon size="small" variant="text" @click="cashierGenerateQRDialog = false" class="text-white">
                        <v-icon>mdi-close</v-icon>
                    </v-btn>
                </div>

                <v-card-text class="pa-5">
                    <v-row dense>
                        <!-- Site -->
                        <v-col cols="6">
                            <div class="text-caption text-medium-emphasis font-weight-medium mb-1">
                                <v-icon size="14" class="mr-1">mdi-map-marker-outline</v-icon>
                                {{ $t('invoices.select_site') }}
                            </div>
                            <v-autocomplete
                                v-model="selectedSiteForQR"
                                :items="siteOptions"
                                :label="$t('invoices.select_site')"
                                item-title="name"
                                item-value="id"
                                density="comfortable"
                                variant="outlined"
                                rounded="lg"
                                hide-details
                                autocomplete="off"
                            />
                        </v-col>

                        <!-- Process Type -->
                        <v-col cols="6" v-if="selectedSiteForQR">
                            <div class="text-caption text-medium-emphasis font-weight-medium mb-1">
                                <v-icon size="14" class="mr-1">mdi-cog-outline</v-icon>
                                Process Type
                            </div>
                            <v-autocomplete
                                v-model="processType"
                                :items="[
                                    { title: 'Partial Payment', value: 'PI' },
                                    { title: 'Invoice And Deposit', value: 'ID' },
                                    { title: 'Single Deposit', value: 'SD' },
                                ]"
                                item-title="title"
                                item-value="value"
                                label="Process Type"
                                density="comfortable"
                                variant="outlined"
                                rounded="lg"
                                hide-details
                                autocomplete="off"
                            />
                        </v-col>

                        <!-- Amount -->
                        <v-col cols="12" class="mt-3" v-if="processType">
                            <div class="text-caption text-medium-emphasis font-weight-medium mb-1">
                                <v-icon size="14" class="mr-1">mdi-currency-usd</v-icon>
                                {{ $t('invoices.amount') }}
                            </div>
                            <v-text-field
                                v-model="amountQR"
                                :label="$t('invoices.amount')"
                                type="text"
                                prefix="៛"
                                placeholder="0.00"
                                density="comfortable"
                                variant="outlined"
                                rounded="lg"
                                hide-details
                                class="text-h6 font-weight-bold"
                                color="success"
                                @input="formatAndQR"
                                autocomplete="off"
                            />
                        </v-col>
                    </v-row>
                </v-card-text>

                <v-divider />

                <!-- Actions -->
                <v-card-actions class="pa-4 gap-2">
                    <v-btn
                        variant="tonal"
                        color="grey"
                        rounded="lg"
                        @click="cashierGenerateQRDialog = false"
                        :disabled="sending"
                    >
                        Cancel
                    </v-btn>
                    <v-spacer />
                    <v-btn
                        variant="flat"
                        color="primary"
                        rounded="lg"
                        size="large"
                        class="font-weight-bold px-8"
                        :loading="sending"
                        :disabled="sending"
                        @click="generateQR()"
                    >
                        <v-icon start size="20">mdi-qrcode-plus</v-icon>
                        Generate QR
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
                    {{ $t('invoices.confirm_update_title') }}
                </v-card-title>

                <!-- Card content with better spacing -->
                <v-card-text class="pa-6">
                    <div class="d-flex align-start mb-4">
                        <v-icon color="info" class="mr-3 mt-1">mdi-help-circle-outline</v-icon>
                        <div>
                            <p class="text-body-1 mb-2">
                                {{ $t('invoices.confirm_update_message') }}
                            </p>
                        </div>
                    </div>
                </v-card-text>

                <!-- Buttons with blue styling -->
                <v-card-actions class="pa-4 bg-grey-lighten-4">
                    <v-spacer></v-spacer>

                    <!-- Cancel button -->
                    <v-btn @click="confirmDialog = false" variant="outlined" class="mr-3" size="small">
                        {{ $t('invoices.cancel') }}
                    </v-btn>

                    <!-- Confirm button with blue styling -->
                    <v-btn color="blue-darken-2" @click="saveTransaction" variant="elevated" size="small" class="px-6">
                        <v-icon left>mdi-check-circle-outline</v-icon>
                        {{ $t('invoices.confirm') }}
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
            <div style="width: 120px;">
                <p> ID: {{ selectedSite?.Id_Site || 'N/A' }}{{ selectedSite?.latest_invoice?.date || month || '' }}</p>
            </div> <!-- Empty div to balance the logo on the left -->
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
                    <td style="font-weight: bold; padding: 4px 8px; width: 50%;">ថ្ងៃទី :
                        {{ selectedSite?.latest_invoice?.date || month || '' }}</td>
                    <td style="font-weight: bold; padding: 4px 8px;">សហគ្រិន : {{
                        selectedSite?.Entrepreneur
                        }}</td>
                </tr>
                <tr>
                    <td style="font-weight: bold; padding: 4px 8px;">ផ្ញើរ : {{ selectedSite?.Id_Site || 'N/A' }}
                    </td>
                    <td style="font-weight: bold; padding: 4px 8px;">អ្នកប្រឹក្សាយោបល់ : {{
                        selectedSite?.Advisor
                        || 'N/A' }}</td>
                </tr>
                <tr>
                    <td v-if="selectedSite?.Platform === 'PP'" style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ : ភ្នំពេញ</td>
                    <td v-if="selectedSite?.Platform === 'KSP'"
                        style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ : កំពង់ស្ពឺ</td>
                    <td v-if="selectedSite?.Platform === 'BTB'"
                        style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ : បាត់ដំបង</td>
                    <td v-if="selectedSite?.Platform === 'KC'" style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ : កំពង់ចាម</td>
                    <td v-if="selectedSite?.Platform === 'SR'" style="font-weight: bold; padding: 4px 8px; width: 50%;">
                        តំបន់ : សៀមរាប</td>
                    <td v-if="selectedSite?.Platform === 'PP' || selectedSite?.Platform === 'KSP'"
                        style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ / Cashier : មន​ សោវី</td>
                    <td v-if="selectedSite?.Platform === 'BTB'" style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ
                        : នូ ចំរើន</td>
                    <td v-if="selectedSite?.Platform === 'KC'" style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ
                        : ហ៊ាង ប៉ោឡេង</td>
                    <td v-if="selectedSite?.Platform === 'SR'" style="font-weight: bold; padding: 4px 8px;">អ្នកគិតលុយ
                        : ហ៊ន ស្រីរត្ន័</td>
                </tr>
            </tbody>
        </table>
        <!-- SUMMARY section -->
        <div style="width: 800px; text-align: center; font-size: 18px; font-weight: bold; user-select: none;">
            <h4>សង្ខេប </h4>
        </div>
        <br>
        <p class="text-center py-3 amount-to-pay" v-if="(totalNormalInvoices - totalSchoolProgram) > 0">
            <strong>ចំនួនទឹកលុយបង់ : ៛ {{ formatNumber(totalNormalInvoices - totalSchoolProgram) }}</strong>
        </p>

        <p class="text-center py-3"
            style="font-size: 30px; font-weight: bold; letter-spacing: 0.5px; color: rebeccapurple" v-else>
            <strong>ចំនួននៅសល់ : ៛ {{ formatNumber(totalNormalInvoices - totalSchoolProgram) }}
                <br>
                លុយនៅសល់នឹងដាក់ចូលក្នុងគណនីយសន្សំ</strong></p>
        <br><br>
        <!-- INVOICES section -->
        <div style="width: 800px; text-align: center; font-size: 18px; font-weight: bold; user-select: none;">
            <h4>វិកយ័បត្រ </h4>
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
                        លេខវិកយ័បត្រ​ </th>
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        បរិយាយ </th>
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 14px; padding: 6px 8px;">
                        តម្លៃ </th>
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
                        <strong>សរុប</strong>
                    </td>
                    <td style="text-align: center;"><strong>៛ {{ formatNumberComma(totalNormalInvoices) }}</strong></td>
                </tr>
            </tbody>
        </table>
        <br><br>
        <!-- SCHOOL PROGRAM INVOICES section -->
        <div style="width: 800px; text-align: center; font-size: 18px; font-weight: bold; user-select: none;">
            <h4>ទឹកសាលា </h4>
        </div>
        <table border="1" cellspacing="0" cellpadding="5"
            style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <thead>
                <tr style="background-color: blue; color: white; font-size: 14px;">
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 16px; padding: 6px 8px;">
                        បរិយាយ </th>
                    <th
                        style="text-align: center; font-family: 'Khmer OS System', 'Battambang', Arial, sans-serif; font-size: 16px; padding: 6px 8px;">
                        តំលៃ </th>
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
        <br> <br>
        <p style="text-align: center;">
            <span style="color: green;">វិកយ័បត្រសរុប ( ៛ {{ formatNumberComma(totalNormalInvoices) }} )</span>
            <span style="color: blue;"> - ទឹកសាលា​ (៛ {{ formatNumberComma(schoolInvoices[0]?.beginning_balance) }}
                )</span>
            <span style="color: red;"> = ចំនួនត្រូបង់ ( ៛ {{ formatNumber(totalNormalInvoices - totalSchoolProgram) }}
                )</span>
        </p>
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
                    <img src="/img/pp.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
                </p>
                <p v-if="selectedSite?.Platform === 'BTB'" style="font-weight: bold; padding: 4px 8px;">រៀបចំដោយ : នូ
                    ចំរើន
                    <br>
                    <img src="/img/btb.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
                </p>
                <p v-if="selectedSite?.Platform === 'KC'" style="font-weight: bold; padding: 4px 8px;">រៀបចំដោយ : ហ៊ន
                    ស្រីរត្ន័ <br>
                    <img src="/img/kc.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
                </p>
                <p v-if="selectedSite?.Platform === 'SR'" style="font-weight: bold; padding: 4px 8px;">រៀបចំដោយ : ហ៊ាង
                    ប៉ោឡេង <br>
                    <img src="/img/sr.png" alt="Logo" style="height: 30px; display: block; margin: 4px auto 0;">
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
    props: {
        month: {
            type: String,
            default: ''
        },
        platform: {
            type: String,
            default: 'All'
        },
        searchQuery: {
            type: String,
            default: ''
        }
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
            invoiceDialog: false,
            viewInvoiceDialog: false,
            selectedSite: null,
            selectedSiteForBalance: null,
            viewSelectedSite: null,
            dialog: false,
            sending: false,
            selectedItem: '',
            depositAndWithdrawalDialog: false,
            cashierGenerateQRDialog: false,
            transactionType: '',
            amountQR: '',
            selectedSiteForQR: null,
            processType: '',
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
        month: {
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

            return this.selectedSite.invoices.filter(i => i.invoice_type !== 'school-program')
                .map(invoice => {
                    // Create a copy of the invoice to avoid mutating the original
                    const modifiedInvoice = { ...invoice };

                    // If invoice_type is EC or Stock, modify the month
                    if (invoice.invoice_type === 'Consumable Bottle' || invoice.invoice_type === 'Stock Invoice' || invoice.invoice_type === 'Technical Intervention'
                        || invoice.invoice_type === 'Water Quality Alert'
                    ) {
                        if (modifiedInvoice.month) {
                            modifiedInvoice.month = this.formatDateMinusOneMonth(modifiedInvoice.month);
                        }
                    }

                    return modifiedInvoice;
                });
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
            if (this.platform === 'All') {
                return this.groupedByPlatform
            }
            return {
                [this.platform]: this.groupedByPlatform[this.platform] || []
            }
        },
        platformFilterItems() {
            return ['All', ...Object.keys(this.groupedByPlatform)]
        },
        pendingSites() {
            return (sites) => {
                return sites.filter(site =>
                    site.latest_invoice?.status === 'pending'
                )
            }
        },
        sentSites() {
            return (sites) => {
                return sites.filter(site => {
                    const status = site.latest_invoice?.status || '';
                    return status.toLowerCase() == 'sending';
                });
            };
        },
        settleSites() {
            return (sites) => {
                return sites.filter(site => {
                    const status = site.latest_invoice?.status || '';
                    const invoiceType = site.latest_invoice?.invoice_type || '';
                    return invoiceType !== 'withdraw' && status.toLowerCase() == 'settle';
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
        downloadInvoice() {
            alert("Download Invoice functionality is in progress. Thank you for your patience!")
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
        formatAndQR() {
            let value = this.amountQR || '';
            value = value.toString();
            // Remove non-digit except dot
            let numeric = value.replace(/[^\d.]/g, '');
            let amount = parseFloat(numeric) || 0;

            // Format number with commas
            this.amountQR = new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(amount);
        },
        openConfirmDialog() {
            this.confirmDialog = true;
        },
        async generateQR() {
            if (!this.selectedSiteForQR) return;
            this.sending = true;

            let chatID = '7359315398';
            try {
                const month = this.selectedDate || (
                    this.selectedSite?.latest_invoice?.month
                        ? new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7)
                        : null
                );

                // 2. Get chat ID
                const response = await axios.get(`/api/getChatID/${this.selectedSiteForQR}`);
                if (response.data.success) {
                    chatID = response.data.data.chat_id;
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

                // 4. Convert to blob & send
                canvas.toBlob(async (blob) => {
                    const formData = new FormData();
                    formData.append('file', blob, `${this.selectedSiteForQR}_invoice.png`);
                    formData.append('chat_id', chatID);
                    formData.append('amount', this.amountQR.replace(/,/g, ''));
                    formData.append('site', this.selectedSiteForQR);
                    formData.append('process_type', this.processType);
                    formData.append('month', this.month);

                    await axios.post('/api/generateQRFromCashier', formData);

                    this.invoiceDialog = false;
                    this.cashierGenerateQRDialog = false;
                    this.sending = false;
                });

            } catch (err) {
                console.error(err);
                this.sending = false;
            }
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
                    month: this.month
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
        async cashierGenerateQR() {
            this.cashierGenerateQRDialog = true;
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
            const reqMonth = this.month ? this.month : null

            axios.get('/api/allInvoices', {
                params: {
                    month: reqMonth
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
            const monthStr = this.month || (this.selectedSite.latest_invoice?.month ?
                new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7) : null);
            axios.post('/api/invoices/update-status-by-site-month', {
                Id_Site: this.selectedSite.Id_Site,
                month: monthStr
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
                const monthStr = this.month || (this.selectedSite.latest_invoice?.month
                    ? new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7)
                    : null);

                await axios.post('/api/invoices/update-status-by-site-month', {
                    Id_Site: this.selectedSite.Id_Site,
                    month: monthStr
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
                doc.text(`Date: ${this.selectedSite.latest_invoice?.date || monthStr || ''}`, leftX, startY);
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
                const monthStr = this.month || (
                    this.selectedSite?.latest_invoice?.month
                        ? new Date(this.selectedSite.latest_invoice.month).toISOString().substr(0, 7)
                        : null
                );

                // 1. Update invoice status on server
                await axios.post('/api/invoices/update-status-by-site-month', {
                    Id_Site: this.selectedSite.Id_Site,
                    month: monthStr
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
                    month: this.month
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
                    formData.append('site', this.selectedSite.Id_Site);
                    formData.append('month', this.month);

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
.bg-gradient-header {
    background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
}

.deposit-header {
    background: linear-gradient(135deg, #1976D2 0%, #42A5F5 100%);
}

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
    color: #d32f2f !important;
    /* Darker red */
    border: 3px solid #d32f2f;
    padding: 15px;
    border-radius: 10px;
    background-color: #ffcdd2;
    /* Light red background */
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    /* Optional shadow for better visibility */
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

.v-chip:hover {
    background-color: #d9e9ff !important;
    border-color: #1a73e8;
    color: #1a3c7c !important;
    box-shadow: 0 4px 8px rgba(26, 115, 232, 0.3);
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
    border: 2px solid #2196f3 !important;
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
