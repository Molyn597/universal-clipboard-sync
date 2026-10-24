// ==========================================
// ICONS (outline, 24px grid)
// ==========================================
const ICON_PATHS = {
    settings: '<path d="M10.3 4.3c.4-1.8 3-1.8 3.4 0a1.7 1.7 0 0 0 2.6 1.1c1.5-.9 3.3.8 2.4 2.4a1.7 1.7 0 0 0 1 2.5c1.8.4 1.8 3 0 3.4a1.7 1.7 0 0 0-1 2.6c.9 1.5-.9 3.3-2.4 2.4a1.7 1.7 0 0 0-2.6 1c-.4 1.8-3 1.8-3.4 0a1.7 1.7 0 0 0-2.5-1c-1.6.9-3.3-.9-2.4-2.4a1.7 1.7 0 0 0-1.1-2.6c-1.8-.4-1.8-3 0-3.4a1.7 1.7 0 0 0 1.1-2.5c-.9-1.6.8-3.3 2.4-2.4a1.7 1.7 0 0 0 2.5-1.1z"/><circle cx="12" cy="12" r="3"/>',
    search: '<circle cx="10" cy="10" r="7"/><path d="M21 21l-6-6"/>',
    pause: '<rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/>',
    play: '<path d="M7 4v16l13-8z"/>',
    'arrow-up': '<path d="M12 5l0 14"/><path d="M18 11l-6-6"/><path d="M6 11l6-6"/>',
    'arrow-down': '<path d="M12 5l0 14"/><path d="M18 13l-6 6"/><path d="M6 13l6 6"/>',
    'file-upload': '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21h-10a2 2 0 0 1-2-2v-14a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M12 11v6"/><path d="M9.5 13.5l2.5-2.5l2.5 2.5"/>',
    download: '<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/><path d="M7 11l5 5l5-5"/><path d="M12 4l0 12"/>',
    copy: '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8v-2a2 2 0 0 0-2-2h-8a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
    pin: '<path d="M15 4.5l-4 4l-4 1.5l-1.5 1.5l7 7l1.5-1.5l1.5-4l4-4"/><path d="M9 15l-4.5 4.5"/><path d="M14.5 4l5.5 5.5"/>',
    folder: '<path d="M5 4h4l3 3h7a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-14a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2"/>',
    trash: '<path d="M4 7l16 0"/><path d="M10 11l0 6"/><path d="M14 11l0 6"/><path d="M5 7l1 12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-12"/><path d="M9 7v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"/>',
    open: '<path d="M12 6h-6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/><path d="M11 13l9-9"/><path d="M15 4h5v5"/>',
    x: '<path d="M18 6l-12 12"/><path d="M6 6l12 12"/>',
    minus: '<path d="M5 12l14 0"/>',
    square: '<rect x="5" y="5" width="14" height="14" rx="2"/>',
    moon: '<path d="M12 3c.13 0 .26 0 .39 0a7.5 7.5 0 0 0 7.92 12.45a9 9 0 1 1-8.31-12.45z"/>',
    sun: '<circle cx="12" cy="12" r="4"/><path d="M3 12h1m8-9v1m8 8h1m-9 8v1m-6.4-15.4l.7.7m12.1-.7l-.7.7m0 11.4l.7.7m-12.1-.7l-.7.7"/>',
    'chevron-left': '<path d="M15 6l-6 6l6 6"/>',
    paperclip: '<path d="M15 7l-6.5 6.5a1.5 1.5 0 0 0 3 3l6.5-6.5a3 3 0 0 0-6-6l-6.5 6.5a4.5 4.5 0 0 0 9 9l6.5-6.5"/>',
    windows: '<path d="M4 6l7-1v7h-7z"/><path d="M13 4.7l7-1.2v8.5h-7z"/><path d="M4 13h7v7l-7-1z"/><path d="M13 13h7v8.5l-7-1.2z"/>',
    apple: '<path d="M8.3 7c-2.3 0-4.3 1.9-4.3 5c0 4 2.8 9 5 9c1.2 0 1.8-.6 3-.6s1.8.6 3 .6c2.2 0 5-5 5-9c0-3.1-2-5-4.2-5c-1.4 0-2.6.8-3.8.8s-2.4-.8-3.7-.8z"/><path d="M12 4a2 2 0 0 0 2-2"/>',
    devices: '<rect x="13" y="8" width="8" height="12" rx="1"/><path d="M18 8v-3a1 1 0 0 0-1-1h-13a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h9"/>',
    doc: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21h-10a2 2 0 0 1-2-2v-14a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6"/><path d="M9 17h6"/>',
    sheet: '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21h-10a2 2 0 0 1-2-2v-14a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M8 11h8v7h-8z"/><path d="M8 15h8"/><path d="M11 11v7"/>',
    slides: '<path d="M3 4h18"/><path d="M4 4v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-10"/><path d="M12 16v4"/><path d="M9 20h6"/>',
    archive: '<rect x="3" y="4" width="18" height="4" rx="2"/><path d="M5 8v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-10"/><path d="M10 12l4 0"/>',
    audio: '<circle cx="6" cy="17" r="3"/><circle cx="16" cy="17" r="3"/><path d="M9 17v-13h10v13"/><path d="M9 8h10"/>',
    video: '<path d="M15 10l4.5-2.3a1 1 0 0 1 1.5.9v6.8a1 1 0 0 1-1.5.9l-4.5-2.3z"/><rect x="3" y="6" width="12" height="12" rx="2"/>',
    clipboard: '<path d="M9 5h-2a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-12a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="2"/>',
};

function icon(name) {
    return `<span class="ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICON_PATHS[name] || ''}</svg></span>`;
}

function hydrateIcons(root = document) {
    root.querySelectorAll('[data-icon]').forEach(el => { el.outerHTML = icon(el.dataset.icon); });
}

const FILE_KINDS = {
    folder: { icon: 'folder', color: 'var(--amber)', label: 'Složka' },
    doc: { icon: 'doc', color: 'var(--blue)', label: 'Dokument' },
    sheet: { icon: 'sheet', color: 'var(--mint)', label: 'Tabulka' },
    slides: { icon: 'slides', color: 'var(--rose)', label: 'Prezentace' },
    archive: { icon: 'archive', color: 'var(--amber)', label: 'Archiv' },
    audio: { icon: 'audio', color: 'var(--lavender)', label: 'Zvuk' },
    video: { icon: 'video', color: 'var(--lavender)', label: 'Video' },
    pdf: { icon: 'doc', color: 'var(--rose)', label: 'PDF' },
    text: { icon: 'doc', color: 'var(--blue)', label: 'Text' },
    image: { icon: 'doc', color: 'var(--lavender)', label: 'Obrázek' },
    file: { icon: 'doc', color: 'var(--periwinkle)', label: 'Soubor' },
};

// ==========================================
// STATE
// ==========================================
const state = {
    history: [],
    settings: { theme: 'dark', paused: false, notifications: true },
    peers: [],
    node: null,
    version: '',
    update: null,
    receiveDir: '',
    dir: 'all',
    search: '',
};
let ws = null;
let currentView = 'clipboard';

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

function formatClock(ts) {
    return new Date(ts * 1000).toLocaleTimeString('cs-CZ', { hour: '2-digit', minute: '2-digit' });
}

function dayLabel(ts) {
    const d = new Date(ts * 1000);
    const today = new Date();
    const yesterday = new Date(Date.now() - 86400000);
    if (d.toDateString() === today.toDateString()) return 'Dnes';
    if (d.toDateString() === yesterday.toDateString()) return 'Včera';
    return d.toLocaleDateString('cs-CZ', { weekday: 'long', day: 'numeric', month: 'long' });
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    $('toasts').appendChild(toast);
    setTimeout(() => toast.remove(), 2600);
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

const osIcon = (system) => (system === 'Darwin' ? 'apple' : 'windows');
const osColor = (system) => (system === 'Darwin' ? 'var(--lavender)' : 'var(--blue)');

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
                settings: data.settings, update: data.update, receiveDir: data.receive_dir,
                defaultReceiveDir: data.default_receive_dir,
            });
            if (data.node?.system === 'Darwin' && window.pywebview) document.documentElement.classList.add('mac-frameless');
            renderAll();
            renderTimeline({ scroll: 'bottom' });
            break;
        case 'clipboard_item':
            state.history = [data.item, ...state.history.filter(i => i.hash !== data.item.hash)];
            renderTimeline({ scroll: data.from_remote ? 'follow' : 'bottom' });
            if (currentView === 'files' && data.item.type === 'file') loadFiles();
            if (data.item.metadata?.too_large) showToast('Soubory jsou větší než 25 MB, neodeslány', 'error');
            break;
        case 'history':
            state.history = data.history;
            renderTimeline();
            break;
        case 'peers_updated':
            state.peers = data.peers || [];
            renderBridge();
            renderDevices();
            break;
        case 'settings':
            state.settings = data.settings;
            if (data.receive_dir) state.receiveDir = data.receive_dir;
            renderSettings();
            if (currentView === 'files') loadFiles();
            break;
        case 'update_status':
            state.update = data.update;
            renderUpdate();
            break;
    }
}

// ==========================================
// BRIDGE (connection status)
// ==========================================
function nodeHtml(device, sub, right = false) {
    return `
        <div class="node ${right ? 'right' : ''}">
            <span class="node-badge" style="background:${osColor(device.system)}">${icon(osIcon(device.system))}</span>
            <div style="min-width:0"><div class="node-name">${escapeHtml(device.name)}</div><div class="node-sub">${escapeHtml(sub)}</div></div>
        </div>`;
}

function renderBridge() {
    if (!state.node) return;
    const me = nodeHtml(state.node, 'Toto zařízení');
    const peers = state.peers;
    let html;
    if (state.settings.paused) {
        const other = peers[0] ? nodeHtml(peers[0], 'Pozastaveno', true) : '';
        html = `${me}<div class="link paused"><span id="resumeLink">pozastaveno · obnovit</span></div>${other}`;
    } else if (peers.length) {
        const more = peers.length > 1 ? ` +${peers.length - 1}` : '';
        html = `${me}<div class="link"><span>propojeno</span></div>${nodeHtml({ ...peers[0], name: peers[0].name + more }, 'Připojeno', true)}`;
    } else {
        html = `${me}<div class="link searching"><span>hledám na Wi-Fi…</span></div>
            <button class="pair-btn" id="pairBtn">Spárovat</button>`;
    }
    $('bridge').innerHTML = html;
    $('pairBtn')?.addEventListener('click', () => {
        showView('devices');
        setTimeout(() => $('newPairingKey').focus(), 50);
    });
    $('resumeLink')?.addEventListener('click', () => saveSettings({ paused: false }));
}

// ==========================================
// TIMELINE
// ==========================================
function firstLine(text) {
    return (text.split('\n').find(l => l.trim()) || text).trim();
}

function isUrl(text) {
    return /^https?:\/\/\S+$/.test(text.trim());
}

function looksLikeCode(text) {
    return /[{};<>]|^\s{2,}\S/m.test(text) && text.includes('\n');
}

function previewHtml(item) {
    const m = item.metadata || {};
    if (item.type === 'text') {
        const text = item.data;
        if (isUrl(text)) {
            let domain = '';
            try { domain = new URL(text.trim()).hostname.replace(/^www\./, ''); } catch (e) { /* not a URL after all */ }
            return `<div class="pv-link" data-action="view"><div class="domain">${escapeHtml(domain)}</div><div class="url">${escapeHtml(text.trim())}</div></div>`;
        }
        return `<div class="pv-text ${looksLikeCode(text) ? 'code' : ''}" data-action="view">${escapeHtml(text)}</div>`;
    }
    if (item.type === 'image') {
        const src = m.thumb || item.data;
        const img = src ? `<img class="pv-image" data-action="view" src="data:image/png;base64,${src}" alt="">` : '';
        return `${img}<div class="cap"><div class="cap-name">${escapeHtml(m.filename || 'Obrázek ze schránky')}</div>
            <div class="cap-sub">${m.width || '?'}×${m.height || '?'} px · ${formatBytes(m.size_bytes)}</div></div>`;
    }
    const files = m.files || [];
    const p = m.preview || { kind: 'file' };
    const first = files[0] || { name: 'Soubor' };
    const more = files.length > 1
        ? `<div class="more-files">+ ${files.length - 1} ${files.length === 2 ? 'další' : 'další'}: ${escapeHtml(files.slice(1, 4).map(f => f.name).join(', '))}${files.length > 4 ? '…' : ''}</div>`
        : '';
    const kind = FILE_KINDS[p.kind] || FILE_KINDS.file;
    const sizeText = first.is_dir ? `Složka · ${formatBytes(m.size_bytes)}` : `${p.pages ? `${p.pages} ${p.pages === 1 ? 'strana' : p.pages < 5 ? 'strany' : 'stran'} · ` : ''}${formatBytes(files.length > 1 ? m.size_bytes : first.size_bytes)}`;
    const caption = `<div class="cap"><div class="cap-name">${escapeHtml(first.name)}</div><div class="cap-sub">${kind.label} · ${sizeText}</div></div>`;

    if (p.kind === 'image' && p.thumb) {
        return `<img class="pv-image" data-action="view" src="data:image/png;base64,${p.thumb}" alt="">${caption}${more}`;
    }
    if (p.kind === 'pdf' && p.thumb) {
        return `<div class="pdf-wrap" data-action="view"><img src="data:image/png;base64,${p.thumb}" alt=""><span class="badge">PDF</span></div>${caption}${more}`;
    }
    const ext = first.is_dir ? '' : (first.name.includes('.') ? first.name.split('.').pop().slice(0, 4).toUpperCase() : '');
    const tile = `<span class="tile" style="background:${kind.color}">${icon(kind.icon)}${escapeHtml(ext)}</span>`;
    const head = `<div class="pv-file" data-action="view" style="cursor:zoom-in">${tile}<div style="min-width:0"><div class="cap-name">${escapeHtml(first.name)}</div><div class="cap-sub">${kind.label} · ${sizeText}</div></div></div>`;
    const snippet = p.kind === 'text' && p.snippet ? `<div class="pv-snippet" data-action="view">${escapeHtml(p.snippet)}</div>` : '';
    return `${head}${snippet}${more}`;
}

function whereHtml(item) {
    if (item.direction === 'received') {
        return `<span class="where">${icon('arrow-down')}z ${escapeHtml(item.device)} · ${formatClock(item.timestamp)}</span>`;
    }
    if (item.metadata?.too_large) return `<span class="where warn">${icon('arrow-up')}Nad 25 MB – neodesláno</span>`;
    const targets = item.targets || [];
    const to = targets.length ? `do ${escapeHtml(targets.join(', '))}` : 'jen na tomto zařízení';
    return `<span class="where">${icon('arrow-up')}${to} · ${formatClock(item.timestamp)}</span>`;
}

function messageHtml(item) {
    const isFile = item.type === 'file';
    const dir = item.direction === 'received' ? 'in' : 'out';
    return `
        <div class="msg ${dir} ${item.pinned ? 'pinned' : ''}" data-hash="${item.hash}">
            <div class="bubble">
                ${previewHtml(item)}
                <div class="meta">
                    ${whereHtml(item)}
                    <div class="actions">
                        ${isFile ? `<button class="act extra" data-action="reveal" title="Zobrazit ve složce">${icon('folder')}</button>` : ''}
                        <button class="act extra" data-action="pin" title="${item.pinned ? 'Odepnout' : 'Připnout'}">${icon('pin')}</button>
                        <button class="act extra" data-action="delete" title="Smazat z historie">${icon('trash')}</button>
                        ${isFile ? `<button class="act" data-action="open" title="Otevřít">${icon('open')}</button>` : ''}
                        <button class="act" data-action="copy" title="Kopírovat do schránky">${icon('copy')}Kopírovat</button>
                    </div>
                </div>
            </div>
        </div>`;
}

function searchText(item) {
    if (item.type === 'text') return item.data;
    const m = item.metadata || {};
    return [m.filename, ...(m.files || []).map(f => f.name), m.preview?.snippet].filter(Boolean).join(' ');
}

function renderTimeline({ scroll = 'keep' } = {}) {
    const tl = $('timeline');
    const nearBottom = tl.scrollHeight - tl.scrollTop - tl.clientHeight < 80;
    const q = state.search.trim().toLowerCase();
    // Oldest first, newest at the bottom next to the composer, like a chat
    const items = [...state.history]
        .sort((a, b) => a.timestamp - b.timestamp)
        .filter(i => state.dir === 'all' || (state.dir === 'pinned' ? i.pinned : i.direction === state.dir))
        .filter(i => !q || `${searchText(i)} ${i.device || ''}`.toLowerCase().includes(q));

    if (!items.length) {
        const searching = q || state.dir !== 'all';
        $('timeline').innerHTML = `
            <div class="empty">${icon('clipboard')}
                <h3>${searching ? 'Nic nenalezeno' : 'Zatím tu nic není'}</h3>
                <p>${searching ? 'Zkus jiný filtr nebo hledání.' : 'Zkopíruj cokoliv (Ctrl+C / Cmd+C) nebo sem přetáhni soubor – objeví se to tady i na druhém zařízení.'}</p>
            </div>`;
        return;
    }
    let lastDay = '';
    const prevTop = tl.scrollTop;
    tl.innerHTML = items.map(item => {
        const day = dayLabel(item.timestamp);
        const sep = day !== lastDay ? `<div class="day">${day}</div>` : '';
        lastDay = day;
        return sep + messageHtml(item);
    }).join('');
    if (scroll === 'bottom' || (scroll === 'follow' && nearBottom)) scrollTimelineToBottom();
    else tl.scrollTop = prevTop;
}

function scrollTimelineToBottom() {
    const tl = $('timeline');
    tl.scrollTop = tl.scrollHeight;
    // Thumbnails finish loading after the first layout and push the content down
    tl.querySelectorAll('img').forEach(img => { if (!img.complete) img.addEventListener('load', () => { tl.scrollTop = tl.scrollHeight; }, { once: true }); });
}

// ==========================================
// IN-APP VIEWER (history items and files)
// ==========================================
const viewer = { item: null, path: null, stack: [] };
const enc = encodeURIComponent;

function showViewer(title, sub, body, { path = null } = {}) {
    viewer.path = path;
    $('lightboxTitle').textContent = title;
    $('lightboxSub').textContent = sub;
    $('lightboxBody').innerHTML = body;
    $('viewerOpen').hidden = !path;
    $('viewerReveal').hidden = !path;
    $('viewerBack').hidden = viewer.stack.length === 0;
    $('lightbox').hidden = false;
}

function openLightbox(item) {
    viewer.item = item;
    viewer.stack = [];
    const m = item.metadata || {};
    if (item.type === 'file') {
        const first = (item.data || '').split('\n')[0];
        if (first) return openFileViewer(first);
    }
    if (item.type === 'image') {
        showViewer(m.filename || 'Obrázek ze schránky', `${m.width}×${m.height} px · ${formatBytes(m.size_bytes)}`,
            `<div class="center"><img src="data:image/png;base64,${item.data || m.thumb}" alt=""></div>`);
    } else {
        showViewer(isUrl(item.data) ? 'Odkaz' : 'Text', `${item.data.length} znaků`, `<pre>${escapeHtml(item.data)}</pre>`);
    }
}

async function openFileViewer(path, { push = false } = {}) {
    if (push && viewer.path) viewer.stack.push(viewer.path);
    let info;
    try {
        info = await api(`/api/files/info?path=${enc(path)}`);
    } catch (err) {
        showToast('Soubor už neexistuje', 'error');
        return;
    }
    const kind = FILE_KINDS[info.kind] || FILE_KINDS.file;
    const raw = `/api/files/raw?path=${enc(path)}`;
    let sub = `${kind.label} · ${info.is_dir ? `${info.children?.length || 0} položek` : formatBytes(info.size)}`;
    let body;
    switch (info.kind) {
        case 'image':
            body = `<div class="center"><img src="${raw}" alt=""></div>`;
            break;
        case 'pdf':
            sub += ` · ${info.pages} ${info.pages === 1 ? 'strana' : info.pages < 5 ? 'strany' : 'stran'}`;
            body = `<div class="pdf-pages">${Array.from({ length: info.pages }, (_, i) =>
                `<img loading="lazy" src="/api/files/pdf-page?path=${enc(path)}&page=${i}" alt="Strana ${i + 1}">`).join('')}</div>`;
            break;
        case 'text': {
            const { text, truncated } = await api(`/api/files/text?path=${enc(path)}`);
            body = `<pre>${escapeHtml(text)}${truncated ? '\n\n… (zkráceno, celý soubor otevři tlačítkem Otevřít)' : ''}</pre>`;
            break;
        }
        case 'video':
            body = `<div class="center"><video controls src="${raw}"></video></div>`;
            break;
        case 'audio':
            body = `<div class="center"><audio controls src="${raw}"></audio></div>`;
            break;
        case 'folder':
            body = `<div class="folder-list">${(info.children || []).map(c => `
                <button class="folder-row" data-path="${escapeHtml(c.path)}">${icon(c.is_dir ? 'folder' : (FILE_KINDS[c.kind] || FILE_KINDS.file).icon)}
                    <span class="grow">${escapeHtml(c.name)}</span><span class="muted">${c.is_dir ? '' : formatBytes(c.size)}</span></button>`).join('')
                || '<div class="muted" style="padding:12px">Složka je prázdná.</div>'}</div>`;
            break;
        default: {
            const ext = info.name.includes('.') ? info.name.split('.').pop().slice(0, 4).toUpperCase() : '';
            body = `<div class="center"><div class="no-preview">
                <span class="tile" style="background:${kind.color}">${icon(kind.icon)}${escapeHtml(ext)}</span>
                <div>Náhled tohoto typu souboru v aplikaci zobrazit nejde.</div>
                <button class="chip-btn accent" data-viewer-open>Otevřít v aplikaci</button></div></div>`;
        }
    }
    showViewer(info.name, sub, body, { path });
}

function closeLightbox() {
    $('lightbox').hidden = true;
    $('lightboxBody').innerHTML = '';  // stops audio/video playback
    viewer.item = null;
    viewer.path = null;
    viewer.stack = [];
}

$('lightboxBody').addEventListener('click', (e) => {
    const row = e.target.closest('.folder-row');
    if (row) openFileViewer(row.dataset.path, { push: true });
    if (e.target.closest('[data-viewer-open]')) api('/api/files/open', { path: viewer.path });
});
$('viewerBack').addEventListener('click', () => {
    const prev = viewer.stack.pop();
    if (prev) openFileViewer(prev);
});
$('viewerOpen').addEventListener('click', () => api('/api/files/open', { path: viewer.path }).catch(err => showToast(err.message, 'error')));
$('viewerReveal').addEventListener('click', () => api('/api/files/reveal', { path: viewer.path }).catch(err => showToast(err.message, 'error')));

async function copyItem(hash) {
    await api('/api/history/copy', { hash });
    showToast('Zkopírováno do schránky');
}

$('timeline').addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-action]');
    const row = btn?.closest('.msg');
    if (!btn || !row) return;
    const hash = row.dataset.hash;
    const item = state.history.find(i => i.hash === hash);
    try {
        switch (btn.dataset.action) {
            case 'view': openLightbox(item); break;
            case 'copy': await copyItem(hash); break;
            case 'open': await api('/api/history/open', { hash }); break;
            case 'reveal': await api('/api/history/reveal', { hash }); break;
            case 'pin': await api('/api/history/pin', { hash, pinned: !item?.pinned }); break;
            case 'delete': await api('/api/history/delete', { hash }); break;
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
});

$('lightboxClose').addEventListener('click', closeLightbox);
$('lightbox').addEventListener('click', (e) => { if (e.target.id === 'lightbox') closeLightbox(); });
$('lightboxCopy').addEventListener('click', async () => {
    try {
        if (viewer.path) await api('/api/files/copy', { path: viewer.path });
        else if (viewer.item) await api('/api/history/copy', { hash: viewer.item.hash });
        showToast('Zkopírováno do schránky');
    } catch (err) {
        showToast(err.message, 'error');
    }
});

// ==========================================
// FILES PAGE
// ==========================================
let fileScope = 'received';
let fileList = [];

async function loadFiles() {
    try {
        const data = await api(`/api/files?scope=${fileScope}`);
        fileList = data.files;
        $('filesDir').textContent = fileScope === 'received' ? data.dir : 'Soubory, které jsi odeslal z tohoto zařízení';
        $('filesOpenDir').hidden = fileScope !== 'received';
        $('filesChangeDir').hidden = fileScope !== 'received';
        renderFiles();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function fileCardHtml(f) {
    const kind = FILE_KINDS[f.kind] || FILE_KINDS.file;
    const ext = f.is_dir ? '' : (f.name.includes('.') ? f.name.split('.').pop().slice(0, 4).toUpperCase() : '');
    const tile = `<span class="tile" style="background:${kind.color}">${icon(kind.icon)}${escapeHtml(ext)}</span>`;
    const visual = f.kind === 'image' || f.kind === 'pdf'
        ? `<img loading="lazy" src="/api/files/thumb?path=${enc(f.path)}" alt="" onerror="this.remove()">`
        : tile;
    const date = new Date(f.mtime * 1000).toLocaleString('cs-CZ', { day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit' });
    return `
        <div class="file-card" data-path="${escapeHtml(f.path)}">
            <div class="file-thumb ${f.kind}">${visual}</div>
            <div class="file-actions">
                <button data-file-action="copy" title="Kopírovat do schránky">${icon('copy')}</button>
                <button data-file-action="send" title="Odeslat znovu">${icon('arrow-up')}</button>
                <button data-file-action="reveal" title="Zobrazit ve složce">${icon('folder')}</button>
            </div>
            <div class="file-info">
                <div class="file-name" title="${escapeHtml(f.name)}">${escapeHtml(f.name)}</div>
                <div class="file-sub">${f.is_dir ? 'Složka' : formatBytes(f.size)} · ${date}</div>
            </div>
        </div>`;
}

function renderFiles() {
    const q = $('fileSearch').value.trim().toLowerCase();
    const files = fileList.filter(f => !q || f.name.toLowerCase().includes(q));
    $('fileGrid').innerHTML = files.length
        ? files.map(fileCardHtml).join('')
        : `<div class="empty" style="grid-column:1/-1">${icon('folder')}<h3>${q ? 'Nic nenalezeno' : 'Zatím tu nejsou žádné soubory'}</h3>
            <p>${fileScope === 'received' ? 'Soubory poslané z druhého zařízení se uloží sem.' : 'Tady uvidíš soubory, které jsi zkopíroval nebo přetáhl do aplikace.'}</p></div>`;
}

$('fileGrid').addEventListener('click', async (e) => {
    const card = e.target.closest('.file-card');
    if (!card) return;
    const path = card.dataset.path;
    const action = e.target.closest('[data-file-action]')?.dataset.fileAction;
    try {
        if (action === 'copy') { await api('/api/files/copy', { path }); showToast('Zkopírováno do schránky'); }
        else if (action === 'send') { await api('/api/files/send', { path }); showToast('Odesláno'); }
        else if (action === 'reveal') await api('/api/files/reveal', { path });
        else { viewer.stack = []; viewer.item = null; openFileViewer(path); }
    } catch (err) {
        showToast(err.message, 'error');
    }
});

$('fileScope').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    fileScope = btn.dataset.value;
    $('fileScope').querySelectorAll('button').forEach(b => b.classList.toggle('active', b === btn));
    loadFiles();
});
$('fileSearch').addEventListener('input', renderFiles);
$('filesOpenDir').addEventListener('click', () => api('/api/open-received', {}));
$('filesChangeDir').addEventListener('click', () => chooseReceiveDir());

// ==========================================
// RECEIVE FOLDER
// ==========================================
async function chooseReceiveDir() {
    let folder;
    if (window.pywebview?.api?.choose_folder) folder = await window.pywebview.api.choose_folder(state.receiveDir);
    else folder = prompt('Cesta ke složce pro přijaté soubory:', state.receiveDir);
    if (!folder) return;
    try {
        const res = await api('/api/settings', { receive_dir: folder });
        state.settings = res;
        state.receiveDir = res.effective_receive_dir;
        renderSettings();
        showToast('Přijaté soubory se teď ukládají do nové složky');
    } catch (err) {
        showToast(err.message, 'error');
    }
}

$('changeReceiveDirBtn').addEventListener('click', chooseReceiveDir);
$('resetReceiveDirBtn').addEventListener('click', async () => {
    const res = await api('/api/settings', { receive_dir: '' });
    state.settings = res;
    state.receiveDir = res.effective_receive_dir;
    renderSettings();
});

// ==========================================
// FILTERS
// ==========================================
$('dirFilter').addEventListener('click', (e) => {
    const btn = e.target.closest('button');
    if (!btn) return;
    state.dir = btn.dataset.value;
    $('dirFilter').querySelectorAll('button').forEach(b => b.classList.toggle('active', b === btn));
    renderTimeline();
});

$('searchInput').addEventListener('input', (e) => {
    state.search = e.target.value;
    renderTimeline();
});

// ==========================================
// COMPOSER, FILE DROP & PASTE
// ==========================================
async function uploadFiles(files) {
    if (!files.length) return;
    const form = new FormData();
    [...files].forEach(f => form.append('files', f, f.name));
    try {
        const res = await fetch('/api/upload-files', { method: 'POST', body: form });
        const data = await res.json();
        if (!res.ok) throw new Error(data.message);
        if (data.status === 'already_sent') showToast('Tyhle soubory už byly odeslány');
    } catch (err) {
        showToast(`Nepodařilo se odeslat: ${err.message}`, 'error');
    }
}

async function uploadImage(file) {
    const form = new FormData();
    form.append('file', file, file.name || 'screenshot.png');
    const res = await fetch('/api/upload', { method: 'POST', body: form });
    if (!res.ok) showToast('Obrázek se nepodařilo odeslat', 'error');
}

function sendText() {
    const text = $('composeText').value;
    if (!text.trim() || ws?.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ action: 'push_text', text }));
    $('composeText').value = '';
    autosize();
}

function autosize() {
    const ta = $('composeText');
    ta.style.height = 'auto';
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`;
}

$('composeText').addEventListener('input', autosize);
$('composeText').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendText();
    }
});
$('sendBtn').addEventListener('click', sendText);
$('attachBtn').addEventListener('click', () => $('fileInput').click());
$('fileInput').addEventListener('change', (e) => { uploadFiles(e.target.files); e.target.value = ''; });

let dragDepth = 0;
window.addEventListener('dragenter', (e) => {
    if (![...e.dataTransfer.types].includes('Files')) return;
    dragDepth++;
    $('dropOverlay').hidden = false;
});
window.addEventListener('dragleave', () => {
    if (--dragDepth <= 0) {
        dragDepth = 0;
        $('dropOverlay').hidden = true;
    }
});
window.addEventListener('dragover', (e) => e.preventDefault());
window.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDepth = 0;
    $('dropOverlay').hidden = true;
    // A dropped folder arrives as a zero-byte entry without a type; folders go through Ctrl+C instead
    const files = [...e.dataTransfer.files].filter(f => f.size > 0 || f.type);
    if (files.length < e.dataTransfer.files.length) showToast('Složky přetáhnout nejde – zkopíruj je přes Ctrl+C', 'error');
    uploadFiles(files);
});

window.addEventListener('paste', (e) => {
    const files = [...(e.clipboardData?.files || [])];
    if (!files.length) return;
    e.preventDefault();
    // A screenshot pasted from the clipboard has no real file behind it; treat it as an image
    if (files.length === 1 && files[0].type.startsWith('image/') && /^image\.\w+$/.test(files[0].name)) uploadImage(files[0]);
    else uploadFiles(files);
});

// ==========================================
// NAVIGATION
// ==========================================
const VIEW_TITLES = { clipboard: 'Schránka', files: 'Soubory', devices: 'Zařízení', settings: 'Nastavení' };

function showView(view) {
    currentView = view;
    if (view === 'files') loadFiles();
    document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.view === view));
    document.querySelectorAll('.view').forEach(v => v.classList.toggle('active', v.dataset.view === view));
    $('viewTitle').textContent = VIEW_TITLES[view];
    if (view === 'devices') loadPairingKey();
    else $('ownPairingKey').value = '';
}

document.querySelectorAll('.nav-item').forEach(b => b.addEventListener('click', () => showView(b.dataset.view)));
$('versionLink').addEventListener('click', () => showView('settings'));

async function saveSettings(changes) {
    try {
        state.settings = await api('/api/settings', changes);
        renderSettings();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function renderDevices() {
    if (!state.node) return;
    const device = (d, sub, status) => `
        <div class="device">
            <span class="node-badge" style="background:${osColor(d.system)}">${icon(osIcon(d.system))}</span>
            <div class="grow"><div class="row-title">${escapeHtml(d.name)}</div><div class="muted">${escapeHtml(sub)}</div></div>
            ${status}
        </div>`;
    $('deviceList').innerHTML = device(state.node, state.node.system === 'Darwin' ? 'macOS' : 'Windows', '<span class="status me">Toto zařízení</span>')
        + (state.peers.length
            ? state.peers.map(p => device(p, `${p.system === 'Darwin' ? 'macOS' : 'Windows'} · ${p.host}`, '<span class="status">Připojeno</span>')).join('')
            : '<div class="device"><div class="muted">Žádné další zařízení není připojené. Spusť aplikaci na druhém zařízení ve stejné Wi-Fi a spáruj ho kódem níže.</div></div>');
}

function renderSettings() {
    const s = state.settings;
    document.documentElement.dataset.theme = s.theme;
    $('themeBtn').innerHTML = icon(s.theme === 'dark' ? 'moon' : 'sun');
    document.querySelectorAll('#themeSelect button').forEach(b => b.classList.toggle('active', b.dataset.value === s.theme));
    $('pauseBtn').innerHTML = icon(s.paused ? 'play' : 'pause');
    $('pauseBtn').classList.toggle('on', s.paused);
    $('pauseBtn').title = s.paused ? 'Obnovit synchronizaci' : 'Pozastavit synchronizaci';
    $('pausedSwitch').checked = s.paused;
    $('notificationsSwitch').checked = s.notifications;
    $('receiveDir').textContent = state.receiveDir || '–';
    $('receiveDir').title = state.receiveDir || '';
    $('resetReceiveDirBtn').hidden = !s.receive_dir;
    renderBridge();
}

function renderUpdate() {
    const u = state.update;
    if (!u) return;
    const busy = u.state === 'downloading' || u.state === 'installing';
    $('updateBtn').hidden = !u.available;
    $('updateDot').hidden = !u.available;
    $('versionLink').textContent = `v${u.current}`;
    $('updateBtnText').textContent = busy ? `${Math.round(u.progress * 100)} %` : 'Aktualizovat';
    $('updateProgress').hidden = !busy;
    $('updateProgressBar').style.width = `${Math.round(u.progress * 100)}%`;
    $('installUpdateBtn').hidden = !u.available || busy;
    $('installUpdateBtn').textContent = u.can_install ? 'Aktualizovat' : 'Stáhnout';
    $('checkUpdateBtn').hidden = busy;
    $('versionText').textContent = `Universal Clipboard ${u.current}`;

    let text = `Verze ${u.current} je aktuální.`;
    if (u.state === 'downloading') text = `Stahuji verzi ${u.latest}… ${Math.round(u.progress * 100)} %`;
    else if (u.state === 'installing') text = `Instaluji verzi ${u.latest}, aplikace se znovu spustí…`;
    else if (u.state === 'error') text = `Aktualizace se nezdařila: ${u.error}`;
    else if (u.available) text = `Je dostupná verze ${u.latest} (máš ${u.current}).`;
    $('updateStatusText').textContent = text;
}

async function installUpdate() {
    if (!state.update?.can_install) {
        api('/api/update/open', {});
        return;
    }
    try {
        await api('/api/update/install', {});
    } catch (err) {
        showToast('Aktualizaci se nepodařilo spustit', 'error');
    }
}

$('themeBtn').addEventListener('click', () => saveSettings({ theme: state.settings.theme === 'dark' ? 'light' : 'dark' }));
$('pauseBtn').addEventListener('click', () => saveSettings({ paused: !state.settings.paused }));
$('pausedSwitch').addEventListener('change', (e) => saveSettings({ paused: e.target.checked }));
$('notificationsSwitch').addEventListener('change', (e) => saveSettings({ notifications: e.target.checked }));
$('themeSelect').addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) saveSettings({ theme: b.dataset.value }); });
$('openReceivedBtn').addEventListener('click', () => api('/api/open-received', {}));
$('updateBtn').addEventListener('click', installUpdate);
$('installUpdateBtn').addEventListener('click', installUpdate);

$('checkUpdateBtn').addEventListener('click', async () => {
    $('updateStatusText').textContent = 'Kontroluji…';
    state.update = await api('/api/update?refresh=1');
    renderUpdate();
    if (!state.update.available) showToast('Máš nejnovější verzi');
});

$('clearHistoryBtn').addEventListener('click', async () => {
    if (confirm('Smazat z historie všechny nepřipnuté položky?')) await api('/api/history/clear', {});
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
        showToast('Spárováno – zařízení se za pár sekund připojí');
    } catch (err) {
        showToast(`Kód nelze použít: ${err.message}`, 'error');
    }
});

// ==========================================
// WINDOW CONTROLS (frameless desktop window)
// ==========================================
window.addEventListener('pywebviewready', () => {
    $('windowControls').hidden = false;
    if (state.node?.system === 'Darwin') document.documentElement.classList.add('mac-frameless');
});
$('minimizeBtn').addEventListener('click', () => window.pywebview?.api.minimize());
$('maximizeBtn').addEventListener('click', () => window.pywebview?.api.toggle_maximize());
$('closeBtn').addEventListener('click', () => window.pywebview?.api.close());
// Buttons sit inside drag regions; keep a click on them from starting a window drag
document.querySelectorAll('.titlebar button, .sidebar button').forEach(b => b.addEventListener('mousedown', (e) => e.stopPropagation()));

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !$('lightbox').hidden) closeLightbox();
});

// ==========================================
// INIT
// ==========================================
function renderAll() {
    renderSettings();
    renderDevices();
    renderTimeline();
    renderUpdate();
}

hydrateIcons();
connect();
setInterval(renderTimeline, 60000); // rolls "Dnes" over to "Včera" at midnight
