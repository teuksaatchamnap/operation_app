<template>
  <v-container fluid class="pa-2">
    <!-- Loading State -->
    <v-row v-if="loading" justify="center" align="center" style="height: 300px;">
      <v-col cols="12" class="text-center">
        <v-progress-circular
          indeterminate
          color="primary"
          size="48"
        ></v-progress-circular>
        <p class="mt-3 text-body-2">Loading invoices data...</p>
      </v-col>
    </v-row>

    <!-- Error State -->
    <v-row v-else-if="error">
      <v-col cols="12">
        <v-alert type="error" dense dismissible @input="clearError">
          {{ error }}
        </v-alert>
      </v-col>
    </v-row>

    <!-- Main Content -->
    <div v-else>
      <!-- Header -->
      <v-row class="mb-3">
        <v-col cols="12">
          <h1 class="text-h4 font-weight-bold primary--text mb-1">Platform Invoices Dashboard</h1>
        </v-col>
      </v-row>

      <!-- Main Table Container -->
      <v-card elevation="2" class="pa-2">
        <!-- Table Header - Platform Names -->
        <div class="d-flex mb-1">
          <div class="first-column d-flex align-center pl-1">
            <span class="text-subtitle-2 font-weight-bold primary--text">Platform</span>
          </div>
          <div class="platforms-header flex-grow-1">
            <div class="d-flex justify-space-between">
              <div 
                v-for="platform in uniquePlatforms" 
                :key="platform"
                class="platform-header"
              >
                <div class="text-center">
                  <v-chip 
                    color="primary" 
                    dark 
                    x-small
                    class="px-1 py-0"
                    label
                  >
                    {{ platform }}
                  </v-chip>
                  <div class="text-caption mt-1 text--secondary">
                    {{ getSiteCountByPlatform(platform) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <v-divider class="mb-1"></v-divider>

        <!-- Invoice Rows -->
        <div v-for="(row, rowIndex) in tableRows" :key="rowIndex">
          <div class="d-flex align-start py-2 invoice-row">
            <div class="first-column d-flex align-center pl-1">
              <v-icon left :color="row.color" size="18">{{ row.icon }}</v-icon>
              <div>
                <span class="text-body-2 font-weight-medium" :class="`${row.color}--text`">{{ row.label }}</span>
              </div>
            </div>
            
            <!-- Platform Columns -->
            <div class="platforms-container flex-grow-1">
              <div class="d-flex justify-space-between">
                <div 
                  v-for="platform in uniquePlatforms" 
                  :key="`${platform}-${row.type}`"
                  class="platform-column"
                >
                  <div class="d-flex flex-wrap justify-center">
                    <!-- Display content based on row type -->
                    <template v-if="row.type === 'pending'">
                      <!-- Pending: Show circles -->
                      <div 
                        v-for="site in getSitesByPlatformAndStatus(platform, 'pending')" 
                        :key="site.Id_Site"
                        class="ma-1"
                      >
                        <v-tooltip bottom>
                          <template v-slot:activator="{ on, attrs }">
                            <div 
                              class="site-circle"
                              :class="getPendingCountClass(site)"
                              v-bind="attrs"
                              v-on="on"
                              @click="viewSiteDetails(site)"
                            >
                              <span class="site-id">{{ site.Id_Site }}</span>

                              <!-- Show pending count badge if needed -->
                              <!-- <div v-if="site.pending_count > 0" class="pending-badge">
                                {{ site.pending_count }}
                              </div> -->
                            </div>
                          </template>
                          <span class="tooltip-content">
                            <strong>Site ID:</strong> {{ site.Id_Site }}<br>
                            <strong>Platform:</strong> {{ site.Platform }}<br>
                            <strong>Advisor:</strong> {{ site.Advisor }}<br>
                            <strong>Pending:</strong> {{ site.pending_count || 0 }}<br>
                            <strong>Total:</strong> {{ site.total_invoices || 0 }}
                          </span>
                        </v-tooltip>
                      </div>
                      
                      <div 
                        v-if="getSitesByPlatformAndStatus(platform, 'pending').length === 0"
                        class="empty-state"
                      >
                        <p class="text-caption text--secondary">-</p>
                      </div>
                    </template>
                    
                    <template v-else>
                      <!-- Sent/Paid: Show chips -->
                      <div class="d-flex flex-wrap justify-center">
                        <v-chip
                          v-for="site in getSitesByPlatformAndStatus(platform, row.type)" 
                          :key="site.Id_Site"
                          :color="row.color"
                          dark
                          x-small
                          class="ma-1"
                          @click="viewSiteStatusDetails(site, row.type)"
                        >
                          {{ site.Id_Site }}
                        </v-chip>
                        
                        <div 
                          v-if="getSitesByPlatformAndStatus(platform, row.type).length === 0"
                          class="text-caption text--secondary empty-state"
                        >
                          -
                        </div>
                      </div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <v-divider v-if="rowIndex < tableRows.length - 1" class="my-1"></v-divider>
        </div>
      </v-card>

      <!-- Statistics -->
      <div class="d-flex mt-3" style="gap: 8px;">
        <div class="flex-grow-1">
          <v-card color="blue-grey lighten-5" elevation="1" class="pa-1 text-center">
            <div class="text-h6 font-weight-bold primary--text">{{ totalSites }}</div>
            <div class="text-caption primary--text">Total Sites</div>
          </v-card>
        </div>
        <div class="flex-grow-1">
          <v-card color="orange lighten-5" elevation="1" class="pa-1 text-center">
            <div class="text-h6 font-weight-bold orange--text">{{ totalPendingInvoices }}</div>
            <div class="text-caption orange--text">Pending</div>
          </v-card>
        </div>
        <div class="flex-grow-1">
          <v-card color="green lighten-5" elevation="1" class="pa-1 text-center">
            <div class="text-h6 font-weight-bold green--text">{{ totalAllInvoices }}</div>
            <div class="text-caption green--text">Total Invoices</div>
          </v-card>
        </div>
      </div>

      <!-- Site Details Dialog -->
      <v-dialog v-model="showSiteDialog" max-width="500px">
        <v-card v-if="selectedSite">
          <v-card-title class="py-2 px-3 primary white--text">
            <div class="d-flex align-center">
              <div class="site-circle-dialog mr-2" :class="getPendingCountClass(selectedSite)">
                {{ selectedSite.Id_Site }}
              </div>
              <div>
                <div class="text-subtitle-1">{{ selectedSite.Platform }}</div>
                <div class="text-caption">{{ selectedSite.Advisor }}</div>
              </div>
            </div>
          </v-card-title>
          
          <v-card-text class="pa-2">
            <v-list dense class="py-0">
              <v-list-item class="px-0">
                <v-list-item-icon class="mr-2" style="min-width: 24px;">
                  <v-icon size="16" color="primary">mdi-identifier</v-icon>
                </v-list-item-icon>
                <v-list-item-content class="py-0">
                  <v-list-item-title class="text-caption font-weight-bold">Site ID</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ selectedSite.Id_Site }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              
              <v-list-item class="px-0">
                <v-list-item-icon class="mr-2" style="min-width: 24px;">
                  <v-icon size="16" color="primary">mdi-file-document-multiple</v-icon>
                </v-list-item-icon>
                <v-list-item-content class="py-0">
                  <v-list-item-title class="text-caption font-weight-bold">Total Invoices</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ selectedSite.total_invoices }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              
              <v-list-item v-if="selectedSite.pending_count > 0" class="px-0">
                <v-list-item-icon class="mr-2" style="min-width: 24px;">
                  <v-icon size="16" color="orange">mdi-alert-circle</v-icon>
                </v-list-item-icon>
                <v-list-item-content class="py-0">
                  <v-list-item-title class="text-caption font-weight-bold orange--text">Pending Invoices</v-list-item-title>
                  <v-list-item-subtitle class="text-body-2">{{ selectedSite.pending_count }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            
            <!-- Invoice Details -->
            <v-card v-if="selectedSite.invoices && selectedSite.invoices.length > 0" 
                    class="mt-2" 
                    flat
                    color="grey lighten-5">
              <v-card-title class="py-1 px-2 text-subtitle-2 font-weight-bold">
                <v-icon left size="16">mdi-file-document</v-icon>
                Invoice Details
              </v-card-title>
              <v-card-text class="py-0 px-2">
                <v-simple-table dense>
                  <template v-slot:default>
                    <thead>
                      <tr>
                        <th class="text-caption font-weight-bold">Type</th>
                        <th class="text-caption font-weight-bold">Status</th>
                        <th class="text-caption font-weight-bold">Amount</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="invoice in selectedSite.invoices.slice(0, 3)" :key="invoice.id">
                        <td class="text-caption">{{ invoice.invoice_type }}</td>
                        <td>
                          <v-chip :color="getStatusColor(invoice.status)" dark x-small>
                            {{ invoice.status }}
                          </v-chip>
                        </td>
                        <td class="text-caption font-weight-bold">
                          ${{ formatCurrency(invoice.beginning_balance) }}
                        </td>
                      </tr>
                      <tr v-if="selectedSite.invoices.length > 3">
                        <td colspan="3" class="text-center text-caption text--secondary py-1">
                          +{{ selectedSite.invoices.length - 3 }} more
                        </td>
                      </tr>
                    </tbody>
                  </template>
                </v-simple-table>
              </v-card-text>
            </v-card>
          </v-card-text>
          
          <v-card-actions class="pa-2">
            <v-spacer></v-spacer>
            <v-btn color="primary" text x-small @click="showSiteDialog = false">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PlatformInvoicesTable',
  
  data() {
    return {
      sites: [],
      loading: true,
      error: null,
      showSiteDialog: false,
      selectedSite: null,
      tableRows: [
        { 
          type: 'pending', 
          label: 'Invoice (Pending)', 
          icon: 'mdi-alert-circle',
          color: 'black'
        },
        { 
          type: 'sent', 
          label: 'Invoice (Sent)', 
          icon: 'mdi-send',
          color: 'teal'
        },
        { 
          type: 'paid', 
          label: 'Invoice (Paid)', 
          icon: 'mdi-check-circle',
          color: 'green'
        }
      ],
    };
  },

  computed: {
    // Get unique platforms from all sites
    uniquePlatforms() {
      const platforms = [...new Set(this.sites.map(site => site.Platform))];
      return platforms.sort();
    },
    
    // Calculate totals
    totalSites() {
      return this.sites.length;
    },
    
    totalPendingInvoices() {
      return this.sites.reduce((total, site) => {
        return total + (site.pending_count || 0);
      }, 0);
    },
    
    totalAllInvoices() {
      return this.sites.reduce((total, site) => {
        return total + (site.total_invoices || 0);
      }, 0);
    }
  },

  mounted() {
    this.fetchSites();
  },

  methods: {
    async fetchSites() {
      try {
        this.loading = true;
        const response = await axios.get('/api/sites/grouped-invoices');
        
        if (response.data.success) {
          this.sites = response.data.data.map(site => {
            // Count invoices by status
            const invoices = Array.isArray(site.invoices) ? site.invoices : [];
            
            return {
              ...site,
              pending_count: invoices.filter(inv => inv.status === 'pending').length,
              sent_count: invoices.filter(inv => inv.status === 'sent').length,
              paid_count: invoices.filter(inv => inv.status === 'paid').length,
              invoices: invoices
            };
          });
        } else {
          this.error = 'Failed to fetch sites data';
        }
      } catch (error) {
        console.error('Error fetching sites:', error);
        this.error = 'Error loading data. Please try again.';
      } finally {
        this.loading = false;
      }
    },

    // Get sites by platform and status
    getSitesByPlatformAndStatus(platform, status) {
      return this.sites.filter(site => {
        if (site.Platform !== platform) return false;
        
        if (Array.isArray(site.invoices)) {
          return site.invoices.some(inv => inv.status === status);
        }
        return false;
      });
    },

    // Get site count for a platform
    getSiteCountByPlatform(platform) {
      return this.sites.filter(site => site.Platform === platform).length;
    },

    // Get CSS class based on pending count
    getPendingCountClass(site) {
      const count = site.pending_count || 0;
      if (count > 3) return 'site-circle-high';
      if (count > 1) return 'site-circle-medium';
      return 'site-circle-low';
    },

    // Get status color for chips
    getStatusColor(status) {
      const colors = {
        'pending': 'orange',
        'sent': 'teal',
        'paid': 'green',
        'overdue': 'red',
        'cancelled': 'grey'
      };
      return colors[status] || 'blue';
    },

    viewSiteDetails(site) {
      this.selectedSite = site;
      this.showSiteDialog = true;
    },

    viewSiteStatusDetails(site, status) {
      this.selectedSite = site;
      this.showSiteDialog = true;
    },

    formatCurrency(amount) {
      if (!amount) return '0.00';
      const num = parseFloat(amount);
      return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    },

    clearError() {
      this.error = null;
    }
  }
};
</script>

<style scoped>
/* Custom layout without Vuetify grid */
.d-flex {
  display: flex;
}

.align-center {
  align-items: center;
}

.align-start {
  align-items: flex-start;
}

.justify-space-between {
  justify-content: space-between;
}

.justify-center {
  justify-content: center;
}

.flex-grow-1 {
  flex-grow: 1;
}

.flex-wrap {
  flex-wrap: wrap;
}

/* 20% for first column, 80% for platform columns */
.first-column {
  width: 20%;
  min-width: 120px;
  flex-shrink: 0;
}

.platforms-header,
.platforms-container {
  width: 80%;
  flex-grow: 1;
}

/* Platform headers and columns - distributed evenly */
.platform-header {
  flex: 1;
  min-width: 0; /* Allow shrinking below content size */
}

.platform-column {
  flex: 1;
  min-width: 0; /* Allow shrinking below content size */
  padding: 0 4px;
}

/* Compact layout */
.invoice-row {
  min-height: 70px;
}

/* Compact Site Circles */
.site-circle {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 9px;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  position: relative;
  flex-shrink: 0;
}

.site-circle:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0,0,0,0.15);
}

.site-id {
  font-size: 8px;
  line-height: 1;
}

.site-circle-low {
  /* background: linear-gradient(135deg, #f0edea, #b4b3b0); */
  background: linear-gradient(135deg, #d6d4d3, #c2c0bf);
}

.site-circle-medium {
  background: linear-gradient(135deg, #e7e5e4, #e4e0df);
}

.site-circle-high {
  background: linear-gradient(135deg, #e9e6e6, #f5f1f1);
}

/* Smaller pending badge */
.pending-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background: #ff4444;
  color: white;
  border-radius: 50%;
  width: 12px;
  height: 12px;
  font-size: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  border: 1.5px solid white;
}

/* Dialog circle */
.site-circle-dialog {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Empty state */
.empty-state {
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

/* Make chips smaller */
.v-chip {
  height: 20px !important;
  font-size: 9px !important;
  min-width: 24px;
  padding: 0 4px;
  flex-shrink: 0;
}

/* Ensure content fits properly */
.platform-column > .d-flex {
  width: 100%;
  min-height: 50px;
}

/* Platform header adjustments */
.platform-header .text-center {
  width: 100%;
}

/* Remove extra margins and padding */
.ma-1 {
  margin: 2px !important;
}

/* Make sure platform columns use all available space */
.platforms-header .d-flex,
.platforms-container .d-flex {
  width: 100%;
}

/* Ensure last platform touches the right edge */
.platforms-container .d-flex > :last-child {
  padding-right: 0;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .first-column {
    width: 25%;
    min-width: 100px;
  }
  
  .platforms-header,
  .platforms-container {
    width: 75%;
  }
  
  .site-circle {
    width: 22px;
    height: 22px;
    font-size: 8px;
  }
  
  .pending-badge {
    width: 10px;
    height: 10px;
    font-size: 6px;
  }
  
  .v-chip {
    height: 18px !important;
    font-size: 8px !important;
    margin: 1px !important;
  }
  
  .platform-column {
    padding: 0 3px;
  }
}

@media (max-width: 600px) {
  .first-column {
    width: 30%;
    min-width: 80px;
  }
  
  .platforms-header,
  .platforms-container {
    width: 70%;
  }
  
  .site-circle {
    width: 20px;
    height: 20px;
    font-size: 7px;
  }
  
  .v-chip {
    height: 16px !important;
    font-size: 7px !important;
    margin: 1px !important;
  }
  
  .platform-column {
    padding: 0 2px;
  }
}

/* Force equal distribution */
.platform-header,
.platform-column {
  flex-basis: 0; /* Start from 0 basis for equal distribution */
}
</style>