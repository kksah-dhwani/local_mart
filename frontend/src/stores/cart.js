import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'

export const useCartStore = defineStore('cart', () => {
  const cart = ref({ id: null, items: [], subtotal: 0, item_count: 0 })
  const loading = ref(false)

  const itemCount = computed(() => cart.value.item_count || 0)
  const subtotal = computed(() => cart.value.subtotal || 0)

  async function fetchCart() {
    try {
      const res = await api.get('/cart')
      cart.value = res.data
    } catch {}
  }

  async function addItem(product_id, quantity = 1) {
    loading.value = true
    try {
      const res = await api.post('/cart/items', { product_id, quantity })
      cart.value = res.data
      return true
    } finally {
      loading.value = false
    }
  }

  async function updateItem(product_id, quantity) {
    const res = await api.put(`/cart/items/${product_id}`, { quantity })
    cart.value = res.data
  }

  async function removeItem(product_id) {
    const res = await api.delete(`/cart/items/${product_id}`)
    cart.value = res.data
  }

  async function clearCart() {
    await api.delete('/cart/clear')
    cart.value = { id: null, items: [], subtotal: 0, item_count: 0 }
  }

  function reset() {
    cart.value = { id: null, items: [], subtotal: 0, item_count: 0 }
  }

  return { cart, loading, itemCount, subtotal, fetchCart, addItem, updateItem, removeItem, clearCart, reset }
})
