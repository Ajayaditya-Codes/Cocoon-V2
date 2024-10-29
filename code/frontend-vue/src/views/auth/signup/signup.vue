<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="signup-wrapper">
    <div class="signup-options">
      <h1>
        How do you plan to<br />
        use Cocoon?
      </h1>
      <div>
        <div class="option-card">
          <RouterLink to="/signup/professional">
            <button class="action-button">
              <h3 class="option-title">
                <span class="pi pi-sparkles icon"></span>
                <b>I am here to Provide Services</b>
              </h3>
            </button>
          </RouterLink>
        </div>
        <div class="option-card">
          <RouterLink to="/signup/customer">
            <button class="action-button">
              <h3 class="option-title">
                <span class="pi pi-search icon"></span>
                <b>I am here to Find Service Professionals</b>
              </h3>
            </button>
          </RouterLink>
        </div>
      </div>
      <RouterLink to="/signin" class="btn btn-link mt-3"
        >Already have an account? Sign In</RouterLink
      >
    </div>
    <div class="signup-image">
      <img src="/house.png" />
    </div>
  </div>
</template>

<style scoped>
.signup-wrapper {
  width: 100vw;
  height: 100vh;
  background-color: #bcc7c6;
  display: flex;
}

.signup-options {
  height: 100vh;
  width: 50vw;
  padding: 0 100px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.action-button {
  background-color: transparent;
  padding: 0;
  border: none;
  box-shadow: none;
}

.option-card {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 30px;
  margin: 20px 0;
  padding: 20px;
  background-color: transparent;
  border: 2px solid;
}

.signup-image {
  width: 40vw;
  align-content: end;
  margin-left: 100px;
  margin-bottom: 100px;
}

.icon {
  margin-right: 20px;
}

h1 {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-size: 5rem;
  margin: 50px 0;
}
</style>
