# Feature Specification: Baku Trip Planner (Hotel, Activities, Confirmation & PDF)

**Feature Branch**: `001-baku-trip-planner`

**Created**: 2026-11-13

**Status**: Draft

**Input**: User description: "I want to Create a travel agent in Copilot Studio for helping users traveling to Baku. Agent should first offer some hotel options to select. Every hotel must have a price per person and per day, when you add the hotel, it must calculate the total price of the stay and show it in the plan. After selecting the hotel, it should offer some activities to choose. For activities, we want to show price, description, name, photos (you can use stock photos). When we add hotel or activity to the plan, you must recalculate the grand total. It should ask if we want to add more activities or continue to confirmation step. In confirmation step it should ask for holder data, and finally, confirm the plan. Finally, it should show all the plan information and an option to export it in PDF. Create skills necesaries to architect a good agent."

## Clarifications

### Session 2026-11-13

- Q: What does confirming the trip plan mean? → A: Confirmed plan/quote only, with a reference
  and PDF; no real reservation or payment.
- Q: Which currency should prices and totals use? → A: Azerbaijani manat (AZN).
- Q: Which holder details are collected at confirmation? → A: Full name, email address, and
  phone number.

## User Scenarios & Testing *(mandatory)*

All amounts in this spec are in AZN.

The traveler goes through one guided conversation with the agent:

**Trip details → Hotel → Activities (repeat) → Holder details → Confirmation → Final plan + PDF**

Throughout, the agent keeps a single **trip plan** and shows it, with an up-to-date
**grand total**, every time something is added, removed, or changed.

### User Story 1 - Choose a hotel and see the stay total (Priority: P1)

A traveler tells the agent they are going to Baku, gives their check-in date, check-out date,
and number of travelers, and is offered a selection of hotels. Each option shows the hotel's
name, neighborhood, short description, photo, and price per person per night. The traveler
picks one; the agent adds it to the plan, calculates the total cost of the stay, and shows the
plan with the stay total and the grand total.

**Why this priority**: The hotel is the first and largest part of every plan; without it no
other step has a basis. On its own, this already gives the traveler a priced stay.

**Independent Test**: Start a conversation, provide dates and party size, select a hotel, and
check that the plan shows the hotel, number of nights, number of travelers, a correctly
calculated stay total, and a grand total equal to the stay total.

**Acceptance Scenarios**:

1. **Given** a new conversation, **When** the traveler says they want to plan a trip to Baku,
   **Then** the agent asks for check-in date, check-out date, and number of travelers before
   showing any hotels.
2. **Given** the trip details are known, **When** the agent offers hotels, **Then** it shows
   between 3 and 5 options from the hotel catalog, each with name, neighborhood, short
   description, at least one photo, and price per person per night.
3. **Given** 2 travelers staying 4 nights, **When** the traveler selects a hotel priced at 60 per
   person per night, **Then** the plan shows a stay total of 480 (60 × 2 × 4) and a grand total
   of 480.
4. **Given** a hotel is already in the plan, **When** the traveler picks a different hotel,
   **Then** the new hotel replaces the old one (a plan holds one hotel), and the stay total and
   grand total are recalculated.
5. **Given** the hotel has been added, **When** the plan is shown, **Then** the agent moves on by
   offering activities.

**Example conversation**:

> **Traveler**: Hi, I'm planning a trip to Baku.
> **Agent**: Great! When do you check in and check out, and how many people are traveling?
> **Traveler**: 10 to 14 March 2027, two of us.
> **Agent**: *(shows 3–5 hotel cards with name, neighborhood, photo, description,
> price per person per night)* Which one would you like?
> **Traveler**: The second one.
> **Agent**: *(adds the hotel and shows the plan)* Hotel: 4 nights × 2 travelers × 60 = 480.
> Grand total: 480. Now, would you like to see some activities in Baku?

---

### User Story 2 - Add activities and keep the grand total up to date (Priority: P2)

After choosing a hotel, the traveler is offered activities in and around Baku. Each activity
shows its name, description, price per person, and at least one photo. The traveler can add
one or more activities; after each addition or removal the agent recalculates the grand total
and shows the updated plan. After each change the agent asks whether to add more activities or
continue to the confirmation step.

**Why this priority**: Activities turn a hotel booking into a trip plan and are the main way the
agent adds value beyond a hotel list, but the plan is still useful without them.

**Independent Test**: With a hotel already in the plan, add two activities and remove one,
checking after each step that the plan lists the right activities and the grand total equals
the stay total plus the activity totals.

**Acceptance Scenarios**:

1. **Given** a hotel is in the plan, **When** the agent offers activities, **Then** it shows
   between 3 and 6 options from the activity catalog, each with name, description, price per
   person, and at least one photo.
2. **Given** a plan with a stay total of 480 and 2 travelers, **When** the traveler adds an
   activity priced at 25 per person, **Then** the plan shows that activity at 50 (25 × 2) and
   the grand total becomes 530.
3. **Given** an activity has been added, **When** the plan is shown, **Then** the agent asks
   whether the traveler wants to add more activities or continue to confirmation.
4. **Given** the plan contains an activity, **When** the traveler asks to remove it, **Then** it
   is removed and the grand total is recalculated.
5. **Given** the plan contains an activity, **When** the traveler tries to add the same activity
   again, **Then** the agent tells them it is already in the plan and does not add it twice.
6. **Given** a hotel is in the plan, **When** the traveler chooses to continue without adding any
   activities, **Then** the agent goes to the confirmation step.

**Example conversation**:

> **Agent**: *(shows activity cards: name, photo, description, price per person)*
> **Traveler**: Add the Old City walking tour.
> **Agent**: *(shows updated plan)* Old City walking tour: 2 × 25 = 50. Grand total: 530.
> Would you like to add more activities, or continue to confirmation?
> **Traveler**: Continue.

---

### User Story 3 - Provide holder details and confirm the plan (Priority: P3)

When the traveler chooses to continue, the agent asks for the plan holder's details, shows a
full summary of the plan with the grand total, and asks the traveler to explicitly confirm it.
Only after the traveler confirms does the plan become confirmed and receive a confirmation
reference.

**Why this priority**: Confirmation turns a draft into a final plan for a named person, which is
needed before the plan can be shared or exported.

**Independent Test**: With a plan containing a hotel and an activity, continue to confirmation,
enter holder details, check the summary, confirm, and verify the plan is marked confirmed with
a confirmation reference. Repeat but decline, and verify the plan stays unconfirmed.

**Acceptance Scenarios**:

1. **Given** a plan with a hotel, **When** the traveler continues to confirmation, **Then** the
   agent asks for the holder details listed in FR-016.
2. **Given** the traveler enters an email address in an invalid format, **When** the agent checks
   it, **Then** it explains the problem and asks again.
3. **Given** valid holder details, **When** the agent shows the summary, **Then** the summary
   includes the holder details, trip dates, number of travelers, hotel, each activity, each
   line total, and the grand total, followed by an explicit request to confirm.
4. **Given** the summary has been shown, **When** the traveler explicitly confirms, **Then** the
   plan is marked confirmed and the agent shows a confirmation reference.
5. **Given** the summary has been shown, **When** the traveler does not confirm (declines or asks
   to change something), **Then** the plan is not confirmed and the traveler can go back to
   change the hotel, activities, or holder details.
6. **Given** any point in the conversation, **When** the traveler offers a passport number or
   payment card details, **Then** the agent does not repeat or keep them and explains they are
   not needed.

**Example conversation**:

> **Agent**: To confirm your plan I need the holder's full name, email address, and phone number.
> **Traveler**: Ana Smith, ana@example.com, +34 600 000 000.
> **Agent**: *(shows full plan summary)* Grand total: 530. Shall I confirm this plan?
> **Traveler**: Yes, confirm.
> **Agent**: Your plan is confirmed. Reference: BAK-20270310-XXXXXX.

---

### User Story 4 - View the final plan and export it as PDF (Priority: P4)

After confirmation, the agent shows all the plan information in one place and offers to export
it as a PDF. The traveler can download the PDF, which contains the same information as the
on-screen plan.

**Why this priority**: The PDF gives the traveler a document to keep and share; it depends on a
confirmed plan, so it comes last.

**Independent Test**: Confirm a plan, ask for the PDF, open it, and check every field against the
on-screen final plan.

**Acceptance Scenarios**:

1. **Given** a confirmed plan, **When** confirmation completes, **Then** the agent shows the final
   plan (see FR-019) and offers to export it as a PDF.
2. **Given** the final plan is shown, **When** the traveler asks for the PDF, **Then** the agent
   provides a downloadable PDF file within the conversation.
3. **Given** the PDF has been generated, **When** the traveler opens it, **Then** it shows the
   same holder details, dates, travelers, hotel, activities (with photos), line totals, grand
   total, currency, and confirmation reference as the on-screen plan.
4. **Given** a plan that is not yet confirmed, **When** the traveler asks for a PDF, **Then** the
   agent explains the plan must be confirmed first and offers to go to confirmation.

---

### Edge Cases

- **Invalid dates**: check-out on or before check-in, or check-in in the past → the agent
  explains and asks again.
- **Stay length**: stays longer than 30 nights → the agent says this is not supported and asks
  for shorter dates.
- **Party size**: fewer than 1 or more than 10 travelers → the agent explains the limit (1–10)
  and asks again.
- **Trip details change**: the traveler changes dates or number of travelers after selecting a
  hotel or activities → all line totals and the grand total are recalculated and the updated
  plan is shown.
- **Hotel not in catalog**: the traveler asks for a hotel or activity that is not in the catalog
  → the agent says it is not available and offers the catalog options; it never invents an
  option or price.
- **Activities before hotel**: the traveler asks to add activities before choosing a hotel → the
  agent explains a hotel is chosen first and offers hotels.
- **Change after confirmation**: the traveler wants to change a confirmed plan → the agent
  explains a confirmed plan cannot be edited and offers to start a new plan.
- **Holder details refused**: the traveler does not want to give holder details → the plan
  cannot be confirmed; the agent can still show the draft plan.
- **Ambiguous selection**: "the cheap one" matches several options → the agent asks which one.
- **Off-topic travel questions** (visas, weather, safety) → the agent answers only from grounded
  sources or points to the official source, per the constitution, then returns to the plan.
- **Conversation abandoned**: the draft plan is not kept once the conversation ends.

## Requirements *(mandatory)*

### Functional Requirements

**Trip details**

- **FR-001**: The agent MUST collect check-in date, check-out date, and number of travelers
  before offering hotels.
- **FR-002**: The agent MUST reject check-out dates on or before check-in, check-in dates in the
  past, stays over 30 nights, and party sizes outside 1–10, and ask again.
- **FR-003**: The agent MUST calculate the number of nights as the number of days between
  check-in and check-out.

**Hotels**

- **FR-004**: The agent MUST offer between 3 and 5 hotels, taken only from the hotel catalog.
- **FR-005**: Each hotel option MUST show name, neighborhood, short description, at least one
  photo, and price per person per night.
- **FR-006**: When a hotel is added, the agent MUST calculate the stay total as
  *price per person per night × number of travelers × number of nights*.
- **FR-007**: A plan MUST contain at most one hotel; selecting another hotel replaces it.

**Activities**

- **FR-008**: After a hotel is in the plan, the agent MUST offer between 3 and 6 activities,
  taken only from the activity catalog.
- **FR-009**: Each activity option MUST show name, description, price per person, and at least
  one photo.
- **FR-010**: When an activity is added, the agent MUST calculate its line total as
  *price per person × number of travelers*.
- **FR-011**: The traveler MUST be able to add multiple different activities, remove an activity,
  and MUST NOT be able to add the same activity twice.
- **FR-012**: After each activity change, the agent MUST ask whether to add more activities or
  continue to confirmation.

**Plan and totals**

- **FR-013**: The grand total MUST equal the stay total plus the sum of all activity line totals.
- **FR-014**: The agent MUST recalculate and show the plan, including every line total and the
  grand total, after every change: adding, replacing, or removing an item, or changing dates or
  number of travelers.
- **FR-015**: All amounts MUST be shown in Azerbaijani manat (AZN), with exactly two decimal
  places, and totals MUST be exact (no approximations).

**Confirmation**

- **FR-016**: In the confirmation step the agent MUST collect the plan holder's full name,
  email address, and phone number (all three required).
- **FR-017**: The agent MUST NOT ask for, repeat, or keep passport/ID numbers, payment card or
  bank details, or passwords, and MUST validate the format of each holder field it collects.
- **FR-018**: The agent MUST show a full summary and require an explicit confirmation from the
  traveler before marking the plan confirmed. Confirmation locks the plan as a confirmed trip
  plan (quote) with a reference; it MUST NOT make a reservation with any hotel or provider,
  take a payment, or send the plan to anyone.

**Final plan and PDF**

- **FR-019**: After confirmation the agent MUST show the final plan: confirmation reference,
  confirmation date, holder details, trip dates, number of nights and travelers, hotel (name,
  neighborhood, price per person per night, stay total), each activity (name, price per person,
  line total), the grand total, and the currency.
- **FR-020**: The agent MUST offer to export the final plan as a PDF and provide it as a
  downloadable file in the conversation.
- **FR-021**: The PDF MUST contain all the information in FR-019, plus the hotel and activity
  photos and a note that prices come from the agent's catalog at the time of confirmation.
- **FR-022**: The agent MUST NOT export a PDF for a plan that is not confirmed.

**Catalog and grounding**

- **FR-023**: Hotel and activity options, descriptions, photos, and prices MUST come only from the
  catalogs; the agent MUST NOT invent options or prices.
- **FR-024**: Photos MAY be stock photos; each catalog item MUST have at least one.

### Agent Capabilities

The agent is organized around these capabilities. How each maps to Copilot Studio skills,
tools, and knowledge is decided in `/speckit-plan`.

- **Trip details**: collect and validate dates and party size.
- **Hotel recommendations**: present catalog hotels and handle selection.
- **Activity recommendations**: present catalog activities and handle add/remove.
- **Plan and pricing**: keep the plan and calculate all totals exactly.
- **Holder details and confirmation**: collect holder data safely, summarize, and confirm.
- **Plan document**: produce the final plan and its PDF export.

### Key Entities

- **Trip Details**: check-in date, check-out date, number of nights (derived), number of
  travelers.
- **Hotel**: catalog item with name, neighborhood, short description, one or more photos, price
  per person per night.
- **Activity**: catalog item with name, description, one or more photos, price per person.
- **Trip Plan**: the traveler's plan for one conversation. Holds trip details, at most one hotel,
  zero or more activities, line totals, grand total, currency, status (draft or confirmed), and
  a confirmation reference once confirmed.
- **Plan Line**: one item in the plan (hotel or activity) with unit price, quantity
  (travelers × nights for the hotel, travelers for an activity), and line total.
- **Plan Holder**: the person responsible for the plan; fields defined by FR-016.
- **Plan Document**: the PDF export of a confirmed plan.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A traveler can go from the first message to a confirmed plan with a hotel and two
  activities in under 10 minutes.
- **SC-002**: In 100% of test conversations, every line total and grand total matches a manual
  calculation exactly.
- **SC-003**: The updated plan and grand total are shown after 100% of plan changes.
- **SC-004**: 100% of fields in the PDF match the on-screen final plan.
- **SC-005**: In test conversations, the agent asks for or repeats passport, ID, or payment data
  0 times, and offers an option or price not in the catalog 0 times.
- **SC-006**: 90% of first-time test users complete the full flow (hotel → confirmation → PDF)
  without help.
- **SC-007**: No plan is ever marked confirmed without an explicit confirmation from the traveler.

## Assumptions

- "Price per person and per day" for hotels means per person per **night**; the number of nights
  is the number of days between check-in and check-out.
- Every traveler takes part in every selected activity, so an activity's quantity is the number
  of travelers; per-activity participant counts are out of scope for v1.
- Activities are not scheduled to specific dates or times in v1.
- Hotel and activity data come from a curated catalog maintained for this agent (initially
  sample data with stock photos), not from live supplier searches.
- Prices include all taxes and fees; no discounts, child rates, or room-type pricing in v1.
- The draft plan lasts only for the conversation; confirmed plans are kept only as the
  confirmation reference and PDF given to the traveler.
- English is the conversation language (per the constitution).
- v1 is checked in the Copilot Studio test chat. Publishing to Teams or Microsoft 365 Copilot is
  out of scope for this feature, because image and file-download support differs by channel.
- Flights, transfers, weather, payment, and real reservations are out of scope for this
  feature; a confirmed plan is a quote the traveler can keep.
- Collecting holder contact details at confirmation is allowed by Constitution v1.1.0,
  Principle III.
