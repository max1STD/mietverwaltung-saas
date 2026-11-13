import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

/**
 * Router — zentrale Routen-Definition
 *
 * Navigation Guards:
 * - requiresAuth: Weiterleitung zu /login, wenn nicht authentifiziert
 * - 2FA-Pflicht: Weiterleitung zu /2fa-setup, wenn authentifiziert aber 2FA nicht verifiziert
 */

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: () => import('../views/LandingView.vue'),
      meta: { public: true },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { public: true, guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { public: true, guestOnly: true },
    },
    {
      path: '/2fa-setup',
      name: 'two-factor-setup',
      component: () => import('../views/auth/TwoFactorSetupView.vue'),
      meta: { requiresAuth: true, allowPending2fa: true },
    },
    {
      path: '/password-reset',
      name: 'password-reset',
      component: () => import('../views/auth/PasswordResetView.vue'),
      meta: { public: true, guestOnly: true },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Für geschützte Routen prüfen wir den Auth-Status.
  // Wenn der Store noch nicht initialisiert ist, laden wir das Profil.
  if (!authStore.isAuthenticated && to.meta.requiresAuth) {
    await authStore.fetchUser()
  }

  const isAuthenticated = authStore.isAuthenticated
  const requires2fa = authStore.requires2fa

  // Geschützte Route ohne Auth -> Login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }

  // Authentifiziert, aber 2FA noch ausstehend -> 2FA-Setup
  if (
    isAuthenticated &&
    requires2fa &&
    !to.meta.allowPending2fa
  ) {
    return next({ name: 'two-factor-setup' })
  }

  // Bereits eingeloggt auf Login/Register/Password-Reset -> Dashboard
  if (to.meta.guestOnly && isAuthenticated && !requires2fa) {
    return next({ name: 'dashboard' })
  }

  next()
})

export default router