// State Management
let ws = null;
let currentFilter = 'all';
let historyItems = [];
let localNode = null;
let activePeers = [];

// DOM Elements
const localDeviceName = document.getElementById('localDeviceName');
const peersIndicator = document.getElementById('peersIndicator');
const peersStatusText = document.getElementById('peersStatusText');
const peersContainer = document.getElementById('peersContainer');
const activePeersCount = document.getElementById('activePeersCount');

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');

const manualTextInput = document.getElementById('manualTextInput');
const charCounter = document.getElementById('charCounter');
const sendTextBtn = document.getElementById('sendTextBtn');

const historyFeed = document.getElementById('historyFeed');
const filterBtns = document.querySelectorAll('.pill-btn');
const toastContainer = document.getElementById('toastContainer');

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${type === 'success' ? '✓' : 'ℹ'}</span> <div>${message}</div>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        toast.style.transition = 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
        setTimeout(() => toast.remove(), 300);
    }, 3200);
}

// ==========================================
// WEBSOCKET & REALTIME
// ==========================================
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('Connected to clipboard sync daemon WebSocket');
    };

    ws.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            handleWsEvent(data);
        } catch (err) {
            console.error('Error parsing WS message', err);
        }
    };

    ws.onclose = () => {
        console.log('WS disconnected. Reconnecting in 2s...');
        setTimeout(connectWebSocket, 2000);
    };
}

function handleWsEvent(data) {
    if (data.event === 'init') {
        localNode = data.node;
        activePeers = data.peers || [];
        historyItems = data.history || [];
        updateHeaderStatus();
        updatePeersList();
        renderHistory();
        renderUpdate(data.update);
    } else if (data.event === 'update_status') {
        renderUpdate(data.update);
    } else if (data.event === 'peers_updated') {
        activePeers = data.peers || [];
        updateHeaderStatus();
        updatePeersList();
    } else if (data.event === 'clipboard_item') {
        const item = data.item;
        // Deduplicate in UI: remove any older identical entry and move fresh one to top
        historyItems = historyItems.filter(i => i.hash !== item.hash);
        historyItems.unshift(item);
        if (historyItems.length > 50) historyItems.pop();
        renderHistory();
        if (data.from_remote) {
            const kind = item.type === 'text' ? 'text' : (item.type === 'file' ? 'soubory (uloženo do Stažené/Universal Clipboard)' : 'obrázek');
            showToast(`Příchozí ${kind} z druhého zařízení synchronizován!`, 'success');
        } else if (item.metadata?.too_large) {
            showToast(`Soubory jsou větší než 25 MB, na druhé zařízení se neposílají.`, 'error');
        }
    }
}

// ==========================================
// UI STATUS UPDATERS
// ==========================================
function updateHeaderStatus() {
    if (localNode) {
        localDeviceName.textContent = `${localNode.name} (${localNode.system})`;
    }

    if (activePeers.length > 0) {
        peersIndicator.className = 'radar-ping connected';
        const names = activePeers.map(p => `${p.name} [${p.system}]`).join(', ');
        peersStatusText.textContent = `Propojeno: ${names}`;
    } else {
        peersIndicator.className = 'radar-ping searching';
        peersStatusText.textContent = 'Hledám zařízení na Wi-Fi...';
    }
}

function updatePeersList() {
    activePeersCount.textContent = activePeers.length;
    if (activePeers.length === 0) {
        peersContainer.innerHTML = `
            <div class="empty-peers-notice">
                <span class="empty-peers-icon">🔍</span>
                <p>Čekám na spuštění na MacBooku... Zařízení se na stejné Wi-Fi propojí automaticky.</p>
            </div>
        `;
        return;
    }

    peersContainer.innerHTML = activePeers.map(peer => {
        const osIcon = peer.system === 'Darwin' ? '🍎' : (peer.system === 'Windows' ? '🪟' : '🐧');
        return `
            <div class="peer-row">
                <div class="peer-info">
                    <span class="peer-os-icon">${osIcon}</span>
                    <div>
                        <div class="peer-name">${escapeHtml(peer.name)}</div>
                        <div class="peer-ip">${peer.host}:${peer.port}</div>
                    </div>
                </div>
                <span class="peer-status-pill">Aktivní</span>
            </div>
        `;
    }).join('');
}

// ==========================================
// HISTORY RENDERING & FILTERING
// ==========================================
function renderHistory() {
    const filtered = historyItems.filter(item => {
        if (currentFilter === 'all') return true;
        return item.type === currentFilter;
    });

    if (filtered.length === 0) {
        historyFeed.innerHTML = `
            <div class="feed-empty-state">
                <div class="empty-halo">📋</div>
                <h3>Schránka je připravena</h3>
                <p>Zkopíruj cokoliv (<kbd>Ctrl+C</kbd> na Win / <kbd>Cmd+C</kbd> na Macu) a obsah se okamžitě objeví zde i na druhém zařízení.</p>
            </div>
        `;
        return;
    }

    historyFeed.innerHTML = filtered.map(item => {
        const timeStr = formatTimestamp(item.timestamp);
        if (item.type === 'text') {
            const previewText = escapeHtml(item.data);
            return `
                <div class="history-card" data-hash="${item.hash}">
                    <div class="history-card-top">
                        <div class="history-meta-tags">
                            <span class="type-pill text">Text / Kód</span>
                            <span class="time-stamp">${timeStr}</span>
                        </div>
                        <button class="copy-action-btn" onclick="copyTextItem('${item.hash}', this)">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Kopírovat</span>
                        </button>
                    </div>
                    <pre class="history-content-text">${previewText}</pre>
                </div>
            `;
        } else if (item.type === 'file') {
            const files = (item.metadata || {}).files || [];
            const rows = files.map(f => `
                <li class="file-row">
                    <span class="file-icon">${f.is_dir ? '📁' : '📄'}</span>
                    <span class="file-name">${escapeHtml(f.name)}</span>
                    <span class="file-size">${f.is_dir ? 'složka' : formatBytes(f.size_bytes)}</span>
                    <span class="file-path">${escapeHtml(f.path)}</span>
                </li>
            `).join('');
            return `
                <div class="history-card" data-hash="${item.hash}">
                    <div class="history-card-top">
                        <div class="history-meta-tags">
                            <span class="type-pill file">Soubory (${files.length})</span>
                            ${item.metadata?.too_large ? '<span class="type-pill too-large">Nad 25 MB, neodesláno</span>' : ''}
                            <span class="time-stamp">${timeStr}</span>
                        </div>
                        <button class="copy-action-btn" onclick="copyTextItem('${item.hash}', this)">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                            <span>Kopírovat cesty</span>
                        </button>
                    </div>
                    <ul class="history-file-list">${rows}</ul>
                </div>
            `;
        } else if (item.type === 'image') {
            const meta = item.metadata || {};
            const metaText = meta.width ? `${meta.width} × ${meta.height} px • ${(meta.size_bytes / 1024).toFixed(1)} KB` : 'Obrázek';
            return `
                <div class="history-card" data-hash="${item.hash}">
                    <div class="history-card-top">
                        <div class="history-meta-tags">
                            <span class="type-pill image">Screenshot / Obrázek</span>
                            <span class="time-stamp">${timeStr}</span>
                        </div>
                        <div class="history-actions-group" style="display: flex; gap: 6px;">
                            <button class="copy-action-btn" onclick="copyImageItem('${item.hash}', this)">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                <span>Kopírovat</span>
                            </button>
                            <button class="copy-action-btn" onclick="downloadImageItem('${item.hash}')" title="Uložit do složky Stažené soubory">
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                                <span>Stáhnout</span>
                            </button>
                        </div>
                    </div>
                    <div class="history-image-wrapper">
                        <img src="data:image/png;base64,${item.data}" class="history-image-tag" alt="Clipboard Preview" />
                        <span class="image-spec">${metaText}</span>
                    </div>
                </div>
            `;
        }
        return '';
    }).join('');
}

function formatTimestamp(ts) {
    if (!ts) return '';
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function formatBytes(bytes) {
    if (!bytes) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let i = 0;
    let v = bytes;
    while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
    return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// ==========================================
// CARD COPY ACTIONS
// ==========================================
window.copyTextItem = function(hash, btn) {
    const item = historyItems.find(i => i.hash === hash);
    if (!item) return;
    navigator.clipboard.writeText(item.data).then(() => {
        if (btn) {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<span>✓ Zkopírováno</span>`;
            setTimeout(() => { btn.innerHTML = originalHTML; }, 1800);
        }
        showToast('Text byl zkopírován do schránky!', 'success');
    }).catch(err => {
        showToast('Chyba schránky: ' + err, 'info');
    });
};

window.copyImageItem = async function(hash, btn) {
    const item = historyItems.find(i => i.hash === hash);
    if (!item) return;
    try {
        const res = await fetch(`data:image/png;base64,${item.data}`);
        const blob = await res.blob();
        await navigator.clipboard.write([
            new ClipboardItem({ 'image/png': blob })
        ]);
        if (btn) {
            const originalHTML = btn.innerHTML;
            btn.innerHTML = `<span>✓ Zkopírováno</span>`;
            setTimeout(() => { btn.innerHTML = originalHTML; }, 1800);
        }
        showToast('Obrázek byl zkopírován do schránky!', 'success');
    } catch (err) {
        showToast('Chyba schránky: ' + err, 'info');
    }
};

window.downloadImageItem = function(hash) {
    const item = historyItems.find(i => i.hash === hash);
    if (!item) return;
    const a = document.createElement('a');
    a.href = `data:image/png;base64,${item.data}`;
    const filename = item.metadata?.filename || `clipboard_${new Date(item.timestamp * 1000).toISOString().slice(0, 19).replace(/[-:T]/g, '_')}.png`;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast(`Obrázek "${filename}" uložen do stažených souborů!`, 'success');
};

// ==========================================
// FILTER BUTTONS
// ==========================================
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderHistory();
    });
});

// ==========================================
// TEXT INPUT & SEND
// ==========================================
manualTextInput.addEventListener('input', () => {
    charCounter.textContent = `${manualTextInput.value.length} znaků`;
});

manualTextInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        e.preventDefault();
        sendManualText();
    }
});

sendTextBtn.addEventListener('click', sendManualText);

function sendManualText() {
    const text = manualTextInput.value.trim();
    if (!text) return;

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'push_text', text: text }));
        manualTextInput.value = '';
        charCounter.textContent = '0 znaků';
        showToast('Odesláno do všech zařízení!', 'success');
    } else {
        fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'text', data: text, metadata: { source: 'dashboard' } })
        }).then(() => {
            manualTextInput.value = '';
            charCounter.textContent = '0 znaků';
            showToast('Odesláno do všech zařízení!', 'success');
        });
    }
}

// ==========================================
// DRAG & DROP & FILE UPLOADS
// ==========================================
browseBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        uploadImageFile(e.target.files[0]);
    }
});

dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) {
        uploadImageFile(e.dataTransfer.files[0]);
    }
});

window.addEventListener('paste', (e) => {
    if (e.clipboardData && e.clipboardData.files.length > 0) {
        const file = e.clipboardData.files[0];
        if (file.type.startsWith('image/')) {
            uploadImageFile(file);
        }
    }
});

function uploadImageFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Vyber prosím obrázek (PNG, JPG, WebP)', 'info');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'ok') {
            showToast(`Obrázek "${file.name}" byl synchronizován!`, 'success');
        } else {
            showToast(`Chyba: ${data.message}`, 'info');
        }
    })
    .catch(err => {
        showToast(`Chyba při nahrávání: ${err}`, 'info');
    });
}

// ==========================================
// SHUTDOWN APPLICATION & SERVER
// ==========================================
const shutdownBtn = document.getElementById('shutdownBtn');
if (shutdownBtn) {
    shutdownBtn.addEventListener('click', async () => {
        if (!confirm('Opravdu chcete ukončit aplikaci a synchronizační server?')) {
            return;
        }
        shutdownBtn.disabled = true;
        shutdownBtn.innerHTML = `
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="spin">
                <line x1="12" y1="2" x2="12" y2="6"></line>
                <line x1="12" y1="18" x2="12" y2="22"></line>
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                <line x1="2" y1="12" x2="6" y2="12"></line>
                <line x1="18" y1="12" x2="22" y2="12"></line>
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
            </svg>
            <span>Ukončuji...</span>
        `;
        showToast('Ukončuji synchronizační server...', 'info');
        try {
            await fetch('/api/shutdown', { method: 'POST' });
        } catch (e) {
            // Expected if server closes instantly
        }
        setTimeout(() => {
            window.close();
            // If window.close() is prevented by browser policies, show exit screen
            document.body.innerHTML = `
                <div style="display:flex;height:100vh;align-items:center;justify-content:center;flex-direction:column;gap:16px;color:#94a3b8;font-family:'Plus Jakarta Sans',sans-serif;background:#080a0f;text-align:center;padding:20px;">
                    <div style="width:64px;height:64px;border-radius:50%;background:rgba(244,63,94,0.12);display:flex;align-items:center;justify-content:center;color:#f43f5e;font-size:24px;border:1px solid rgba(244,63,94,0.3);">⏻</div>
                    <h2 style="color:#f8fafc;margin:0;font-size:1.5rem;">Aplikace a server byly ukončeny</h2>
                    <p style="margin:0;max-width:400px;font-size:0.95rem;line-height:1.5;">Proces na pozadí byl bezpečně zastaven. Nyní můžete toto okno zavřít.</p>
                </div>
            `;
        }, 500);
    });
}

// ==========================================
// UPDATES
// ==========================================
const versionTag = document.getElementById('versionTag');
const updateBanner = document.getElementById('updateBanner');
const updateBannerText = document.getElementById('updateBannerText');
const updateBtn = document.getElementById('updateBtn');
const updateProgress = document.getElementById('updateProgress');
const updateProgressBar = document.getElementById('updateProgressBar');
let updateInfo = null;

function renderUpdate(update) {
    if (!update) return;
    updateInfo = update;
    versionTag.textContent = `v${update.current}`;
    updateBanner.hidden = !update.available;
    if (!update.available) return;

    const busy = update.state === 'downloading' || update.state === 'installing';
    updateProgress.hidden = !busy;
    updateBtn.hidden = busy;
    updateProgressBar.style.width = `${Math.round(update.progress * 100)}%`;

    if (update.state === 'downloading') {
        updateBannerText.textContent = `Stahuji verzi ${update.latest}... ${Math.round(update.progress * 100)} %`;
    } else if (update.state === 'installing') {
        updateBannerText.textContent = `Instaluji verzi ${update.latest}, aplikace se za chvíli znovu spustí...`;
    } else if (update.state === 'error') {
        updateBannerText.textContent = `Aktualizace se nezdařila: ${update.error}`;
        updateBtn.textContent = 'Zkusit znovu';
    } else {
        updateBannerText.textContent = `Je dostupná nová verze ${update.latest} (máš ${update.current}).`;
        updateBtn.textContent = update.can_install ? 'Aktualizovat' : 'Stáhnout';
    }
}

updateBtn.addEventListener('click', async () => {
    if (!updateInfo) return;
    if (!updateInfo.can_install) {
        fetch('/api/update/open', { method: 'POST' });
        return;
    }
    updateBtn.hidden = true;
    const res = await fetch('/api/update/install', { method: 'POST' });
    if (!res.ok) {
        updateBtn.hidden = false;
        showToast('Aktualizaci se nepodařilo spustit.', 'error');
    }
});

// ==========================================
// PAIRING
// ==========================================
const pairingModal = document.getElementById('pairingModal');
const ownPairingKey = document.getElementById('ownPairingKey');
const newPairingKey = document.getElementById('newPairingKey');
const togglePairingKey = document.getElementById('togglePairingKey');

async function openPairing() {
    const res = await fetch('/api/pairing');
    ownPairingKey.value = (await res.json()).key;
    ownPairingKey.type = 'password';
    togglePairingKey.textContent = 'Zobrazit';
    newPairingKey.value = '';
    pairingModal.hidden = false;
}

function closePairing() {
    pairingModal.hidden = true;
    ownPairingKey.value = '';
}

document.getElementById('pairingBtn').addEventListener('click', openPairing);
document.getElementById('pairingClose').addEventListener('click', closePairing);
pairingModal.addEventListener('click', (e) => { if (e.target === pairingModal) closePairing(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && !pairingModal.hidden) closePairing(); });

togglePairingKey.addEventListener('click', () => {
    const show = ownPairingKey.type === 'password';
    ownPairingKey.type = show ? 'text' : 'password';
    togglePairingKey.textContent = show ? 'Skrýt' : 'Zobrazit';
});

document.getElementById('copyPairingKey').addEventListener('click', async () => {
    await fetch('/api/pairing/copy', { method: 'POST' });
    showToast('Párovací kód zkopírován. Vlož ho na druhém zařízení.', 'success');
});

document.getElementById('applyPairingKey').addEventListener('click', async () => {
    const key = newPairingKey.value.trim();
    if (!key) return;
    const res = await fetch('/api/pairing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key })
    });
    const data = await res.json();
    if (res.ok) {
        closePairing();
        showToast('Spárováno! Zařízení se do pár sekund objeví v seznamu.', 'success');
    } else {
        showToast(`Kód nelze použít: ${data.message}`, 'error');
    }
});

// Initialize on load
connectWebSocket();

// Periodic fallback polling to keep status & peers 100% in sync
setInterval(async () => {
    try {
        const res = await fetch('/api/status');
        if (res.ok) {
            const data = await res.json();
            localNode = data.node;
            activePeers = data.peers || [];
            updateHeaderStatus();
            updatePeersList();
        }
    } catch (e) {}
}, 2500);
