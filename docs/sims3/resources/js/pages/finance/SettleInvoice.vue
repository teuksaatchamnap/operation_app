<template>
    <v-app>
        <v-main>
            <!-- Add this wrapper div with 80% width -->
            <div class="content-wrapper">
                <v-container class="pa-4">
                    <v-btn icon @click="$emit('cancel-modal')" class="mb-4">
                        <v-icon color="red">mdi-close</v-icon>
                    </v-btn>
                    <!-- Header -->
                    <v-row>
                        <!-- Left Panel: Site Display & Payment -->
                        <v-col cols="12" md="3">
                            <!-- Site Display Card -->
                            <v-card elevation="2" class="mb-6">
                                <v-card-title class="bg-primary">
                                    <span class="text-h6 text-white">{{ $t('settle_invoice.site') }}</span>
                                </v-card-title>
                                <v-card-text class="pa-4">
                                    <!-- Show Site as readonly text field -->
                                    <v-text-field :model-value="site" :label="$t('settle_invoice.site_name')"
                                        variant="outlined" readonly prepend-inner-icon="mdi-office-building"
                                        density="compact" />
                                    <!-- Site Summary -->
                                    <v-card v-if="siteInvoices.length" class="mt-4 pa-3" color="blue-lighten-5" flat>
                                        <div class="d-flex justify-space-between mb-1">
                                            <span class="font-weight-bold text-caption">{{
                                                $t('settle_invoice.total_invoices_amount') }}</span>
                                            <span class="font-weight-bold text-blue-darken-2 text-caption">៛
                                                {{ formatNumber(totalNormalRemaining ?? 0) }}</span>
                                        </div>
                                        <div class="d-flex justify-space-between mb-1">
                                            <span class="font-weight-bold text-caption">{{
                                                $t('settle_invoice.amount_school_program') }}</span>
                                            <span class="font-weight-bold text-green-darken-2 text-caption">៛ {{
                                                formatNumber(totalSchoolAmount ?? 0) }}</span>
                                        </div>
                                        <v-divider class="my-1"></v-divider>
                                        <div class="d-flex justify-space-between">
                                            <span class="font-weight-bold text-caption">{{
                                                $t('settle_invoice.total_to_collect') }}</span>
                                            <span class="font-weight-bold text-caption" :class="netAmountClass">៛ {{
                                                formatNumber(netAmount??0) }}</span>
                                        </div>
                                        <div v-if="netAmount < 0" class="text-caption text-red mt-1">
                                            {{ $t('settle_invoice.need_to_pay_entrepreneur') }}
                                        </div>
                                        <div v-else-if="netAmount > 0" class="text-caption text-blue-darken-2 mt-1">
                                            {{ $t('settle_invoice.entrepreneur_needs_to_pay') }}
                                        </div>
                                    </v-card>
                                </v-card-text>
                            </v-card>

                            <!-- Payment Input -->
                            <v-card elevation="2" v-if="siteInvoices.length">
                                <v-card-title class="bg-primary">
                                    <span class="text-h6 text-white">{{ $t('settle_invoice.enter_payment') }}</span>
                                </v-card-title>
                                <v-card-text class="pa-4">
                                    <v-text-field v-model="paymentInput" :label="$t('settle_invoice.amount_received')"
                                        type="text" variant="outlined" :readonly="netAmount < 0"
                                        prepend-inner-icon="mdi-currency-reil"
                                        :hint="`Remain: ៛${formatNumber(Math.max(netAmount, 0))}`" persistent-hint
                                        @update:model-value="handlePaymentInput" @blur="formatPaymentInput"
                                        density="compact" autocomplete="off">
                                        <template v-slot:append>
                                            <v-btn @click="payAll" size="small" variant="tonal" color="primary"
                                                class="text-caption">
                                                {{ $t('settle_invoice.pay_all') }}
                                            </v-btn>
                                        </template>
                                    </v-text-field>
                                    <v-text-field v-model="paymentDate" label="Payment Date" type="date"
                                        variant="outlined" prepend-inner-icon="mdi-note-text" density="compact"
                                        autocomplete="off" class="mt-3" />
                                    <v-text-field v-model="transactionID" label="Transaction ID" type="text"
                                        variant="outlined" prepend-inner-icon="mdi-note-text" density="compact"
                                        autocomplete="off" class="mt-3" />
                                    <!-- Action Buttons -->
                                    <v-row class="mt-3" dense>
                                        <v-col cols="6">
                                            <v-btn @click="resetPayment" color="red" block
                                                size="small">
                                                {{ $t('settle_invoice.clear') }}
                                            </v-btn>
                                        </v-col>
                                        <v-col cols="6">
                                            <v-btn @click="processPayment" :disabled="!canProcessPayment"
                                                color="primary" block size="small">
                                                {{ $t('settle_invoice.process') }}
                                            </v-btn>
                                        </v-col>
                                    </v-row>
                                </v-card-text>
                            </v-card>
                            <!-- display withdrawal amount -->
                            <v-card class="mt-4" v-if="isBalanceShown">
                                <v-card-title class="bg-primary">
                                    <span class="text-h6 text-white">{{ $t('settle_invoice.withdraw_saving') }}</span>
                                </v-card-title>
                                <v-card-text class="pa-4">
                                    <div class="d-flex align-center">
                                        <div>
                                            <div class="text-body-1">{{ $t('settle_invoice.withdraw_saving_label') }}
                                                <span class="text-h6 font-weight-bold primary--text">៛
                                                    {{
                                                        formatNumber(autoWithdrawalAmount) }}</span></div>
                                        </div>
                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-col>
                        <v-col cols="12" md="3">
                            <v-card elevation="2" class="h-100">
                                <!-- show site balance  -->
                                <v-card elevation="2" class="mb-6">
                                    <v-card-title class="bg-secondary d-flex justify-space-between align-center py-2">
                                        <span class="text-h6 text-white">{{ $t('settle_invoice.site_balance') }}</span>
                                    </v-card-title>
                                    <v-card-text class="pa-4">
                                        <!-- Site Summary -->
                                        <v-card v-if="siteInvoices.length" class="mt-4 pa-3" color="blue-lighten-5"
                                            flat>
                                            <div class="d-flex justify-space-between mb-1">
                                                <span class="font-weight-bold text-caption">{{
                                                    $t('settle_invoice.balance') }}</span>
                                                <span class="font-weight-bold text-green-darken-2 text-caption">៛
                                                    {{ formatNumber(Math.floor(balance ?? 0))
                                                    }}</span>
                                            </div>
                                            <v-divider class="my-1"></v-divider>
                                            <div class="d-flex justify-space-between mb-1">
                                                <span class="font-weight-bold text-caption">{{
                                                    $t('settle_invoice.sale_income') }}</span>
                                                <span class="font-weight-bold text-blue-darken-2 text-caption">៛ {{
                                                    formatNumber(saleIncome ??
                                                    0)
                                                    }}</span>
                                            </div>
                                            <div class="d-flex justify-space-between">
                                                <span class="font-weight-bold text-caption">{{
                                                    $t('settle_invoice.total_expense') }}</span>
                                                <span class="font-weight-bold text-caption" style="color: red;">៛ {{
                                                    formatNumber(expenseTotal
                                                    ?? 0)
                                                    }}</span>
                                            </div>
                                            <v-divider class="my-1"></v-divider>
                                            <div class="d-flex justify-space-between">
                                                <span class="font-weight-bold text-caption">{{
                                                    $t('settle_invoice.income_remain') }}</span>
                                                <span class="font-weight-bold text-caption" :class="netAmountClass">៛ {{
                                                    formatNumber((saleIncome ?? 0) -
                                                    (expenseTotal ?? 0)) }}</span>
                                            </div>
                                            <v-divider class="my-1"></v-divider>
                                            <div class="d-flex justify-space-between">
                                                <span class="font-weight-bold text-caption">{{
                                                    $t('settle_invoice.income_sal_profit') }}</span>
                                                <span class="font-weight-bold text-caption" :class="netAmountClass">
                                                    ៛ {{ formatNumber((expensesByCategory.salary_entrepreneur ?? 0) +
                                                        ((saleIncome ?? 0) -
                                                    (expenseTotal ??
                                                    0))) }}</span>
                                            </div>
                                        </v-card>
                                    </v-card-text>
                                </v-card>
                                <v-card-title class="bg-green d-flex justify-space-between align-center py-2">
                                    <span class="text-h6 text-white">{{ $t('settle_invoice.upload_transaction')
                                        }}</span>
                                </v-card-title>
                                <!-- File Upload Fields -->
                                <v-row class="mt-3">
                                    <v-col cols="12" md="12">
                                        <div class="upload-container">
                                            <v-file-input v-model="qrFile" :multiple="false"
                                                :label="$t('settle_invoice.upload_qr_code')" accept="image/*,application/pdf,application/zip,application/x-zip-compressed"
                                                prepend-icon="mdi-qrcode" density="compact" clearable
                                                @change="handleFileChange('qr', $event)" color="primary"
                                                variant="outlined" class="upload-input" hide-details>
                                                <template v-slot:prepend>
                                                    <div class="upload-icon">
                                                        <v-icon color="primary"
                                                            size="32">mdi-cloud-upload-outline</v-icon>
                                                    </div>
                                                </template>

                                                <template v-slot:selection="{ fileNames }">
                                                    <v-chip v-if="fileNames.length" size="small" class="me-2"
                                                        color="primary" text-color="white" closable>
                                                        {{ fileNames[0] }}
                                                    </v-chip>
                                                </template>
                                            </v-file-input>

                                        </div>
                                    </v-col>
                                </v-row>

                                <!-- File Preview (Optional) -->
                                <v-row v-if="qrPreview || receiptPreview" class="mt-2">
                                    <v-col cols="12" md="12" v-if="qrPreview" class="d-flex justify-center">
                                        <div>
                                            <div class="text-caption text-grey mb-1">{{ $t('settle_invoice.qr_preview')
                                                }}</div>
                                            <img :src="qrPreview" alt="QR Code Preview" class="file-preview" />
                                        </div>
                                    </v-col>
                                </v-row>
                            </v-card>
                        </v-col>

                        <!-- Right Panel: Invoices Table -->
                        <v-col cols="12" md="6">
                            <v-card elevation="2" class="h-100">
                                <v-card-title class="bg-grey d-flex justify-space-between align-center py-2">
                                    <span class="text-h6 text-white">{{ $t('settle_invoice.site_invoices') }}</span>
                                </v-card-title>

                                <v-card-text class="pa-0">
                                    <!-- Loading State -->
                                    <div v-if="loading" class="text-center py-8">
                                        <v-progress-circular indeterminate color="primary" size="48" />
                                    </div>

                                    <!-- Empty State -->
                                    <div v-else-if="!siteInvoices.length" class="text-center py-8">
                                        <v-icon size="48" color="grey-lighten-2"
                                            class="mb-2">mdi-file-document-outline</v-icon>
                                        <p class="text-grey text-caption">{{ $t('settle_invoice.no_invoices_found') }}
                                        </p>
                                    </div>

                                    <!-- Custom Table -->
                                    <div v-else class="custom-table-container">
                                        <!-- ============================= -->
                                        <!-- NORMAL INVOICES (THEY PAY YOU) -->
                                        <!-- ============================= -->
                                        <h4 class="pa-3 text-primary">{{ $t('settle_invoice.invoices_amount_to_collect')
                                            }}</h4>

                                        <!-- Table Header -->
                                        <div class="table-header">
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.site') }}</div>
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.invoice_type') }}
                                            </div>
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.amount_pay') }}
                                            </div>
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.amount_receive')
                                                }}</div>
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.status') }}</div>
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.remaining') }}
                                            </div>
                                        </div>

                                        <!-- Table Body -->
                                        <div v-for="invoice in displayNormalInvoices" :key="invoice.id"
                                            class="table-row">
                                            <div class="table-cell">
                                                <v-chip size="small" color="primary" class="text-caption">{{
                                                    invoice.id_site }}</v-chip>
                                            </div>
                                            <div class="table-cell text-caption">{{ invoice.invoice_type }}</div>
                                            <div class="table-cell text-left">
                                                <strong class="text-caption">៛ {{ formatNumber(invoice.amount_pay)
                                                    }}</strong>
                                            </div>
                                            <div class="table-cell text-left text-caption"
                                                :class="getAmountReceiveClass(invoice)">
                                                ៛ {{ formatNumber(invoice.displayAmountReceive) }}
                                            </div>
                                            <div class="table-cell">
                                                <v-chip :color="getStatusColor(invoice)" size="small"
                                                    class="status-chip text-caption">
                                                    {{ invoice.displayStatus }}
                                                </v-chip>
                                            </div>
                                            <div class="table-cell text-left text-caption"
                                                :class="getRemainingClass(invoice)">
                                                ៛ {{ formatNumber(invoice.displayRemaining) }}
                                            </div>
                                        </div>

                                        <!-- Normal Total -->
                                        <div class="pa-3 text-right bg-blue-lighten-5">
                                            <strong class="text-body-2">{{ $t('settle_invoice.total_remaining')
                                                }}</strong>
                                            <span class="text-blue-darken-2 text-body-2 ml-2">៛ {{
                                                formatNumber(totalNormalRemaining ?? 0)
                                                }}</span>
                                        </div>

                                        <!-- ============================= -->
                                        <!-- SCHOOL PROGRAM (YOU PAY THEM) -->
                                        <!-- ============================= -->
                                        <h4 class="pa-3 mt-4 text-green-darken-2">{{
                                            $t('settle_invoice.school_program_amount_to_pay') }}</h4>

                                        <!-- Table Header -->
                                        <div class="table-header">
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.site') }}</div>
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.invoice_type') }}
                                            </div>
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.pay_ent') }}
                                            </div>
                                        </div>

                                        <!-- Table Body -->
                                        <div v-for="invoice in displaySchoolInvoices" :key="invoice.id"
                                            class="table-row">
                                            <div class="table-cell">
                                                <v-chip size="small" color="green" class="text-caption">{{
                                                    invoice.id_site }}</v-chip>
                                            </div>
                                            <div class="table-cell text-caption">{{ invoice.invoice_type }}</div>
                                            <div class="table-cell text-left">
                                                <strong class="text-caption">៛ {{ formatNumber(invoice.amount_pay)
                                                    }}</strong>
                                            </div>
                                        </div>
                                        <!-- show invoice_records -->
                                        <h4 class="pa-3 mt-4 text-yellow-darken-2">Invoice Records</h4>

                                        <!-- Table Header -->
                                        <div class="table-header">
                                            <div class="table-cell text-caption">{{ $t('settle_invoice.site') }}</div>
                                            <div class="table-cell text-caption">Tran_ID</div>
                                            <div class="table-cell text-caption">Amount</div>
                                            <div class="table-cell text-caption">Status</div>
                                        </div>

                                        <!-- Table Body -->
                                        <div v-for="invoice in invoiceRecord" :key="invoice.id" class="table-row">
                                            <div class="table-cell">
                                                <v-chip size="small" color="green" class="text-caption">{{ invoice.site
                                                    }}</v-chip>
                                            </div>
                                            <div class="table-cell text-caption">{{ invoice.transaction_id }}</div>
                                            <div class="table-cell text-caption">{{ invoice.amount }}</div>
                                            <div class="table-cell text-caption">{{ invoice.payment_status }}</div>

                                        </div>

                                    </div>
                                </v-card-text>
                            </v-card>
                        </v-col>
                    </v-row>

                    <!-- Snackbar -->
                    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="snackbar.timeout"
                        location="top right">
                        {{ snackbar.message }}
                    </v-snackbar>
                    <v-dialog v-model="confirmDialog" max-width="450" persistent>
                        <v-card class="elevation-6 rounded-lg">
                            <v-card-title class="primary white--text d-flex align-center">
                                <v-icon left color="white">mdi-check-circle</v-icon>
                                <span class="text-h6 font-weight-medium text-center primary--text"
                                    style="width: 100%; display: block;">{{
                                        $t('settle_invoice.confirm_payment') }}</span>

                            </v-card-title>

                            <v-card-text class="pt-4">
                                <!-- Payment Summary Table -->
                                <div class="mb-4">
                                    <!-- Table Header -->
                                    <div class="d-flex justify-space-between mb-2">
                                        <div class="text-body-2 font-weight-bold blue--text">{{
                                            $t('settle_invoice.description') }}</div>
                                        <div class="text-body-2 font-weight-bold grey--text text--darken-2">{{
                                            $t('settle_invoice.amount')
                                            }}</div>
                                    </div>

                                    <!-- Table Rows -->
                                    <div class="mb-3">
                                        <!-- Cash Received -->
                                        <div class="d-flex justify-space-between py-2 border-bottom">
                                            <div class="d-flex align-center">
                                                <v-icon x-small left color="success">mdi-hand-coin</v-icon>
                                                <span class="text-body-2">{{ $t('settle_invoice.cash_received')
                                                    }}</span>
                                            </div>
                                            <div class="text-body-2 font-weight-bold">៛ {{ formatNumber(paymentAmount -
                                                autoWithdrawalAmount)
                                                }}</div>
                                        </div>

                                        <!-- Withdrawal from Balance (only if applicable) -->
                                        <div v-if="autoWithdrawalAmount > 0"
                                            class="d-flex justify-space-between py-2 border-bottom">
                                            <div class="d-flex align-center">
                                                <v-icon x-small left color="blue">mdi-bank-transfer</v-icon>
                                                <span class="text-body-2">{{
                                                    $t('settle_invoice.withdrawal_from_balance') }}</span>
                                            </div>
                                            <div class="text-body-2 font-weight-bold blue--text">៛ {{
                                                formatNumber(autoWithdrawalAmount) }}
                                            </div>
                                        </div>

                                        <!-- School Program -->
                                        <!-- <div class="d-flex justify-space-between py-2 border-bottom">
                      <div class="d-flex align-center">
                        <v-icon x-small left color="orange">mdi-school</v-icon>
                        <span class="text-body-2">School Program to Pay</span>
                      </div>
                      <div class="text-body-2 font-weight-bold">៛ {{ formatNumber(totalSchoolAmount) }}</div>
                    </div> -->

                                        <!-- Total Collected -->
                                        <div class="d-flex justify-space-between py-2 border-bottom">
                                            <div class="d-flex align-center">
                                                <v-icon x-small left color="green">mdi-cash-multiple</v-icon>
                                                <span class="text-body-2">{{
                                                    $t('settle_invoice.total_remaining_summary') }}</span>
                                            </div>
                                            <div class="text-body-2 font-weight-bold green--text">៛ {{
                                                formatNumber(totalNormalRemaining) }}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Confirmation Message -->
                                <div class="text-center mt-4 pa-3 grey lighten-4 rounded-lg">
                                    <v-icon color="grey" class="mb-2">mdi-help-circle</v-icon>
                                    <div class="text-body-2 font-weight-medium">{{
                                        $t('settle_invoice.are_you_sure_process') }}</div>
                                </div>
                            </v-card-text>

                            <v-card-actions class="pa-4 pt-2">
                                <v-btn text @click="confirmDialog = false" class="text-capitalize rounded-lg"
                                    color="grey" width="120" elevation="2">
                                    <v-icon left small>mdi-close</v-icon>
                                    {{ $t('settle_invoice.cancel') }}
                                </v-btn>
                                <v-spacer></v-spacer>
                                <v-btn color="success" @click="confirmAndProcess"
                                    class="text-capitalize rounded-lg font-weight-bold" size="large" elevation="2">
                                    <v-icon left small>mdi-check-circle</v-icon>
                                    {{ $t('settle_invoice.confirm_payment_button') }}
                                </v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>

                    <!-- box to withdraw from balance -->
                    <v-dialog v-model="wathdrawalBalance" max-width="420" persistent>
                        <v-card class="elevation-6 rounded-lg">
                            <!-- Header with icon -->
                            <v-card-title class="primary white--text d-flex align-center">
                                <v-icon left color="white">mdi-bank-transfer-out</v-icon>
                                <span class="text-h6 font-weight-medium text-center green white--text">{{
                                    $t('settle_invoice.withdraw_saving_info') }}</span>
                            </v-card-title>

                            <!-- Balance Summary Section -->
                            <v-card-text class="pt-4 pb-0">
                                <div class="text-subtitle-1 font-weight-medium primary--text mb-3">
                                    <v-icon small left color="primary">mdi-chart-box</v-icon>
                                    {{ $t('settle_invoice.balance_summary') }}
                                </div>

                                <v-divider class="mb-4"></v-divider>

                                <!-- Balance Cards -->
                                <v-row dense class="mb-4">
                                    <v-col cols="12">
                                        <v-card outlined class="rounded-lg pa-3"
                                            :class="netAmount > 0 ? 'green lighten-5' : 'grey lighten-4'">
                                            <div class="d-flex align-center">
                                                <v-icon left color="green" class="mr-2">mdi-cash-multiple</v-icon>
                                                <div class="text-body-2 text-grey-darken-3">{{
                                                    $t('settle_invoice.total_payment') }}</div>
                                                <v-spacer></v-spacer>
                                                <div class="text-h6 font-weight-bold green--text">៛ {{
                                                    formatNumber(netAmount) }}</div>
                                            </div>
                                        </v-card>
                                    </v-col>
                                </v-row>

                                <!-- Detailed Balance Breakdown -->
                                <div class="pl-2">
                                    <div class="d-flex align-center justify-space-between mb-3">
                                        <div class="d-flex align-center">
                                            <v-icon small left color="blue" class="mr-1">mdi-bank</v-icon>
                                            <span class="text-body-2">{{ $t('settle_invoice.saving') }}</span>
                                        </div>
                                        <div class="text-body-1 font-weight-bold">៛ {{ formatNumber(Math.floor(balance))
                                            }}</div>
                                    </div>

                                    <div class="d-flex align-center justify-space-between mb-3">
                                        <div class="d-flex align-center">
                                            <v-icon small left color="success" class="mr-1">mdi-hand-coin</v-icon>
                                            <span class="text-body-2">{{ $t('settle_invoice.cash_received_summary')
                                                }}</span>
                                        </div>
                                        <div class="text-body-1 font-weight-bold success--text">៛ {{
                                            formatNumber(reserveAmount) }}</div>
                                    </div>
                                </div>

                                <!-- Automatic Withdrawal Calculation -->
                                <v-divider class="my-4"></v-divider>

                                <!-- Auto-calculated amount -->
                                <div class="text-center mb-3">
                                    <div class="text-subtitle-2 font-weight-medium mb-1">{{
                                        $t('settle_invoice.auto_calculated_withdrawal')
                                        }}</div>
                                    <div class="text-h5 font-weight-bold primary--text">
                                        ៛ {{ formatNumber(autoWithdrawalAmount) }}
                                    </div>
                                    <div class="text-caption text-grey mt-1">
                                        <v-icon x-small left :color="statusColor">{{ statusIcon }}</v-icon>
                                        {{ statusMessage }}
                                    </div>
                                </div>
                                <!-- Display in input field (read-only) -->
                                <div class="text-subtitle-2 font-weight-medium mb-2">{{
                                    $t('settle_invoice.amount_to_withdraw') }}</div>
                                <v-text-field :value="autoWithdrawalAmount" outlined dense readonly prefix="៛"
                                    hide-details class="rounded-lg"
                                    :class="autoWithdrawalAmount > 0 ? 'green lighten-5' : 'grey lighten-3'">
                                </v-text-field>
                                <v-divider class="my-4"></v-divider>
                                <div class="text-center">
                                    <v-btn icon small @click="closeWithdrawalDialog" color="green white--text">
                                        {{ $t('settle_invoice.ok') }}
                                    </v-btn>
                                </div>
                            </v-card-text>
                        </v-card>
                    </v-dialog>

                    <v-dialog v-model="savingFromSchool" max-width="500">
                        <v-card class="elevation-6 rounded-lg">
                            <!-- Title -->
                            <v-card-title class="primary white--text d-flex align-center">
                                <v-icon left color="blue">mdi-school</v-icon> <v-spacer></v-spacer>
                                <span class="text-h6 font-weight-medium">{{
                                    $t('settle_invoice.remaining_amount_from_school') }}</span>
                                <v-spacer></v-spacer>
                                <!-- <v-btn icon small @click="savingFromSchool = false" class="white--text">
                  <v-icon>mdi-close</v-icon>
                </v-btn> -->
                            </v-card-title>

                            <!-- Body content with amount display -->
                            <v-card-text class="pa-6 text-center">
                                <div class="mb-4">
                                    <!-- <v-icon color="black" size="64" class="mb-4">mdi-currency-usd</v-icon> -->
                                    <div class="d-flex justify-center align-center">
                                        <span class="text-h3 font-weight-bold primary--text">
                                            ៛ {{ formatNumber(netAmount * -1) }}
                                        </span>
                                    </div>
                                    <p class="text-body-1 text-green mt-2">
                                        {{ $t('settle_invoice.this_full_amount_will_be_saved') }}
                                    </p>
                                </div>
                            </v-card-text>
                            <!-- Centered Save button with full border -->
                            <v-card-actions class="pa-4 pb-6">
                                <v-spacer></v-spacer>
                                <v-btn color="blue" @click="closeSavingFromSchoolDialog()"
                                    class="text-capitalize rounded-lg font-weight-bold" size="large" elevation="2"
                                    variant="elevated" style="border: 2px solid; min-width: 100px;">
                                    <v-icon left>mdi-check-circle</v-icon>
                                    {{ $t('settle_invoice.ok') }}
                                </v-btn>
                                <v-spacer></v-spacer>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>

                    <!-- show cash receipt upload and preview -->
                    <v-dialog v-model="cashReceipt" max-width="500px">
                        <v-card class="elevation-6 rounded-lg">
                            <v-card-title class="primary white--text d-flex align-center">
                                <v-icon left color="white">mdi-school</v-icon>
                                <span class="text-h6 font-weight-medium">{{ $t('settle_invoice.preview_cash_receipt')
                                    }}</span>
                                <v-spacer></v-spacer>
                                <v-btn icon small @click="cashReceipt = false" class="white--text">
                                    <v-icon>mdi-close</v-icon>
                                </v-btn>
                            </v-card-title>
                            <v-card-actions class="pa-4 pt-2">
                                <v-spacer></v-spacer>
                                <v-btn color="success" @click="cashReceipt = false"
                                    class="text-capitalize rounded-lg font-weight-bold" size="large" elevation="2">
                                    <v-icon left small>mdi-check-circle</v-icon>
                                    {{ $t('invoices.close') }}
                                </v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>

                    <v-dialog v-model="savingFromSchool" max-width="500">
                        <v-card class="elevation-6 rounded-lg">
                            <!-- Title -->
                            <v-card-title class="primary white--text d-flex align-center">
                                <v-icon left color="blue">mdi-school</v-icon> <v-spacer></v-spacer>
                                <span class="text-h6 font-weight-medium">Remaining Amount From School Program</span>
                                <v-spacer></v-spacer>
                                <!-- <v-btn icon small @click="savingFromSchool = false" class="white--text">
                  <v-icon>mdi-close</v-icon>
                </v-btn> -->
                            </v-card-title>

                            <!-- Body content with amount display -->
                            <v-card-text class="pa-6 text-center">
                                <div class="mb-4">
                                    <!-- <v-icon color="black" size="64" class="mb-4">mdi-currency-usd</v-icon> -->
                                    <div class="d-flex justify-center align-center">
                                        <span class="text-h3 font-weight-bold primary--text">
                                            ៛ {{ formatNumber(netAmount * -1) }}
                                        </span>
                                    </div>
                                    <p class="text-body-1 text-green mt-2">
                                        This full amount will be put as saving for the entrepreneur
                                    </p>
                                </div>
                            </v-card-text>
                            <!-- Centered Save button with full border -->
                            <v-card-actions class="pa-4 pb-6">
                                <v-spacer></v-spacer>
                                <v-btn color="blue" @click="closeSavingFromSchoolDialog()"
                                    class="text-capitalize rounded-lg font-weight-bold" size="large" elevation="2"
                                    variant="elevated" style="border: 2px solid; min-width: 100px;">
                                    <v-icon left>mdi-check-circle</v-icon>
                                    OK
                                </v-btn>
                                <v-spacer></v-spacer>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>

                    <!-- show cash receipt upload and preview -->
                    <v-dialog v-model="cashReceipt" max-width="500px">
                        <v-card class="elevation-6 rounded-lg">
                            <v-card-title class="primary white--text d-flex align-center">
                                <v-icon left color="white">mdi-school</v-icon>
                                <span class="text-h6 font-weight-medium">Preview Cash Receipt</span>
                                <v-spacer></v-spacer>
                                <v-btn icon small @click="cashReceipt = false" class="white--text">
                                    <v-icon>mdi-close</v-icon>
                                </v-btn>
                            </v-card-title>
                            <v-card-actions class="pa-4 pt-2">
                                <v-spacer></v-spacer>
                                <v-btn color="success" @click="cashReceipt = false"
                                    class="text-capitalize rounded-lg font-weight-bold" size="large" elevation="2">
                                    <v-icon left small>mdi-check-circle</v-icon>
                                    Close
                                </v-btn>
                            </v-card-actions>
                        </v-card>
                    </v-dialog>

                </v-container>
            </div>
        </v-main>
    </v-app>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
// import { useRouter } from 'vue-router'
import { useRoute, useRouter } from "vue-router";
import { useI18n } from 'vue-i18n'
import { tr } from 'vuetify/locale';
//const router = useRouter()
const router = useRouter();
const { t } = useI18n()
const backToFinance = () => {
    router.push('/importInvoice')
    console.log('Navigating to /settleInvoice')

}
const props = defineProps({
    invoiceSite: {
        type: Object,
        required: true
    }
})

const cashReceipt = ref(false)
const paymentInput = ref('') // This stores the display value
const rawPaymentValue = ref(0) // This stores the actual number value
const loading = ref(false)
const invoices = ref([])
const confirmDialog = ref(false)
const qrFile = ref(null)
const expensesByCategory = ref({})
const qrPreview = ref('')
const receiptPreview = ref('')
const wathdrawalBalance = ref(false)
const emit = defineEmits(['close-dialog'])
const site = props.invoiceSite.site
const month = props.invoiceSite.month
const reserveAmount = ref(0) // This tracks the CASH amount entered by user
const isBalanceShown = ref(false)
const hasShownWithdrawal = ref(false)
const savingFromSchool = ref(false)
const invoiceRecord = ref([])
const paymentDate = ref(new Date().toISOString().slice(0, 10)) // default to today
const transactionID = ref('') // New field for Transaction ID
const snackbar = ref({
    show: false,
    message: '',
    color: 'success',
    timeout: 5000
})

// Format number with commas
const formatNumber = (num) => {
    if (num === null || num === undefined || isNaN(num)) return '0'
    const numStr = num.toString()
    return numStr.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

const handleFileChange = (type, event) => {
    const file = event.target.files[0]
    if (!file) return

    if (type === 'qr') {
        qrFile.value = file
        // Create preview for image files
        if (file.type.startsWith('image/')) {
            const reader = new FileReader()
            reader.onload = (e) => {
                qrPreview.value = e.target.result
            }
            reader.readAsDataURL(file)
        }
    }
}

// Calculate auto withdrawal amount based on CASH entered (reserveAmount)
const autoWithdrawalAmount = computed(() => {
    const shortage = netAmount.value - reserveAmount.value

    if (shortage <= 0) {
        return 0 // Cash already covers everything
    }

    // Use balance to cover shortage, but not more than available balance
    return Math.min(balance.value, shortage)
})

// Watch for when withdrawal dialog opens to add auto withdrawal amount
watch(wathdrawalBalance, (newValue) => {
    if (newValue) {
        // When withdrawal dialog opens, add auto withdrawal amount to payment
        addAutoWithdrawalToPayment()
    }
})

// Function to add auto withdrawal amount to payment
const addAutoWithdrawalToPayment = () => {
    if (autoWithdrawalAmount.value > 0) {
        // Add the shortage amount to paymentInput
        const currentPayment = rawPaymentValue.value
        const newPayment = currentPayment + autoWithdrawalAmount.value

        rawPaymentValue.value = newPayment
        paymentInput.value = formatNumber(newPayment)

        // Note: reserveAmount stays as the original cash amount
        // Recalculate allocation with the new total
        calculateAllocation()
    }
}

const totalPaid = computed(() => {
    return Math.min(netAmount.value, reserveAmount.value + autoWithdrawalAmount.value)
})

const statusMessage = computed(() => {
    if (autoWithdrawalAmount.value <= 0) {
        return t('settle_invoice.cash_covers_full_amount')
    }
    if (autoWithdrawalAmount.value < (netAmount.value - reserveAmount.value)) {
        return t('settle_invoice.insufficient_balance')
    }
    return t('settle_invoice.full_amount_using_balance')
})

// Status color
const statusColor = computed(() => {
    if (autoWithdrawalAmount.value <= 0) return 'success'
    if (autoWithdrawalAmount.value < (netAmount.value - reserveAmount.value)) return 'warning'
    return 'success'
})

const closeSavingFromSchoolDialog = () => {
    savingFromSchool.value = false
    confirmDialog.value = true
}

// Status icon
const statusIcon = computed(() => {
    if (autoWithdrawalAmount.value <= 0) return 'mdi-check-circle'
    if (autoWithdrawalAmount.value < (netAmount.value - reserveAmount.value)) return 'mdi-alert-circle'
    return 'mdi-check-circle'
})

// Check if file is an image
const isImage = (file) => {
    return file && file.type && file.type.startsWith('image/')
}

// Convert file to base64
const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => resolve(reader.result)
        reader.onerror = error => reject(error)
    })
}

// Parse formatted string back to number
const parseFormattedNumber = (str) => {
    if (!str && str !== 0) return 0
    // Convert to string first to ensure we have a string
    const strValue = String(str)
    // Remove all commas and non-digit characters
    const cleanStr = strValue.replace(/[^0-9]/g, '')
    const result = parseFloat(cleanStr) || 0
    return result
}

// Handle payment input - allow typing without formatting
const handlePaymentInput = (value) => {
    paymentInput.value = value
    const parsedValue = parseFormattedNumber(value)
    rawPaymentValue.value = parsedValue
    // IMPORTANT: Set reserveAmount to the cash amount entered
    reserveAmount.value = parsedValue
    calculateAllocation()
}

// Format payment input when user leaves the field
const formatPaymentInput = () => {
    if (paymentInput.value !== '' && paymentInput.value !== null && paymentInput.value !== undefined) {
        const parsed = parseFormattedNumber(paymentInput.value)
        if (parsed >= 0) {
            paymentInput.value = formatNumber(parsed)
        } else {
            paymentInput.value = ''
        }
    }
}

// Filter invoices for this fixed site
const siteInvoices = computed(() => {
    return invoices.value.filter(inv => inv.id_site === site)
})

// Filter normal invoices (non-school program) - THEY PAY YOU
const normalInvoices = computed(() => {
    return siteInvoices.value.filter(inv => inv.invoice_type !== 'school-program')
})

// Filter school program invoices - amount YOU PAY TO CLIENT
const schoolInvoices = computed(() => {
    return siteInvoices.value.filter(inv => inv.invoice_type === 'school-program')
})

// Calculate total school program amount (what you pay to client)
const totalSchoolAmount = computed(() => {
    return schoolInvoices.value.reduce((sum, inv) => sum + (inv.amount_pay || 0), 0)
})

// Calculate ORIGINAL total for normal invoices (before any payments)
const totalNormalOriginal = computed(() => {
    return normalInvoices.value.reduce((sum, inv) => sum + (inv.amount_pay || 0), 0)
})

// Calculate remaining for normal invoices (amount to collect from client)
const totalNormalRemaining = computed(() => {
    return normalInvoices.value.reduce((sum, inv) => {
        const currentReceived = inv.amount_receive + (inv.tempPayment || 0)
        const remaining = Math.max(0, inv.amount_pay - currentReceived)
        return sum + remaining
    }, 0)
})

// Check if school program is larger than normal invoices
const isSchoolProgramLarger = computed(() => {
    return totalSchoolAmount.value > totalNormalOriginal.value
})

// Net amount = ORIGINAL Amount client owes you - Amount you owe client for school program
const netAmount = computed(() => {
    return totalNormalOriginal.value - totalSchoolAmount.value
})

// How much the entrepreneur ACTUALLY needs to pay right now
const netAmountRemaining = computed(() => {
    if (isSchoolProgramLarger.value) {
        // If school program is larger, entrepreneur doesn't need to pay anything
        return 0
    }
    return totalNormalRemaining.value - totalSchoolAmount.value
})

// Display normal invoices with calculated values
const displayNormalInvoices = computed(() => {
    return normalInvoices.value.map(inv => {
        const currentReceived = inv.amount_receive + (inv.tempPayment || 0)
        let remaining = Math.max(0, inv.amount_pay - currentReceived)

        // If school program is larger than all normal invoices, mark everything as paid
        if (isSchoolProgramLarger.value && !inv.tempPayment) {
            // Auto-allocate school program amount to cover all invoices
            inv.tempPayment = inv.amount_pay - inv.amount_receive
            remaining = 0
        }

        return {
            ...inv,
            displayAmountReceive: inv.amount_receive + (inv.tempPayment || 0),
            displayRemaining: remaining,
            displayStatus: getInvoiceStatus(inv)
        }
    })
})

// Display school program as a summary (not individual invoices)
const displaySchoolInvoices = computed(() => {
    return schoolInvoices.value.map(inv => {
        return {
            ...inv,
            displayAmountReceive: inv.amount_pay, // Always fully paid to client
            displayRemaining: 0,
            displayStatus: 'To Pay'
        }
    })
})

const paymentAmount = computed(() => {
    return rawPaymentValue.value || 0
})

const canProcessPayment = computed(() => {
    const hasInput = paymentInput.value !== '' && paymentInput.value !== null
    const validAmount = rawPaymentValue.value >= 0
    const hasInvoices = siteInvoices.value.length > 0
    return hasInput && validAmount && hasInvoices
})

// Add missing computed properties for template
const netAmountClass = computed(() => {
    if (netAmount.value < 0) return 'text-red-darken-2'
    if (netAmount.value > 0) return 'text-blue-darken-2'
    return 'text-grey'
})

const netAmountBgClass = computed(() => {
    if (netAmount.value < 0) return 'bg-red-lighten-5'
    if (netAmount.value > 0) return 'bg-blue-lighten-5'
    return 'bg-grey-lighten-5'
})

const netAmountTextClass = computed(() => {
    if (netAmount.value < 0) return 'text-red-darken-2 font-weight-bold'
    if (netAmount.value > 0) return 'text-blue-darken-2 font-weight-bold'
    return 'text-grey font-weight-bold'
})

const arrayToObject = (arr) => {
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
}

const balance = ref('');
const saleIncome = ref('');
const expenseTotal = ref('');

// Load invoices from API
const loadSiteInvoices = async () => {
    if (!site || !month) return
    loading.value = true
    try {
        const response = await axios.get('/api/invoicesDetail', {
            params: {
                site: site,
                month: month.slice(0, 7)
            }
        })
        const data = response.data.data.invoices
        expensesByCategory.value = arrayToObject(response.data.data.expenses_by_category || {})
        balance.value = response.data.data.balance?.beginning_balance || 0
        saleIncome.value = response.data.data.sale_income?.Total_Income || 0
        expenseTotal.value = response.data.data.expense || 0
        invoiceRecord.value = response.data.data.invoices_record || []
        // Clear existing invoices for this site
        invoices.value = invoices.value.filter(inv => inv.id_site !== site)

        // Add new invoices
        data.forEach(invoice => {
            invoices.value.push({
                id: invoice.id,
                id_site: invoice.site,
                invoice_type: invoice.invoice_type || 'N/A',
                amount_pay: Number(invoice.beginning_balance) || 0,
                beginning_balance: Number(invoice.beginning_balance) || 0,
                month: invoice.month ? invoice.month.slice(0, 10) : '',
                amount_receive: Number(invoice.amount_receive) || 0,
                tempPayment: 0,
                status: invoice.status || 'unpaid',
                remain_amount: Number(invoice.remain_amount) || 0
            })
        })

        // If school program is larger, auto-calculate allocation
        if (isSchoolProgramLarger.value) {
            calculateAutoAllocation()
        }

    } catch (error) {
        console.error('Error loading invoices:', error)
        snackbar.value = {
            show: true,
            message: t('settle_invoice.failed_to_load_invoices'),
            color: 'error'
        }
    } finally {
        loading.value = false
        resetPayment()
    }
}

// Auto-allocate when school program is larger than normal invoices
const calculateAutoAllocation = () => {
    // Reset temp payments for normal invoices
    normalInvoices.value.forEach(inv => {
        inv.tempPayment = 0
    })

    // School program amount is larger, so all normal invoices get fully paid
    const schoolAmountRemaining = totalSchoolAmount.value

    let remainingAllocation = schoolAmountRemaining

    // Allocate school program amount to normal invoices, sorted by month ascending
    const sortedNormalInvoices = normalInvoices.value
        .sort((a, b) => new Date(a.month) - new Date(b.month))

    for (const invoice of sortedNormalInvoices) {
        if (remainingAllocation <= 0) break

        const currentReceived = invoice.amount_receive + invoice.tempPayment
        const dueAmount = invoice.amount_pay - currentReceived

        if (dueAmount > 0) {
            const allocated = Math.min(remainingAllocation, dueAmount)
            invoice.tempPayment = allocated
            remainingAllocation -= allocated
        }
    }

    // Update payment input to show the calculated amount
    rawPaymentValue.value = 0
    paymentInput.value = '0'
}

// Allocation logic
const calculateAllocation = () => {
    const userPayment = rawPaymentValue.value || 0;

    // Reset temp payments for normal invoices
    normalInvoices.value.forEach(inv => {
        inv.tempPayment = 0
    })

    if (userPayment < 0) {
        // If no payment and school program is larger, still need to auto-allocate
        if (isSchoolProgramLarger.value) {
            calculateAutoAllocation()
        }
        return
    }

    // Total to allocate to normal invoices = user payment + school program amount
    const totalToAllocate = userPayment + totalSchoolAmount.value

    let remainingAllocation = totalToAllocate

    // Allocate to normal invoices, sorted by month ascending
    const sortedNormalInvoices = normalInvoices.value
        .sort((a, b) => new Date(a.month) - new Date(b.month))

    for (const invoice of sortedNormalInvoices) {
        if (remainingAllocation <= 0) break

        const currentReceived = invoice.amount_receive + invoice.tempPayment
        const dueAmount = invoice.amount_pay - currentReceived

        if (dueAmount > 0) {
            const allocated = Math.min(remainingAllocation, dueAmount)
            invoice.tempPayment = allocated
            remainingAllocation -= allocated
        }
    }
}

// Payment confirmation and processing
const confirmAndProcess = async () => {
    confirmDialog.value = false

    // if (!qrFile.value) {
    //     snackbar.value = {
    //         show: true,
    //         message: t('settle_invoice.upload_qr_required'),
    //         color: 'error',
    //         timeout: 5000
    //     }
    //     return
    // }

    let qrBase64 = null
    let qrFilename = null
    let qrFiletype = null

    if (qrFile.value) {
        const MAX_FILE_SIZE = 5 * 1024 * 1024 // 5MB
        if (qrFile.value.size > MAX_FILE_SIZE) {
            snackbar.value = {
                show: true,
                message: t('settle_invoice.qr_file_too_large'),
                color: 'error',
                timeout: 5000
            }
            return
        }

        const allowedImageTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'application/pdf', 'application/zip', 'application/x-zip-compressed']
        if (!allowedImageTypes.includes(qrFile.value.type)) {
            snackbar.value = {
                show: true,
                message: t('settle_invoice.qr_must_be_image'),
                color: 'error',
                timeout: 5000
            }
            return
        }

        const fileToBase64 = file =>
            new Promise((resolve, reject) => {
                const reader = new FileReader()
                reader.readAsDataURL(file)
                reader.onload = () => resolve(reader.result)
                reader.onerror = error => reject(error)
            })

        qrBase64 = await fileToBase64(qrFile.value)
        qrFilename = qrFile.value.name
        qrFiletype = qrFile.value.type
    }

    try {

        const normalPaymentsToSend = normalInvoices.value
            .filter(inv => inv.tempPayment > 0)
            .map(inv => {
                const newAmountReceive = inv.amount_receive + inv.tempPayment
                const newRemainAmount = Math.max(0, inv.amount_pay - newAmountReceive)
                const invoiceType = inv.invoice_type || 'N/A'
                const beginningBalance = inv.beginning_balance || 0
                return {
                    id: inv.id,
                    amount_receive: newAmountReceive,
                    remain_amount: newRemainAmount,
                    invoice_type: invoiceType,
                    beginning_balance: beginningBalance
                }
            })

        const schoolPaymentsToSend = schoolInvoices.value.map(inv => ({
            id: inv.id,
            amount_receive: inv.amount_pay,
            remain_amount: 0
        }))

        const paymentsToSend = [...normalPaymentsToSend, ...schoolPaymentsToSend]

        if (paymentsToSend.length === 0) {
            snackbar.value = {
                show: true,
                message: t('settle_invoice.no_payments_to_process'),
                color: 'warning',
                timeout: 5000
            }
            return
        }

        const paymentData = {
            payments: paymentsToSend,
            site: site,
            month: month,
            amount_received: paymentAmount.value,
            school_program_amount: totalSchoolAmount.value,
            originalBalance: balance.value,
            deductSaving: autoWithdrawalAmount.value,
            netAmount: netAmount.value,
            totalNormalRemaining: totalNormalRemaining.value,
            invoiceAndDeposit: paymentInput.value - netAmount.value, // Show how much is cash vs saving
            qr_code: qrBase64,
            qr_filename: qrFilename,
            qr_filetype: qrFiletype,
            paymentDate: paymentDate.value,
            transactionID: transactionID.value
        }

        const response = await axios.post('/api/invoices/update-payments', paymentData)

        if (response.data.success) {
            let successMessage = response.data.message
            snackbar.value = {
                show: true,
                message: successMessage,
                color: 'success',
                timeout: 6000
            }

            // Update local invoice states
            normalPaymentsToSend.forEach(payment => {
                const inv = invoices.value.find(i => i.id === payment.id)
                if (inv) {
                    inv.amount_receive = payment.amount_receive
                    inv.remain_amount = payment.remain_amount
                    inv.tempPayment = 0
                }
            })

            schoolPaymentsToSend.forEach(payment => {
                const inv = invoices.value.find(i => i.id === payment.id)
                if (inv) {
                    inv.amount_receive = payment.amount_receive
                    inv.remain_amount = payment.remain_amount
                    inv.tempPayment = 0
                }
            })

            // Reset inputs
            rawPaymentValue.value = 0
            paymentInput.value = ''
            reserveAmount.value = 0
            qrFile.value = null
            qrPreview.value = ''
            receiptPreview.value = ''

            // Close dialog if you emit event for it, uncomment if you have it:
            if (typeof emit === 'function') {
                emit('close-dialog')
            }

            router.push({
                path: '/cashReceipt',
                query: {
                    site: site,
                    month: month,
                }
            })
            //cashReceipt.value = true
            //location.reload()
            return
        }

        snackbar.value = {
            show: true,
            message: response.data.message || t('settle_invoice.payment_processing_failed'),
            color: 'error',
            timeout: 7000
        }

    } catch (error) {
        console.error('Failed to update payments:', error)

        let errorMessage = t('settle_invoice.failed_to_process_payment')

        if (error.response) {
            errorMessage = error.response.data.message ||
                error.response.data.error ||
                `Server error: ${error.response.status}`

            if (error.response.data.errors) {
                const validationErrors = Object.values(error.response.data.errors).flat()
                errorMessage += ' ' + validationErrors.join(', ')
            }
        } else if (error.request) {
            errorMessage = t('settle_invoice.no_response_server')
        } else {
            errorMessage = error.message || t('settle_invoice.unexpected_error')
        }

        snackbar.value = {
            show: true,
            message: errorMessage,
            color: 'error',
            timeout: 8000
        }
    }
}


const processPayment = () => {
    if (!canProcessPayment.value) return

    if (totalNormalRemaining.value > 0 && balance.value > 0) {
        // Only show if NOT shown before
        if (!hasShownWithdrawal.value) {
            isBalanceShown.value = true
            wathdrawalBalance.value = true
            hasShownWithdrawal.value = true // Mark as shown
            return
        }
        // If already shown, skip to confirm dialog
    }
    if (netAmount.value < 0) {
        // If net amount is negative, no payment needed
        savingFromSchool.value = true
        return
    }

    confirmDialog.value = true
}

// When you close the withdrawal dialog, automatically proceed to confirm
const closeWithdrawalDialog = () => {
    wathdrawalBalance.value = false
    // Automatically show confirm dialog after closing withdrawal
    setTimeout(() => {
        confirmDialog.value = true
    }, 100) // Small delay to ensure dialog closes properly
}

const resetPayment = () => {
    rawPaymentValue.value = 0
    paymentInput.value = ''
    reserveAmount.value = 0 // Reset reserve amount too
    qrFile.value = null
    qrPreview.value = ''
    receiptPreview.value = ''
    normalInvoices.value.forEach(inv => {
        inv.tempPayment = 0
    })
    if (isSchoolProgramLarger.value) {
        calculateAutoAllocation()
    }
}

const payAll = () => {
    if (isSchoolProgramLarger.value) {
        // If school program is larger, entrepreneur doesn't need to pay anything
        rawPaymentValue.value = 0
        paymentInput.value = '0'
        reserveAmount.value = 0
    } else {
        // Pay the net amount remaining (what client actually needs to pay)
        const amountToPay = Math.max(0, totalNormalRemaining.value - totalSchoolAmount.value)
        rawPaymentValue.value = amountToPay
        paymentInput.value = formatNumber(amountToPay)
        reserveAmount.value = amountToPay
    }
    calculateAllocation()
}

const getInvoiceStatus = (invoice) => {
    const currentReceived = invoice.amount_receive + (invoice.tempPayment || 0)
    if (currentReceived >= invoice.amount_pay) return 'Full'
    if (currentReceived > 0) return 'Not Full'
    return 'Unpaid'
}

const getSchoolInvoiceStatus = () => {
    return 'To Pay' // School program amount is always "to pay" to client
}

const getStatusColor = (item) => {
    const status = item.displayStatus
    if (status === 'Full') return 'green'
    if (status === 'Not Full') return 'amber'
    return 'red'
}

const getSchoolStatusColor = () => {
    return 'green' // School program is shown as "to pay" in green
}

const getAmountReceiveClass = (item) => {
    const status = item.displayStatus
    if (status === 'Full') return 'text-green-darken-2 font-weight-bold'
    if (status === 'Not Full') return 'text-blue-darken-2 font-weight-bold'
    return 'text-grey'
}

const getSchoolAmountReceiveClass = () => {
    return 'text-green-darken-2 font-weight-bold' // School program amount
}

// Use the same function for both normal and school invoices
const getRemainingClass = (item) => {
    if (item.displayRemaining === 0) return 'text-green-darken-2 font-weight-bold'
    if (item.displayRemaining > 0 && item.displayAmountReceive > 0) return 'text-amber-darken-2'
    return 'text-red-darken-2'
}
const saveAmountFromSchoolProgram = () => {
    alert('Site :' + site + ' Month :' + month + ' Amount to save :' + formatNumber(netAmount.value * -1))
    window.location.href = `/CashReceipt?site=${site}&month=${month}&save_amount=${netAmount.value * -1}`;
}
// Alias for template to avoid errors
const getSchoolRemainingClass = getRemainingClass

onMounted(() => {
    loadSiteInvoices()
})
</script>

<style scoped>
/* Main wrapper for 80% width */
.content-wrapper {
    width: 100%;
    margin: 0 auto;
    height: 100vh;
    overflow-y: auto;
}

/* Adjust container padding */
.v-container {
    max-width: 100% !important;
    padding: 8px !important;
}

.custom-table-container {
    overflow-x: auto;
    font-size: 0.85rem;
}

.file-preview {
    max-width: 100%;
    max-height: 200px;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 4px;
}

.table-header {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr 0.8fr 0.8fr 0.8fr 0.8fr;
    background-color: #f5f5f5;
    font-weight: bold;
    padding: 8px 12px;
    border-bottom: 2px solid #ddd;
    font-size: 0.8rem;
}

.table-row {
    display: grid;
    grid-template-columns: 0.8fr 1.2fr 0.8fr 0.8fr 0.8fr 0.8fr;
    padding: 6px 12px;
    border-bottom: 1px solid #eee;
    align-items: center;
    font-size: 0.8rem;
}

.table-row:hover {
    background-color: #f9f9f9;
}

.table-cell {
    padding: 2px 6px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.status-chip {
    min-width: 70px;
    justify-content: center;
    font-size: 0.75rem;
    height: 22px !important;
}

.h-100 {
    height: calc(100vh - 120px);
    min-height: 500px;
}

.text-right {
    text-align: right;
}

/* Make text smaller throughout */
.text-caption {
    font-size: 0.75rem !important;
}

.text-body-2 {
    font-size: 0.875rem !important;
}

/* Adjust padding for cards */
.v-card-text {
    padding: 12px !important;
}

.v-card-title {
    padding: 8px 16px !important;
}

/* Make buttons smaller */
.v-btn {
    font-size: 0.75rem !important;
}

/* Adjust close button */
.v-btn.icon {
    margin-bottom: 8px !important;
}
</style>
