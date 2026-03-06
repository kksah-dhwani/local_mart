<template>
  <div>
    <Navbar />
    <div class="max-w-4xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>
      <div class="grid md:grid-cols-2 gap-6">
        <!-- Profile Info -->
        <div class="card p-5">
          <h2 class="font-bold text-gray-900 mb-4">Personal Info</h2>
          <div class="space-y-3">
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Name</label>
              <input v-model="form.name" type="text" class="input-field" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Phone</label>
              <input v-model="form.phone" type="text" class="input-field" />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Email</label>
              <input :value="auth.user?.email" type="email" class="input-field bg-gray-50" disabled />
            </div>
          </div>
          <button @click="saveProfile" :disabled="saving" class="btn-primary mt-4 w-full">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>

          <hr class="my-4" />

          <h3 class="font-bold text-gray-900 mb-3">Change Password</h3>
          <div class="space-y-2">
            <input v-model="pwForm.old_password" type="password" placeholder="Current password" class="input-field" />
            <input v-model="pwForm.new_password" type="password" placeholder="New password" class="input-field" />
          </div>
          <button @click="changePassword" :disabled="changingPw" class="btn-secondary mt-3 w-full">
            {{ changingPw ? 'Updating...' : 'Update Password' }}
          </button>

          <!-- Forgot Password Link -->
          <div class="mt-3 text-center">
            <button @click="openForgotModal" class="text-sm text-blue-600 hover:underline">
              Forgot your password?
            </button>
          </div>
        </div>

        <!-- Addresses -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-bold text-gray-900">My Addresses</h2>
            <button @click="showAddForm = !showAddForm" class="btn-primary text-sm py-1.5">+ Add Address</button>
          </div>

          <!-- Add Form -->
          <div v-if="showAddForm" class="card p-4 mb-4">
            <h3 class="font-semibold mb-3">New Address</h3>
            <div class="space-y-2">
              <select v-model="addrForm.block_id" class="input-field" @change="addrForm.zone_id = null; loadZones(addrForm.block_id)">
                <option value="">Select Block</option>
                <option v-for="b in blocks" :key="b.id" :value="b.id">{{ b.name }}</option>
              </select>
              <select v-model="addrForm.zone_id" class="input-field" :disabled="!addrForm.block_id">
                <option value="">Select Zone</option>
                <option v-for="z in zones[addrForm.block_id]" :key="z.id" :value="z.id">{{ z.zone_name }} (₹{{ z.delivery_charge }} delivery)</option>
              </select>
              <input v-model="addrForm.label" placeholder="Label (Home/Work)" class="input-field" />
              <input v-model="addrForm.address_line1" placeholder="Address Line 1 *" class="input-field" />
              <input v-model="addrForm.address_line2" placeholder="Address Line 2" class="input-field" />
              <input v-model="addrForm.landmark" placeholder="Landmark" class="input-field" />
              <input v-model="addrForm.pincode" placeholder="Pincode" class="input-field" />
              <label class="flex items-center gap-2 text-sm">
                <input type="checkbox" v-model="addrForm.is_default" /> Set as default
              </label>
            </div>
            <div class="flex gap-2 mt-3">
              <button @click="saveAddress" :disabled="savingAddr" class="btn-primary flex-1">
                {{ savingAddr ? 'Saving...' : 'Save' }}
              </button>
              <button @click="showAddForm = false" class="btn-secondary flex-1">Cancel</button>
            </div>
          </div>

          <!-- Address List -->
          <div class="space-y-3">
            <div v-for="addr in addresses" :key="addr.id" class="card p-4">
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-semibold text-sm">
                    {{ addr.label }}
                    <span v-if="addr.is_default" class="text-xs text-green-600 font-medium">(Default)</span>
                  </p>
                  <p class="text-sm text-gray-700">{{ addr.address_line1 }}<span v-if="addr.address_line2">, {{ addr.address_line2 }}</span></p>
                  <p v-if="addr.landmark" class="text-xs text-gray-500">Near {{ addr.landmark }}</p>
                  <p class="text-xs text-blue-600 mt-1 font-medium">{{ addr.block?.name }} — {{ addr.zone?.zone_name }}</p>
                </div>
                <div class="flex flex-col gap-1">
                  <button v-if="!addr.is_default" @click="setDefault(addr.id)" class="text-xs text-blue-600 hover:underline">Set Default</button>
                  <button @click="deleteAddress(addr.id)" class="text-xs text-red-500 hover:underline">Delete</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Forgot Password Modal ──────────────────────────── -->
    <div v-if="showForgotModal"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4"
      @click.self="closeForgotModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-6">

        <!-- Step 1: Enter Email -->
        <div v-if="forgotStep === 1">
          <div class="text-center mb-5">
            <p class="text-3xl mb-2">🔐</p>
            <h2 class="text-xl font-bold text-gray-900">Forgot Password?</h2>
            <p class="text-sm text-gray-500 mt-1">Enter your registered email. We'll send you an OTP.</p>
          </div>
          <input
            v-model="forgotEmail"
            type="email"
            placeholder="Enter your email"
            class="input-field mb-4"
            @keyup.enter="sendOtp"
          />
          <button
            @click="sendOtp"
            :disabled="sendingOtp || !forgotEmail"
            class="btn-primary w-full"
          >
            {{ sendingOtp ? 'Sending OTP...' : 'Send OTP' }}
          </button>
          <button @click="closeForgotModal" class="btn-secondary w-full mt-2">Cancel</button>
        </div>

        <!-- Step 2: Enter OTP + New Password -->
        <div v-if="forgotStep === 2">
          <div class="text-center mb-5">
            <p class="text-3xl mb-2">📧</p>
            <h2 class="text-xl font-bold text-gray-900">Check Your Email</h2>
            <p class="text-sm text-gray-500 mt-1">
              OTP sent to <strong>{{ forgotEmail }}</strong>
            </p>
            <p class="text-xs text-gray-400 mt-1">Valid for 10 minutes</p>
          </div>

          <div class="space-y-3 mb-4">
            <!-- OTP Input — large styled boxes -->
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">Enter 6-digit OTP</label>
              <input
                v-model="forgotOtp"
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="_ _ _ _ _ _"
                class="input-field text-center text-2xl font-bold tracking-widest"
                @keyup.enter="resetPassword"
              />
            </div>
            <div>
              <label class="text-sm font-medium text-gray-700 block mb-1">New Password</label>
              <input
                v-model="forgotNewPassword"
                type="password"
                placeholder="Minimum 6 characters"
                class="input-field"
                @keyup.enter="resetPassword"
              />
            </div>
          </div>

          <button
            @click="resetPassword"
            :disabled="resetting || forgotOtp.length < 6 || !forgotNewPassword"
            class="btn-primary w-full"
          >
            {{ resetting ? 'Resetting...' : 'Reset Password' }}
          </button>

          <!-- Resend OTP -->
          <div class="text-center mt-3">
            <span class="text-sm text-gray-500">Didn't get the OTP? </span>
            <button
              @click="sendOtp"
              :disabled="sendingOtp || resendCooldown > 0"
              class="text-sm text-blue-600 hover:underline disabled:text-gray-400"
            >
              {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP' }}
            </button>
          </div>

          <button @click="forgotStep = 1" class="btn-secondary w-full mt-2">← Back</button>
        </div>

        <!-- Step 3: Success -->
        <div v-if="forgotStep === 3" class="text-center py-4">
          <p class="text-5xl mb-4">🎉</p>
          <h2 class="text-xl font-bold text-gray-900 mb-2">Password Reset!</h2>
          <p class="text-sm text-gray-500 mb-6">Your password has been updated successfully. You can now login with your new password.</p>
          <button @click="closeForgotModal" class="btn-primary w-full">Done</button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Navbar from '@/components/common/Navbar.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api'

const auth = useAuthStore()
const toast = useToastStore()

// ── Profile ───────────────────────────────────────────────
const form = ref({ name: auth.user?.name || '', phone: auth.user?.phone || '' })
const pwForm = ref({ old_password: '', new_password: '' })
const saving = ref(false)
const changingPw = ref(false)

// ── Addresses ─────────────────────────────────────────────
const addresses = ref([])
const blocks = ref([])
const zones = ref({})
const showAddForm = ref(false)
const savingAddr = ref(false)
const addrForm = ref({
  block_id: '', zone_id: '', label: 'Home',
  address_line1: '', address_line2: '', landmark: '', pincode: '', is_default: false
})

// ── Forgot Password Modal ─────────────────────────────────
const showForgotModal = ref(false)
const forgotStep = ref(1)        // 1 = email, 2 = otp+password, 3 = success
const forgotEmail = ref('')
const forgotOtp = ref('')
const forgotNewPassword = ref('')
const sendingOtp = ref(false)
const resetting = ref(false)
const resendCooldown = ref(0)
let cooldownTimer = null

// ── Profile Functions ─────────────────────────────────────
async function loadZones(blockId) {
  if (!blockId) return
  const res = await api.get(`/blocks/${blockId}/zones`)
  zones.value[blockId] = res.data
}

async function saveProfile() {
  saving.value = true
  try {
    await auth.updateProfile({ name: form.value.name, phone: form.value.phone })
    toast.success('Profile updated!')
  } catch (e) { toast.error(e.response?.data?.detail || 'Failed to update') }
  finally { saving.value = false }
}

async function changePassword() {
  changingPw.value = true
  try {
    await auth.changePassword(pwForm.value)
    toast.success('Password changed!')
    pwForm.value = { old_password: '', new_password: '' }
  } catch (e) { toast.error(e.response?.data?.detail || 'Failed to change password') }
  finally { changingPw.value = false }
}

async function saveAddress() {
  if (!addrForm.value.block_id || !addrForm.value.zone_id || !addrForm.value.address_line1) {
    return toast.error('Please fill all required fields')
  }
  savingAddr.value = true
  try {
    await api.post('/addresses', addrForm.value)
    toast.success('Address saved!')
    showAddForm.value = false
    await loadAddresses()
    addrForm.value = { block_id: '', zone_id: '', label: 'Home', address_line1: '', address_line2: '', landmark: '', pincode: '', is_default: false }
  } catch (e) { toast.error(e.response?.data?.detail || 'Failed to save address') }
  finally { savingAddr.value = false }
}

async function setDefault(id) {
  await api.patch(`/addresses/${id}/set-default`)
  await loadAddresses()
  toast.success('Default address updated!')
}

async function deleteAddress(id) {
  if (!confirm('Delete this address?')) return
  await api.delete(`/addresses/${id}`)
  await loadAddresses()
  toast.success('Address deleted')
}

async function loadAddresses() {
  const res = await api.get('/addresses')
  addresses.value = res.data
}

// ── Forgot Password Functions ─────────────────────────────
function openForgotModal() {
  forgotStep.value = 1
  forgotEmail.value = auth.user?.email || ''
  forgotOtp.value = ''
  forgotNewPassword.value = ''
  showForgotModal.value = true
}

function closeForgotModal() {
  showForgotModal.value = false
  if (cooldownTimer) clearInterval(cooldownTimer)
  resendCooldown.value = 0
}

function startResendCooldown() {
  resendCooldown.value = 60
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownTimer)
      resendCooldown.value = 0
    }
  }, 1000)
}

async function sendOtp() {
  if (!forgotEmail.value) return
  sendingOtp.value = true
  try {
    await api.post('/auth/forgot-password', { email: forgotEmail.value })
    toast.success('OTP sent! Check your email.')
    forgotStep.value = 2
    startResendCooldown()
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to send OTP')
  } finally {
    sendingOtp.value = false
  }
}

async function resetPassword() {
  if (forgotOtp.value.length < 6 || !forgotNewPassword.value) return
  resetting.value = true
  try {
    await api.post('/auth/reset-password', {
      email: forgotEmail.value,
      otp: forgotOtp.value,
      new_password: forgotNewPassword.value,
    })
    forgotStep.value = 3
    toast.success('Password reset successful!')
  } catch (e) {
    toast.error(e.response?.data?.detail || 'Failed to reset password')
  } finally {
    resetting.value = false
  }
}

// ── Lifecycle ─────────────────────────────────────────────
onMounted(async () => {
  const [addrRes, blockRes] = await Promise.all([api.get('/addresses'), api.get('/blocks')])
  addresses.value = addrRes.data
  blocks.value = blockRes.data
})

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
</script>
