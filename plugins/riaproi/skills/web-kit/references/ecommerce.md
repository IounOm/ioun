# E-commerce checklist

> **Rule:** this file lists what to decide, not current facts. Before choosing a payment
> provider, fee model, tax document flow or carrier, run a fresh web search: providers, fees and
> regulations change. Cite what you found with the date you checked it, and tell the user which
> numbers still need a quote from the provider.

## Payments

- Local instant payment (in Thailand: PromptPay / Thai QR) through a gateway with a verified
  webhook, not a personal QR plus a slip upload.
- Gateways to compare for the market (e.g. Opn Payments / Omise, 2C2P, GB Prime Pay, Stripe):
  supported methods, settlement currency, refund and dispute flow, recurring support, fees.
- Amounts are computed on the server through the money helper (2 decimals, one rounding rule).
  Webhooks verify the signature and are idempotent.
- Never store card numbers: hosted fields or the gateway's tokens only.

## Tax and documents

- Which receipts / tax invoices the business must issue, and whether e-Tax invoice applies.
- Numbering, credit notes for refunds, VAT shown per line or total.

## Personal data

- Privacy notice and consent before non-essential tracking (PDPA in Thailand, GDPR in the EU).
- Keep only what fulfilment needs; set a retention period; a way to ask for deletion.

## Shipping

- Carriers and cash on delivery: rates, pickup, tracking API, COD fees and payout timing.
- Address format for the country; phone number required for couriers.

## Catalog and checkout

- Variants (size / color), stock per variant, what happens when stock runs out mid-checkout.
- Guest checkout, clear totals before payment (shipping, tax, discounts), one-page or stepped
  checkout with visible progress.
- Order states and the emails they trigger (see `transactional-email.md`).

## Discoverability

- Product pages with `Product` / `Offer` structured data (see the `riaproi:marketing-schema` skill), one
  canonical URL per product, a sitemap.
- Analytics events for view item, add to cart, begin checkout and purchase, after consent.
