<template>
  <v-container>
    <v-select
      v-model="selectedSite"
      :items="sites"
      label="Select Site"
      @change="reloadGraph"
    ></v-select>

    <historic-sales-graph ref="historicGraph" />
  </v-container>
</template>

<script>
import HistoricSalesGraph from "./HistoricSalesGraph.vue";

export default {
  components: { HistoricSalesGraph },

  data() {
    return {
      selectedSite: "A1",
      sites: ["A1", "A2", "A3"],
    };
  },

  methods: {
    reloadGraph() {
      this.$refs.historicGraph.siteId = this.selectedSite;
      this.$refs.historicGraph.fetchHistoricSales();
    },
  },
};
</script>
