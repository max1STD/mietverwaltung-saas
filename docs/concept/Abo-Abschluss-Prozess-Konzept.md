# Abo-Abschluss-Prozess (Checkout) — MietVerwaltung SaaS

> **Status:** Konzept (Planung)  
> **Gültige Preise:** Free 0 € / Basis 14,90 € / Pro 29,90 € / Business 49,90 € (nach Wohnungen, nicht Objekten).  
> **Zahlungsanbieter:** Stripe (EU-Hosting, DSGVO-konform mit AVV).  
> **Ziel:** In 2–3 Klicks vom Interessenten zum zahlenden Kunden — so einfach wie Netflix, Spotify oder Apple One.

---

## 1. Vision: Netflix-style Checkout

### Warum Netflix-style?

Netflix, Spotify, Apple One und Disney+ haben den digitalen Checkout auf ein Minimum reduziert. Das Ergebnis: extrem hohe Conversion-Raten. Was machen sie richtig?

| Anbieter | Checkout-Länge | Was wir lernen können |
|----------|---------------|----------------------|
| **Netflix** | 1 Seite: Plan → Zahlungsmethode → los | Keine Registrierung vor dem Plan; E-Mail wird erst am Ende abgefragt. |
| **Spotify** | 2 Klicks: Plan wählen → Apple Pay / Karte | Mobile-first, Wallet-Zahlung bevorzugt, keine Adresse. |
| **Apple One** | 1 Klick auf iPhone (FaceID) | Apple Pay = Reibungslosigkeit null. Device-Authentifizierung ersetzt Formulare. |
| **Disney+** | Plan → Zahlungsmethode → starten | Klare Preisdarstellung, keine versteckten Schritte. |

### Grundprinzipien für MietVerwaltung

1. **Keine Frage, die Stripe nicht beantworten kann.** Wir fragen keine Rechnungsadresse, keine Telefonnummer, kein Geburtsdatum.
2. **Wallet first.** Apple Pay / Google Pay sind der schnellste Weg — 1 Klick + FaceID/TouchID.
3. **SEPA ist DACH-kritisch.** Viele deutsche Vermieter zahlen lieber per Lastschrift. IBAN eingeben, fertig.
4. **Sofortiger Zugang.** Nach dem Klick ist das Abo aktiv; keine "Wir prüfen Ihre Zahlung"-Wartezeit.
5. **Mobile = primär.** 60–70 % der Free-User werden das Abo auf dem Smartphone abschließen.

### Der ideale Flow Schritt für Schritt

```
1. User stößt im Dashboard an ein Limit (z. B. 3. Wohnung) oder klickt „Upgrade".
2. Pricing-Seite: 4 Karten, Pro als „Beliebtester Plan".
3. Klick 1: Plan wählen (Basis / Pro / Business) oder „30 Tage kostenlos testen".
4. Klick 2: Zahlungsmethode (Apple Pay / Karte / SEPA / PayPal).
5. Klick 3: „Jetzt abonnieren" bestätigen.
6. Sofort zurück ins Dashboard mit aktivem Abo.
```

---

## 2. Der Checkout-Flow (2–3 Klicks)

### 2.1 Klick 1: Plan wählen

#### Pricing-Page UX

- **4 Karten:** Free, Basis, Pro, Business.
- **Hervorhebung:** Pro bekommt den „Beliebtester Plan"-Badge.
- **Jahres/Monat-Toggle:** Default = jährlich (2 Monate geschenkt = 20 % Rabatt).
- **CTA je Plan:**
  - Free: „Kostenlos starten"
  - Basis/Pro: „30 Tage kostenlos testen" (keine Kreditkarte)
  - Business: „14 Tage kostenlos testen" (Kreditkarte nötig)
- **Apple-Style:** Navy #0D3B70, weiße Karten, sanfte Schatten, viel Whitespace.

#### PricingCard.vue

```vue
<script setup lang="ts">
interface Plan {
  id: 'free' | 'basis' | 'pro' | 'business'
  name: string
  monthlyPrice: number
  yearlyPrice: number
  wohnungen: string
  popular?: boolean
  cta: string
}

const props = defineProps<{
  plan: Plan
  billing: 'monthly' | 'yearly'
  isAnnualDefault: boolean
}>()

const emit = defineEmits<{ (e: 'select', planId: string): void }>()

const displayPrice = computed(() =>
  props.billing === 'yearly' ? props.plan.yearlyPrice / 12 : props.plan.monthlyPrice
)

const periodLabel = computed(() =>
  props.billing === 'yearly' ? '/Monat, jährlich bezahlt' : '/Monat'
)
</script>

<template>
  <div
    class="pricing-card"
    :class="{ 'pricing-card--popular': plan.popular }"
  >
    <div v-if="plan.popular" class="badge-popular">Beliebtester Plan</div>

    <h3 class="plan-name">{{ plan.name }}</h3>
    <div class="plan-price">
      <span class="price">{{ displayPrice.toFixed(2).replace('.', ',') }} €</span>
      <span class="period">{{ periodLabel }}</span>
    </div>
    <div v-if="billing === 'yearly'" class="yearly-total">
      {{ plan.yearlyPrice.toFixed(2).replace('.', ',') }} €/Jahr
      <span class="save-tag">2 Monate geschenkt</span>
    </div>

    <p class="limit">{{ plan.wohnungen }}</p>

    <button
      class="cta-button"
      :class="{ 'cta-button--primary': plan.popular }"
      @click="emit('select', plan.id)"
    >
      {{ plan.cta }}
    </button>
  </div>
</template>

<style scoped>
.pricing-card {
  background: var(--card-bg, #ffffff);
  border: 1px solid var(--card-border, #e5e5e7);
  border-radius: 20px;
  padding: 28px;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}
.pricing-card--popular {
  border: 2px solid #0D3B70;
  box-shadow: 0 12px 40px rgba(13, 59, 112, 0.12);
  transform: scale(1.02);
}
.badge-popular {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #0D3B70;
  color: #fff;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}
.plan-name { font-size: 20px; font-weight: 600; margin-bottom: 12px; }
.price { font-size: 34px; font-weight: 700; color: #0D3B70; }
.period { font-size: 14px; color: #6e6e73; }
.yearly-total { font-size: 13px; color: #6e6e73; margin-top: 8px; }
.save-tag { color: #0D3B70; font-weight: 600; margin-left: 6px; }
.limit { font-size: 15px; margin: 18px 0; }
.cta-button {
  width: 100%;
  padding: 14px 20px;
  border-radius: 12px;
  border: 1px solid #0D3B70;
  background: #fff;
  color: #0D3B70;
  font-weight: 600;
  cursor: pointer;
}
.cta-button--primary { background: #0D3B70; color: #fff; }
@media (prefers-color-scheme: dark) {
  .pricing-card {
    --card-bg: #1c1c1e;
    --card-border: #2c2c2e;
    color: #f5f5f7;
  }
  .period, .yearly-total { color: #a1a1a6; }
}
</style>
```

---

### 2.2 Klick 2: Zahlungsmethode

#### Zahlungsmethoden

| Methode | User-Aufwand | Besonderheit |
|---------|-------------|--------------|
| **Apple Pay / Google Pay** | 1 Klick + Biometrie | Wallet-Token; keine Kartendetails im Formular. |
| **Kreditkarte** | Kartennummer, Ablauf, CVC | Stripe Elements (hosted fields, PCI-DSS compliant). |
| **SEPA-Lastschrift** | IBAN eingeben | DACH-wichtig; Autovervollständigung + IBAN-Validierung. |
| **PayPal** | Redirect & Login | Optional; für Nutzer, die PayPal bevorzugen. |

**Keine Rechnungsadresse.** Stripe Checkout bzw. Elements erfasst Name und E-Mail bereits; bei SEPA ist das ausreichend. Rechnungsadresse wird nur bei Bedarf (z. B. B2B-USt-Nachweis) später im Settings-Bereich ergänzt.

#### PaymentMethodSelection.vue

```vue
<script setup lang="ts">
import { loadStripe } from '@stripe/stripe-js'
import { ref, onMounted } from 'vue'

const props = defineProps<{
  stripePublishableKey: string
  planName: string
  planPrice: number
}>()

const emit = defineEmits<{
  (e: 'token', methodId: string, type: 'card' | 'sepa_debit' | 'paypal'): void
}>()

const selected = ref<'card' | 'sepa' | 'paypal' | 'apple' | 'google'>('card')
const stripe = ref<any>(null)
const elements = ref<any>(null)
const cardElement = ref<any>(null)
const ibanElement = ref<any>(null)
const isReady = ref(false)
const error = ref('')

onMounted(async () => {
  stripe.value = await loadStripe(props.stripePublishableKey)
  elements.value = stripe.value.elements({
    locale: 'de',
    appearance: { theme: 'stripe', variables: { colorPrimary: '#0D3B70' } }
  })

  cardElement.value = elements.value.create('card', {
    style: { base: { fontSize: '16px' } }
  })
  cardElement.value.mount('#card-element')

  ibanElement.value = elements.value.create('iban', {
    supportedCountries: ['SEPA']
  })
  ibanElement.value.mount('#iban-element')

  isReady.value = true
})

async function confirmMethod() {
  error.value = ''
  try {
    if (selected.value === 'card') {
      const { paymentMethod, error: stripeError } = await stripe.value.createPaymentMethod({
        type: 'card',
        card: cardElement.value
      })
      if (stripeError) throw stripeError
      emit('token', paymentMethod.id, 'card')
    }
    else if (selected.value === 'sepa') {
      const { paymentMethod, error: stripeError } = await stripe.value.createPaymentMethod({
        type: 'sepa_debit',
        sepa_debit: ibanElement.value
      })
      if (stripeError) throw stripeError
      emit('token', paymentMethod.id, 'sepa_debit')
    }
    else if (selected.value === 'apple' || selected.value === 'google') {
      // Wallet-Button startet eigene Session; Token kommt über onToken-Callback.
      // Hier nur visuelle Auswahl, der eigentliche Flow wird im Parent gesteuert.
    }
  } catch (e: any) {
    error.value = e.message || 'Zahlungsmethode konnte nicht erfasst werden.'
  }
}
</script>

<template>
  <div class="payment-screen">
    <h2 class="title">Zahlungsmethode für {{ planName }}</h2>
    <p class="subtitle">{{ planPrice.toFixed(2).replace('.', ',') }} €/Monat · jederzeit kündbar</p>

    <div class="methods">
      <button
        v-for="m in [
          { id: 'apple', label: 'Apple Pay', icon: '' },
          { id: 'google', label: 'Google Pay', icon: 'G' },
          { id: 'card', label: 'Kreditkarte', icon: '💳' },
          { id: 'sepa', label: 'SEPA-Lastschrift', icon: '⇄' },
        ]"
        :key="m.id"
        class="method-button"
        :class="{ active: selected === m.id }"
        @click="selected = m.id"
      >
        <span class="icon">{{ m.icon }}</span>
        <span>{{ m.label }}</span>
      </button>
    </div>

    <div v-if="selected === 'card'" id="card-element" class="stripe-element" />
    <div v-if="selected === 'sepa'" id="iban-element" class="stripe-element" />

    <p v-if="error" class="error">{{ error }}</p>

    <button class="primary-button" :disabled="!isReady" @click="confirmMethod">
      Weiter
    </button>

    <p class="trust">
      🔒 Zahlung sicher über Stripe. Wir speichern keine Kartendaten.
    </p>
  </div>
</template>

<style scoped>
.payment-screen { max-width: 420px; margin: 0 auto; padding: 24px; }
.title { font-size: 24px; font-weight: 600; margin-bottom: 8px; }
.subtitle { color: #6e6e73; margin-bottom: 24px; }
.methods { display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px; }
.method-button {
  display: flex; align-items: center; gap: 12px;
  padding: 14px; border: 1px solid #e5e5e7; border-radius: 12px;
  background: #fff; cursor: pointer; text-align: left;
}
.method-button.active { border-color: #0D3B70; background: #f2f7ff; }
.stripe-element { margin: 20px 0; padding: 14px; border: 1px solid #e5e5e7; border-radius: 12px; }
.primary-button {
  width: 100%; padding: 16px; border-radius: 12px;
  background: #0D3B70; color: #fff; font-weight: 600; border: none;
}
.error { color: #d32f2f; margin: 12px 0; }
.trust { font-size: 12px; color: #6e6e73; text-align: center; margin-top: 16px; }
</style>
```

---

### 2.3 Klick 3: Bestätigen

#### Bestätigungs-Screen

- Zeigt Plan, Preis, Limits (z. B. „5 Wohnungen").
- Kein weiteres Formular.
- Bei Wallet-Zahlung: Button-Label „Apple Pay bestätigen" → FaceID/TouchID.
- Bei Karte/SEPA: „Jetzt abonnieren".
- Nach Erfolg: Apple-Style Checkmark + Sofort-Zugang.

#### CheckoutConfirm.vue

```vue
<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  planName: string
  planPrice: number
  wohnungen: string
  paymentMethodLabel: string
  isWallet: boolean
}>()

const emit = defineEmits<{ (e: 'subscribe'): void }>()
const loading = ref(false)

async function subscribe() {
  loading.value = true
  emit('subscribe')
}
</script>

<template>
  <div class="confirm-screen">
    <h2 class="title">Fast fertig</h2>

    <div class="summary-card">
      <div class="row">
        <span>Plan</span>
        <strong>{{ planName }}</strong>
      </div>
      <div class="row">
        <span>Preis</span>
        <strong>{{ planPrice.toFixed(2).replace('.', ',') }} €/Monat</strong>
      </div>
      <div class="row">
        <span>Inklusive</span>
        <strong>{{ wohnungen }}</strong>
      </div>
      <div class="row">
        <span>Zahlung</span>
        <strong>{{ paymentMethodLabel }}</strong>
      </div>
    </div>

    <button
      class="primary-button"
      :disabled="loading"
      @click="subscribe"
    >
      <span v-if="loading">Wird verarbeitet…</span>
      <span v-else-if="isWallet">Mit {{ paymentMethodLabel }} bestätigen</span>
      <span v-else>Jetzt abonnieren</span>
    </button>

    <p class="terms">
      Mit Klick startest du das Abo. Jederzeit im Account kündbar.
      Es gelten unsere <a href="/agb">AGB</a>.
    </p>
  </div>
</template>

<style scoped>
.confirm-screen { max-width: 420px; margin: 0 auto; padding: 24px; }
.title { font-size: 24px; font-weight: 600; margin-bottom: 20px; }
.summary-card {
  background: #fff; border: 1px solid #e5e5e7; border-radius: 16px;
  padding: 20px; margin-bottom: 24px;
}
.row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #f0f0f0; }
.row:last-child { border-bottom: none; }
.primary-button {
  width: 100%; padding: 16px; border-radius: 12px;
  background: #0D3B70; color: #fff; font-weight: 600; border: none;
}
.terms { font-size: 12px; color: #6e6e73; margin-top: 16px; }
</style>
```

---

## 3. Free Trial Flow (30 Tage kostenlos)

### 3.1 Basis/Pro: 30 Tage ohne Kreditkarte

```
1. User registriert sich → Free-Plan (2 Wohnungen).
2. Klickt „Upgrade" oder „30 Tage Pro testen".
3. Wählt Basis oder Pro.
4. CTA: „30 Tage kostenlos starten".
5. Keine Zahlungsinformation nötig.
6. Subscription.status = 'trialing', trial_ends_at = NOW() + 30 Tage.
7. Nach 30 Tagen:
   a) Zahlungsmethode hinterlegt → active
   b) Keine Zahlungsmethode → downgrade auf free, Daten bleiben erhalten
```

### 3.2 Business: 14 Tage mit Kreditkarte

```
1. User wählt Business.
2. Flow wie Netflix: Kreditkarte/SEPA hinterlegen, sofort 14 Tage testen.
3. Nach 14 Tagen: erste Abbuchung.
4. Keine Abbuchung möglich → downgrade auf free.
```

### 3.3 Trial-Reminder-E-Mails

| Zeitpunkt | Betreff | Inhalt | CTA |
|-----------|---------|--------|-----|
| Tag 0 | „Willkommen — Ihre 30 Tage Pro starten jetzt" | Plan aktiviert, keine Kreditkarte nötig, erste Schritte. | „Zum Dashboard" |
| Tag 7 | „Noch 23 Tage volle KI-Power" | Social Proof, 3 Top-Features. | „Zahlungsmethode hinterlegen" |
| Tag 25 | „Ihr Testzeitraum endet in 5 Tagen" | Was passiert danach (Downgrade auf Free, keine Datenverlust). | „Jetzt Abo sichern" |
| Tag 29 | „Ihr Testzeitraum endet morgen" | Loss-Aversion: Liste der Features, die gesperrt werden. | „Jetzt Zahlungsmethode hinterlegen" |
| Tag 30 (keine Zahlung) | „Willkommen im Free-Plan" | Downgrade erklärt, Daten erhalten, Upgrade jederzeit. | „Upgrade jederzeit" |
| Tag 30 (mit Zahlung) | „Danke — Ihr Abo ist aktiv" | Rechnungsbestätigung, nächste Abbuchung. | „Zum Dashboard" |

### 3.4 Trial-Flow-Code (FastAPI)

```python
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Subscription
from app.db import get_db
from app.auth import get_current_vermieter

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])

PLAN_LIMITS = {
    "free": 2,
    "basis": 5,
    "pro": 25,
    "business": None,
}

@router.post("/trial")
async def start_trial(
    plan: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_vermieter),
):
    if plan not in PLAN_LIMITS:
        raise HTTPException(400, "Ungültiger Plan")

    existing = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = existing.scalar_one_or_none()

    trial_days = 30 if plan in ("basis", "pro") else 14

    if sub is None:
        sub = Subscription(
            user_id=user.id,
            plan=plan,
            status="trialing",
            wohnungen_limit=PLAN_LIMITS[plan],
            trial_ends_at=datetime.utcnow() + timedelta(days=trial_days),
        )
        db.add(sub)
    elif sub.status == "free":
        sub.plan = plan
        sub.status = "trialing"
        sub.trial_ends_at = datetime.utcnow() + timedelta(days=trial_days)
        sub.wohnungen_limit = PLAN_LIMITS[plan]
    else:
        raise HTTPException(400, "Es besteht bereits ein aktives oder laufendes Abo")

    await db.commit()

    # Event für E-Mail „Trial gestartet"
    await event_bus.publish("trial.started", {"user_id": user.id, "plan": plan})

    return {
        "plan": plan,
        "status": "trialing",
        "trial_ends_at": sub.trial_ends_at,
    }
```

---

## 4. Stripe Integration

### 4.1 Empfehlung: Stripe Elements (inline)

**Stripe Checkout (hosted page)** vs. **Stripe Elements (inline):**

| Kriterium | Stripe Checkout | Stripe Elements |
|-----------|-----------------|-----------------|
| Implementierung | Minimal (Redirect) | Mehr Frontend-Code |
| Branding | Stripe-Page | Eigener Look (Apple-Style) |
| Conversion | Gut (vertraut) | Besser (kein Redirect, 2–3 Klicks) |
| Mobile | Gut | Perfekt |
| DACH-Methoden | Alle | Alle |

**Empfehlung:** Stripe Elements inline. Damit bleiben wir im eigenen UI, reduzieren Abbrüche und halten das Netflix-Gefühl.

### 4.2 Stripe Backend-Integration (FastAPI)

```python
import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Subscription
from app.db import get_db
from app.auth import get_current_vermieter

stripe.api_key = "sk_live_..."  # via Umgebungsvariable
STRIPE_WEBHOOK_SECRET = "whsec_..."

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

PRICE_MAP = {
    "basis": {"monthly": "price_1BasisM", "yearly": "price_1BasisY"},
    "pro": {"monthly": "price_1ProM", "yearly": "price_1ProY"},
    "business": {"monthly": "price_1BizM", "yearly": "price_1BizY"},
}

@router.post("/subscribe")
async def subscribe(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_vermieter),
):
    plan = payload["plan"]
    interval = payload.get("interval", "yearly")
    payment_method_id = payload.get("payment_method_id")

    # Stripe Customer anlegen/updaten
    customer_id = user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            metadata={"user_id": str(user.id)},
        )
        customer_id = customer.id
        user.stripe_customer_id = customer_id

    # Zahlungsmethode zuordnen
    if payment_method_id:
        stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payment_method_id},
        )

    # Subscription anlegen
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": PRICE_MAP[plan][interval]}],
        payment_settings={"save_default_payment_method": "on_subscription"},
        expand=["latest_invoice.payment_intent"],
        metadata={"user_id": str(user.id), "plan": plan},
    )

    # Lokale Subscription aktualisieren
    sub = await db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    )
    sub = sub.scalar_one_or_none() or Subscription(user_id=user.id)

    sub.plan = plan
    sub.status = "active"
    sub.stripe_customer_id = customer_id
    sub.stripe_subscription_id = subscription.id
    sub.payment_method_id = payment_method_id
    sub.current_period_start = datetime.fromtimestamp(subscription.current_period_start, tz=timezone.utc)
    sub.current_period_end = datetime.fromtimestamp(subscription.current_period_end, tz=timezone.utc)
    sub.cancel_at_period_end = False
    sub.trial_ends_at = None

    db.add(sub)
    await db.commit()

    await event_bus.publish("subscription.created", {"user_id": user.id, "plan": plan})

    return {
        "status": "active",
        "subscription_id": subscription.id,
        "client_secret": subscription.latest_invoice.payment_intent.client_secret
        if subscription.latest_invoice and subscription.latest_invoice.payment_intent
        else None,
    }
```

### 4.3 Stripe Webhook Handler

```python
@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(400, f"Webhook-Fehler: {e}")

    data = event["data"]["object"]

    if event["type"] == "invoice.payment_succeeded":
        subscription_id = data.get("subscription")
        sub = await get_subscription_by_stripe_id(db, subscription_id)
        if sub:
            sub.status = "active"
            sub.current_period_start = datetime.fromtimestamp(data["period_start"], tz=timezone.utc)
            sub.current_period_end = datetime.fromtimestamp(data["period_end"], tz=timezone.utc)
            await record_payment(db, sub.user_id, data["id"], data["amount_paid"], "succeeded")
            await event_bus.publish("payment.succeeded", {"user_id": sub.user_id})

    elif event["type"] == "invoice.payment_failed":
        subscription_id = data.get("subscription")
        sub = await get_subscription_by_stripe_id(db, subscription_id)
        if sub:
            sub.status = "past_due"
            await record_payment(db, sub.user_id, data["id"], data["amount_due"], "failed")
            await event_bus.publish("payment.failed", {"user_id": sub.user_id})

    elif event["type"] == "customer.subscription.deleted":
        subscription_id = data["id"]
        sub = await get_subscription_by_stripe_id(db, subscription_id)
        if sub:
            sub.status = "cancelled"
            sub.plan = "free"
            sub.wohnungen_limit = PLAN_LIMITS["free"]
            sub.cancel_at_period_end = False
            await event_bus.publish("subscription.cancelled", {"user_id": sub.user_id})

    elif event["type"] == "customer.subscription.updated":
        subscription_id = data["id"]
        sub = await get_subscription_by_stripe_id(db, subscription_id)
        if sub:
            sub.cancel_at_period_end = data.get("cancel_at_period_end", False)
            sub.current_period_start = datetime.fromtimestamp(data["current_period_start"], tz=timezone.utc)
            sub.current_period_end = datetime.fromtimestamp(data["current_period_end"], tz=timezone.utc)
            if data.get("status") == "active":
                sub.status = "active"

    await db.commit()
    return {"status": "ok"}
```

### 4.4 Stripe Customer Portal

```python
@router.post("/create-portal-session")
async def create_portal_session(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_vermieter),
):
    sub = await get_subscription_by_user_id(db, user.id)
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(400, "Kein Stripe-Konto vorhanden")

    session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url="https://app.mietverwaltung.de/settings/billing",
    )
    return {"url": session.url}
```

---

## 5. Upgrade / Downgrade / Kündigung

### 5.1 Regeln

| Aktion | Wirkung | Proration | UI-Kommunikation |
|--------|---------|-----------|------------------|
| **Upgrade** (Free → Basis → Pro → Business) | Sofort | Ja, anteilige Berechnung | „Upgrade wirksam sofort" |
| **Downgrade** (Business → Pro → Basis) | Nächste Periode | Keine Rückerstattung | „Änderung wirksam ab [Datum]" |
| **Kündigung** | Periodenende | Keine | „Aktiv bis [Datum], dann Free" |

### 5.2 Upgrade/Downgrade-Logik (FastAPI)

```python
PLAN_ORDER = ["free", "basis", "pro", "business"]

@router.post("/change-plan")
async def change_plan(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_vermieter),
):
    new_plan = payload["plan"]
    interval = payload.get("interval", "yearly")

    sub = await get_subscription_by_user_id(db, user.id)
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(400, "Kein aktives Abo")

    current_idx = PLAN_ORDER.index(sub.plan)
    new_idx = PLAN_ORDER.index(new_plan)
    is_upgrade = new_idx > current_idx

    if new_plan == sub.plan:
        return {"status": "unchanged"}

    stripe_subscription = stripe.Subscription.retrieve(sub.stripe_subscription_id)

    if is_upgrade:
        # Sofortiger Wechsel mit Proration
        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            items=[{
                "id": stripe_subscription["items"]["data"][0]["id"],
                "price": PRICE_MAP[new_plan][interval],
            }],
            proration_behavior="create_prorations",
        )
        sub.plan = new_plan
        sub.wohnungen_limit = PLAN_LIMITS[new_plan]
        sub.status = "active"
        msg = "Upgrade sofort wirksam"
    else:
        # Downgrade erst zum Periodenende
        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            items=[{
                "id": stripe_subscription["items"]["data"][0]["id"],
                "price": PRICE_MAP[new_plan][interval],
            }],
            proration_behavior="none",
        )
        msg = f"Downgrade wirksam ab {sub.current_period_end.strftime('%d.%m.%Y')}"

    await db.commit()
    await event_bus.publish("subscription.changed", {
        "user_id": user.id,
        "new_plan": new_plan,
        "is_upgrade": is_upgrade,
    })

    return {"status": sub.status, "effective_plan": new_plan, "message": msg}
```

### 5.3 Kündigung

```python
@router.post("/cancel")
async def cancel_subscription(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_vermieter),
):
    sub = await get_subscription_by_user_id(db, user.id)
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(400, "Kein aktives Abo")

    stripe.Subscription.modify(
        sub.stripe_subscription_id,
        cancel_at_period_end=True,
    )

    sub.cancel_at_period_end = True
    await db.commit()

    await event_bus.publish("subscription.cancellation_scheduled", {
        "user_id": user.id,
        "cancel_at": sub.current_period_end,
    })

    return {
        "status": "cancellation_scheduled",
        "active_until": sub.current_period_end,
        "afterwards_plan": "free",
    }
```

### 5.4 Upgrade/Downgrade-UI

```vue
<script setup lang="ts">
const plans = [
  { id: 'basis', name: 'Basis', price: 14.90, limit: '5 Wohnungen' },
  { id: 'pro', name: 'Pro', price: 29.90, limit: '25 Wohnungen', popular: true },
  { id: 'business', name: 'Business', price: 49.90, limit: 'Unbegrenzt' },
]

const currentPlan = ref('basis')
const emit = defineEmits(['change'])

function changePlan(planId: string) {
  if (confirm(`Möchtest du wirklich auf ${planId.toUpperCase()} wechseln?`)) {
    emit('change', planId)
  }
}
</script>

<template>
  <div class="plan-manager">
    <h3>Aktueller Plan: {{ currentPlan.toUpperCase() }}</h3>
    <div class="plan-list">
      <div
        v-for="plan in plans"
        :key="plan.id"
        class="plan-row"
        :class="{ current: plan.id === currentPlan }"
      >
        <div>
          <strong>{{ plan.name }}</strong>
          <span v-if="plan.popular" class="badge">Beliebt</span>
          <p>{{ plan.limit }} · {{ plan.price.toFixed(2).replace('.', ',') }} €/Mo</p>
        </div>
        <button
          v-if="plan.id !== currentPlan"
          class="change-btn"
          @click="changePlan(plan.id)"
        >
          {{ plan.price > plans.find(p => p.id === currentPlan)!.price ? 'Upgrade' : 'Downgrade' }}
        </button>
      </div>
    </div>
  </div>
</template>
```

---

## 6. DB-Schema Erweiterung

### 6.1 Bestehende Tabellen erweitern

```sql
-- ============================================================
-- subscriptions erweitern (v4 → Checkout-Ready)
-- ============================================================
ALTER TABLE subscriptions
    ADD COLUMN stripe_customer_id VARCHAR(255),
    ADD COLUMN stripe_subscription_id VARCHAR(255),
    ADD COLUMN payment_method_id VARCHAR(255),
    ADD COLUMN cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN billing_interval VARCHAR(10) CHECK (billing_interval IN ('monthly','yearly')) DEFAULT 'yearly',
    ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW(),
    ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();

-- ============================================================
-- plan_usage erweitern
-- ============================================================
ALTER TABLE plan_usage
    ADD COLUMN storage_bytes_used BIGINT NOT NULL DEFAULT 0,
    ADD COLUMN eid_used_this_month INT NOT NULL DEFAULT 0,
    ADD COLUMN ai_calls_used_this_month JSONB DEFAULT '{}',
    ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
```

### 6.2 Neue Tabellen

```sql
-- ============================================================
-- payment_history — Jede erfolgreiche/fehlgeschlagene Zahlung
-- ============================================================
CREATE TABLE payment_history (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_invoice_id   VARCHAR(255),
    stripe_charge_id    VARCHAR(255),
    amount              DECIMAL(10,2) NOT NULL,
    currency            VARCHAR(3) NOT NULL DEFAULT 'EUR',
    status              VARCHAR(20) NOT NULL CHECK (status IN ('succeeded','failed','refunded','disputed')),
    failure_message     TEXT,
    paid_at             TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_payment_history_user ON payment_history(user_id);
CREATE INDEX idx_payment_history_status ON payment_history(status);

-- ============================================================
-- invoices — Stripe-Rechnungen (Nur-Cache, Single-Source-of-Truth bleibt Stripe)
-- ============================================================
CREATE TABLE invoices (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_invoice_id   VARCHAR(255) UNIQUE NOT NULL,
    stripe_pdf_url      TEXT,
    amount              DECIMAL(10,2) NOT NULL,
    status              VARCHAR(20) NOT NULL,
    period_start        TIMESTAMPTZ,
    period_end          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_invoices_user ON invoices(user_id);

-- ============================================================
-- subscription_events — Internes Audit-Log für Abo-Änderungen
-- ============================================================
CREATE TABLE subscription_events (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id             INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    event_type          VARCHAR(50) NOT NULL CHECK (event_type IN (
        'trial_started','subscription_created','plan_changed','payment_succeeded',
        'payment_failed','cancellation_scheduled','subscription_cancelled','renewed'
    )),
    previous_plan       VARCHAR(20),
    new_plan            VARCHAR(20),
    metadata            JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_subscription_events_user ON subscription_events(user_id);

-- ============================================================
-- RLS für neue Tabellen
-- ============================================================
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY payment_history_isolation ON payment_history
    FOR ALL USING (user_id = current_setting('app.current_vermieter_id')::INT);

CREATE POLICY invoices_isolation ON invoices
    FOR ALL USING (user_id = current_setting('app.current_vermieter_id')::INT);

CREATE POLICY subscription_events_isolation ON subscription_events
    FOR ALL USING (user_id = current_setting('app.current_vermieter_id')::INT);
```

---

## 7. E-Mail-Templates für Abo-Events

### 7.1 Trial gestartet

**Betreff:** Willkommen — Ihre 30 Tage Pro starten jetzt

```html
<h1>Willkommen bei MietVerwaltung, {{ user.first_name }}!</h1>
<p>Sie haben den <strong>Pro-Plan</strong> für 30 Tage kostenlos aktiviert.</p>
<ul>
  <li>✓ 25 Wohnungen verwalten</li>
  <li>✓ KI-Beleg-Scan</li>
  <li>✓ KI-Mahnungen & Smart Insights</li>
</ul>
<p><strong>Keine Kreditkarte nötig.</strong> Ihr Testzeitraum endet am {{ trial_ends_at|date }}.</p>
<a href="https://app.mietverwaltung.de/dashboard" class="cta">Zum Dashboard</a>

<p style="font-size:12px;color:#6e6e73;">
  Hinweis: Nach Ablauf fallen Sie automatisch auf den Free-Plan zurück, wenn Sie keine Zahlungsmethode hinterlegen.
  Ihre Daten bleiben erhalten.
</p>
```

### 7.2 Trial endet in 7 Tagen

```html
<h1>Noch 7 Tage volle KI-Power</h1>
<p>Ihr Pro-Testzeitraum endet am {{ trial_ends_at|date }}.</p>
<p>Falls Sie keine Zahlungsmethode hinterlegen, wechseln Sie danach auf den Free-Plan (2 Wohnungen).</p>
<a href="https://app.mietverwaltung.de/settings/billing" class="cta">Zahlungsmethode hinterlegen</a>
```

### 7.3 Trial endet in 1 Tag

```html
<h1>Letzte Chance: Ihr Testzeitraum endet morgen</h1>
<p>Ab morgen sind diese Features gesperrt, sofern Sie nicht auf Pro upgraden:</p>
<ul>
  <li>KI-Beleg-Scan</li>
  <li>KI-Mahnungen & Smart Insights</li>
  <li>Mehr als 2 Wohnungen</li>
</ul>
<a href="https://app.mietverwaltung.de/settings/billing" class="cta">Jetzt Pro sichern</a>
```

### 7.4 Trial abgelaufen → Free Plan

```html
<h1>Willkommen im Free-Plan</h1>
<p>Ihr Pro-Testzeitraum ist abgelaufen. Ihr Account wurde auf den Free-Plan downgraded.</p>
<p>Was bleibt: 2 Wohnungen, Basis-Dashboard, manuelle Kosten-Erfassung.</p>
<p>Was gesperrt ist: KI-Features, mehr als 2 Wohnungen, PDF-Export.</p>
<a href="https://app.mietverwaltung.de/settings/billing" class="cta">Jederzeit upgraden</a>
```

### 7.5 Zahlung erfolgreich

```html
<h1>Zahlung erfolgreich</h1>
<p>Vielen Dank! Wir haben Ihr Abo für {{ plan_name }} erfolgreich verlängert.</p>
<table>
  <tr><td>Plan</td><td>{{ plan_name }}</td></tr>
  <tr><td>Betrag</td><td>{{ amount }} €</td></tr>
  <tr><td>Zeitraum</td><td>{{ period_start }} – {{ period_end }}</td></tr>
  <tr><td>Rechnung</td><td><a href="{{ invoice_pdf_url }}">PDF herunterladen</a></td></tr>
</table>
```

### 7.6 Zahlung fehlgeschlagen

```html
<h1>Zahlung konnte nicht eingezogen werden</h1>
<p>Leider ist die Abbuchung für Ihr Abo {{ plan_name }} fehlgeschlagen.</p>
<p>Grund: {{ failure_message }}</p>
<p>Bitte aktualisieren Sie Ihre Zahlungsmethode, um eine Unterbrechung zu vermeiden.</p>
<a href="https://app.mietverwaltung.de/settings/billing" class="cta">Zahlungsmethode aktualisieren</a>
<p style="font-size:12px;">Falls die Zahlung weiterhin ausfällt, wechseln wir Ihren Account in 7 Tagen auf den Free-Plan.</p>
```

### 7.7 Abo gekündigt

```html
<h1>Ihr Abo wurde gekündigt</h1>
<p>Sie haben Ihr {{ plan_name }}-Abo gekündigt. Es bleibt aktiv bis {{ active_until|date }}.</p>
<p>Danach wechseln Sie automatisch auf den Free-Plan. Ihre Daten bleiben erhalten.</p>
<a href="https://app.mietverwaltung.de/settings/billing" class="cta">Abo reaktivieren</a>
```

### 7.8 Upgrade bestätigt

```html
<h1>Upgrade bestätigt</h1>
<p>Sie nutzen jetzt <strong>{{ new_plan }}</strong>.</p>
<p>Alle neuen Features stehen Ihnen sofort zur Verfügung.</p>
<a href="https://app.mietverwaltung.de/dashboard" class="cta">Zum Dashboard</a>
```

---

## 8. UX-Details

### 8.1 Loading-States

```vue
<template>
  <button :disabled="isLoading" class="primary-button">
    <span v-if="isLoading" class="spinner"></span>
    <span v-else>Jetzt abonnieren</span>
  </button>
</template>

<style scoped>
.spinner {
  display: inline-block;
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
```

### 8.2 Fehlerbehandlung

| Fehler | Anzeige | Fallback |
|--------|---------|----------|
| Karte abgelehnt | Inline unter Stripe-Element: „Ihre Bank hat die Zahlung abgelehnt." | Anderes Zahlungsmittel anbieten. |
| IBAN ungültig | Inline: „Bitte überprüfen Sie die IBAN." | Stripe IBAN-Element validiert live. |
| 3D Secure fehlgeschlagen | Modal: „Bitte bestätigen Sie die Zahlung in Ihrer Banking-App." | Retry-Button. |
| Netzwerkfehler | Toast: „Verbindung gestört. Bitte versuchen Sie es erneut." | Wiederholen ohne Datenverlust. |

### 8.3 Success-Animation

```vue
<template>
  <div class="success-overlay">
    <svg class="checkmark" viewBox="0 0 52 52">
      <circle class="circle" cx="26" cy="26" r="25" fill="none" />
      <path class="check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8" />
    </svg>
    <h2>Abo aktiv!</h2>
    <p>Sie werden ins Dashboard weitergeleitet…</p>
  </div>
</template>

<style scoped>
.success-overlay {
  position: fixed; inset: 0; background: rgba(255,255,255,0.95);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.checkmark { width: 80px; height: 80px; }
.circle { stroke: #0D3B70; stroke-width: 3; stroke-dasharray: 166; stroke-dashoffset: 166; animation: draw 0.6s ease forwards; }
.check { stroke: #0D3B70; stroke-width: 3; stroke-dasharray: 48; stroke-dashoffset: 48; animation: draw 0.4s ease 0.4s forwards; }
@keyframes draw { to { stroke-dashoffset: 0; } }
</style>
```

### 8.4 Mobile-Optimierung

- Bottom-Sheet statt Modal auf iPhone (nativer Look).
- Apple Pay / Google Pay als erste Option sichtbar.
- Input-Felder mindestens 44 px hoch, 16px Font (kein Zoom auf iOS).
- Touch-ID/FaceID sofort auslösen, wenn Wallet gewählt.
- Ein-Klick-Zahlung ohne Scrollen.

### 8.5 Dark-Mode Support

```css
:root {
  --bg: #f5f5f7;
  --card-bg: #ffffff;
  --text: #1d1d1f;
  --primary: #0D3B70;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #000000;
    --card-bg: #1c1c1e;
    --text: #f5f5f7;
    --primary: #5e9aff;
  }
}
```

---

## 9. Rechtliches

### 9.1 Checkliste

| # | Anforderung | Status | Bemerkung |
|---|-------------|--------|-----------|
| 1 | AGB für Abonnements | ⚠️ nötig | Automatische Verlängerung, Kündigungsfrist, Preisanpassung. |
| 2 | Widerrufsrecht §355 BGB | ⚠️ nötig | Bei SaaS mit sofortiger Erfüllung kann Widerruf ausgeschlossen werden; Einwilligung erforderlich. |
| 3 | Impressum | ⚠️ nötig | Vollständige Anschrift, Telekommunikationsdaten. |
| 4 | Datenschutzerklärung | ⚠️ nötig | Stripe als Auftragsverarbeiter nennen, AVV verlinken. |
| 5 | AVV mit Stripe | ⚠️ nötig | Stripe Standard Contractual Clauses / DPA abschließen. |
| 6 | Preistransparenz | ⚠️ nötig | Alle Preise inkl. MwSt. angeben (19 % in DE). |
| 7 | Kostenpflichtige Verlängerung deutlich | ⚠️ nötig | „Abonnement verlängert sich automatisch" vor Checkout klar sichtbar. |
| 8 | Kündigungsmöglichkeit | ⚠️ nötig | Jederzeit im Account kündbar; einfacher als beim Abschluss. |
| 9 | Zahlungsmethoden-Belehrung | ⚠️ nötig | SEPA: Lastschriftmandat in E-Mail bestätigen. |
| 10 | EU-DSGVO Konformität | ⚠️ nötig | Datenverarbeitung dokumentieren, Einwilligung einholen. |
| 11 | Aufbewahrung von Zahlungsdaten | ⚠️ nötig | Keine Kreditkartendaten speichern; Stripe-IDs reichen. |
| 12 | MwSt.-Rechnungen | ⚠️ nötig | Stripe-Rechnung als PDF bereitstellen. |

### 9.2 SEPA-Lastschriftmandat (Textbaustein)

```text
Sie ermächtigen [Firmenname], Zahlungen von Ihrem Konto mittels Lastschrift einzuziehen.
Zugleich weisen Sie Ihr Kreditinstitut an, die von [Firmenname] auf Ihr Konto gezogenen
Lastschriften einzulösen. Hinweis: Sie können innerhalb von acht Wochen, beginnend mit dem
Belastungsdatum, die Erstattung des belasteten Betrages verlangen.
```

---

## 10. Kosten

### 10.1 Stripe-Gebühren

| Methode | Gebühr | Bemerkung |
|---------|--------|-----------|
| EU-Kreditkarte | 1,5 % + 0,25 € | Inkl. 3D Secure, Apple Pay, Google Pay. |
| SEPA-Lastschrift | 0,5 % | Günstig für wiederkehrende Zahlungen in DACH. |

### 10.2 Netto-Marge pro Plan

| Plan | Brutto | Stripe-Kosten (Karte) | Netto | Marge % |
|------|--------|----------------------|-------|---------|
| Basis | 14,90 € | 0,4735 € | **14,4265 €** | **96,82 %** |
| Pro | 29,90 € | 0,6985 € | **29,2015 €** | **97,66 %** |
| Business | 49,90 € | 0,9985 € | **48,9015 €** | **98,00 %** |

| Plan | Brutto | Stripe-Kosten (SEPA) | Netto | Marge % |
|------|--------|----------------------|-------|---------|
| Basis | 14,90 € | 0,0745 € | **14,8255 €** | **99,50 %** |
| Pro | 29,90 € | 0,1495 € | **29,7505 €** | **99,50 %** |
| Business | 49,90 € | 0,2495 € | **49,6505 €** | **99,50 %** |

### 10.3 Break-even inkl. Stripe

Bei geschätzten Fixkosten von 24 €/Monat und Annahme Kreditkartenzahlung:

| Plan | Netto/Kunde | Kunden für Break-even |
|------|------------|----------------------|
| Basis | 14,4265 € | **1,66** |
| Pro | 29,2015 € | **0,82** |
| Business | 48,9015 € | **0,49** |

> **Fazit:** Stripe frisst nur 0,5–3,2 % des Bruttoerlöses. Die Margen bleiben extrem hoch. Bei SEPA sind die Kosten fast vernachlässigbar. Das Abo-Modell ist deshalb sehr robust gegenüber Zahlungsanbieter-Gebühren.

### 10.4 Empfehlung zur Zahlungsmethode

- **Push Free-User zu SEPA:** Geringste Gebühren, besonders bei Jahreszahlung.
- **Wallets prominent platzieren:** Höchste Conversion, akzeptable Kosten.
- **PayPal optional:** Für Nutzer, die keine Karte eingeben wollen.

---

## 11. Payment & Checkout Sicherheit (100% dicht)

> **Prinzip:** Der Checkout-Prozess ist die sensibelste Schnittstelle der SaaS. Frontend ist nie vertrauenswürdig; Stripe-Webhooks sind die einzige Source of Truth für Zahlungsstatus.

---

### 11.1 Stripe Integration Sicherheit

| Regel | Umsetzung | Warum |
|-------|-----------|-------|
| Keine Kartendaten auf unserem Server | Stripe Elements (iframe) oder Stripe Checkout (hosted) | PCI-DSS SAQ-A = niedrigstes Compliance-Level |
| Secret Key NUR Backend | `STRIPE_SECRET_KEY` als Env-Variable, niemals im Frontend | Mit Secret Key kann alles abgebucht werden |
| Publishable Key nur Frontend | `pk_live_...` ist public und ungefährlich | Wird für Stripe.js benötigt |
| Webhook Secret separat | `STRIPE_WEBHOOK_SECRET` rotierbar | Verhindert gefälschte Webhooks |
| Keys nicht committed | `.env` in `.gitignore`, SOPS+age für Produktion | Keine Leaks in Repos oder Docker-Layern |
| Docker-Layer sauber | Multi-Stage-Build, keine `.env` im Image | Vermeidet `docker history` Leaks |

**Docker-Ausschluss in `.dockerignore`:**

```text
.env
.env.*
*.pem
secrets/
```

---

### 11.2 Webhook Sicherheit

#### Regeln

1. **Signature-Verification bei JEDEM Webhook.** `stripe.webhooks.construct_event` mit raw body.
2. **Raw-Body verwenden.** JSON-parsed body zerstört die Signatur-Validierung.
3. **Idempotenz.** `stripe_event_id` als UNIQUE in DB speichern; doppelte Events werden verworfen.
4. **IP-Whitelisting optional.** Signatur-Verifizierung reicht; IP-Filter zusätzlich möglich.
5. **Antwort innerhalb 3 Sekunden.** Schwere Arbeit (E-Mails, Plan-Änderungen) in Background-Queue.
6. **Jeder Webhook wird geloggt.** `audit_logs` + dedizierte `stripe_webhook_events` Tabelle.

#### Sicherer Webhook-Handler (FastAPI)

```python
import stripe
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from app.db import get_db
from app.models import Subscription, AuditLog, StripeWebhookEvent
from app.security import verify_csrf
from app.tasks import queue_task

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

STRIPE_WEBHOOK_SECRET = "whsec_..."  # aus Umgebungsvariable


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # 1. Raw Body holen (NICHT request.json())
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(400, "Missing stripe-signature")

    # 2. Stripe Signatur verifizieren
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(400, "Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid signature")

    event_id = event["id"]
    event_type = event["type"]

    # 3. Idempotenz: Event schon verarbeitet?
    async with db.begin_nested():
        exists = await db.execute(
            select(StripeWebhookEvent).where(StripeWebhookEvent.stripe_event_id == event_id)
        )
        if exists.scalar_one_or_none():
            return {"status": "already_processed"}

        # Event sofort als verarbeitet markieren (verhindert Race Conditions)
        db.add(StripeWebhookEvent(stripe_event_id=event_id, event_type=event_type))
        await db.flush()

    # 4. Audit-Log
    await log_audit(db, action="stripe_webhook_received", details={
        "event_id": event_id,
        "event_type": event_type,
    })

    # 5. Antwort innerhalb 3 Sekunden, schwere Arbeit in Queue
    background_tasks.add_task(process_stripe_event, event_id, event_type, event["data"]["object"])

    return {"status": "ok"}


async def process_stripe_event(event_id: str, event_type: str, data: dict):
    async with async_session() as db:
        try:
            if event_type == "invoice.payment_succeeded":
                await handle_payment_succeeded(db, data)
            elif event_type == "invoice.payment_failed":
                await handle_payment_failed(db, data)
            elif event_type == "customer.subscription.deleted":
                await handle_subscription_deleted(db, data)
            elif event_type == "customer.subscription.updated":
                await handle_subscription_updated(db, data)

            await db.execute(
                text("UPDATE stripe_webhook_events SET processed_at = NOW() WHERE stripe_event_id = :eid"),
                {"eid": event_id},
            )
            await db.commit()
        except Exception as exc:
            await db.rollback()
            # Dead-Letter-Queue / Admin-Alert
            await queue_task("admin.alert", {
                "message": f"Webhook-Verarbeitung fehlgeschlagen: {event_id}",
                "error": str(exc),
            })
            raise


async def handle_payment_succeeded(db: AsyncSession, invoice: dict):
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return

    # SELECT FOR UPDATE verhindert Race Conditions
    result = await db.execute(
        select(Subscription)
        .where(Subscription.stripe_subscription_id == subscription_id)
        .with_for_update()
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return

    sub.status = "active"
    sub.current_period_start = datetime.fromtimestamp(invoice["period_start"], tz=timezone.utc)
    sub.current_period_end = datetime.fromtimestamp(invoice["period_end"], tz=timezone.utc)

    await record_payment(db, sub.user_id, invoice["id"], invoice["amount_paid"], "succeeded")
    await event_bus.publish("payment.succeeded", {"user_id": sub.user_id})
```

#### Idempotenz-Tabelle

```sql
CREATE TABLE stripe_webhook_events (
    id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stripe_event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type      VARCHAR(100) NOT NULL,
    received_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ
);
CREATE INDEX idx_stripe_webhook_events_event_id ON stripe_webhook_events(stripe_event_id);
```

---

### 11.3 Checkout-Flow Sicherheit

#### Grundsätze

- **Frontend ist niemals Source of Truth.** Preis, Plan und Status kommen ausschließlich vom Backend / Webhook.
- **Subscription-Status wird NUR durch Webhooks geändert.** Das Frontend zeigt zwar "Erfolg", aber die DB wird erst durch `invoice.payment_succeeded` auf `active` gesetzt.
- **Race-Condition-Schutz** via `SELECT FOR UPDATE` beim Subscription-Update.
- **CSRF-Schutz** für alle Checkout-Endpunkte.
- **HTTPS Pflicht.** Stripe lehnt HTTP-Payment-Seiten ab.
- **Checkout-Session 30-Min-Timeout.** Stripe-Default.

#### Sicherer Subscribe-Endpunkt

```python
from fastapi import Depends, HTTPException, Header
from app.security import get_csrf_token, verify_csrf_token

@router.post("/subscribe")
async def subscribe(
    payload: SubscribeRequest,
    csrf_token: str = Header(..., alias="X-CSRF-Token"),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_vermieter),
):
    # 1. CSRF-Token prüfen
    await verify_csrf_token(user.id, csrf_token)

    # 2. Plan-Preis im Backend validieren (nicht aus Frontend übernehmen)
    if payload.plan not in PRICE_MAP:
        raise HTTPException(400, "Ungültiger Plan")

    # 3. Subscription mit Lock holen/erstellen
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user.id)
        .with_for_update()
    )
    sub = result.scalar_one_or_none()

    # 4. Stripe-Customer anlegen/updaten
    customer_id = user.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            metadata={"user_id": str(user.id)},
        )
        customer_id = customer.id
        user.stripe_customer_id = customer_id

    # 5. Zahlungsmethode anhängen
    if payload.payment_method_id:
        stripe.PaymentMethod.attach(payload.payment_method_id, customer=customer_id)
        stripe.Customer.modify(
            customer_id,
            invoice_settings={"default_payment_method": payload.payment_method_id},
        )

    # 6. Stripe Subscription anlegen
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": PRICE_MAP[payload.plan][payload.interval]}],
        payment_settings={"save_default_payment_method": "on_subscription"},
        metadata={"user_id": str(user.id), "plan": payload.plan},
        expand=["latest_invoice.payment_intent"],
    )

    # 7. Lokale DB vorbereiten — aber status erst Webhook setzt final
    if sub is None:
        sub = Subscription(user_id=user.id)
    sub.plan = payload.plan
    sub.status = "pending"  # Webhook setzt später 'active'
    sub.stripe_customer_id = customer_id
    sub.stripe_subscription_id = subscription.id
    sub.payment_method_id = payload.payment_method_id
    sub.billing_interval = payload.interval
    sub.cancel_at_period_end = False
    sub.trial_ends_at = None

    db.add(sub)
    await db.commit()

    await event_bus.publish("subscription.pending", {"user_id": user.id, "plan": payload.plan})

    return {
        "status": "pending",
        "subscription_id": subscription.id,
        "client_secret": subscription.latest_invoice.payment_intent.client_secret
        if subscription.latest_invoice and subscription.latest_invoice.payment_intent
        else None,
    }
```

---

### 11.4 Subscription-Management Sicherheit

- **Nur Backend darf Plans wechseln.** Frontend übergibt nur den Wunsch; Backend prüft Berechtigung und Stripe.
- **User darf nur EIGENE Subscription ändern.** `vermieter_id`-Check + RLS.
- **Kündigung** entweder über Stripe Customer Portal (Stripe-hosted) oder authentifizierten Backend-Endpoint.
- **Plan-Limit-Enforcement** bei JEDER `einheiten`-Erstellung im Backend (nicht Frontend).
- **Status-Sync** nur via Webhook.

#### Limit-Enforcement beim Anlegen einer Einheit

```python
from sqlalchemy import func

async def can_add_einheit(db: AsyncSession, vermieter_id: int) -> bool:
    sub_result = await db.execute(
        select(Subscription).where(Subscription.user_id == vermieter_id)
    )
    sub = sub_result.scalar_one_or_none()
    if not sub:
        return False

    limit = sub.wohnungen_limit  # None = unbegrenzt (Business)
    if limit is None:
        return True

    count_result = await db.execute(
        select(func.count(Einheit.id))
        .where(Einheit.vermieter_id == vermieter_id)
        .where(Einheit.deleted_at.is_(None))
    )
    current_count = count_result.scalar()
    return current_count < limit
```

---

### 11.5 SEPA-Lastschrift Sicherheit

- **SEPA-Mandat** wird von Stripe erstellt und bei Stripe gespeichert. Wir speichern keine IBAN.
- **Mandats-Referenz** loggen wir als Verweis; die IBAN bleibt bei Stripe.
- **First-Payment-Bestätigung** dauert 5–14 Tage. Wir warten auf `payment_succeeded` Webhook.
- **Trial + SEPA:** Mandat wird während Trial erfasst, aber noch nicht belastet.
- **DSGVO:** IBAN fließt direkt in Stripe-iframe; wir sehen sie nicht. AVV mit Stripe nötig.

```python
# Stripe SEPA PaymentMethod erstellen (Frontend übergibt payment_method_id)
# Wir speichern NIE IBAN, nur payment_method_id und mandate_id

async def store_sepa_mandate(db: AsyncSession, user_id: int, payment_method_id: str):
    pm = stripe.PaymentMethod.retrieve(payment_method_id)
    mandate_id = pm.sepa_debit.get("mandate") if hasattr(pm, "sepa_debit") else None

    await db.execute(
        text("""
            UPDATE subscriptions
            SET payment_method_id = :pmid,
                sepa_mandate_id = :mandate,
                payment_method_type = 'sepa_debit'
            WHERE user_id = :uid
        """),
        {"pmid": payment_method_id, "mandate": mandate_id, "uid": user_id},
    )
    await db.commit()
```

---

### 11.6 Fraud Prevention

| Maßnahme | Implementierung |
|----------|-----------------|
| Rate-Limiting | 3 Checkout-Versuche pro IP/Stunde |
| Stripe Radar | Aktivieren (kostenlos enthalten) |
| E-Mail-Validierung | MX-Record-Check bei Registrierung |
| Trial-Missbrauch | 1 Trial pro E-Mail + 1 Trial pro IP (gehasht) |
| Disposable E-Mail | Block-Liste temporärer Domains |

#### Rate-Limiting Middleware (FastAPI)

```python
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib

_checkout_attempts = defaultdict(list)

async def checkout_rate_limit(request: Request):
    client_ip = request.client.host
    now = datetime.utcnow()
    window = [t for t in _checkout_attempts[client_ip] if now - t < timedelta(hours=1)]
    _checkout_attempts[client_ip] = window

    if len(window) >= 3:
        raise HTTPException(429, "Zu viele Checkout-Versuche. Bitte versuchen Sie es später erneut.")

    _checkout_attempts[client_ip].append(now)


@router.post("/subscribe")
async def subscribe(...):
    await checkout_rate_limit(request)
    ...
```

#### Trial-Missbrauch-Schutz

```python
async def is_trial_eligible(db: AsyncSession, email: str, ip: str) -> bool:
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    email_trial = await db.execute(
        select(Subscription)
        .join(User)
        .where(User.email == email)
        .where(Subscription.status == "trialing")
    )
    if email_trial.scalar_one_or_none():
        return False

    ip_trial = await db.execute(
        select(func.count(Subscription.id))
        .where(Subscription.trial_ip_hash == ip_hash)
        .where(Subscription.created_at > datetime.utcnow() - timedelta(days=90))
    )
    if ip_trial.scalar() >= 3:
        return False

    # Disposable-Domain-Check
    domain = email.split("@")[-1].lower()
    if domain in DISPOSABLE_DOMAINS:
        return False

    return True
```

---

### 11.7 Datenbank-Sicherheit für Payment-Daten

- **`subscriptions`**: Nur `stripe_customer_id`, `stripe_subscription_id`, `payment_method_id` — **keine Kartendaten**.
- **`payment_history`**: Nur `stripe_invoice_id`, Betrag, Status — **keine Kartendaten**.
- **`bankverbindungen`**: Für Vermieter-Auszahlungen, separat von Stripe-Zahlungsdaten, **AES-256 verschlüsselt**.
- **IBAN bei SEPA**: Nur bei Stripe, nie in unserer DB.
- **Audit-Log**: Jede Abo-Änderung in `audit_logs` und `subscription_events`.

#### Verschlüsselte Bankverbindungen

```sql
CREATE TABLE bankverbindungen (
    id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vermieter_id        INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    iban_enc            BYTEA NOT NULL,          -- AES-256-GCM
    bic                 VARCHAR(11),
    kontoinhaber        VARCHAR(100) NOT NULL,
    is_default          BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 11.8 Error-Handling & Recovery

| Szenario | Verhalten |
|----------|-----------|
| Webhook-Ausfall | Stripe retry 3×, dann Dead-Letter-Queue + Admin-Alert |
| Payment failed | Status = `past_due`, 3 Retries via Stripe Smart Retries, E-Mail |
| Nach 3 failures | Status = `cancelled`, Downgrade auf Free, E-Mail |
| DB-Sync-Fehler | Stündlicher Reconciliation-Cron gleicht Stripe-Status mit DB ab |

#### Reconciliation-Cron (Python)

```python
async def reconcile_subscriptions():
    async with async_session() as db:
        # Lokal als aktiv markierte Abos
        result = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id.isnot(None))
        )
        local_subs = result.scalars().all()

        for sub in local_subs:
            stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
            expected_status = stripe_sub.status  # active, past_due, canceled, etc.
            expected_cancel_at_end = stripe_sub.cancel_at_period_end

            if sub.status != expected_status or sub.cancel_at_period_end != expected_cancel_at_end:
                await log_audit(db, action="subscription_reconciled", details={
                    "user_id": sub.user_id,
                    "old_status": sub.status,
                    "new_status": expected_status,
                })
                sub.status = expected_status
                sub.cancel_at_period_end = expected_cancel_at_end

        await db.commit()
```

---

## Nächste Schritte

1. **Abo-Modell.md aktualisieren:** Preise in `Abo-Modell.md` auf 14,90 € / 29,90 € / 49,90 € angleichen (aktuell noch 9,90 € / 19,90 € / 39,90 €).
2. **Mockup:** Pricing-Page + Checkout-Flow in `/root/mietverwaltung/mockup/pricing.html` ergänzen.
3. **Stripe-Test-Account:** Test-API-Keys einrichten und Webhook-Endpunkte testen.
4. **AGB & Datenschutz:** Rechtstexte erstellen lassen.
5. **AVV mit Stripe:** Im Stripe-Dashboard abschließen und verlinken.
6. **E-Mail-Templates:** In Transactional-E-Mail-Service (z. B. Resend) hinterlegen.
7. **Backend:** FastAPI-Routen, Webhooks und DB-Migrationen implementieren.
8. **Frontend:** Vue-Komponenten in Code-Base überführen.
9. **Sicherheit:** Penetration-Test der Checkout-Schnittstelle (CSRF, Webhook-Spoofing, Rate-Limiting, Trial-Abuse).
