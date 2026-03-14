<template>
  <div>
    <Navbar />
    <div class="max-w-7xl mx-auto px-4 py-6">
      <div class="flex flex-col md:flex-row gap-6">
        <!-- Sidebar Filters -->
        <aside class="w-full md:w-56 flex-shrink-0">
          <div class="card p-4 sticky top-20">
            <h3 class="font-bold text-gray-900 mb-3">Filters</h3>
            <div class="mb-4">
              <label class="text-sm font-medium text-gray-700 block mb-2"
                >Category</label
              >
              <div class="space-y-1">
                <button
                  @click="filters.category = ''"
                  :class="[
                    'w-full text-left text-sm px-2 py-1.5 rounded-lg',
                    !filters.category
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'hover:bg-gray-50',
                  ]"
                >
                  All
                </button>
                <button
                  v-for="cat in categories"
                  :key="cat.id"
                  @click="filters.category = cat.slug"
                  :class="[
                    'w-full text-left text-sm px-2 py-1.5 rounded-lg',
                    filters.category === cat.slug
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'hover:bg-gray-50',
                  ]"
                >
                  {{ cat.name }}
                </button>
              </div>
            </div>
            <div class="mb-4">
              <label class="text-sm font-medium text-gray-700 block mb-2"
                >Price Range</label
              >
              <div class="flex gap-2">
                <input
                  v-model.number="filters.min_price"
                  type="number"
                  placeholder="Min"
                  class="input-field text-sm py-1"
                />
                <input
                  v-model.number="filters.max_price"
                  type="number"
                  placeholder="Max"
                  class="input-field text-sm py-1"
                />
              </div>
            </div>
            <button @click="applyFilters" class="btn-primary w-full text-sm">
              Apply
            </button>
            <button
              @click="resetFilters"
              class="btn-secondary w-full text-sm mt-2"
            >
              Reset
            </button>
          </div>
        </aside>

        <!-- Product Grid -->
        <div class="flex-1">
          <div class="flex items-center justify-between mb-4">
            <h1 class="text-lg font-bold text-gray-900">
              {{
                filters.search
                  ? `Results for "${filters.search}"`
                  : "All Products"
              }}
              <span class="text-sm font-normal text-gray-500 ml-2"
                >({{ total }} items)</span
              >
            </h1>
          </div>

          <LoadingSpinner v-if="loading" />
          <div
            v-else-if="products.length === 0"
            class="text-center text-gray-500 py-16"
          >
            <p class="text-4xl mb-3">🔍</p>
            <p>No products found. Try different filters.</p>
          </div>
          <div
            v-else
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4"
          >
            <ProductCard v-for="p in products" :key="p.id" :product="p" />
          </div>

          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
            <button
              v-for="p in totalPages"
              :key="p"
              @click="goToPage(p)"
              :class="[
                'w-9 h-9 rounded-lg text-sm font-medium',
                page === p
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200 hover:border-blue-300',
              ]"
            >
              {{ p }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import Navbar from "@/components/common/Navbar.vue";
import ProductCard from "@/components/product/ProductCard.vue";
import LoadingSpinner from "@/components/common/LoadingSpinner.vue";
import api from "@/services/api";

const route = useRoute();
const router = useRouter();
const products = ref([]);
const categories = ref([]);
const total = ref(0);
const totalPages = ref(1);
const page = ref(1);
const loading = ref(true);

const filters = ref({
  category: route.query.category || "",
  search: route.query.search || "",
  min_price: route.query.min_price || "",
  max_price: route.query.max_price || "",
});

async function fetchProducts() {
  loading.value = true;
  try {
    const params = { page: page.value, limit: 20 };
    if (filters.value.category) params.category = filters.value.category;
    if (filters.value.search) params.search = filters.value.search;
    if (filters.value.min_price) params.min_price = filters.value.min_price;
    if (filters.value.max_price) params.max_price = filters.value.max_price;
    const res = await api.get("/products", { params });
    products.value = res.data.products;
    total.value = res.data.total;
    totalPages.value = res.data.pages;
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  page.value = 1;
  fetchProducts();
}
function resetFilters() {
  filters.value = { category: "", search: "", min_price: "", max_price: "" };
  page.value = 1;
  fetchProducts();
}
function goToPage(p) {
  page.value = p;
  fetchProducts();
}

watch(
  () => route.query,
  (q) => {
    filters.value.search = q.search || "";
    filters.value.category = q.category || "";
    fetchProducts();
  },
);

onMounted(async () => {
  const catRes = await api.get("/categories");
  categories.value = catRes.data;
  fetchProducts();
});
</script>
