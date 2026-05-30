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
    
    let currentRoomId = null;
    let pollInterval = null;

    // Obtener id de la room de la URL (si venimos redireccionados del radar)
    const urlParams = new URLSearchParams(window.location.search);
    const initialRoomId = urlParams.get('room');

    // Mocks de rooms
    const mockRooms = [
        { id: 101, user: { name: 'Ana García', avatar: 'https://i.pravatar.cc/150?u=1' }, lastMessage: '¡Hola! ¿Vas a La Solar?' },
        { id: 102, user: { name: 'Carlos Ruiz', avatar: 'https://i.pravatar.cc/150?u=2' }, lastMessage: 'Brutal el último disco' },
        { id: 103, user: { name: 'Luisa F.', avatar: 'https://i.pravatar.cc/150?u=3' }, lastMessage: 'Jaja de acuerdo' },
        { id: 104, user: { name: 'David', avatar: 'https://i.pravatar.cc/150?u=4' }, lastMessage: 'Nuevo Match' }
    ];

    // Mocks de mensajes por room
    const mockMessages = {
        101: [
            { sender: 'them', text: '¡Hola! Hicimos match musical 🙌' },
            { sender: 'me', text: '¡Hola Ana! Sí, veo que ambos somos VIP.' },
            { sender: 'them', text: 'Total. ¿Vas a ir a La Solar?' }
        ],
        102: [
            { sender: 'them', text: 'Brutal el último disco' }
        ]
    };

    function renderRooms() {
        roomsList.innerHTML = '';
        mockRooms.forEach(room => {
            const div = document.createElement('div');
            div.style.padding = '1rem';
            div.style.borderRadius = '8px';
            div.style.cursor = 'pointer';
            div.style.display = 'flex';
            div.style.alignItems = 'center';
            div.style.gap = '1rem';
            div.style.background = room.id == currentRoomId ? 'rgba(255,255,255,0.05)' : 'transparent';
            
            div.innerHTML = `
                <img src="${room.user.avatar}" style="width: 40px; height: 40px; border-radius: 50%;">
                <div style="flex: 1; overflow: hidden;">
                    <h4 style="margin-bottom: 0.2rem;">${room.user.name}</h4>
                    <p style="color: var(--color-text-secondary); font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${room.lastMessage}</p>
                </div>
            `;
            
            div.onclick = () => selectRoom(room.id);
            roomsList.appendChild(div);
        });
    }

    async function selectRoom(roomId) {
        currentRoomId = roomId;
        const roomInfo = mockRooms.find(r => r.id == roomId) || { user: { name: 'Match Nuevo', avatar: 'https://i.pravatar.cc/150?u=99' } };
        
        chatHeaderName.textContent = roomInfo.user.name;
        chatHeaderAvatar.style.backgroundImage = `url(${roomInfo.user.avatar})`;
        chatHeaderAvatar.style.backgroundSize = 'cover';
        chatHeaderAvatar.style.backgroundPosition = 'center';
        
        chatInput.disabled = false;
        btnSend.disabled = false;
        chatInput.focus();

        renderRooms(); // Update selected style
        
        if (pollInterval) clearInterval(pollInterval);
        
        await loadMessages();
        
        // Polling cada 3 segundos a GET /api/chat/rooms/{id}/messages/ para simular RT
        pollInterval = setInterval(loadMessages, 3000);
    }

    async function loadMessages() {
        if (!currentRoomId) return;
        
        let messages = [];
        try {
            // const response = await api.get(`/chat/rooms/${currentRoomId}/messages/`);
            throw new Error("Mocks");
        } catch (err) {
            messages = mockMessages[currentRoomId] || [];
        }

        renderMessages(messages);
    }

    function renderMessages(messages) {
        chatMessages.innerHTML = '';
        if (messages.length === 0) {
            chatMessages.innerHTML = '<p style="text-align: center; color: var(--color-text-muted); margin-top: auto; margin-bottom: auto;">Di hola 👋</p>';
            return;
        }

        messages.forEach(msg => {
            const isMe = msg.sender === 'me';
            const b = document.createElement('div');
            b.style.maxWidth = '70%';
            b.style.padding = '0.8rem 1rem';
            b.style.borderRadius = '16px';
            b.style.marginBottom = '0.5rem';
            b.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
            b.style.background = isMe ? 'var(--color-neon-purple)' : 'rgba(255,255,255,0.1)';
            b.style.color = 'white';
            
            if (isMe) {
                b.style.borderBottomRightRadius = '0';
            } else {
                b.style.borderBottomLeftRadius = '0';
            }
            
            b.textContent = msg.text;
            chatMessages.appendChild(b);
        });
        
        // Scroll al fondo
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text || !currentRoomId) return;

        chatInput.value = '';
        
        try {
            // POST /api/chat/rooms/{id}/messages/
            // await api.post(`/chat/rooms/${currentRoomId}/messages/`, { text });
            
            // Mock local update
            if (!mockMessages[currentRoomId]) mockMessages[currentRoomId] = [];
            mockMessages[currentRoomId].push({ sender: 'me', text });
            
            // Actualizar lastMessage en room
            const room = mockRooms.find(r => r.id == currentRoomId);
            if(room) room.lastMessage = text;
            
            renderRooms();
            renderMessages(mockMessages[currentRoomId]);
            
        } catch (err) {
            console.error("Error al enviar mensaje");
        }
    }

    btnSend.onclick = sendMessage;
    chatInput.onkeypress = (e) => {
        if (e.key === 'Enter') sendMessage();
    };

    renderRooms();

    if (initialRoomId) {
        selectRoom(initialRoomId);
    }
});
