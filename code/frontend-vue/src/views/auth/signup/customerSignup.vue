<template>
  <div class="registration-page">
    <div class="image-section">
      <img src="/customer_couple.png" alt="Customer" height="900" />
    </div>
    <div class="form-section">
      <div class="container registration-form">
        <h2 class="form-title">Customer Registration</h2>
        <form @submit.prevent="submitForm">
          <div class="form-group mb-3">
            <label for="username" class="form-label">Username</label>
            <input
              v-model="form.username"
              type="text"
              class="form-control"
              id="username"
              required
            />
          </div>

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

          <div class="form-group mb-3">
            <label for="fullName" class="form-label">Full Name</label>
            <input
              v-model="form.fullName"
              type="text"
              class="form-control"
              id="fullName"
              required
            />
          </div>

          <div class="form-group mb-3">
            <label for="address" class="form-label">Address</label>
            <textarea
              v-model="form.address"
              type="text"
              class="form-control"
              id="address"
              required
            />
          </div>

          <div class="form-group mb-3">
            <label for="pinCode" class="form-label">Pin Code</label>
            <input
              v-model="form.pinCode"
              type="number"
              class="form-control"
              id="pinCode"
              required
            />
          </div>
          <div class="form-group mb-3">
            <label for="phone" class="form-label">Phone</label>
            <input
              v-model="form.phone"
              type="number"
              class="form-control"
              id="phone"
              required
            />
          </div>

          <div class="form-group actions mt-4">
            <button type="submit" class="btn btn-primary btn-styled">
              Register
            </button>
            <RouterLink to="/signin" class="btn btn-link">
              Already have an account? Sign In
            </RouterLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'CustomerRegistration',
  setup() {
    const form = ref({
      username: '',
      email: '',
      password: '',
      fullName: '',
      address: '',
      pinCode: '',
      phone: '',
    })

    const router = useRouter()

    const submitForm = async () => {
      try {
        const response = await axios.post(
          'http://localhost:5000/signup-customer',
          form.value,
        )

        if (response.data.success) {
          console.log('Customer registered successfully')
          router.push('/signin')
        } else {
          alert(response.data.message)
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 400) {
            if (error.response.data.message) {
              alert(`Error: ${error.response.data.message}`)
            } else {
              alert('All fields are required.')
            }
          } else if (error.response.status === 409) {
            alert('Username or email already exists. Please try another.')
          } else if (error.response.status === 500) {
            alert(
              `Registration failed: ${error.response.data.message || 'Please try again later.'}`,
            )
          } else {
            alert('An unexpected error occurred. Please try again later.')
          }
          console.error('Error response:', error.response)
        } else if (error.request) {
          alert(
            'No response from server. Please check your connection and try again.',
          )
          console.error('Error request:', error.request)
        } else {
          alert('An error occurred: ' + error.message)
          console.error('Error message:', error.message)
        }
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
.registration-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  background-color: #f2f2f2;
}
.image-section {
  width: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.form-section {
  width: 50%;
  padding: 0 100px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.registration-form {
  font-size: 20px;
}
.form-title {
  width: 100%;
  text-align: center;
  margin: 30px 0;
}

.btn-styled {
  width: 50%;
}

.actions {
  width: 100%;
  justify-self: center;
  align-items: center;
  display: flex;
  flex-direction: column;
}
</style>
