<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">

      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Users</h1>
        <span class="text-sm text-gray-500">{{ total }} registered customers</span>
      </div>

      <!-- Search -->
      <div class="mb-4">
        <input
          v-model="search"
          @input="debouncedFetch"
          type="text"
          placeholder="🔍 Search by name, email or phone..."
          class="input-field max-w-sm"
        />
      </div>

      <LoadingSpinner v-if="loading" />
      <div v-else class="card overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b text-left text-gray-500">
            <tr>
              <th class="px-4 py-3">Customer</th>
              <th class="px-4 py-3">Phone</th>
              <th class="px-4 py-3">Joined</th>
              <th class="px-4 py-3">Orders</th>
              <th class="px-4 py-3">Spent</th>
              <th class="px-4 py-3">Last Order</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="u in users"
              :key="u.id"
              class="hover:bg-gray-50 cursor-pointer"
              @click="openUser(u)"
            >
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold text-sm flex items-center justify-center flex-shrink-0">
                    {{ u.name?.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <p class="font-medium text-gray-900">{{ u.name }}</p>
                    <p class="text-xs text-gray-500">{{ u.email }}</p>
                  </div>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-700">{{ u.phone || '—' }}</td>
              <td class="px-4 py-3 text-gray-500 text-xs">{{ formatDate(u.joined_at) }}</td>
              <td class="px-4 py-3">
                <span :class="[
                  'font-bold text-sm',
                  u.order_count > 0 ? 'text-blue-600' : 'text-gray-400'
                ]">{{ u.order_count }}</span>
              </td>
              <td class="px-4 py-3">
                <span :class="u.total_spent > 0 ? 'text-green-600 font-semibold' : 'text-gray-400'">
                  {{ u.total_spent > 0 ? '₹' + u.total_spent.toFixed(0) : '₹0' }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-gray-500">
                {{ u.last_order_at ? formatDate(u.last_order_at) : '—' }}
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="users.length === 0" class="text-center py-14 text-gray-400">
          <p class="text-3xl mb-2">👥</p>
          <p>No users found.</p>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="total > limit" class="flex justify-center gap-2 mt-4">
        <button
          @click="page--; fetchUsers()"
          :disabled="page === 1"
          class="btn-secondary text-sm py-1.5 disabled:opacity-40"
        >← Prev</button>
        <span class="text-sm text-gray-600 py-1.5 px-2">Page {{ page }}</span>
        <button
          @click="page++; fetchUsers()"
          :disabled="page * limit >= total"
          class="btn-secondary text-sm py-1.5 disabled:opacity-40"
        >Next →</button>
      </div>

      <!-- User Detail Modal -->
      <div v-if="selectedUser" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto">
          <div class="p-5 border-b flex items-center justify-between sticky top-0 bg-white">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">
                {{ selectedUser.name?.charAt(0).toUpperCase() }}
              </div>
              <div>
                <p class="font-bold text-gray-900">{{ selectedUser.name }}</p>
                <p class="text-xs text-gray-500">{{ selectedUser.email }}</p>
              </div>
            </div>
            <button @click="selectedUser = null; userOrders = []" class="text-gray-400 hover:text-gray-700 text-xl">✕</button>
          </div>

          <div class="p-5">
            <!-- User Stats -->
            <div class="grid grid-cols-3 gap-3 mb-5">
              <div class="bg-blue-50 rounded-xl p-3 text-center">
                <p class="text-2xl font-bold text-blue-600">{{ selectedUser.order_count }}</p>
                <p class="text-xs text-blue-500">Total Orders</p>
              </div>
              <div class="bg-green-50 rounded-xl p-3 text-center">
                <p class="text-2xl font-bold text-green-600">₹{{ selectedUser.total_spent.toFixed(0) }}</p>
                <p class="text-xs text-green-500">Total Spent</p>
              </div>
              <div class="bg-gray-50 rounded-xl p-3 text-center">
                <p class="text-sm font-bold text-gray-700">{{ formatDate(selectedUser.joined_at) }}</p>
                <p class="text-xs text-gray-400">Joined</p>
              </div>
            </div>

            <!-- User Orders -->
            <h3 class="font-bold text-gray-900 mb-3">Order History</h3>
            <LoadingSpinner v-if="ordersLoading" />
            <div v-else-if="userOrders.length === 0" class="text-center py-8 text-gray-400">
              <p>No orders yet.</p>
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="o in userOrders"
                :key="o.id"
                class="border border-gray-100 rounded-xl p-3 flex items-center justify-between"
              >
                <div>
                  <p class="font-semibold text-gray-900 text-sm">#{{ o.id }}</p>
                  <p class="text-xs text-gray-500">{{ formatDate(o.ordered_at) }}</p>
                  <p class="text-xs text-gray-400 mt-0.5">{{ o.snap_block_name }} · {{ o.item_count }} item(s)</p>
                </div>
                <div class="text-right">
                  <p class="font-bold text-gray-900">₹{{ o.total_amount }}</p>
                  <span :class="`badge-${o.status} text-xs`">{{ o.status }}</span>
                  <p class="text-xs text-gray-400 mt-0.5">
                    {{ o.payment_method === 'online' ? '💳' : '💵' }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '@/components/admin/Sidebar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import api from '@/services/api'

const users        = ref([])
const loading      = ref(true)
const search       = ref('')
const page         = ref(1)
const limit        = ref(20)
const total        = ref(0)
const selectedUser = ref(null)
const userOrders   = ref([])
const ordersLoading = ref(false)

let debounceTimer = null

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }) : ''
}

async function fetchUsers() {
  loading.value = true
  try {
    const res = await api.get('/admin/users', {
      params: { page: page.value, limit: limit.value, search: search.value || undefined }
    })
    users.value = res.data.users
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function debouncedFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => { page.value = 1; fetchUsers() }, 400)
}

async function openUser(user) {
  selectedUser.value = user
  ordersLoading.value = true
  userOrders.value = []
  try {
    const res = await api.get('/admin/orders', {
      params: { limit: 100 }
    })
    // Filter orders for this user
    userOrders.value = res.data.orders.filter(o => o.user_id === user.id)
  } finally {
    ordersLoading.value = false
  }
}

onMounted(fetchUsers)
</script>
