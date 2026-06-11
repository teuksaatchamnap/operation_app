<template>
  <div class="receipt-container" ref="receiptContainerRef">
    <!-- Receipt Header - Logo Left, Title Center -->
    <div class="receipt-header">
      <div class="header-container">
        <div class="logo-container">
          <img :src="logoPath" alt="Company Logo" class="company-logo" />
        </div>
        <div class="title-container">
          <h1 class="receipt-title" > បណ្ណ័ទទួលប្រាក់ </h1>
        </div>
        <div > CR N: {{ receiptData.invoiceNumber || "" }}</div>
      </div>
    </div>

    <!-- Receipt Information -->
    <div class="receipt-info">
      <div class="info-left">
        <div class="info-item">
          <span class="info-label">បានទទួលប្រាក់ពី : {{ receiptData.customerName || "" }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">ទីតាំង : {{ receiptData.site || "" }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">ថ្ងៃខែ : {{ formattedKhmerDate(formattedDate) }}</span>
        </div>
      </div>
    </div>
    <div class="text-center receipt-title-balance">វិកយ័បត្រ</div><br>
    <!-- Total Receive Money -->
    <div class="table-section">
      <!-- <h3 class="receipt-title text-center invoice-show"> ប្រតិបត្តិការ /Transaction </h3> -->
      <div class="invoice-table">
        <table>
          <thead>
            <tr>
              <th class="info-label1 text-center invoice-show">បរិយាយ </th>
              <th class="info-label1 text-center invoice-show">ចំនួន </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="info-label text-center">ចំនួនទឹកប្រាក់សរុប   </td>
              <td class="text-center"> ៛ {{ formatCurrency(invoiceTotal) }}</td>
            </tr>
            <tr>
              <td class="info-label text-center"> ទឹកសាលា   </td>
              <td class="text-center"> ៛ {{ formatCurrency(receiptData.schoolProgram[0]?.beginning_balance || 0) }}</td>
            </tr>
            <tr v-if="(invoiceTotal - (receiptData.schoolProgram[0]?.beginning_balance || 0)) > 0">
                <td class="info-label text-center">
                  ទឹកប្រាក់ត្រូវបង់
                </td>
                <td class="text-center">
                  ៛ {{ formatCurrency(invoiceTotal - (receiptData.schoolProgram[0]?.beginning_balance || 0)) }}
                </td>
              </tr>
            <!-- <tr v-if="receiptData.savingOrWithdraw[0]?.invoice_type == 'saving'">
                    <td class="info-label text-center">
                      សន្សំ
                    </td>
                    <td class="text-center">
                      ៛ {{ formatCurrency(receiptData.savingOrWithdraw[0]?.transaction_amount || 0) }}
                    </td>
            </tr>
            <tr v-if="receiptData.savingOrWithdraw[0]?.invoice_type == 'withdraw'">
                    <td class="info-label text-center">
                      ដកប្រាក់
                    </td>
                    <td class="text-center">
                      ៛ {{ formatCurrency(receiptData.savingOrWithdraw[0]?.transaction_amount || 0) }}
                    </td>
            </tr> -->
            <tr v-if="cashReceived > 0">
              <td class="info-label text-center"> ប្រាក់ទទួលបាន   </td>
              <td v-if="receiptData.extraSaving[0]?.invoice_type == 'saving'" class="text-center">
                 ៛ {{formatCurrency(Number(cashReceived || 0) + Number(receiptData.extraSaving[0]?.transaction_amount || 0))}}
              </td>
              <td v-else class="text-center "> ៛ {{ formatCurrency(cashReceived) }}</td>
            </tr>
            <tr v-if="cashReceived < 0">
              <td class="info-label text-center"> ប្រាក់ទទួលបាន   </td>
              <td class="text-center "> ៛ 0</td>
            </tr>
            <tr>
              <td class="info-label text-center"> ទឹកប្រាក់នៅសល់  </td>
              <td class="text-center"> ៛ {{ formatCurrency(receiptData.totalRemainingInvoice ) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <br>
      <div class="text-center receipt-title-balance" > សមតុល្យសាច់ប្រាក់ </div><br>
      <!-- second table for details if needed -->
       <div class="invoice-table">
        <table>
          <thead>
            <tr>
              <th class="info-label1 text-center invoice-show">បរិយាយ </th>
              <th class="info-label1 text-center invoice-show">ចំនួន </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="info-label text-center"> សមតុល្យប្រាក់ដើមគ្រា  </td>
              <td class="text-center"> ៛ {{ formatCurrency(receiptData.balance || 0) }}</td>
            </tr>
            <tr v-if="receiptData.savingOrWithdraw[0]?.invoice_type == 'saving'">
                    <td class="info-label text-center">
                      សន្សំ
                    </td>
                    <td class="text-center">
                      ៛ {{ formatCurrency(receiptData.savingOrWithdraw[0]?.transaction_amount || 0) }}
                    </td>
            </tr>
            <tr v-if="receiptData.savingOrWithdraw[0]?.invoice_type == 'withdraw'">
                    <td class="info-label text-center">
                      ដកប្រាក់
                    </td>
                    <td class="text-center">
                      ៛ {{ formatCurrency(receiptData.savingOrWithdraw[0]?.transaction_amount || 0) }}
                    </td>
            </tr>


            <tr>
              <td class="info-label text-center"> សមតុល្យប្រាក់ចុងគ្រា  </td>
              <td class="text-center"> ៛ {{ formatCurrency(receiptData.beginning_month_balance || 0) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <br>

    <!-- Signatures Section -->
    <div class="signatures-section">
      <div class="signature-column">
        <div class="signature-line"></div>
        <p class="signature-label">បានបង់ប្រាក់ </p><br><br><br>
        <!-- <img src="/img/pp1.png" alt="Logo" style="height: 50px; width: 50px; margin-right: 10px;"> -->
        <p class="signature-name">
          {{ receiptData.customerName || "" }}
        </p>
      </div>

      <div class="signature-column">
        <div class="signature-line"></div>
        <p class="signature-label">ទទួលដោយ </p><br>
        <div v-if="receiptData.preparedBy == 'មន​ សោវី'" style="text-align: center;">
          <img src="/img/pp.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
        </div>
        <div v-else-if="receiptData.preparedBy == 'នូ ចំរើន'" style="text-align: center;">
          <img src="/img/btb.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
        </div>
        <div v-else-if="receiptData.preparedBy == 'ហ៊ន ស្រីរត្ន័'" style="text-align: center;">
          <img src="/img/kc.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
        </div>
        <div v-else-if="receiptData.preparedBy == 'ហ៊ាង ប៉ោឡេង'" style="text-align: center;">
          <img src="/img/sr.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
        </div>
        <div v-else style="text-align: center;">
          <img src="/img/default.png" alt="Logo" style="height: 50px; width: 50px; display: block; margin: 4px auto 0;">
        </div>
        <p class="signature-name">
          {{ receiptData.preparedBy || "________________" }}
        </p>
        <!-- <p class="signature-name">
          {{ receiptData.preparedBy || "________________" }}
        </p> -->
      </div>
    </div>
  </div>
  <!-- Action Buttons -->
    <div class="action-buttons mb-2" v-if="!isPrinting">
      <TableExportPng
        ref="tableExportPngRef"
        :table-ref="$refs.receiptContainerRef"
        :site-id="site"
        filename-prefix="cash-receipt"
        :message="notificationMessage"
        @telegram-sent="handleTelegramSent"
      />
    </div>
</template>

<script>
import axios from 'axios'
import TableExportPng from "../../components/TableExportPng.vue"
import { useCashierNotifications } from "../../composables/useCashierNotifications"

export default {
  name: "CashReceipt",
  components: {
    TableExportPng
  },
  data() {
    return {
      isPrinting: false,
      logoPath: "/img/logo.png",
      notificationMessage: {
        message: '💵 Cash Receipt',
        audio: null
      },

      receiptData: {
        balance: 0,
        beginning_month_balance: 0,
        customerName: "",
        site: "",
        receiptNumber: "",
        date: new Date(),
        schoolProgram: [],
        cashReceived: [],
        invoiceItems: [],      // Non-saving items
        savingBalance: [],     // Saving, withdraw, school-program
        siteBalances: [],      // Expenses and current balance
        savingOrWithdraw: [],   // To determine if it's saving or withdraw
        acknowledgedBy: "",
        preparedBy: "",
        invoiceNumber: "",
        totalRemainingInvoice: 0,
        extraSaving: [], // To hold any extra saving transactions if needed
      },
      site: this.$route.query.site || "",
      month: this.$route.query.month || "",
    }
  },
  computed: {
    formattedDate() {
      if (!this.receiptData.date) return ""
      return new Date(this.receiptData.date).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    },
    invoiceTotal() {
      return this.receiptData.invoiceItems.reduce((sum, item) => sum + Number(item.beginning_balance), 0)
    },
    cashReceived() {
      const result = this.receiptData.cashReceived.reduce((acc, item) => {
        const amount = Number(item.transaction_amount || 0)
        const type = item.invoice_type?.toLowerCase()?.trim() || ''

        // Skip withdraw and saving entirely
        if (type.includes('withdraw') || type.includes('saving')) {
          return acc
        }

        // Subtract school-program
        if (type.includes('school-program')) {
          acc.minus += amount
        } else {
          acc.total += amount
        }

        return acc
      }, { total: 0, minus: 0 })

      return result.total - result.minus
    },
    totalCashReceived() {
      return this.invoiceTotal - this.cashReceived
    },
    totalSchoolProgram() {
      return this.receiptData.schoolProgram.reduce((sum, item) => sum + Number(item.beginning_balance), 0)
    },
    totalEntrepreneurPayment() {
      return this.invoiceTotal - this.totalSchoolProgram
    },
    savingTotal() {
      return this.receiptData.savingBalance.reduce((sum, item) => sum + Number(item.beginning_balance), 0)
    },
    balanceTotal() {
      return this.receiptData.siteBalances.reduce((sum, balance) => sum + Number(balance.amount), 0)
    },
    grandTotal() {
      return this.invoiceTotal + this.savingTotal + this.balanceTotal
    },

  },
  watch: {
    '$route.query.site'(newSite) {
      this.site = newSite
      this.fetchReceiptData()
    },
    '$route.query.month'(newMonth) {
      this.month = newMonth
      this.fetchReceiptData()
    },
  },
  mounted() {
    this.fetchReceiptData()
    const { fetchNotificationMessage } = useCashierNotifications()
    fetchNotificationMessage('cash-receipt').then(message => {
      if (message) {
        this.notificationMessage = message
      }
    })
  },
  methods: {
    formattedKhmerDate(dateValue) {
        if (!dateValue) return '';
        const date = new Date(dateValue);
        return date.toLocaleDateString('en-GB');
    },
    async fetchReceiptData() {
      if (!this.site || !this.month) {
        return
      }

      try {
        const response = await axios.get("/api/invoicesDetail", {
          params: {
            site: this.site,
            month: this.month,
          },
        })

        const data = response.data.data || {}

        // Filter invoices - exclude saving, withdraw, school-program
        const schoolProgramTypes = ["school-program"]
        const savingOrWithdraw = ["withdraw", "saving"]
        const withdrawOrSavingTypes = ["saving"]
        const excludedTypes = ["saving", "withdraw", "school-program"]
        const regularInvoices = (data.invoicesCashReceipt || []).filter(
          inv => !excludedTypes.includes(inv.invoice_type?.toLowerCase())
        )
        const { totalBalance, totalTransactionAmount } = regularInvoices.reduce(
                  (acc, inv) => ({
                    totalBalance: acc.totalBalance + (parseFloat(inv.beginning_balance) || 0),
                    totalTransactionAmount: acc.totalTransactionAmount + (parseFloat(inv.transaction_amount) || 0)
                  }),
                  { totalBalance: 0, totalTransactionAmount: 0 }
                );
        // const totalBalance = regularInvoices.reduce((sum, inv) => sum + (inv.beginning_balance || 0), 0);
        // const totalTransactionAmount = regularInvoices.reduce((sum, inv) => sum + (inv.transaction_amount || 0), 0);
        const leftAmount = totalBalance - totalTransactionAmount
         if (leftAmount <= 0) {
          this.receiptData.totalRemainingInvoice = leftAmount
        } else {
           this.receiptData.totalRemainingInvoice = -1 * leftAmount
        }
        const schoolProgramInvoices = (data.invoicesCashReceipt || []).filter(
          inv => schoolProgramTypes.includes(inv.invoice_type?.toLowerCase())
        )
        const cashReceiptInvoices = (data.invoicesCashReceipt || []).filter(
          inv => !withdrawOrSavingTypes.includes(inv.invoice_type?.toLowerCase())
        )
        const extraSaving = (data.invoicesCashReceipt || []).filter(
          inv => withdrawOrSavingTypes.includes(inv.invoice_type?.toLowerCase())
        )
        this.receiptData.extraSaving = extraSaving.map((inv) => ({
          invoice_type: inv.invoice_type,
          beginning_balance: Number(inv.beginning_balance || 0),
          transaction_amount: Number(inv.transaction_amount || 0),
          status: inv.status || '',
        }))
        console.log('💾 Extra Saving:', this.receiptData.extraSaving)

        // Get saving-related invoices
        const savingInvoices = (data.invoicesCashReceipt || []).filter(
          inv => excludedTypes.includes(inv.invoice_type?.toLowerCase())
        )
        const savingOrWithdrawInvoices = (data.invoicesCashReceipt || []).filter(
          inv => savingOrWithdraw.includes(inv.invoice_type?.toLowerCase())
        )

        // Map regular invoices to invoiceItems (non-saving items)
        this.receiptData.invoiceItems = regularInvoices.map((inv) => ({
          invoice_type: inv.invoice_type,
          beginning_balance: Number(inv.beginning_balance || 0),
          status: inv.status || "",
        }))
        console.log('📊 cashReceiptInvoices:', this.receiptData.invoiceItems)
        this.receiptData.schoolProgram = schoolProgramInvoices.map((inv) => ({
          invoice_type: inv.invoice_type,
          beginning_balance: Number(inv.beginning_balance || 0),
          status: inv.status || "",
        }))

        // Map regular invoices to cashReceived
        this.receiptData.cashReceived = cashReceiptInvoices.map((inv) => ({
          invoice_type: inv.invoice_type,
          transaction_amount: Number(inv.transaction_amount || 0),
          status: inv.status || "",
        }))

        console.log('💰 Cash Receipt Invoices:', this.receiptData.cashReceived)

        // Map saving invoices to savingBalance
        this.receiptData.savingBalance = savingInvoices.map((inv) => ({
          invoice_type: inv.invoice_type,
          beginning_balance: Number(inv.beginning_balance || 0),
          status: inv.status || "",
        }))
        this.receiptData.savingOrWithdraw = savingOrWithdrawInvoices.map((inv) => ({
            invoice_type: inv.invoice_type,
            transaction_amount: Number(inv.transaction_amount || 0),
            status: inv.status || "",
        }))
        this.receiptData.siteBalances = (data.site_balances || []).map((balance) => ({
            balance_type: balance.balance_type,
            amount: Number(balance.amount || 0),
          }))
        this.receiptData.balance = Number(data.balance?.balance) || 0
        this.receiptData.beginning_month_balance = Number(data.balance?.beginning_balance) || 0

        // Set other receipt data fields
        this.receiptData.customerName = data.site_info?.Entrepreneur_Khmer_Name || "No Name"
        this.receiptData.site = this.site
        this.receiptData.date = new Date()
        this.receiptData.receiptNumber = data.receiptNumber || ""
        this.receiptData.invoiceNumber = this.site + this.month

        if(data.site_info.Platform == "PP" || data.site_info.Platform == "KSP"){
          this.receiptData.preparedBy = "មន​ សោវី"
        }
        else if (data.site_info.Platform == "BTB"){
          this.receiptData.preparedBy = "នូ ចំរើន"
        }
        else if (data.site_info.Platform == "KC"){
          this.receiptData.preparedBy = "ហ៊ន ស្រីរត្ន័"
        }
        else if (data.site_info.Platform == "SR"){
          this.receiptData.preparedBy = "ហ៊ាង ប៉ោឡេង"
        }
        else {
          this.receiptData.preparedBy = " ________________"
        }
        this.receiptData.acknowledgedBy = data.acknowledgedBy || ""

      } catch (error) {
        console.error("Failed to fetch receipt data:", error)
      }
    },

    formatCurrency(amount) {
      if (amount == null || isNaN(amount)) return "-"
      return new Intl.NumberFormat("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      }).format(amount)
    },

    handleTelegramSent() {
      this.$router.push('/cashier?tab=invoices');
    },

  }
}
</script>

<style scoped>
.receipt-container {
  font-family: Arial, sans-serif;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: white;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
.green-bg-black-text {
    background-color: #28a745 !important;
    color: #000000 !important;
}

.yellow-bg-black-text {
    background-color: #FFC107 !important;
    color: #000000 !important;
}
.invoice-show {
    background-color: #28a745 !important;
    color: #000000 !important;
}
.receipt-header {
  margin-bottom: 20px;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-container {
  flex: 0 0 auto;
}

.company-logo {
  height: 80px;
  width: auto;
}

.title-container {
  flex: 1;
  text-align: center;
}

.receipt-title {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  font-family: 'Hanuman', 'Khmer OS', 'Leelawadee UI', 'Arial', sans-serif;
}
.receipt-title-balance {
  margin: 0;
  font-size: 16px;
  color: blue ;
  font-weight: bold;
  font-family: 'Hanuman', 'Khmer OS', 'Leelawadee UI', 'Arial', sans-serif;
}

.header-spacer {
  flex: 0 0 auto;
  width: 80px;
}

.receipt-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.info-left {
  flex: 1;
}

.info-item {
  margin-bottom: 8px;
}

.info-label {
  margin: 0;
  font-size: 14px;
  font-weight: bold;
  font-family: 'Hanuman', 'Khmer OS', 'Leelawadee UI', 'Arial', sans-serif;
}
.info-label1 {
  margin: 0;
  font-size: 20px;
  font-weight: bold;
  font-family: 'Hanuman', 'Khmer OS', 'Leelawadee UI', 'Arial', sans-serif;
}
.table-section {
  margin-bottom: 20px;
}

.table-title {
  background-color: #f8f9fa;
  padding: 10px;
  margin: 0 0 10px 0;
  border: 1px solid #dee2e6;
  border-radius: 5px 5px 0 0;
}

.invoice-table {
  border: 1px solid #dee2e6;
  border-radius: 0 0 5px 5px;
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background-color: #f8f9fa;
  padding: 10px;
  border-bottom: 2px solid #dee2e6;
  text-align: left;
}

td {
  padding: 10px;
  border-bottom: 1px solid #dee2e6;
}

.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

.col-no {
  width: 50px;
}

.col-desc {
  width: 60%;
}

.col-price {
  width: 20%;
}

.invoice-total-row {
  background-color: #f8f9fa;
  font-weight: bold;
}

.total-label {
  padding-right: 20px;
}

.total-amount {
  font-size: 16px;
}

.summary-section {
  background-color: #f8f9fa;
  padding: 15px;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  padding-bottom: 5px;
  border-bottom: 1px dashed #ddd;
}

.summary-label {
  font-weight: bold;
}

.summary-value {
  font-weight: bold;
}

.final-section {
  margin-bottom: 30px;
}

.final-total-box {
  background-color: #007bff;
  color: white;
  padding: 20px;
  border-radius: 5px;
  text-align: center;
}

.final-total-content {
  margin-bottom: 10px;
}

.final-label {
  font-size: 18px;
  margin-right: 10px;
}

.final-amount {
  font-size: 24px;
  font-weight: bold;
}

.final-subtitle {
  font-size: 14px;
  opacity: 0.9;
}

.signatures-section {
  display: flex;
  justify-content: space-between;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 2px solid #dee2e6;
}

.signature-column {
  flex: 1;
  text-align: center;
}

.signature-line {
  height: 1px;
  background-color: #000;
  margin: 0 auto 10px;
  width: 200px;
}

.signature-label {
  margin: 5px 0;
  font-weight: bold;
}

.signature-name {
  margin: 0;
}

.action-buttons {
  margin-top: 30px;
  text-align: center;
}

.btn-download {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  border-radius: 5px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: background-color 0.3s;
}

.btn-download:hover:not(:disabled) {
  background-color: #218838;
}

.btn-download:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
}

.download-icon {
  margin-right: 8px;
  font-size: 18px;
}
</style>
