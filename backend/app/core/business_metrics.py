from prometheus_client import Counter

# Auth Metrics
auth_failures_total = Counter(
    'auth_failures_total',
    'Total authentication failures',
    ['reason']
)

auth_tokens_created_total = Counter(
    'auth_tokens_created_total',
    'Total auth tokens created',
    ['token_type']
)

auth_tokens_consumed_total = Counter(
    'auth_tokens_consumed_total',
    'Total auth tokens consumed',
    ['token_type']
)

# Stripe Metrics
stripe_webhooks_total = Counter(
    'stripe_webhooks_total',
    'Total Stripe webhooks received',
    ['event_type', 'status']
)

stripe_webhook_failures_total = Counter(
    'stripe_webhook_failures_total',
    'Total Stripe webhook processing failures',
    ['event_type']
)
