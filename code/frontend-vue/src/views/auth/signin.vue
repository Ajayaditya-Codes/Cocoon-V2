<template>
  <div class="signin-page">
    <div class="signin-container">
      <h2 class="signin-title">Welcome Back to Cocoon!</h2>
      <form @submit.prevent="submitForm">
        <div class="form-group mb-3">
          <label for="email" class="form-label">Email</label>
          <input
            v-model="form.email"
            type="email"
            class="form-control"
            id="email"
            required
          />
        </div>

        <div class="form-group mb-3">
          <label for="password" class="form-label">Password</label>
          <input
            v-model="form.password"
            type="password"
            class="form-control"
            id="password"
            required
          />
        </div>

        <div class="form-group">
          <button type="submit" class="btn btn-primary w-100">Sign In</button>
        </div>
        <RouterLink to="/signup" class="btn btn-link w-100 mt-3"
          >Don't have an account? Sign Up</RouterLink
        >
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'SignIn',

  setup() {
    const form = ref({
      email: '',
      password: '',
    })

    const router = useRouter()

    const submitForm = async () => {
      try {
        const res = await axios.post(
          'http://localhost:5000/login',
          form.value,
          {
            withCredentials: true,
          },
        )
        if (res.data.user === 'admin') {
          router.push('/admin-dashboard')
        } else if (res.data.user === 'customer') {
          router.push('/customer-dashboard')
        } else if (res.data.user === 'professional') {
          router.push('/professional-dashboard')
        }
      } catch (error) {
        if (error.response) {
          const status = error.response.status
          const message = error.response.data.message || 'An error occurred.'

          if (status === 400) {
            alert('Please provide both email and password.')
          } else if (status === 401) {
            alert('Invalid email or password. Please try again.')
          } else if (status === 500) {
            alert('A server error occurred. Please try again later.')
          } else if (status === 403) {
            alert('Your account has been blocked. Please contact support.')
          } else {
            alert(`Unexpected error: ${message}`)
          }
        } else if (error.request) {
          alert(
            'No response from the server. Please check your network connection and try again.',
          )
        } else {
          alert(`An error occurred: ${error.message}`)
        }
        console.error('Error:', error)
      }
    }

    return {
      form,
      submitForm,
    }
  },
}
</script>

<style scoped>
.signin-page {
  display: flex;
  background-image: url('signin.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh;
  width: 100vw;
  position: relative;
  justify-content: center;
  align-items: center;
}

.signin-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: white;
  box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
}

.signin-title {
  text-align: center;
  margin-bottom: 20px;
}
</style>
