<template>
  <div class="registration-page">
    <div class="image-container">
      <img src="/professional.png" alt="Professional" height="800" />
    </div>
    <div class="form-container">
      <div class="container registration-form">
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
            <label for="serviceProvided" class="form-label"
              >Service Provided</label
            >
            <select
              v-model="form.serviceProvided"
              class="form-select"
              id="serviceProvided"
              required
            >
              <option value="" disabled>Select a service</option>
              <option
                v-for="service in services"
                :key="service.id"
                :value="service.name"
              >
                {{ service.name }}
              </option>
            </select>
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
            <label for="experience" class="form-label"
              >Experience (Years)</label
            >
            <input
              v-model="form.experience"
              type="number"
              class="form-control"
              id="experience"
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
          <div class="form-group mb-3">
            <label for="link" class="form-label"
              >Documents Link (For verification)</label
            >
            <input
              v-model="form.link"
              type="text"
              class="form-control"
              id="link"
              required
            />
          </div>
          <div class="form-group group mt-4">
            <button type="submit" class="btn btn-primary btn-styled">
              Register
            </button>
            <RouterLink to="/signin" class="btn btn-link"
              >Already have an account? Sign In</RouterLink
            >
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  name: 'ProfessionalRegistration',
  setup() {
    const form = ref({
      username: '',
      email: '',
      password: '',
      fullName: '',
      serviceProvided: '',
      pinCode: '',
      experience: '',
      phone: '',
      link: '',
    })

    const router = useRouter()
    const services = ref([])

    const fetchServices = async () => {
      try {
        const response = await axios.get('http://localhost:5000/services')
        services.value = response.data
      } catch (error) {
        console.error('Error fetching services:', error)
      }
    }

    onMounted(() => {
      fetchServices()
    })

    const submitForm = async () => {
      try {
        const response = await axios.post(
          'http://localhost:5000/signup-professional',
          form.value,
        )
        if (response.data.success) {
          console.log('Professional registered successfully')
          router.push('/signin')
        } else {
          alert(`Error: ${response.data.message}`)
          console.log('Error:', response.data.message)
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
            alert(
              'Username or email already exists. Please try with different credentials.',
            )
          } else if (error.response.status === 500) {
            alert(
              `Registration failed due to a server error: ${error.response.data.message}`,
            )
          } else {
            alert('An unknown error occurred. Please try again later.')
          }
          console.error('Error response:', error.response)
        } else if (error.request) {
          alert(
            'No response from the server. Please check your internet connection or try again later.',
          )
          console.error('Error request:', error.request)
        } else {
          alert(
            'An error occurred during registration. Please try again later.',
          )
          console.error('Error message:', error.message)
        }
      }
    }

    return {
      form,
      services,
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
  background-color: #ddcfb6;
}
.image-container {
  width: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.form-container {
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

.group {
  width: 100%;
  justify-self: center;
  align-items: center;
  display: flex;
  flex-direction: column;
}
</style>
