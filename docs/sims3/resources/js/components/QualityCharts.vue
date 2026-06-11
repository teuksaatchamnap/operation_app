<template>
  <v-row
    v-if="!loading"
    dense
  >
    <v-col
      cols="12"
      md="3"
    >
      <v-card
        title="Contamination after corrective actions"
        class="ma-3 rounded-lg"
      >
        <v-card-text>
          <apexchart
            type="pie"
            :options="contaminationAfter.chartOptions"
            :series="contaminationAfter.series"
          />
        </v-card-text>
      </v-card>
    </v-col>
    <v-col
      cols="12"
      md="3"
    >
      <v-card
        title="Unsafe water root cause"
        class="ma-3 rounded-lg"
      >
        <v-card-text>
          <apexchart
            type="pie"
            :options="unsafeWaterRootCause.chartOptions"
            :series="unsafeWaterRootCause.series"
          />
        </v-card-text>
      </v-card>
    </v-col>
    <v-col
      cols="12"
      md="3"
    >
      <v-card
        title="Contamination before corrective actions"
        class="ma-3 rounded-lg"
      >
        <v-card-text>
          <apexchart
            type="pie"
            :options="contaminationBefore.chartOptions"
            :series="contaminationBefore.series"
          />
        </v-card-text>
      </v-card>
    </v-col>
    <v-col
      cols="12"
      md="3"
    >
      <v-card
        title="Physico-chemical conformity"
        class="ma-3 rounded-lg"
      >
        <v-card-text>
          <apexchart
            type="bar"
            :options="physicoConformity.chartOptions"
            :series="physicoConformity.series"
          />
        </v-card-text>
      </v-card>
    </v-col>
    <v-col
      cols="12"
      md="3"
    >
      <v-card
        title="Sampling to analysis delay"
        class="ma-3 rounded-lg"
      >
        <v-card-text>
          <apexchart
            type="pie"
            :options="delay.chartOptions"
            :series="delay.series"
          />
        </v-card-text>
      </v-card>
    </v-col>
    <v-col
      cols="12"
      md="3"
    >
      <v-card
        title="Number of corrective actions"
        class="ma-3 rounded-lg"
      >
        <v-card-text class="d-flex justify-center pa-10 text-h3 font-weight-bold text-primary">
          {{ nbCorrectiveActions }}
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
<script>
import VueApexCharts from "vue3-apexcharts";

export default {
    name: 'QualityCharts',
    components: {
        apexchart: VueApexCharts,
    },
    props: {
        samples: {
            type: Object,
            default: () => { },
        }
    },
    data: function () {
        return {
            loading: true,
            nbCorrectiveActions: 0,
            contaminationAfter: {
                chartOptions: {
                    width: '100%',
                    legend: { position: 'top' },
                    labels: ['ok', 'level 1 - low risk', 'level 2 - medium risk', 'level 3 - high risk'],
                    colors: ['#03A9F4', '#FFEB3B', '#FF9800', '#F44336']
                },
                series: [0, 0, 0, 0]
            },
            contaminationBefore: {
                chartOptions: {
                    width: '100%',
                    legend: { position: 'top' },
                    labels: ['ok', 'level 1 - low risk', 'level 2 - medium risk', 'level 3 - high risk'],
                    colors: ['#03A9F4', '#FFEB3B', '#FF9800', '#F44336']
                },
                series: [0, 0, 0, 0]
            },
            delay: {
                chartOptions: {
                    width: '100%',
                    legend: { position: 'top' },
                    labels: ['<1', '1-3', '3-5', '>5'],
                    colors: ['#03A9F4', '#FFEB3B', '#FF9800', '#F44336']
                },
                series: [0, 0, 0, 0]
            },
            unsafeWaterRootCause: {
                chartOptions: {
                    width: '100%',
                    legend: { position: 'top' },
                    labels: [],
                },
                series: []
            },
            physicoConformity: {
                chartOptions: {
                    id: 1,
                    chart: {
                        type: 'bar',
                        stacked: true,
                        stackType: '100%'
                    },
                    plotOptions: {
                        bar: {
                            horizontal: true
                        }
                    },
                    width: '100%',
                    legend: { position: 'top' },
                    colors: ['#03A9F4', '#F44336', '#aaaaaa'],
                    xaxis: {
                        categories: ['free chlorine', 'conductivity', 'aluminium', 'turbidity', 'pH'],
                    },
                },
                series: [{
                    name: 'Conform',
                    data: [0, 0, 0, 0, 0]
                }, {
                    name: 'Not conform',
                    data: [0, 0, 0, 0, 0]
                }, {
                    name: 'Not tested',
                    data: [0, 0, 0, 0, 0]
                }]
            }
        }
    },
    watch: {
        samples(newSamples) {
            this.updateCharts(newSamples)
        }
    },
    mounted() {
        this.updateCharts(this.samples)
    },
    methods: {
        updateCharts(samples) {
            this.loading = true
            this.contaminationAfter.series = [0, 0, 0, 0]
            this.contaminationBefore.series = [0, 0, 0, 0]
            this.delay.series = [0, 0, 0, 0]
            this.unsafeWaterRootCause.series = []
            this.unsafeWaterRootCause.chartOptions.labels = []
            this.physicoConformity.series.forEach(s => s.data = [0, 0, 0, 0, 0])
            this.nbCorrectiveActions = 0
            Object.keys(samples).forEach(site => {
                let lastSample = samples[site][0];
                let firstSample = samples[site].slice(-1)[0]
                let contamination = Math.max(lastSample.contamination_level_bottle, lastSample.contamination_level_machine);
                this.contaminationAfter.series[contamination]++;
                contamination = Math.max(firstSample.contamination_level_bottle, firstSample.contamination_level_machine);
                this.contaminationBefore.series[contamination]++;
                let sampleWithPhysico = samples[site].find(s => s.chlorine || s.conductivity || s.ph)
                if (!sampleWithPhysico) {
                    sampleWithPhysico = firstSample
                }
                if (!sampleWithPhysico.chlorine) {
                    this.physicoConformity.series[2].data[0]++
                } else if (sampleWithPhysico.chlorine > 0.45) {
                    this.physicoConformity.series[1].data[0]++
                } else {
                    this.physicoConformity.series[0].data[0]++
                }
                if (!sampleWithPhysico.conductivity) {
                    this.physicoConformity.series[2].data[1]++
                } else if (sampleWithPhysico.conductivity > 800) {
                    this.physicoConformity.series[1].data[1]++
                } else {
                    this.physicoConformity.series[0].data[1]++
                }
                if (!sampleWithPhysico.aluminium) {
                    this.physicoConformity.series[2].data[2]++
                } else if (sampleWithPhysico.aluminium > 0.2) {
                    this.physicoConformity.series[1].data[2]++
                } else {
                    this.physicoConformity.series[0].data[2]++
                }
                if (!sampleWithPhysico.turbidity) {
                    this.physicoConformity.series[2].data[3]++
                } else if (sampleWithPhysico.turbidity > 2) {
                    this.physicoConformity.series[1].data[3]++
                } else {
                    this.physicoConformity.series[0].data[3]++
                }
                if (!sampleWithPhysico.ph) {
                    this.physicoConformity.series[2].data[4]++
                } else if (sampleWithPhysico.ph > 9 || sampleWithPhysico.ph < 6.5) {
                    this.physicoConformity.series[1].data[4]++
                } else {
                    this.physicoConformity.series[0].data[4]++
                }
                samples[site].forEach(s => {
                    if (s.root_cause) {
                        const rootCauseIndex = this.unsafeWaterRootCause.chartOptions.labels.findIndex(r => r === s.root_cause)
                        if (rootCauseIndex >= 0) {
                            this.unsafeWaterRootCause.series[rootCauseIndex]++
                        } else {
                            this.unsafeWaterRootCause.chartOptions.labels.push(s.root_cause)
                            this.unsafeWaterRootCause.series.push(1)
                        }
                    }
                    if(s.delay <= 1) {
                      this.delay.series[0]++
                    } else if(s.delay < 3) {
                      this.delay.series[1]++
                    }  else if(s.delay <= 5) {
                      this.delay.series[2]++
                    } else {
                      this.delay.series[3]++
                    }

                    if(s.action_done) {
                      this.nbCorrectiveActions++
                    }
                })
                this.physicoConformity.series = [...this.physicoConformity.series]
                this.unsafeWaterRootCause.series = [...this.unsafeWaterRootCause.series]
                this.delay.series = [...this.delay.series]
                this.unsafeWaterRootCause.chartOptions = {...this.unsafeWaterRootCause.chartOptions}
                this.contaminationAfter.series = [...this.contaminationAfter.series]
                this.contaminationBefore.series = [...this.contaminationBefore.series]
            })
            this.loading = false
        }
    }
}
</script>