"""
Route: AI Use Case Generator
POST /api/generate-automation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from services.gemini_service import generate_json_response

router = APIRouter()


# ── Request / Response Models ──────────────────────────────────────────

class AutomationRequest(BaseModel):
    industry: str = Field(..., min_length=1, max_length=200)
    problem: str = Field(..., min_length=5, max_length=1000)
    role: Optional[str] = Field(None, max_length=200)


class AutomationResponse(BaseModel):
    problem_summary: str
    ai_opportunities: List[str]
    expected_business_impact: List[str]


# ── Endpoint ───────────────────────────────────────────────────────────

@router.post("/api/generate-automation", response_model=AutomationResponse)
async def generate_automation(req: AutomationRequest):
    role_context = (
        f"Requester Role: {req.role}\n"
        f"Tailor the problem framing, opportunities, and business impact specifically to the concerns, "
        f"priorities, and language of a {req.role}. "
        f"What matters most to them — their KPIs, their accountability, their day-to-day pain."
    ) if req.role else ""

    system_prompt = (
        "You are a senior AI & Automation consultant at Chiacon, "
        "an IT consulting company specializing in RPA, Data & Analytics, "
        "Power Platform, QA, and enterprise automation bots.\n\n"

        "TASK: Analyze the business problem and produce a senior-level consulting response.\n\n"

        "ROLE ADAPTATION (critical):\n"
        "- If a requester role is provided, adapt the ENTIRE response to that person's perspective.\n"
        "- Mirror their language, their KPIs, their accountability. "
        "A CFO cares about cost and financial risk. A COO cares about throughput and process efficiency. "
        "A Head of QA cares about defect rates and compliance. An IT Director cares about system reliability and integration. "
        "Apply this logic to whatever role is given — infer what matters most to that role.\n"
        "- If no role is provided, write at a general senior leadership level.\n\n"

        "RULES FOR problem_summary:\n"
        "- Write 2-3 sentences at an executive level, framed for the requester's role.\n"
        "- Frame it around strategic consequence: what is the business risk, inefficiency, "
        "or missed opportunity caused by this problem?\n"
        "- Do NOT just restate the problem. Add context about what it impacts "
        "(e.g. financial accuracy, decision-making speed, operational resilience).\n"
        "- Avoid generic phrases like 'this is a challenge'. Be sharp and specific.\n\n"

        "RULES FOR ai_opportunities:\n"
        "- Each opportunity must combine an outcome with a method. "
        "Format: [what it achieves] + [how, using what technology].\n"
        "- Lead with the business outcome, follow with the automation/AI approach.\n"
        "- Be specific to the industry and problem. No generic AI buzzwords.\n"
        "- Example style: 'Eliminate invoice reconciliation delays by deploying an "
        "AI-powered OCR and validation engine that automates matching and flags exceptions in real time.'\n\n"

        "RULES FOR expected_business_impact:\n"
        "- Each impact must be directionally quantified using softened, credible language.\n"
        "- Use hedged phrasing: 'up to X', 'typically in the range of', 'potential to reduce', "
        "'meaningfully lower', 'significantly faster'. Avoid hard, precise percentages.\n"
        "- Tie each impact to a business metric: cost, speed, accuracy, risk, or revenue.\n"
        "- Do NOT make claims that sound exaggerated or unverifiable.\n\n"

        "You MUST respond with ONLY valid JSON in this exact format, "
        "with no extra text, no markdown, no explanation:\n"
        "{\n"
        '  "problem_summary": "Executive-level 2-3 sentence strategic framing of the problem",\n'
        '  "ai_opportunities": ["outcome-led opportunity 1", "outcome-led opportunity 2", "outcome-led opportunity 3"],\n'
        '  "expected_business_impact": ["quantified impact 1", "quantified impact 2", "quantified impact 3"]\n'
        "}"
    )

    user_prompt = (
        f"Industry: {req.industry}\n"
        f"Business Problem: {req.problem}\n"
        f"{role_context}"
    )

    try:
        data = generate_json_response(system_prompt, user_prompt)
        return AutomationResponse(**data)
    except Exception as e:
        import traceback
        print("===== GEMINI ERROR =====")
        print(str(e))
        print(traceback.format_exc())
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
