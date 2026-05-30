/**
 * Chat en (casi) tiempo real mediante polling.
 * Consume datos reales: GET /chat/rooms/, GET/POST /chat/rooms/{id}/messages/.
 * Las salas existen solo cuando hay un match ACEPTADO entre dos usuarios.
 */
document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    const roomsList = document.getElementById('chat-rooms-list');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send-message');
    const chatHeaderName = document.getElementById('chat-header-name');
    const chatHeaderAvatar = document.getElementById('chat-header-avatar');

    const me = JSON.parse(sessionStorage.getItem('user_info') || '{}');
    const myId = me.id;

    let rooms = [];
    let currentRoomId = null;
    let pollInterval = null;

    const urlParams = new URLSearchParams(window.location.search);
    const initialRoomId = urlParams.get('room');

    function otherName(room) {
        return (room.other_user && (room.other_user.display_name || room.other_user.username)) || 'Match';
    }

    function asList(response) {
        return Array.isArray(response) ? response : (response.results || []);
    }

    async function loadRooms() {
        try {
            rooms = asList(await api.get('/chat/rooms/'));
        } catch (err) {
            console.error('Error cargando salas:', err);
            rooms = [];
        }
        renderRooms();
        if (rooms.length === 0) {
            roomsList.innerHTML =
                '<p style="color: var(--color-text-muted); padding: 1rem;">Aún no tienes matches aceptados. Conecta desde el Radar.</p>';
        }
    }

    function renderRooms() {
        roomsList.innerHTML = '';
        rooms.forEach(room => {
            const name = otherName(room);
            const div = document.createElement('div');
            div.style.padding = '1rem';
            div.style.borderRadius = '8px';
            div.style.cursor = 'pointer';
            div.style.display = 'flex';
            div.style.alignItems = 'center';
            div.style.gap = '1rem';
            div.style.background = room.id == currentRoomId ? 'rgba(255,255,255,0.05)' : 'transparent';
            div.innerHTML = `
                <div style="width:40px;height:40px;border-radius:50%;background:var(--color-neon-purple);
                     display:flex;align-items:center;justify-content:center;font-weight:800;color:#000;">
                    ${name.charAt(0).toUpperCase()}
                </div>
                <div style="flex: 1; overflow: hidden;">
                    <h4 style="margin-bottom: 0.2rem;">${name}</h4>
                    <p style="color: var(--color-text-secondary); font-size: 0.85rem;">Match musical</p>
                </div>
            `;
            div.onclick = () => selectRoom(room.id);
            roomsList.appendChild(div);
        });
    }

    async function selectRoom(roomId) {
        currentRoomId = roomId;
        const room = rooms.find(r => r.id == roomId);
        const name = room ? otherName(room) : 'Match';

        chatHeaderName.textContent = name;
        chatHeaderAvatar.textContent = name.charAt(0).toUpperCase();
        chatHeaderAvatar.style.display = 'flex';
        chatHeaderAvatar.style.alignItems = 'center';
        chatHeaderAvatar.style.justifyContent = 'center';
        chatHeaderAvatar.style.background = 'var(--color-neon-purple)';
        chatHeaderAvatar.style.color = '#000';
        chatHeaderAvatar.style.fontWeight = '800';

        chatInput.disabled = false;
        btnSend.disabled = false;
        chatInput.focus();
        renderRooms();

        if (pollInterval) clearInterval(pollInterval);
        await loadMessages();
        pollInterval = setInterval(loadMessages, 3000);
    }

    async function loadMessages() {
        if (!currentRoomId) return;
        try {
            const messages = asList(await api.get(`/chat/rooms/${currentRoomId}/messages/`));
            renderMessages(messages);
        } catch (err) {
            console.error('Error cargando mensajes:', err);
        }
    }

    function renderMessages(messages) {
        chatMessages.innerHTML = '';
        if (!messages.length) {
            chatMessages.innerHTML =
                '<p style="text-align: center; color: var(--color-text-muted); margin: auto;">Di hola 👋</p>';
            return;
        }
        messages.forEach(msg => {
            const isMe = msg.sender && msg.sender.id === myId;
            const b = document.createElement('div');
            b.style.maxWidth = '70%';
            b.style.padding = '0.8rem 1rem';
            b.style.borderRadius = '16px';
            b.style.marginBottom = '0.5rem';
            b.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
            b.style.background = isMe ? 'var(--color-neon-purple)' : 'rgba(255,255,255,0.1)';
            b.style.color = 'white';
            b.style[isMe ? 'borderBottomRightRadius' : 'borderBottomLeftRadius'] = '0';
            b.textContent = msg.content;
            chatMessages.appendChild(b);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || !currentRoomId) return;
        chatInput.value = '';
        try {
            await api.post(`/chat/rooms/${currentRoomId}/messages/`, { content: text });
            await loadMessages();
        } catch (err) {
            console.error('Error al enviar mensaje:', err);
            chatInput.value = text;
        }
    }

    btnSend.onclick = sendMessage;
    chatInput.onkeypress = (e) => {
        if (e.key === 'Enter') sendMessage();
    };

    // ── Crear grupo ────────────────────────────────────────────────
    // Los candidatos son tus matches (el "otro usuario" de tus chats directos).
    function matchCandidates() {
        const seen = new Map();
        rooms.filter(r => !r.is_group && r.other_user).forEach(r => {
            seen.set(r.other_user.id, r.other_user.display_name || r.other_user.username);
        });
        return [...seen.entries()].map(([id, name]) => ({ id, name }));
    }

    function openGroupModal() {
        const candidates = matchCandidates();
        if (!candidates.length) {
            alert('Necesitas al menos un match aceptado para crear un grupo.');
            return;
        }

        const overlay = document.createElement('div');
        overlay.style.cssText =
            'position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.6);display:flex;' +
            'align-items:center;justify-content:center;';
        const checks = candidates.map(c =>
            `<label style="display:flex;align-items:center;gap:.5rem;padding:.3rem 0;cursor:pointer;">
                <input type="checkbox" value="${c.id}"> ${c.name}
            </label>`).join('');
        overlay.innerHTML = `
            <div class="panel" style="width:340px;padding:1.5rem;">
                <h3 style="margin-bottom:1rem;color:var(--color-neon-blue);">Nuevo grupo</h3>
                <input id="grp-name" class="form-control" placeholder="Nombre del grupo" style="margin-bottom:1rem;">
                <p style="color:var(--color-text-secondary);font-size:.85rem;margin-bottom:.5rem;">Participantes:</p>
                <div style="max-height:180px;overflow-y:auto;margin-bottom:1rem;">${checks}</div>
                <div style="display:flex;gap:.5rem;justify-content:flex-end;">
                    <button id="grp-cancel" class="btn btn-outline" style="padding:.4rem 1rem;">Cancelar</button>
                    <button id="grp-create" class="btn btn-primary" style="padding:.4rem 1rem;">Crear</button>
                </div>
            </div>`;
        document.body.appendChild(overlay);

        const close = () => overlay.remove();
        overlay.querySelector('#grp-cancel').onclick = close;
        overlay.onclick = (e) => { if (e.target === overlay) close(); };

        overlay.querySelector('#grp-create').onclick = async () => {
            const name = overlay.querySelector('#grp-name').value.trim();
            const ids = [...overlay.querySelectorAll('input[type=checkbox]:checked')]
                .map(c => parseInt(c.value, 10));
            if (!name) { alert('Ponle un nombre al grupo.'); return; }
            if (!ids.length) { alert('Selecciona al menos un participante.'); return; }
            try {
                const room = await api.post('/chat/rooms/', { name, participant_ids: ids });
                close();
                await loadRooms();
                selectRoom(room.id);
            } catch (err) {
                console.error('Error al crear grupo:', err);
                alert('No se pudo crear el grupo.');
            }
        };
    }

    const btnNewGroup = document.getElementById('btn-new-group');
    if (btnNewGroup) btnNewGroup.onclick = openGroupModal;

    (async () => {
        await loadRooms();
        if (initialRoomId) selectRoom(initialRoomId);
    })();
});
