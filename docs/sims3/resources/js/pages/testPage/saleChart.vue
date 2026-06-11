<template>
  <div>
    <!-- Site Selector -->
    <v-autocomplete v-model="selectedSite" :items="siteOptions" label="Select Site" outlined item-title="text"
      item-value="value" style="width: 150px;" @update:modelValue="fetchSalesData"></v-autocomplete>

    <!-- Chart Container -->
    <div class="chart-container">
      <canvas ref="lineChart"></canvas>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { Chart, registerables } from "chart.js";
import Swal from "sweetalert2";

export default {
  data() {
    return {
      selectedSite: null, // Selected site
      siteOptions: [],
      salesData: [],
      labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], // Months
      datasets: [], // Datasets for each year
      chart: null, // Chart instance
      colorMap: {
        2020: "rgba(0, 128, 0, 1)", // Green
        2021: "rgba(0, 0, 139, 1)", // Dark Blue
        2022: "rgba(0, 0, 0, 1)", // Black
        2023: "rgba(255, 99, 132, 1)", // Red
        2024: "rgba(54, 162, 235, 1)", // Blue
        2025: "rgba(255, 206, 86, 1)", // Yellow
        2026: "rgba(75, 192, 192, 1)"  // Green
      }
    };
  },
  async mounted() {
    Chart.register(...registerables);
    await this.fetchSalesData(); // Fetch data on initial load
  },
  methods: {
    async fetchSalesData() {
      // Show loading indicator
      Swal.fire({
        title: "Loading...",
        allowOutsideClick: false,
        didOpen: () => {
          Swal.showLoading();
        }
      });

      try {
        // Fetch data based on selected site
        const url = this.selectedSite
          ? `/api/salesChart/${this.selectedSite}`
          : "/api/salesChart";
        const response = await axios.get(url);
        this.salesData = response.data.data;
        this.siteOptions = response.data.sites;

        // Process data to create datasets for each year
        this.datasets = [];
        this.salesData.forEach((yearData) => {
          const year = yearData.year;
          const data = yearData.data;

          // Create an array of sales amounts for each month
          const salesAmounts = Array(12).fill(null); // Initialize with null for missing months
          data.forEach((entry) => {
            const monthIndex = parseInt(entry.month) - 1; // Convert month to array index (0-11)
            salesAmounts[monthIndex] = entry.sale_amount;
          });

          // Add dataset for this year
          this.datasets.push({
            label: `Sales ${year}`,
            data: salesAmounts,
            borderColor: this.colorMap[year] || "rgba(150, 150, 150, 1)", // Use fixed color or gray if year is unknown
            borderWidth: 2
          });
        });

        // Destroy existing chart before creating a new one
        if (this.chart) {
          this.chart.destroy();
        }

        this.renderChart();
      } catch (error) {
        console.error("Error fetching sales data:", error);
        Swal.fire("Error", "Failed to fetch data", "error");
      } finally {
        Swal.close(); // Close loading indicator
      }
    },
    renderChart() {
      const ctx = this.$refs.lineChart.getContext("2d");
      this.chart = new Chart(ctx, {
        type: "line",
        data: {
          labels: this.labels, // Months (01 to 12)
          datasets: this.datasets // Datasets for each year
        },
        options: {
          responsive: true, // Make the chart responsive
          maintainAspectRatio: false, // Allow the chart to adjust its aspect ratio
          scales: {
            x: {
              title: {
                display: true,
                text: "Month"
              }
            },
            y: {
              title: {
                display: true,
                text: "Sales Amount"
              }
            }
          }
        }
      });
    }
  }
};
</script>


<style scoped>
.chart-container {
  width: 70%;
  /* Set width to 70% */
  margin: 0 auto;
  /* Center the container */
  height: 400px;
  /* Set a fixed height */
}
</style>
