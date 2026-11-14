import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Dashboard-Store — zentrale Datenquelle für KPIs, Finanzen und Insights.
 *
 * Endpunkte:
 * - GET /api/v1/dashboard/summary
 * - GET /api/v1/dashboard/object/{id}
 * - GET /api/v1/dashboard/financials
 * - GET /api/v1/dashboard/insights
 */

export interface DashboardSubscription {
  status: 'trial' | 'active' | 'past_due' | 'cancelled'
  billing_cycle: 'monthly' | 'yearly'
  wohnungen_count: number
  price_per_we: number
  total_monthly: number
  trial_ends_at?: string
  is_trial: boolean
}

export interface DashboardSummary {
  objekte_count: number
  einheiten_count: number
  mieter_count: number
  offene_tickets_count: number
  subscription: DashboardSubscription
  umsatz_diesen_monat: number
  kosten_diesen_monat: number
}

export interface DashboardObjectSummary {
  objekt_id: number
  name: string
  einheiten_total: number
  einheiten_vermietet: number
  vermietungsquote: number
  jahreskaltmiete: number
  jahreskosten: number
  kaufpreis: number | null
  bruttomietrendite: number | null
  nettomietrendite: number | null
}

export interface MonthlyFinance {
  monat: string
  label: string
  einnahmen: number
  kosten: number
  netto: number
}

export interface DashboardFinancials {
  monate: MonthlyFinance[]
  summe_einnahmen: number
  summe_kosten: number
  summe_netto: number
}

export interface DashboardInsight {
  typ: 'leerstand' | 'ticket' | 'mahnung' | 'frist' | 'info'
  titel: string
  beschreibung: string
  link?: string
  prioritaet: 'niedrig' | 'normal' | 'hoch' | 'dringend'
  entity_id?: number
}

export interface DashboardInsights {
  insights: DashboardInsight[]
}

export const useDashboardStore = defineStore('dashboard', () => {
  // State
  const summary = ref<DashboardSummary | null>(null)
  const objectSummaries = ref<Record<number, DashboardObjectSummary>>({})
  const financials = ref<DashboardFinancials | null>(null)
  const insights = ref<DashboardInsights | null>(null)
  const loading = ref(false)
  const error = ref<ApiError | null>(null)

  // Getters
  const hasData = computed(() => summary.value !== null)

  /**
   * Dashboard-Summary laden.
   */
  async function fetchSummary(): Promise<DashboardSummary | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<DashboardSummary>('/dashboard/summary')
      summary.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Objekt-Kennzahlen laden.
   */
  async function fetchObjectSummary(objektId: number): Promise<DashboardObjectSummary | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<DashboardObjectSummary>(`/dashboard/object/${objektId}`)
      objectSummaries.value[objektId] = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * 12-Monats-Finanzen laden.
   */
  async function fetchFinancials(): Promise<DashboardFinancials | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<DashboardFinancials>('/dashboard/financials')
      financials.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Smart Insights laden.
   */
  async function fetchInsights(): Promise<DashboardInsights | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<DashboardInsights>('/dashboard/insights')
      insights.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Alles auf einmal laden — für das initiale Dashboard.
   */
  async function loadDashboard(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await Promise.all([
        fetchSummary(),
        fetchFinancials(),
        fetchInsights(),
      ])
    } finally {
      loading.value = false
    }
  }

  return {
    summary,
    objectSummaries,
    financials,
    insights,
    loading,
    error,
    hasData,
    fetchSummary,
    fetchObjectSummary,
    fetchFinancials,
    fetchInsights,
    loadDashboard,
  }
})
