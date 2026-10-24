// ==========================================
// ICONS (outline, 24px grid)
// ==========================================
const ICON_PATHS = {
    home: '<path d="M5 12l-2 0l9-9l9 9l-2 0"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/><path d="M10 21v-5a2 2 0 0 1 4 0v5"/>',
    history: '<path d="M12 8l0 4l2 2"/><path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5"/>',
    devices: '<rect x="13" y="8" width="8" height="12" rx="1"/><path d="M18 8v-3a1 1 0 0 0-1-1h-13a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h9"/><path d="M16 9h2"/>',
    settings: '<path d="M10.3 4.3c.4-1.8 3-1.8 3.4 0a1.7 1.7 0 0 0 2.6 1.1c1.5-.9 3.3.8 2.4 2.4a1.7 1.7 0 0 0 1 2.5c1.8.4 1.8 3 0 3.4a1.7 1.7 0 0 0-1 2.6c.9 1.5-.9 3.3-2.4 2.4a1.7 1.7 0 0 0-2.6 1c-.4 1.8-3 1.8-3.4 0a1.7 1.7 0 0 0-2.5-1c-1.6.9-3.3-.9-2.4-2.4a1.7 1.7 0 0 0-1.1-2.6c-1.8-.4-1.8-3 0-3.4a1.7 1.7 0 0 0 1.1-2.5c-.9-1.6.8-3.3 2.4-2.4a1.7 1.7 0 0 0 2.5-1.1z"/><circle cx="12" cy="12" r="3"/>',
    search: '<circle cx="10" cy="10" r="7"/><path d="M21 21l-6-6"/>',
    pause: '<rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/>',
    play: '<path d="M7 4v16l13-8z"/>',
    moon: '<path d="M12 3c.13 0 .26 0 .39 0a7.5 7.5 0 0 0 7.92 12.45a9 9 0 1 1-8.31-12.45z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M3 12h1m8-9v1m8 8h1m-9 8v1m-6.4-15.4l.7.7m12.1-.7l-.7.7m0 11.4l.7.7m-12.1-.7l-.7.7"/>',
    'arrow-up': '<path d="M12 5l0 14"/><path d="M18 11l-6-6"/><path d="M6 11l6-6"/>',
    'arrow-down': '<path d="M12 5l0 14"/><path d="M18 13l-6 6"/><path d="M6 13l6 6"/>',
    'file-upload': '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21h-10a2 2 0 0 1-2-2v-14a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6"/><path d="M9.5 13.5l2.5-2.5l2.5 2.5"/>',
    download: '<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/><path d="M7 11l5 5l5-5"/><path d="M12 4l0 12"/>',
    copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8v-2a2 2 0 0 0-2-2h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
    pin: '<path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5-1.5l1.5-4l4-4"/><path d="M9 15l-4.5 4.5"/><path d="M14.5 4l5.5 5.5"/>',
    folder: '<path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-14a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2"/>',
    trash: '<path d="M4 7l16 0"/><path d="M10 11l0 6"/><path d="M14 11l0 6"/><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-12"/><path d="M9 7v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    plus: '<path d="M12 5l0 14"/><path d="M5 12l14 0"/>',
    x: '<path d="M18 6l-12 12"/><path d="M6 6l12 12"/>',
    windows: '<path d="M4 6l7-1v7h-7z"/><path d="M13 4.7l7-1.2v8.5h-7z"/><path d="M4 13h7v7l-7-1z"/><path d="M13 13h7v8.5l-7-1.2z"/>',
    apple: '<path d="M8.3 7c-2.3 0-4.3 1.9-4.3 5c0 4 2.8 9 5 9c1.2 0 1.8-.6 3-.6s1.8.6 3 .6c2.2 0 5-5 5-9c0-3.1-2-5-4.2-5c-1.4 0-2.6.8-3.8.8s-2.4-.8-3.7-.8z"/><path d="M12 4a2 2 0 0 0 2-2"/>',
    folderdoc: '<path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-14a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2"/>',
};

function icon(name) {
    return `<span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICON_PATHS[name] || ''}</svg></span>`;
}

function hydrateIcons(root = document) {
    root.querySelectorAll('[data-icon]').forEach(el => { el.outerHTML = icon(el.dataset.icon); });
}

// ==========================================
// STATE
// ==========================================
const state = {
    history: [],
    stats: { sent_count: 0, sent_bytes: 0, received_count: 0, received_bytes: 0 },
    settings: { theme: 'dark', paused: false, notifications: true },
    peers: [],
    node: null,
    version: '',
    update: null,
    receiveDir: '',
    view: 'dashboard',
    dir: 'all',
    type: 'all',
    search: '',
};
let ws = null;

const $ = (id) => document.getElementById(id);

// ==========================================
// HELPERS
// ==========================================
function escapeHtml(str) {
    return String(str ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

function formatBytes(bytes) {
    if (!bytes) return '0 B';
    const units = ['B', 'KB', 'MB', 'GB'];
    let v = bytes, i = 0;
    while (v >= 1024 && i < units.length - 1) { v /= 1024; i++; }
    return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

function formatTime(ts) {
    const d = new Date(ts * 1000);
    const diff = (Date.now() - d.getTime()) / 1000;
    if (diff < 60) return 'právě teď';
    if (diff < 3600) return `před ${Math.floor(diff / 60)} min`;
    const time = d.toLocaleTimeString('cs-CZ', { hour: '2-digit', minute: '2-digit' });
    if (d.toDateString() === new Date().toDateString()) return `dnes ${time}`;
    return `${d.toLocaleDateString('cs-CZ', { day: 'numeric', month: 'numeric' })} ${time}`;
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    $('toasts').appendChild(toast);
    setTimeout(() => toast.remove(), 3200);
}

async function api(path, body) {
    const res = await fetch(path, {
        method: body === undefined ? 'GET' : 'POST',
        headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.message || `HTTP ${res.status}`);
    return data;
}

function osIcon(system) {
    return system === 'Darwin' ? 'apple' : 'windows';
}

// ==========================================
// WEBSOCKET
// ==========================================
function connect() {
    ws = new WebSocket(`ws://${location.host}/ws`);
    ws.onmessage = (e) => handleEvent(JSON.parse(e.data));
    ws.onclose = () => setTimeout(connect, 2000);
}

function handleEvent(data) {
    switch (data.event) {
        case 'init':
            Object.assign(state, {
                node: data.node, version: data.version, peers: data.peers || [], history: data.history || [],
                stats: data.stats, settings: data.settings, update: data.update, receiveDir: data.receive_dir,
            });
            renderAll();
            break;
        case 'clipboard_item':
            state.history = [data.item, ...state.history.filter(i => i.hash !== data.item.hash)];
            state.stats = data.stats || state.stats;
            renderStats();
            renderLists();
            if (data.from_remote) showToast(`Přijato z ${data.item.device}`);
            else if (data.item.metadata?.too_large) showToast('Soubory jsou větší než 25 MB, neodeslány.', 'error');
            break;
        case 'history':
            state.history = data.history;
            state.stats = data.stats || state.stats;
            renderStats();
            renderLists();
            break;
        case 'peers_updated':
            state.peers = data.peers || [];
            renderPeers();
            break;
        case 'settings':
            state.settings = data.settings;
            renderSettings();
            break;
        case 'update_status':
            state.update = data.update;
            renderUpdate();
            break;
    }
}

// ==========================================
// RENDERING
// ==========================================
function renderAll() {
    $('versionLink').textContent = `v${state.version}`;
    renderSettings();
    renderStats();
    renderPeers();
    renderLists();
    renderUpdate();
}

function renderStats() {
    const s = state.stats;
    $('statSent').textContent = s.sent_count;
    $('statSentBytes').textContent = `· ${formatBytes(s.sent_bytes)}`;
    $('statReceived').textContent = s.received_count;
    $('statReceivedBytes').textContent = `· ${formatBytes(s.received_bytes)}`;
}

function renderPeers() {
    const peers = state.peers;
    $('statPeers').textContent = peers.length;
    $('statPeersLabel').textContent = peers.length ? peers.map(p => p.name).join(', ') : 'Žádné připojené zařízení';

    const pill = $('statusPill');
    pill.classList.toggle('connected', peers.length > 0 && !state.settings.paused);
    pill.classList.toggle('paused', state.settings.paused);
    $('statusText').textContent = state.settings.paused
        ? 'Synchronizace pozastavena'
        : peers.length ? `Propojeno: ${peers.map(p => p.name).join(', ')}` : 'Hledám zařízení na Wi-Fi…';

    if (state.node) {
        $('ownDevice').innerHTML = deviceRow(state.node, 'Toto zařízení', 'var(--blue)');
    }
    $('peerList').innerHTML = peers.length
        ? peers.map(p => deviceRow(p, `${p.host}`, 'var(--lavender)', '<span class="tag received">Aktivní</span>')).join('')
        : '<p class="muted">Zatím nic. Spusť aplikaci na druhém zařízení ve stejné Wi-Fi a spáruj ho kódem vpravo.</p>';
}

function deviceRow(device, sub, color, extra = '') {
    return `
        <div class="device-row">
            <span class="device-badge" style="background:${color}">${icon(osIcon(device.system))}</span>
            <div><div class="device-name">${escapeHtml(device.name)}</div><div class="device-sub">${escapeHtml(sub)}</div></div>
            ${extra}
        </div>`;
}

function itemTitle(item) {
    if (item.type === 'text') return item.data.split('\n').find(l => l.trim()) || item.data;
    if (item.type === 'image') {
        const m = item.metadata || {};
        return m.filename || `Obrázek ${m.width || ''}×${m.height || ''}`;
    }
    const files = item.metadata?.files || [];
    if (files.length === 1) return files[0].name;
    return `${files[0]?.name || 'Soubory'} a ${files.length - 1} další`;
}

function itemThumb(item) {
    if (item.type === 'image') {
        const src = item.metadata?.thumb || item.data;
        return src ? `<div class="thumb image"><img src="data:image/png;base64,${src}" alt=""></div>` : '<div class="thumb image"><span class="doc">IMG</span></div>';
    }
    if (item.type === 'file') {
        const files = item.metadata?.files || [];
        if (files.length === 1 && files[0].is_dir) return `<div class="thumb file">${icon('folder')}</div>`;
        const ext = files.length === 1 ? (files[0].name.split('.').pop() || '').slice(0, 4).toUpperCase() : `${files.length}×`;
        return `<div class="thumb file"><span class="doc">${escapeHtml(ext || 'FILE')}</span></div>`;
    }
    return '<div class="thumb text"><span class="doc">TXT</span></div>';
}

function itemSize(item) {
    if (item.type === 'text') return `${item.data.length} znaků`;
    if (item.type === 'file') {
        const m = item.metadata || {};
        return `${m.count || 1} ${m.count === 1 ? 'soubor' : 'souborů'} · ${formatBytes(m.size_bytes)}`;
    }
    return formatBytes(item.metadata?.size_bytes);
}

function directionTag(item) {
    if (item.direction === 'received') return '<span class="tag received">Přijato</span>';
    if (item.metadata?.too_large) return '<span class="tag warn">Nad 25 MB</span>';
    if (!item.targets || !item.targets.length) return '<span class="tag local">Jen lokálně</span>';
    return '<span class="tag sent">Odesláno</span>';
}

function directionMeta(item) {
    if (item.direction === 'received') return `<span class="meta">${icon('arrow-down')}z ${escapeHtml(item.device)}</span>`;
    const targets = item.targets || [];
    return `<span class="meta">${icon('arrow-up')}${targets.length ? `do ${escapeHtml(targets.join(', '))}` : 'z tohoto zařízení'}</span>`;
}

function renderItem(item) {
    const isFile = item.type === 'file';
    const line = item.direction === 'received' ? 'received' : (item.targets?.length ? 'sent' : '');
    return `
        <div class="item" data-hash="${item.hash}">
            <div class="item-main">
                ${itemThumb(item)}
                <div class="item-body">
                    <div class="item-title-row">
                        <div class="item-title" title="${escapeHtml(itemTitle(item))}">${item.pinned ? `<span class="pin-mark">●</span> ` : ''}${escapeHtml(itemTitle(item))}</div>
                        <div class="item-tools">
                            ${isFile ? `<button class="tool" data-action="reveal" title="Zobrazit ve složce">${icon('folder')}</button>` : ''}
                            <button class="tool" data-action="delete" title="Smazat z historie">${icon('trash')}</button>
                        </div>
                    </div>
                    <div class="item-meta">
                        ${directionMeta(item)}
                        <span class="meta">${icon('clock')}${formatTime(item.timestamp)}</span>
                        <span class="meta">${escapeHtml(itemSize(item))}</span>
                        ${directionTag(item)}
                    </div>
                </div>
                ${line ? `<div class="item-line ${line}"></div>` : ''}
            </div>
            <button class="item-action" data-action="copy">${icon('copy')}Kopírovat</button>
            <button class="item-action secondary" data-action="pin">${icon('pin')}${item.pinned ? 'Odepnout' : 'Připnout'}</button>
        </div>`;
}

function matchesSearch(item, q) {
    if (!q) return true;
    const hay = item.type === 'text' ? item.data : [itemTitle(item), ...(item.metadata?.files || []).map(f => f.name)].join(' ');
    return `${hay} ${item.device || ''}`.toLowerCase().includes(q);
}

function sortedHistory() {
    return [...state.history].sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0) || b.timestamp - a.timestamp);
}

function renderList(el, items, emptyTitle, emptyText) {
    el.innerHTML = items.length
        ? items.map(renderItem).join('')
        : `<div class="empty"><h3>${emptyTitle}</h3><p>${emptyText}</p></div>`;
}

function renderLists() {
    const q = state.search.trim().toLowerCase();
    const all = sortedHistory().filter(i => matchesSearch(i, q));

    renderList($('recentList'), all.slice(0, 5),
        q ? 'Nic nenalezeno' : 'Schránka je připravená',
        q ? 'Zkus jiné hledání.' : 'Zkopíruj cokoliv (Ctrl+C / Cmd+C) a objeví se to tady i na druhém zařízení.');

    const filtered = all.filter(i =>
        (state.dir === 'all' || (state.dir === 'pinned' ? i.pinned : i.direction === state.dir)) &&
        (state.type === 'all' || i.type === state.type));
    renderList($('historyList'), filtered, 'Nic tu není', 'Pro tenhle filtr zatím žádné položky.');
}

function renderSettings() {
    const s = state.settings;
    document.documentElement.dataset.theme = s.theme;
    $('themeToggle').innerHTML = icon(s.theme === 'dark' ? 'moon' : 'sun');
    document.querySelectorAll('#themeSelect button').forEach(b => b.classList.toggle('active', b.dataset.value === s.theme));
    $('pauseToggle').innerHTML = icon(s.paused ? 'play' : 'pause');
    $('pauseToggle').classList.toggle('on', s.paused);
    $('pauseToggle').title = s.paused ? 'Obnovit synchronizaci' : 'Pozastavit synchronizaci';
    $('pausedSwitch').checked = s.paused;
    $('notificationsSwitch').checked = s.notifications;
    $('receiveDir').textContent = state.receiveDir || '–';
    renderPeers();
}

function renderUpdate() {
    const u = state.update;
    if (!u) return;
    const busy = u.state === 'downloading' || u.state === 'installing';
    $('updateDot').hidden = !u.available;
    $('updatePill').hidden = !u.available || busy;
    $('updatePillText').textContent = `Nová verze ${u.latest}`;
    $('updateProgress').hidden = !busy;
    $('updateProgressBar').style.width = `${Math.round(u.progress * 100)}%`;
    $('installUpdateBtn').hidden = !u.available || busy;
    $('installUpdateBtn').textContent = u.can_install ? 'Aktualizovat' : 'Stáhnout';
    $('checkUpdateBtn').hidden = busy;

    let text = `Verze ${u.current} je aktuální.`;
    if (u.state === 'downloading') text = `Stahuji verzi ${u.latest}… ${Math.round(u.progress * 100)} %`;
    else if (u.state === 'installing') text = `Instaluji verzi ${u.latest}, aplikace se za chvíli znovu spustí…`;
    else if (u.state === 'error') text = `Aktualizace se nezdařila: ${u.error}`;
    else if (u.available) text = `Je dostupná verze ${u.latest} (máš ${u.current}).`;
    $('updateStatusText').textContent = text;
}

// ==========================================
// NAVIGATION & FILTERS
// ==========================================
function showView(view) {
    state.view = view;
    document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.view === view));
    document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', v.dataset.view === view));
    $('composeBtn').hidden = view === 'settings';
    if (view === 'devices') loadPairingKey();
}

document.querySelectorAll('.nav-item').forEach(b => b.addEventListener('click', () => showView(b.dataset.view)));
document.querySelectorAll('[data-goto]').forEach(b => b.addEventListener('click', () => showView(b.dataset.goto)));
$('versionLink').addEventListener('click', () => showView('settings'));
$('updatePill').addEventListener('click', () => showView('settings'));

function bindSegmented(id, key) {
    $(id).addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        state[key] = btn.dataset.value;
        $(id).querySelectorAll('button').forEach(b => b.classList.toggle('active', b === btn));
        renderLists();
    });
}
bindSegmented('dirFilter', 'dir');
bindSegmented('typeFilter', 'type');

$('searchInput').addEventListener('input', (e) => {
    state.search = e.target.value;
    renderLists();
    if (state.search && state.view !== 'dashboard' && state.view !== 'history') showView('history');
});

// ==========================================
// ITEM ACTIONS
// ==========================================
document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-action]');
    const row = btn?.closest('.item');
    if (!btn || !row) return;
    const hash = row.dataset.hash;
    const item = state.history.find(i => i.hash === hash);
    try {
        switch (btn.dataset.action) {
            case 'copy':
                await api('/api/history/copy', { hash });
                showToast('Zkopírováno do schránky');
                break;
            case 'pin':
                await api('/api/history/pin', { hash, pinned: !item?.pinned });
                break;
            case 'delete':
                await api('/api/history/delete', { hash });
                break;
            case 'reveal':
                await api('/api/history/reveal', { hash });
                break;
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
});

$('clearHistoryBtn').addEventListener('click', async () => {
    if (confirm('Smazat z historie všechny nepřipnuté položky?')) await api('/api/history/clear', {});
});

// ==========================================
// FILE DROP & PASTE
// ==========================================
async function uploadFiles(files) {
    if (!files.length) return;
    const form = new FormData();
    [...files].forEach(f => form.append('files', f, f.name));
    try {
        const res = await fetch('/api/upload-files', { method: 'POST', body: form });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message);
        showToast(data.status === 'already_sent' ? 'Tyhle soubory už byly odeslány.' : `Odesláno: ${data.count} ${data.count === 1 ? 'soubor' : 'souborů'}`);
    } catch (err) {
        showToast(`Nepodařilo se odeslat: ${err.message}`, 'error');
    }
}

async function uploadImage(file) {
    const form = new FormData();
    form.append('file', file, file.name || 'screenshot.png');
    const res = await fetch('/api/upload', { method: 'POST', body: form });
    if (res.ok) showToast('Obrázek odeslán');
    else showToast('Obrázek se nepodařilo odeslat', 'error');
}

let dragDepth = 0;
window.addEventListener('dragenter', (e) => {
    if (![...e.dataTransfer.types].includes('Files')) return;
    dragDepth++;
    $('dropOverlay').hidden = false;
    $('dropCard').classList.add('dragover');
});
window.addEventListener('dragleave', () => {
    if (--dragDepth <= 0) {
        dragDepth = 0;
        $('dropOverlay').hidden = true;
        $('dropCard').classList.remove('dragover');
    }
});
window.addEventListener('dragover', (e) => e.preventDefault());
window.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDepth = 0;
    $('dropOverlay').hidden = true;
    $('dropCard').classList.remove('dragover');
    // A dropped folder arrives as a zero-byte entry without a type; copy folders with Ctrl+C instead
    const files = [...e.dataTransfer.files].filter(f => f.size > 0 || f.type);
    if (files.length < e.dataTransfer.files.length) showToast('Složky přetáhnout nejde – zkopíruj je přes Ctrl+C.', 'error');
    uploadFiles(files);
});

$('browseBtn').addEventListener('click', () => $('fileInput').click());
$('fileInput').addEventListener('change', (e) => { uploadFiles(e.target.files); e.target.value = ''; });

window.addEventListener('paste', (e) => {
    if (e.target.closest('input, textarea')) return;
    const files = [...(e.clipboardData?.files || [])];
    if (!files.length) return;
    e.preventDefault();
    // A screenshot pasted from the clipboard has no real file behind it; treat it as an image
    if (files.length === 1 && files[0].type.startsWith('image/') && /^image\.\w+$/.test(files[0].name)) uploadImage(files[0]);
    else uploadFiles(files);
});

// ==========================================
// COMPOSE TEXT
// ==========================================
function openCompose() {
    $('composeModal').hidden = false;
    $('composeText').focus();
}
function closeCompose() {
    $('composeModal').hidden = true;
}
function sendCompose() {
    const text = $('composeText').value;
    if (!text.trim() || ws?.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ action: 'push_text', text }));
    $('composeText').value = '';
    closeCompose();
    showToast('Odesláno do všech zařízení');
}
$('composeBtn').addEventListener('click', openCompose);
$('composeClose').addEventListener('click', closeCompose);
$('composeSend').addEventListener('click', sendCompose);
$('composeModal').addEventListener('click', (e) => { if (e.target.id === 'composeModal') closeCompose(); });
$('composeText').addEventListener('keydown', (e) => { if (e.ctrlKey && e.key === 'Enter') sendCompose(); });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeCompose(); });

// ==========================================
// SETTINGS
// ==========================================
async function saveSettings(changes) {
    try {
        state.settings = await api('/api/settings', changes);
        renderSettings();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

$('pauseToggle').addEventListener('click', () => saveSettings({ paused: !state.settings.paused }));
$('pausedSwitch').addEventListener('change', (e) => saveSettings({ paused: e.target.checked }));
$('notificationsSwitch').addEventListener('change', (e) => saveSettings({ notifications: e.target.checked }));
$('themeToggle').addEventListener('click', () => saveSettings({ theme: state.settings.theme === 'dark' ? 'light' : 'dark' }));
$('themeSelect').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) saveSettings({ theme: b.dataset.value }); });
$('openReceivedBtn').addEventListener('click', () => api('/api/open-received', {}));

$('checkUpdateBtn').addEventListener('click', async () => {
    $('updateStatusText').textContent = 'Kontroluji…';
    state.update = await api('/api/update?refresh=1');
    renderUpdate();
    if (!state.update.available) showToast('Máš nejnovější verzi');
});

$('installUpdateBtn').addEventListener('click', async () => {
    if (!state.update?.can_install) {
        api('/api/update/open', {});
        return;
    }
    try {
        await api('/api/update/install', {});
    } catch (err) {
        showToast('Aktualizaci se nepodařilo spustit', 'error');
    }
});

$('shutdownBtn').addEventListener('click', async () => {
    if (!confirm('Ukončit aplikaci? Synchronizace se zastaví.')) return;
    try { await api('/api/shutdown', {}); } catch (e) { /* the server exits right away */ }
});

// ==========================================
// PAIRING
// ==========================================
async function loadPairingKey() {
    $('ownPairingKey').value = (await api('/api/pairing')).key;
    $('ownPairingKey').type = 'password';
    $('togglePairingKey').textContent = 'Zobrazit';
}

$('togglePairingKey').addEventListener('click', () => {
    const show = $('ownPairingKey').type === 'password';
    $('ownPairingKey').type = show ? 'text' : 'password';
    $('togglePairingKey').textContent = show ? 'Skrýt' : 'Zobrazit';
});

$('copyPairingKey').addEventListener('click', async () => {
    await api('/api/pairing/copy', {});
    showToast('Kód zkopírován – vlož ho na druhém zařízení');
});

$('applyPairingKey').addEventListener('click', async () => {
    const key = $('newPairingKey').value.trim();
    if (!key) return;
    try {
        await api('/api/pairing', { key });
        $('newPairingKey').value = '';
        loadPairingKey();
        showToast('Spárováno – zařízení se do pár sekund objeví v seznamu');
    } catch (err) {
        showToast(`Kód nelze použít: ${err.message}`, 'error');
    }
});

// ==========================================
// INIT
// ==========================================
hydrateIcons();
connect();
setInterval(renderLists, 60000); // keeps relative times ("před 5 min") fresh
