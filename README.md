# Chiacon AI Automation Studio

> **Pre-sales Automation Assessment Engine** — a production-quality prototype that identifies, structures, and communicates AI-driven automation opportunities for enterprise clients.

---

## Problem Statement

Enterprise sales teams face a consistent challenge: walking into client meetings and articulating *specific*, *relevant* automation opportunities without prior deep-dive analysis. Generic pitches fail. Executives want to hear their problem, framed with strategic consequence, and presented with a clear path forward.

**Chiacon AI Automation Studio** solves this by combining a structured AI analysis engine with intelligent, role-aware outreach generation — turning an industry and a business problem into a complete pre-sales narrative in under 30 seconds.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   React Frontend                    │
│  Automation Opportunity Engine │ Executive Outreach  │
│         (UseCaseGenerator)    │  (EmailGenerator)   │
└──────────────────┬──────────────────────────────────┘
                   │ REST (JSON)
                   ▼
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
│   /api/generate-automation  │  /api/generate-email   │
│        automation.py        │       email.py         │
└──────────────────┬──────────────────────────────────┘
                   │ Gemini SDK
                   ▼
┌─────────────────────────────────────────────────────┐
│              Google Gemini API                       │
│   gemini_service.py — centralised model instance,   │
│   retry logic with exponential backoff              │
└─────────────────────────────────────────────────────┘
```

**Tech Stack:**
- **Frontend:** React + Vite + Vanilla CSS (no Tailwind runtime dependency in production)
- **Backend:** FastAPI + Uvicorn + Pydantic
- **AI Layer:** Google Gemini API via `google-generativeai` SDK
- **Architecture:** Stateless, modular, deployable — no database required

---

## Feature Flow

```
Step 1 — Automation Opportunity Engine
  User selects industry (dropdown) + describes business problem + optional role
        ↓
  Gemini generates structured JSON:
    • problem_summary    — executive-level, role-framed strategic consequence
    • ai_opportunities   — outcome-led, technology-specific (3 bullets)
    • expected_business_impact — directionally quantified metrics (3 bullets)
        ↓
  Results displayed in clean, separated cards

Step 2 — Context Lock Activates
  automationIndustry stored in parent state
  User switches to Executive Outreach Generator tab
        ↓
  Industry field auto-fills + becomes disabled (locked)
  Context-Aware Mode badge displayed

Step 3 — Executive Outreach Generator
  User enters company name (auto-capitalised) + recipient role
  Backend detects context_summary present → uses context-aware prompt
        ↓
  Gemini generates:
    • Dynamic subject — specific to industry + pain point (not generic)
    • Email body      — role-toned, consulting-style, 120–180 words
    • CTA closing     — distinct per role (CFO / CTO / COO / QA / Sales / HR / other)

Step 4 — Email Actions
  Copy to clipboard  (✓ Copied! feedback)
  Download as .txt   (filename: chiacon-email-{company}.txt)
```

---

## Design Decisions

### Why is the industry field locked in the Email Generator?

**State integrity.** Once an automation opportunity is generated for a specific industry, all downstream artefacts must reference that same industry. Allowing the user to change industry in the email form would create a logical mismatch:

- Automation context: *FMCG invoice reconciliation*
- Email context: *Banking compliance* ← wrong

By storing `automationIndustry` at the parent `App` level and passing it down as a locked prop, we enforce a single source of truth. This mirrors how real SaaS products manage context chaining (e.g. Salesforce opportunity → quote → invoice all share the same account context).

Resetting is explicit: the user clicks **✕ Clear** to start over, which resets both `automationResult` and `automationIndustry` to `null`, returning the email generator to standalone mode.

### Why two mode prompts instead of one?

The standalone email and context-aware email require fundamentally different prompt architectures:

- **Standalone** must not imply prior knowledge of the client — it reads as a cold outreach
- **Context-aware** must reference the specific pain point naturally, without sounding like "we ran a report on you"

Using a single prompt with conditionals would degrade quality. Two clean prompt builders produce reliably better output.

### Why exponential backoff in the Gemini service?

The free-tier Gemini API enforces per-minute rate limits. Rather than surfacing quota errors to the user, `gemini_service.py` retries up to 3 times with exponential backoff. Only after exhausting retries does a clean, user-safe error surface (no raw API error strings exposed).

---

## Prompt Engineering Highlights

| Feature | Technique |
|---------|-----------|
| Executive problem framing | Instructed to frame around strategic consequence, not just restate the problem |
| Role adaptation | Explicit per-role rules (CFO → cost/ROI, CTO → architecture, COO → throughput etc.) |
| Dynamic subject lines | Rules + 3 concrete examples prevent generic subjects |
| Role-specific CTAs | 6 distinct per-role closing lines — Gemini must derive, not copy |
| Banned phrases | `we analysed / our assessment / we identified / we found that / we reviewed` |
| Softened impact claims | Hedged phrasing: `up to X`, `typically in the range of`, `potential to reduce` |

---

## Running Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
# Create .env with: GEMINI_API_KEY=your_key_here
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
# Create .env with: VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

---

## Deployment Targets

| Layer | Recommended Platform |
|-------|---------------------|
| Backend | Render / Railway (free tier) |
| Frontend | Vercel / Netlify |
| Environment | Set `GEMINI_API_KEY` and `VITE_API_BASE_URL` in platform env vars |

---

## Project Structure

```
Chiacon/
├── backend/
│   ├── main.py                   # FastAPI app, CORS, router registration
│   ├── routes/
│   │   ├── automation.py         # POST /api/generate-automation
│   │   └── email.py              # POST /api/generate-email
│   ├── services/
│   │   └── gemini_service.py     # Gemini client, retry logic, JSON helpers
│   ├── requirements.txt
│   └── .env                      # GEMINI_API_KEY
└── frontend/
    ├── src/
    │   ├── App.jsx               # Root: state management, tab routing, context lock
    │   ├── api.js                # Fetch wrappers with safe error handling
    │   ├── index.css             # Design system (glassmorphism, tokens, animations)
    │   └── components/
    │       ├── UseCaseGenerator.jsx   # Automation Opportunity Engine
    │       └── EmailGenerator.jsx    # Executive Outreach Generator
    ├── index.html
    └── .env                     # VITE_API_BASE_URL
```

---

*Built using React, FastAPI, and Gemini API with modular service architecture and context-aware workflow management.*
