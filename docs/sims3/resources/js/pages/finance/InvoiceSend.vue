<template>
  <v-container class="pa-8" style="max-width: 900px; border: 1px solid #000; background: #fff;">

    <!-- ===== HEADER SECTION ===== -->
    <div style="display: flex; align-items: center;">
      <img src="/img/logo.png" alt="Company Logo" style="height: 70px; margin-right: 15px;" />
      <h2 style="margin: 0;">{{ company.name }}</h2>
    </div>

    <!-- BTB Office centered -->
    <h2 class="text-center mt-2" style="margin: 0;">
      {{ invoice.platform }}
    </h2>

    <!-- Dynamic address centered -->
    <div class="text-center" style="margin-top: 4px;">
      {{ officeAddress }}
    </div>

    <!-- ===== INVOICE DETAILS ===== -->
    <v-row class="mt-6">
      <v-col cols="6">
        <p><strong>Date:</strong> {{ invoice.date }}</p>
        <p><strong>To:</strong> {{ invoice.to }}</p>
        <p><strong>Platform:</strong> {{ invoice.platform }}</p>
      </v-col>

      <v-col cols="6" class="text-right">
        <p><strong>No:</strong> {{ invoice.no }}</p>
        <p><strong>Advisor:</strong> {{ invoice.advisor }}</p>
        <p><strong>Cashier:</strong> {{ invoice.cashier }}</p>
      </v-col>
    </v-row>

    <h2 class="text-center mt-6 mb-4" style="text-decoration: underline;">INVOICE</h2>

    <table class="invoice-table">
      <thead>
        <tr>
          <th>No</th>
          <th>Item Code</th>
          <th>Description</th>
          <th>QTY</th>
          <th>Price</th>
          <th>Total Price</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="(item, index) in invoice.items" :key="index">
          <td>{{ index + 1 }}</td>
          <td>{{ item.code }}</td>
          <td>{{ item.description }}</td>
          <td>{{ item.qty }}</td>
          <td>{{ formatCurrency(item.price) }}</td>
          <td>{{ formatCurrency(item.qty * item.price) }}</td>
        </tr>
      </tbody>

      <tfoot>
        <tr>
          <td colspan="5" class="text-right"><strong>Total</strong></td>
          <td><strong>{{ formatCurrency(totalAmount) }}</strong></td>
        </tr>
      </tfoot>
    </table>

    <v-row class="mt-12 text-center">
      <v-col>
        <strong>Buyer</strong>
        <div class="signature-line"></div>
      </v-col>

      <v-col>
        <strong>Seller</strong>
        <div class="signature-line"></div>
      </v-col>

      <v-col>
        <strong>Staff</strong>
        <div class="signature-line"></div>
      </v-col>
    </v-row>

  </v-container>
</template>

<script>
export default {
  name: "InvoicePage",

  data() {
    return {
      company: {
        name: "Name of Company",
      },

      invoice: {
        date: "2025-12-01",
        no: "SBIC2025",
        to: "Jhon",
        advisor: "Samnang",
        cashier: "Chamrouen",
        platform: "BTB",

        items: [
          { code: "2025334", description: "test", qty: 1, price: 1000 },
          { code: "432123", description: "cloreing", qty: 3, price: 100 }
        ]
      }
    };
  },

  computed: {
    totalAmount() {
      return this.invoice.items.reduce(
        (sum, item) => sum + item.qty * item.price,
        0
      );
    },

    // 🔥 Dynamic office address based on platform
    officeAddress() {
      const platform = this.invoice.platform;

      if (platform === "BTB") return "sok BTB";
      if (platform === "PP") return "sok PP";
      if (platform === "KC") return "sok KC";

      return "No address";
    }
  },

  methods: {
    formatCurrency(value) {
      return value.toLocaleString();
    }
  }
};
</script>

<style scoped>
.invoice-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
  font-size: 15px;
}

.invoice-table th,
.invoice-table td {
  border: 1px solid #000;
  padding: 10px;
  text-align: center;
}

.invoice-table th {
  background: #f0f0f0;
  font-weight: bold;
}

.signature-line {
  margin-top: 40px;
  border-top: 1px solid #000;
  width: 150px;
  margin-left: auto;
  margin-right: auto;
}
</style>
