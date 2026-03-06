<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <router-link to="/" class="text-3xl font-bold text-blue-600">🛒 Local Mart</router-link>
        <p class="text-gray-500 mt-2">Create your account</p>
      </div>
      <div class="card p-8">
        <h1 class="text-2xl font-bold text-gray-900 mb-6">Create Account</h1>
        <form @submit.prevent="doRegister" class="space-y-4">
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1">Full Name</label>
            <input v-model="form.name" type="text" required class="input-field" placeholder="Your name" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1">Email</label>
            <input v-model="form.email" type="email" required class="input-field" placeholder="you@example.com" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1">Phone Number</label>
            <input v-model="form.phone" type="tel" required class="input-field" placeholder="10-digit mobile number" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-700 block mb-1">Password</label>
            <input v-model="form.password" type="password" required class="input-field" placeholder="Min 6 characters" />
          </div>
          <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>
          <p v-if="success" class="text-green-600 text-sm font-medium">{{ success }}</p>
          <button type="submit" :disabled="loading" class="btn-primary w-full py-2.5">
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>
        </form>
        <p class="text-center text-sm text-gray-600 mt-4">
          Already have an account? <router-link to="/login" class="text-blue-600 font-medium hover:underline">Sign In</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ name: '', email: '', phone: '', password: '' })
const loading = ref(false)
const error = ref('')
const success = ref('')

async function doRegister() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(form.value)
    success.value = 'Account created! Redirecting to login...'
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed'
  } finally { loading.value = false }
}
</script>
