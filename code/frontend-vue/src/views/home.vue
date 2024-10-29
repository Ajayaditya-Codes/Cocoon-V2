<template>
  <div class="hero-section">
    <div class="hero-overlay">
      <div class="navbar">
        <div class="logo">
          <span class="pi pi-home icon"></span>
          <h2>Cocoon</h2>
        </div>
        <div class="auth-buttons">
          <template v-if="userType">
            <RouterLink :to="dashboardLink">
              <button class="btn btn-dashboard">Go to Dashboard</button>
            </RouterLink>
          </template>
          <template v-else>
            <RouterLink to="/signin">
              <button class="btn btn-signin">Sign In</button>
            </RouterLink>
            <RouterLink to="/signup">
              <button class="btn btn-join">Join Now</button>
            </RouterLink>
          </template>
        </div>
      </div>
      <div class="hero-title">
        <h1>
          Discover Home <br />
          Comfort with Cocoon
        </h1>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import Cookies from 'js-cookie'

export default {
  setup() {
    const userType = ref(null)
    const dashboardLink = ref('')

    onMounted(() => {
      userType.value = Cookies.get('user_type')

      if (userType.value) {
        switch (userType.value) {
          case 'admin':
            dashboardLink.value = '/admin-dashboard'
            break
          case 'professional':
            dashboardLink.value = '/professional-dashboard' // Adjust as necessary
            break
          case 'customer':
            dashboardLink.value = '/customer-dashboard' // Adjust as necessary
            break
          default:
            dashboardLink.value = '' // In case of an unexpected user type
        }
      }
    })

    return {
      userType,
      dashboardLink,
    }
  },
}
</script>

<style scoped>
.hero-section {
  background-image: url('header.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh;
  width: 100vw;
  position: relative;
}

.icon {
  font-size: 1.5rem;
  margin-right: 7px;
}

.btn {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.btn-join {
  border-color: white;
  border-radius: 10px;
  padding: 5px 10px;
  border: solid 1px;
  margin-left: 10px;
}

.hero-overlay {
  position: absolute;
  height: 100vh;
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  top: 50%;
  left: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(1px);
  transform: translate(-50%, -50%);
  color: white;
  text-align: center;
  font-size: 2rem;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 10vh;
  width: 95%;
  padding: 10px;
  border-bottom: 2px solid white;
}

.logo {
  display: flex;
  align-items: center;
}

.hero-title {
  font-family: 'Georgia', 'Times New Roman', serif;
  height: 85vh;
  width: 95vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: radial-gradient(farthest-side at 60% 55%, #99f2c8, #5f8aef);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

h2 {
  margin: 0;
}

h1 {
  margin: 0;
  font-size: 7rem;
  font-weight: bold;
}

p {
  font-size: 1.5rem;
}
</style>
