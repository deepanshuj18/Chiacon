import { useState } from 'react';
import { generateAutomation } from '../api';

const INDUSTRIES = [
    'FMCG',
    'Banking & Financial Services',
    'Healthcare',
    'Insurance',
    'Retail',
    'Manufacturing',
    'Logistics & Supply Chain',
    'Telecommunications',
    'Energy & Utilities',
    'Real Estate',
    'Education',
    'Government & Public Sector',
    'Oil & Gas',
    'Pharmaceuticals',
    'Other',
];

export default function UseCaseGenerator({ onResultGenerated, onResultCleared }) {
    const [industry, setIndustry] = useState('');
    const [customIndustry, setCustomIndustry] = useState('');
    const [problem, setProblem] = useState('');
    const [role, setRole] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const effectiveIndustry = industry === 'Other' ? customIndustry.trim() : industry;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResult(null);
        if (onResultCleared) onResultCleared();

        try {
            const data = await generateAutomation({
                industry: effectiveIndustry,
                problem,
                role: role || undefined,
            });
            setResult(data);
            if (onResultGenerated) onResultGenerated(data, effectiveIndustry);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setResult(null);
        setError('');
        if (onResultCleared) onResultCleared();
    };

    return (
        <div>
            <form onSubmit={handleSubmit} className="form-stack">
                {/* Industry */}
                <div>
                    <label className="input-label">Industry</label>
                    <select
                        id="industry-input"
                        className="input-field"
                        value={industry}
                        onChange={(e) => { setIndustry(e.target.value); setCustomIndustry(''); }}
                        required
                    >
                        <option value="" disabled>Select your industry...</option>
                        {INDUSTRIES.map((ind) => (
                            <option key={ind} value={ind}>{ind}</option>
                        ))}
                    </select>
                    {industry === 'Other' && (
                        <input
                            id="custom-industry-input"
                            className="input-field"
                            style={{ marginTop: '10px' }}
                            placeholder="Enter your industry..."
                            value={customIndustry}
                            onChange={(e) => setCustomIndustry(e.target.value)}
                            required
                            autoFocus
                        />
                    )}
                </div>

                {/* Business Problem */}
                <div>
                    <label className="input-label">Business Problem</label>
                    <textarea
                        id="problem-input"
                        className="input-field"
                        placeholder="Describe the business problem you're facing..."
                        value={problem}
                        onChange={(e) => setProblem(e.target.value)}
                        required
                    />
                </div>

                {/* Role */}
                <div>
                    <label className="input-label">
                        Your Role
                        <span style={{ opacity: 0.45, fontWeight: 400, textTransform: 'none', letterSpacing: 0, fontSize: '0.78rem' }}>
                            (Optional)
                        </span>
                    </label>
                    <input
                        id="role-input"
                        className="input-field"
                        placeholder="e.g. CFO, COO, Head of Operations"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                    />
                </div>

                <button
                    id="generate-usecase-btn"
                    type="submit"
                    className="btn-primary"
                    style={{ width: '100%' }}
                    disabled={loading || !effectiveIndustry || !problem}
                >
                    {loading ? (
                        <><span className="spinner" />Analyzing...</>
                    ) : result ? (
                        'Regenerate Analysis'
                    ) : (
                        'Identify AI Opportunities'
                    )}
                </button>
            </form>

            {error && <div className="error-msg" style={{ marginTop: '20px' }}>{error}</div>}

            {result && (
                <div className="fade-in" style={{ marginTop: '28px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {/* Header row */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--accent-light)' }}>
                            Analysis Results
                        </span>
                        <button
                            id="clear-result-btn"
                            onClick={handleClear}
                            style={{
                                background: 'none',
                                border: 'none',
                                cursor: 'pointer',
                                fontSize: '0.78rem',
                                color: 'var(--text-muted)',
                                padding: '4px 8px',
                                borderRadius: '6px',
                                transition: 'color 0.2s',
                            }}
                            onMouseEnter={e => e.target.style.color = '#f87171'}
                            onMouseLeave={e => e.target.style.color = 'var(--text-muted)'}
                        >
                            ✕ Clear
                        </button>
                    </div>

                    {/* Problem Summary */}
                    <div className="result-card">
                        <div className="result-label">Problem Summary</div>
                        <p className="result-text">{result.problem_summary}</p>
                    </div>

                    {/* AI Opportunities */}
                    <div className="result-card">
                        <div className="result-label">AI &amp; Automation Opportunities</div>
                        <ul className="result-list">
                            {result.ai_opportunities.map((item, i) => (
                                <li key={i}>{item}</li>
                            ))}
                        </ul>
                    </div>

                    {/* Business Impact */}
                    <div className="result-card">
                        <div className="result-label">Expected Business Impact</div>
                        <ul className="result-list">
                            {result.expected_business_impact.map((item, i) => (
                                <li key={i}>{item}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            )}
        </div>
    );
}
