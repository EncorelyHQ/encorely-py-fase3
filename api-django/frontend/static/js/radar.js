document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    const userInfo = JSON.parse(sessionStorage.getItem('user_info') || '{}');
    const requiredSwipes = 25;
    const currentSwipes = userInfo.swipe_count || 0;

    const lockedDiv = document.getElementById('radar-locked');
    const contentDiv = document.getElementById('radar-content');

    if (currentSwipes < requiredSwipes && !userInfo.has_enough_swipes) {
        lockedDiv.style.display = 'block';
        document.getElementById('radar-lock-progress-text').textContent = `${currentSwipes} / ${requiredSwipes} Deslices`;
        document.getElementById('radar-lock-progress-fill').style.width = `${(currentSwipes/requiredSwipes)*100}%`;
    } else {
        contentDiv.style.display = 'block';
        fetchMatches();
    }

    async function fetchMatches() {
        try {
            // Intento real (en el futuro)
            // const response = await api.get('/matches/');
            // renderMatches(response.results);
            throw new Error('Mocks');
        } catch (error) {
            // Datos Mockeados
            const mocks = [
                { id: 101, display_name: 'Ana García', city: 'Medellín', concert_mood: 'Front Row', match_percentage: 95, avatar: 'https://i.pravatar.cc/150?u=1' },
                { id: 102, display_name: 'Carlos Ruiz', city: 'Bogotá', concert_mood: 'Moshpit', match_percentage: 88, avatar: 'https://i.pravatar.cc/150?u=2' },
                { id: 103, display_name: 'Luisa F.', city: 'Medellín', concert_mood: 'Chiller', match_percentage: 82, avatar: 'https://i.pravatar.cc/150?u=3' },
                { id: 104, display_name: 'David', city: 'Cali', concert_mood: 'VIP', match_percentage: 75, avatar: 'https://i.pravatar.cc/150?u=4' }
            ];
            renderMatches(mocks);
        }
    }

    function renderMatches(matches) {
        const grid = document.getElementById('radar-grid');
        grid.innerHTML = '';

        matches.forEach(m => {
            const card = document.createElement('div');
            card.className = 'panel';
            card.style.textAlign = 'center';
            card.style.padding = '1.5rem';
            
            // Color según match
            let matchColor = 'var(--color-neon-green)';
            if (m.match_percentage < 85) matchColor = 'var(--color-neon-blue)';
            if (m.match_percentage < 80) matchColor = 'var(--color-text-secondary)';

            card.innerHTML = `
                <img src="${m.avatar}" alt="${m.display_name}" style="width: 100px; height: 100px; border-radius: 50%; border: 3px solid ${matchColor}; margin-bottom: 1rem; object-fit: cover;">
                <h3 style="margin-bottom: 0.2rem;">${m.display_name}</h3>
                <p style="color: var(--color-text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">📍 ${m.city} • ${m.concert_mood}</p>
                <div style="font-size: 1.5rem; font-weight: 800; color: ${matchColor}; margin-bottom: 1rem;">${m.match_percentage}% Compatibilidad</div>
                <button class="btn btn-primary" style="width: 100%; padding: 0.5rem;" onclick="connect(${m.id}, this)">Conectar</button>
            `;
            grid.appendChild(card);
        });
    }

    window.connect = async (targetId, btn) => {
        btn.disabled = true;
        btn.textContent = 'Conectando...';
        
        try {
            // await api.post('/matches/', { target_user_id: targetId });
            setTimeout(() => {
                btn.textContent = '¡Match!';
                btn.style.background = 'var(--color-neon-green)';
                btn.style.color = '#000';
                
                // Redirigir al chat
                setTimeout(() => {
                    window.location.href = `/chat/?room=${targetId}`;
                }, 800);
            }, 500);
        } catch (err) {
            btn.textContent = 'Error';
            btn.disabled = false;
        }
    };
});
