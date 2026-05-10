# 16 — Embedding and Web Component (Mode 2 — Inline Page)

## Scope of this document

This document covers the **`<ai-chat>` component** — the inline page embedding mode (Mode 2). It is the complete, full-featured conversation interface for use on dedicated assistant pages or embedded content sections.

The AI Chat Platform has three distinct embedding modes. For the full picture, see [18-entry-points-and-embedding-modes.md](./18-entry-points-and-embedding-modes.md):

| Mode | Component | Description |
|------|-----------|-------------|
| **1 — Floating Widget** | `<ai-chat-widget>` | FAB + collapsible mini/full panel, persists across pages |
| **2 — Inline Page** | `<ai-chat>` | This document — full three-zone layout embedded in a page |
| **3 — Form Field Assist** | `<ai-chat-field>` | Ephemeral contextual popover scoped to a form field |

Modes 1 and 2 share conversation history. Mode 3 is ephemeral and fully independent.

---

## Overview

The `<ai-chat>` component is a **custom HTML element** that host applications embed within their own UI. The component is self-contained — it manages its own state, handles streaming, renders content, and communicates with the platform API independently of the host application's framework.

Host applications include the component script once and configure it via HTML attributes and a JavaScript API. No framework-specific adapters are required; the component works in any modern web environment.

---

## Quick start

```html
<!-- 1. Include the component script -->
<script type="module" src="https://chat-platform.io/sdk/v1/ai-chat.js"></script>

<!-- 2. Mount the component -->
<ai-chat
  tenant-id="acme-corp"
  user-token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  theme="light"
></ai-chat>
```

The component renders at 100% of its container's width and height. Host applications control sizing via the container element.

---

## HTML attributes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `tenant-id` | Yes | string | The tenant's registered `tenantId` from the application config |
| `user-token` | Yes | string | The host-authenticated user's JWT. Must contain the required claims (see Authentication bridge). Refreshed by calling `updateToken()`. |
| `theme` | No | `"light"` \| `"dark"` | Initial colour scheme. Defaults to `"light"`. Dark mode is not supported in v1 — this attribute is reserved. |
| `locale` | No | string | BCP 47 locale tag (e.g. `"en-GB"`). Overrides the tenant config `scope.language` for UI strings. |
| `initial-conversation-id` | No | string | Opens a specific conversation on mount instead of the default new/recent conversation. Useful for deep-linking from the host application. |

---

## Authentication bridge

The platform does not authenticate users independently. The host application authenticates its users and passes the result to the component as a **signed JWT** via the `user-token` attribute.

### Required JWT claims

| Claim | Type | Description |
|-------|------|-------------|
| `sub` | string | User's unique identifier within the tenant |
| `email` | string | User's email address (used for invitation search) |
| `name` | string | User's display name (shown in shared conversation attribution) |
| `tenant_id` | string | Must match the `tenant-id` attribute — enforced server-side |
| `exp` | number | JWT expiry time — the component checks this and fires `token-expired` when within 60 seconds of expiry |

### Optional JWT claims

| Claim | Type | Description |
|-------|------|-------------|
| Any field in `userProfile.styleField` | string | Communication style value (e.g. `"business"`) |
| Any field in `userProfile.verbosityField` | string | Response verbosity value (e.g. `"concise"`) |
| Any role identifiers listed in MCP server `roles` | string[] | Role claims used to enforce MCP server access restrictions |
| `avatar_url` | string | URL to the user's avatar image (used in shared conversation thread) |

### JWT signature verification

The platform verifies the JWT signature against the JWKS endpoint registered by the host application at tenant registration time. Tokens signed with keys not in the registered JWKS are rejected.

### Token refresh

```javascript
const chat = document.querySelector('ai-chat');

// Listen for token expiry warning
chat.addEventListener('token-expired', async () => {
  const newToken = await yourAuthService.refreshToken();
  chat.updateToken(newToken);
});
```

`updateToken(token)` updates the active token without remounting the component. The user's session and conversation state are preserved.

---

## JavaScript API

Access the component's API via a reference to the element:

```javascript
const chat = document.querySelector('ai-chat');
```

### Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `updateToken(token)` | `token: string` | Refresh the user's JWT without remounting |
| `openConversation(id)` | `id: string` | Navigate to a specific conversation by ID |
| `startNewConversation()` | — | Open a new conversation, clearing the current one |
| `setLocale(locale)` | `locale: string` | Change the UI locale at runtime |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `currentConversationId` | `string \| null` | The ID of the currently open conversation |
| `isStreaming` | `boolean` | Whether the assistant is currently generating a response |

---

## Events

The component fires custom events on the element. Listen with `addEventListener`.

| Event | Detail payload | Description |
|-------|---------------|-------------|
| `binding-click` | `{ typeId, objectId, displayId, name }` | Fired when a user clicks a binding chip. The host application should handle navigation to the object's detail page. |
| `conversation-created` | `{ conversationId, title }` | Fired when a new conversation is created |
| `conversation-opened` | `{ conversationId, title }` | Fired when an existing conversation is opened |
| `turn-complete` | `{ conversationId, turnId, model, tokenCounts }` | Fired when an assistant response completes (not on partial/stopped) |
| `tool-invoked` | `{ conversationId, turnId, serverId, toolName, status }` | Fired on each MCP tool invocation completion |
| `token-expired` | — | Fired when the user's JWT is within 60 seconds of expiry |
| `error` | `{ code, message }` | Fired on component-level errors (auth failure, network error, config error) |
| `csat-submitted` | `{ conversationId, score, comment }` | Fired when a user submits a CSAT rating |

### Handling `binding-click`

```javascript
chat.addEventListener('binding-click', (event) => {
  const { typeId, objectId, displayId, name } = event.detail;

  switch (typeId) {
    case 'data_domain':
      router.navigate(`/domains/${objectId}`);
      break;
    case 'policy':
      router.navigate(`/policies/${objectId}`);
      break;
    default:
      console.log('Unhandled binding type:', typeId);
  }
});
```

---

## Sizing and layout

The `<ai-chat>` component renders at **100% width and 100% height of its containing element**. The host application controls the component's footprint by sizing the container.

### Full-page embedding

```css
/* Host application styles */
.chat-page {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
```

```html
<div class="chat-page">
  <ai-chat tenant-id="..." user-token="..."></ai-chat>
</div>
```

### Side panel embedding

```css
.chat-panel {
  width: 480px;
  height: 100%;
  border-left: 1px solid var(--border-color);
}
```

```html
<aside class="chat-panel">
  <ai-chat tenant-id="..." user-token="..."></ai-chat>
</aside>
```

### Minimum dimensions

| Dimension | Minimum |
|-----------|---------|
| Width | 320px |
| Height | 400px |

Below these minimums the component renders a fallback state: *"This panel is too small to display the assistant. Please expand the window."*

### Breakpoint behaviour in containers

When the component is mounted in a container narrower than the desktop breakpoint (< 1280px), it uses the container width rather than the viewport width to determine which layout to apply. A 480px side panel will use the tablet layout regardless of the overall page width.

---

## Content Security Policy (CSP)

The `<ai-chat>` component requires the following CSP directives on the host page:

```
script-src    https://chat-platform.io;
connect-src   https://api.chat-platform.io wss://api.chat-platform.io;
frame-src     'none';
img-src       https://cdn.chat-platform.io [host CDN origins];
style-src     https://chat-platform.io 'nonce-{page-nonce}';
```

Additionally, any URLs provided in the `branding` config (`logoUrl`, `faviconUrl`) must be included in `img-src`.

The component does not use `eval`, `inline-script`, or `blob:` URLs. All assets are loaded from `https://chat-platform.io` or `https://cdn.chat-platform.io`.

---

## React / Vue / Angular integration

The web component works without framework adapters. Framework-specific wrappers are provided for convenience:

**React:**
```jsx
import { AiChat } from '@chat-platform/react';

<AiChat
  tenantId="acme-corp"
  userToken={jwt}
  onBindingClick={({ typeId, objectId }) => navigate(`/${typeId}/${objectId}`)}
/>
```

**Vue:**
```vue
<AiChat
  tenant-id="acme-corp"
  :user-token="jwt"
  @binding-click="handleBindingClick"
/>
```

**Angular:**
```html
<ai-chat
  tenant-id="acme-corp"
  [attr.user-token]="jwt"
  (binding-click)="handleBindingClick($event)"
></ai-chat>
```

---

## Security considerations

### JWT forwarding

The `user-token` attribute value is passed as a bearer token to the platform API on every request. It must:
- Be issued by the host application's authenticated session (never a long-lived API key)
- Have a short expiry (recommended: 15 minutes)
- Be refreshed via `updateToken()` before expiry

### Preventing attribute injection

Do not interpolate untrusted user input into the `tenant-id` or `user-token` attributes. Both are validated server-side, but attribute injection could result in failed sessions or user confusion.

### CORS

The platform API enforces CORS. Only origins registered at tenant registration time are permitted to make requests. The host application must register all deployment origins (development, staging, production) during tenant setup.

### Iframe considerations

The component must not be embedded within an `<iframe>` — this prevents the platform from accessing the host page's cookies and local storage required for session management. The component is designed for direct DOM embedding only.
