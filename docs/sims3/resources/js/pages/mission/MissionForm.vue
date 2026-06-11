<template>
  <v-form v-if="!loading" class="bg-grey-lighten-1 pa-4" @submit.prevent="saveMission">
    <v-card>
      <v-tabs v-model="tab" bg-color="primary">
        <v-tab value="Mission">Mission</v-tab>
        <v-tab value="Mission_Detail">Mission Detail</v-tab>
        <v-tab value="Other_expense">Other Expense</v-tab>
      </v-tabs>
      <v-card-text>
        <v-window v-model="tab">
          <v-window-item value="Mission">
            <v-card prepend-icon="mdi-briefcase-edit" title="Mission Letter" class="mb-3 rounded-lg">
              <v-card-text>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field v-model="mission.requester" density="compact" label="Requester" hide-details="auto"
                      :readonly="true" :rules="required" />
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field v-model="mission.validator" density="compact" label="Validator" hide-details="auto"
                      :readonly="true" :rules="required" />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" md="3">
                    <v-text-field v-model="mission.location" density="compact" label="Location" hide-details="always" />
                  </v-col>
                  <v-col cols="12" md="3">
                    <v-text-field v-model="mission.distance" density="compact" type="number" label="Distance"
                      hide-details="always" />
                  </v-col>
                  <v-col cols="12" md="2">
                    <v-text-field v-model="mission.start_date" density="compact" type="date" label="Start date"
                      hide-details="always" />
                  </v-col>
                  <v-col cols="12" md="2">
                    <v-text-field v-model="mission.end_date" density="compact" type="date" label="End date"
                      hide-details="auto" />
                  </v-col>
                  <v-col cols="12" md="2">
                    <v-text-field v-model="mission.days_off" density="compact" type="number" label="Days off"
                      hide-details="auto" />
                  </v-col>
                </v-row>
                <v-row>
                  <v-col cols="12" md="6">
                    <v-row>
                      <v-col cols="12" md="12">
                        <v-text-field v-model="mission.title" density="compact" label="Title" hide-details="always" />
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-select v-model="mission.transportation" density="compact" label="Transportation"
                          :items="configurations.transportation" />
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-select v-model="mission.need_advance" density="compact" label="Need advance?"
                          item-title="name" item-value="value" :items="configurations.cashiers" />
                      </v-col>
                    </v-row>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-textarea v-model="mission.purpose" auto-grow density="compact" label="Purpose of mission"
                      rows="4" />
                  </v-col>
                </v-row>
                <v-row v-if="$store.state.user.permissions.includes('mission_admin')" class="mt-0 pt-0">
                  <v-col cols="12" md="12">
                    <v-textarea v-model="mission.admin_comment" auto-grow density="compact"
                      label="Admin comment / only visible to admin team" rows="1" />
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-window-item>


          <v-window-item value="Mission_Detail">
            <v-card prepend-icon="mdi-briefcase-edit" title="Mission Letter" class="mb-3 rounded-lg">
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="8">
                      <v-table density="compact">
                        <thead>
                          <tr>
                            <th class="text-left">
                              Start Date
                            </th>
                            <th class="text-left">
                              End Date
                            </th>
                            <th class="text-left">
                              Purpose
                            </th>
                            <th class="text-left">
                              Perdiem
                            </th>
                            <th class="text-left">
                              Accommodation
                            </th>
                            <th class="text-left">
                              Location
                            </th>
                            <th class="text-left">
                              Signature
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="item in mission.mission_detail" :key="item.site">
                            <td>{{ item.mission_start_date }}</td>
                            <td>{{ item.mission_end_date }}</td>
                            <td>{{ item.purpose }}</td>
                            <td>{{ item.perdiem }}</td>
                            <td>{{ item.accommodation }}</td>
                            <td>{{ item.site }}</td>
                            <td>Correct</td>
                            <!-- <td>{{ new Intl.NumberFormat('en-US', {
                              style: 'currency', currency: 'USD'
                              }).format(item.total) }}
                            </td> -->
                            <td>
                              <v-btn icon="mdi-trash-can" density="compact" color="red"
                                @click="deleteExpense($event, index)" />
                            </td>
                          </tr>
                          <!-- <tr class="text-h6">
                            <td colspan="3" class="text-right">
                              Total
                            </td>
                            <td>
                              {{ new Intl.NumberFormat('en-US', {
                                style: 'currency', currency: 'USD'
                              }).format(mission.total) }}
                            </td>
                          </tr> -->
                        </tbody>
                      </v-table>
                    </v-col>
                    <v-col cols="12" md="4" class="d-flex flex-row align-end">
                      <v-btn color="deep-orange" prepend-icon="mdi-cash-plus" @click="showExpenseForm = true">
                        Add expense
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-card-text>
              
            </v-card>
          </v-window-item>

          <v-window-item value="Other_expense">
            <v-card prepend-icon="mdi-briefcase-edit" title="Mission Letter" class="mb-3 rounded-lg">
                <v-card-text>
                  <v-row>
                    <v-col cols="12" md="8">
                      <v-table density="compact">
                        <thead>
                          <tr>
                            <th class="text-left">
                              Expense type
                            </th>
                            <th class="text-left">
                              Quantity
                            </th>
                            <th class="text-left">
                              Unit price
                            </th>
                            <th class="text-left">
                              Total
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          <!-- <tr v-for="item in mission.other_expenses" :key="item.title">
                            <td>{{ item.title }}</td>
                            <td>{{ item.quantity }}</td>
                            <td>{{ item.unit_price }}</td>
                            <td>{{ new Intl.NumberFormat('en-US', {
                              style: 'currency', currency: 'USD'
                              }).format(item.total) }}
                            </td>
                            <td>
                              <v-btn icon="mdi-trash-can" density="compact" color="red"
                                @click="deleteExpense($event, index)" />
                            </td>
                          </tr> -->
                          <tr>
                            <td>
                              <v-text-field v-model="expense.title" density="compact" label="Title" :rules="required" />
                            </td>
                            <td>
                              <v-text-field v-model="expense.quantity" density="compact" label="Quantity"
                                type="number" :rules="required" />
                            </td>
                            <td>
                              <v-text-field v-model="expense.unit_price" type="number" density="compact"
                                label="Unit price" :rules="required" />
                            </td>
                            <td>
                              {{ isNaN(expense.quantity * expense.unit_price) ? 0 : expense.quantity * expense.unit_price }}
                            </td>
                          </tr>
                        </tbody>
                      </v-table>
                    </v-col>
                    <v-col cols="12" md="4" class="d-flex flex-row align-end">
                      <v-btn color="deep-orange" prepend-icon="mdi-cash-plus" @click="showExpenseForm = true">
                        Add expense
                      </v-btn>
                    </v-col>
                  </v-row>
                </v-card-text>  
              </v-card>
            </v-window-item>
        </v-window> 
      </v-card-text>
    </v-card>
    <v-container>
      <v-row class="ma-2" justify="center">
        <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" size="large" @click="$router.go(-1)">
          Cancel
        </v-btn>
        <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" size="large" type="submit">
          Save
        </v-btn>
      </v-row>
    </v-container>
  </v-form>
  <div v-if="loading" class="d-flex justify-center pt-10 mt-10">
    <v-progress-circular indeterminate :size="60" color="primary" />
  </div>
  <v-dialog v-model="showExpenseForm" transition="dialog-bottom-transition" width="500">
    <v-card>
      <v-card-text>
        <v-form v-if="!loading" @submit.prevent="addMissionDetail">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model="mission_letter.mission_start_date" type="date" density="compact" label="Start Date" :rules="required" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="mission_letter.mission_end_date" type="date" density="compact" label="End Date" :rules="required" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="12">
              <v-textarea v-model="mission_letter.purpose" auto-grow density="compact" label="Purpose" rows="3" :rules="required" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field v-model="mission_letter.perdiem" density="compact" label="Perdiem" type="number" :rules="required" />
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field v-model="mission_letter.accommodation" density="compact" label="Accommodation" type="number" :rules="required" />
            </v-col>
            <v-col cols="12" md="6">              
              <v-text-field v-model="mission_letter.site" density="compact" label="Site" type="text" :rules="required" />
            </v-col>
          </v-row>
          <v-row class="ma-2" justify="center">
            <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" @click="showExpenseForm = false">
              Cancel
            </v-btn>
            <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" type="submit">
              Add expense
            </v-btn>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog>

  <!-- <v-dialog v-model="showExpenseForm" transition="dialog-bottom-transition" width="500">
    <v-card>
      <v-card-text>
        <v-form v-if="!loading" @submit.prevent="addExpense">
          <v-text-field v-model="expense.title" density="compact" label="Title" :rules="required" />
          <v-text-field v-model="expense.unit_price" type="number" density="compact" label="Unit price"
            :rules="required" />
          <v-text-field v-model="expense.quantity" density="compact" label="Quantity" type="number" :rules="required" />
          <div class="text-h6">
            Total: {{ isNaN(expense.quantity * expense.unit_price) ? 0 : expense.quantity * expense.unit_price }}
          </div>
          <v-row class="ma-2" justify="center">
            <v-btn prepend-icon="mdi-cancel" rounded="lg" color="error" class="ma-4" @click="showExpenseForm = false">
              Cancel
            </v-btn>
            <v-btn prepend-icon="mdi-content-save" rounded="lg" color="primary" class="ma-4" type="submit">
              Add expense
            </v-btn>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>
  </v-dialog> -->
</template>

<script>

export default {
  name: 'MissionForm',
  data: function () {
    return {
      loading: true,
      sites: [],
      configurations: {},
      showExpenseForm: false,
      mission_letter: {
        mission_start_date: new Date().toJSON().slice(0, 10),
        mission_end_date: new Date().toJSON().slice(0, 10),
      },
      error: null,
      expense: {
        title: '',
        quantity: 0,
        unit_price: 0,
        total: 0,
      },
      dataLocation:[],
      tab: null,
      mission: {
        admin_comment: '',
        pa: '',
        id: undefined,
        location: undefined,
        start_date: new Date().toJSON().slice(0, 10),
        end_date: new Date().toJSON().slice(0, 10),
        days_off: 0,
        distance: 0,
        cost_accomodation: 0,
        cost_gasoline: 0,
        cost_per_diem: 0,
        nb_days: 0,
        nb_nights: 0,
        need_advance: undefined,
        other_expenses: [],
        mission_detail: [],
        other_expenses_total: 0,
        position: undefined,
        purpose: "",
        requester: "",
        status: "waiting validation",
        title: "",
        total: 0,
        liters: 0,
        transportation: undefined,
        validator: "",
        throttleTimer: -1,
      },
      hasError: false,
      required: [
        value => {
          if (value) return true
          return 'This field is required.'
        },
      ]
    }
  },
  computed: {
  },
  watch: {
    "mission.distance"() {
      this.calculate()
    },
    "mission.start_date"() {
      this.calculate()
    },
    "mission.end_date"() {
      this.calculate()
    },
    "mission.transportation"() {
      this.calculate()
    },
    "mission.days_off"() {
      this.calculate()
    },
  },
  unmounted() {
    document.body.classList.remove('bg-grey-lighten-1')
  },
  mounted() {
    document.body.classList.add('bg-grey-lighten-1')
    const requests = []
    if (this.$route.params.id) {
      requests.push(window.axios.get("/api/missions/" + this.$route.params.id).then(response => {
        this.mission = response.data;
        this.mission.other_expenses = JSON.parse(this.mission.other_expenses)
      }))
    }
    requests.push(window.axios.get("/api/sites").then(response => {
      this.sites = response.data.reduce(function (map, obj) {
        map[obj.Id_Site] = obj.Advisor;
        return map;
      }, {});
    }))
    requests.push(window.axios.get("/api/configurations?app=mission").then(response => {
      this.configurations = response.data.reduce(function (map, c) {
        map[c.name] = JSON.parse(c.value);
        return map;
      }, {});
    }))
    window.axios.all(requests).then(() => {
      if (!this.$route.params.id) {
        this.mission.transportation = this.configurations.transportation[0]
        this.mission.need_advance = this.configurations.cashiers[this.configurations.cashiers.length - 1]
        this.calculate()
      }
      this.mission.requester = this.$store.state.user.email
      this.mission.validator = this.$store.state.user.manager
      this.loading = false
    })
  },
  methods: {
    calculateTotal() {
      this.mission.total = 0;
      this.mission.other_expenses_total = 0;
      this.mission.total += (this.mission.cost_gasoline * this.mission.liters);
      this.mission.total += (this.mission.cost_accomodation * this.mission.nb_nights);
      this.mission.total += (this.mission.cost_per_diem * this.mission.nb_days);
      for (expense in this.mission.other_expenses) {
        var expense = this.mission.other_expenses[expense];
        this.mission.total += Number.parseFloat(expense.total);
        this.mission.other_expenses_total += Number.parseFloat(expense.total);
      }
    },
    calculate() {
      if (this.throttleTimer) {
        clearTimeout(this.throttleTimer);
      }
      this.throttleTimer = setTimeout(() => {
        let position = this.$store.state.user.position;
        let days = (new Date(this.mission.end_date) - new Date(this.mission.start_date)) / (1000 * 60 * 60 * 24)
        this.mission.nb_days = days - this.mission.days_off + 1
        this.mission.nb_nights = this.mission.nb_days - 1

        var km_per_liter = this.configurations.cost.km_per_liter;
        if (this.mission.transportation == "TS car")
          km_per_liter = this.configurations.cost.km_per_liter_car;
        this.mission.cost_gasoline = this.configurations.cost.gasoline_price;
        this.mission.liters = Math.round(100 * this.mission.distance / km_per_liter) / 100;
        if (this.mission.transportation == "other")
          this.mission.liters = 0;
        if (this.mission.distance > 40) {
          if (position == "staff") {
            this.mission.cost_per_diem = this.configurations.cost.per_diem_more_than_40;
            this.mission.cost_accomodation = this.configurations.cost.accomodation;
          } else if (position == "manager") {
            this.mission.cost_per_diem = this.configurations.cost.manager_per_diem_more_than_40;
            this.mission.cost_accomodation = this.configurations.cost.manager_accomodation;
          } else if (position == "excom") {
            this.mission.cost_per_diem = this.configurations.cost.excom_per_diem_more_than_40;
            this.mission.cost_accomodation = this.configurations.cost.excom_accomodation;
          } else if (position == "ed") {
            this.mission.cost_per_diem = this.configurations.cost.ed_per_diem;
            this.mission.cost_accomodation = this.configurations.cost.ed_accomodation;
          }
        }
        else if (this.mission.distance > 10) {
          if (position == "staff") {
            this.mission.cost_per_diem = this.configurations.cost.per_diem_10_to_40;
            this.mission.cost_accomodation = this.configurations.cost.accomodation;
          } else if (position == "manager") {
            this.mission.cost_per_diem = this.configurations.cost.manager_per_diem_10_to_40;
            this.mission.cost_accomodation = this.configurations.cost.manager_accomodation;
          }
        }
        else {
          this.mission.cost_per_diem = 0;
          this.mission.cost_accomodation = 0;
        }
        console.log(position, this.mission.cost_per_diem, this.mission.cost_accomodation)
        this.calculateTotal();
      }, 500);
    },
    addExpense(validationEvent) {
      validationEvent.then(result => {
        if (result.valid === true) {
          this.expense.total = isNaN(this.expense.quantity * this.expense.unit_price) ? 0 : this.expense.quantity * this.expense.unit_price
          this.mission.other_expenses.push(this.expense)
          this.expense = {}
          this.calculateTotal()
          this.showExpenseForm = false
        }
      })
    },
    addMissionDetail(validationEvent) {
      validationEvent.then(result => {
        if (result.valid === true) {
         
        this.error = null;

      // Get current location
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
           // this.sendLocationToBackend(latitude, longitude);
          console.log("Latitude: " + latitude + ", Longitude: " + longitude);
          },
          (error) => {
            this.loading = false;
            this.error = 'Unable to retrieve location: ' + error.message;
          }
        );
      } else {
        this.loading = false;
        this.error = 'Geolocation is not supported by this browser.';
      }



          this.mission.mission_detail.push(this.mission_letter)
          this.mission_letter = {}
          this.calculateTotal()
          this.showExpenseForm = false
        }
      })
    },
    deleteExpense(index) {
      this.mission.other_expenses.splice(index, 1);
      this.calculateTotal();
    },
    saveMission(validationEvent) {
      this.hasError = false;
      validationEvent.then(result => {
        if (result.valid === true) {
          this.loading = true;
          if (!this.mission.id) {
            window.axios.post("/api/missions", this.mission).then(() => {
              this.$router.go(-1)
            }).catch(() => {
              this.loading = false;
              this.hasError = true;
            })
          } else {
            window.axios.put("/api/missions/" + this.mission.id, this.mission).then(() => {
              this.$router.go(-1)
            }).catch(() => {
              this.loading = false;
              this.hasError = true;
            })
          }
        } else {
          this.hasError = true;
        }
      })
    },
    async sendToBackend(latitude, longitude) {
      try {
        const response = await window.axios.post('/api/checkLocation', {
          siteName: this.siteName,
          latitude,
          longitude,
        });

        this.dataLocation = response.data;
        this.loading = false;
      } catch (error) {
        this.loading = false;
        this.error = error.response?.data?.message || 'Error checking location';
      }
    },
  }
}
</script>
