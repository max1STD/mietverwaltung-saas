<template>
  <!-- Landing Page — öffentliche Startseite -->
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-2">
          <span class="text-xl font-bold text-[#0D3B70]">MietVerwaltung</span>
        </div>
        <nav class="flex gap-4">
          <RouterLink to="/login" class="text-sm text-gray-600 hover:text-[#0D3B70]">
            Anmelden
          </RouterLink>
          <RouterLink to="/register" class="text-sm bg-[#0D3B70] text-white px-4 py-2 rounded-lg hover:bg-[#2a5a9e]">
            14 Tage kostenlos testen
          </RouterLink>
        </nav>
      </div>
    </header>

    <!-- Hero -->
    <main class="max-w-7xl mx-auto px-6 py-20">
      <div class="text-center">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">
          Die erste KI-gestützte<br />Mietverwaltung für DACH
        </h1>
        <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          80% der Vermieter-Arbeit automatisch erledigt — Dokumente scannen,
          Abrechnungen erstellen, Tickets kategorisieren, Mahnungen schreiben.
          Der Vermieter entscheidet, die KI macht den Rest.
        </p>
        <RouterLink to="/register"
          class="inline-block bg-[#0D3B70] text-white text-lg px-8 py-3 rounded-xl hover:bg-[#2a5a9e] transition-colors">
          14 Tage kostenlos testen
        </RouterLink>
        <p class="text-sm text-gray-400 mt-3">
          Nur 9,75 € pro Wohneinheit / Monat. Kein Free-Plan. Jederzeit kündbar.
        </p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * LandingView — öffentliche Startseite
 * Marketing-Seite mit USP und CTA zur Registrierung.
 */
</script>
