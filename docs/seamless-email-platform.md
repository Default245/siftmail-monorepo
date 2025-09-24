# SiftMail Seamless Email Experience Platform

## Vision
Deliver a calm, secure inbox that automatically neutralizes noise, surfaces what matters, and keeps people at inbox zero from the moment they sign in.

## Core Outcomes
- **Zero spam and phishing surprises.** Multi-engine analysis blocks malicious intent while keeping people in the loop with human-readable explanations.
- **Organized intent-based streams.** Finance, travel, community, and other contexts auto-route so every account feels instantly tidy.
- **High-value clarity.** Critical emails summarize into executive snippets the moment the app opens.
- **Multi-account calm.** Personal, work, and shared mailboxes act like one orchestrated workspace with consistent controls.
- **Sustained inbox zero.** Playbooks and nudges maintain the calm state every day.

## Pillars & Features
### 1. Trustworthy Defense
- Layered spam scoring with LLM content understanding, sender reputation, and header forensics.
- Phishing heuristics (urgent tone, credential requests, payment lures) that immediately quarantine suspicious mail.
- Explainable badges and undo for every automated action to maintain user trust.

### 2. Intent Intelligence
- Keyword/semantic detectors map messages into categories such as Finance, Travel, Logistics, Social, and Security Alert.
- Graymail logic suggests quick archive/bulk actions for newsletters and promotions.
- Adaptive importance scoring combines sender history and past behavior to highlight crucial threads.

### 3. High-Value Summaries
- The top five important emails render as compact snippets containing sender context, key asks, and recommended next steps.
- Action chips (approve, delegate, snooze) let users respond without opening the entire thread.
- Summaries delivered via morning digest and within the product dashboard.

### 4. Multi-Account Command Center
- OAuth onboarding connects Gmail, Outlook, and custom IMAP accounts with per-profile preferences.
- Unified search and prioritized timeline across all accounts while respecting compliance boundaries.
- Shared mailbox support with assignment, internal notes, and escalation to security teams.

### 5. Inbox Zero Lifecycle
1. **Connect** accounts in minutes.
2. **Sweep** historical mail to categorize, quarantine spam, and surface commitments.
3. **Focus** on high-value snippets and suggested actions.
4. **Nudge** users with daily digest reminders and goal tracking.
5. **Learn** continuously from feedback to keep the inbox calm.

## System Overview
- **FastAPI backend** provides classification, batch scoring, and inbox snapshot endpoints.
- **Static frontend** communicates the experience and integrates with the backend for onboarding.
- **Data flows**: emails are ingested, classified, summarized, and aggregated into category totals and inbox zero plans.

## Security & Privacy
- OAuth with the minimum necessary scopes per provider.
- Deterministic quarantine with reversible actions (no destructive deletes).
- Auditable explanation logs to help people understand why every action was taken.

## Roadmap Highlights
- Expand classification models with semantic embeddings for richer intent detection.
- Roll out proactive assistant that drafts responses for high-value emails.
- Integrate with calendar and task systems for end-to-end follow-up workflows.

