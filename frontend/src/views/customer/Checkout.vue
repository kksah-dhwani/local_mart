<template>
  <div>
    <Navbar />
    <div class="max-w-5xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Checkout</h1>

      <div class="grid md:grid-cols-3 gap-6">
        <!-- Left -->
        <div class="md:col-span-2 space-y-4">

          <!-- Address Selection -->
          <div class="card p-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="font-bold text-gray-900">Delivery Address</h2>
              <router-link to="/profile" class="text-sm text-blue-600 hover:underline">
                + Add Address
              </router-link>
            </div>

            <div v-if="addresses.length === 0" class="text-center py-6 text-gray-500">
              <p>No addresses saved.
                <router-link to="/profile" class="text-blue-600 underline">Add one now</router-link>
              </p>
            </div>

            <div v-else class="space-y-3">
              <label
                v-for="addr in addresses"
                :key="addr.id"
                :class="[
                  'flex gap-3 p-3 border-2 rounded-lg cursor-pointer transition',
                  selectedAddressId === addr.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300',
                ]"
              >
                <input
                  type="radio"
                  v-model="selectedAddressId"
                  :value="addr.id"
                  class="mt-1"
                  @change="calculateDelivery"
                />
                <div>
                  <p class="font-semibold text-sm">
                    {{ addr.label }}
                    <span v-if="addr.is_default" class="text-xs text-green-600">(Default)</span>
                  </p>
                  <p class="text-sm text-gray-700">
                    {{ addr.address_line1 }}<span v-if="addr.address_line2">, {{ addr.address_line2 }}</span>
                  </p>
                  <p v-if="addr.landmark" class="text-xs text-gray-500">Near {{ addr.landmark }}</p>
                  <p class="text-xs text-blue-600 font-medium mt-1">
                    {{ addr.block?.name }} — {{ addr.zone?.zone_name }}
                  </p>
                </div>
              </label>
            </div>
          </div>

          <!-- Delivery Info Message -->
          <div
            v-if="deliveryInfo"
            :class="[
              'p-3 rounded-lg text-sm font-medium',
              deliveryInfo.is_deliverable ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700',
            ]"
          >
            {{ deliveryInfo.message }}
            <span v-if="deliveryInfo.free_delivery_above && cart.subtotal < deliveryInfo.free_delivery_above">
              — Free delivery above ₹{{ deliveryInfo.free_delivery_above }}
            </span>
          </div>

          <!-- Payment Method -->
          <div class="card p-5">
            <h2 class="font-bold text-gray-900 mb-3">Payment Method</h2>
            <div class="grid grid-cols-2 gap-3">

              <label :class="[
                'border-2 rounded-xl p-4 cursor-pointer text-center transition',
                paymentMethod === 'cod'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]">
                <input type="radio" v-model="paymentMethod" value="cod" class="hidden" />
                <p class="text-2xl mb-1">💵</p>
                <p class="font-semibold text-sm text-gray-900">Cash on Delivery</p>
                <p class="text-xs text-gray-500 mt-0.5">Pay when delivered</p>
              </label>

              <label :class="[
                'border-2 rounded-xl p-4 cursor-pointer text-center transition',
                paymentMethod === 'online'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              ]">
                <input type="radio" v-model="paymentMethod" value="online" class="hidden" />
                <p class="text-2xl mb-1">💳</p>
                <p class="font-semibold text-sm text-gray-900">Pay Online</p>
                <p class="text-xs text-gray-500 mt-0.5">UPI / Card / Net Banking</p>
              </label>

            </div>

            <div
              v-if="paymentMethod === 'online'"
              class="mt-3 flex items-center gap-2 text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2"
            >
              <span>🔒</span>
              <span>Secured by Razorpay — UPI, Debit/Credit Card, Net Banking supported</span>
            </div>
          </div>

          <!-- Order Notes -->
          <div class="card p-5">
            <h2 class="font-bold text-gray-900 mb-3">Order Notes (Optional)</h2>
            <textarea
              v-model="notes"
              rows="3"
              placeholder="Any special instructions..."
              class="input-field resize-none"
            ></textarea>
          </div>

        </div>

        <!-- Right: Summary -->
        <div class="card p-5 h-fit sticky top-20">
          <h2 class="font-bold text-gray-900 mb-4">Order Summary</h2>

          <div class="space-y-2 text-sm mb-4">
            <div
              v-for="item in cart.cart.items"
              :key="item.id"
              class="flex justify-between text-gray-600"
            >
              <span class="truncate mr-2">{{ item.product.name }} × {{ item.quantity }}</span>
              <span class="font-medium flex-shrink-0">
                ₹{{ (item.product.price * item.quantity).toFixed(2) }}
              </span>
            </div>
          </div>

          <hr class="mb-3" />

          <div class="space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Subtotal</span>
              <span class="font-semibold">₹{{ cart.subtotal.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Delivery</span>
              <span class="font-semibold">
                {{
                  deliveryInfo
                    ? deliveryInfo.delivery_charge == 0
                      ? 'FREE'
                      : `₹${deliveryInfo.delivery_charge}`
                    : '—'
                }}
              </span>
            </div>
          </div>

          <hr class="my-3" />

          <div class="flex justify-between text-base font-bold mb-1">
            <span>Total</span>
            <span class="text-blue-600">₹{{ total.toFixed(2) }}</span>
          </div>

          <p class="text-xs text-gray-400 mb-4">
            {{ paymentMethod === 'online' ? '💳 Online Payment via Razorpay' : '💵 Cash on Delivery' }}
          </p>

          <button
            @click="placeOrder"
            :disabled="placing || !deliveryInfo?.is_deliverable || !selectedAddressId"
            class="btn-primary w-full py-3"
          >
            <span v-if="placing" class="flex items-center justify-center gap-2">
              <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
              </svg>
              Processing...
            </span>
            <span v-else>
              {{ paymentMethod === 'online' ? `💳 Pay ₹${total.toFixed(2)}` : '✅ Place Order (COD)' }}
            </span>
          </button>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '@/components/common/Navbar.vue'
import { useCartStore } from '@/stores/cart'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api'

const router = useRouter()
const cart = useCartStore()
const toast = useToastStore()

const addresses = ref([])
const selectedAddressId = ref(null)
const deliveryInfo = ref(null)
const notes = ref('')
const placing = ref(false)
const paymentMethod = ref('cod')

// ── Total ────────────────────────────────────────────────
const total = computed(() => {
  const d = deliveryInfo.value?.delivery_charge || 0
  return cart.subtotal + Number(d)
})

// ── Fetch Addresses ──────────────────────────────────────
async function fetchAddresses() {
  const res = await api.get('/addresses')
  addresses.value = res.data
  const def = res.data.find(a => a.is_default)
  if (def) {
    selectedAddressId.value = def.id
    calculateDelivery()
  }
}

// ── Delivery Charge Calculation ──────────────────────────
async function calculateDelivery() {
  if (!selectedAddressId.value) return
  try {
    const res = await api.get('/delivery/calculate', {
      params: { address_id: selectedAddressId.value }
    })
    deliveryInfo.value = res.data
  } catch {
    deliveryInfo.value = null
  }
}

// ── Main Order Handler ───────────────────────────────────
async function placeOrder() {
  if (!selectedAddressId.value) {
    return toast.error('Please select a delivery address')
  }
  if (!deliveryInfo.value?.is_deliverable) {
    return toast.error('Delivery not available at selected address')
  }

  placing.value = true
  try {
    if (paymentMethod.value === 'online') {
      await handleOnlinePayment()
    } else {
      await handleCOD()
    }
  } catch (e) {
    if (e?.message !== 'payment_cancelled') {
      toast.error(e.response?.data?.detail || 'Failed to place order')
    }
  } finally {
    placing.value = false
  }
}

// ── COD Flow ─────────────────────────────────────────────
async function handleCOD() {
  const res = await api.post('/orders/checkout', {
    address_id: selectedAddressId.value,
    notes: notes.value,
  })
  await cart.fetchCart()
  toast.success('Order placed successfully!')
  router.push(`/orders/${res.data.order.id}`)
}

// ── Razorpay Online Payment Flow ─────────────────────────
async function handleOnlinePayment() {
  if (!window.Razorpay) {
    toast.error('Razorpay failed to load. Check your internet connection.')
    return
  }

  // Step 1: Backend se Razorpay order banao
  const res = await api.post('/payments/create-order', {
    address_id: selectedAddressId.value,
    notes: notes.value,
  })
  const rzpData = res.data

  // Step 2: Razorpay popup kholo
  await new Promise((resolve, reject) => {
    const options = {
      key: rzpData.key_id,
      amount: rzpData.amount,
      currency: rzpData.currency,
      name: 'Local Mart',
      description: 'Order Payment',
      image: '/vite.svg',
      order_id: rzpData.razorpay_order_id,
      prefill: {
        name: rzpData.user_name,
        email: rzpData.user_email,
        contact: rzpData.user_phone,
      },
      theme: { color: '#2563eb' },

      // Step 3: Payment success hone par backend se verify karo
      handler: async (response) => {
        try {
          const verifyRes = await api.post('/payments/verify', {
            razorpay_order_id: response.razorpay_order_id,
            razorpay_payment_id: response.razorpay_payment_id,
            razorpay_signature: response.razorpay_signature,
            address_id: selectedAddressId.value,
            notes: notes.value,
          })
          await cart.fetchCart()
          toast.success('Payment successful! Order confirmed 🎉')
          router.push(`/orders/${verifyRes.data.order_id}`)
          resolve()
        } catch (err) {
          toast.error('Payment verification failed. Please contact support.')
          reject(err)
        }
      },

      modal: {
        ondismiss: () => {
          toast.info('Payment cancelled.')
          reject(new Error('payment_cancelled'))
        },
      },
    }

    const rzp = new window.Razorpay(options)

    rzp.on('payment.failed', (response) => {
      toast.error(`Payment failed: ${response.error.description}`)
      reject(new Error(response.error.description))
    })

    rzp.open()
  })
}

// ── Lifecycle ────────────────────────────────────────────
onMounted(() => {
  if (cart.cart.items.length === 0) {
    router.push('/cart')
  } else {
    fetchAddresses()
  }
})
</script>
