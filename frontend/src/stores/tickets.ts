import { defineStore } from 'pinia'
import { ref } from 'vue'
import apiClient, { ApiError, normalizeError } from '@/api/client'

/**
 * Tickets-Store — Verwaltung des Ticketing-Systems inklusive Kommentare.
 *
 * Endpunkte:
 * - GET/POST/PATCH/DELETE /api/v1/tickets
 * - GET /api/v1/tickets/{id}
 * - GET/POST /api/v1/tickets/{id}/kommentare
 */

export type TicketKategorie =
  | 'heizung'
  | 'wasser'
  | 'elektrik'
  | 'schimmel'
  | 'sanitaer'
  | 'schluessel'
  | 'sauberkeit'
  | 'sonstiges'

export type TicketPrioritaet = 'niedrig' | 'normal' | 'hoch' | 'dringend'

export type TicketStatus =
  | 'offen'
  | 'in_bearbeitung'
  | 'wartend_auf_mieter'
  | 'wartend_auf_handwerker'
  | 'erledigt'
  | 'geschlossen'
  | 'abgelehnt'

export interface Ticket {
  id: string
  titel: string
  beschreibung?: string
  kategorie?: TicketKategorie | string
  prioritaet?: TicketPrioritaet | string
  status?: TicketStatus | string
  objekt_id?: string
  einheit_id?: string
  mieter_id?: string
  zugewiesen_an?: string
  created_at?: string
  updated_at?: string
  mieter?: {
    id: string
    name: string
  }
  objekt?: {
    id: string
    bezeichnung: string
  }
  einheit?: {
    id: string
    bezeichnung: string
  }
}

export interface TicketKommentar {
  id: string
  ticket_id: string
  autor_id?: string
  autor_name?: string
  nachricht: string
  intern?: boolean
  created_at?: string
}

export const useTicketsStore = defineStore('tickets', () => {
  // State
  const tickets = ref<Ticket[]>([])
  const currentTicket = ref<Ticket | null>(null)
  const kommentare = ref<TicketKommentar[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<ApiError | null>(null)

  /**
   * Alle Tickets laden (optional gefiltert per Query-Parameter).
   */
  async function fetchTickets(params?: Record<string, string>): Promise<Ticket[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Ticket[]>('/tickets', { params })
      tickets.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Einzelnes Ticket laden.
   */
  async function fetchTicket(id: string): Promise<Ticket | null> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<Ticket>(`/tickets/${id}`)
      currentTicket.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      loading.value = false
    }
  }

  /**
   * Neues Ticket anlegen.
   */
  async function createTicket(payload: Partial<Ticket>): Promise<Ticket | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<Ticket>('/tickets', payload)
      tickets.value.unshift(data)
      currentTicket.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Ticket aktualisieren (Status, Priorität, Zuweisung etc.).
   */
  async function updateTicket(id: string, payload: Partial<Ticket>): Promise<Ticket | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.patch<Ticket>(`/tickets/${id}`, payload)
      const index = tickets.value.findIndex((t) => t.id === id)
      if (index !== -1) {
        tickets.value[index] = data
      }
      if (currentTicket.value?.id === id) {
        currentTicket.value = data
      }
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Ticket löschen.
   */
  async function deleteTicket(id: string): Promise<boolean> {
    saving.value = true
    error.value = null
    try {
      await apiClient.delete(`/tickets/${id}`)
      tickets.value = tickets.value.filter((t) => t.id !== id)
      if (currentTicket.value?.id === id) {
        currentTicket.value = null
      }
      return true
    } catch (err) {
      error.value = normalizeError(err as Error)
      return false
    } finally {
      saving.value = false
    }
  }

  /**
   * Kommentare eines Tickets laden.
   */
  async function fetchKommentare(ticketId: string): Promise<TicketKommentar[]> {
    loading.value = true
    error.value = null
    try {
      const { data } = await apiClient.get<TicketKommentar[]>(`/tickets/${ticketId}/kommentare`)
      kommentare.value = data
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * Kommentar zu einem Ticket hinzufügen.
   */
  async function createKommentar(
    ticketId: string,
    nachricht: string,
    intern = false,
  ): Promise<TicketKommentar | null> {
    saving.value = true
    error.value = null
    try {
      const { data } = await apiClient.post<TicketKommentar>(`/tickets/${ticketId}/kommentare`, {
        nachricht,
        intern,
      })
      kommentare.value.push(data)
      return data
    } catch (err) {
      error.value = normalizeError(err as Error)
      return null
    } finally {
      saving.value = false
    }
  }

  /**
   * Aktuelles Ticket setzen.
   */
  function setCurrentTicket(ticket: Ticket | null): void {
    currentTicket.value = ticket
  }

  /**
   * Fehler-State zurücksetzen.
   */
  function clearError(): void {
    error.value = null
  }

  return {
    tickets,
    currentTicket,
    kommentare,
    loading,
    saving,
    error,
    fetchTickets,
    fetchTicket,
    createTicket,
    updateTicket,
    deleteTicket,
    fetchKommentare,
    createKommentar,
    setCurrentTicket,
    clearError,
  }
})
