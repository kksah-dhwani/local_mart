<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">

      <div class="flex items-center justify-between mb-6">
        <h1 class="text-2xl font-bold text-gray-900">Order Analytics</h1>
      </div>

      <!-- Date Filter -->
      <div class="card p-4 mb-5 flex flex-wrap items-center gap-3">
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500 font-medium">From</label>
          <input type="date" v-model="fromDate" class="input-field text-sm py-1.5" />
        </div>
        <div class="flex items-center gap-2">
          <label class="text-xs text-gray-500 font-medium">To</label>
          <input type="date" v-model="toDate" class="input-field text-sm py-1.5" />
        </div>
        <button @click="fetchAnalytics" class="btn-primary text-sm py-1.5">Apply Filter</button>

        <!-- Quick shortcuts -->
        <div class="flex gap-2 ml-auto">
          <button
            v-for="q in quickFilters" :key="q.label"
            @click="applyQuick(q)"
            class="text-xs px-3 py-1.5 rounded-full border border-gray-300 hover:border-blue-400 hover:text-blue-600 text-gray-600 transition"
          >{{ q.label }}</button>
        </div>
      </div>

      <LoadingSpinner v-if="loading" />
      <template v-else>

        <!-- Summary Cards -->
        <div class="grid grid-cols-3 gap-4 mb-5">
          <div class="card p-4">
            <p class="text-xs text-gray-500 mb-1">Total Orders</p>
            <p class="text-3xl font-bold text-gray-900">{{ analytics.total_orders }}</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-gray-500 mb-1">Revenue</p>
            <p class="text-3xl font-bold text-green-600">₹{{ analytics.total_revenue?.toFixed(0) }}</p>
            <p class="text-xs text-gray-400">Excluding cancelled</p>
          </div>
          <div class="card p-4">
            <p class="text-xs text-gray-500 mb-1">Avg per Day</p>
            <p class="text-3xl font-bold text-blue-600">
              {{ analytics.by_date?.length ? (analytics.total_orders / analytics.by_date.length).toFixed(1) : 0 }}
            </p>
          </div>
        </div>

        <!-- Date-wise breakdown -->
        <div class="space-y-3">
          <div
            v-for="day in analytics.by_date"
            :key="day.date"
            class="card overflow-hidden"
          >
            <!-- Day Header -->
            <div
              class="px-4 py-3 flex items-center justify-between cursor-pointer hover:bg-gray-50"
              @click="toggleDay(day.date)"
            >
              <div class="flex items-center gap-3">
                <span class="text-lg">📅</span>
                <div>
                  <p class="font-bold text-gray-900">{{ formatDisplayDate(day.date) }}</p>
                  <p class="text-xs text-gray-500">{{ day.count }} order(s) · ₹{{ day.revenue.toFixed(0) }} revenue</p>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div class="flex gap-2">
                  <span class="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
                    {{ day.count }} orders
                  </span>
                  <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-medium">
                    ₹{{ day.revenue.toFixed(0) }}
                  </span>
                </div>
                <span class="text-gray-400 text-sm">{{ expandedDays.includes(day.date) ? '▲' : '▼' }}</span>
              </div>
            </div>

            <!-- Day Orders (expanded) -->
            <div v-if="expandedDays.includes(day.date)" class="border-t border-gray-100">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr class="text-xs text-gray-500 text-left">
                    <th class="px-4 py-2">Order</th>
                    <th class="px-4 py-2">Customer</th>
                    <th class="px-4 py-2">Time</th>
                    <th class="px-4 py-2">Amount</th>
                    <th class="px-4 py-2">Payment</th>
                    <th class="px-4 py-2">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-for="o in day.orders" :key="o.id" class="hover:bg-gray-50">
                    <td class="px-4 py-2 font-bold text-gray-900">#{{ o.id }}</td>
                    <td class="px-4 py-2">
                      <p class="font-medium text-gray-800">{{ o.user_name }}</p>
                      <p class="text-xs text-gray-500">📞 {{ o.user_phone }}</p>
                    </td>
                    <td class="px-4 py-2 text-xs text-gray-500">{{ formatTime(o.ordered_at) }}</td>
                    <td class="px-4 py-2 font-bold text-gray-900">₹{{ o.total_amount }}</td>
                    <td class="px-4 py-2">
                      <span v-if="o.payment_method === 'online'"
                        class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">💳 Paid</span>
                      <span v-else
                        class="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">💵 COD</span>
                    </td>
                    <td class="px-4 py-2">
                      <span :class="`badge-${o.status} text-xs`">{{ o.status }}</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="analytics.by_date?.length === 0" class="text-center py-14 text-gray-400">
            <p class="text-4xl mb-3">📭</p>
            <p>No orders in selected period.</p>
          </div>
        </div>

      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '@/components/admin/Sidebar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import api from '@/services/api'

const analytics   = ref({ total_orders: 0, total_revenue: 0, by_date: [] })
const loading     = ref(true)
const fromDate    = ref('')
const toDate      = ref('')
const expandedDays = ref([])

// Default — last 30 days
const today = new Date()
toDate.value   = today.toISOString().split('T')[0]
fromDate.value = new Date(today - 30 * 86400000).toISOString().split('T')[0]

const quickFilters = [
  { label: 'Today',    days: 0 },
  { label: 'Last 7d',  days: 7 },
  { label: 'Last 30d', days: 30 },
  { label: 'Last 90d', days: 90 },
]

function applyQuick(q) {
  const t = new Date()
  toDate.value   = t.toISOString().split('T')[0]
  fromDate.value = new Date(t - q.days * 86400000).toISOString().split('T')[0]
  fetchAnalytics()
}

function toggleDay(date) {
  const i = expandedDays.value.indexOf(date)
  if (i >= 0) expandedDays.value.splice(i, 1)
  else expandedDays.value.push(date)
}

function formatDisplayDate(d) {
  return new Date(d).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
}

function formatTime(d) {
  return d ? new Date(d).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : ''
}

async function fetchAnalytics() {
  loading.value = true
  expandedDays.value = []
  try {
    const res = await api.get('/admin/analytics/orders', {
      params: { from_date: fromDate.value, to_date: toDate.value }
    })
    analytics.value = res.data
    // Auto-expand agar sirf 1 din ka data ho
    if (res.data.by_date?.length === 1) {
      expandedDays.value = [res.data.by_date[0].date]
    }
  } finally {
    loading.value = false
  }
}

onMounted(fetchAnalytics)
</script>
