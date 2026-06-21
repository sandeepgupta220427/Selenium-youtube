"""
QA Bug Triage Crew — Runner + HTML Report Generator
Runs the CrewAI bug triage pipeline and produces a polished HTML report.
"""

import re, requests, os, datetime, webbrowser, html, time, litellm
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, LLM, Task, Crew, Process

load_dotenv()

# ── Rate-limit retry config ───────────────────────────────────────
os.environ["LITELLM_NUM_RETRIES"] = "5"
litellm.num_retries = 5
litellm.request_timeout = 120

# ── Jira Ticket Fetch ──────────────────────────────────────────────
def fetch_jira_ticket(bug_id):
    url = f"https://bugzz.atlassian.net/rest/api/3/issue/{bug_id}"
    r = requests.get(url, auth=(
        os.getenv("JIRA_EMAIL"),
        os.getenv("JIRA_API_TOKEN")
    ))
    data = r.json()
    f = data["fields"]
    desc = f["description"]["content"][0]["content"][0]["text"]
    return {
        "title": f["summary"],
        "key": data["key"],
        "reporter": f["reporter"]["displayName"],
        "description": desc,
        "full_text": f"""Bug Title: {f['summary']}
Bug ID: {data['key']}
Reporter: {f['reporter']['displayName']}

{desc}"""
    }

print("📡 Fetching Jira ticket VWO-48 ...")
ticket = fetch_jira_ticket("VWO-48")
bug_report = ticket["full_text"]
print(f"✅ Fetched: {ticket['title']} ({ticket['key']})")

# ── LLM Setup (with retry for Groq rate limits) ───────────────────
llm = LLM(
    model="groq/openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    num_retries=5,
    request_timeout=120
)

# ── Agents ─────────────────────────────────────────────────────────
bug_analyst = Agent(
    role="Senior Bug Triage Analyst",
    goal="Accurately classify incoming bugs by severity, category, and priority",
    backstory="""You are a veteran QA engineer with 15 years of experience.
    You follow strict severity classification:
    - P0 (Blocker): System down, data loss, security breach
    - P1 (Critical): Major feature broken, no workaround
    - P2 (Major): Feature impaired, workaround exists
    - P3 (Minor): Cosmetic issue, minor inconvenience
    - P4 (Trivial): Enhancement request, typo
    You never inflate severity. You always justify your classification.""",
    llm=llm, verbose=True, allow_delegation=False
)

root_cause_agent = Agent(
    role="Root Cause Analysis Specialist",
    goal="Identify the likely root cause and affected system components",
    backstory="""You are a debugging expert who thinks in system layers.
    You analyze bugs by tracing through: UI → API → Service → Database.
    You identify whether the issue is in frontend, backend,
    infrastructure, or third-party integration. You suggest which
    log files or monitoring dashboards to check first.""",
    llm=llm, verbose=True, allow_delegation=False
)

test_recommender = Agent(
    role="Test Strategy Advisor",
    goal="Recommend specific tests to validate the fix and prevent regression",
    backstory="""You are an SDET who designs test strategies.
    For every bug, you recommend:
    1. Immediate smoke tests to verify the fix
    2. Regression test cases to prevent recurrence
    3. Edge cases that should be added to the test suite
    You specify tests in Playwright TypeScript style when applicable.""",
    llm=llm, verbose=True, allow_delegation=False
)

# ── Tasks ──────────────────────────────────────────────────────────
triage_task = Task(
    description=f"""Analyze and classify this bug report:

{bug_report}

Provide:
1. Severity (P0-P4) with justification
2. Category (UI, Functional, Performance, Security, Data)
3. Affected component/module
4. Business impact assessment
5. Recommended priority for sprint planning""",
    expected_output="A structured triage report with severity, category, component, business impact, and sprint priority.",
    agent=bug_analyst
)

root_cause_task = Task(
    description=f"""Based on the triage analysis, investigate the likely root cause of this bug:

{bug_report}

Provide:
1. Most likely root cause
2. System layer affected (UI/API/Service/DB/Infra)
3. Related components that might be impacted
4. Suggested investigation steps
5. Which logs/dashboards to check first""",
    expected_output="A root cause analysis report with the probable cause, affected layer, related components, and investigation steps.",
    agent=root_cause_agent,
    context=[triage_task]
)

test_task = Task(
    description=f"""Based on the triage and root cause analysis, recommend test cases for this bug:

{bug_report}

Provide:
1. Verification test (confirm the fix works)
2. 3-5 regression test cases
3. Edge cases to add to the test suite
4. Suggested test automation approach (Playwright with Typescript)
5. Any load/performance tests if applicable""",
    expected_output="A test recommendation report with verification tests, regression cases, edge cases, and automation approach.",
    agent=test_recommender,
    context=[triage_task, root_cause_task]
)

# ── Run Crew ───────────────────────────────────────────────────────
crew = Crew(
    agents=[bug_analyst, root_cause_agent, test_recommender],
    tasks=[triage_task, root_cause_task, test_task],
    process=Process.sequential,
    verbose=True,
    max_rpm=4  # Throttle to avoid Groq rate limits
)

print("\n🔍 QA Bug Triage Crew — Starting Analysis")
print("=" * 60)

result = crew.kickoff()

# ── Gather individual task outputs ─────────────────────────────────
triage_output = str(triage_task.output) if triage_task.output else "No output"
rca_output = str(root_cause_task.output) if root_cause_task.output else "No output"
test_output = str(test_task.output) if test_task.output else "No output"
final_output = str(result)

print("\n" + "=" * 60)
print("📋 FINAL TRIAGE REPORT")
print("=" * 60)
print(final_output)

# ── Markdown → HTML conversion helpers ─────────────────────────────
def md_to_html(text):
    """Convert markdown-style text to HTML with proper formatting."""
    t = html.escape(text)

    # Code blocks (```...```)
    t = re.sub(
        r'```(\w+)?\n(.*?)```',
        lambda m: f'<div class="code-block"><div class="code-lang">{m.group(1) or "code"}</div><pre><code>{m.group(2)}</code></pre></div>',
        t, flags=re.DOTALL
    )

    # Inline code
    t = re.sub(r'`([^`]+)`', r'<code class="inline-code">\1</code>', t)

    # Bold
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)

    # Headers
    t = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', t, flags=re.MULTILINE)
    t = re.sub(r'^### (.+)$', r'<h3>\1</h3>', t, flags=re.MULTILINE)
    t = re.sub(r'^## (.+)$', r'<h2>\1</h2>', t, flags=re.MULTILINE)
    t = re.sub(r'^# (.+)$', r'<h1>\1</h1>', t, flags=re.MULTILINE)

    # Horizontal rules
    t = re.sub(r'^---+$', r'<hr>', t, flags=re.MULTILINE)

    # Bullet points
    t = re.sub(r'^[\s]*[-*] (.+)$', r'<li>\1</li>', t, flags=re.MULTILINE)
    t = re.sub(r'(<li>.*?</li>(\s*<li>.*?</li>)*)', r'<ul>\1</ul>', t, flags=re.DOTALL)

    # Numbered lists
    t = re.sub(r'^\d+\.\s+(.+)$', r'<li>\1</li>', t, flags=re.MULTILINE)

    # Paragraphs — wrap standalone lines
    lines = t.split('\n')
    result_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            result_lines.append(f'<p>{stripped}</p>')
        else:
            result_lines.append(line)
    t = '\n'.join(result_lines)

    return t


# ── Generate HTML Report ──────────────────────────────────────────
now = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QA Bug Triage Report — {html.escape(ticket['key'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg-primary: #0a0e1a;
    --bg-secondary: #111827;
    --bg-card: #1a2035;
    --bg-card-hover: #1f2847;
    --border: #2a3550;
    --text-primary: #f0f4fc;
    --text-secondary: #94a3c0;
    --text-muted: #6b7a99;
    --accent-blue: #3b82f6;
    --accent-purple: #8b5cf6;
    --accent-cyan: #06b6d4;
    --accent-green: #10b981;
    --accent-amber: #f59e0b;
    --accent-red: #ef4444;
    --accent-pink: #ec4899;
    --gradient-hero: linear-gradient(135deg, #1e1b4b 0%, #0f172a 50%, #042f2e 100%);
    --gradient-card-triage: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.05));
    --gradient-card-rca: linear-gradient(135deg, rgba(249,115,22,0.08), rgba(239,68,68,0.05));
    --gradient-card-test: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(6,182,212,0.05));
    --shadow-glow: 0 0 40px rgba(59,130,246,0.08);
    --radius: 16px;
    --radius-sm: 10px;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.7;
    min-height: 100vh;
  }}

  /* ── Animated Background ────────────────────────────── */
  .bg-grid {{
    position: fixed;
    inset: 0;
    background-image:
      radial-gradient(circle at 20% 20%, rgba(59,130,246,0.04) 0%, transparent 50%),
      radial-gradient(circle at 80% 80%, rgba(139,92,246,0.04) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(6,182,212,0.02) 0%, transparent 50%);
    z-index: 0;
    pointer-events: none;
  }}

  .container {{
    position: relative;
    z-index: 1;
    max-width: 1100px;
    margin: 0 auto;
    padding: 40px 24px 80px;
  }}

  /* ── Hero Section ───────────────────────────────────── */
  .hero {{
    background: var(--gradient-hero);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 48px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-glow);
  }}

  .hero::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(59,130,246,0.06) 0%, transparent 60%);
    pointer-events: none;
  }}

  .hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.25);
    color: var(--accent-blue);
    padding: 6px 16px;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    margin-bottom: 20px;
  }}

  .hero-badge .dot {{
    width: 8px;
    height: 8px;
    background: var(--accent-green);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }}

  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(0.8); }}
  }}

  .hero h1 {{
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f0f4fc 0%, #94a3c0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
  }}

  .hero-subtitle {{
    color: var(--text-secondary);
    font-size: 1rem;
    margin-bottom: 28px;
  }}

  .hero-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
  }}

  .meta-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 0.88rem;
  }}

  .meta-item .label {{
    color: var(--text-muted);
    font-weight: 500;
  }}

  .meta-item .value {{
    color: var(--text-primary);
    font-weight: 600;
  }}

  /* ── Bug Info Panel ─────────────────────────────────── */
  .bug-info {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 28px;
    margin-bottom: 32px;
  }}

  .bug-info h3 {{
    color: var(--accent-amber);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}

  .bug-info pre {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.8;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
  }}

  /* ── Section Cards ──────────────────────────────────── */
  .section {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    margin-bottom: 28px;
    overflow: hidden;
    transition: all 0.3s ease;
  }}

  .section:hover {{
    border-color: rgba(59,130,246,0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    transform: translateY(-2px);
  }}

  .section-header {{
    padding: 24px 28px 0;
    display: flex;
    align-items: center;
    gap: 14px;
  }}

  .section-icon {{
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
  }}

  .section-icon.triage {{ background: rgba(59,130,246,0.12); }}
  .section-icon.rca {{ background: rgba(249,115,22,0.12); }}
  .section-icon.test {{ background: rgba(16,185,129,0.12); }}
  .section-icon.verdict {{ background: rgba(139,92,246,0.12); }}

  .section-title-group h2 {{
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 2px;
  }}

  .section-title-group .agent-tag {{
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 500;
  }}

  .section-body {{
    padding: 20px 28px 28px;
  }}

  .section-body h1, .section-body h2, .section-body h3, .section-body h4 {{
    color: var(--accent-cyan);
    margin: 20px 0 10px;
    font-weight: 600;
  }}

  .section-body h1 {{ font-size: 1.3rem; }}
  .section-body h2 {{ font-size: 1.15rem; }}
  .section-body h3 {{ font-size: 1.05rem; }}
  .section-body h4 {{ font-size: 0.95rem; }}

  .section-body p {{
    color: var(--text-secondary);
    margin-bottom: 10px;
    font-size: 0.92rem;
  }}

  .section-body ul {{
    margin: 10px 0 16px 6px;
    list-style: none;
  }}

  .section-body ul li {{
    position: relative;
    padding-left: 20px;
    margin-bottom: 8px;
    color: var(--text-secondary);
    font-size: 0.92rem;
  }}

  .section-body ul li::before {{
    content: '▸';
    position: absolute;
    left: 0;
    color: var(--accent-blue);
    font-weight: bold;
  }}

  .section-body strong {{
    color: var(--text-primary);
    font-weight: 600;
  }}

  .section-body hr {{
    border: none;
    border-top: 1px solid var(--border);
    margin: 20px 0;
  }}

  /* ── Code Blocks ────────────────────────────────────── */
  .code-block {{
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: var(--radius-sm);
    margin: 16px 0;
    overflow: hidden;
  }}

  .code-lang {{
    background: #161b22;
    color: var(--accent-cyan);
    padding: 8px 16px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid #21262d;
    font-family: 'JetBrains Mono', monospace;
  }}

  .code-block pre {{
    padding: 20px;
    margin: 0;
    overflow-x: auto;
  }}

  .code-block code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    line-height: 1.8;
    color: #c9d1d9;
  }}

  .inline-code {{
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.2);
    color: var(--accent-cyan);
    padding: 2px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
  }}

  /* ── Verdict Section ────────────────────────────────── */
  .verdict {{
    background: linear-gradient(135deg, rgba(139,92,246,0.06), rgba(59,130,246,0.04));
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: var(--radius);
    margin-top: 8px;
  }}

  .verdict:hover {{
    border-color: rgba(139,92,246,0.4);
    box-shadow: 0 8px 40px rgba(139,92,246,0.1);
  }}

  /* ── Footer ─────────────────────────────────────────── */
  .footer {{
    text-align: center;
    padding: 40px 0 20px;
    color: var(--text-muted);
    font-size: 0.82rem;
  }}

  .footer .brand {{
    color: var(--accent-purple);
    font-weight: 600;
  }}

  /* ── Divider line between sections ──────────────────── */
  .section-divider {{
    border: none;
    border-top: 1px dashed var(--border);
    margin: 12px 28px;
  }}

  /* ── Responsive ─────────────────────────────────────── */
  @media (max-width: 768px) {{
    .container {{ padding: 20px 16px 60px; }}
    .hero {{ padding: 28px 20px; }}
    .hero h1 {{ font-size: 1.6rem; }}
    .hero-meta {{ flex-direction: column; gap: 10px; }}
    .section-body {{ padding: 16px 20px 24px; }}
  }}
</style>
</head>
<body>
<div class="bg-grid"></div>

<div class="container">
  <!-- Hero -->
  <div class="hero">
    <div class="hero-badge"><span class="dot"></span> CrewAI Analysis Complete</div>
    <h1>🔍 QA Bug Triage Report</h1>
    <p class="hero-subtitle">Automated bug analysis powered by a 3-agent CrewAI pipeline — triage, root cause analysis, and test recommendations.</p>
    <div class="hero-meta">
      <div class="meta-item">
        <span class="label">Ticket:</span>
        <span class="value">{html.escape(ticket['key'])}</span>
      </div>
      <div class="meta-item">
        <span class="label">Title:</span>
        <span class="value">{html.escape(ticket['title'])}</span>
      </div>
      <div class="meta-item">
        <span class="label">Reporter:</span>
        <span class="value">{html.escape(ticket['reporter'])}</span>
      </div>
      <div class="meta-item">
        <span class="label">Generated:</span>
        <span class="value">{now}</span>
      </div>
    </div>
  </div>

  <!-- Original Bug Report -->
  <div class="bug-info">
    <h3>🐛 Original Bug Report</h3>
    <pre>{html.escape(bug_report)}</pre>
  </div>

  <!-- Section 1: Triage -->
  <div class="section">
    <div class="section-header">
      <div class="section-icon triage">🎯</div>
      <div class="section-title-group">
        <h2>Bug Triage Classification</h2>
        <span class="agent-tag">Agent: Senior Bug Triage Analyst</span>
      </div>
    </div>
    <hr class="section-divider">
    <div class="section-body">
      {md_to_html(triage_output)}
    </div>
  </div>

  <!-- Section 2: Root Cause Analysis -->
  <div class="section">
    <div class="section-header">
      <div class="section-icon rca">🔬</div>
      <div class="section-title-group">
        <h2>Root Cause Analysis (RCA)</h2>
        <span class="agent-tag">Agent: Root Cause Analysis Specialist</span>
      </div>
    </div>
    <hr class="section-divider">
    <div class="section-body">
      {md_to_html(rca_output)}
    </div>
  </div>

  <!-- Section 3: Test Recommendations -->
  <div class="section">
    <div class="section-header">
      <div class="section-icon test">🧪</div>
      <div class="section-title-group">
        <h2>Test Recommendations &amp; Playwright Scripts</h2>
        <span class="agent-tag">Agent: Test Strategy Advisor</span>
      </div>
    </div>
    <hr class="section-divider">
    <div class="section-body">
      {md_to_html(test_output)}
    </div>
  </div>

  <!-- Final Verdict -->
  <div class="section verdict">
    <div class="section-header">
      <div class="section-icon verdict">⚖️</div>
      <div class="section-title-group">
        <h2>Final Verdict</h2>
        <span class="agent-tag">Combined output from all 3 agents</span>
      </div>
    </div>
    <hr class="section-divider">
    <div class="section-body">
      {md_to_html(final_output)}
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <p>Generated by <span class="brand">QA Bug Triage Crew</span> — CrewAI × Groq × Jira</p>
    <p style="margin-top:4px;">AITesterBlueprint · {now}</p>
  </div>
</div>
</body>
</html>
"""

# ── Write & Open Report ───────────────────────────────────────────
report_path = Path(__file__).parent / "bug_triage_report.html"
report_path.write_text(html_content, encoding="utf-8")
print(f"\n✅ HTML report saved to: {report_path}")
webbrowser.open(f"file://{report_path.resolve()}")
print("🌐 Opening report in browser ...")
