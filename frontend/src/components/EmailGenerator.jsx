import { useState, useEffect } from 'react';
import { generateEmail } from '../api';

export default function EmailGenerator({ automationResult, automationIndustry }) {
    const [companyName, setCompanyName] = useState('');
    const [industry, setIndustry] = useState('');
    const [role, setRole] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');
    const [copied, setCopied] = useState(false);

    const isContextAware = !!automationResult;

    // Auto-capitalize: "abc fmcg ltd" → "Abc Fmcg Ltd"
    const toTitleCase = (str) =>
        str.replace(/\b\w/g, (c) => c.toUpperCase());

    useEffect(() => {
        if (automationResult && automationIndustry) {
            setIndustry(automationIndustry);
        }
    }, [automationResult, automationIndustry]);

    const buildContextSummary = () => {
        if (!automationResult) return null;
        const { problem_summary, ai_opportunities, expected_business_impact } = automationResult;
        return [
            `Problem: ${problem_summary}`,
            `Opportunities: ${ai_opportunities.join('; ')}`,
            `Impact: ${expected_business_impact.join('; ')}`,
        ].join('\n');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);
        setCopied(false);
        try {
            const data = await generateEmail({
                company_name: companyName,
                industry,
                role,
                context_summary: buildContextSummary(),
            });
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const getEmailText = () =>
        result ? `Subject: ${result.email_subject}\n\n${result.email_body}` : '';

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(getEmailText());
            setCopied(true);
            setTimeout(() => setCopied(false), 2500);
        } catch {
            // Fallback for older browsers
            const el = document.createElement('textarea');
            el.value = getEmailText();
            document.body.appendChild(el);
            el.select();
            document.execCommand('copy');
            document.body.removeChild(el);
            setCopied(true);
            setTimeout(() => setCopied(false), 2500);
        }
    };

    const handleDownload = () => {
        const filename = `chiacon-email-${companyName.replace(/\s+/g, '-').toLowerCase()}.txt`;
        const blob = new Blob([getEmailText()], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div>
            {/* Context-Aware Banner */}
            {isContextAware && (
                <div className="context-banner fade-in">
                    <svg style={{ flexShrink: 0, marginTop: '1px' }} width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <circle cx="8" cy="8" r="7.5" stroke="#818cf8" />
                        <path d="M8 5v4M8 11v.5" stroke="#818cf8" strokeWidth="1.5" strokeLinecap="round" />
                    </svg>
                    <div>
                        <p style={{ fontSize: '0.88rem', fontWeight: 600, color: '#a5b4fc' }}>
                            Context-Aware Mode Active
                        </p>
                        <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: '4px', lineHeight: 1.6 }}>
                            Industry locked to{' '}
                            <strong style={{ color: '#c7d2fe' }}>{automationIndustry}</strong>.
                            {' '}Email will reference your identified automation opportunity.
                        </p>
                    </div>
                </div>
            )}

            <form onSubmit={handleSubmit} className="form-stack">
                {/* Company Name */}
                <div>
                    <label className="input-label">Company Name</label>
                    <input
                        id="company-input"
                        className="input-field"
                        placeholder="e.g. ABC FMCG Ltd"
                        value={companyName}
                        onChange={(e) => setCompanyName(toTitleCase(e.target.value))}
                        required
                    />
                </div>

                {/* Industry */}
                <div>
                    <label className="input-label">
                        Industry
                        {isContextAware && (
                            <span className="locked-pill">Locked</span>
                        )}
                    </label>
                    <input
                        id="email-industry-input"
                        className="input-field"
                        placeholder="e.g. FMCG, Healthcare, Banking"
                        value={industry}
                        onChange={(e) => !isContextAware && setIndustry(e.target.value)}
                        disabled={isContextAware}
                        required
                        style={isContextAware ? {
                            opacity: 0.55,
                            cursor: 'not-allowed',
                            background: 'rgba(99,102,241,0.04)',
                        } : {}}
                    />
                </div>

                {/* Recipient Role */}
                <div>
                    <label className="input-label">Recipient Role</label>
                    <input
                        id="email-role-input"
                        className="input-field"
                        placeholder="e.g. CFO, CTO, VP Operations"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        required
                    />
                </div>

                <button
                    id="generate-email-btn"
                    type="submit"
                    className="btn-primary"
                    style={{ width: '100%' }}
                    disabled={loading || !companyName || !industry || !role}
                >
                    {loading ? (
                        <><span className="spinner" />Generating Email...</>
                    ) : isContextAware ? (
                        'Generate Context-Aware Email'
                    ) : (
                        'Generate Outreach Email'
                    )}
                </button>
            </form>

            {error && <div className="error-msg" style={{ marginTop: '20px' }}>{error}</div>}

            {result && (
                <div className="fade-in" style={{ marginTop: '28px' }}>
                    {/* Action bar */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        marginBottom: '12px',
                    }}>
                        <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            textTransform: 'uppercase',
                            letterSpacing: '0.1em',
                            color: 'var(--accent-light)',
                        }}>
                            Generated Email
                        </span>
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {/* Copy button */}
                            <button
                                id="copy-email-btn"
                                onClick={handleCopy}
                                className="action-btn"
                                title="Copy to clipboard"
                            >
                                {copied ? (
                                    <>
                                        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                                            <path d="M2 6.5L5 9.5L11 3.5" stroke="#34d399" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
                                        </svg>
                                        <span style={{ color: '#34d399' }}>Copied!</span>
                                    </>
                                ) : (
                                    <>
                                        <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                                            <rect x="4" y="4" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.3" />
                                            <path d="M4 9H2a1 1 0 01-1-1V2a1 1 0 011-1h6a1 1 0 011 1v2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                                        </svg>
                                        Copy
                                    </>
                                )}
                            </button>
                            {/* Download button */}
                            <button
                                id="download-email-btn"
                                onClick={handleDownload}
                                className="action-btn"
                                title="Download as .txt"
                            >
                                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                                    <path d="M6.5 1v8M3.5 6.5l3 3 3-3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
                                    <path d="M1 10.5v1a1 1 0 001 1h9a1 1 0 001-1v-1" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
                                </svg>
                                Download
                            </button>
                        </div>
                    </div>

                    {/* Email block */}
                    <div className="email-block">
                        <div className="email-subject-label">Subject</div>
                        <div className="email-subject-text">{result.email_subject}</div>
                        <div className="email-body">{result.email_body}</div>
                    </div>
                </div>
            )}
        </div>
    );
}
