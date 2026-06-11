<template>
  <v-card class="pa-4">
    <h3>Historic Sales (Bot/day exc. WinS)</h3>
    <canvas ref="historicChart"></canvas>
  </v-card>
</template>

<script>
import { Chart, registerables } from "chart.js";
import axios from "axios";

Chart.register(...registerables);

export default {
  name: "HistoricSalesGraph",

  data() {
    return {
      siteId: "A1", // default site, you can bind this with your v-select
      chart: null,
      historicData: [],
    };
  },

  mounted() {
    this.fetchHistoricSales();
  },

  methods: {
    async fetchHistoricSales() {
      try {
        const response = await axios.get(`/api/report/${this.siteId}`);
        this.historicData = response.data.historicSale || [];
        this.renderChart();
      } catch (error) {
        console.error("Error fetching historic sales:", error);
      }
    },

    renderChart() {
      const ctx = this.$refs.historicChart.getContext("2d");

      if (this.chart) {
        this.chart.destroy(); // destroy old chart before rendering new
      }

      const labels = this.historicData.map((item) => item.Month);
      const values = this.historicData.map((item) => item.total_bottle);

      this.chart = new Chart(ctx, {
        type: "line",
        data: {
          labels,
          datasets: [
            {
              label: "Bottles/Day",
              data: values,
              borderColor: "#42A5F5",
              backgroundColor: "rgba(66,165,245,0.2)",
              fill: true,
              tension: 0.3,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: true },
          },
          scales: {
            x: {
              title: { display: true, text: "Month" },
            },
            y: {
              title: { display: true, text: "Bottles Sold" },
              beginAtZero: true,
            },
          },
        },
      });
    },
  },
};
</script>
