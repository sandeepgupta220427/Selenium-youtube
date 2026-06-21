import React, { useState } from 'react';
import {
    Play,
    RotateCcw,
    ClipboardCheck,
    Clipboard,
    CheckCircle2,
    FileCode,
    Cpu,
    ChevronRight
} from 'lucide-react';
import './App.css';

function App() {
    const [javaCode, setJavaCode] = useState('');
    const [playwrightCode, setPlaywrightCode] = useState('');
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleConvert = async () => {
        setLoading(true);
        setPlaywrightCode(''); // Clear previous
        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sourceCode: javaCode })
            });
            const data = await response.json();
            if (data.error) {
                setPlaywrightCode(`// Error: ${data.error}`);
            } else {
                setPlaywrightCode(data.convertedCode);
            }
        } catch (error) {
            console.error('Conversion failed', error);
            setPlaywrightCode('// Error: API Server Not Responding. Ensure "npm run server" is running.');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(playwrightCode);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const clearAll = () => {
        setJavaCode('');
        setPlaywrightCode('');
    };

    return (
        <div className="dashboard">
            <nav className="top-nav">
                <div className="logo">
                    <Cpu className="logo-icon" size={24} />
                    <span>BLAST Engine <span className="version">v1.2</span></span>
                </div>
                <div className="nav-actions">
                    <button className="nav-btn secondary" onClick={clearAll}>
                        <RotateCcw size={16} /> Reset
                    </button>
                </div>
            </nav>

            <div className="hero">
                <h1>Conversion Sentinel</h1>
                <p>Strategic migration from Selenium Java to Playwright TS/JS with 1:1 Precision</p>
            </div>

            <main className="comparison-theater">
                <section className="panel source-panel">
                    <div className="panel-header">
                        <div className="panel-title">
                            <FileCode className="panel-icon java" size={18} />
                            <span>Selenium Java (TestNG)</span>
                        </div>
                        <span className="badge">Source</span>
                    </div>
                    <div className="editor-container">
                        <textarea
                            value={javaCode}
                            onChange={(e) => setJavaCode(e.target.value)}
                            placeholder="Paste your Java @Test methods here..."
                            spellCheck="false"
                        />
                    </div>
                </section>

                <section className="control-center">
                    <div className="bridge-line"></div>
                    <button
                        className={`blast-trigger ${loading ? 'loading' : ''}`}
                        onClick={handleConvert}
                        disabled={loading || !javaCode}
                    >
                        {loading ? (
                            <div className="pulse"></div>
                        ) : (
                            <div className="trigger-content">
                                <ChevronRight size={32} />
                            </div>
                        )}
                        <span className="tooltip">{loading ? 'Processing...' : 'Blast It!'}</span>
                    </button>
                </section>

                <section className="panel target-panel">
                    <div className="panel-header">
                        <div className="panel-title">
                            <FileCode className="panel-icon playwright" size={18} />
                            <span>Playwright TypeScript</span>
                        </div>
                        <div className="header-actions">
                            {playwrightCode && (
                                <button
                                    className={`copy-btn ${copied ? 'copied' : ''}`}
                                    onClick={copyToClipboard}
                                    title="Copy to Clipboard"
                                >
                                    {copied ? <ClipboardCheck size={18} /> : <Clipboard size={18} />}
                                </button>
                            )}
                            <span className="badge success">Target</span>
                        </div>
                    </div>
                    <div className="editor-container">
                        <textarea
                            value={playwrightCode}
                            readOnly
                            placeholder="Deterministic output will appear here..."
                            spellCheck="false"
                        />
                    </div>
                </section>
            </main>

            <footer className="status-bar">
                <div className="status-item">
                    <CheckCircle2 size={14} className="success-icon" />
                    <span>Ollama (codellama) Connected</span>
                </div>
                <div className="status-item">
                    <div className="dot"></div>
                    <span>API: Online</span>
                </div>
            </footer>
        </div>
    );
}

export default App;
