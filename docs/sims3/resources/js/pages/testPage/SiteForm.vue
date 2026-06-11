<template>
  <div class="form-wrapper">
    <!-- Header -->
    <div class="form-header">
      <div class="header-inner">
        <div class="brand">
          <div class="brand-drop">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
              <path d="M12 2C8.5 7 5 10.5 5 14a7 7 0 0014 0c0-3.5-3.5-7-7-12z"/>
            </svg>
          </div>
          <span class="brand-label">Teuk Saat 1001</span>
        </div>
        <h1>New Site Registration</h1>
        <p>Complete all sections to register a new water kiosk location</p>
      </div>
    </div>

    <!-- Step bar -->
    <div class="steps-bar">
      <button
        v-for="(section, i) in sections"
        :key="i"
        class="step-btn"
        :class="{ active: currentStep === i, done: i < currentStep }"
        @click="goTo(i)"
      >
        <span class="step-num">
          <svg v-if="i < currentStep" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
          <span v-else>{{ i + 1 }}</span>
        </span>
        {{ section.label }}
      </button>
    </div>
    <div class="progress-track">
      <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
    </div>

    <!-- Form body -->
    <form @submit.prevent="handleSubmit" novalidate>
      <div class="section-body">

        <!-- ── SECTION 0: ID ── -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 0" key="s0">
            <div class="section-title">
              <span class="section-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><line x1="7" y1="10" x2="17" y2="10"/><line x1="7" y1="14" x2="13" y2="14"/></svg>
              </span>
              Site Identification
            </div>
            <div class="grid-2">
              <div class="field">
                <label>Site Code <span class="req">*</span></label>
                <input v-model="form.site_code" type="text" placeholder="e.g. BB-024" :class="{ 'is-error': errors.site_code }" />
                <span v-if="errors.site_code" class="field-error">{{ errors.site_code }}</span>
              </div>
              <div class="field">
                <label>Platform <span class="req">*</span></label>
                <select v-model="form.platform" :class="{ 'is-error': errors.platform }">
                  <option value="" disabled>Select platform...</option>
                  <option v-for="p in options.platforms" :key="p">{{ p }}</option>
                </select>
                <span v-if="errors.platform" class="field-error">{{ errors.platform }}</span>
              </div>
              <div class="field">
                <label>Technician</label>
                <select v-model="form.technician">
                  <option value="" disabled>Assign technician...</option>
                  <option v-for="t in options.technicians" :key="t">{{ t }}</option>
                </select>
              </div>
              <div class="field">
                <label>Advisor</label>
                <select v-model="form.advisor">
                  <option value="" disabled>Assign advisor...</option>
                  <option v-for="a in options.advisors" :key="a">{{ a }}</option>
                </select>
              </div>
            </div>
          </div>
        </transition>

        <!-- ── SECTION 1: ADDRESS ── -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 1" key="s1">
            <div class="section-title">
              <span class="section-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/><circle cx="12" cy="9" r="2.5"/></svg>
              </span>
              Address Information
            </div>

            <div class="subsection-label">Village</div>
            <div class="grid-3 mb-3">
              <div class="field"><label>Village Code</label><input v-model="form.village_code" type="text" placeholder="V-XXX" /></div>
              <div class="field"><label>Village Name (EN)</label><input v-model="form.village_name_en" type="text" /></div>
              <div class="field"><label>Village Name (KH)</label><input v-model="form.village_name_kh" type="text" /></div>
            </div>

            <div class="subsection-label">Commune</div>
            <div class="grid-2 mb-3">
              <div class="field"><label>Commune Name (EN)</label><input v-model="form.commune_name_en" type="text" /></div>
              <div class="field"><label>Commune Name (KH)</label><input v-model="form.commune_name_kh" type="text" /></div>
            </div>

            <div class="subsection-label">District</div>
            <div class="grid-2 mb-3">
              <div class="field"><label>District Name (EN)</label><input v-model="form.district_name_en" type="text" /></div>
              <div class="field"><label>District Name (KH)</label><input v-model="form.district_name_kh" type="text" /></div>
            </div>

            <div class="subsection-label">Province</div>
            <div class="grid-3 mb-3">
              <div class="field"><label>Province Code</label><input v-model="form.province_code" type="text" /></div>
              <div class="field"><label>Province Name (EN)</label><input v-model="form.province_name_en" type="text" /></div>
              <div class="field"><label>Province Name (KH)</label><input v-model="form.province_name_kh" type="text" /></div>
            </div>

            <div class="subsection-label">Geographical Coordinates</div>
            <div class="geo-row">
              <div class="field"><label>Latitude</label><input v-model="form.latitude" type="number" step="0.0000001" placeholder="12.5657" /></div>
              <div class="field"><label>Longitude</label><input v-model="form.longitude" type="number" step="0.0000001" placeholder="104.9910" /></div>
              <button type="button" class="locate-btn" @click="autoLocate">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/></svg>
                {{ locating ? 'Locating...' : locateSuccess ? '✓ Located' : 'Auto-locate' }}
              </button>
            </div>
          </div>
        </transition>

        <!-- ── SECTION 2: PROJECT ── -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 2" key="s2">
            <div class="section-title">
              <span class="section-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
              </span>
              Project Details
            </div>
            <div class="grid-2">
              <div class="field"><label>Project Agreement Date</label><input v-model="form.project_agreement_date" type="date" /></div>
              <div class="field"><label>Wave</label><input v-model="form.wave" type="text" placeholder="e.g. Wave 3" /></div>
              <div class="field"><label>Funder 1</label><input v-model="form.funder_1" type="text" placeholder="Organization name" /></div>
              <div class="field"><label>Funder 2</label><input v-model="form.funder_2" type="text" placeholder="Organization name" /></div>
              <div class="field"><label>Funder 3</label><input v-model="form.funder_3" type="text" placeholder="Organization name" /></div>
            </div>
          </div>
        </transition>

        <!-- ── SECTION 3: DEMOGRAPHY ── -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 3" key="s3">
            <div class="section-title">
              <span class="section-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>
              </span>
              Demography
            </div>
            <div class="grid-2">
              <div class="field"><label>Number of Villages</label><input v-model.number="form.num_villages" type="number" min="0" placeholder="0" /></div>
              <div class="field"><label>Number of Families</label><input v-model.number="form.num_families" type="number" min="0" placeholder="0" /></div>
              <div class="field"><label>Population</label><input v-model.number="form.population" type="number" min="0" placeholder="0" /></div>
              <div class="field"><label>Population within 5 km</label><input v-model.number="form.population_5km" type="number" min="0" placeholder="0" /></div>
            </div>
          </div>
        </transition>

        <!-- ── SECTION 4: INFRASTRUCTURE ── -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 4" key="s4">
            <div class="section-title">
              <span class="section-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              </span>
              Infrastructure
            </div>
            <div class="grid-2 mb-3">
              <div class="field"><label>Number of Pagodas</label><input v-model.number="form.num_pagodas" type="number" min="0" placeholder="0" /></div>
              <div class="field"><label>Number of Primary Schools</label><input v-model.number="form.num_primary_schools" type="number" min="0" placeholder="0" /></div>
              <div class="field">
                <label>Land of Kiosk</label>
                <select v-model="form.land_of_kiosk">
                  <option value="" disabled>Select...</option>
                  <option v-for="l in options.landTypes" :key="l">{{ l }}</option>
                </select>
              </div>
              <div class="field">
                <label>Road Leading to Kiosk</label>
                <select v-model="form.road_leading_to_kiosk">
                  <option value="" disabled>Select...</option>
                  <option v-for="r in options.roadTypes" :key="r">{{ r }}</option>
                </select>
              </div>
            </div>

            <div class="subsection-label">Road Surface Breakdown (%)</div>
            <div class="grid-4">
              <div class="field"><label>Paved Asphalt</label><input v-model.number="form.pct_asphalt_road" type="number" min="0" max="100" placeholder="0" /></div>
              <div class="field"><label>Concrete</label><input v-model.number="form.pct_concrete_road" type="number" min="0" max="100" placeholder="0" /></div>
              <div class="field"><label>Laterite</label><input v-model.number="form.pct_laterite_road" type="number" min="0" max="100" placeholder="0" /></div>
              <div class="field"><label>White Soil</label><input v-model.number="form.pct_white_soil_road" type="number" min="0" max="100" placeholder="0" /></div>
            </div>
          </div>
        </transition>

        <!-- ── SECTION 5: TECHNICAL ── -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 5" key="s5">
            <div class="section-title">
              <span class="section-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              </span>
              Technical Details
            </div>

            <!-- Water Source 1 -->
            <div class="source-card mb-3">
              <div class="source-card-header">
                <span class="source-dot primary"></span>
                Main Water Source
              </div>
              <div class="grid-2">
                <div class="field">
                  <label>Source Type</label>
                  <select v-model="form.ws1_type">
                    <option value="" disabled>Select...</option>
                    <option v-for="w in options.waterSourceTypes" :key="w">{{ w }}</option>
                  </select>
                </div>
                <div class="field"><label>Distance to Kiosk (m)</label><input v-model.number="form.ws1_distance" type="number" min="0" placeholder="0" /></div>
              </div>
              <transition name="expand">
                <div v-if="ws1NeedsOwner" class="conditional-fields">
                  <div class="grid-2">
                    <div class="field"><label>Owner of Source</label><input v-model="form.ws1_owner" type="text" placeholder="Name or organization" /></div>
                    <div class="field"><label>Depth (m)</label><input v-model.number="form.ws1_depth" type="number" min="0" placeholder="0" /></div>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Water Source 2 -->
            <div class="source-card mb-3">
              <div class="source-card-header">
                <span class="source-dot secondary"></span>
                Second Water Source
              </div>
              <div class="grid-2">
                <div class="field">
                  <label>Source Type</label>
                  <select v-model="form.ws2_type">
                    <option value="" disabled>Select...</option>
                    <option v-for="w in options.waterSourceTypes" :key="w">{{ w }}</option>
                  </select>
                </div>
                <div class="field"><label>Distance to Kiosk (m)</label><input v-model.number="form.ws2_distance" type="number" min="0" placeholder="0" /></div>
              </div>
              <transition name="expand">
                <div v-if="ws2NeedsOwner" class="conditional-fields">
                  <div class="grid-2">
                    <div class="field"><label>Owner of Source</label><input v-model="form.ws2_owner" type="text" placeholder="Name or organization" /></div>
                    <div class="field"><label>Depth (m)</label><input v-model.number="form.ws2_depth" type="number" min="0" placeholder="0" /></div>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Power Sources -->
            <div class="subsection-label mb-2">Power Sources</div>
            <div class="grid-2 mb-3">
              <div class="field">
                <label>Main Power Source</label>
                <div class="toggle-group">
                  <button type="button" v-for="p in ['Grid','Solar']" :key="p"
                    class="toggle-pill" :class="{ active: form.main_power_source === p }"
                    @click="form.main_power_source = p">{{ p }}</button>
                </div>
              </div>
              <div class="field">
                <label>Second Power Source</label>
                <div class="toggle-group">
                  <button type="button" v-for="p in ['Grid','Solar','Absent']" :key="p"
                    class="toggle-pill" :class="{ active: form.second_power_source === p }"
                    @click="form.second_power_source = p">{{ p }}</button>
                </div>
              </div>
            </div>

            <div class="field" style="max-width:300px">
              <label>Water Tank Type</label>
              <select v-model="form.water_tank_type">
                <option value="" disabled>Select...</option>
                <option v-for="t in options.tankTypes" :key="t">{{ t }}</option>
              </select>
            </div>
          </div>
        </transition>

        <!-- ── SECTION 6: ENTREPRENEUR ── -->
        <transition name="fade-slide" mode="out-in">
          <div v-if="currentStep === 6" key="s6">
            <div class="section-title">
              <span class="section-icon">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              </span>
              Entrepreneur Profile
            </div>

            <div class="grid-2 mb-3">
              <div class="field"><label>Name (EN)</label><input v-model="form.ent_name_en" type="text" placeholder="Full name" /></div>
              <div class="field"><label>Name (KH)</label><input v-model="form.ent_name_kh" type="text" placeholder="ឈ្មោះ" /></div>
            </div>

            <div class="field mb-3">
              <label>Sex</label>
              <div class="toggle-group">
                <button type="button" v-for="s in ['Male','Female']" :key="s"
                  class="toggle-pill" :class="{ active: form.ent_sex === s }"
                  @click="form.ent_sex = s">{{ s }}</button>
              </div>
            </div>

            <div class="grid-2 mb-3">
              <div class="field"><label>Commune of Birth</label><input v-model="form.ent_commune_of_birth" type="text" /></div>
              <div class="field"><label>Province of Birth</label><input v-model="form.ent_province_of_birth" type="text" /></div>
              <div class="field"><label>Date of Birth</label><input v-model="form.ent_date_of_birth" type="date" /></div>
              <div class="field"><label>Start Work Date</label><input v-model="form.ent_start_work_date" type="date" /></div>
              <div class="field"><label>Phone Number</label><input v-model="form.ent_phone" type="tel" placeholder="0xx xxx xxx" /></div>
              <div class="field"><label>ID Number</label><input v-model="form.ent_id_number" type="text" /></div>
              <div class="field"><label>Education Background</label><input v-model="form.ent_education" type="text" /></div>
              <div class="field"><label>Previous Job</label><input v-model="form.ent_previous_job" type="text" /></div>
              <div class="field"><label>Part-time Job</label><input v-model="form.ent_part_time_job" type="text" /></div>
            </div>

            <!-- Skills -->
            <div class="subsection-label mb-2">Skill Assessment</div>
            <div class="skills-block mb-3">
              <div v-for="skill in skillFields" :key="skill.key" class="skill-row">
                <label class="skill-label">{{ skill.label }}</label>
                <div class="skill-group">
                  <button type="button" v-for="lvl in skillLevels" :key="lvl"
                    class="skill-pill" :class="{ active: form[skill.key] === lvl }"
                    @click="form[skill.key] = lvl">{{ lvl }}</button>
                </div>
              </div>
            </div>

            <div class="field mb-3">
              <label>Why working as an entrepreneur?</label>
              <textarea v-model="form.ent_why_entrepreneur" rows="4" placeholder="Briefly describe your motivation..."></textarea>
            </div>

            <!-- Submit summary box -->
            <div class="submit-hint">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <div>
                <strong>Ready to submit?</strong>
                <p>Please review all sections before submitting. Once submitted, the site will be added to the system for review.</p>
              </div>
            </div>
          </div>
        </transition>

      </div>

      <!-- Navigation footer -->
      <div class="form-footer">
        <button type="button" class="btn btn-secondary" :disabled="currentStep === 0" @click="navigate(-1)">
          ← Back
        </button>
        <span class="step-counter">Section {{ currentStep + 1 }} of {{ sections.length }}</span>
        <button
          v-if="currentStep < sections.length - 1"
          type="button"
          class="btn btn-primary"
          @click="navigate(1)"
        >Continue →</button>
        <button
          v-else
          type="submit"
          class="btn btn-primary"
          :disabled="submitting"
        >
          <span v-if="submitting" class="spinner-sm"></span>
          {{ submitting ? 'Submitting...' : 'Submit Registration' }}
        </button>
      </div>
    </form>

    <!-- Success overlay -->
    <transition name="fade">
      <div v-if="submitted" class="success-overlay">
        <div class="success-card">
          <div class="success-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <h2>Site Registered!</h2>
          <p>The site <strong>{{ form.site_code }}</strong> has been successfully registered in the system.</p>
          <button class="btn btn-primary" style="margin-top:1.5rem" @click="resetForm">Register Another Site</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

// ── Options ───────────────────────────────────────────────────────
const options = {
  platforms:        ['Battambang','Siem Reap','Kampong Speu','Phnom Penh','Kampong Cham','Kampong Chhnang'],
  technicians:      ['Dara Sok','Chanthy Pich','Mony Chea','Sovann Rath','Bopha Keo'],
  advisors:         ['Ratha Lim','Sreymom Heng','Virak Chan','Kosal Noun','Phally Tep'],
  landTypes:        ['Commune Land','Community Land','School Land','Pagoda Land','District Land','Health Center Land','Private Land'],
  roadTypes:        ['Paved Asphalt Road','White Soiled Road','Concrete Road','Laterite Road'],
  waterSourceTypes: ['Pond','Well','Pipe','River'],
  tankTypes:        ['Concrete','Plastic','FRP','600+','Kiosk 2.0'],
}

const skillLevels = ['No ability','Basic','Intermediate','Proficient','Advanced']
const skillFields = [
  { key: 'ent_reading_skill',     label: 'Reading Skills' },
  { key: 'ent_writing_skill',     label: 'Writing Skills' },
  { key: 'ent_calculation_skill', label: 'Calculation Skills' },
]

const sections = [
  { label: 'ID' },
  { label: 'Address' },
  { label: 'Project' },
  { label: 'Demography' },
  { label: 'Infrastructure' },
  { label: 'Technical' },
  { label: 'Entrepreneur' },
]

// ── State ─────────────────────────────────────────────────────────
const currentStep   = ref(0)
const submitting    = ref(false)
const submitted     = ref(false)
const locating      = ref(false)
const locateSuccess = ref(false)
const errors        = reactive({})

const form = reactive({
  // ID
  site_code: '', platform: '', technician: '', advisor: '',
  // Village
  village_code: '', village_name_en: '', village_name_kh: '',
  // Commune
  commune_name_en: '', commune_name_kh: '',
  // District
  district_name_en: '', district_name_kh: '',
  // Province
  province_code: '', province_name_en: '', province_name_kh: '',
  // Geo
  latitude: '', longitude: '',
  // Project
  project_agreement_date: '', wave: '', funder_1: '', funder_2: '', funder_3: '',
  // Demography
  num_villages: '', num_families: '', population: '', population_5km: '',
  // Infrastructure
  num_pagodas: '', num_primary_schools: '', land_of_kiosk: '', road_leading_to_kiosk: '',
  pct_asphalt_road: '', pct_concrete_road: '', pct_laterite_road: '', pct_white_soil_road: '',
  // Technical
  ws1_type: '', ws1_owner: '', ws1_depth: '', ws1_distance: '',
  ws2_type: '', ws2_owner: '', ws2_depth: '', ws2_distance: '',
  main_power_source: '', second_power_source: '', water_tank_type: '',
  // Entrepreneur
  ent_name_en: '', ent_name_kh: '', ent_sex: '',
  ent_commune_of_birth: '', ent_province_of_birth: '',
  ent_date_of_birth: '', ent_start_work_date: '',
  ent_phone: '', ent_id_number: '', ent_education: '',
  ent_previous_job: '', ent_part_time_job: '',
  ent_reading_skill: '', ent_writing_skill: '', ent_calculation_skill: '',
  ent_why_entrepreneur: '',
})

// ── Computed ──────────────────────────────────────────────────────
const progressPct    = computed(() => ((currentStep.value + 1) / sections.length) * 100)
const ws1NeedsOwner  = computed(() => ['Well','Pond'].includes(form.ws1_type))
const ws2NeedsOwner  = computed(() => ['Well','Pond'].includes(form.ws2_type))

// ── Methods ───────────────────────────────────────────────────────
function validate() {
  Object.keys(errors).forEach(k => delete errors[k])
  if (!form.site_code.trim()) errors.site_code = 'Site code is required.'
  if (!form.platform)         errors.platform  = 'Platform is required.'
  return Object.keys(errors).length === 0
}

function navigate(dir) {
  if (dir === 1 && currentStep.value === 0 && !validate()) return
  const next = currentStep.value + dir
  if (next >= 0 && next < sections.length) currentStep.value = next
}

function goTo(i) {
  if (i === 0 || i <= currentStep.value + 1) currentStep.value = i
}

async function autoLocate() {
  if (!navigator.geolocation) return
  locating.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      form.latitude  = pos.coords.latitude.toFixed(7)
      form.longitude = pos.coords.longitude.toFixed(7)
      locating.value = false
      locateSuccess.value = true
      setTimeout(() => { locateSuccess.value = false }, 3000)
    },
    () => { locating.value = false },
  )
}

async function handleSubmit() {
  if (!validate()) { currentStep.value = 0; return }
  submitting.value = true
  try {
    // Replace with: await siteApi.create(form)
    await new Promise(r => setTimeout(r, 1200))
    submitted.value = true
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  submitted.value = false
  currentStep.value = 0
  Object.keys(form).forEach(k => { form[k] = '' })
}
</script>

<style scoped>
/* ── Layout ────────────────────────────────────────────────────── */
.form-wrapper {
  max-width: 780px;
  margin: 2rem auto;
  background: #fff;
  border-radius: 16px;
  border: 1px solid #E8E6DF;
  overflow: hidden;
  position: relative;
  font-family: 'DM Sans', system-ui, sans-serif;
  box-shadow: 0 4px 32px rgba(4,52,44,0.07);
}

/* ── Header ────────────────────────────────────────────────────── */
.form-header {
  background: linear-gradient(135deg, #085041 0%, #0F6E56 100%);
  padding: 2rem 2rem 1.75rem;
  position: relative;
  overflow: hidden;
}
.form-header::before {
  content: '';
  position: absolute;
  top: -40px; right: -40px;
  width: 160px; height: 160px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
}
.form-header::after {
  content: '';
  position: absolute;
  bottom: -30px; right: 80px;
  width: 90px; height: 90px;
  border-radius: 50%;
  background: rgba(255,255,255,0.04);
}
.header-inner { position: relative; z-index: 1; }
.brand { display: flex; align-items: center; gap: 9px; margin-bottom: 12px; }
.brand-drop {
  width: 34px; height: 34px;
  background: rgba(255,255,255,0.18);
  border-radius: 50% 50% 50% 10%;
  display: flex; align-items: center; justify-content: center;
}
.brand-label { font-size: 11px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(255,255,255,0.8); }
.form-header h1 { font-family: 'Playfair Display', Georgia, serif; font-size: 22px; font-weight: 500; color: #fff; margin-bottom: 4px; }
.form-header p  { font-size: 13px; color: rgba(255,255,255,0.65); font-weight: 300; }

/* ── Steps bar ─────────────────────────────────────────────────── */
.steps-bar {
  display: flex;
  background: #F8F7F3;
  border-bottom: 1px solid #EEECE6;
  padding: 0 1.5rem;
  overflow-x: auto;
  scrollbar-width: none;
}
.steps-bar::-webkit-scrollbar { display: none; }

.step-btn {
  display: flex; align-items: center; gap: 7px;
  flex-shrink: 0;
  padding: 13px 11px;
  font-size: 12.5px;
  font-weight: 400;
  color: #888780;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s, border-color 0.15s;
  font-family: 'DM Sans', sans-serif;
}
.step-btn:hover { color: #2C2C2A; }
.step-btn.active { color: #0F6E56; border-bottom-color: #0F6E56; font-weight: 500; }
.step-btn.done   { color: #1D9E75; }

.step-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px;
  border-radius: 50%;
  font-size: 10px; font-weight: 700;
  background: #E8E6DF;
  color: #888780;
  transition: all 0.15s;
  flex-shrink: 0;
}
.step-btn.active .step-num { background: #0F6E56; color: #fff; }
.step-btn.done   .step-num { background: #9FE1CB; color: #085041; }

.progress-track { height: 3px; background: #EEECE6; }
.progress-fill  { height: 100%; background: #5DCAA5; transition: width 0.35s ease; }

/* ── Section body ──────────────────────────────────────────────── */
.section-body { padding: 2rem 2rem 1rem; min-height: 340px; }

.section-title {
  display: flex; align-items: center; gap: 9px;
  font-family: 'Playfair Display', Georgia, serif;
  font-size: 17px; font-weight: 500;
  color: #2C2C2A;
  margin-bottom: 1.5rem;
  padding-bottom: 12px;
  border-bottom: 1px solid #EEECE6;
}
.section-icon {
  width: 30px; height: 30px;
  background: #E1F5EE;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  color: #0F6E56;
  flex-shrink: 0;
}

.subsection-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: #888780;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #EEECE6;
}

/* ── Grids ─────────────────────────────────────────────────────── */
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }

.mb-2 { margin-bottom: 1rem; }
.mb-3 { margin-bottom: 1.5rem; }

/* ── Field ─────────────────────────────────────────────────────── */
.field { display: flex; flex-direction: column; }
.field label {
  font-size: 12px; font-weight: 500;
  color: #5F5E5A;
  margin-bottom: 5px;
}
.field label .req { color: #E24B4A; margin-left: 2px; }
.field-error { font-size: 11px; color: #E24B4A; margin-top: 4px; }

input, select, textarea {
  width: 100%;
  font-family: 'DM Sans', sans-serif;
  font-size: 13.5px;
  color: #2C2C2A;
  background: #fff;
  border: 1px solid #D3D1C7;
  border-radius: 8px;
  padding: 0 11px;
  height: 38px;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  appearance: none;
}
input:focus, select:focus, textarea:focus {
  border-color: #1D9E75;
  box-shadow: 0 0 0 3px rgba(29,158,117,0.12);
}
input.is-error, select.is-error { border-color: #E24B4A; }
input::placeholder { color: #B4B2A9; }
textarea { height: auto; padding: 10px 11px; resize: vertical; }
select {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: right 11px center; padding-right: 30px; cursor: pointer;
}

/* ── Geo row ────────────────────────────────────────────────────── */
.geo-row { display: grid; grid-template-columns: 1fr 1fr auto; gap: 12px; align-items: end; }
.locate-btn {
  height: 38px; padding: 0 14px;
  display: flex; align-items: center; gap: 6px;
  font-size: 12.5px; font-weight: 500;
  font-family: 'DM Sans', sans-serif;
  color: #085041;
  background: #E1F5EE;
  border: 1px solid #9FE1CB;
  border-radius: 8px;
  cursor: pointer; white-space: nowrap;
  transition: background 0.15s;
}
.locate-btn:hover { background: #9FE1CB; }

/* ── Toggles ────────────────────────────────────────────────────── */
.toggle-group { display: flex; gap: 7px; flex-wrap: wrap; margin-top: 2px; }
.toggle-pill {
  padding: 7px 16px;
  font-size: 13px; font-family: 'DM Sans', sans-serif;
  color: #5F5E5A;
  background: #fff;
  border: 1px solid #D3D1C7;
  border-radius: 99px;
  cursor: pointer; transition: all 0.15s;
}
.toggle-pill:hover { border-color: #5DCAA5; color: #0F6E56; }
.toggle-pill.active { background: #0F6E56; border-color: #0F6E56; color: #fff; font-weight: 500; }

/* ── Source cards ──────────────────────────────────────────────── */
.source-card {
  border: 1px solid #EEECE6;
  border-radius: 12px;
  padding: 1.25rem;
  background: #FAFAF8;
}
.source-card-header {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 600; color: #2C2C2A;
  margin-bottom: 12px;
}
.source-dot { width: 9px; height: 9px; border-radius: 50%; }
.source-dot.primary   { background: #5DCAA5; }
.source-dot.secondary { background: #D3D1C7; }

.conditional-fields {
  margin-top: 12px;
  padding: 12px;
  background: #fff;
  border: 1px solid #EEECE6;
  border-radius: 8px;
}

/* ── Skills ─────────────────────────────────────────────────────── */
.skills-block { display: flex; flex-direction: column; gap: 12px; }
.skill-row { display: flex; align-items: center; gap: 12px; }
.skill-label { font-size: 12px; font-weight: 500; color: #5F5E5A; min-width: 130px; flex-shrink: 0; }
.skill-group { display: flex; gap: 5px; flex: 1; }
.skill-pill {
  flex: 1; padding: 6px 4px;
  font-size: 11.5px; font-family: 'DM Sans', sans-serif;
  text-align: center;
  color: #5F5E5A;
  background: #fff;
  border: 1px solid #D3D1C7;
  border-radius: 6px;
  cursor: pointer; transition: all 0.15s;
}
.skill-pill:hover { border-color: #5DCAA5; color: #0F6E56; }
.skill-pill.active { background: #0F6E56; border-color: #0F6E56; color: #fff; font-weight: 500; }

/* ── Submit hint ────────────────────────────────────────────────── */
.submit-hint {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 1rem 1.25rem;
  background: #E1F5EE;
  border: 1px solid #9FE1CB;
  border-radius: 12px;
  color: #0F6E56;
}
.submit-hint strong { display: block; font-size: 13px; font-weight: 600; margin-bottom: 3px; }
.submit-hint p { font-size: 12px; color: #085041; margin: 0; }
.submit-hint svg { flex-shrink: 0; margin-top: 2px; }

/* ── Footer ─────────────────────────────────────────────────────── */
.form-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 2rem;
  border-top: 1px solid #EEECE6;
  background: #F8F7F3;
}
.step-counter { font-size: 12px; color: #888780; }

.btn {
  display: inline-flex; align-items: center; gap: 7px;
  height: 38px; padding: 0 20px;
  font-family: 'DM Sans', sans-serif; font-size: 13.5px; font-weight: 500;
  border-radius: 8px; border: 1px solid transparent;
  cursor: pointer; transition: all 0.15s; white-space: nowrap;
}
.btn:active { transform: scale(0.98); }
.btn:disabled { opacity: 0.45; cursor: not-allowed; }
.btn-primary  { background: #0F6E56; color: #fff; border-color: #0F6E56; }
.btn-primary:hover:not(:disabled) { background: #085041; border-color: #085041; }
.btn-secondary { background: #fff; color: #2C2C2A; border-color: #D3D1C7; }
.btn-secondary:hover:not(:disabled) { background: #F8F7F3; }

.spinner-sm {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Transitions ────────────────────────────────────────────────── */
.fade-slide-enter-active { transition: all 0.22s ease; }
.fade-slide-leave-active { transition: all 0.15s ease; }
.fade-slide-enter-from   { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to     { opacity: 0; transform: translateY(-6px); }

.expand-enter-active, .expand-leave-active { transition: all 0.2s ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; margin-top: 0; }
.expand-enter-to, .expand-leave-from { max-height: 200px; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── Success overlay ────────────────────────────────────────────── */
.success-overlay {
  position: absolute; inset: 0;
  background: rgba(4,52,44,0.6);
  display: flex; align-items: center; justify-content: center;
  z-index: 100;
  backdrop-filter: blur(2px);
}
.success-card {
  background: #fff;
  border-radius: 16px;
  padding: 2.5rem 2rem;
  text-align: center;
  max-width: 360px;
  width: 90%;
}
.success-icon {
  width: 64px; height: 64px;
  background: #0F6E56;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.25rem;
}
.success-card h2 { font-family: 'Playfair Display', serif; font-size: 22px; color: #2C2C2A; margin-bottom: 8px; }
.success-card p  { font-size: 14px; color: #5F5E5A; line-height: 1.6; }
.success-card strong { color: #0F6E56; }

/* ── Responsive ─────────────────────────────────────────────────── */
@media (max-width: 640px) {
  .form-wrapper { margin: 0; border-radius: 0; }
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
  .geo-row { grid-template-columns: 1fr 1fr; }
  .geo-row .locate-btn { grid-column: 1/-1; justify-content: center; }
  .skill-row { flex-direction: column; align-items: flex-start; }
  .skill-label { min-width: unset; }
}
</style>
