/* ================================================
   RESULTS.JS — Renders detection results
   ================================================ */

const SCORE_COLORS = {
  low:    { stroke: '#4ade9a', text: '#4ade9a' },
  medium: { stroke: '#e8a94a', text: '#e8a94a' },
  high:   { stroke: '#e05252', text: '#e05252' },
};

function getScoreLevel(score) {
  if (score <= 33) return 'low';
  if (score <= 66) return 'medium';
  return 'high';
}

function getScoreColor(score) {
  return SCORE_COLORS[getScoreLevel(score)];
}

function buildScoreRing(score) {
  const radius = 44;
  const circumference = 2 * Math.PI * radius;
  const color = getScoreColor(score);
  const offset = circumference - (score / 100) * circumference;

  return `
    <div class="score-ring" id="score-ring">
      <svg viewBox="0 0 110 110">
        <circle class="track" cx="55" cy="55" r="${radius}"/>
        <circle class="fill"
                cx="55" cy="55" r="${radius}"
                stroke="${color.stroke}"
                stroke-dasharray="${circumference}"
                stroke-dashoffset="${circumference}"
                id="score-fill"/>
      </svg>
      <div class="score-text">
        <span id="score-num" style="color:${color.text}">0</span>
        <span class="score-label">/ 100</span>
      </div>
    </div>
  `;
}

function animateScore(score) {
  const fill = document.getElementById('score-fill');
  const num  = document.getElementById('score-num');
  if (!fill || !num) return;

  const radius = 44;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  // Animate stroke
  setTimeout(() => {
    fill.style.strokeDashoffset = offset;
  }, 200);

  // Animate count-up
  let current = 0;
  const duration = 1200;
  const step = score / (duration / 16);
  const timer = setInterval(() => {
    current = Math.min(current + step, score);
    num.textContent = Math.round(current);
    if (current >= score) clearInterval(timer);
  }, 16);
}

function buildBreakdownBars(breakdown) {
  if (!breakdown || !Object.keys(breakdown).length) return '';

  return Object.entries(breakdown).map(([key, value]) => {
    const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    const score = typeof value === 'number' ? value : 0;
    const color = getScoreColor(score);

    return `
      <div class="breakdown-row">
        <span class="breakdown-label">${label}</span>
        <div class="breakdown-bar-wrap">
          <div class="progress-bar" style="flex:1">
            <div class="progress-fill"
                 style="width:0%;background:linear-gradient(90deg,${color.stroke},${color.stroke}cc)"
                 data-target="${score}"></div>
          </div>
          <span class="breakdown-score" style="color:${color.text}">${score}</span>
        </div>
      </div>
    `;
  }).join('');
}

function animateProgressBars() {
  document.querySelectorAll('.progress-fill[data-target]').forEach(bar => {
    const target = bar.getAttribute('data-target');
    setTimeout(() => {
      bar.style.width = target + '%';
    }, 400);
  });
}

function getVerdictColor(score) {
  if (score <= 33) return 'var(--success)';
  if (score <= 66) return 'var(--warning)';
  return 'var(--danger)';
}

function renderResults(result) {
  const container = document.getElementById('results-container');
  if (!container) return;

  const score   = result.score || 0;
  const verdict = escapeHtml(result.verdict || 'Unknown');
  const conf    = escapeHtml(result.confidence || 'Low');
  const type    = escapeHtml((result.detection_type || '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()));

  const TOOL_ICONS = {
    ai_content: '🤖', plagiarism: '📋', fake_news: '📰',
    fake_review: '⭐', fake_profile: '👤', fake_job: '💼',
    phishing: '🎣', code_plagiarism: '⟨⟩', general: '🔍'
  };
  const icon = TOOL_ICONS[result.detection_type] || '🔍';

  container.innerHTML = `
    <!-- Header -->
    <div class="results-header animate-fade-up">
      <div>
        <div style="display:flex;align-items:center;gap:var(--space-md);margin-bottom:var(--space-md)">
          <span class="badge badge-gold">${icon} ${type} Detection</span>
          ${result.source_url ? `<span class="badge badge-muted" title="${escapeHtml(result.source_url)}">🔗 URL Scan</span>` : ''}
          ${result.source_filename ? `<span class="badge badge-muted">📄 ${escapeHtml(result.source_filename)}</span>` : ''}
        </div>
        <h1 style="font-size:var(--text-4xl);font-weight:900;letter-spacing:-0.04em;margin-bottom:var(--space-sm)">
          Detection Report
        </h1>
        <p>Analysis complete — here is your detailed breakdown.</p>
      </div>
      <div style="display:flex;gap:var(--space-sm);flex-wrap:wrap">
        <a href="/detect" class="btn btn-secondary">← Run Another</a>
        <button class="btn btn-primary" onclick="window.print()">Export PDF</button>
      </div>
    </div>

    <div class="results-layout">
      <!-- Left Column -->
      <div>
        <!-- Score Overview -->
        <div class="score-overview-card animate-fade-up">
          ${buildScoreRing(score)}
          <div class="score-details">
            <div class="score-verdict" style="color:${getVerdictColor(score)}">${verdict}</div>
            <p style="margin-top:var(--space-sm);font-size:var(--text-sm)">
              ${escapeHtml(result.raw_analysis || 'Analysis complete.')}
            </p>
            <div class="score-meta">
              <span class="badge ${score > 66 ? 'badge-danger' : score > 33 ? 'badge-warning' : 'badge-success'}">
                Score: ${score}/100
              </span>
              <span class="badge badge-muted">Confidence: ${conf}</span>
            </div>
          </div>
        </div>

        <!-- Score Breakdown -->
        ${result.breakdown && Object.keys(result.breakdown).length ? `
        <div class="breakdown-card reveal">
          <h3>📊 Score Breakdown</h3>
          ${buildBreakdownBars(result.breakdown)}
        </div>` : ''}

        <!-- Evidence / Highlights -->
        ${result.highlights && result.highlights.length ? `
        <div class="highlights-card reveal">
          <h3>⚠ Evidence Found</h3>
          <p style="font-size:var(--text-sm);margin-bottom:var(--space-md)">
            These specific patterns triggered the detection:
          </p>
          ${result.highlights.map(h => `
            <div class="highlight-item">
              <div class="highlight-dot"></div>
              <span>${escapeHtml(h)}</span>
            </div>
          `).join('')}
        </div>` : ''}

        <!-- Improvements -->
        ${result.improvements && result.improvements.length ? `
        <div class="highlights-card reveal">
          <h3>✦ Improvement Suggestions</h3>
          <p style="font-size:var(--text-sm);margin-bottom:var(--space-md)">
            Here's how to address the detected issues:
          </p>
          ${result.improvements.map((imp, i) => `
            <div class="improvement-item">
              <div class="improvement-num">${i + 1}</div>
              <span>${escapeHtml(imp)}</span>
            </div>
          `).join('')}
        </div>` : ''}
      </div>

      <!-- Right Sidebar -->
      <div>
        <!-- Quick Summary Card -->
        <div class="card card-gold reveal" style="margin-bottom:var(--space-lg)">
          <h3 style="font-size:var(--text-base);font-weight:700;margin-bottom:var(--space-lg)">Quick Summary</h3>
          <div style="display:flex;flex-direction:column;gap:var(--space-md)">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-size:var(--text-sm);color:var(--text-muted)">Detection Type</span>
              <span style="font-size:var(--text-sm);font-weight:600">${icon} ${type}</span>
            </div>
            <div class="divider" style="margin:0"></div>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-size:var(--text-sm);color:var(--text-muted)">Score</span>
              <span style="font-size:var(--text-sm);font-weight:700;color:${getVerdictColor(score)}">${score}/100</span>
            </div>
            <div class="divider" style="margin:0"></div>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-size:var(--text-sm);color:var(--text-muted)">Verdict</span>
              <span class="badge ${score > 66 ? 'badge-danger' : score > 33 ? 'badge-warning' : 'badge-success'}">${verdict}</span>
            </div>
            <div class="divider" style="margin:0"></div>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-size:var(--text-sm);color:var(--text-muted)">Confidence</span>
              <span style="font-size:var(--text-sm);font-weight:600">${conf}</span>
            </div>
            <div class="divider" style="margin:0"></div>
            <div style="display:flex;justify-content:space-between;align-items:center">
              <span style="font-size:var(--text-sm);color:var(--text-muted)">Issues Found</span>
              <span style="font-size:var(--text-sm);font-weight:600">${(result.highlights || []).length}</span>
            </div>
          </div>
        </div>

        <!-- What This Means Card -->
        <div class="card reveal" style="margin-bottom:var(--space-lg)">
          <h3 style="font-size:var(--text-base);font-weight:700;margin-bottom:var(--space-md)">What This Means</h3>
          <p style="font-size:var(--text-sm);line-height:1.7">
            ${getScoreInterpretation(score, result.detection_type)}
          </p>
        </div>

        <!-- Actions Card -->
        <div class="card reveal">
          <h3 style="font-size:var(--text-base);font-weight:700;margin-bottom:var(--space-md)">Actions</h3>
          <div style="display:flex;flex-direction:column;gap:var(--space-sm)">
            <a href="/detect" class="btn btn-secondary" style="justify-content:center">
              Run Another Scan
            </a>
            <a href="/history" class="btn btn-ghost" style="justify-content:center">
              View History
            </a>
            <button class="btn btn-ghost" onclick="window.print()" style="justify-content:center">
              Export as PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Trigger animations
  requestAnimationFrame(() => {
    animateScore(score);
    setTimeout(animateProgressBars, 300);
    setTimeout(() => {
      document.querySelectorAll('.reveal').forEach((el, i) => {
        setTimeout(() => el.classList.add('visible'), i * 80);
      });
    }, 100);
  });
}

function getScoreInterpretation(score, type) {
  if (score <= 20) return 'This content appears highly authentic and genuine. No significant red flags were detected.';
  if (score <= 40) return 'This content is mostly authentic with minor concerns. Review the highlighted areas for context.';
  if (score <= 60) return 'This content shows moderate warning signs. Treat with caution and verify key claims independently.';
  if (score <= 80) return 'This content has significant indicators of being fake or problematic. Exercise strong caution.';
  return 'This content shows very strong indicators of being fake, misleading, or AI-generated. Do not trust without independent verification.';
}

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get('id');

  if (!id) {
    document.getElementById('results-container').innerHTML = `
      <div style="text-align:center;padding:var(--space-3xl)">
        <div style="font-size:3rem;margin-bottom:var(--space-lg);opacity:0.4">⬡</div>
        <h2 style="font-size:var(--text-2xl);margin-bottom:var(--space-md)">No results to display</h2>
        <p style="margin-bottom:var(--space-xl)">Run a detection scan to see results here.</p>
        <a href="/detect" class="btn btn-primary">Start Scanning</a>
      </div>
    `;
    return;
  }

  try {
    const res = await fetch('/api/history/' + id);
    if (!res.ok) throw new Error('Result not found');
    const data = await res.json();
    // Use the full_result inside the history row
    const result = data.full_result || data;
    renderResults(result);
  } catch (e) {
    showToast('Failed to load results.', 'error');
    document.getElementById('results-container').innerHTML = `
      <div style="text-align:center;padding:var(--space-3xl)">
        <div style="font-size:3rem;margin-bottom:var(--space-lg);color:var(--danger)">⚠</div>
        <h2 style="font-size:var(--text-2xl);margin-bottom:var(--space-md)">Result Not Found</h2>
        <p style="margin-bottom:var(--space-xl)">The requested scan result does not exist or was deleted.</p>
        <a href="/detect" class="btn btn-primary">Run New Scan</a>
      </div>
    `;
  }
});
