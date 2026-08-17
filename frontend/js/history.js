/* ================================================
   HISTORY.JS — Scan history page logic
   ================================================ */

const API_BASE = '/api';

const DETECTION_LABELS = {
  ai_content: { label: 'AI Content', icon: '🤖' },
  plagiarism:  { label: 'Plagiarism',  icon: '📋' },
  fake_news:   { label: 'Fake News',   icon: '📰' },
  fake_review: { label: 'Fake Review', icon: '⭐' },
  fake_profile:{ label: 'Fake Profile',icon: '👤' },
  fake_job:    { label: 'Fake Job',    icon: '💼' },
  phishing:    { label: 'Phishing',    icon: '🎣' },
  code_plagiarism: { label: 'Code Plagiarism', icon: '⟨⟩' },
  general:     { label: 'General',     icon: '🔍' },
};

async function loadHistory() {
  const container = document.getElementById('history-container');
  if (!container) return;

  container.innerHTML = `
    <div style="display:flex;align-items:center;justify-content:center;padding:var(--space-3xl);gap:var(--space-md)">
      <div class="spinner"></div>
      <span style="color:var(--text-muted)">Loading history...</span>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/history?limit=100`);
    if (!res.ok) throw new Error('Failed to load history');
    const data = await res.json();
    renderHistory(data.scans || []);
  } catch (err) {
    container.innerHTML = `
      <div style="text-align:center;padding:var(--space-3xl)">
        <p style="color:var(--danger)">Could not load history. Is the server running?</p>
        <button class="btn btn-secondary mt-lg" onclick="loadHistory()">Retry</button>
      </div>
    `;
  }
}

function renderHistory(scans) {
  const container = document.getElementById('history-container');
  if (!container) return;

  if (!scans.length) {
    container.innerHTML = `
      <div class="history-empty">
        <div class="empty-icon">◷</div>
        <h3 style="font-size:var(--text-xl);font-weight:700;margin-bottom:var(--space-sm)">No scans yet</h3>
        <p style="margin-bottom:var(--space-xl)">Your scan history will appear here.</p>
        <a href="/detect" class="btn btn-primary">Run Your First Scan</a>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="history-table-wrap">
      <table class="history-table">
        <thead>
          <tr>
            <th>Type</th>
            <th>Content Preview</th>
            <th>Source</th>
            <th>Score</th>
            <th>Verdict</th>
            <th>Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="history-tbody">
          ${scans.map(scan => buildHistoryRow(scan)).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function buildHistoryRow(scan) {
  const info   = DETECTION_LABELS[scan.detection_type] || { label: 'Unknown', icon: '🔍' };
  const score  = scan.score || 0;
  const date   = new Date(scan.created_at).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });

  const scoreClass = score > 66 ? 'badge-danger' : score > 33 ? 'badge-warning' : 'badge-success';
  const srcIcon    = scan.input_source === 'url' ? '🔗' : scan.input_source === 'file' ? '📄' : '✏';

  return `
    <tr>
      <td>
        <span style="font-size:var(--text-sm);font-weight:600;color:var(--text-primary)">
          ${info.icon} ${info.label}
        </span>
      </td>
      <td style="max-width:300px">
        <div style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis" title="${escapeHtml(scan.input_preview).replace(/"/g, '&quot;')}">
          ${escapeHtml(scan.input_preview)}
        </div>
      </td>
      <td>
        <span class="badge badge-muted">${srcIcon} ${scan.input_source}</span>
      </td>
      <td>
        <span class="badge ${scoreClass}">${Math.round(score)}</span>
      </td>
      <td>
        <span style="font-size:var(--text-sm);font-weight:600;color:${score > 66 ? 'var(--danger)' : score > 33 ? 'var(--warning)' : 'var(--success)'}">
          ${scan.verdict}
        </span>
      </td>
      <td style="color:var(--text-muted);white-space:nowrap">${date}</td>
      <td style="text-align:right">
        <a href="/results?id=${scan.id}" class="btn btn-ghost btn-sm">👁 View</a>
        <button class="btn btn-ghost btn-sm" onclick="deleteScan(${scan.id})" style="color:var(--danger)">✕</button>
      </td>
    </tr>
  `;
}

async function viewScan(id) {
  try {
    const res = await fetch(`${API_BASE}/history/${id}`);
    if (!res.ok) throw new Error();
    const data = await res.json();
    sessionStorage.setItem('lastResult', JSON.stringify(data.full_result));
    window.location.href = '/results';
  } catch {
    showToast('Could not load scan details.', 'error');
  }
}

async function deleteScan(id) {
  if (!confirm('Are you sure you want to delete this scan?')) return;
  try {
    await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' });
    showToast('Scan deleted.', 'success');
    loadHistory();
  } catch {
    showToast('Could not delete scan.', 'error');
  }
}

document.addEventListener('DOMContentLoaded', loadHistory);
window.viewScan   = viewScan;
window.deleteScan = deleteScan;
window.loadHistory = loadHistory;
