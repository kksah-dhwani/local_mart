<template>
  <aside
    :style="{ width: sidebarWidth + 'px' }"
    class="relative min-h-screen bg-white border-r border-gray-200 flex flex-col flex-shrink-0 select-none"
  >
    <!-- Logo -->
    <div class="p-4 border-b border-gray-100 overflow-hidden">
      <router-link to="/" class="font-bold text-blue-600 text-lg whitespace-nowrap">
        🛒 <span v-if="sidebarWidth > 100">Local Mart</span>
      </router-link>
      <p v-if="sidebarWidth > 100" class="text-xs text-gray-500 mt-0.5">Admin Panel</p>
    </div>

    <!-- Nav -->
    <nav class="flex-1 p-3 space-y-1 overflow-hidden">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        :title="sidebarWidth <= 100 ? item.label : ''"
        :class="[
          'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition',
          $route.path === item.path
            ? 'bg-blue-50 text-blue-600'
            : 'text-gray-600 hover:bg-gray-50',
          sidebarWidth <= 100 ? 'justify-center' : ''
        ]"
      >
        <span class="flex-shrink-0 text-base">{{ item.icon }}</span>
        <span v-if="sidebarWidth > 100" class="truncate">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Width indicator (shows while dragging) -->
    <transition name="fade">
      <div
        v-if="isDragging"
        class="absolute top-2 right-8 bg-gray-800 text-white text-xs px-2 py-0.5 rounded-full pointer-events-none"
      >
        {{ sidebarWidth }}px
      </div>
    </transition>

    <!-- Logout -->
    <div class="p-3 border-t border-gray-100 overflow-hidden">
      <button
        @click="doLogout"
        :title="sidebarWidth <= 100 ? 'Logout' : ''"
        :class="[
          'flex items-center gap-2 w-full px-3 py-2 text-sm text-red-500 hover:bg-red-50 rounded-lg transition',
          sidebarWidth <= 100 ? 'justify-center' : ''
        ]"
      >
        🚪
        <span v-if="sidebarWidth > 100">Logout</span>
      </button>
    </div>

    <!-- ── Resize Handle ── -->
    <div
      @mousedown="startDrag"
      :class="[
        'absolute top-0 right-0 h-full w-1 cursor-col-resize group z-10',
        isDragging ? 'bg-blue-500' : 'hover:bg-blue-400 bg-transparent'
      ]"
      title="Drag to resize sidebar"
    >
      <!-- Visual grip dots -->
      <div class="absolute top-1/2 -translate-y-1/2 right-0 flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition pr-0.5">
        <span class="w-1 h-1 rounded-full bg-gray-400 block"></span>
        <span class="w-1 h-1 rounded-full bg-gray-400 block"></span>
        <span class="w-1 h-1 rounded-full bg-gray-400 block"></span>
        <span class="w-1 h-1 rounded-full bg-gray-400 block"></span>
        <span class="w-1 h-1 rounded-full bg-gray-400 block"></span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const auth   = useAuthStore()
const cart   = useCartStore()
const router = useRouter()

const navItems = [
  { path: '/admin',            icon: '📊', label: 'Dashboard' },
  { path: '/admin/orders',     icon: '📦', label: 'Orders' },
  { path: '/admin/analytics',  icon: '📈', label: 'Order Analytics' },
  { path: '/admin/users',      icon: '👥', label: 'Users' },
  { path: '/admin/products',   icon: '🛍️', label: 'Products' },
  { path: '/admin/categories', icon: '📂', label: 'Categories' },
  { path: '/admin/blocks',     icon: '🗺️', label: 'Blocks & Zones' },
]

// ── Resize logic ──────────────────────────────────────────
const MIN_WIDTH = 60
const MAX_WIDTH = 320
const STORAGE_KEY = 'admin_sidebar_width'
const DEFAULT_WIDTH = 224  // w-56 = 224px

const sidebarWidth = ref(DEFAULT_WIDTH)
const isDragging = ref(false)

// Restore saved width on mount
onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved) {
    const parsed = parseInt(saved)
    if (!isNaN(parsed) && parsed >= MIN_WIDTH && parsed <= MAX_WIDTH) {
      sidebarWidth.value = parsed
    }
  }
})

function startDrag(e) {
  e.preventDefault()
  isDragging.value = true

  const startX = e.clientX
  const startWidth = sidebarWidth.value

  function onMouseMove(e) {
    const delta = e.clientX - startX
    const newWidth = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, startWidth + delta))
    sidebarWidth.value = newWidth
  }

  function onMouseUp() {
    isDragging.value = false
    // Width save karo localStorage mein
    localStorage.setItem(STORAGE_KEY, sidebarWidth.value)
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    // Cursor reset karo
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
  }

  // Drag ke dauran cursor aur selection fix karo
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

function doLogout() {
  auth.logout()
  cart.reset()
  router.push('/login')
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.15s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
