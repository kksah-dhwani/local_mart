<template>
  <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <router-link to="/" class="flex items-center gap-2 font-bold text-xl text-blue-600">
          🛒 Local Mart
        </router-link>

        <!-- Search -->
        <div class="hidden md:flex flex-1 max-w-md mx-8">
          <input
            v-model="search"
            @keyup.enter="doSearch"
            type="text"
            placeholder="Search products..."
            class="w-full border border-gray-300 rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button @click="doSearch" class="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700">
            🔍
          </button>
        </div>

        <!-- Right Actions -->
        <div class="flex items-center gap-3">
          <router-link v-if="auth.isLoggedIn && !auth.isAdmin" to="/cart" class="relative p-2 text-gray-600 hover:text-blue-600">
            🛒
            <span v-if="cart.itemCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {{ cart.itemCount }}
            </span>
          </router-link>

          <template v-if="!auth.isLoggedIn">
            <router-link to="/login" class="btn-secondary text-sm">Login</router-link>
            <router-link to="/register" class="btn-primary text-sm">Register</router-link>
          </template>

          <template v-else>
            <div class="relative" v-click-outside="() => menuOpen = false">
              <button @click="menuOpen = !menuOpen" class="flex items-center gap-2 text-sm font-medium text-gray-700 hover:text-blue-600">
                👤 {{ auth.user?.name?.split(' ')[0] }}
                <span class="text-xs">▼</span>
              </button>
              <div v-if="menuOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
                <template v-if="auth.isAdmin">
                  <router-link to="/admin" class="block px-4 py-2 text-sm hover:bg-gray-50" @click="menuOpen=false">Dashboard</router-link>
                  <router-link to="/admin/products" class="block px-4 py-2 text-sm hover:bg-gray-50" @click="menuOpen=false">Products</router-link>
                  <router-link to="/admin/orders" class="block px-4 py-2 text-sm hover:bg-gray-50" @click="menuOpen=false">Orders</router-link>
                </template>
                <template v-else>
                  <router-link to="/profile" class="block px-4 py-2 text-sm hover:bg-gray-50" @click="menuOpen=false">My Profile</router-link>
                  <router-link to="/orders" class="block px-4 py-2 text-sm hover:bg-gray-50" @click="menuOpen=false">My Orders</router-link>
                </template>
                <hr class="my-1" />
                <button @click="doLogout" class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50">Logout</button>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const auth = useAuthStore()
const cart = useCartStore()
const router = useRouter()
const search = ref('')
const menuOpen = ref(false)

function doSearch() {
  if (search.value.trim()) {
    router.push({ path: '/products', query: { search: search.value } })
    search.value = ''
  }
}

function doLogout() {
  auth.logout()
  cart.reset()
  menuOpen.value = false
  router.push('/login')
}

// click-outside directive
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (e) => { if (!el.contains(e.target)) binding.value(e) }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) { document.removeEventListener('click', el._clickOutside) },
}
</script>
