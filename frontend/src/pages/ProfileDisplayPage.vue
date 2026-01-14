<template>
  <div class="container mt-4">
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="user" class="row">
      <div class="col-md-8 offset-md-2">
        <!-- User Profile Card -->
        <div class="card shadow-sm mb-4">
          <div class="card-body text-center">
            <div class="mb-3">
              <img 
                v-if="user.profile_image_url" 
                :src="user.profile_image_url" 
                :alt="user.username"
                class="rounded-circle"
                style="width: 120px; height: 120px; object-fit: cover;"
              >
              <div v-else class="bg-secondary rounded-circle d-inline-flex align-items-center justify-content-center" 
                   style="width: 120px; height: 120px;">
                <i class="bi bi-person-fill text-white" style="font-size: 3rem;"></i>
              </div>
            </div>
            <h2 class="mb-1">{{ user.username }}</h2>
            <p class="text-muted mb-3">
              <i class="bi bi-envelope"></i> {{ user.email }}
            </p>
            <p v-if="user.first_name || user.last_name" class="mb-2">
              <strong>{{ user.first_name }} {{ user.last_name }}</strong>
            </p>
            <p v-if="user.date_of_birth" class="text-muted">
              <i class="bi bi-calendar"></i> Born: {{ formatDate(user.date_of_birth) }}
            </p>
          </div>
        </div>

        <!-- User's Items -->
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0"><i class="bi bi-box"></i> Items Listed</h5>
          </div>
          <div class="card-body">
            <div v-if="userItems.length === 0" class="text-center text-muted py-3">
              No items listed yet
            </div>
            <div v-else class="row">
              <div v-for="item in userItems" :key="item.id" class="col-md-6 mb-3">
                <div class="card h-100">
                  <img 
                    v-if="item.image_url" 
                    :src="item.image_url" 
                    class="card-img-top" 
                    :alt="item.title"
                    style="height: 150px; object-fit: cover;"
                  >
                  <div class="card-body">
                    <h6 class="card-title">
                      <RouterLink :to="{ name: 'Item Detail', params: { id: item.id } }">
                        {{ item.title }}
                      </RouterLink>
                    </h6>
                    <p class="card-text small text-muted">
                      Current: ${{ item.current_price }}
                    </p>
                    <p class="card-text small">
                      <i class="bi bi-clock"></i> Ends: {{ formatDate(item.ends_at) }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- User's Bids -->
        <div class="card shadow-sm">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0"><i class="bi bi-cash-stack"></i> Recent Bids</h5>
          </div>
          <div class="card-body">
            <div v-if="userBids.length === 0" class="text-center text-muted py-3">
              No bids placed yet
            </div>
            <div v-else class="list-group list-group-flush">
              <div v-for="bid in userBids" :key="bid.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <RouterLink :to="{ name: 'Item Detail', params: { id: bid.item_id } }">
                      <strong>{{ bid.item_title }}</strong>
                    </RouterLink>
                    <p class="mb-0 small text-muted">
                      <i class="bi bi-clock"></i> {{ formatDate(bid.created_at) }}
                    </p>
                  </div>
                  <span class="badge bg-success">${{ bid.amount }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import { useRoute, RouterLink } from 'vue-router';

interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  profile_image_url?: string;
}

interface Item {
  id: number;
  title: string;
  current_price: string;
  image_url: string;
  ends_at: string;
}

interface Bid {
  id: number;
  item_id: number;
  item_title: string;
  amount: string;
  created_at: string;
}

const route = useRoute();
const loading = ref(true);
const error = ref('');
const user = ref<User | null>(null);
const userItems = ref<Item[]>([]);
const userBids = ref<Bid[]>([]);

const userId = route.params.id;

onMounted(async () => {
  await loadUserProfile();
});

async function loadUserProfile() {
  try {
    loading.value = true;
    error.value = '';

    const response = await fetch(`/api/users/${userId}/`, {
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Failed to load user profile');
    }

    const data = await response.json();
    user.value = data.user;
    userItems.value = data.items || [];
    userBids.value = data.bids || [];
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'An error occurred';
  } finally {
    loading.value = false;
  }
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

a {
  text-decoration: none;
  color: #0d6efd;
}

a:hover {
  text-decoration: underline;
}
</style>
