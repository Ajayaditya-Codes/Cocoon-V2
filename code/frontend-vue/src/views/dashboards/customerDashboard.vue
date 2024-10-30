<template>
  <div class="customer-dashboard">
    <div class="navbar">
      <div class="logo">
        <span class="pi pi-home icon icon-style"></span>
        <h2>Cocoon</h2>
      </div>
      <div class="nav-links">
        <button
          :class="{ active: activeTab === 'dashboard' }"
          @click="switchTab('dashboard')"
        >
          Dashboard
        </button>
        <button
          :class="{ active: activeTab === 'book_service' }"
          @click="switchTab('book_service')"
        >
          Book Service
        </button>
        <button
          :class="{ active: activeTab === 'report' }"
          @click="switchTab('report')"
        >
          Report
        </button>
        <button
          :class="{ active: activeTab === 'profile' }"
          @click="switchTab('profile')"
        >
          Profile
        </button>
      </div>
      <button class="btn btn-logout" @click="logout">Logout</button>
    </div>

    <div v-if="activeTab === 'dashboard'" class="dashboard-tab">
      <h2>Welcome, {{ userInfo.full_name }}!</h2>

      <!-- Requested Services Table -->
      <h3 class="title">Requested Services</h3>
      <table class="service-table">
        <thead>
          <tr>
            <th>Professional Name</th>
            <th>Service</th>
            <th>Pincode</th>
            <th>Price</th>
            <th>Date of Service</th>
            <th>Service Description</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in requestedServices" :key="service.request_id">
            <td>{{ service.professional_name }} ({{ service.p_phone }})</td>
            <td>{{ service.service_name }}</td>
            <td>{{ service.professional_pincode }}</td>
            <td>{{ service.price }}</td>

            <td>
              <input
                type="date"
                v-model="service.date_of_service"
                :min="minDate"
              />
            </td>
            <td>
              <input
                type="text"
                v-model="service.service_description"
                placeholder="Describe your service..."
              />
            </td>
            <td>
              <button
                class="btn btn-service-action"
                @click="cancelRequest(service.request_id)"
              >
                Cancel Request
              </button>
              <button
                class="btn btn-service-action"
                @click="
                  updateRequest(
                    service.request_id,
                    service.price,
                    service.date_of_service,
                    service.service_description,
                  )
                "
              >
                Update Request
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!requestedServices.length" class="error">
        No active service requests found
      </p>

      <!-- Quoted Services Table -->
      <h3 class="title">Quoted Services</h3>
      <table class="service-table">
        <thead>
          <tr>
            <th>Professional Name</th>
            <th>Service</th>
            <th>Pincode</th>
            <th>Price</th>
            <th>Date of Service</th>
            <th>Service Description</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in quotedServices" :key="service.request_id">
            <td>{{ service.professional_name }}({{ service.p_phone }})</td>
            <td>{{ service.service_name }}</td>
            <td>{{ service.professional_pincode }}</td>
            <td>{{ service.price }}</td>
            <td>{{ service.date_of_service }}</td>
            <td>{{ service.service_description }}</td>
            <td>
              <button
                class="btn btn-service-action"
                @click="
                  acceptRequest(
                    service.request_id,
                    service.professional_id,
                    service.price,
                  )
                "
              >
                Accept Service
              </button>
              <button
                class="btn btn-service-action"
                @click="cancelRequest(service.request_id)"
              >
                Cancel Request
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!quotedServices.length" class="error">
        No quoted service requests found
      </p>

      <!-- Assigned Services Table -->
      <h3 class="title">Assigned Services</h3>
      <table class="service-table">
        <thead>
          <tr>
            <th>Professional Name</th>
            <th>Service</th>
            <th>Pincode</th>
            <th>Price</th>
            <th>Date of Service</th>
            <th>Service Description</th>
            <th>Review</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in assignedServices" :key="service.id">
            <td>{{ service.professional_name }} ({{ service.p_phone }})</td>
            <td>{{ service.service_name }}</td>
            <td>{{ service.professional_pincode }}</td>
            <td>{{ service.price }}</td>
            <td>{{ service.date_of_service }}</td>
            <td>{{ service.service_description }}</td>
            <td>
              <input
                type="text"
                v-model="service.review"
                class="form-control"
                placeholder="Review for Service..."
              />
              <select v-model="service.rating" class="form-select">
                <option value="" disabled>Select a service</option>
                <option v-for="n in 5" :key="n" :value="n">{{ n }}</option>
              </select>
            </td>
            <td>
              <button
                class="btn btn-service-action"
                @click="
                  closeRequest(
                    service.request_id,
                    service.rating,
                    service.review,
                  )
                "
              >
                Close Request
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!assignedServices.length" class="error">
        No assigned services found
      </p>
    </div>

    <div v-if="activeTab === 'book_service'" class="tab-content book-service">
      <h2>Available Services</h2>
      <form @submit.prevent="filterServices" class="service-filter-form">
        <input
          v-model="searchQuery"
          class="form-control"
          placeholder="Search services or professionals..."
        />
        <select v-model="selectedPincode" class="form-control">
          <option value="">Select Pincode</option>
          <option
            v-for="pincode in uniquePincodes"
            :key="pincode"
            :value="pincode"
          >
            {{ pincode }}
          </option>
        </select>
        <button type="submit" class="btn btn-filter">Filter</button>
      </form>
      <table class="service-table">
        <thead>
          <tr>
            <th>Professional Name</th>
            <th>Service</th>
            <th>Pincode</th>
            <th>Price</th>
            <th>Date</th>
            <th>Description</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in filteredServices" :key="service.id">
            <td>{{ service.professionalName }} ({{ service.p_phone }})</td>
            <td>
              {{ service.serviceName }}
              {{
                service.average_rating
                  ? '(Rating - ' + service.average_rating + ')'
                  : ''
              }}
            </td>
            <td>{{ service.professional_pincode }}</td>
            <td>{{ service.price }}</td>
            <td>
              <input type="date" v-model="service.date" :min="minDate" />
            </td>
            <td>
              <input
                type="text"
                v-model="service.description"
                placeholder="Describe your service..."
              />
            </td>
            <td>
              <button
                class="btn btn-book-service"
                @click="
                  bookService(
                    service.id,
                    service.professional_id,
                    service.price,
                    service.date,
                    service.description,
                  )
                "
              >
                Book Service
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'profile'" class="profile-card">
      <h2>Profile Information</h2>
      <form @submit.prevent="updateProfile">
        <div class="form-group">
          <label>Username</label>
          <input type="text" v-model="userInfo.username" disabled />
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="userInfo.email" disabled />
        </div>
        <div class="form-group">
          <label>Full Name</label>
          <input type="text" v-model="userInfo.full_name" />
        </div>
        <div class="form-group">
          <label>Address</label>
          <input type="text" v-model="userInfo.address" />
        </div>
        <div class="form-group">
          <label>Pincode</label>
          <input type="number" v-model="userInfo.pincode" />
        </div>
        <div class="form-group">
          <label>Phone</label>
          <input
            type="number"
            v-model="userInfo.phone"
            placeholder="Enter new phone (optional)"
          />
        </div>
        <div class="form-group">
          <label>New Password</label>
          <input
            type="password"
            v-model="userInfo.password"
            placeholder="Enter new password (optional)"
          />
        </div>
        <button type="submit" class="btn btn-update">Update Profile</button>
      </form>
    </div>

    <div v-if="activeTab === 'report'" class="report-tab">
      <h2 class="report-title">Generate Your Report</h2>
      <button class="btn btn-generate" @click="generateReport">
        Generate Report
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const activeTab = ref('dashboard')
    const userInfo = ref({
      username: '',
      email: '',
      full_name: '',
      address: '',
      pincode: '',
      password: '',
      phone: '',
      blocked: 0,
    })

    const services = ref([])
    const filteredServices = ref([])

    const searchQuery = ref('')

    const selectedPincode = ref('')
    const uniquePincodes = ref([])

    const requestedServices = ref([])
    const quotedServices = ref([])
    const assignedServices = ref([])

    const router = useRouter()
    const today = new Date()
    const minDate = ref(today.toISOString().split('T')[0])

    const switchTab = tab => {
      activeTab.value = tab
      if (tab === 'book_service') fetchServices()
      if (tab === 'dashboard') servicesSetup()
    }

    const logout = async () => {
      try {
        await axios.get('http://localhost:5000/logout', {
          withCredentials: true,
        })
        router.push('/signin')
      } catch (error) {
        console.error('Logout failed:', error)
        alert('Failed to logout. Please try again')
      }
    }

    const fetchUserData = async () => {
      try {
        const statusResponse = await axios.get(
          'http://localhost:5000/session-status',
          { withCredentials: true },
        )
        if (statusResponse.data.message === 'User is logged in') {
          const response = await axios.get(
            'http://localhost:5000/customer/profile',
            { withCredentials: true },
          )
          userInfo.value = response.data
        } else {
          router.push('/signin')
        }
      } catch (error) {
        console.error('Failed to fetch user data:', error)
        if (error.response?.status === 401) {
          alert('Please sign in to continue')
          router.push('/signin')
        } else if (error.response?.status === 403) {
          alert('You do not have permission to access this profile')
        } else if (error.response?.status === 404) {
          alert('User profile not found')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again later')
        } else {
          alert('Failed to load profile. Please check your connection')
        }
      }
    }

    const updateProfile = async () => {
      try {
        if (userInfo.value.pincode.toString().length !== 6) {
          alert('Pincode must be exactly 6 digits long.')
          return
        }

        if (
          userInfo.value.phone &&
          userInfo.value.phone.toString().length !== 10
        ) {
          alert('Phone number must be exactly 10 digits long.')
          return
        }
        await axios.put(
          'http://localhost:5000/customer/profile',
          userInfo.value,
          { withCredentials: true },
        )
        alert('Profile updated successfully')
      } catch (error) {
        console.error('Profile update failed:', error)
        if (error.response?.status === 400) {
          alert(
            error.response.data.message || 'Please check your input details',
          )
        } else if (error.response?.status === 401) {
          alert('Please sign in again to update your profile')
          router.push('/signin')
        } else if (error.response?.status === 403) {
          alert('You do not have permission to update this profile')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again later')
        } else {
          alert('Failed to update profile. Please try again')
        }
      }
    }

    const fetchServices = async () => {
      try {
        const response = await axios.get('http://localhost:5000/get_services')
        const serviceList = response.data
        for (const service of serviceList) {
          service.date = today.toISOString().split('T')[0]
          service.description = ''
        }
        services.value = serviceList
        filteredServices.value = response.data
        uniquePincodes.value = [
          ...new Set(
            response.data.map(service => service.professional_pincode),
          ),
        ]
      } catch (error) {
        console.error('Failed to fetch services:', error)
        if (error.response?.status === 500) {
          alert('Unable to load services due to server error')
        } else {
          alert('Failed to load services. Please try again')
        }
      }
    }

    const generateReport = async () => {
      try {
        const response = await axios.get(
          'http://localhost:5000/generate-report/customer',
          { withCredentials: true, responseType: 'blob' },
        )
        const url = window.URL.createObjectURL(new Blob([response.data]))

        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', 'customer_report.pdf') // Set the file name

        document.body.appendChild(link)
        link.click()

        link.remove()
        window.URL.revokeObjectURL(url)

        alert('Report generated successfully')
      } catch (error) {
        console.error('Failed to generate report:', error)
        if (error.response?.status === 403) {
          alert('You do not have permission to generate a report')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again later')
        } else {
          alert('Failed to generate report. Please try again')
        }
      }
    }

    const bookService = async (
      serviceId,
      professionalId,
      price,
      serviceDate,
      serviceDescription,
    ) => {
      try {
        if (!serviceDate || !serviceDescription) {
          alert('Please select a date and provide a service description')
          return
        }
        await axios.post(
          'http://localhost:5000/book_service',
          {
            service_id: serviceId,
            professional_id: professionalId,
            price,
            service_date: serviceDate,
            service_description: serviceDescription,
          },
          { withCredentials: true },
        )
        alert('Service booked successfully')
      } catch (error) {
        console.error('Service booking failed:', error)
        if (error.response?.status === 400) {
          alert(error.response.data.message || 'Invalid booking details')
        } else if (error.response?.status === 401) {
          alert('Please sign in to book services')
          router.push('/signin')
        } else if (error.response?.status === 403) {
          alert('You do not have permission to book services')
        } else if (error.response?.status === 404) {
          alert('Service or professional not found')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again later')
        } else {
          alert('Booking failed. Please try again')
        }
      }
    }

    const fetchServiceRequests = async (status, serviceArr) => {
      try {
        const response = await axios.get(
          `http://localhost:5000/service-requests/${status}`,
          { withCredentials: true },
        )
        serviceArr.value = response.data
      } catch (error) {
        console.error(`Failed to fetch ${status} services:`, error)
        if (error.response?.status === 403) {
          alert(`You do not have permission to view ${status} services`)
        } else if (error.response?.status === 500) {
          alert(`Unable to load ${status} services due to server error`)
        } else {
          alert(`Failed to load ${status} services`)
        }
      }
    }

    const servicesSetup = async () => {
      fetchServiceRequests('quoted', quotedServices)
      fetchServiceRequests('assigned', assignedServices)
      fetchServiceRequests('requested', requestedServices)
    }

    const updateRequest = async (
      requestId,
      price,
      serviceDate,
      serviceDescription,
    ) => {
      try {
        const response = await axios.put(
          `http://localhost:5000/update-service-request/${requestId}`,
          {
            service_date: serviceDate,
            service_description: serviceDescription,
            service_price: price,
            quote: false,
          },
          { withCredentials: true },
        )

        alert('Service updated successfully')
        servicesSetup()
        return response.data
      } catch (error) {
        console.error('Failed to update service:', error)

        if (error.response?.status === 403) {
          alert('You do not have permission to update this service request')
        } else if (error.response?.status === 404) {
          alert('Request not found or already updated')
        } else if (error.response?.status === 400) {
          alert('Invalid input. Please check the service date and description')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again')
        } else {
          alert('Failed to update service. Please try again')
        }
      }
    }

    const cancelRequest = async requestId => {
      try {
        await axios.delete(
          `http://localhost:5000/delete-service-request/${requestId}`,
          { withCredentials: true },
        )
        alert('Request cancelled successfully')
        servicesSetup()
      } catch (error) {
        console.error('Failed to cancel request:', error)
        if (error.response?.status === 403) {
          alert('You do not have permission to cancel this request')
        } else if (error.response?.status === 404) {
          alert('Request not found or already cancelled')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again')
        } else {
          alert('Failed to cancel request. Please try again')
        }
      }
    }

    const closeRequest = async (requestId, rating, review) => {
      if (review === undefined || rating === undefined) {
        alert('Please Provide a valid Rating and Review')
        return
      }
      try {
        await axios.put(
          `http://localhost:5000/close-service-request/${requestId}`,
          {
            rating: rating,
            review: review,
          },
          { withCredentials: true },
        )
        alert('Request closed successfully')
        servicesSetup()
      } catch (error) {
        console.error('Failed to close request:', error)
        if (error.response?.status === 403) {
          alert('You do not have permission to close this request')
        } else if (error.response?.status === 404) {
          alert('Request not found or already closed')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again')
        } else {
          alert('Failed to close request. Please try again')
        }
      }
    }

    const acceptRequest = async requestId => {
      try {
        await axios.get(
          `http://localhost:5000/accept-service-request/${requestId}`,
          { withCredentials: true },
        )
        alert('Request accepted successfully')
        servicesSetup()
      } catch (error) {
        console.error('Failed to accept request:', error)
        if (error.response?.status === 403) {
          alert('You do not have permission to accpet this request')
        } else if (error.response?.status === 404) {
          alert('Request not found or already accpetd')
        } else if (error.response?.status === 500) {
          alert('Server error occurred. Please try again')
        } else {
          alert('Failed to accpet request. Please try again')
        }
      }
    }

    const filterServices = () => {
      filteredServices.value = services.value.filter(service => {
        const matchesSearch =
          service.professionalName
            .toLowerCase()
            .includes(searchQuery.value.toLowerCase()) ||
          service.serviceName
            .toLowerCase()
            .includes(searchQuery.value.toLowerCase())
        const matchesPincode = selectedPincode.value
          ? service.professional_pincode === selectedPincode.value
          : true
        return matchesSearch && matchesPincode
      })
    }

    const checkUser = async () => {
      fetchUserData()
      if (
        userInfo.username === null ||
        userInfo.username === undefined ||
        userInfo.username === '' ||
        userInfo.blocked === 1
      ) {
        router.push('/signin')
      }
    }

    onMounted(() => {
      fetchUserData()
      servicesSetup()
      checkUser()
    })

    return {
      activeTab,
      userInfo,
      searchQuery,
      selectedPincode,
      filteredServices,
      uniquePincodes,
      switchTab,
      logout,
      updateProfile,
      bookService,
      filterServices,
      requestedServices,
      quotedServices,
      assignedServices,
      cancelRequest,
      closeRequest,
      minDate,
      acceptRequest,
      updateRequest,
      generateReport,
    }
  },
}
</script>

<style scoped>
.customer-dashboard {
  padding: 20px;
}

.logo {
  display: flex;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background-color: #444;
  color: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.report-title {
  margin-top: 10px;
}

.title {
  margin: 40px 0px 20px 0px;
}

h2 {
  margin-bottom: 0;
  font-size: 1.5rem;
  font-weight: bold;
}

.icon-style {
  font-size: 1.8rem;
  margin-right: 10px;
}

.error {
  color: red;
  text-align: center;
  margin-top: 20px;
}

.nav-links {
  display: flex;
  gap: 15px;
}

.nav-links button {
  background: none;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  padding: 10px 15px;
  border-radius: 5px;
  transition:
    background-color 0.3s,
    color 0.3s;
}

.nav-links button:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: aqua;
}

.nav-links button.active {
  background-color: rgba(255, 255, 255, 0.2);
  color: aqua;
}

.btn-logout {
  background: #e63946;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-logout:hover {
  background: #d62839;
}

.book-service {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.service-filter-form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.form-select {
  margin-top: 10px;
}

.form-control {
  margin-top: 20px;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
  flex: 1;
}

.btn-filter {
  margin-top: 20px;
  padding: 0px 20px;
  font-size: 1rem;
  background-color: #2a9d8f;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-filter:hover {
  background-color: #21867a;
}

.btn-book-service {
  padding: 8px 12px;
  background-color: #2a9d8f;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-book-service:hover {
  background-color: #21867a;
}

.profile-card {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.report-tab {
  padding: 20px;
  text-align: center;
}

.btn-generate {
  padding: 10px 20px;
  font-size: 1rem;
  margin: 20px;
  background-color: #e63946;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-generate:hover {
  background-color: #d62839;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input {
  padding: 10px;
  width: 100%;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.btn-update {
  padding: 10px 20px;
  font-size: 1rem;
  background-color: #2a9d8f;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-update:hover {
  background-color: #21867a;
}

.dashboard-tab {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.service-table {
  width: 100%;
  border-collapse: collapse;
}

.service-table th,
.service-table td {
  padding: 10px;
  border: 1px solid #ddd;
}

.service-table th {
  background-color: #f2f2f2;
}

.btn-service-action {
  padding: 8px 12px;
  margin-left: 10px;
  background-color: #2a9d8f;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.btn-service-action:hover {
  background-color: #21867a;
}
</style>
