<template>
  <div class="login-box">
    <img src="/img/logo.png">
    <v-card
      v-if="loading"
      color="primary"
      class="mt-5"
    >
      <v-card-text>
        Please stand by
        <v-progress-linear
          indeterminate
          color="white"
          class="mb-0"
        />
      </v-card-text>
    </v-card>
    <div v-if="!loading">
      <p class="pt-4">
        Access to this application is restricted to TeukSaat employees.
      </p>
      <p>Please login using your Google @teuksaat1001.com or @1001fontaines.com account.</p>
      <GoogleLogin
        :callback="onGoogleAuthSuccess"
        prompt
      />
    </div>
  </div>
</template>
<script>
export default {
  name: 'LoginPage',

  data: function () {
    return {
      loading: true,
    }
  },
  mounted() {
    window.axios.get('/sanctum/csrf-cookie').then(() => {
      this.getAuth()
    });
  },
  methods: {
    onGoogleAuthSuccess(token) {
      token = {...token, client_id: window.googleClientId}
      window.axios.post("/api/login", { token: token }).then(() => {
        this.getAuth()
      });
    },
    getAuth() {
      window.axios.get("/api/getAuth").then(response => {
        this.$store.commit('login', response.data)
        if(this.$store.state.initialRoute) {
          this.$router.push({ path: this.$store.state.initialRoute });
        } else {
          this.$router.push({ path: '/welcome' });
        }        
      }).catch(() => this.loading = false);
    }
  }
}
</script>

<style scoped>
.login-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  margin-top: 30px;
}
</style>