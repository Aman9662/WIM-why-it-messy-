let activeTool = 'image-compress';
const files = {
  'image-compress': null,
  'image-resize': null,
  'pdf-compress': null
};

document.addEventListener('DOMContentLoaded', () => {
  // Handle URL hashes to auto-select tool
  const hash = window.location.hash.replace('#', '');
  if (['image-compress', 'image-resize', 'pdf-compress'].includes(hash)) {
    activeTool = hash;
  }
  
  // Setup tabs
  document.querySelectorAll('.tool-tab').forEach(tab => {
    tab.addEventListener('click', (e) => {
      document.querySelectorAll('.tool-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tool-panel').forEach(p => p.classList.remove('active'));
      
      const toolId = e.target.getAttribute('data-tool');
      activeTool = toolId;
      window.location.hash = toolId;
      
      e.target.classList.add('active');
      document.getElementById('panel-' + toolId).classList.add('active');
    });
  });

  // Activate the initially selected tab
  const activeTabEl = document.getElementById('tab-' + activeTool);
  if (activeTabEl) activeTabEl.click();

  window.addEventListener('hashchange', () => {
    const newHash = window.location.hash.replace('#', '');
    if (['image-compress', 'image-resize', 'pdf-compress'].includes(newHash)) {
      const el = document.getElementById('tab-' + newHash);
      if (el) el.click();
    }
  });

  // Setup file drops
  ['image-compress', 'image-resize', 'pdf-compress'].forEach(tool => {
    const dropArea = document.getElementById('drop-' + tool);
    const input = document.getElementById('file-' + tool);

    dropArea.addEventListener('click', () => input.click());

    dropArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropArea.classList.add('dragover');
    });

    dropArea.addEventListener('dragleave', () => dropArea.classList.remove('dragover'));

    dropArea.addEventListener('drop', (e) => {
      e.preventDefault();
      dropArea.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        handleFileSelect(tool, e.dataTransfer.files[0]);
      }
    });

    input.addEventListener('change', (e) => {
      if (e.target.files.length) {
        handleFileSelect(tool, e.target.files[0]);
      }
    });
  });
});

function handleFileSelect(tool, file) {
  files[tool] = file;
  
  document.getElementById('drop-' + tool).style.display = 'none';
  document.getElementById('options-' + tool).style.display = 'block';
  
  document.getElementById('name-' + tool).textContent = file.name;
  document.getElementById('size-' + tool).textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
}

function clearFile(tool) {
  files[tool] = null;
  document.getElementById('file-' + tool).value = '';
  document.getElementById('options-' + tool).style.display = 'none';
  document.getElementById('drop-' + tool).style.display = 'block';
}

async function processFile(endpoint, tool) {
  const file = files[tool];
  if (!file) {
    showToast('Please select a file first.', 'warning');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  // Append extra fields based on tool
  if (tool === 'image-compress') {
    const quality = document.getElementById('quality-image-compress').value;
    formData.append('quality', quality);
  } else if (tool === 'image-resize') {
    const width = document.getElementById('width-image-resize').value;
    const height = document.getElementById('height-image-resize').value;
    formData.append('width', width);
    formData.append('height', height);
  }

  const overlay = document.getElementById('processing-overlay');
  overlay.style.display = 'flex';

  try {
    const res = await fetch('/api/utils/' + endpoint, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      let errText = await res.text();
      try { errText = JSON.parse(errText).detail; } catch (e) {}
      throw new Error(errText || 'Processing failed');
    }

    // Get the filename from Content-Disposition header if possible
    let filename = 'processed_' + file.name;
    const disposition = res.headers.get('Content-Disposition');
    if (disposition && disposition.indexOf('filename=') !== -1) {
      filename = disposition.split('filename=')[1].replace(/"/g, '');
    } else if (tool === 'image-compress') {
       // compress always outputs JPG
       filename = 'compressed_' + file.name.split('.')[0] + '.jpg';
    }

    // Trigger download
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    
    showToast('File processed successfully!', 'success');

  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    overlay.style.display = 'none';
  }
}
