"""
Route: AI Email Generator
POST /api/generate-email

Supports two modes:
  - Standalone:     context_summary is null → generic outreach email
  - Context-Aware:  context_summary provided → references identified opportunities
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from services.gemini_service import generate_json_response

router = APIRouter()


# ── Request / Response Models ──────────────────────────────────────────

class EmailRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=300)
    industry: str = Field(..., min_length=1, max_length=200)
    role: str = Field(..., min_length=1, max_length=200)
    context_summary: Optional[str] = None


class EmailResponse(BaseModel):
    email_subject: str
    email_body: str


# ── Prompt Builders ───────────────────────────────────────────────────

def _build_standalone_prompt(req: EmailRequest) -> tuple[str, str]:
    system_prompt = (
        "You are a senior business development consultant at Chiacon, "
        "an IT consulting & automation company specializing in RPA, "
        "Data & Analytics, Power Platform, QA, and enterprise automation.\n\n"

        "Write a professional executive outreach email.\n\n"

        "ROLE ADAPTATION (apply to every element of the email):\n"
        "- CFO / Finance: cost reduction, ROI, financial accuracy, risk mitigation.\n"
        "- CTO / IT Director: scalability, modernisation, technical architecture.\n"
        "- COO / Operations: process efficiency, throughput, operational continuity.\n"
        "- Head of QA / Quality: defect reduction, compliance, audit readiness.\n"
        "- VP Sales / Commercial: revenue growth, speed to market, customer experience.\n"
        "- Any other role: infer what matters most to that function and lead with it.\n\n"

        "EMAIL SUBJECT RULES:\n"
        "- Must be specific — reference the industry AND a specific business outcome.\n"
        "- Do NOT write generic subjects like 'AI Partnership' or 'Automation Opportunity'.\n"
        "- Examples of good subjects:\n"
        "  'Reducing Manual Overhead in FMCG Finance Operations'\n"
        "  'Accelerating Claims Processing in Insurance Through Intelligent Automation'\n"
        "  'Improving QA Throughput in Pharmaceutical Manufacturing'\n\n"

        "EMAIL RULES:\n"
        "- Be personalized to the recipient's company, industry, and role\n"
        "- Be consulting-style and professional in tone\n"
        "- Under 160 words total — every sentence must introduce new value, not repeat prior points\n"
        "- Avoid repetitive benefit statements: do not restate the same outcome in different words\n"
        "- Maintain the role's specific tone throughout: CFO emails read like cost-control conversations, "
        "CTO emails like architecture decisions, COO emails like operational trade-offs — "
        "infer the right register from the role and never slip out of it\n"
        "- Focus on AI and automation value specific to their industry; "
        "mention at least one concrete automation approach (e.g. 'intelligent document processing', "
        "'automated exception handling', 'RPA-driven reconciliation') relevant to the sector\n"
        "- Do NOT reference any prior analysis, assessment, or research about the recipient\n"
        "- Do NOT use phrases like: 'we analysed', 'our assessment', 'we identified', 'we noticed', "
        "'based on our research', 'we found that', 'we reviewed'\n"
        "COMPANY NAME RULES:\n"
        "- Use the company name ONLY for: the greeting, light personalisation, and the subject line.\n"
        "- Do NOT make claims about the company's internal state, systems, or operations. "
        "Never say 'We observed at [Company]...', 'Based on [Company]'s operations...', "
        "'We analysed [Company]...', or anything that implies insider knowledge.\n"
        "- Instead, use neutral sector-level phrasing: 'Organisations in the [industry] sector...', "
        "'Many enterprises of this scale face...', 'In large-scale [industry] operations...'. "
        "This keeps the email credible and avoids unverifiable claims.\n"
        "- No exaggerated claims. No superlatives. No emojis. No markdown formatting.\n"
        "- End with a role-specific CTA closing line (one sentence only). Use these as a guide:\n"
        "  CFO / Finance: 'I would welcome 20 minutes to walk through a cost-benefit framework tailored to your finance operations.'\n"
        "  CTO / IT Director: 'Happy to arrange a short technical session showing how this integrates with your existing architecture.'\n"
        "  COO / Operations: 'I would welcome a brief conversation to map this to your operational priorities.'\n"
        "  Head of QA / Quality: 'Happy to share how similar teams have improved audit readiness and reduced manual QA overhead.'\n"
        "  VP Sales / Commercial: 'I would be glad to explore how this could accelerate your commercial throughput in a short call.'\n"
        "  HR / Talent: 'Happy to show how automation has helped similar HR teams reduce administrative load significantly.'\n"
        "  Any other role: derive a natural, specific CTA based on what matters most to that function — do not reuse the examples above verbatim.\n\n"

        "Respond with ONLY valid JSON in this exact format:\n"
        "{\n"
        '  "email_subject": "Specific outcome-oriented subject line",\n'
        '  "email_body": "Full email body including role-specific CTA closing line"\n'
        "}"
    )
    user_prompt = (
        f"Generate an outreach email for:\n"
        f"Company: {req.company_name}\n"
        f"Industry: {req.industry}\n"
        f"Recipient Role: {req.role}\n"
        f"Tailor every element — subject, body, and CTA — to what matters most to a {req.role}."
    )
    return system_prompt, user_prompt


def _build_context_prompt(req: EmailRequest) -> tuple[str, str]:
    system_prompt = (
        "You are a senior business development consultant at Chiacon, "
        "an IT consulting & automation company specializing in RPA, "
        "Data & Analytics, Power Platform, QA, and enterprise automation.\n\n"

        "Write a professional executive outreach email that references "
        "a specific automation opportunity already identified for this client.\n\n"

        "ROLE ADAPTATION (apply to every element of the email):\n"
        "- CFO / Finance: cost reduction, ROI, financial accuracy, risk mitigation.\n"
        "- CTO / IT Director: scalability, modernisation, technical architecture.\n"
        "- COO / Operations: process efficiency, throughput, operational continuity.\n"
        "- Head of QA / Quality: defect reduction, compliance, audit readiness.\n"
        "- VP Sales / Commercial: revenue growth, speed to market, customer experience.\n"
        "- Any other role: infer what matters most to that function and lead with it.\n\n"

        "EMAIL SUBJECT RULES:\n"
        "- Must be specific — reference the industry AND a concrete business outcome from the context.\n"
        "- Do NOT write generic subjects like 'AI Partnership' or 'Automation Discussion'.\n"
        "- Examples of good subjects:\n"
        "  'Eliminating Invoice Reconciliation Delays in FMCG Finance'\n"
        "  'Automating Claims Intake to Reduce Processing Backlog in Insurance'\n"
        "  'Accelerating Batch QA in Pharmaceutical Production Lines'\n\n"

        "EMAIL RULES:\n"
        "- Be personalized to the recipient's company, industry, and role\n"
        "- Naturally reference the identified business pain point\n"
        "- Reference at least one specific automation mechanism from the context "
        "(e.g. 'AI-powered OCR', 'RPA-driven reconciliation', 'intelligent validation engine') — "
        "name it naturally, not technically. Do not vaguely say 'automation solution'.\n"
        "- Maintain executive tone throughout: confident, concise, outcome-focused. "
        "Every sentence must earn its place — no filler.\n"
        "- Avoid generic consulting filler: never use 'streamline', 'optimise', 'leverage', "
        "'synergies', 'end-to-end', 'best-in-class', or 'cutting-edge'.\n"
        "- Include a strategic transformation angle relevant to the recipient's role\n"
        "- Be consulting-style and professional\n"
        "- Under 160 words total — every sentence must introduce new value, not repeat prior points\n"
        "- Avoid repetitive benefit statements: do not restate the same outcome in different words\n"
        "- Maintain the role's specific tone throughout: CFO emails read like cost-control conversations, "
        "CTO emails like architecture decisions, COO emails like operational trade-offs — "
        "infer the right register from the role and never slip out of it\n"
        "- Do NOT reference any prior analysis, assessment, or research about the recipient\n"
        "- Do NOT use phrases like: 'we analysed', 'our assessment', 'we identified', 'we noticed', "
        "'based on our research', 'we found that', 'we reviewed'\n"
        "COMPANY NAME RULES:\n"
        "- Use the company name ONLY for: the greeting, light personalisation, and the subject line.\n"
        "- Do NOT make claims about the company's internal state, systems, or operations. "
        "Never say 'We observed at [Company]...', 'Based on [Company]'s operations...', "
        "'We analysed [Company]...', or anything that implies insider knowledge.\n"
        "- Instead, use neutral sector-level phrasing: 'Organisations in the [industry] sector...', "
        "'Many enterprises of this scale face...', 'In large-scale [industry] operations...'. "
        "This keeps the email credible and avoids unverifiable claims.\n"
        "- Do NOT exaggerate claims or use superlatives\n"
        "- No emojis. No markdown formatting.\n"
        "- End with a role-specific CTA closing line (one sentence only). Use these as a guide:\n"
        "  CFO / Finance: 'I would welcome 20 minutes to walk through a cost-benefit framework tailored to your finance operations.'\n"
        "  CTO / IT Director: 'Happy to arrange a short technical session showing how this integrates with your existing architecture.'\n"
        "  COO / Operations: 'I would welcome a brief conversation to map this directly to your operational priorities.'\n"
        "  Head of QA / Quality: 'Happy to share how similar teams have meaningfully improved audit readiness and reduced manual QA overhead.'\n"
        "  VP Sales / Commercial: 'I would be glad to explore how this could accelerate your commercial throughput in a short call.'\n"
        "  HR / Talent: 'Happy to show how automation has helped similar HR teams reduce administrative load and refocus on strategic work.'\n"
        "  Any other role: derive a natural, specific CTA based on what matters most to that function — do not reuse the examples above verbatim.\n\n"

        "Respond with ONLY valid JSON in this exact format:\n"
        "{\n"
        '  "email_subject": "Specific outcome-oriented subject line referencing the pain point",\n'
        '  "email_body": "Full email body including role-specific CTA closing line"\n'
        "}"
    )
    user_prompt = (
        f"Generate an outreach email for:\n"
        f"Company: {req.company_name}\n"
        f"Industry: {req.industry}\n"
        f"Recipient Role: {req.role}\n"
        f"Tailor every element — subject, body, and CTA — to what matters most to a {req.role}.\n\n"
        f"Automation Opportunity Context:\n{req.context_summary}"
    )
    return system_prompt, user_prompt


# ── Endpoint ───────────────────────────────────────────────────────────

@router.post("/api/generate-email", response_model=EmailResponse)
async def generate_email(req: EmailRequest):
    if req.context_summary:
        system_prompt, user_prompt = _build_context_prompt(req)
    else:
        system_prompt, user_prompt = _build_standalone_prompt(req)

    try:
        data = generate_json_response(system_prompt, user_prompt)
        return EmailResponse(**data)
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower() or "rate" in err.lower():
            raise HTTPException(
                status_code=503,
                detail="The AI service is temporarily unavailable due to rate limits. Please try again in a moment."
            )
        if isinstance(e, (ValueError, KeyError)) or "json" in err.lower() or "parse" in err.lower():
            raise HTTPException(
                status_code=422,
                detail="Unable to generate a structured response. Please try again."
            )
        raise HTTPException(
            status_code=500,
            detail="Unable to generate response. Please try again."
        )
