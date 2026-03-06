<template>
  <div class="min-h-screen bg-gray-50 flex">
    <AdminSidebar />
    <main class="flex-1 p-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Blocks & Delivery Zones</h1>

      <div class="grid md:grid-cols-2 gap-6">
        <!-- Blocks Column -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-bold text-gray-900">Delivery Blocks</h2>
            <button @click="openBlockForm()" class="btn-primary text-sm py-1.5">+ Add Block</button>
          </div>

          <!-- Block Form -->
          <div v-if="showBlockForm" class="card p-4 mb-4">
            <div class="space-y-2">
              <input v-model="blockForm.name" placeholder="Block Name *" class="input-field" />
              <input v-model="blockForm.description" placeholder="Description" class="input-field" />
            </div>
            <div class="flex gap-2 mt-3">
              <button @click="saveBlock" :disabled="savingBlock" class="btn-primary flex-1 text-sm">{{ savingBlock ? '...' : 'Save' }}</button>
              <button @click="showBlockForm = false" class="btn-secondary flex-1 text-sm">Cancel</button>
            </div>
          </div>

          <div class="space-y-3">
            <div
              v-for="block in blocks"
              :key="block.id"
              :class="['card p-4 cursor-pointer transition', selectedBlock?.id === block.id ? 'border-2 border-blue-500' : '']"
              @click="selectBlock(block)"
            >
              <div class="flex items-center justify-between">
                <div>
                  <p class="font-semibold text-gray-900">{{ block.name }}</p>
                  <p v-if="block.description" class="text-xs text-gray-500">{{ block.description }}</p>
                </div>
                <div class="flex flex-col items-end gap-1">
                  <span :class="block.is_active ? 'badge-confirmed' : 'badge-cancelled'" class="text-xs">{{ block.is_active ? 'Active' : 'Inactive' }}</span>
                  <span class="text-xs text-blue-600">Click to manage zones →</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Zones Column -->
        <div>
          <div class="flex items-center justify-between mb-3">
            <h2 class="font-bold text-gray-900">
              {{ selectedBlock ? `Zones in ${selectedBlock.name}` : 'Select a Block' }}
            </h2>
            <button v-if="selectedBlock" @click="openZoneForm()" class="btn-primary text-sm py-1.5">+ Add Zone</button>
          </div>

          <!-- Zone Form -->
          <div v-if="showZoneForm && selectedBlock" class="card p-4 mb-4">
            <div class="space-y-2">
              <input v-model="zoneForm.zone_name" placeholder="Zone Name *" class="input-field" />
              <input v-model.number="zoneForm.delivery_charge" type="number" step="0.01" placeholder="Delivery Charge (₹) *" class="input-field" />
              <input v-model.number="zoneForm.min_order_value" type="number" step="0.01" placeholder="Free delivery above (₹) — 0 = always charge" class="input-field" />
            </div>
            <div class="flex gap-2 mt-3">
              <button @click="saveZone" :disabled="savingZone" class="btn-primary flex-1 text-sm">{{ savingZone ? '...' : 'Save Zone' }}</button>
              <button @click="showZoneForm = false" class="btn-secondary flex-1 text-sm">Cancel</button>
            </div>
          </div>

          <div v-if="!selectedBlock" class="text-center text-gray-400 py-10">
            ← Select a block to manage its zones
          </div>

          <div v-else class="space-y-3">
            <div v-for="zone in zones" :key="zone.id" class="card p-4">
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-semibold text-sm">{{ zone.zone_name }}</p>
                  <p class="text-sm text-blue-600 font-bold">₹{{ zone.delivery_charge }} delivery charge</p>
                  <p v-if="zone.min_order_value > 0" class="text-xs text-green-600">Free above ₹{{ zone.min_order_value }}</p>
                </div>
                <div class="flex flex-col gap-1 items-end">
                  <span :class="zone.is_active ? 'badge-confirmed' : 'badge-cancelled'" class="text-xs">{{ zone.is_active ? 'Active' : 'Off' }}</span>
                  <button @click="toggleZone(zone)" :class="zone.is_active ? 'text-red-500' : 'text-green-600'" class="text-xs hover:underline">
                    {{ zone.is_active ? 'Deactivate' : 'Activate' }}
                  </button>
                </div>
              </div>
            </div>
            <div v-if="zones.length === 0" class="text-center text-gray-400 py-6">No zones yet for this block.</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '@/components/admin/Sidebar.vue'
import { useToastStore } from '@/stores/toast'
import api from '@/services/api'

const toast = useToastStore()
const blocks = ref([])
const zones = ref([])
const selectedBlock = ref(null)

const showBlockForm = ref(false)
const showZoneForm = ref(false)
const savingBlock = ref(false)
const savingZone = ref(false)

const blockForm = ref({ name: '', description: '' })
const zoneForm = ref({ zone_name: '', delivery_charge: 0, min_order_value: 0 })

async function fetchBlocks() {
  const res = await api.get('/blocks')
  blocks.value = res.data
}

async function selectBlock(block) {
  selectedBlock.value = block
  showZoneForm.value = false
  const res = await api.get(`/blocks/${block.id}/zones`)
  zones.value = res.data
}

function openBlockForm() { blockForm.value = { name: '', description: '' }; showBlockForm.value = true }
function openZoneForm() { zoneForm.value = { zone_name: '', delivery_charge: 0, min_order_value: 0 }; showZoneForm.value = true }

async function saveBlock() {
  if (!blockForm.value.name) return
  savingBlock.value = true
  try {
    await api.post('/blocks', blockForm.value)
    toast.success('Block added!')
    showBlockForm.value = false
    await fetchBlocks()
  } catch (e) { toast.error(e.response?.data?.detail || 'Failed') }
  finally { savingBlock.value = false }
}

async function saveZone() {
  if (!zoneForm.value.zone_name || !selectedBlock.value) return
  savingZone.value = true
  try {
    await api.post('/blocks/zones', { ...zoneForm.value, block_id: selectedBlock.value.id })
    toast.success('Zone added!')
    showZoneForm.value = false
    await selectBlock(selectedBlock.value)
  } catch (e) { toast.error(e.response?.data?.detail || 'Failed') }
  finally { savingZone.value = false }
}

async function toggleZone(zone) {
  await api.put(`/blocks/zones/${zone.id}`, { is_active: !zone.is_active })
  await selectBlock(selectedBlock.value)
}

onMounted(fetchBlocks)
</script>
