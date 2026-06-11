<template>
  <v-card class="ma-4">
    <v-tabs
      v-model="tab"
      bg-color="primary"
    >
      <v-tab value="my-missions">
        Your missions
      </v-tab>
      <v-tab value="manager">
        Missions of my team
      </v-tab>
      <v-tab value="admin">
        All missions
      </v-tab>
    </v-tabs>
    <v-card-text
      v-if="loading"
      class="d-flex justify-center mt-10"
    >
      <v-progress-circular
        indeterminate
        :size="60"
        color="primary"
      />
    </v-card-text>
    <v-card-text v-else>
      <div class="d-flex flex-row align-center mb-3">
        <v-btn
          class="mr-5"
          color="primary"
          icon="mdi-briefcase-plus"
          @click="$router.push({ path: '/mission/form' })"
        />
        <v-text-field
          v-model="search"
          density="compact"
          label="Search"
          hide-details
          clearable
          class="shrink"
          prepend-inner-icon="mdi-clipboard-text-search"
        />
        <v-btn
          class="ml-5 mt-2 mr-5"
          color="secondary"
          icon="mdi-microsoft-excel"
          @click="exportExcel()"
        />
      </div>
      <v-data-table
        v-model:items-per-page="itemsPerPage"
        :headers="headers"
        :items="filteredMissions"
        density="compact"
        item-value="sample_date"
        class="pa-4"
      >
        <template #item.status="{ item }">
          <span :class="item.status">{{ item.status }}</span>
        </template>
        <template #item.actions="{ item }">
          <span v-if="item.status != 'loading'">
            <v-chip
              v-if="
                (item.requester === $store.state.user.email &&
                  item.status != 'expenses validated') ||
                  $store.state.user.permissions.includes(
                    'mission_admin'
                  ) ||
                  item.validator === $store.state.user.email
              "
              size="small"
              color="primary"
              @click.prevent="
                $router.push({
                  path: '/mission/' + item.id,
                })
              "
            >
              <v-icon
                start
                size="x-small"
                icon="mdi-pencil"
              />edit
            </v-chip>
            <v-chip
              v-if="
                item.status == 'waiting validation' &&
                  (item.validator === $store.state.user.email ||
                    $store.state.user.permissions.includes(
                      'mission_admin'
                    ))
              "
              size="small"
              color="blue"
              @click.prevent="updateMission(item, 'validated')"
            ><v-icon
              start
              size="x-small"
              icon="mdi-check-circle"
            />validate</v-chip>
            <v-chip
              v-if="
                $store.state.user.permissions.includes(
                  'mission_admin'
                ) && item.status == 'validated'
              "
              size="small"
              color="red"
              @click.prevent="updateMission(item, 'advanced')"
            ><v-icon
              start
              size="x-small"
              icon="mdi-cash-fast"
            />advance</v-chip>
            <v-chip
              v-if="
                $store.state.user.permissions.includes(
                  'mission_admin'
                ) &&
                  (item.status == 'validated' ||
                    item.status == 'advanced')
              "
              size="small"
              color="green"
              @click.prevent="
                updateMission(item, 'expenses validated')
              "
            ><v-icon
              start
              size="x-small"
              icon="mdi-cash-check"
            />expenses validate</v-chip>
            <v-chip
              size="small"
              @click.prevent="printMission(item)"
            ><v-icon
              start
              size="x-small"
              icon="mdi-printer"
              color="purple"
            />print</v-chip>
          </span>
          <v-progress-linear
            v-else
            indeterminate
            color="yellow-darken-2"
          />
        </template>
        <template #item.requester="{ item }">
          {{
            item.requester.substring(0, item.requester.indexOf("@"))
          }}
        </template>
        <template #item.validator="{ item }">
          {{
            item.validator.substring(0, item.validator.indexOf("@"))
          }}
        </template>
        <template #item.need_advance="{ item }">
          {{
            item.need_advance.indexOf("@") > 0
              ? item.need_advance.substring(
                0,
                item.need_advance.indexOf("@")
              )
              : item.need_advance
          }}
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
export default {
    name: "MissionHome",
    data: function () {
        return {
            loading: true,
            missions: [],
            itemsPerPage: 15,
            search: "",
            tab: "my-missions",
            throttleTimer: -1,
            headers: [
                { title: "Date", align: "start", key: "start_date" },
                { title: "Requester", align: "center", key: "requester" },
                { title: "Validator", align: "center", key: "validator" },
                { title: "Location", align: "center", key: "location" },
                {
                    title: "Need advance?",
                    align: "center",
                    key: "need_advance",
                },
                { title: "Status", align: "center", key: "status" },
                { title: "", align: "center", key: "actions" },
            ],
        };
    },
    computed: {
        filteredMissions() {
            if (this.search == "") {
                return this.missions;
            } else {
                return this.missions.filter((m) =>
                    (
                        m.requester +
                        m.validator +
                        m.status +
                        m.start_date +
                        m.end_date +
                        m.location
                    ).includes(this.search)
                );
            }
        },
    },
    watch: {
        tab() {
            // we throttle the call in case people click too much
            if (this.throttleTimer) {
                clearTimeout(this.throttleTimer);
            }
            this.throttleTimer = setTimeout(() => {
                this.getMissions();
            });
        },
    },
    mounted() {
        this.getMissions();
    },
    methods: {
        getMissions() {
            this.loading = true;
            window.axios
                .get("/api/missions/?" + this.tab + "=1")
                .then((response) => {
                    this.missions = response.data;
                    this.loading = false;
                });
        },
        updateMission(mission, newStatus) {
            mission.status = newStatus;
            window.axios
                .put("/api/missions/" + mission.id, mission)
                .then(() => (mission.status = newStatus));
            mission.status = "loading";
        },
        printMission(mission) {
            window.axios
                .get("/api/missions/" + mission.id + "/print", {
                    responseType: "blob",
                })
                .then((response) => {
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/msword",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute(
                        "download",
                        "mission_" + mission.id + ".docx"
                    );
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
        exportExcel() {
            window.axios
                .get("/api/missionsExport?" + this.tab + "=1&excel=1", {
                    responseType: "blob",
                })
                .then((response) => {
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute(
                        "download",
                        "missions_" +
                            new Date().toISOString().substring(0, 10) +
                            ".xlsx"
                    );
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
    },
};
</script>

<style>
.waiting {
    color: red;
    font-weight: bold;
}

.validated {
    color: orange;
    font-weight: bold;
}

.advanced {
    color: green;
    font-weight: bold;
}

.expense_validated {
    color: #666666;
    font-weight: bold;
}
</style>
