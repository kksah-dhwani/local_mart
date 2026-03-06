<template>
  <div>
    <Navbar />
    <div class="max-w-5xl mx-auto px-4 py-8">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">Shopping Cart</h1>

      <div v-if="cart.cart.items.length === 0" class="text-center py-16">
        <p class="text-5xl mb-4">🛒</p>
        <p class="text-gray-500 text-lg mb-4">Your cart is empty</p>
        <router-link to="/products" class="btn-primary">Start Shopping</router-link>
      </div>

      <div v-else class="grid md:grid-cols-3 gap-6">
        <!-- Items -->
        <div class="md:col-span-2 space-y-3">
          <div v-for="item in cart.cart.items" :key="item.id" class="card p-4 flex gap-4">
            <ProductImage
              :src="item.product.image_url"
              :alt="item.product.name"
              container-class="w-20 h-20 rounded-lg flex-shrink-0"
            />
            <div class="flex-1">
              <router-link :to="`/products/${item.product.slug}`" class="font-semibold text-gray-900 hover:text-blue-600 text-sm">
                {{ item.product.name }}
              </router-link>
              <p v-if="item.product.unit" class="text-xs text-gray-500">{{ item.product.unit }}</p>
              <p class="text-blue-600 font-bold mt-1">₹{{ item.product.price }}</p>

              <div class="flex items-center gap-3 mt-2">
                <div class="flex items-center border border-gray-300 rounded-lg">
                  <button @click="updateQty(item, item.quantity - 1)" class="px-2 py-1 hover:bg-gray-50 text-lg leading-none">−</button>
                  <span class="px-3 py-1 text-sm font-semibold">{{ item.quantity }}</span>
                  <button @click="updateQty(item, item.quantity + 1)" class="px-2 py-1 hover:bg-gray-50 text-lg leading-none">+</button>
                </div>
                <span class="text-sm font-semibold text-gray-700">= ₹{{ (item.product.price * item.quantity).toFixed(2) }}</span>
                <button @click="removeItem(item.product_id)" class="ml-auto text-red-400 hover:text-red-600 text-sm">🗑 Remove</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary -->
        <div class="card p-5 h-fit sticky top-20">
          <h2 class="font-bold text-gray-900 mb-4">Order Summary</h2>
          <div class="space-y-2 text-sm mb-4">
            <div class="flex justify-between">
              <span class="text-gray-600">Subtotal ({{ cart.cart.item_count }} items)</span>
              <span class="font-semibold">₹{{ cart.subtotal.toFixed(2) }}</span>
            </div>
            <div class="flex justify-between text-gray-500">
              <span>Delivery</span>
              <span>Calculated at checkout</span>
            </div>
          </div>
          <hr class="mb-4" />
          <router-link to="/checkout" class="btn-primary w-full block text-center">
            Proceed to Checkout →
          </router-link>
          <button @click="cart.clearCart()" class="btn-secondary w-full mt-2 text-sm">Clear Cart</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Navbar from '@/components/common/Navbar.vue'
import ProductImage from '@/components/common/ProductImage.vue'
import { useCartStore } from '@/stores/cart'
import { useToastStore } from '@/stores/toast'

const cart = useCartStore()
const toast = useToastStore()

async function updateQty(item, newQty) {
  if (newQty <= 0) return removeItem(item.product_id)
  if (newQty > item.product.stock_qty) return toast.error(`Only ${item.product.stock_qty} in stock`)
  try { await cart.updateItem(item.product_id, newQty) }
  catch (e) { toast.error(e.response?.data?.detail || 'Update failed') }
}

async function removeItem(productId) {
  try { await cart.removeItem(productId) }
  catch { toast.error('Failed to remove item') }
}
</script>
