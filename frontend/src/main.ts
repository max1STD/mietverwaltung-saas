import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import { useAuthStore } from './stores/auth'
import './styles/main.css'
import App from './App.vue'

/**
 * App-Initialisierung
 *
 * 1. Pinia und Router einrichten.
 * 2. Auth-Store initialisieren: Versuch, über Refresh-Token das aktuelle
 *    Benutzerprofil zu laden. So bleibt der Login auch nach Seiten-Reload bestehen.
 */
async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)
  app.use(router)

  const authStore = useAuthStore()
  await authStore.refreshToken()
  if (authStore.isAuthenticated) {
    await authStore.fetchUser()
  }

  app.mount('#app')
}

bootstrap()
