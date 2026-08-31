<template>
        <v-card rounded="xl" elevation="3" class="overflow-hidden">

          <!-- Header -->
          <div class="form-header pa-5">
            <div class="d-flex align-center ga-3">
              <v-avatar color="white" size="44">
                <v-icon color="primary" size="24">mdi-account-group</v-icon>
              </v-avatar>
              <div>
                <div class="text-h6 font-weight-bold text-white">Entrepreneur Management</div>
                <div class="text-caption text-white opacity-80">Site & Entrepreneur Records</div>
              </div>
            </div>
          </div>

          <!-- Tab Buttons -->
          <div class="pa-4 d-flex flex-wrap ga-2 bg-white">
            <v-btn
              v-for="tab in tabs"
              :key="tab.value"
              :color="tab.color"
              :variant="activeTab === tab.value ? 'flat' : 'tonal'"
              :prepend-icon="tab.icon"
              rounded="lg"
              size="small"
              class="text-none font-weight-bold"
              @click="activeTab = tab.value"
            >
              {{ tab.label }}
            </v-btn>
          </div>

          <v-divider />

          <v-tabs-window v-model="activeTab">

            <!-- ── Tab 1 : Site Close ─────────────────────────────── -->
            <v-tabs-window-item value="site_close">
              <v-card-text class="pa-5">
                <div class="tab-section-label mb-4">
                  <v-icon size="16" color="error" class="mr-1">mdi-lock</v-icon>
                  <span>Site Close Information</span>
                </div>

                <v-form ref="formClose" @submit.prevent="submit('site_close')">
                  <v-row density="comfortable">
                    <v-col cols="12" sm="6">
                      <v-autocomplete
                        v-model="siteClose.site"
                        :items="sites"
                        label="Site *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-office-building"
                        :rules="[required]"
                        clearable
                        autocomplete="off"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="siteClose.close_date"
                        type="date"
                        label="Close Date *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-calendar"
                        :rules="[required]"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="siteClose.report_by"
                        label="Report By *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-account"
                        :rules="[required]"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="siteClose.reason"
                        label="Reason *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-alert-circle-outline"
                        :rules="[required]"
                      />
                    </v-col>
                    <v-col cols="12">
                      <v-textarea
                        v-model="siteClose.reason_detail"
                        label="Reason Detail"
                        variant="outlined"
                        density="compact"
                        hide-details
                        prepend-inner-icon="mdi-text-box-outline"
                        rows="3"
                        auto-grow
                      />
                    </v-col>
                  </v-row>

                  <v-alert v-if="alerts.site_close" :type="alerts.site_close.type" class="mt-4" density="compact" closable
                    @click:close="alerts.site_close = null">
                    {{ alerts.site_close.message }}
                  </v-alert>

                  <div class="d-flex justify-end ga-2 mt-5">
                    <v-btn variant="text" @click="reset('site_close')">Reset</v-btn>
                    <v-btn color="error" variant="flat" type="submit" :loading="loading.site_close"
                      prepend-icon="mdi-content-save" rounded="lg">
                      Save
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-tabs-window-item>

            <!-- ── Tab 2 : Site Open ──────────────────────────────── -->
            <v-tabs-window-item value="site_open">
              <v-card-text class="pa-5">
                <div class="tab-section-label mb-4">
                  <v-icon size="16" color="success" class="mr-1">mdi-lock-open</v-icon>
                  <span>Site Open Information</span>
                </div>

                <v-form ref="formOpen" @submit.prevent="submit('site_open')">
                  <v-row density="comfortable">
                    <v-col cols="12" sm="6">
                      <v-autocomplete
                        v-model="siteOpen.site"
                        :items="sites"
                        label="Site *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-office-building"
                        :rules="[required]"
                        clearable
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="siteOpen.open_date"
                        type="date"
                        label="Open Date *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-calendar"
                        :rules="[required]"
                      />
                    </v-col>
                  </v-row>

                  <v-alert v-if="alerts.site_open" :type="alerts.site_open.type" class="mt-4" density="compact" closable
                    @click:close="alerts.site_open = null">
                    {{ alerts.site_open.message }}
                  </v-alert>

                  <div class="d-flex justify-end ga-2 mt-5">
                    <v-btn variant="text" @click="reset('site_open')">Reset</v-btn>
                    <v-btn color="success" variant="flat" type="submit" :loading="loading.site_open"
                      prepend-icon="mdi-content-save" rounded="lg">
                      Save
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-tabs-window-item>

            <!-- ── Tab 3 : Entrepreneur Coming ───────────────────── -->
            <v-tabs-window-item value="entre_coming">
              <v-card-text class="pa-5">
                <div class="tab-section-label mb-4">
                  <v-icon size="16" color="primary" class="mr-1">mdi-account-arrow-right</v-icon>
                  <span>Entrepreneur Coming Information</span>
                </div>

                <v-form ref="formComing" @submit.prevent="submit('entre_coming')">
                  <v-row density="comfortable">
                    <v-col cols="12" sm="6">
                      <v-autocomplete
                        v-model="entreComing.site"
                        :items="sites"
                        label="Site *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-office-building"
                        :rules="[required]"
                        clearable
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="entreComing.date_coming"
                        type="date"
                        label="Date Coming *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-calendar"
                        :rules="[required]"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="entreComing.entre_name"
                        label="Entrepreneur Name *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-account"
                        :rules="[required]"
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="entreComing.phone"
                        label="Phone"
                        variant="outlined"
                        density="compact"
                        hide-details
                        prepend-inner-icon="mdi-phone"
                        type="tel"
                      />
                    </v-col>
                  </v-row>

                  <v-alert v-if="alerts.entre_coming" :type="alerts.entre_coming.type" class="mt-4" density="compact" closable
                    @click:close="alerts.entre_coming = null">
                    {{ alerts.entre_coming.message }}
                  </v-alert>

                  <div class="d-flex justify-end ga-2 mt-5">
                    <v-btn variant="text" @click="reset('entre_coming')">Reset</v-btn>
                    <v-btn color="primary" variant="flat" type="submit" :loading="loading.entre_coming"
                      prepend-icon="mdi-content-save" rounded="lg">
                      Save
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-tabs-window-item>

            <!-- ── Tab 4 : Entrepreneur Closed ───────────────────── -->
            <v-tabs-window-item value="entre_closed">
              <v-card-text class="pa-5">
                <div class="tab-section-label mb-4">
                  <v-icon size="16" color="warning" class="mr-1">mdi-account-arrow-left</v-icon>
                  <span>Entrepreneur Closed Information</span>
                </div>

                <v-form ref="formClosed" @submit.prevent="submit('entre_closed')">
                  <v-row density="comfortable">
                    <v-col cols="12" sm="6">
                      <v-autocomplete
                        v-model="entreClosed.site"
                        :items="sites"
                        label="Site *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-office-building"
                        :rules="[required]"
                        clearable
                      />
                    </v-col>
                    <v-col cols="12" sm="6">
                      <v-text-field
                        v-model="entreClosed.resign_date"
                        type="date"
                        label="Resign Date *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-calendar"
                        :rules="[required]"
                      />
                    </v-col>
                    <v-col cols="12" sm="12">
                      <v-text-field
                        v-model="entreClosed.entre_name"
                        label="Entrepreneur Name *"
                        variant="outlined"
                        density="compact"
                        hide-details="auto"
                        prepend-inner-icon="mdi-account"
                        :rules="[required]"
                      />
                    </v-col>
                  </v-row>

                  <v-alert v-if="alerts.entre_closed" :type="alerts.entre_closed.type" class="mt-4" density="compact" closable
                    @click:close="alerts.entre_closed = null">
                    {{ alerts.entre_closed.message }}
                  </v-alert>

                  <div class="d-flex justify-end ga-2 mt-5">
                    <v-btn variant="text" @click="reset('entre_closed')">Reset</v-btn>
                    <v-btn color="warning" variant="flat" type="submit" :loading="loading.entre_closed"
                      prepend-icon="mdi-content-save" rounded="lg">
                      Save
                    </v-btn>
                  </div>
                </v-form>
              </v-card-text>
            </v-tabs-window-item>

          </v-tabs-window>
        </v-card>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// ── Tabs definition ───────────────────────────────────────────────
const tabs = [
  { value: 'site_close',   label: 'Site Close',             icon: 'mdi-lock',               color: 'error'   },
  { value: 'site_open',    label: 'Site Open',              icon: 'mdi-lock-open',           color: 'success' },
  { value: 'entre_coming', label: 'Entrepreneur Coming',    icon: 'mdi-account-arrow-right', color: 'primary' },
  { value: 'entre_closed', label: 'Entrepreneur Closed',    icon: 'mdi-account-arrow-left',  color: 'warning' },
]

// ── Active tab ────────────────────────────────────────────────────
const activeTab = ref('site_close')

// ── Sites list ────────────────────────────────────────────────────
const sites = ref(['A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'C1', 'C2'])

// ── Form refs ─────────────────────────────────────────────────────
const formClose  = ref()
const formOpen   = ref()
const formComing = ref()
const formClosed = ref()

const formRefMap = {
  site_close:   formClose,
  site_open:    formOpen,
  entre_coming: formComing,
  entre_closed: formClosed,
}

// ── Form data ─────────────────────────────────────────────────────
const today = new Date().toISOString().slice(0, 10)

const siteClose = ref({ site: '', close_date: today, report_by: '', reason: '', reason_detail: '' })
const siteOpen  = ref({ site: '', open_date: today })
const entreComing = ref({ site: '', entre_name: '', phone: '', date_coming: today })
const entreClosed = ref({ site: '', entre_name: '', resign_date: today })

const dataMap = { site_close: siteClose, site_open: siteOpen, entre_coming: entreComing, entre_closed: entreClosed }

// ── API endpoints ─────────────────────────────────────────────────
const endpointMap = {
  site_close:   '/api/entrepreneur/site-close',
  site_open:    '/api/entrepreneur/site-open',
  entre_coming: '/api/entrepreneur/coming',
  entre_closed: '/api/entrepreneur/closed',
}

// ── Loading & alerts ──────────────────────────────────────────────
const loading = ref({ site_close: false, site_open: false, entre_coming: false, entre_closed: false })
const alerts  = ref({ site_close: null,  site_open: null,  entre_coming: null,  entre_closed: null  })

// ── Validation ────────────────────────────────────────────────────
const required = v => (v !== null && v !== undefined && v !== '') || 'This field is required.'

// ── Submit ────────────────────────────────────────────────────────
const submit = async (tab) => {
  const { valid } = await formRefMap[tab].value.validate()
  if (!valid) return

  loading.value[tab] = true
  alerts.value[tab]  = null

  try {
    await axios.post(endpointMap[tab], dataMap[tab].value)
    alerts.value[tab] = { type: 'success', message: 'Saved successfully!' }
    reset(tab)
  } catch (e) {
    const msg = e.response?.data?.message ?? 'Failed to save. Please try again.'
    alerts.value[tab] = { type: 'error', message: msg }
  } finally {
    loading.value[tab] = false
  }
}

// ── Reset ─────────────────────────────────────────────────────────
const reset = (tab) => {
  formRefMap[tab].value?.resetValidation()
  if (tab === 'site_close')   siteClose.value   = { site: '', close_date: today, report_by: '', reason: '', reason_detail: '' }
  if (tab === 'site_open')    siteOpen.value    = { site: '', open_date: today }
  if (tab === 'entre_coming') entreComing.value = { site: '', entre_name: '', phone: '', date_coming: today }
  if (tab === 'entre_closed') entreClosed.value = { site: '', entre_name: '', resign_date: today }
}
</script>

<style scoped>
.form-header {
  background: linear-gradient(135deg, #1565c0, #42a5f5);
}
.tab-section-label {
  display: flex;
  align-items: center;
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #1e40af;
  padding: 6px 12px;
  background: #eff6ff;
  border-left: 4px solid #2563eb;
  border-radius: 0 8px 8px 0;
}
</style>
