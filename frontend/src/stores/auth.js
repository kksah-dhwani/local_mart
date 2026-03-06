import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(email, password) {
    const res = await api.post('/auth/login', { email, password })
    token.value = res.data.access_token
    localStorage.setItem('token', token.value)
    await fetchMe()
    return res.data
  }

  async function fetchMe() {
    const res = await api.get('/auth/me')
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(user.value))
    return user.value
  }

  async function register(data) {
    const res = await api.post('/auth/register', data)
    return res.data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function updateProfile(data) {
    await api.put('/auth/profile', data)
    await fetchMe()
  }

  async function changePassword(data) {
    await api.put('/auth/change-password', data)
  }

  return { token, user, isLoggedIn, isAdmin, login, register, logout, fetchMe, updateProfile, changePassword }
})
