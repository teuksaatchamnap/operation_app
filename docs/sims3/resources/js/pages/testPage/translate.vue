<template>
  <v-container>
    <v-card>
      <v-card-title>Permissions Tree</v-card-title>
      <v-card-text>
        <v-list density="compact" nav v-model:opened="opened">
          <v-list-group v-for="(permissions, app) in groupedPermissions" :key="app" :value="app"
            :append-icon="opened.includes(app) ? 'mdi-minus' : 'mdi-plus'" no-action>
            <!-- App Name -->
            <template #activator>
              <v-list-item @click.stop="toggle(app)">
                <v-list-item-icon>
                  <v-icon>mdi-application</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ app }}</v-list-item-title>
              </v-list-item>
            </template>

            <!-- Child Permissions -->
            <v-list-item v-for="perm in permissions" :key="perm.name" class="pl-8">
              <v-checkbox v-model="selectedUser.permissions" :label="perm.name" :value="perm.name" density="compact"
                hide-details />
            </v-list-item>
          </v-list-group>
        </v-list>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      allPermissions: [],          // fetched from Laravel
      selectedUser: { permissions: [] },
      opened: [],                  // controls which app is expanded
    };
  },
  computed: {
    groupedPermissions() {
      return this.allPermissions.reduce((acc, p) => {
        const app = p.app_name ?? 'Unknown';
        if (!acc[app]) acc[app] = [];
        acc[app].push(p);           // no change needed, p.name exists
        return acc;
      }, {});
    },
  },
  mounted() {
    this.loadPermissions();
  },
  methods: {
    loadPermissions() {
      window.axios.get('/api/allPermissions')
        .then(response => {
          this.allPermissions = response.data;
        })
        .catch(err => console.error('Error loading permissions', err));
    },
    toggle(app) {
      // only one app opens at a time
      this.opened = this.opened.includes(app) ? [] : [app];
    },
  },
};
</script>
