import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient, { type ApiError, normalizeError } from '@/api/client'

/**
 * Billing-Store — verwaltet Abo-Status, Preisvorschau und Stripe-Checkout.
 */

export interface Subscription {
  id: number
  user_id: number
  status: 'trial' | 'active' | 'past_due' | 'cancelled'
  price_per_we: string
  billing_cycle: 'monthly' | 'yearly'
  wohnungen_count: number
  total_monthly: string
  total_yearly: string
  trial_ends_at: string | null
  current_period_start: string | null
  current_period_end: string | null
  stripe_subscription_id: string | null
  cancel_at_period_end: boolean
}

export interface PricePreview {
  wohnungen_count: number
  price_per_we: string
  interval: 'monthly' | 'yearly'
  total_monthly: string
  total_yearly: string
  yearly_discount_percent: number
  currency: string
}

export interface CheckoutSession {
  session_url: string | null
  session_id: string | null
  mode: string
  message: string | null
}

export interface PortalSession {
  url: string | null
  message: string | null
}

export const useBillingStore = defineStore('billing', () => {
  // State
  const subscription = ref<Subscription | null>(null)
  const pricePreview = ref<PricePreview | null>(null)
  const checkoutSession = ref<CheckoutSession | null>(null)
  const portalSession = ref<PortalSession | null>(null)
  const loading = ref(false)
  const error = ref<ApiError | null>(null)

  // Getters
  const isTrial = computed(() => subscription.value?.status === 'trial')
  const isActive = computed(() => subscription.value?.status === 'active')
  const isCancelled = computed(() => subscription.value?.status === 'cancelled')
  const currentTotal = computed(() => {
    if (!subscription.value) return '0.00'
    return subscription.value.billing_cycle === 'yearly'
      ? subscription.value.total_yearly
      : subscription.value.total_monthly
  })

  /**
   * Preisvorschau für eine WE-Anzahl abrufen.
   */
  async function fetchPricePreview(we: number, interval: 'monthly' | 'yearly' = 'yearly'): Promise<PricePreview | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<PricePreview>('/billing/price-preview', {
        params: { we, interval },
      })
      pricePreview.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Aktuelles Abonnement laden.
   */
  async function fetchSubscription(): Promise<Subscription | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Subscription>('/billing/subscription/me')
      subscription.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Checkout-Session starten.
   */
  async function startCheckout(
    weCount: number,
    interval: 'monthly' | 'yearly',
    successUrl?: string,
    cancelUrl?: string,
  ): Promise<CheckoutSession | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<CheckoutSession>('/billing/checkout-session', {
        we_count: weCount,
        interval,
        success_url: successUrl || window.location.origin + '/dashboard',
        cancel_url: cancelUrl || window.location.origin + '/einstellungen',
      })
      checkoutSession.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Abo aktualisieren (WE-Anzahl / Intervall).
   */
  async function updateSubscription(
    weCount: number,
    interval: 'monthly' | 'yearly',
  ): Promise<Subscription | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Subscription>('/billing/subscription/me', {
        we_count: weCount,
        interval,
      })
      subscription.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Abo kündigen.
   */
  async function cancelSubscription(reason?: string): Promise<Subscription | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Subscription>('/billing/subscription/me/cancel', {
        reason: reason || '',
      })
      subscription.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Stripe Customer Portal öffnen.
   */
  async function openCustomerPortal(returnUrl?: string): Promise<PortalSession | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<PortalSession>('/billing/portal', {
        return_url: returnUrl || window.location.origin + '/einstellungen',
      })
      portalSession.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    subscription,
    pricePreview,
    checkoutSession,
    portalSession,
    loading,
    error,
    isTrial,
    isActive,
    isCancelled,
    currentTotal,
    fetchPricePreview,
    fetchSubscription,
    startCheckout,
    updateSubscription,
    cancelSubscription,
    openCustomerPortal,
  }
})
