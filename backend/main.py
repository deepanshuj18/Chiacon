"""
Chiacon AI Automation Studio — FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.automation import router as automation_router
from routes.email import router as email_router

app = FastAPI(
    title="Chiacon AI Automation Studio",
    version="1.0.0",
    description="AI-powered automation consulting demo",
)

# ── CORS ───────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────────────────────────
app.include_router(automation_router)
app.include_router(email_router)


@app.get("/")
async def health():
    return {"status": "ok", "service": "Chiacon AI Automation Studio"}
