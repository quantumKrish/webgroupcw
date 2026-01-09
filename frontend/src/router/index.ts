// Example of how to use Vue Router

import { createRouter, createWebHistory } from 'vue-router'

// 1. Define route components.
// These can be imported from other files
const MainPage = () => import('../pages/MainPage.vue');
const OtherPage = () => import('../pages/OtherPage.vue');
const ProfilePage = () => import('../pages/ProfilePage.vue');

let base = (import.meta.env.MODE == 'development') ? import.meta.env.BASE_URL : ''

// 2. Define some routes
// Each route should map to a component.
// We'll talk about nested routes later.
const router = createRouter({
    history: createWebHistory(base),
    routes: [
        { path: '/', name: 'Main Page', component: MainPage },
        { path: '/other/', name: 'Other Page', component: OtherPage },
        { path: '/profile/', name: 'Profile', component: ProfilePage },
    ]
})

export default router
