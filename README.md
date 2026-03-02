# Chiacon AI Automation Studio

> **Pre-sales Automation Assessment Engine** — a production-quality prototype that identifies, structures, and communicates AI-driven automation opportunities for enterprise clients.

**Live Demo:** [chiacon-lake.vercel.app](https://chiacon-lake.vercel.app) · **API:** [chiacon.onrender.com](https://chiacon.onrender.com)

---

## Problem Statement

Enterprise sales teams face a consistent challenge: walking into client meetings and articulating *specific*, *relevant* automation opportunities without prior deep-dive analysis. Generic pitches fail. Executives want to hear their problem, framed with strategic consequence, and presented with a clear path forward.

**Chiacon AI Automation Studio** solves this by combining a structured AI analysis engine with intelligent, role-aware outreach generation — turning an industry and a business problem into a complete pre-sales narrative in under 30 seconds.

---

## How to Use

### Step 1 — Identify Automation Opportunities

1. Open the app → **Automation Opportunity Engine** tab is active by default
2. Select an **Industry** from the dropdown (or choose "Other" to type custom)
3. Describe the **Business Problem** (e.g. *"Manual invoice reconciliation causing month-end delays"*)
4. Optionally enter your **Role** (e.g. CFO, CTO) — this adapts the entire output to your perspective
5. Click **Identify AI Opportunities**
6. Results appear in 3 separated cards: Problem Summary, AI Opportunities, Business Impact

### Step 2 — Generate Executive Outreach Email

7. After results appear, click **Generate Executive Outreach Email →** (this switches tabs and locks context)
8. Enter the **Company Name** (auto-capitalised as you type)
9. The **Industry** field is pre-filled and locked — this ensures the email matches the analysis
10. Enter the **Recipient Role** (e.g. CFO, VP Operations)
11. Click **Generate Context-Aware Email**
12. The email appears with a dynamic, industry-specific subject line and role-matched CTA

### Step 3 — Export

13. Click **Copy** to copy the full email (subject + body) to clipboard
14. Click **Download** to save as a `.txt` file

### Standalone Mode

You can also use the **Executive Outreach Generator** tab independently — without running the analysis first. In standalone mode, the industry field is editable and no context is passed.

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
                   │ google-genai SDK
                   ▼
┌─────────────────────────────────────────────────────┐
│              Google Gemini API                       │
│   gemini_service.py — genai.Client, retry logic,    │
│   token usage logging, safe JSON parsing            │
└─────────────────────────────────────────────────────┘
```

**Tech Stack:**
- **Frontend:** React + Vite + Vanilla CSS
- **Backend:** FastAPI + Uvicorn + Pydantic
- **AI Layer:** Google Gemini API via `google-genai` SDK (GA)
- **Model:** `gemini-2.5-flash` with thinking disabled
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
  Results displayed in stagger-animated, separated cards

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
    • Email body      — role-toned, consulting-style, under 160 words
    • CTA closing     — distinct per role (CFO / CTO / COO / QA / Sales / HR / other)

Step 4 — Email Actions
  Copy to clipboard  (✓ Copied! feedback with checkmark animation)
  Download as .txt   (filename: chiacon-email-{company}.txt)
```

---

## Design Decisions

### Why is the industry field locked in the Email Generator?

**State integrity.** Once an automation opportunity is generated for a specific industry, all downstream artefacts must reference that same industry. Allowing the user to change industry in the email form would create a logical mismatch. Resetting is explicit: the user clicks **✕ Clear** to start over.

### Why two mode prompts instead of one?

The standalone email and context-aware email require fundamentally different prompt architectures. Standalone must not imply prior knowledge. Context-aware must reference the specific pain point naturally. Two clean prompt builders produce reliably better output.

### Why is thinking disabled on Gemini 2.5 Flash?

`gemini-2.5-flash` enables internal reasoning ("thinking") by default. For structured JSON generation, this consumes ~1000 tokens internally without improving output quality — and can cause JSON truncation when the output budget is consumed by thinking. Setting `thinking_budget=0` ensures all tokens go to actual output.

### Why exponential backoff?

The free-tier Gemini API enforces per-minute rate limits. `gemini_service.py` retries up to 3 times with exponential backoff (10s → 20s → 40s). Only after exhausting retries does a clean, user-safe error surface.

---

## AI & Model Configuration

| Setting | Value | Rationale |
|---------|-------|-----------|
| Model | `gemini-2.5-flash` | Latest GA model, fast, cost-effective |
| SDK | `google-genai` >= 1.0.0 | New GA SDK (replaces deprecated `google-generativeai`) |
| Thinking | Disabled (`thinking_budget=0`) | Prevents token waste and JSON truncation |
| Temperature | 0.4 | Lower = more consistent, reliable JSON formatting |
| Max output tokens | 2048 | Sufficient for structured JSON with arrays |
| Retry logic | 3 attempts, exponential backoff | Handles 429 rate limits gracefully |
| Token logging | Every call | Logs prompt/output/total tokens + latency to terminal |
| JSON parsing | Safe fallback with regex | Extracts `{...}` block if direct parse fails |

**Terminal output on every call:**
```
[Gemini] Model: gemini-2.5-flash | Prompt: 649 tk | Output: 342 tk | Total: 991 tk | Latency: 4.2s
```

---

## Prompt Engineering Highlights

| Feature | Technique |
|---------|-----------|
| Executive problem framing | Instructed to frame around strategic consequence, not just restate the problem |
| Role adaptation | Explicit per-role rules (CFO → cost/ROI, CTO → architecture, COO → throughput etc.) |
| Dynamic subject lines | Rules + 3 concrete examples prevent generic subjects |
| Role-specific CTAs | 7 distinct per-role closing lines — Gemini must derive, not copy |
| Banned phrases | `we analysed / our assessment / we identified / we found that / we reviewed` |
| Company name rules | Used only for greeting/personalisation/subject — never for observational claims |
| Softened impact claims | Hedged phrasing: `up to X`, `typically in the range of`, `potential to reduce` |
| Anti-filler | Banned words: `streamline / optimise / leverage / synergies / cutting-edge` |

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

**Get your API key:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## Deployment

| Layer | Platform | URL |
|-------|----------|-----|
| Backend | Render (free) | `https://chiacon.onrender.com` |
| Frontend | Vercel (free) | `https://chiacon-lake.vercel.app` |

**Environment variables to set:**
- **Render:** `GEMINI_API_KEY`
- **Vercel:** `VITE_API_BASE_URL` = your Render URL

> Note: Render free tier sleeps after 15 min idle. First request after sleep takes ~30 seconds.

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
│   │   └── gemini_service.py     # Gemini client, token logging, retry, JSON parsing
│   ├── requirements.txt
│   ├── .python-version           # Pins Python 3.11.9 for Render
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

*Built with React, FastAPI, and Google Gemini 2.5 Flash — modular service architecture with context-aware workflow management, token-level observability, and production-grade error handling.*
