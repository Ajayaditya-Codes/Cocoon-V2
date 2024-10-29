import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/home.vue'
import signup from '../views/auth/signup/signup.vue'
import signupProfessional from '../views/auth/signup/professionalSignup.vue'
import signupCustomer from '../views/auth/signup/customerSignup.vue'
import NotFound from '@/views/404.vue'
import signIn from '@/views/auth/signin.vue'
import CustomerDashboard from '@/views/dashboards/customerDashboard.vue'
import ProfessionalDashboard from '@/views/dashboards/professionalDashboard.vue'
import AdminDashboard from '@/views/dashboards/admin/adminDashboard.vue'
import AdminProfessional from '@/views/dashboards/admin/adminProfessional.vue'
import AdminCustomer from '@/views/dashboards/admin/adminCustomer.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/signup',
      name: 'Sign Up',
      component: signup,
    },
    {
      path: '/signup/professional',
      name: 'Sign Up for Professionals',
      component: signupProfessional,
    },
    {
      path: '/signup/customer',
      name: 'Sign Up for Customer',
      component: signupCustomer,
    },
    {
      path: '/signin',
      name: 'Sign In',
      component: signIn,
    },
    {
      path: '/customer-dashboard',
      name: 'Customer Dashboard',
      component: CustomerDashboard,
    },
    {
      path: '/professional-dashboard',
      name: 'Professional Dashboard',
      component: ProfessionalDashboard,
    },
    {
      path: '/admin-dashboard',
      name: 'Admin Dashboard',
      component: AdminDashboard,
    },
    {
      path: '/admin/professional/:id',
      name: 'Admin Professional',
      component: AdminProfessional,
      props: true,
    },
    {
      path: '/admin/customer/:id',
      name: 'Admin Customer',
      component: AdminCustomer,
      props: true,
    },
    {
      path: '/:pathMatch(.*)*', // Catch all undefined routes
      name: 'NotFound',
      component: NotFound,
    },
  ],
})

export default router
