<!--
Sync Impact Report
- Version change: 1.1.0 → 1.1.1 (PATCH: wording only)
- Modified sections: Platform & Technology Constraints — the environment is described generically
  ("the demo environment") instead of by name and URL, so the repository can be published and
  reused; the rule that changing the target environment needs an amendment is unchanged.
- Added/removed sections: none
- Deferred TODOs: none
-->

# Baku Travel Agent Constitution

## Core Principles

### I. Spec-First Agent Design

Every agent capability (instructions, skills, tools, knowledge sources, settings) MUST trace to
a requirement in an approved Spec Kit specification before any agent YAML is written or changed.

- Work follows the Spec Kit flow: specify → (clarify) → plan → tasks → implement.
- A capability with no matching requirement MUST be removed or have a spec added for it first.
- Plans MUST map each requirement to the Copilot Studio artifact that implements it.

**Rationale**: Generative agents drift easily; traceability keeps behavior intentional and
reviewable.

### II. Grounded & Honest Travel Information

Time-sensitive or safety-relevant travel facts (visa and e-visa rules, entry requirements,
customs, currency and exchange, safety advisories, transport schedules, opening hours, prices)
MUST come from configured, authoritative knowledge sources and MUST be presented with the source.

- Official sources (e.g., Azerbaijan government e-visa portal, official tourism board, embassy and
  government travel advisories) take precedence over blogs or aggregators.
- When the agent cannot ground an answer, it MUST say so plainly and point the traveler to the
  relevant official source instead of inventing details.
- Answers about rules that change (visas, fees, entry requirements) MUST advise travelers to
  verify with the official source before traveling.

**Rationale**: Wrong visa or entry information causes real harm to travelers; honesty about
limits is better than a confident but wrong answer.

### III. Traveler Safety & Privacy (NON-NEGOTIABLE)

- The agent MUST NOT book, reserve, purchase, or take any action that spends money or commits the
  traveler without an explicit, per-action confirmation from the user in the conversation.
- **Confirming a plan is not booking.** A confirmed plan is a quote with a reference. Confirming
  it MUST NOT reserve with any hotel or provider, take a payment, or send the plan to a third
  party. Any future feature that does book or pay MUST be specified separately and meet the
  per-action confirmation rule above.
- The agent MUST NOT request, collect, or store sensitive personal data in chat: passport or ID
  numbers, payment card or bank details, passwords, or similar identifiers. If a user volunteers
  such data, the agent MUST NOT repeat it and MUST advise using the official channel instead.
- Only the minimum trip context needed (dates, party size, interests, budget range) may be asked
  for during planning.
- **Plan holder contact details** (full name, email address, phone number) MAY be collected, and
  only at the confirmation step. They MUST be used only in the confirmed plan and its PDF, and
  MUST NOT be reused for any other purpose (such as marketing) or shared with third parties.
- Safety and health guidance MUST be framed as general information with a pointer to official
  advisories, not as professional advice.

**Rationale**: A travel assistant is trusted with plans and money; privacy and consent are the
baseline for that trust.

### IV. Copilot Studio Native, YAML as Source of Truth

- The agent MUST use Copilot Studio's modern generative orchestration (agentic loop with
  instructions, skills, tools, and knowledge). Classic topic-based flows are allowed only where
  the plan documents why orchestration cannot meet the requirement.
- All agent assets MUST live as YAML in this repository, authored with the Copilot Studio
  authoring plugin (mcs-assistant) and PAC CLI. The repository, not the portal, is the source of
  truth; portal-only edits MUST be pulled (`pac copilot pull`) and committed before further work.
- YAML MUST be validated before every `pac copilot push`.
- Nothing is published (`pac copilot publish`) without the review gate in this constitution.

**Rationale**: Version-controlled YAML makes changes reviewable, reproducible, and reversible.

### V. Testable Conversations

- Every user story MUST include example conversations (user prompt plus the expected behavior or
  acceptance criteria) in its spec.
- Before publishing, those conversations MUST be run against the pushed draft agent (for example
  with the plugin's chat command) and the results recorded in the feature folder.
- Each release MUST include negative tests: an ungroundable question, a request to book without
  confirmation, and a user volunteering sensitive data (Principles II and III).

**Rationale**: Conversation tests are the only practical way to verify generative behavior
before travelers see it.

### VI. Simplicity & Incremental Delivery

- The first release is a minimal, useful agent: trip and itinerary planning for Baku plus grounded
  practical information (entry, money, transport, neighborhoods, sights, etiquette).
- Integrations (flights, hotels, weather, maps, bookings) come in later, separately specified
  increments, each delivering value on its own.
- New skills, tools, or connectors MUST be justified in the plan; YAGNI applies.

**Rationale**: A small agent that is accurate beats a broad agent that is unreliable.

## Platform & Technology Constraints

- **Platform**: Microsoft Copilot Studio, deployed to one designated Power Platform environment
  with Dataverse (the "demo environment"; its URL is chosen at `pac copilot init`, see
  `docs/03-tenant-and-environment.md`). Changing the target environment of a deployed agent
  requires a constitution amendment.
- **Tooling**: Spec Kit (`specify` CLI) for specifications; Copilot Studio authoring plugin
  (mcs-assistant) and Power Platform CLI (`pac`, version 2.9.3 or later) for authoring and ALM.
- **ALM**: `pac copilot pull`, `push`, and `publish` are the only supported ways to sync with the
  environment.
- **Secrets**: No credentials, tokens, or connection secrets are committed. Connections are
  configured in the environment, not in YAML.
- **Language**: English is the default conversation language; additional languages require
  their own specification.

## Development Workflow & Quality Gates

1. **Specify**: write or update the spec with user stories and example conversations.
2. **Clarify** (recommended): resolve ambiguities before planning.
3. **Plan**: map requirements to agent artifacts and knowledge sources; run the Constitution
   Check.
4. **Tasks**: generate dependency-ordered tasks; run `/speckit-analyze` for consistency.
5. **Implement**: author YAML with the plugin, validate it, then `pac copilot push` to the draft.
6. **Test**: run the spec's example conversations and the negative tests against the draft.
7. **Review gate**: a human reviews the YAML diff and the test results.
8. **Publish**: `pac copilot publish` only after the review gate passes.

A plan MUST NOT proceed past its Constitution Check while it violates a principle, unless the
violation is recorded with a justification in the plan's Complexity Tracking section.

## Governance

- This constitution supersedes other practices for this project. Specs, plans, tasks, and reviews
  MUST check compliance with it.
- **Amendments**: proposed through `/speckit-constitution`. Each amendment MUST update the version,
  set the Last Amended date, and include a short note describing the change (Sync Impact Report).
- **Versioning**: semantic versioning.
  - MAJOR: removing or redefining a principle or gate.
  - MINOR: adding a principle or section, or materially expanding guidance.
  - PATCH: clarifications and wording fixes.
- **Compliance review**: every publish is preceded by the review gate above. Exceptions are
  allowed only when recorded in the relevant plan with a justification.

**Version**: 1.1.1 | **Ratified**: 2026-11-13 | **Last Amended**: 2026-11-14
