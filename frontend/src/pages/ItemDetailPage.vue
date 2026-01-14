<template>
  <div v-if="loading" class="loading">Loading item…</div>
  <div v-else-if="error" class="error">{{ error }}</div>
  <div v-else class="page">
    <div class="item-card">
      <div v-if="item?.image_url" class="item-image">
        <img :src="item.image_url" :alt="item.title" />
      </div>
      <div class="item-body">
        <p class="eyebrow">Ends {{ formatDate(item?.ends_at) }}</p>
        <h1>{{ item?.title }}</h1>
        <p class="description">{{ item?.description }}</p>
        <p class="owner-info">          <img 
            v-if="item?.owner_profile_image" 
            :src="item.owner_profile_image" 
            alt="Seller" 
            class="profile-pic-small"
          />
          <span v-else class="profile-placeholder-small">
            <i class="bi bi-person-circle"></i>
          </span>          Seller: <RouterLink v-if="item?.owner" :to="getUserProfileRoute(item.owner)" class="username-link">
            {{ item?.owner_username }}
          </RouterLink>
        </p>
        <div class="price-row">
          <div>
            <span class="label">Current price</span>
            <div class="price">${{ item?.current_price }}</div>
          </div>
          <form v-if="isLoggedIn && !isSeller" class="bid-form" @submit.prevent="placeBid">
            <label for="bid">Place a bid</label>
            <div class="bid-input">
              <input
                id="bid"
                v-model="bidAmount"
                type="number"
                min="0"
                step="0.01"
                required
                :disabled="bidSubmitting"
              />
              <button type="submit" :disabled="bidSubmitting">
                {{ bidSubmitting ? 'Submitting…' : 'Bid' }}
              </button>
            </div>
            <p v-if="bidError" class="text-error">{{ bidError }}</p>
          </form>
          <div v-else-if="!isLoggedIn" class="placeholder">
            <p class="muted"><a href="/login/">Log in</a> to place a bid</p>
          </div>
          <div v-else-if="isSeller" class="placeholder">
            <p class="muted">You cannot bid on your own item</p>
          </div>
        </div>
        <div class="item-actions">
          <button @click="deleteItem" class="delete-btn" :disabled="deleting">
            {{ deleting ? 'Deleting…' : 'Delete Item' }}
          </button>
        </div>
      </div>
    </div>

    <div class="grid">
      <section class="panel">
        <div class="panel-head">
          <h2>Bid history</h2>
          <span class="muted">Newest first</span>
        </div>
        <div v-if="item?.bids?.length === 0" class="muted">No bids yet.</div>
        <ul class="list" v-else>
          <li v-for="bid in item?.bids" :key="bid.id" class="list-row">
            <div>
              <div class="label">${{ bid.amount }}</div>
              <div class="muted">{{ formatDate(bid.created_at) }}</div>
            </div>
            <div class="bid-actions">
              <RouterLink :to="getUserProfileRoute(bid.bidder)" class="pill user-pill">
                <img 
                  v-if="bid.bidder_profile_image" 
                  :src="bid.bidder_profile_image" 
                  alt="Bidder" 
                  class="profile-pic-tiny"
                />
                <span v-else class="profile-placeholder-tiny">
                  <i class="bi bi-person-circle"></i>
                </span>
                {{ bid.bidder_name }}
              </RouterLink>
              <button 
                v-if="auth.user && auth.user.id === bid.bidder" 
                @click="deleteBid(bid.id)" 
                class="delete-btn-small"
                title="Delete bid"
              >
                ×
              </button>
            </div>
          </li>
        </ul>
      </section>

      <section class="panel">
        <div class="panel-head">
          <h2>Q &amp; A</h2>
          <span class="muted">Ask or reply</span>
        </div>

        <form v-if="isLoggedIn && !isSeller" class="qa-form" @submit.prevent="submitQuestion">
          <label for="question">Ask a question</label>
          <textarea
            id="question"
            v-model="questionText"
            rows="2"
            placeholder="Type your question"
            :disabled="qaSubmitting"
          ></textarea>
          <button type="submit" :disabled="qaSubmitting || !questionText.trim()">
            {{ qaSubmitting ? 'Posting…' : 'Post question' }}
          </button>
          <p v-if="qaError" class="text-error">{{ qaError }}</p>
        </form>
        <div v-else-if="!isLoggedIn" class="placeholder">
          <p class="muted"><a href="/login/">Log in</a> to ask a question</p>
        </div>
        <div v-else-if="isSeller" class="placeholder">
          <p class="muted">You cannot ask questions on your own item</p>
        </div>

        <div v-if="item?.questions?.length === 0" class="muted">No questions yet.</div>
        <div v-else class="qa-list">
          <div v-for="q in item?.questions" :key="q.id" class="qa-item">
            <div class="qa-question">
              <div class="qa-question-header">
                <div class="label">Q: {{ q.content }}</div>
                <button 
                  v-if="auth.user && auth.user.id === q.asker" 
                  @click="deleteQuestion(q.id)" 
                  class="delete-btn-small"
                  title="Delete question"
                >
                  ×
                </button>
              </div>
              <div class="muted">
                <img 
                  v-if="q.asker_profile_image" 
                  :src="q.asker_profile_image" 
                  alt="Asker" 
                  class="profile-pic-tiny"
                />
                <span v-else class="profile-placeholder-tiny">
                  <i class="bi bi-person-circle"></i>
                </span>
                Asked by <RouterLink :to="getUserProfileRoute(q.asker)" class="username-link">{{ q.asker_name }}</RouterLink> • {{ formatDate(q.created_at) }}
              </div>
            </div>
            <div class="qa-replies" v-if="q.replies?.length">
              <div v-for="r in q.replies" :key="r.id" class="qa-reply">
                <div class="qa-reply-header">
                  <div class="label">A: {{ r.content }}</div>
                  <button 
                    v-if="auth.user && auth.user.id === r.author" 
                    @click="deleteReply(r.id)" 
                    class="delete-btn-small"
                    title="Delete reply"
                  >
                    ×
                  </button>
                </div>
                <div class="muted">
                  <img 
                    v-if="r.author_profile_image" 
                    :src="r.author_profile_image" 
                    alt="Author" 
                    class="profile-pic-tiny"
                  />
                  <span v-else class="profile-placeholder-tiny">
                    <i class="bi bi-person-circle"></i>
                  </span>
                  By <RouterLink :to="getUserProfileRoute(r.author)" class="username-link">{{ r.author_name }}</RouterLink> • {{ formatDate(r.created_at) }}
                </div>
              </div>
            </div>
            <form v-if="isLoggedIn && isSeller" class="reply-form" @submit.prevent="submitReply(q.id)">
              <label :for="`reply-${q.id}`">Reply</label>
              <textarea
                :id="`reply-${q.id}`"
                v-model="replyText[q.id]"
                rows="2"
                placeholder="Write a reply"
                :disabled="qaSubmitting"
              ></textarea>
              <button type="submit" :disabled="qaSubmitting || !(replyText[q.id] && replyText[q.id].trim())">
                {{ qaSubmitting ? 'Posting…' : 'Reply' }}
              </button>
            </form>
            <div v-else-if="!isLoggedIn" class="placeholder">
              <p class="muted"><a href="/login/">Log in</a> to reply</p>
            </div>
            <div v-else-if="!isSeller" class="placeholder">
              <p class="muted">Only the seller can reply to questions</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import type { Item, Bid, Question, Reply } from '../types';

type QuestionDetail = Question & { asker: number; replies: Reply[] };

interface ItemDetail extends Item {
  bids: Bid[];
  questions: QuestionDetail[];
  owner_username: string;
}

const route = useRoute();
const auth = useAuthStore();
const item = ref<ItemDetail | null>(null);
const loading = ref(true);
const error = ref('');

const isSeller = computed(() => auth.user && item.value ? auth.user.id === item.value.owner : false);
const isLoggedIn = computed(() => auth.isAuthenticated);

// Helper to get profile route - own profile goes to edit page, others to display page
function getUserProfileRoute(userId: number) {
  if (auth.user && auth.user.id === userId) {
    return { name: 'Profile' };
  }
  return { name: 'User Profile', params: { id: userId } };
}

const bidAmount = ref('');
const bidSubmitting = ref(false);
const bidError = ref('');

const questionText = ref('');
const replyText = reactive<Record<number, string>>({});
const qaSubmitting = ref(false);
const qaError = ref('');

const deleting = ref(false);

async function fetchItem() {
  loading.value = true;
  error.value = '';
  try {
    const res = await fetch(`/api/items/${route.params.id}/`);
    if (!res.ok) throw new Error('Failed to load item');
    const data = await res.json();
    item.value = data as ItemDetail;
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Failed to load item';
  } finally {
    loading.value = false;
  }
}

function formatDate(iso: string | undefined) {
  if (!iso) return '';
  return new Date(iso).toLocaleString();
}

async function placeBid() {
  if (!item.value) return;
  bidSubmitting.value = true;
  bidError.value = '';
  try {
    const res = await fetch('/api/bids/create/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: item.value.id, amount: bidAmount.value })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Bid failed');
    bidAmount.value = '';
    await fetchItem();
  } catch (e) {
    bidError.value = e instanceof Error ? e.message : 'Bid failed';
  } finally {
    bidSubmitting.value = false;
  }
}

async function submitQuestion() {
  if (!item.value || !questionText.value.trim()) return;
  qaSubmitting.value = true;
  qaError.value = '';
  try {
    const res = await fetch('/api/questions/create/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: item.value.id, content: questionText.value })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to post question');
    questionText.value = '';
    await fetchItem();
  } catch (e) {
    qaError.value = e instanceof Error ? e.message : 'Failed to post question';
  } finally {
    qaSubmitting.value = false;
  }
}

async function submitReply(questionId: number) {
  if (!item.value || !replyText[questionId]?.trim()) return;
  qaSubmitting.value = true;
  qaError.value = '';
  try {
    const res = await fetch('/api/replies/create/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_id: questionId, content: replyText[questionId] })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Failed to post reply');
    replyText[questionId] = '';
    await fetchItem();
  } catch (e) {
    qaError.value = e instanceof Error ? e.message : 'Failed to post reply';
  } finally {
    qaSubmitting.value = false;
  }
}

async function deleteItem() {
  if (!item.value) return;
  if (!confirm(`Are you sure you want to delete "${item.value.title}"?`)) return;
  
  deleting.value = true;
  try {
    const res = await fetch(`/api/items/${item.value.id}/delete/`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete item');
    
    // Redirect to items list
    window.location.href = '/items/';
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to delete item');
  } finally {
    deleting.value = false;
  }
}

async function deleteBid(bidId: number) {
  if (!confirm('Are you sure you want to delete this bid?')) return;
  
  try {
    const res = await fetch(`/api/bids/${bidId}/delete/`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete bid');
    await fetchItem(); // Refresh to show updated bid list
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to delete bid');
  }
}

async function deleteQuestion(questionId: number) {
  if (!confirm('Are you sure you want to delete this question?')) return;
  
  try {
    const res = await fetch(`/api/questions/${questionId}/delete/`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete question');
    await fetchItem(); // Refresh to show updated Q&A list
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to delete question');
  }
}

async function deleteReply(replyId: number) {
  if (!confirm('Are you sure you want to delete this reply?')) return;
  
  try {
    const res = await fetch(`/api/replies/${replyId}/delete/`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete reply');
    await fetchItem(); // Refresh to show updated Q&A list
  } catch (e) {
    alert(e instanceof Error ? e.message : 'Failed to delete reply');
  }
}

onMounted(fetchItem);
</script>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.loading,
.error {
  padding: 2rem;
}

.item-card {
  display: grid;
  grid-template-columns: minmax(240px, 340px) 1fr;
  gap: 1.5rem;
  align-items: center;
  border: 1px solid #e2e8f0;
  border-radius: 1rem;
  padding: 1.5rem;
  background: #fff;
  box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}

.item-image img {
  width: 100%;
  border-radius: 0.75rem;
  object-fit: cover;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 700;
  color: #0d6efd;
  margin: 0 0 0.35rem;
}

h1 { margin: 0 0 0.35rem; }
.description { color: #4a5568; margin: 0 0 0.5rem; }
.owner-info { 
  margin: 0 0 1rem; 
  font-size: 0.95rem; 
  color: #4a5568;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profile-pic-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e5e7eb;
}

.profile-pic-tiny {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e5e7eb;
  margin-right: 0.25rem;
  vertical-align: middle;
}

.profile-placeholder-small,
.profile-placeholder-tiny {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #e5e7eb;
  border-radius: 50%;
  color: #6b7280;
}

.profile-placeholder-small {
  width: 32px;
  height: 32px;
  font-size: 20px;
}

.profile-placeholder-tiny {
  width: 20px;
  height: 20px;
  font-size: 12px;
  margin-right: 0.25rem;
  vertical-align: middle;
}

.user-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.price-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  align-items: end;
}

.label { font-weight: 600; }
.price { font-size: 1.6rem; font-weight: 700; }

.bid-form label { display: block; margin-bottom: 0.35rem; }
.bid-input { display: flex; gap: 0.5rem; }
.bid-input input {
  flex: 1;
  padding: 0.65rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
}
.bid-input button {
  padding: 0.65rem 1.1rem;
  border: none;
  border-radius: 0.5rem;
  background: #0d6efd;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1rem;
}

.panel {
  border: 1px solid #e2e8f0;
  border-radius: 0.75rem;
  background: #fff;
  padding: 1rem;
  box-shadow: 0 6px 16px rgba(0,0,0,0.04);
}

.panel-head { display: flex; align-items: baseline; gap: 0.5rem; }
.muted { color: #6b7280; font-size: 0.95rem; }

.placeholder {
  padding: 0;
  color: #6b7280;
  font-size: 0.95rem;
  text-align: left;
  background: transparent;
  border: none;
}

.placeholder p { margin: 0; }

.placeholder a {
  color: #0d6efd;
  text-decoration: none;
  font-weight: 600;
}

.placeholder a:hover {
  text-decoration: underline;
}

.list { list-style: none; padding: 0; margin: 0; }
.list-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e5e7eb;
}

.bid-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pill {
  background: #e0f2fe;
  color: #0369a1;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-weight: 600;
  text-decoration: none;
}

.delete-btn-small {
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: background 0.2s;
}

.delete-btn-small:hover {
  background: #b91c1c;
}

.qa-question-header,
.qa-reply-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.qa-question-header .label,
.qa-reply-header .label {
  flex: 1;
}

.qa-form, .reply-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.qa-form textarea,
.reply-form textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
}
.qa-form button,
.reply-form button {
  align-self: flex-start;
  padding: 0.55rem 1rem;
  border: none;
  background: #0d6efd;
  color: white;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
}

.qa-item { border-top: 1px solid #e5e7eb; padding-top: 0.75rem; margin-top: 0.75rem; }
.qa-reply { margin-left: 0.5rem; padding-left: 0.75rem; border-left: 2px solid #e5e7eb; }

.text-error { color: #b91c1c; }

.username-link {
  color: #0d6efd;
  text-decoration: none;
  font-weight: 600;
}

.username-link:hover {
  text-decoration: underline;
}

.pill {
  text-decoration: none;
}

.item-actions {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.delete-btn {
  padding: 0.65rem 1.2rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.delete-btn:hover:not(:disabled) {
  background: #b91c1c;
}

.delete-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}
</style>
