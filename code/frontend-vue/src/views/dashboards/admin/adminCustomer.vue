<template>
  <div class="admin-dashboard">
    <div class="navbar">
      <div class="logo">
        <span class="pi pi-home icon icon-style"></span>
        <h2>Cocoon</h2>
      </div>
      <button class="btn btn-styled" @click="goToDashboard">
        Go back to Dashboard
      </button>
    </div>

    <div class="profile-card" v-if="customerDetails">
      <h3>Customer Details</h3>
      <p><strong>ID:</strong> {{ customerDetails.id }}</p>
      <p><strong>Full Name:</strong> {{ customerDetails.full_name }}</p>
      <p></p>
      <p><strong>Address:</strong> {{ customerDetails.address }} years</p>
      <p><strong>Pincode:</strong> {{ customerDetails.pincode }}</p>
      <p><strong>Phone:</strong> {{ customerDetails.phone }}</p>
      <p>
        <strong>Verified:</strong>
        {{ customerDetails.verified ? 'Yes' : 'No' }}
      </p>
      <p><strong>Email:</strong> {{ customerDetails.email }}</p>
      <p><strong>Username:</strong> {{ customerDetails.username }}</p>
      <div class="action-buttons">
        <button
          class="btn-action"
          @click="blockUser"
          :disabled="customerDetails.blocked === 1"
        >
          Block User
        </button>
        <button
          class="btn-action"
          @click="unblockUser"
          :disabled="customerDetails.blocked === 0"
        >
          Unblock User
        </button>
      </div>
    </div>

    <div class="dashboard-tab" v-if="serviceRequests.length">
      <h3>Service Requests</h3>
      <table class="service-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Service ID</th>
            <th>Professional ID</th>
            <th>Professional Name</th>
            <th>Professional Phone</th>
            <th>Professional Pincode</th>
            <th>Price</th>
            <th>Status</th>
            <th>Date of Service</th>
            <th>Description</th>
            <th>Rating</th>
            <th>Review</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="request in serviceRequests" :key="request.id">
            <td>{{ request.id }}</td>
            <td>{{ request.service_id }}</td>
            <td>{{ request.professional_id }}</td>
            <td>
              <RouterLink
                :to="{ path: `/admin/professional/${request.professional_id}` }"
                >{{ request.full_name }}</RouterLink
              >
            </td>
            <td>{{ request.phone }}</td>
            <td>{{ request.pincode }}</td>
            <td>{{ request.price }}</td>
            <td>{{ request.service_status }}</td>
            <td>
              {{ new Date(request.date_of_service).toLocaleDateString() }}
            </td>
            <td>{{ request.service_description }}</td>
            <td>{{ request.rating }}</td>
            <td>{{ request.review }}</td>
            <td>
              <button
                class="btn-service-action"
                @click="deleteRequest(request.id)"
              >
                Delete
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
import { useRouter, useRoute, RouterLink } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    const route = useRoute()
    const userId = route.params.id
    const customerDetails = ref(null)
    const serviceRequests = ref([])

    const goToDashboard = () => {
      router.push('/admin-dashboard')
    }

    const blockUser = async () => {
      try {
        const response = await axios.put(
          `http://localhost:5000/admin/block-user/${userId}`,
          {},
          { withCredentials: true },
        )

        if (response.data.success) {
          alert('User blocked successfully!')
          fetchCustomerDetails()
        } else {
          alert(`Error: ${response.data.message || 'Failed to block user.'}`)
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 403) {
            alert(
              'Access denied: You do not have permission to block this user.',
            )
          } else if (error.response.status === 404) {
            alert('Error: The user you are trying to block was not found.')
          } else if (error.response.status === 500) {
            alert(
              'Server error: Please try again later. If the issue persists, contact support.',
            )
          } else {
            alert(
              `Error: ${error.response.data.message || 'An unknown error occurred.'}`,
            )
          }
        } else if (error.request) {
          alert(
            'Network error: Unable to reach the server. Please check your connection and try again.',
          )
        } else {
          alert('An unexpected error occurred. Please try again later.')
        }
      }
    }

    const unblockUser = async () => {
      try {
        const response = await axios.put(
          `http://localhost:5000/admin/unblock-user/${userId}`,
          {},
          { withCredentials: true },
        )

        if (response.data.success) {
          alert('User unblocked successfully!')
          fetchCustomerDetails()
        } else {
          alert(`Error: ${response.data.message || 'Failed to unblock user.'}`)
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 403) {
            alert(
              'Access denied: You do not have permission to unblock this user.',
            )
          } else if (error.response.status === 404) {
            alert('Error: The user you are trying to unblock was not found.')
          } else if (error.response.status === 500) {
            alert(
              'Server error: Please try again later. If the issue persists, contact support.',
            )
          } else {
            alert(
              `Error: ${error.response.data.message || 'An unknown error occurred.'}`,
            )
          }
        } else if (error.request) {
          alert(
            'Network error: Unable to reach the server. Please check your connection and try again.',
          )
        } else {
          alert('An unexpected error occurred. Please try again later.')
        }
      }
    }

    const fetchCustomerDetails = async () => {
      try {
        const response = await axios.get(
          `http://localhost:5000/admin/customer/${userId}`,
          {
            withCredentials: true,
          },
        )
        if (response.data.success) {
          customerDetails.value = response.data.customer
          serviceRequests.value = response.data.service_requests
        } else {
          console.error(
            'Failed to fetch customer details:',
            response.data.message,
          )
          alert('Failed to fetch customer details. Please try again')
        }
      } catch (error) {
        console.error('Failed to fetch customer details:', error)
        alert('Failed to fetch customer details. Please try again')
      }
    }

    const deleteRequest = async requestId => {
      try {
        const response = await axios.delete(
          `http://localhost:5000/admin/delete-service-request/${requestId}`,
          { withCredentials: true },
        )

        if (response.data.success) {
          alert('Request deleted successfully!')
          fetchCustomerDetails()
        } else {
          alert(
            `Error: ${response.data.message || 'Failed to delete request.'}`,
          )
        }
      } catch (error) {
        if (error.response) {
          if (error.response.status === 403) {
            alert(
              'Access denied: You do not have permission to delete this request.',
            )
          } else if (error.response.status === 404) {
            alert(
              'Error: The service request you are trying to delete was not found.',
            )
          } else if (error.response.status === 500) {
            alert(
              'Server error: Please try again later. If the issue persists, contact support.',
            )
          } else {
            alert(
              `Error: ${error.response.data.message || 'An unknown error occurred.'}`,
            )
          }
        } else if (error.request) {
          alert(
            'Network error: Unable to reach the server. Please check your connection and try again.',
          )
        } else {
          alert('An unexpected error occurred. Please try again later.')
        }
      }
    }

    onMounted(() => {
      fetchCustomerDetails()
    })

    return {
      goToDashboard,
      serviceRequests,
      blockUser,
      customerDetails,
      unblockUser,
      deleteRequest,
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

h3 {
  margin-bottom: 30px;
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

.action-buttons {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-action {
  padding: 8px 12px;
  background-color: #2a9d8f;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-action:hover {
  background-color: #21867a;
}

.btn-action:disabled,
abled,
.btn-service-action:disabled,
:disabled,
.btn-styled:disabled {
  background-color: #ccc;
  cursor: not-allowed;
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

.btn-styled {
  background: #e63946;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-styled:hover {
  background: #d62839;
}

.profile-card {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
