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

    (async () => {
        await loadRooms();
        if (initialRoomId) selectRoom(initialRoomId);
    })();
});
