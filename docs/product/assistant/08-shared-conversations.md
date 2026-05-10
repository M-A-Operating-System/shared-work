# 08 — Shared Conversations

## Overview

Any Data AI Assistant conversation may be shared with other authenticated DDA platform users **within the same organisation**. Sharing is **explicit and controlled** — there are no open links, no public access, and no anonymous participants. Every person in a shared conversation must hold an active DDA account in the same tenant. The org/tenant boundary and its rationale are specified in [15-memory-and-recall.md — Recall and access scope](./15-memory-and-recall.md).

---

## Invitation model

The conversation owner invites participants by searching for their name or email address **within their organisation's DDA user directory**. Cross-organisation sharing is not supported — the search is hard-scoped to the authenticated user's tenant.

| Rule | Specification |
|------|--------------|
| Search scope | DDA platform accounts within the same organisation/tenant only — it is not possible to invite a user from another tenant or an external email address |
| Shareable URLs | Not supported — invitations are directed to a specific named user |
| Maximum participants | **10 participants** (platform-configured) |
| Invitation delivery | In-platform notification (and optionally email, per the recipient's DDA notification preferences) |
| Invitation content | Conversation title, inviting user's name, accept/decline action |
| Accept | Adds the conversation to the participant's history panel under the **Shared With Me** group |
| Decline | Removes the invitation; no notification to the inviter |

---

## Participant model

All participants are **equal**. There are no roles, no elevated permissions, and no designated owner after the conversation has been shared. Any participant may:

- Invite additional authenticated DDA users to the conversation
- Remove any other participant
- Leave the conversation themselves
- Archive or rename the conversation

### The last-participant constraint

**A conversation must always have at least one participant.** This is a hard rule — a conversation with zero participants is not permitted. If a participant is the **last person remaining**, they cannot leave or remove themselves until at least one other user has been invited and accepted.

The interface handles this by:
- Disabling the **Leave** and **Self-remove** controls when the user is the last participant
- Surfacing a tooltip explaining the constraint: *"You are the only person in this conversation. Invite another participant before leaving."*
- Hiding the remove control next to their own name in the participant list when they are alone

If the last remaining participant's DDA account is **deactivated by an administrator**, the conversation is locked to **read-only** and flagged for administrative review.

---

## Conversation history visibility

When a participant accepts an invitation, they see the **full conversation history from the beginning** — not only from the point they were invited. This is intentional: the value of a shared conversation is the full context.

### Acceptance disclaimer

Before a user can accept an invitation, they must acknowledge a **full-page disclaimer**:

> **Before you join this conversation**
>
> You have been invited to join *"[Conversation title]"* by [Inviter name].
>
> By accepting, you will have access to the **complete conversation history** from the beginning — including all messages sent before you were invited.
>
> This conversation is a governance record. Everything you send will be stored as part of the DDA audit trail.
>
> [**Accept and open conversation**] &nbsp;&nbsp; [Decline]

The disclaimer is shown every time a user accepts an invitation — it is not a one-time acknowledgement. The user cannot enter the conversation without explicitly clicking **Accept and open conversation**. Declining removes the invitation with no notification to the inviter.

---

## Message attribution

In a shared conversation thread, each message bubble carries the **author's name and avatar**.

| Message source | Display |
|---------------|---------|
| Active user's messages | Right-aligned, muted bubble (standard) |
| Other participants' messages | Left-aligned, with a distinct colour per participant (DDA design system participant palette — up to nine distinct colours for non-owner participants) |
| Model responses | Left-aligned as the assistant — never attributed to a user |

The model label (and, on hover, the name of the user who submitted the preceding message) is visible on each assistant response.

---

## `@`-binding in shared conversations

Each user's `@`-binding typeahead is **scoped to their own DDA permission level**. A participant cannot bind to a DDA object they do not have access to in the main platform.

If a user submits a message containing a binding to an object that another participant **cannot access**:
- The restricted participant sees the binding chip labelled **"[Restricted object]"**
- They do not see the resolved context that was injected into the model prompt
- The tool call disclosure for any resulting MCP call shows `[Restricted — insufficient permissions]` on the result summary for that participant

This preserves the integrity of each user's permission boundary within the shared thread.

---

## Communication style in shared sessions

Each user's `communication_style` and `response_verbosity` profile settings apply **to the turns they submit**. A response generated for a `technical` user may sit alongside a response generated for a `business` user within the same thread.

The style label (e.g. `Business · Standard`) is visible on each assistant response — participants can always see the context in which a response was calibrated.

---

## Model and tool configuration in shared sessions

The active model and any opt-in MCP tools **apply to the session as a whole** — they are not per-user settings within a shared conversation. The user who submits a message determines the model and tool context for that turn, based on their current model chip selection and tool panel state. Other participants see the model label on each assistant response.

---

## Sharing controls (input area)

The **share icon** in the input area opens the participant management panel. From this panel, any participant may:

| Action | Behaviour |
|--------|----------|
| Search for users | Search within the authenticated user's organisation/tenant by name or email — cross-tenant results are excluded |
| Invite a user | Sends in-platform notification to the named user |
| View participants | See all current participants with name, avatar, and join date |
| Remove a participant | Removes their access; their prior messages remain in the thread |
| Leave the conversation | Removes self; only available when at least one other participant remains |

---

## Notifications

| Event | Notification |
|-------|-------------|
| New invitation received | In-platform notification with conversation title, inviter name, accept/decline |
| New message in shared conversation (not actively viewing) | In-platform notification + badge count on conversation in history panel |
| Email notifications | Follows user's DDA notification preferences; **off by default** for shared conversation activity |

---

## Audit trail for shared conversations

The audit trail records the `user_id` of the message author on every turn. In shared conversations this records the specific participant who submitted each turn.

| Recorded element | Table | Notes |
|-----------------|-------|-------|
| Message author | `assistant.turns.user_id` | FK to `auth.users`; records the submitting participant on every turn |
| Participant list | `assistant.conversation_participants` | `user_id`, `invited_by`, `invited_at`, `accepted_at`, `departed_at` |
| Invitation events | `assistant.conversation_participants` | Full invitation lifecycle per participant |

There are no role fields — all participants are equal. The audit record reflects actions taken, not role assignments.

Full schema detail is in the companion technical specification (Appendix D of Issue #216).

---

## Leaving and removing participants

| Action | Who can do it | Effect |
|--------|--------------|--------|
| Leave | Any participant (subject to last-participant constraint) | Conversation removed from leaver's history panel; their prior messages remain in thread |
| Remove another participant | Any participant | Removed user loses access; their prior messages remain; they may be reinvited |
| Reinvite a departed participant | Any remaining participant | Same invitation flow as initial invite |

Departed or removed participants' messages remain **visible to all remaining participants** and in the **full audit trail**. No message is deleted when a participant leaves.
