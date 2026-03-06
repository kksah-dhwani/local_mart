<template>
  <div>
    <Navbar />
    <div class="max-w-3xl mx-auto px-4 py-8">
      <router-link
        to="/orders"
        class="text-blue-600 text-sm hover:underline mb-4 inline-block"
        >← Back to Orders</router-link
      >

      <LoadingSpinner v-if="loading" />
      <div v-else-if="order" class="space-y-4">
        <!-- Header -->
        <div class="card p-5">
          <div class="flex items-start justify-between">
            <div>
              <h1 class="text-xl font-bold text-gray-900">
                Order #{{ order.id }}
              </h1>
              <p class="text-sm text-gray-500 mt-1">
                Placed on {{ formatDate(order.ordered_at) }}
              </p>
            </div>
            <span :class="`badge-${order.status} text-base`">{{
              formatStatus(order.status)
            }}</span>
          </div>

          <!-- Timeline -->
          <div class="mt-6 flex items-center gap-0">
            <div
              v-for="(step, i) in timeline"
              :key="step.key"
              class="flex items-center flex-1"
            >
              <div class="flex flex-col items-center flex-shrink-0">
                <div
                  :class="[
                    'w-8 h-8 rounded-full flex items-center justify-center text-sm',
                    isStepDone(step.key)
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-400',
                  ]"
                >
                  {{ step.icon }}
                </div>
                <span
                  class="text-xs text-gray-500 mt-1 text-center leading-tight"
                  >{{ step.label }}</span
                >
              </div>
              <div
                v-if="i < timeline.length - 1"
                :class="[
                  'flex-1 h-1 mx-1 rounded',
                  isStepDone(step.key) ? 'bg-blue-400' : 'bg-gray-200',
                ]"
              ></div>
            </div>
          </div>
        </div>

        <!-- Items -->
        <div class="card p-5">
          <div class="cardHeader flex justify-between">
            <span class="font-bold text-gray-900 mb-4">Items Ordered</span>
            <!-- <button
              @click="dropDown = !dropDown"
              class="text-sm font-medium text-blue-600 cursor-pointer hover:underline"
            >
              {{ dropDown ? "Show less" : "Show more..." }}
            </button> -->
          </div>
          <div class="space-y-3">
            <div v-for="item in order.items" :key="item.id" class="flex gap-3">
              <ProductImage
                :src="item.product_image"
                :alt="item.product_name"
                container-class="w-14 h-14 rounded-lg flex-shrink-0"
              />
              <div class="flex-1">
                <p class="font-medium text-sm">{{ item.product_name }}</p>
                <p class="text-xs text-gray-500">
                  ₹{{ item.unit_price }} × {{ item.quantity }}
                </p>
              </div>
              <div>
                <p class="font-bold text-lg">₹{{ item.line_total }}</p>
                <button
                  class="btn-secondary text-sm py-1.5 my-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Return
                </button>
              </div>
            </div>
          </div>
          <!-- <hr class="my-4" />
          <div class="space-y-1 text-sm">
            <div class="flex justify-between text-gray-600">
              <span>Subtotal</span><span>₹{{ order.subtotal }}</span>
            </div>
            <div class="flex justify-between text-gray-600">
              <span>Delivery</span>
              <span>{{
                order.delivery_charge == 0
                  ? "FREE"
                  : `₹${order.delivery_charge}`
              }}</span>
            </div>
            <div class="flex justify-between font-bold text-base mt-2">
              <span>Total</span>
              <span class="text-blue-600">₹{{ order.total_amount }}</span>
            </div>
          </div>
          <hr class="my-4" /> -->
          <div class="space-y-1 text-sm"></div>
        </div>

        <!-- Delivery Address -->
        <div class="card p-5 flex justify-between">
          <div class="cardItem">
            <h2 class="font-bold text-gray-900 mb-2">Delivery Details</h2>
            <p class="text-sm font-medium text-blue-600">
              {{ order.snap_block_name }} — {{ order.snap_zone_name }}
            </p>
            <p class="text-sm text-gray-700 mt-1">{{ parsedAddress }}</p>
            <p v-if="order.notes" class="text-sm text-gray-500 mt-2 italic">
              Note: {{ order.notes }}
            </p>
          </div>
          <div class="cardItem"></div>
        </div>

        <!-- Review section (if delivered) -->
        <div v-if="order.status === 'delivered'" class="card p-5">
          <h2 class="font-bold text-gray-900 mb-4">Rate Your Order</h2>
          <div
            v-for="item in order.items"
            :key="item.id"
            class="mb-5 pb-5 border-b last:border-b-0 last:mb-0 last:pb-0"
          >
            <!-- ✅ Only show if NOT already reviewed -->
            <template v-if="!reviewForm[item.product_id]?.submitted">
              <p class="text-sm font-medium text-gray-700 mb-2">
                {{ item.product_name }}
              </p>
              <div
                class="flex gap-1 text-2xl mb-2"
                :class="
                  reviewForm[item.product_id]?.submitting
                    ? 'opacity-50 pointer-events-none'
                    : 'cursor-pointer'
                "
              >
                <span
                  v-for="i in 5"
                  :key="i"
                  @click="setRating(item.product_id, i)"
                  :class="
                    (reviewForm[item.product_id]?.rating || 0) >= i
                      ? 'text-yellow-400'
                      : 'text-gray-300'
                  "
                  >★</span
                >
              </div>
              <textarea
                v-model="reviewForm[item.product_id].comment"
                rows="2"
                placeholder="Share your experience..."
                class="input-field text-sm resize-none mb-2"
                :disabled="reviewForm[item.product_id]?.submitting"
              ></textarea>
              <button
                @click="submitReview(item.product_id)"
                :disabled="
                  !reviewForm[item.product_id]?.rating ||
                  reviewForm[item.product_id]?.submitting
                "
                class="btn-primary text-sm py-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{
                  reviewForm[item.product_id]?.submitting
                    ? "Submitting..."
                    : "Submit Review"
                }}
              </button>
            </template>

            <!-- ✅ Already reviewed — show thank you -->
            <div
              v-else
              class="flex items-center gap-3 bg-green-50 border border-green-200 rounded-lg px-4 py-3"
            >
              <span class="text-lg">✅</span>
              <div>
                <p class="text-sm font-medium text-green-700">
                  {{ item.product_name }}
                </p>
                <p class="text-xs text-green-600">
                  Review submitted! Thank you.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import Navbar from "@/components/common/Navbar.vue";
import ProductImage from "@/components/common/ProductImage.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import { useToastStore } from "@/stores/toast";
import api from "@/services/api";

const route = useRoute();
const toast = useToastStore();
const order = ref(null);
const loading = ref(true);
const reviewForm = ref({});
// const dropDown = ref(false);

const timeline = [
  { key: "pending", icon: "📋", label: "Ordered" },
  { key: "confirmed", icon: "✅", label: "Confirmed" },
  { key: "out_for_delivery", icon: "🚴", label: "On the way" },
  { key: "delivered", icon: "🎉", label: "Delivered" },
];
const statusOrder = ["pending", "confirmed", "out_for_delivery", "delivered"];

function isStepDone(key) {
  if (order.value?.status === "cancelled") return false;
  return statusOrder.indexOf(order.value?.status) >= statusOrder.indexOf(key);
}

function formatDate(d) {
  return d ? new Date(d).toLocaleString("en-IN") : "";
}

function formatStatus(s) {
  return (
    {
      pending: "Pending",
      confirmed: "Confirmed",
      out_for_delivery: "Out for Delivery",
      delivered: "Delivered",
      cancelled: "Cancelled",
    }[s] || s
  );
}

const parsedAddress = computed(() => {
  try {
    const a = JSON.parse(order.value?.snap_address || "{}");
    return [
      a.address_line1,
      a.address_line2,
      a.landmark ? `Near ${a.landmark}` : "",
      a.pincode,
    ]
      .filter(Boolean)
      .join(", ");
  } catch {
    return "";
  }
});

function setRating(productId, rating) {
  reviewForm.value[productId] = { ...reviewForm.value[productId], rating };
}

async function submitReview(productId) {
  const form = reviewForm.value[productId];
  if (!form?.rating || form.submitting) return;

  reviewForm.value[productId].submitting = true;
  try {
    await api.post("/reviews", {
      product_id: productId,
      order_id: order.value.id,
      rating: form.rating,
      comment: form.comment,
    });
    // ✅ Mark as submitted — hides the form permanently
    reviewForm.value[productId] = { submitted: true };
    toast.success("Review submitted!");
  } catch (e) {
    reviewForm.value[productId].submitting = false;
    toast.error(e.response?.data?.detail || "Failed to submit review");
  }
}

onMounted(async () => {
  try {
    const res = await api.get(`/orders/${route.params.id}`);
    order.value = res.data;

    // ✅ already_reviewed flag backend se aa raha hai
    res.data.items.forEach((item) => {
      reviewForm.value[item.product_id] = {
        rating: 0,
        comment: "",
        submitted: item.already_reviewed ?? false,
      };
    });
  } finally {
    loading.value = false;
  }
});
</script>
