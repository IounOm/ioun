# Transactional email standard

For mail the system sends by itself (verify account, set password, order, notification), not
marketing mail.

## Stack

- **React Email**: templates are components, rendered on the server to HTML and plain text.
- **One layout** for every template: logo header, body, footer (company name, why the recipient
  got this mail).
- One sending helper over one SMTP / provider. Routes never send mail directly.

## Colors and type

- One **palette module** holds the design tokens converted to **hex**, because email clients do
  not support CSS variables or OKLCH. Change a token, change the palette with it. No hex anywhere
  else in templates.
- Font stack that covers Thai without loading a web font, e.g. `"Noto Sans Thai", "Leelawadee UI",
  Tahoma, Arial, sans-serif` (a brand web font may come first as long as the fallbacks follow).
- `line-height` >= 1.6 for Thai, body text >= 14px, inline styles (React Email handles them).

## Content

- Always send **HTML + plain text**.
- One primary CTA button **and** the raw URL under it, so the link still works when the button
  does not.
- Every string through the project's i18n layer, in the recipient's locale, keys complete in
  every language.
- Token links expire and are single-use. No personal data beyond what the mail needs; never
  another customer's prices.
- Money through the project's money helper.

## Dark mode and images

- Logo readable on light and dark: transparent PNG with a light plate, or a variant that works in
  both. Always `width`, `height` and `alt`.
- Never rely on a background color to carry meaning; some clients invert colors.
- Images on a public https URL, not large base64.

## Deliverability

- Sender domain has **SPF, DKIM and DMARC** (start DMARC at `p=none` with reports, then tighten).
  `From` is your own domain; `Reply-To` is a mailbox someone reads.
- System mail on its own subdomain (e.g. `mail.`), separate from marketing mail.
- Send logs keep the message id, template and status only, not the body or full addresses.

## Preview and test

- Dev: **Mailpit** (fake SMTP in Docker) to see every template for real; the React Email preview
  server while designing.
- Tests: every template renders in every locale, has a plain-text part, and the raw URL matches
  the button.
- Before go-live: send test mails to Gmail, Outlook and Apple Mail, in light and dark.
