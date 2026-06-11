<script setup>
import { useRoute, useRouter } from "vue-router";
import { ref, computed } from "vue";
import EntrepreneurCard from "../../components/EntrepreneurCard.vue";
import SchoolCard from "../../components/SchoolCard.vue";
import { formatDateForDisplay } from "../../utils/dateUtils";
import { isCambodianHoliday } from "../../utils/cambodianHolidays";
import { useCurrency } from "../../composables/useCurrency";
import { useStore } from "vuex";

const route = useRoute();
const siteId = route.params.site;
const startDate = route.params.startDate;
const endDate = route.params.endDate;
const router = useRouter();

const queryParams = {
    start: startDate,
    end: endDate,
    site: siteId,
};
const loading = ref(true);
const saving = ref(false);
const readOnly = ref(false);
const review = ref(false);
const sales = ref({});
const errors = ref({});
const unitPrice = ref(null);
const files = ref([]);
const existingFiles = ref([]);
const schools = ref([]);
const touchedDates = ref(new Set());

const store = useStore();

const createObjectURL = (file) => {
    return URL.createObjectURL(file);
};

const isCashierAdmin = computed(() => {
    const user = store.state.user;
    return !!(
        user &&
        user.permissions &&
        user.permissions.includes("cashier_admin")
    );
});

const total = computed(() => {
    let total = 0;
    for (let i of Object.keys(sales.value)) {
        total += sales.value[i][0].quantity;
    }
    return total;
});

window.axios
    .get("/api/cashier/wis", {
        params: queryParams,
    })
    .then((response) => {
        const salesNormalized = response.data.wis;
        unitPrice.value = response.data.unit_price;
        schools.value = response.data.school;
        let currentDate = new Date(startDate)
        const stopDate = new Date(endDate)

        while (currentDate <= stopDate) {
            if (salesNormalized[currentDate.toISOString().slice(0,10)] == undefined) {
                salesNormalized[currentDate.toISOString().slice(0,10)] = [{
                    quantity: null,
                    sale_date: currentDate.toISOString().slice(0,10),
                    site: siteId,
                    type: "wis",
                }];
            }
            currentDate.setDate(currentDate.getDate() + 1)
        }
        sales.value = salesNormalized;
        if (response.data.is_validated && isCashierAdmin.value == false) {
            readOnly.value = true;
        }
        existingFiles.value = response.data.images;
        loading.value = false;
    });

const { formatKHR } = useCurrency();

const uploadFiles = async () => {
    if (files.value.length === 0) {
        return;
    }
    const formData = new FormData();
    files.value.forEach((file) => {
        formData.append("files[]", file);
    });
    formData.append("site", siteId);
    formData.append("related_date", endDate);
    formData.append("type", "wis");
    try {
        await window.axios.post("/api/cashier/upload", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });
        console.log("Files uploaded successfully in the background.");
        files.value = [];
    } catch (error) {
        console.error("Error uploading files:", error);
    }
};

const save = () => {
    saving.value = true;
    window.axios
        .post("/api/cashier/wis", { 
            unit_price: unitPrice.value,
            month: endDate,
            site: siteId,
            wis: Object.entries(sales.value)
                .filter(([date]) => touchedDates.value.has(date))
                .map(([, sale]) => sale[0])
        })
        .then(() => {
            uploadFiles();
            touchedDates.value = new Set();
            saving.value = false;
            router.push("/cashier?tab=wis");
        })
        .catch(() => {
            saving.value = false;
            alert("An error occurred while saving WiS.");
        });
};

const dateRange = computed(() => {
  const dates = []
  let currentDate = new Date(startDate)
  let stopDate = new Date(endDate)

  while (currentDate <= stopDate) {
    dates.push(new Date(currentDate))
    currentDate.setDate(currentDate.getDate() + 1)
  }

  return dates
})

const dateIntervals = computed(() => {
    const dates = dateRange.value;
    return [dates.slice(0, 10), dates.slice(10, 20), dates.slice(20)];
});

const handleKeyNavigation = (event, direction) => {
    if (readOnly.value) return;

    const focusedElement = event.target;
    const inputs = Array.from(
        document.querySelectorAll(".month-table input")
    ).filter((el) => !el.disabled && !el.readOnly);
    const currentIndex = inputs.indexOf(focusedElement);

    if (currentIndex === -1) return;

    let targetIndex = currentIndex;
    if (direction === "down") {
        targetIndex = currentIndex + 1;
    } else if (direction === "up") {
        targetIndex = currentIndex - 1;
    }

    if (targetIndex >= 0 && targetIndex < inputs.length) {
        inputs[targetIndex].focus();
        inputs[targetIndex].select();
    }
};

</script>

<template>
    <div>
        <div v-if="loading" class="d-flex justify-center mt-10 pt-10">
            <v-progress-circular indeterminate :size="60" color="primary" />
        </div>
        <div v-else>
            <div class="d-flex flex-row">
                <v-btn
                    class="ml-1 mr-5 mt-2"
                    prepend-icon="mdi-arrow-left"
                    append-icon="mdi-view-dashboard"
                    @click="$router.push('/cashier?tab=wis')"
                >
                    {{ $t("cashier.back_to_dashboard") }}
                </v-btn>
                <h4 class="pa-4">
                    {{ $t("cashier.wis") }} for site {{ siteId }}
                    <small class="ml-3">
                        {{ startDate }}
                        <v-icon size="x-small">mdi-arrow-right</v-icon>
                        {{ endDate }}
                    </small>
                </h4>
            </div>
            <v-sheet elevation="4">
                <v-row align="center" justify="center" align-content="center" class="pt-5">
                    <v-chip class="mt-2" color="primary" variant="elevated">{{ $t("cashier.unit_price") }}</v-chip>
                    <span v-if="readOnly" class="readOnly-input mt-2">{{unitPrice}}</span>
                    <div v-else>
                        <v-number-input
                            v-model="unitPrice"
                            :class="{
                                danger: unitPrice > 9999,
                            }"
                            density="compact"
                            class="py-0 px-1 mx-0 my-0 text-center no-underline"
                            style="width: 150px;"
                            hide-details
                            control-variant="hidden"
                            :min="0"
                            autocomplete="off"
                        />
                    </div>
                </v-row>
                <v-row v-if="dateRange.length > 0" align="center" justify="center" class="pt-5">
                    <table
                        v-for="(interval, i) in dateIntervals"
                        :key="i"
                        class="mr-5 month-table"
                    >
                        <tbody>
                            <tr 
                                v-for="date in interval" 
                                :key="date.toISOString()"
                                :class="{ 
                                    'bg-secondary-lighten-4': isCambodianHoliday(date),
                                    'bg-primary-lighten-4': !isCambodianHoliday(date) && date.getDay() === 0 
                                }"
                            >
                                <td>
                                    <v-chip :color="
                                        isCambodianHoliday(date) ? 'secondary' : 
                                        date.getDay() === 0 ? 'primary' : 
                                        'primary-lighten-4'
                                    ">{{
                                        formatDateForDisplay(date)
                                    }}</v-chip>
                                </td>
                                <td>
                                    <span v-if="readOnly" class="readOnly-input">{{
                                        sales[date.toISOString().slice(0, 10)]?.[0]
                                            ?.quantity ?? "-"
                                    }}</span>
                                    <v-number-input
                                        v-else
                                        v-model="
                                            sales[date.toISOString().slice(0, 10)][0]
                                                .quantity
                                        "
                                        :class="{
                                            danger:
                                                sales[
                                                    date.toISOString().slice(0, 10)
                                                ][0].quantity > 9999,
                                        }"
                                        density="compact"
                                        class="py-0 px-1 mx-0 my-0 text-center no-underline"
                                        hide-details
                                        control-variant="hidden"
                                        :min="0"
                                        autocomplete="off"
                                        @update:model-value="
                                            touchedDates.add(
                                                date.toISOString().slice(0, 10)
                                            )
                                        "
                                        @keydown.enter.prevent="
                                            handleKeyNavigation($event, 'down')
                                        "
                                        @keydown.up.capture.prevent.stop="
                                            handleKeyNavigation($event, 'up')
                                        "
                                        @keydown.down.capture.prevent.stop="
                                            handleKeyNavigation($event, 'down')
                                        "
                                    />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </v-row>

                <v-row align="center" justify="center" class="py-3">
                    Total: {{ total }} bottles = {{ formatKHR(total*unitPrice) }}
                </v-row>

                <v-row align="center" justify="center">
                    <v-col
                        v-for="(file, index) in existingFiles"
                        :key="'existingFiles' + index"
                        class="pic-scroll"
                    >
                        <v-img
                            :src="
                                file.path.replace(
                                    'public/',
                                    'storage/'
                                )
                            "
                            style="min-height: 500px; width: 100%"
                        >
                            <template #placeholder>
                                <v-row
                                    class="fill-height ma-0"
                                    align="center"
                                    justify="center"
                                >
                                    <v-progress-circular
                                        indeterminate
                                        color="grey-lighten-5"
                                    />
                                </v-row>
                            </template>
                        </v-img>
                    </v-col>
                </v-row>

                <v-row align="center" justify="center">
                    <v-col
                        v-if="!files.length && !readOnly"
                        class="px-5"
                        cols="auto"
                    >
                        <div class="text-center">
                            <v-file-input
                                v-model="files"
                                label="Add picture from entrepreneur"
                                multiple
                                placeholder="Add picture from entrepreneur"
                                prepend-icon="mdi-paperclip"
                                variant="outlined"
                                accept="image/*"
                                class="w-300"
                            />
                        </div>
                    </v-col>
                    <v-col
                        v-for="(file, index) in files"
                        v-else
                        :key="index"
                        class="pic-scroll"
                    >
                        <v-img
                            :src="createObjectURL(file)"
                            style="min-height: 500px; width: 100%"
                        >
                            <template #placeholder>
                                <v-row
                                    class="fill-height ma-0"
                                    align="center"
                                    justify="center"
                                >
                                    <v-progress-circular
                                        indeterminate
                                        color="grey-lighten-5"
                                    />
                                </v-row>
                            </template>
                        </v-img>
                        <div class="text-center">
                            <v-btn
                                class="mt-2 text-center"
                                @click="files.splice(index, 1)"
                            >
                                delete picture
                            </v-btn>
                        </div>
                    </v-col>
                </v-row>

                <v-row align="center" justify="space-around">
                    <EntrepreneurCard :site="route.params.site" />
                    <SchoolCard :site="route.params.site" :schools="schools" :year="parseInt(endDate.substring(0, 4))"/>
                    <v-btn
                        v-if="readOnly == false"
                        class="mx-5 my-5"
                        :loading="saving"
                        :disabled="saving"
                        prepend-icon="mdi-check"
                        variant="flat"
                        color="primary"
                        @click="review = true ; readOnly = true"
                    >
                        Next
                        <v-icon icon="mdi-arrow-right" />
                    </v-btn>
                    <v-btn
                        v-if="readOnly && review"
                        class="mx-5 my-5"
                        :loading="saving"
                        :disabled="saving"
                        prepend-icon="mdi-arrow-left"
                        variant="flat"
                        color="secondary"
                        @click="review = false ; readOnly = false"
                    >
                        Back
                    </v-btn>
                    <v-btn
                        v-if="readOnly && review"
                        class="mx-5 my-5"
                        :loading="saving"
                        :disabled="saving"
                        prepend-icon="mdi-check"
                        variant="flat"
                        color="primary"
                        @click="save()"
                    >
                        Save
                    </v-btn>
                    <v-btn
                        v-if="readOnly && !review"
                        class="mx-5 my-5"
                        :loading="saving"
                        :disabled="saving"
                        prepend-icon="mdi-check"
                        variant="flat"
                        color="primary"
                        @click="
                            $router.push('/cashier?tab=wis')
                        "
                    >
                        {{ $t("cashier.back_to_dashboard") }}
                    </v-btn>
                </v-row>
            </v-sheet>
        </div>
    </div>
</template>

<style scoped>
.w-300 {
    width: 300px;
}
.pic-scroll {
    max-height: 200px;
    overflow-y: scroll;
    max-width: 95%;
}
.expense-input {
    max-width: 400px;
    min-width: 300px;
}

.expenses-container {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    align-items: center;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}

.buttons {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.danger :deep(input) {
    box-shadow: inset 0 0 0 3px red;
    background-color: coral;
}
.readOnly-input {
    margin-left: 0.5rem;
    margin-right: 0.5rem;
    min-width: 3rem;
    display: inline-block;
    border: 1px solid #ccc;
    text-align: center;
    border-radius: 5px;
}
</style>
