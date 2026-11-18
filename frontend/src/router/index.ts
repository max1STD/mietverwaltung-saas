import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useOnboardingStore } from '@/stores/onboarding'

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
      component: () => import('../views/dashboard/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/onboarding',
      name: 'onboarding-welcome',
      component: () => import('../views/onboarding/OnboardingWelcomeView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/objekte',
      name: 'objekte',
      component: () => import('../views/objekte/ObjekteListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/objekte/neu',
      name: 'objekt-create',
      component: () => import('../views/objekte/ObjektFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/objekte/:id',
      name: 'objekt-detail',
      component: () => import('../views/objekte/ObjektDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/einheiten/:id',
      name: 'einheit-detail',
      component: () => import('../views/einheiten/EinheitDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/einheiten/:id/bearbeiten',
      name: 'einheit-edit',
      component: () => import('../views/einheiten/EinheitFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/objekte/:id/bearbeiten',
      name: 'objekt-edit',
      component: () => import('../views/objekte/ObjektFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mieter',
      name: 'mieter',
      component: () => import('../views/mieter/MieterListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mieter/neu',
      name: 'mieter-create',
      component: () => import('../views/mieter/MieterFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mieter/:id',
      name: 'mieter-detail',
      component: () => import('../views/mieter/MieterDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mieter/:id/bearbeiten',
      name: 'mieter-edit',
      component: () => import('../views/mieter/MieterFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mietvertraege',
      name: 'mietvertraege',
      component: () => import('../views/mietvertraege/MietvertraegeListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tickets',
      name: 'tickets',
      component: () => import('../views/tickets/TicketListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tickets/neu',
      name: 'ticket-create',
      component: () => import('../views/tickets/TicketFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/tickets/:id',
      name: 'ticket-detail',
      component: () => import('../views/tickets/TicketDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/preise',
      name: 'preise',
      component: () => import('../views/billing/PricingView.vue'),
      meta: { public: true },
    },
    {
      path: '/abo',
      name: 'subscription',
      component: () => import('../views/billing/SubscriptionView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/einstellungen',
      name: 'einstellungen',
      component: () => import('../views/settings/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/zaehler',
      name: 'zaehler',
      component: () => import('../views/zaehler/ZaehlerListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/zaehler/neu',
      name: 'zaehler-create',
      component: () => import('../views/zaehler/ZaehlerFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/zaehler/:id',
      name: 'zaehler-detail',
      component: () => import('../views/zaehler/ZaehlerDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/zaehler/:id/bearbeiten',
      name: 'zaehler-edit',
      component: () => import('../views/zaehler/ZaehlerFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/kosten',
      name: 'kosten',
      component: () => import('../views/kosten/KostenListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/kosten/neu',
      name: 'kosten-create',
      component: () => import('../views/kosten/KostenFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/kosten/:id/bearbeiten',
      name: 'kosten-edit',
      component: () => import('../views/kosten/KostenFormView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/abrechnungen',
      name: 'abrechnungen',
      component: () => import('../views/abrechnungen/AbrechnungenListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/abrechnungen/:id',
      name: 'abrechnung-detail',
      component: () => import('../views/abrechnungen/AbrechnungDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/mietzahlungen',
      name: 'mietzahlungen',
      component: () => import('../views/mietzahlungen/MietzahlungenListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/bewerbungen',
      name: 'bewerbungen',
      component: () => import('../views/bewerbungen/BewerbungenListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/bewerbungen/:id',
      name: 'bewerbung-detail',
      component: () => import('../views/bewerbungen/BewerbungDetailView.vue'),
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

  // Onboarding-Redirect für neue Vermieter: nur beim allerersten Login (0% Fortschritt)
  // oder wenn explizit gewünscht. Sobald einmal begonnen wurde, landet man im Dashboard.
  if (isAuthenticated && to.name === 'dashboard') {
    const onboardingStore = useOnboardingStore()
    try {
      await onboardingStore.fetchProgress()
      // Nur umleiten, wenn noch gar nichts erledigt ist UND der Nutzer nicht schon "isDone" ist
      if (onboardingStore.progressPercent === 0 && !onboardingStore.isDone) {
        return next({ name: 'onboarding-welcome', query: { redirect: to.fullPath } })
      }
    } catch {
      // Onboarding-Fehler sollten den App-Start nicht blockieren
    }
  }

  // Admin-Route schuetzen
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next({ name: 'dashboard' })
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
