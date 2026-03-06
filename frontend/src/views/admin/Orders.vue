<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">
      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">Orders</h1>
          <p class="text-xs text-gray-400 mt-0.5">
            Auto-refreshes every 30s
            <span v-if="lastRefreshed" class="ml-1"
              >— Last updated {{ lastRefreshed }}</span
            >
          </p>
        </div>

        <!-- Live indicator + manual refresh -->
        <div class="flex items-center gap-3">
          <div
            class="flex items-center gap-1.5 text-xs text-green-600 font-medium"
          >
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Live
          </div>
          <button @click="fetchOrders" class="btn-secondary text-sm py-1.5">
            🔄 Refresh
          </button>
        </div>
      </div>

      <!-- New order alert banner -->
      <transition name="slide-down">
        <div
          v-if="newOrderAlert"
          class="mb-4 bg-blue-600 text-white px-4 py-3 rounded-xl flex items-center justify-between shadow-lg"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">🛒</span>
            <div>
              <p class="font-bold text-sm">New order received!</p>
              <p class="text-xs text-blue-100">
                {{ newOrderAlert }} new pending order(s) waiting for
                confirmation
              </p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="filterAndDismiss"
              class="bg-white text-blue-600 text-xs font-bold px-3 py-1.5 rounded-lg hover:bg-blue-50"
            >
              View Pending
            </button>
            <button
              @click="newOrderAlert = null"
              class="text-blue-200 hover:text-white text-lg leading-none"
            >
              ✕
            </button>
          </div>
        </div>
      </transition>

      <!-- Filter Tabs -->
      <div class="flex gap-2 mb-4 overflow-x-auto pb-1">
        <button
          v-for="s in statuses"
          :key="s.value"
          @click="activeFilter = s.value; fetchOrders();"
          :class="[
            'px-4 py-1.5 rounded-full text-sm font-medium flex-shrink-0 transition flex items-center gap-1.5',
            activeFilter === s.value
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-600 border hover:border-blue-300',
          ]"
        >
          {{ s.label }}
          <span
            v-if="s.value === 'pending' && pendingCount > 0"
            class="bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center"
          >
            {{ pendingCount > 9 ? "9+" : pendingCount }}
          </span>
        </button>
      </div>

      <!-- Orders Table -->
      <LoadingSpinner v-if="loading" />
      <div v-else class="card overflow-hidden">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b">
            <tr class="text-left text-gray-500">
              <th class="px-4 py-3">Order</th>
              <th class="px-4 py-3">Customer</th>
              <th class="px-4 py-3">Area</th>
              <th class="px-4 py-3">Amount</th>
              <th class="px-4 py-3">Payment</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Action</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="order in orders"
              :key="order.id"
              :class="[
                'hover:bg-gray-50 transition',
                order.status === 'pending' ? 'bg-yellow-50/40' : '',
              ]"
            >
              <!-- Order -->
              <td class="px-4 py-3">
                <p class="font-bold text-gray-900">#{{ order.id }}</p>
                <p class="text-xs text-gray-500">
                  {{ formatDate(order.ordered_at) }}
                </p>
                <p class="text-xs text-gray-400">
                  {{ order.item_count }} item(s)
                </p>
              </td>

              <!-- Customer -->
              <td class="px-4 py-3">
                <p class="font-medium text-gray-900">{{ order.user_name }}</p>
                <p class="text-xs text-gray-500">📞 {{ order.user_phone }}</p>
              </td>

              <!-- Area -->
              <td class="px-4 py-3">
                <p class="text-xs font-medium text-gray-900">
                  {{ order.snap_block_name }}
                </p>
                <p class="text-xs text-gray-500">{{ order.snap_zone_name }}</p>
              </td>

              <!-- Amount -->
              <td class="px-4 py-3">
                <p class="font-bold text-gray-900">₹{{ order.total_amount }}</p>
              </td>

              <!-- Payment -->
              <td class="px-4 py-3">
                <span
                  v-if="order.payment_method === 'online'"
                  class="bg-green-100 text-green-700 text-xs font-medium px-2 py-0.5 rounded-full"
                >
                  💳 Paid
                </span>
                <span
                  v-else
                  class="bg-yellow-100 text-yellow-700 text-xs font-medium px-2 py-0.5 rounded-full"
                >
                  💵 COD
                </span>
              </td>

              <!-- Current Status Badge -->
              <td class="px-4 py-3">
                <span :class="`badge-${order.status}`">
                  {{ statusConfig[order.status]?.icon }}
                  {{ statusConfig[order.status]?.label }}
                </span>
              </td>

              <!-- Action — sirf allowed next steps ke buttons -->
              <td class="px-4 py-3">
                <div
                  v-if="order.allowed_next && order.allowed_next.length > 0"
                  class="flex flex-col gap-1.5"
                >
                  <button
                    v-for="next in order.allowed_next"
                    :key="next"
                    @click="updateStatus(order.id, next)"
                    :disabled="updating === order.id"
                    :class="[
                      'text-xs font-semibold px-3 py-1.5 rounded-lg transition whitespace-nowrap disabled:opacity-50',
                      next === 'cancelled'
                        ? 'bg-red-100 text-red-600 hover:bg-red-200 border border-red-200'
                        : 'bg-blue-600 text-white hover:bg-blue-700',
                    ]"
                  >
                    <span v-if="updating === order.id">⏳ Wait...</span>
                    <span v-else>{{ statusConfig[next]?.action }}</span>
                  </button>
                </div>

                <!-- Final state — koi action nahi -->
                <p v-else class="text-xs text-gray-400 italic">
                  {{ order.status === 'delivered' ? '✅ Completed' : '❌ Cancelled' }}
                </p>
              </td>
            </tr>
          </tbody>
        </table>

        <div v-if="orders.length === 0" class="text-center py-14 text-gray-400">
          <p class="text-3xl mb-2">📭</p>
          <p>No orders found.</p>
        </div>
      </div>

      <!-- Total count -->
      <p v-if="totalOrders > 0" class="text-xs text-gray-400 mt-3 text-right">
        Showing {{ orders.length }} of {{ totalOrders }} orders
      </p>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import AdminSidebar from "@/components/admin/Sidebar.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import { useToastStore } from "@/stores/toast";
import api from "@/services/api";

const toast = useToastStore();

const orders = ref([]);
const loading = ref(true);
const updating = ref(null);
const activeFilter = ref("");
const totalOrders = ref(0);
const pendingCount = ref(0);
const lastRefreshed = ref("");
const newOrderAlert = ref(null);

// Polling state
let pollingTimer = null;
let previousPendingCount = 0;

// ── Status config — label, icon, action button text ──────
const statusConfig = {
  pending:          { label: "Pending",          icon: "⏳", action: null },
  confirmed:        { label: "Confirmed",         icon: "✅", action: "✅ Confirm Order" },
  out_for_delivery: { label: "Out for Delivery",  icon: "🚴", action: "🚴 Out for Delivery" },
  delivered:        { label: "Delivered",          icon: "🎉", action: "🎉 Mark Delivered" },
  cancelled:        { label: "Cancelled",          icon: "❌", action: "❌ Cancel Order" },
};

const statuses = [
  { value: "",                 label: "All" },
  { value: "pending",          label: "Pending" },
  { value: "confirmed",        label: "Confirmed" },
  { value: "out_for_delivery", label: "Out for Delivery" },
  { value: "delivered",        label: "Delivered" },
  { value: "cancelled",        label: "Cancelled" },
];

function formatDate(d) {
  return d
    ? new Date(d).toLocaleDateString("en-IN", {
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";
}

function formatStatus(s) {
  return statuses.find((x) => x.value === s)?.label || s;
}

// ── Fetch Orders ─────────────────────────────────────────
async function fetchOrders(silent = false) {
  if (!silent) loading.value = true;
  try {
    const params = { limit: 100 };
    if (activeFilter.value) params.status = activeFilter.value;
    const res = await api.get("/admin/orders", { params });
    orders.value = res.data.orders;
    totalOrders.value = res.data.total;

    // Update last refreshed time
    const now = new Date();
    lastRefreshed.value = now.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } finally {
    if (!silent) loading.value = false;
  }
}

// ── Fetch Pending Count (for polling) ───────────────────
async function fetchPendingCount() {
  try {
    const res = await api.get("/admin/orders", {
      params: { status: "pending", limit: 1 },
    });
    const currentPending = res.data.total;
    pendingCount.value = currentPending;

    // Naye orders aaye hain?
    if (previousPendingCount > 0 && currentPending > previousPendingCount) {
      const newCount = currentPending - previousPendingCount;
      newOrderAlert.value = newCount;

      // Browser notification (agar permission hai)
      if (Notification.permission === "granted") {
        new Notification("🛒 New Order on Local Mart!", {
          body: `${newCount} new order(s) waiting for confirmation`,
          icon: "/vite.svg",
        });
      }

      // Table silently refresh karo
      await fetchOrders(true);
    }

    previousPendingCount = currentPending;
  } catch {}
}

// ── Update Order Status ──────────────────────────────────
async function updateStatus(orderId, newStatus) {
  updating.value = orderId;
  try {
    await api.patch(`/admin/orders/${orderId}/status`, { status: newStatus });
    toast.success(`Order #${orderId} → ${statusConfig[newStatus]?.label}`);
    await fetchOrders(true);
    await fetchPendingCount();
  } catch (e) {
    toast.error(e.response?.data?.detail || "Failed to update status");
  } finally {
    updating.value = null;
  }
}

// ── Filter to pending and dismiss alert ─────────────────
function filterAndDismiss() {
  activeFilter.value = "pending";
  fetchOrders();
  newOrderAlert.value = null;
}

// ── Start Polling ────────────────────────────────────────
function startPolling() {
  // Browser notification permission maango
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }

  // Har 30 second mein pending count check karo
  pollingTimer = setInterval(async () => {
    await fetchPendingCount();
  }, 30000);
}

// ── Lifecycle ────────────────────────────────────────────
onMounted(async () => {
  await fetchOrders();
  await fetchPendingCount();
  startPolling();
});

onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer);
});
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}
.slide-down-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}
.slide-down-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
</style>
