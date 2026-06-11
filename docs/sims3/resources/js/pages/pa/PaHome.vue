<template>
  <v-card class="ma-4">
    <v-tabs
      v-model="tab"
      bg-color="green"
      :touch="false"
    >
      <v-tab value="my-pa">
        My PA
      </v-tab>
      <v-tab value="manager">
        My Team PA
      </v-tab>
      <div v-if="$store.state.user.permissions.includes('mission_admin')">
        <v-tab value="admin">
          All Staff PA
        </v-tab>
      </div>
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
          color="blue"
          icon="mdi-hospital"
          @click="$router.push({ path: '/pa/form' })"
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
          v-if="email"
          class="ml-5 mt-2 mr-5"
          color="secondary"
          icon="mdi-microsoft-excel"
          @click="exportExcel()"
        />
      </div>
      <!-- show data -->
      <v-data-table
        v-model:items-per-page="itemsPerPage"
        :headers="headers"
        :items="filterPA"
        density="compact"
        item-value="sample_date"
        class="pa-4"
      >
        <template #item.training="{ item }">
          <!-- <span v-if="item.status != 'loading'"> -->
          <v-chip
            size="small"
            color="green"
            @click.prevent="
              $router.push({
                path: '/training/' + item.staff_email,
              })
            "
          >
            <v-icon
              start
              size="x-small"
              icon="mdi-apple-keyboard-shift"
            />Click
          </v-chip>
          <!-- </span> -->
          <!-- <v-progress-linear v-else indeterminate color="yellow-darken-2" /> -->
        </template>
        <template #item.total_score="{ item }">
          <div v-if="item.total_score > 0">
            {{ item.total_score }}
          </div>
          <div v-else-if="item.score_last_time > 0">
            {{ item.score_last_time }}
          </div>
          <div v-else>
            0
          </div>
        </template>
        <template #item.validate="{ item }">
          <div v-if="item.validate == 'validated'">
            <v-chip
              size="small"
              color="orange"
              class="validated"
            >
              Validated
            </v-chip>
          </div>
          <div v-else>
            <v-chip
              size="small"
              color="red"
              class="waiting"
            >
              Waiting
            </v-chip>
          </div>
        </template>
        <template #item.staff_agree="{ item }">
          <div v-if="item.staff_agree == 'agree'">
            <v-chip
              size="small"
              color="blue"
              class="validated"
            >
              Agree
            </v-chip>
          </div>
          <div v-else>
            <v-chip
              size="small"
              color="red"
              class="waiting"
            />
          </div>
        </template>

        <template #item.actions="{ item }">
          <!-- <div v-for="item in position" :key="item.position"> && item.validate !='validated' -->
          <v-chip
            size="small"
            color="primary"
            @click.prevent="
              $router.push({ path: '/pa/' + item.id })
            "
          >
            <v-icon
              start
              size="x-small"
              icon="mdi-pencil"
            />Modify
          </v-chip>
          ||
          <v-chip
            v-if="item.staff_agree != 'agree'"
            size="small"
            color="primary"
            @click.prevent="staffAgree(item.id)"
          >
            <v-icon
              start
              size="x-small"
              icon="mdi-pencil"
            />Agree
          </v-chip>
          <!-- ||
          <v-chip size="small" color="blue" @click="newPrintExcel(item.id)">
            <v-icon start size="x-small" icon="mdi-printer" />Print
          </v-chip>  -->
          <!-- <v-chip v-if="$store.state.user.permissions.includes('edit_permissions')" size="small" color="error"
            @click.prevent="showConfirmationDialog(item.id)">
            <v-icon start size="x-small" icon="mdi-pencil" />Delete
          </v-chip> -->

          <!-- </div> -->
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
  <div class="text-center">
    <v-dialog
      v-model="dialog"
      activator="parent"
      width="auto"
    >
      <v-card>
        <v-card-text>
          PA excel is ready for download. Click Print !!!
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="primary"
            block
            @click="dialog = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
  <div class="text-center">
    <v-dialog
      v-model="showConfirmation"
      activator="parent"
      width="auto"
    >
      <v-card>
        <v-card-title class="text-h6">
          Confirm Deletion
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete this record?
        </v-card-text>
        <v-card-actions>
          <v-btn
            color="error"
            text
            @click="showConfirmation = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            text
            @click="deleteRecord()"
          >
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
// import { VDataTable } from 'vuetify/labs/VDataTable'
import Swal from "sweetalert2";
export default {
    name: "PAHome",
    data: function () {
        return {
            open: false,
            position: "",
            positionData: [],
            dialog: false,
            loading: true,
            PA: [],
            showConfirmation: false,
            itemsPerPage: 15,
            deleteId: "",
            email: "",
            search: "",
            tab: "my-pa",
            throttleTimer: -1,
            headers: [
                {
                    title: "Name",
                    align: "start",
                    key: "staff_name",
                    width: 130,
                },
                // { title: 'Department', align: 'center', key: 'staff_dept', width: 150 },
                {
                    title: "Type",
                    align: "center",
                    key: "staff_type_pa",
                    width: 150,
                },
                {
                    title: "Supervisor By",
                    align: "center",
                    key: "staff_supervisor_by",
                    width: 150,
                },
                {
                    title: "PA Date",
                    align: "center",
                    key: "staff_do_pa_date",
                    width: 120,
                },
                {
                    title: "PA score",
                    align: "center",
                    key: "total_score",
                    width: 100,
                },
                {
                    title: "Manager Status",
                    align: "center",
                    key: "validate",
                    width: 100,
                },
                {
                    title: "Staff Status",
                    align: "center",
                    key: "staff_agree",
                    width: 100,
                },
                {
                    title: "Training",
                    align: "center",
                    key: "training",
                    width: 100,
                },
                { title: "", align: "center", key: "actions", width: 250 },
            ],
        };
    },
    computed: {
        filterPA() {
            if (this.search == "") {
                return this.PA;
            } else {
                // return this.PA.filter(m => (m.staff_name + m.staff_dept + m.staff_supervisor_by + m.staff_type_pa + m.staff_do_pa_date + m.total_score).includes(this.search))
                return this.PA.filter((m) =>
                    (
                        m.staff_name +
                        m.staff_dept +
                        m.staff_supervisor_by +
                        m.staff_type_pa +
                        m.staff_do_pa_date +
                        m.total_score
                    )
                        .toLowerCase()
                        .includes(this.search.toLowerCase())
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
                this.getPA();
            });
        },
    },
    mounted() {
        //this.email = this.$store.state.user.email
        if (this.$store.state.user.permissions.includes("mission_admin")) {
            this.email = true;
        } else {
            this.email = false;
        }
        this.getPA();
        this.showExcelDownloadMessage();
    },
    methods: {
        showConfirmationDialog(id) {
            this.showConfirmation = true;
            this.deleteId = id;
        },
        staffAgree(id) {
            Swal.fire({
                title: "Are you sure?",
                text: "By clicking agree, you will be agree this PA",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#3085d6",
                cancelButtonColor: "#d33",
                confirmButtonText: "Yes, agree!",
            }).then((result) => {
                if (result.isConfirmed) {
                    window.axios
                        .put("/api/pa/staffAgree/" + id)
                        .then((response) => {
                            Swal.fire(
                                "Agreed!",
                                response.data.message,
                                "success"
                            );
                            this.getPA();
                        });
                }
            });
            // window.axios.put('/api/pa/staffAgree/' + id).then(response => {
            //   alert(response.data.message);
            //   this.getPA()
            // });
        },
        getPA() {
            this.loading = true;
            window.axios.get("/api/pa/?" + this.tab + "=1").then((response) => {
                this.PA = response.data.pa;
                this.loading = false;
            });
        },
        showExcelDownloadMessage() {
            // alert ("Download excel is in construction !!! Thank you for your patient")
            setTimeout(() => {
                this.dialog = false;
            }, 500);
        },
        printExcel(id) {
            window.axios
                .get("/api/pa/print/" + id, { responseType: "blob" })
                .then((response) => {
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", "PA.xlsx");
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
        newPrintExcel(id) {
            window.axios
                .get("/api/pa/newprint/" + id, { responseType: "blob" })
                .then((response) => {
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", "PA.xlsx");
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                });
        },
        deleteRecord() {
            window.axios
                .delete("/api/pa/delete/" + this.deleteId)
                .then((response) => {
                    this.showConfirmation = false;
                    alert(response.data);
                    this.getPA();
                });
        },
        exportExcel() {
            window.axios
                .get("/api/padownloadExcel", { responseType: "blob" })
                .then((response) => {
                    console.log(response.data);
                    const url = URL.createObjectURL(
                        new Blob([response.data], {
                            type: "application/vnd.ms-excel",
                        })
                    );
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute("download", "PA.xlsx");
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
