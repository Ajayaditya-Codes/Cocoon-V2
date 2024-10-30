<template>
  <div class="admin-dashboard">
    <div class="navbar">
      <div class="logo">
        <span class="pi pi-home icon icon-style"></span>
        <h2>Cocoon</h2>
      </div>
      <div class="nav-links">
        <button
          :class="{ active: activeTab === 'services' }"
          @click="switchTab('services')"
        >
          Services
        </button>
        <button
          :class="{ active: activeTab === 'customers' }"
          @click="switchTab('customers')"
        >
          Customers
        </button>
        <button
          :class="{ active: activeTab === 'professionals' }"
          @click="switchTab('professionals')"
        >
          Professionals
        </button>
      </div>
      <button class="btn btn-logout" @click="logout">Logout</button>
    </div>
    <div v-if="activeTab === 'services'" class="dashboard-tab">
      <table class="service-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Price</th>
            <th>Description</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>New</td>
            <td>
              <input
                v-model="newServiceName"
                placeholder="Service Name"
                class="form-control"
              />
            </td>
            <td>
              <input
                v-model="newServicePrice"
                type="number"
                placeholder="Price"
                class="form-control"
              />
            </td>
            <td>
              <input
                v-model="newServiceDescription"
                placeholder="Description"
                class="form-control"
              />
            </td>
            <td>
              <button
                class="btn-service-action"
                @click="
                  createService(
                    newServiceName,
                    newServicePrice,
                    newServiceDescription,
                  )
                "
              >
                Create
              </button>
            </td>
          </tr>
          <tr v-for="service in services" :key="service.id">
            <td>{{ service.id }}</td>
            <td>{{ service.name }}</td>
            <td>
              <input
                v-model.number="service.price"
                type="number"
                class="form-control"
              />
            </td>
            <td>
              <input
                v-model="service.description"
                type="text"
                class="form-control"
              />
            </td>
            <td>
              <button
                class="btn-service-action"
                @click="
                  updateService(service.id, service.price, service.description)
                "
              >
                Update
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="activeTab === 'professionals'" class="dashboard-tab">
      <table class="service-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Full Name</th>
            <th>Service Provided</th>
            <th>Pincode</th>
            <th>Experience</th>
            <th>Phone</th>
            <th>Verified</th>
            <th>Email</th>
            <th>Username</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="professional in professionals" :key="professional.id">
            <td>{{ professional.id }}</td>
            <td>{{ professional.full_name }}</td>
            <td>{{ professional.service_provided }}</td>
            <td>{{ professional.pincode }}</td>
            <td>{{ professional.experience }} Years</td>
            <td>{{ professional.phone }}</td>
            <td>
              {{ (professional.verified === 1).toString().toUpperCase() }}
            </td>
            <td>{{ professional.email }}</td>
            <td>{{ professional.username }}</td>
            <td>
              <button
                class="btn-service-action"
                @click="goToProfessional(professional.id)"
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="activeTab === 'customers'" class="dashboard-tab">
      <table class="service-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Full Name</th>
            <th>Address</th>
            <th>Pincode</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Username</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="customer in customers" :key="customer.id">
            <td>{{ customer.id }}</td>
            <td>{{ customer.full_name }}</td>
            <td>{{ customer.address }}</td>
            <td>{{ customer.pincode }}</td>
            <td>{{ customer.phone }}</td>
            <td>{{ customer.email }}</td>
            <td>{{ customer.username }}</td>
            <td>
              <button
                class="btn-service-action"
                @click="goToCustomer(customer.id)"
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const activeTab = ref('services')
    const router = useRouter()
    const professionals = ref([])
    const customers = ref([])
    const services = ref([])

    const switchTab = tab => {
      activeTab.value = tab
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

    const fetchProfessionals = async () => {
      try {
        const response = await axios.get(
          'http://localhost:5000/admin/professionals',
          {
            withCredentials: true,
          },
        )
        professionals.value = response.data
      } catch (error) {
        console.error('Failed to fetch professionals:', error)
        alert('Failed to fetch professionals. Please try again')
      }
    }

    const goToProfessional = id => {
      router.push(`/admin/professional/${id}`)
    }

    const goToCustomer = id => {
      router.push(`/admin/customer/${id}`)
    }

    const fetchCustomers = async () => {
      try {
        const response = await axios.get(
          'http://localhost:5000/admin/customers',
          {
            withCredentials: true,
          },
        )
        customers.value = response.data
      } catch (error) {
        console.error('Failed to fetch customers:', error)
        alert('Failed to fetch customers. Please try again')
      }
    }

    const fetchServices = async () => {
      try {
        const response = await axios.get('http://localhost:5000/services', {
          withCredentials: true,
        })
        services.value = response.data
      } catch (error) {
        console.error('Failed to fetch services:', error)

        if (error.response) {
          alert(
            `Failed to fetch services. Server responded with status code ${error.response.status}: ${error.response.data.message}`,
          )
        } else if (error.request) {
          alert(
            'Failed to fetch services. No response received from the server. Please check your network connection.',
          )
        } else {
          alert(`Failed to fetch services. Error: ${error.message}`)
        }
      }
    }

    const updateService = async (serviceId, newPrice, newDescription) => {
      if (!newPrice || !newDescription || newPrice <= 0 || isNaN(newPrice)) {
        alert('Please enter a valid price and description.')
        return
      }
      try {
        const response = await axios.put(
          `http://localhost:5000/admin/update-service-price/${serviceId}`,
          { new_price: newPrice, new_description: newDescription },
          {
            withCredentials: true,
          },
        )

        if (response.data.success) {
          alert('Service price updated successfully.')
          fetchServices()
        } else {
          alert(`Failed to update service: ${response.data.message}`)
        }
      } catch (error) {
        console.error('Failed to update service:', error)

        if (error.response) {
          const { status, data } = error.response
          alert(
            `Failed to update service. Server responded with status code ${status}: ${data.message}`,
          )
        } else if (error.request) {
          alert(
            'Failed to update service. No response received from the server. Please check your network connection.',
          )
        } else {
          alert(`Failed to update service. Error: ${error.message}`)
        }
      }
    }

    const createService = async (serviceName, servicePrice, description) => {
      if (
        !servicePrice ||
        !description ||
        servicePrice <= 0 ||
        isNaN(servicePrice) ||
        serviceName
      ) {
        alert('Please enter a valid input.')
        return
      }
      try {
        const response = await axios.post(
          'http://localhost:5000/admin/create-service',
          { name: serviceName, price: servicePrice, description: description },
          {
            withCredentials: true,
          },
        )

        if (response.data.success) {
          alert('Service created successfully.')
          fetchServices()
        } else {
          alert(`Failed to create service: ${response.data.message}`)
        }
      } catch (error) {
        console.error('Failed to create service:', error)

        if (error.response) {
          const { status, data } = error.response
          alert(
            `Failed to create service. Server responded with status code ${status}: ${data.message}`,
          )
        } else if (error.request) {
          alert(
            'Failed to create service. No response received from the server. Please check your network connection.',
          )
        } else {
          alert(`Failed to create service. Error: ${error.message}`)
        }
      }
    }

    onMounted(() => {
      fetchProfessionals()
      fetchCustomers()
      fetchServices()
    })

    return {
      activeTab,
      goToProfessional,
      goToCustomer,
      logout,
      switchTab,
      professionals,
      customers,
      services,
      updateService,
      createService,
    }
  },
}
</script>

<style scoped>
.admin-dashboard {
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

.service-select {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 5px;
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
