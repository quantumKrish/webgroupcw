<template>
    <div class="hero">
        <div>
            <p class="eyebrow">Welcome to</p>
            <h1>Auction App</h1>
            <p class="lede">Bid on live auctions or post a new listing. All the merged work lives here now.</p>
            <div class="hero-actions">
                <RouterLink class="btn primary" :to="{ name: 'Items' }">Browse items</RouterLink>
                <RouterLink class="btn ghost" :to="{ name: 'Create Item' }">Post an item</RouterLink>
            </div>
        </div>
        <div class="hero-card">
            <div class="card-head">
                <div>
                    <p class="eyebrow">Ending soon</p>
                    <h2>Live bids closing soon</h2>
                </div>
                <RouterLink class="link" :to="{ name: 'Items' }">See all</RouterLink>
            </div>
            <div v-if="soonLoading" class="muted">Loading…</div>
            <div v-else-if="soonError" class="text-error">{{ soonError }}</div>
            <ul v-else class="soon-list">
                <li v-for="item in endingSoon" :key="item.id">
                    <RouterLink :to="{ name: 'Item Detail', params: { id: item.id } }">
                        <div class="title-row">
                            <span class="title">{{ item.title }}</span>
                            <span class="price">${{ item.current_price }}</span>
                        </div>
                        <div class="muted">Ends {{ formatDate(item.ends_at) }}</div>
                    </RouterLink>
                </li>
                <li v-if="endingSoon.length === 0" class="muted">No active auctions yet.</li>
            </ul>
        </div>
    </div>

    <!-- Won Auctions Banner (smaller, below) -->
    <div v-if="auth.user?.won_items && auth.user.won_items.length > 0" class="won-banner compact">
        <h3>Congratulations! You won {{ auth.user.won_items.length }} auction{{ auth.user.won_items.length > 1 ? 's' : '' }}.</h3>
        <div class="won-items">
            <RouterLink 
                v-for="won in auth.user.won_items" 
                :key="won.id" 
                :to="{ name: 'Item Detail', params: { id: won.id } }"
                class="won-item"
            >
                <img v-if="won.image_url" :src="won.image_url" :alt="won.title" />
                <div>
                    <strong>{{ won.title }}</strong>
                    <p>Final price: ${{ won.final_price }}</p>
                </div>
            </RouterLink>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();

interface SimpleItem {
    id: number;
    title: string;
    current_price: string;
    ends_at: string;
}

const endingSoon = ref<SimpleItem[]>([]);
const soonLoading = ref(true);
const soonError = ref('');

function formatDate(iso: string) {
    return new Date(iso).toLocaleString();
}

// Load items ending soon
// Fetches items from /api/items/, filters and sorts them
// Updates endingSoon, soonLoading, and soonError accordingly
async function loadEndingSoon() {
    soonLoading.value = true;
    soonError.value = '';
    try {
        const res = await fetch('/api/items/');
        if (!res.ok) throw new Error('Failed to load items');
        const data = await res.json();
        const now = Date.now();
        endingSoon.value = (data.items || [])
            .filter((i: any) => new Date(i.ends_at).getTime() > now)
            .sort((a: any, b: any) => new Date(a.ends_at).getTime() - new Date(b.ends_at).getTime())
            .slice(0, 3);
    } catch (e) {
        soonError.value = e instanceof Error ? e.message : 'Failed to load items';
    } finally {
        soonLoading.value = false;
    }
}

onMounted(() => {
    loadEndingSoon();
    auth.checkAuth();
});
</script>

<style scoped>
.hero {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    align-items: center;
    padding: 3rem 0;
}

.eyebrow {
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    color: #0d6efd;
    margin: 0 0 0.25rem;
}

h1 {
    font-size: 2.5rem;
    margin: 0 0 0.5rem;
}

.lede {
    max-width: 40ch;
    color: #4a5568;
    margin-bottom: 1.25rem;
}

.hero-actions {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}

.btn {
    padding: 0.75rem 1.2rem;
    border-radius: 0.5rem;
    font-weight: 600;
    text-decoration: none;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.btn.primary {
    background: #0d6efd;
    color: #fff;
    box-shadow: 0 10px 25px rgba(13, 110, 253, 0.25);
}

.btn.ghost {
    border: 1px solid #cbd5e0;
    color: #1a202c;
    background: #fff;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.08);
}

.hero-card {
    border: 1px solid #e2e8f0;
    border-radius: 1rem;
    padding: 1.5rem;
    background: #fff;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
}

.hero-card h2 {
    margin: 0 0 1rem;
}

.card-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.5rem;
}

.link {
    font-weight: 600;
    color: #0d6efd;
    text-decoration: none;
}

.link:hover { text-decoration: underline; }

.soon-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 0.75rem;
}

.soon-list li a {
    display: block;
    padding: 0.75rem 0.9rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.75rem;
    text-decoration: none;
    color: inherit;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.soon-list li a:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.06);
}

.title-row {
    display: flex;
    justify-content: space-between;
    gap: 0.5rem;
}

.title { font-weight: 700; }
.price { font-weight: 700; color: #0d6efd; }

.text-error { color: #b91c1c; }


.won-banner {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border: 1px solid #86efac;
    border-radius: 0.85rem;
    padding: 1rem 1.25rem;
    margin: 1rem 0 0;
}

.won-banner.compact h3 {
    margin: 0 0 0.65rem;
    color: #15803d;
    font-size: 1.05rem;
}

.won-items {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}

.won-item {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: white;
    border-radius: 0.65rem;
    border: 1px solid #86efac;
    text-decoration: none;
    color: inherit;
    transition: transform 0.15s;
}

.won-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

.won-item img {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: 0.5rem;
}

.won-item strong {
    display: block;
    margin-bottom: 0.15rem;
    color: #15803d;
}

.won-item p {
    margin: 0;
    color: #16a34a;
    font-weight: 600;
}

.hero-card ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    gap: 0.75rem;
}

.hero-card li {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

.hero-card a {
    font-weight: 600;
    color: #0d6efd;
    text-decoration: none;
}

.hero-card a:hover {
    text-decoration: underline;
}

.hero-card span {
    color: #4a5568;
    font-size: 0.95rem;
}
</style>
