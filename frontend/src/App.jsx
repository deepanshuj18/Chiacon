import { useState, useEffect } from 'react';
import UseCaseGenerator from './components/UseCaseGenerator';
import EmailGenerator from './components/EmailGenerator';

const TABS = [
  { id: 'usecase', label: 'Automation Opportunity Engine' },
  { id: 'email', label: 'Executive Outreach Generator' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('usecase');
  const [automationResult, setAutomationResult] = useState(null);
  const [automationIndustry, setAutomationIndustry] = useState(null);

  const switchToEmail = () => setActiveTab('email');

  const clearAutomation = () => {
    setAutomationResult(null);
    setAutomationIndustry(null);
  };

  // Cold-start banner — show once per session
  const [showBanner, setShowBanner] = useState(
    () => !sessionStorage.getItem('banner-dismissed')
  );
  const [bannerFading, setBannerFading] = useState(false);

  const dismissBanner = () => {
    setBannerFading(true);
    setTimeout(() => {
      setShowBanner(false);
      sessionStorage.setItem('banner-dismissed', '1');
    }, 400);
  };

  useEffect(() => {
    if (!showBanner) return;
    const t = setTimeout(dismissBanner, 8000);
    return () => clearTimeout(t);
  }, [showBanner]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>

      {/* ── Cold-start Banner ────────────────────────────────────────── */}
      {showBanner && (
        <div className={`coldstart-banner${bannerFading ? ' fading' : ''}`}>
          <span className="coldstart-icon">⚡</span>
          <div className="coldstart-text">
            <strong>First request may take ~30 seconds</strong>
            <span>The server sleeps when inactive. It wakes up automatically — just give it a moment.</span>
          </div>
          <button className="coldstart-close" onClick={dismissBanner} aria-label="Dismiss">✕</button>
        </div>
      )}

      {/* ── Header ──────────────────────────────────────────────────── */}
      <header style={{ padding: '52px 24px 20px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 700, letterSpacing: '-0.02em', lineHeight: 1.2 }}>
          <span style={{
            background: 'linear-gradient(135deg, #818cf8, #a78bfa, #6366f1)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}>
            Chiacon
          </span>{' '}
          <span style={{ color: '#e2e8f0', fontWeight: 300 }}>AI Automation Studio</span>
        </h1>

        <p style={{
          color: '#64748b',
          fontSize: '0.88rem',
          maxWidth: '460px',
          margin: '12px auto 0',
          lineHeight: 1.75,
        }}>
          Identify RPA, Data &amp; Analytics, and AI-driven automation opportunities
          — and generate executive outreach for enterprise transformation.
        </p>

        {/* ── Strategic Positioning Line ───────────────────────────── */}
        <div style={{
          display: 'inline-block',
          marginTop: '20px',
          padding: '10px 20px',
          borderRadius: '99px',
          background: 'rgba(99,102,241,0.07)',
          border: '1px solid rgba(99,102,241,0.2)',
        }}>
          <p style={{
            fontSize: '0.78rem',
            color: '#818cf8',
            letterSpacing: '0.02em',
            lineHeight: 1.5,
            margin: 0,
          }}>
            This interactive prototype demonstrates how Chiacon identifies, structures, and communicates
            AI-driven automation opportunities for enterprise clients.
          </p>
        </div>
      </header>

      {/* ── Main Content ────────────────────────────────────────────── */}
      <main style={{
        flex: 1,
        width: '100%',
        maxWidth: '720px',
        margin: '0 auto',
        padding: '28px 24px 80px',
        boxSizing: 'border-box',
      }}>
        {/* Tab Bar */}
        <div className="tab-bar" style={{ marginBottom: '24px' }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content Card */}
        <div className="glass-card" style={{ padding: '36px 40px' }}>
          <div style={{ display: activeTab === 'usecase' ? 'block' : 'none' }}>
            <UseCaseGenerator
              onResultGenerated={(data, industry) => {
                setAutomationResult(data);
                setAutomationIndustry(industry);
              }}
              onResultCleared={clearAutomation}
            />
            {automationResult && (
              <div style={{ marginTop: '28px', paddingTop: '24px', borderTop: '1px solid rgba(99,102,241,0.15)' }}>
                <button
                  id="context-email-btn"
                  className="btn-primary"
                  onClick={switchToEmail}
                  style={{ width: '100%' }}
                >
                  Generate Executive Outreach Email &rarr;
                </button>
              </div>
            )}
          </div>

          <div style={{ display: activeTab === 'email' ? 'block' : 'none' }}>
            <EmailGenerator
              automationResult={automationResult}
              automationIndustry={automationIndustry}
            />
          </div>
        </div>
      </main>

      {/* ── Footer ──────────────────────────────────────────────────── */}
      <footer style={{
        padding: '20px 24px 28px',
        textAlign: 'center',
      }}>
        <p style={{ fontSize: '0.72rem', color: '#334155', marginBottom: '6px' }}>
          Chiacon &middot; IT Consulting &amp; Automation
        </p>
        <p style={{ fontSize: '0.7rem', color: '#1e293b' }}>
          Built with React, FastAPI &amp; Gemini API &mdash; modular service architecture with context-aware workflow management
        </p>
      </footer>
    </div>
  );
}
