<template>
  <div
    class="d-flex flex-column justify-content-center align-items-center vh-100 bg-light"
  >
    <b-container class="text-center">
      <b-row>
        <b-col>
          <h1 class="display-1 text-danger">404</h1>
          <h2 class="mb-4">Page Not Found</h2>
          <p class="lead">
            Oops! The page you are looking for does not exist. It might have
            been moved or deleted.
          </p>
          <b-button class="btn btn-link" @click="goHome">Go to Home</b-button>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goHome() {
      this.$router.push('/')
    },
  },
}
</script>

<style scoped>
.vh-100 {
  height: 100vh;
}
</style>
