<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">

      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-xs text-gray-400">Today: {{ todayDate }}</p>
      </div>

      <LoadingSpinner v-if="loading" />
      <template v-else>

        <!-- ── Stat Cards ── -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div class="card p-4">
            <p class="text-xs text-gray-500 mb-1">Total Users</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.total_users }}</p>
            <p class="text-xs text-green-600 mt-1">+{{ stats.new_users_7d }} this week</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-gray-500 mb-1">Users Ordered</p>
            <p class="text-3xl font-bold text-blue-600">{{ stats.users_with_orders }}</p>
            <p class="text-xs text-gray-400 mt-1">out of {{ stats.total_users }} registered</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-gray-500 mb-1">Total Orders</p>
            <p class="text-3xl font-bold text-gray-900">{{ stats.total_orders }}</p>
            <p class="text-xs text-orange-500 mt-1">{{ stats.status_counts.pending }} pending</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-gray-500 mb-1">Revenue (Delivered)</p>
            <p class="text-3xl font-bold text-green-600">₹{{ stats.total_revenue.toFixed(0) }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ stats.status_counts.delivered }} orders</p>
          </div>
        </div>

        <!-- ── Order Status Breakdown ── -->
        <div class="card p-5 mb-6">
          <h2 class="font-bold text-gray-900 mb-4">Order Status Breakdown</h2>
          <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div v-for="s in statusList" :key="s.key"
              class="rounded-xl p-3 text-center"
              :style="{ backgroundColor: s.bg }"
            >
              <p class="text-2xl mb-1">{{ s.icon }}</p>
              <p class="text-2xl font-bold" :style="{ color: s.color }">
                {{ stats.status_counts[s.key] || 0 }}
              </p>
              <p class="text-xs font-medium mt-0.5" :style="{ color: s.color }">{{ s.label }}</p>
            </div>
          </div>
        </div>

        <!-- ── Last 7 Days Chart (simple bar) ── -->
        <div class="card p-5 mb-6">
          <h2 class="font-bold text-gray-900 mb-4">Orders — Last 7 Days</h2>
          <div class="flex items-end gap-2 h-32">
            <div
              v-for="day in stats.orders_by_day"
              :key="day.date"
              class="flex-1 flex flex-col items-center gap-1"
            >
              <p class="text-xs font-bold text-gray-700">{{ day.orders || '' }}</p>
              <div
                class="w-full rounded-t-md bg-blue-500 transition-all"
                :style="{ height: barHeight(day.orders) }"
                :title="`${day.date}: ${day.orders} orders, ₹${day.revenue}`"
              ></div>
              <p class="text-xs text-gray-400">{{ day.date }}</p>
            </div>
          </div>
          <div class="mt-3 flex gap-6 text-xs text-gray-500">
            <span>Total this week:
              <strong class="text-gray-900">{{ weekTotal }} orders</strong>
            </span>
            <span>Revenue:
              <strong class="text-green-600">₹{{ weekRevenue.toFixed(0) }}</strong>
            </span>
          </div>
        </div>

        <div class="grid md:grid-cols-2 gap-6">

          <!-- ── Recent Orders ── -->
          <div class="card p-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="font-bold text-gray-900">Recent Orders</h2>
              <router-link to="/admin/orders" class="text-xs text-blue-600 hover:underline">View all →</router-link>
            </div>
            <div class="space-y-3">
              <div
                v-for="o in stats.recent_orders"
                :key="o.id"
                class="flex items-center justify-between py-2 border-b border-gray-50 last:border-0"
              >
                <div>
                  <p class="text-sm font-semibold text-gray-900">#{{ o.id }} — {{ o.user_name }}</p>
                  <p class="text-xs text-gray-500">{{ formatDate(o.ordered_at) }}</p>
                </div>
                <div class="text-right">
                  <p class="text-sm font-bold text-gray-900">₹{{ o.total_amount }}</p>
                  <span :class="`badge-${o.status} text-xs`">{{ o.status }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- ── Top Products ── -->
          <div class="card p-5">
            <h2 class="font-bold text-gray-900 mb-4">Top Selling Products</h2>
            <div class="space-y-3">
              <div
                v-for="(p, i) in stats.top_products"
                :key="p.name"
                class="flex items-center gap-3"
              >
                <span class="w-6 h-6 rounded-full bg-blue-100 text-blue-700 text-xs font-bold flex items-center justify-center flex-shrink-0">
                  {{ i + 1 }}
                </span>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">{{ p.name }}</p>
                  <p class="text-xs text-gray-500">{{ p.sold }} sold · ₹{{ p.revenue.toFixed(0) }}</p>
                </div>
              </div>
              <p v-if="stats.top_products.length === 0" class="text-sm text-gray-400">No orders yet.</p>
            </div>
          </div>

        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminSidebar from '@/components/admin/Sidebar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import api from '@/services/api'

const loading = ref(true)
const stats = ref({
  total_users: 0, total_orders: 0, total_revenue: 0,
  users_with_orders: 0, new_users_7d: 0, total_products: 0,
  status_counts: {}, orders_by_day: [], recent_orders: [], top_products: [],
})

const todayDate = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })

const statusList = [
  { key: 'pending',          label: 'Pending',          icon: '⏳', color: '#92400e', bg: '#fef9c3' },
  { key: 'confirmed',        label: 'Confirmed',         icon: '✅', color: '#1e40af', bg: '#dbeafe' },
  { key: 'out_for_delivery', label: 'Out for Delivery',  icon: '🚴', color: '#5b21b6', bg: '#ede9fe' },
  { key: 'delivered',        label: 'Delivered',          icon: '🎉', color: '#166534', bg: '#dcfce7' },
  { key: 'cancelled',        label: 'Cancelled',          icon: '❌', color: '#991b1b', bg: '#fee2e2' },
]

const maxOrders = computed(() => Math.max(...(stats.value.orders_by_day.map(d => d.orders) || [1]), 1))
const weekTotal  = computed(() => stats.value.orders_by_day.reduce((s, d) => s + d.orders, 0))
const weekRevenue = computed(() => stats.value.orders_by_day.reduce((s, d) => s + d.revenue, 0))

function barHeight(count) {
  if (!count) return '4px'
  return Math.max((count / maxOrders.value) * 100, 8) + 'px'
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''
}

onMounted(async () => {
  const res = await api.get('/admin/dashboard')
  stats.value = res.data
  loading.value = false
})
</script>
