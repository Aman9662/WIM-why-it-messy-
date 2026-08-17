/* ================================================
   DETECT.JS — Detection form logic
   ================================================ */

const API_BASE = '/api';

const DETECTION_TOOLS = [
  { id: 'ai_content',     icon: '🤖', label: 'AI Content',        desc: 'Detect AI-generated text' },
  { id: 'plagiarism',     icon: '📋', label: 'Plagiarism',         desc: 'Check originality & idea copying' },
  { id: 'fake_news',      icon: '📰', label: 'Fake News',          desc: 'Verify news credibility' },
  { id: 'fake_review',    icon: '⭐', label: 'Fake Review',        desc: 'Spot bot/fake reviews' },
  { id: 'fake_profile',   icon: '👤', label: 'Fake Profile',       desc: 'Detect fake social profiles' },
  { id: 'fake_job',       icon: '💼', label: 'Fake Job Posting',   desc: 'Identify scam job offers' },
  { id: 'phishing',       icon: '🎣', label: 'Phishing Email',     desc: 'Detect phishing attempts' },
  { id: 'code_plagiarism',icon: '⟨⟩', label: 'Code Plagiarism',   desc: 'Check copied or AI code' },
];

let activeTool    = DETECTION_TOOLS[0];
let activeTab     = 'text';
let selectedFile  = null;
let isAnalyzing   = false;

function initDetectPage() {
  renderSidebar();
  renderInputPanel();
  bindTabEvents();
}

function renderSidebar() {
  const sidebar = document.getElementById('detect-sidebar');
  if (!sidebar) return;

  sidebar.innerHTML = `
    <div class="detect-sidebar-label">Detection Tools</div>
    ${DETECTION_TOOLS.map(tool => `
      <button class="detect-tool-btn ${tool.id === activeTool.id ? 'active' : ''}"
              id="tool-${tool.id}"
              onclick="selectTool('${tool.id}')">
        <div class="tool-icon">${tool.icon}</div>
        <div>
          <div style="font-weight:600;font-size:var(--text-sm);color:var(--text-primary)">${tool.label}</div>
          <div style="font-size:10px;color:var(--text-muted);margin-top:1px">${tool.desc}</div>
        </div>
      </button>
    `).join('')}
  `;
}

function selectTool(toolId) {
  activeTool = DETECTION_TOOLS.find(t => t.id === toolId);
  document.querySelectorAll('.detect-tool-btn').forEach(btn => btn.classList.remove('active'));
  const btn = document.getElementById(`tool-${toolId}`);
  if (btn) btn.classList.add('active');

  const titleEl = document.getElementById('detect-tool-title');
  const descEl  = document.getElementById('detect-tool-desc');
  if (titleEl) titleEl.textContent = activeTool.label + ' Detection';
  if (descEl)  descEl.textContent  = activeTool.desc;

  const placeholder = getPlaceholder(toolId);
  const textarea = document.getElementById('text-input');
  if (textarea) textarea.placeholder = placeholder;

  const labelEl = document.getElementById('current-tool-label');
  if (labelEl) labelEl.innerHTML = `${activeTool.icon} ${activeTool.label} Detection`;
}

function getPlaceholder(toolId) {
  const map = {
    ai_content:      'Paste your text here to check how much was written by AI...',
    plagiarism:      'Paste your project idea, report, or proposal here to check for originality...',
    fake_news:       'Paste the news article or claim you want to fact-check...',
    fake_review:     'Paste the product review(s) you want to analyze...',
    fake_profile:    'Paste the social media profile bio or description here...',
    fake_job:        'Paste the job posting description to check for scam indicators...',
    phishing:        'Paste the email or message content to check for phishing...',
    code_plagiarism: 'Paste your code here to check for plagiarism or AI generation...',
  };
  return map[toolId] || 'Enter content to analyze...';
}

function renderInputPanel() {
  const panel = document.getElementById('detect-panel');
  if (!panel) return;

  panel.innerHTML = `
    <div style="position:relative">
      <div class="input-tabs" role="tablist">
        <button class="input-tab active" id="tab-text"   onclick="switchTab('text')" role="tab" aria-selected="true">
          ✏ Text Input
        </button>
        <button class="input-tab"        id="tab-url"    onclick="switchTab('url')" role="tab" aria-selected="false">
          🔗 URL
        </button>
        <button class="input-tab"        id="tab-file"   onclick="switchTab('file')" role="tab" aria-selected="false">
          📁 File Upload
        </button>
      </div>

      <div class="detect-panel-body">
        <!-- Text Tab -->
        <div class="input-section active" id="section-text">
          <div class="form-group">
            <label class="form-label" for="text-input">Content to Analyze</label>
            <textarea class="form-textarea"
                      id="text-input"
                      rows="8"
                      placeholder="${getPlaceholder(activeTool.id)}"></textarea>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;margin-top:var(--space-sm)">
            <span style="font-size:var(--text-xs);color:var(--text-muted)" id="char-count">0 characters</span>
            <button class="btn btn-ghost btn-sm" onclick="clearInput()">Clear</button>
          </div>
        </div>

        <!-- URL Tab -->
        <div class="input-section" id="section-url">
          <div class="form-group">
            <label class="form-label" for="url-input">Website or Article URL</label>
            <input class="form-input"
                   id="url-input"
                   type="url"
                   placeholder="https://example.com/article" />
          </div>
          <p style="font-size:var(--text-xs);color:var(--text-muted);margin-top:var(--space-sm)">
            We'll fetch and analyze the content of this URL in real-time.
          </p>
        </div>

        <!-- File Tab -->
        <div class="input-section" id="section-file">
          <div class="file-drop-zone" id="file-drop-zone">
            <div class="drop-icon">📄</div>
            <h3>Drop your file here</h3>
            <p>Supports .txt, .pdf, .docx files</p>
            <input type="file" id="file-input" accept=".txt,.pdf,.docx" onchange="handleFileSelect(event)" />
          </div>
          <div class="file-selected" id="file-selected" style="display:none">
            <span style="font-size:1.2rem">📄</span>
            <div style="flex:1">
              <div style="font-size:var(--text-sm);font-weight:600;color:var(--text-primary)" id="file-name"></div>
              <div style="font-size:var(--text-xs);color:var(--text-muted)" id="file-size"></div>
            </div>
            <button class="btn btn-ghost btn-sm" onclick="clearFile()">✕ Remove</button>
          </div>
        </div>
      </div>

      <div class="analyze-actions">
        <span style="font-size:var(--text-xs);color:var(--text-muted)">
          Using: <strong style="color:var(--text-secondary)" id="current-tool-label">${activeTool.icon} ${activeTool.label} Detection</strong>
        </span>
        <button class="btn btn-primary" id="analyze-btn" onclick="runAnalysis()">
          <span>Analyze Now</span>
        </button>
      </div>

      <!-- Scanning Overlay -->
      <div class="scanning-overlay" id="scanning-overlay">
        <div class="scanning-icon">⬡</div>
        <div class="scanning-text">
          <h3>Analyzing content...</h3>
          <div class="loading-dots mt-sm" style="justify-content:center">
            <span></span><span></span><span></span>
          </div>
          <p style="margin-top:var(--space-sm)">Powered by death</p>
        </div>
      </div>
    </div>
  `;

  // Char count
  const textarea = document.getElementById('text-input');
  if (textarea) {
    textarea.addEventListener('input', () => {
      const el = document.getElementById('char-count');
      if (el) el.textContent = textarea.value.length + ' characters';
    });
  }

  // File drag events
  const dropZone = document.getElementById('file-drop-zone');
  if (dropZone) {
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file) setFile(file);
    });
  }
}

function switchTab(tab) {
  activeTab = tab;
  document.querySelectorAll('.input-tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.input-section').forEach(s => s.classList.remove('active'));
  const tabEl = document.getElementById(`tab-${tab}`);
  const secEl = document.getElementById(`section-${tab}`);
  if (tabEl) tabEl.classList.add('active');
  if (secEl) secEl.classList.add('active');
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) setFile(file);
}

function setFile(file) {
  selectedFile = file;
  const nameEl = document.getElementById('file-name');
  const sizeEl = document.getElementById('file-size');
  const selectedEl = document.getElementById('file-selected');
  const dropEl = document.getElementById('file-drop-zone');

  if (nameEl) nameEl.textContent = file.name;
  if (sizeEl) sizeEl.textContent = formatFileSize(file.size);
  if (selectedEl) selectedEl.style.display = 'flex';
  if (dropEl) dropEl.style.display = 'none';
}

function clearFile() {
  selectedFile = null;
  const selectedEl = document.getElementById('file-selected');
  const dropEl = document.getElementById('file-drop-zone');
  if (selectedEl) selectedEl.style.display = 'none';
  if (dropEl) dropEl.style.display = 'block';
  const fileInput = document.getElementById('file-input');
  if (fileInput) fileInput.value = '';
}

function clearInput() {
  const textarea = document.getElementById('text-input');
  if (textarea) {
    textarea.value = '';
    const el = document.getElementById('char-count');
    if (el) el.textContent = '0 characters';
  }
  const urlInput = document.getElementById('url-input');
  if (urlInput) {
    urlInput.value = '';
  }
  if (selectedFile) {
    clearFile();
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function bindTabEvents() {}

async function runAnalysis() {
  if (isAnalyzing) return;

  const overlay = document.getElementById('scanning-overlay');
  const analyzeBtn = document.getElementById('analyze-btn');

  try {
    isAnalyzing = true;
    if (overlay) overlay.classList.add('active');
    if (analyzeBtn) analyzeBtn.disabled = true;

    let result;

    if (activeTab === 'text') {
      const text = document.getElementById('text-input')?.value?.trim();
      if (!text || text.length < 20) {
        throw new Error('Please enter at least 20 characters to analyze.');
      }
      const formData = new FormData();
      formData.append('text', text);
      formData.append('detection_type', activeTool.id);
      const res = await fetch(`${API_BASE}/detect/text`, { method: 'POST', body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Analysis failed.');
      }
      result = await res.json();

    } else if (activeTab === 'url') {
      const url = document.getElementById('url-input')?.value?.trim();
      if (!url) throw new Error('Please enter a URL to analyze.');
      const formData = new FormData();
      formData.append('url', url);
      formData.append('detection_type', activeTool.id);
      const res = await fetch(`${API_BASE}/detect/url`, { method: 'POST', body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Could not fetch URL.');
      }
      result = await res.json();

    } else if (activeTab === 'file') {
      if (!selectedFile) throw new Error('Please select a file to analyze.');
      if (selectedFile.size > 10 * 1024 * 1024) {
        throw new Error('File too large. Maximum size is 10MB.');
      }
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('detection_type', activeTool.id);
      const res = await fetch(`${API_BASE}/detect/file`, { method: 'POST', body: formData });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'File analysis failed.');
      }
      result = await res.json();
    }

    // Navigate to results page using scan ID
    window.location.href = '/results?id=' + result.id;

  } catch (err) {
    showToast(err.message || 'An error occurred. Please try again.', 'error');
  } finally {
    isAnalyzing = false;
    if (overlay) overlay.classList.remove('active');
    if (analyzeBtn) analyzeBtn.disabled = false;
  }
}

document.addEventListener('DOMContentLoaded', initDetectPage);
window.selectTool    = selectTool;
window.switchTab     = switchTab;
window.handleFileSelect = handleFileSelect;
window.clearFile     = clearFile;
window.clearInput    = clearInput;
window.runAnalysis   = runAnalysis;
