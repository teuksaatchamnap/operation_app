<template>
  <v-container>
    <v-row no-gutters>
      <v-col cols="12" sm="12" class="text-h4 text-center my-10">
        Welcome to SIMS 3.0
      </v-col>
    </v-row>

    <div class="d-flex flex-wrap" style="gap:30px">
      <v-card class="text-center mx-auto" :width="cardWidth - 120" :height="cardWidth - 120" elevation="10" :ripple="true"
        href="https://dashboard.teuksaat1001.com/" target="_blank">
        <v-img :width="cardWidth" aspect-ratio="16/9" cover src="img/commcare.png" />
        <v-card-title>
          Commcare dashboard
        </v-card-title>
        <v-card-subtitle>
          Sites monthly follow-up
        </v-card-subtitle>
        <v-card-actions class="flex-row-reverse">
          <v-btn class="bg-teal text-white font-weight-black" href="https://dashboard.teuksaat1001.com/" target="_blank">
            Go
          </v-btn>
        </v-card-actions>
      </v-card>
      <!-- Site Analysis  img/analysis.jpeg-->
      <v-card  class="text-center mx-auto" :width="cardWidth - 120" :height="cardWidth - 120"
        elevation="10" :ripple="true" @click="$router.push('/analysis')">
        <v-img :width="cardWidth" aspect-ratio="16/9" cover src="img/analysis.jpeg" />
        <v-card-title>
          Site Analysis
        </v-card-title>
        <v-card-subtitle>
          Analysis Data
        </v-card-subtitle>
        <v-card-actions class="flex-row-reverse">
          <v-btn class="bg-blue text-white font-weight-black" @click="$router.push('/analysis')">
            Go
          </v-btn>
        </v-card-actions>
      </v-card>
      <!-- end site analysis -->
      <v-card v-if="$store.state.user.permissions.includes('quality_view')" class="text-center mx-auto" :width="cardWidth - 120" :height="cardWidth - 120"
        elevation="10" :ripple="true" @click="$router.push('/quality')">
        <v-img :width="cardWidth" aspect-ratio="16/9" cover src="img/lab.png" />
        <v-card-title>
          Quality app
        </v-card-title>
        <v-card-subtitle>
          Record and follow-up on lab results
        </v-card-subtitle>
        <v-card-actions class="flex-row-reverse">
          <v-btn class="bg-blue text-white font-weight-black" @click="$router.push('/quality')">
            Go
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-card v-if="$store.state.user.permissions.includes('consumable_request')" class="text-center mx-auto" :width="cardWidth - 120" :height="cardWidth - 120" elevation="10" :ripple="true"
        @click="$router.push('/consumable/excelUpload')">
        <v-img :width="cardWidth" aspect-ratio="16/9" cover src="img/mission.png" />
        <v-card-title>
          Consumable Request
        </v-card-title>
        <v-card-subtitle>
          Order consumables for sites
        </v-card-subtitle>
        <v-card-actions class="flex-row-reverse">
          <v-btn class="bg-green text-white font-weight-black" @click="$router.push('/consumable/excelUpload')">
            Go
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-card class="text-center mx-auto" :width="cardWidth - 120" :height="cardWidth - 120" elevation="10" :ripple="true"
        @click="$router.push('/technical')">
        <v-img :width="cardWidth" aspect-ratio="16/9" cover src="img/technical.png" />
        <v-card-title>
          Technical app
        </v-card-title>
        <v-card-subtitle>
          Follow up on technical interventions
        </v-card-subtitle>
        <v-card-actions class="flex-row-reverse">
          <v-btn class="bg-purple text-white font-weight-black" @click="$router.push('/technical')">
            Go
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-card  v-if="$store.state.user.permissions.includes('finance_check')" class="text-center mx-auto" :width="cardWidth - 120" :height="cardWidth - 120" elevation="10" :ripple="true"
        @click="$router.push('/finance')">
        <v-img :width="cardWidth" aspect-ratio="16/9" cover src="img/finance.png" />
        <v-card-title>
          Finance app
        </v-card-title>
        <v-card-subtitle>
          Process invoice settlements from sites
        </v-card-subtitle>
        <v-card-actions class="flex-row-reverse">
          <v-btn class="bg-pink text-white font-weight-black" @click="$router.push('/finance')">
            Go
          </v-btn>
        </v-card-actions>
      </v-card>

      <v-card v-if="$store.state.user.permissions.includes('site_view')" class="text-center mx-auto" :width="cardWidth - 120" :height="cardWidth - 120"
        elevation="10" :ripple="true" @click="$router.push('/site')">
        <v-img :width="cardWidth" aspect-ratio="16/9" cover src="img/site.png" />
        <v-card-title>
          Site database
        </v-card-title>
        <v-card-subtitle>
          Collect all information about sites
        </v-card-subtitle>
        <v-card-actions class="flex-row-reverse">
          <v-btn class="bg-indigo text-white font-weight-black" @click="$router.push('/site')">
            Go
          </v-btn>
        </v-card-actions>
      </v-card>
    </div>
  </v-container>
</template>
<script>
export default {
  name: 'WelcomePage',
  data: function () {
    return {
      cardWidth: 380
    }
  },
}
</script>