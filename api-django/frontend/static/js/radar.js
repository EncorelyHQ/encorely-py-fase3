/**
 * Radar de compatibilidad.
 * Consume /matches/radar/ (sugerencias calculadas por la IA — similitud del coseno
 * sobre el ADN musical) y permite enviar solicitudes de match reales.
 */
document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    const requiredSwipes = 25;
    const lockedDiv = document.getElementById('radar-locked');
    const contentDiv = document.getElementById('radar-content');

    init();

    async function init() {
        try {
            const radar = await api.get('/matches/radar/');
            lockedDiv.style.display = 'none';
            contentDiv.style.display = 'block';
            renderMatches(radar.suggestions || []);
        } catch (err) {
            // 403 → aún no alcanza los 25 swipes: mostrar el estado bloqueado.
            if (err && err.status === 403) {
                showLocked();
            } else {
                console.error('Error cargando el radar:', err);
                contentDiv.style.display = 'block';
                document.getElementById('radar-grid').innerHTML =
                    '<p style="color: var(--color-text-muted);">No se pudo cargar el radar.</p>';
            }
        }
    }

    async function showLocked() {
        let swipes = 0;
        try {
            const me = await api.get('/auth/me/');
            swipes = me.swipe_count || 0;
        } catch (_) { /* usa 0 */ }

        lockedDiv.style.display = 'block';
        contentDiv.style.display = 'none';
        document.getElementById('radar-lock-progress-text').textContent =
            `${swipes} / ${requiredSwipes} Deslices`;
        document.getElementById('radar-lock-progress-fill').style.width =
            `${Math.min((swipes / requiredSwipes) * 100, 100)}%`;
    }

    function avatar(name, color) {
        const letter = (name || '?').trim().charAt(0).toUpperCase();
        return `<div style="width:100px;height:100px;border-radius:50%;margin:0 auto 1rem;
                display:flex;align-items:center;justify-content:center;font-size:2.5rem;font-weight:800;
                color:#000;background:${color};border:3px solid ${color};">${letter}</div>`;
    }

    function renderMatches(matches) {
        const grid = document.getElementById('radar-grid');
        grid.innerHTML = '';

        if (!matches.length) {
            grid.innerHTML =
                '<p style="color: var(--color-text-muted);">Aún no hay sugerencias compatibles. ¡Sigue descubriendo música!</p>';
            return;
        }

        matches.forEach(m => {
            const pct = Math.round((m.compatibility_score || 0) * 100);
            let color = 'var(--color-neon-green)';
            if (pct < 85) color = 'var(--color-neon-blue)';
            if (pct < 80) color = 'var(--color-text-secondary)';

            const name = m.display_name || m.username;
            const card = document.createElement('div');
            card.className = 'panel';
            card.style.textAlign = 'center';
            card.style.padding = '1.5rem';
            card.innerHTML = `
                ${avatar(name, color)}
                <h3 style="margin-bottom: 0.2rem;">${name}</h3>
                <p style="color: var(--color-text-secondary); font-size: 0.9rem; margin-bottom: 1rem;">📍 ${m.city || '—'}</p>
                <div style="font-size: 1.5rem; font-weight: 800; color: ${color}; margin-bottom: 1rem;">${pct}% Compatibilidad</div>
                <button class="btn btn-primary" style="width: 100%; padding: 0.5rem;" onclick="connect(${m.user_id}, this)">Conectar</button>
            `;
            grid.appendChild(card);
        });
    }

    window.connect = async (targetUserId, btn) => {
        btn.disabled = true;
        btn.textContent = 'Enviando...';
        try {
            await api.post('/matches/', { other_user_id: targetUserId });
            btn.textContent = '¡Solicitud enviada!';
            btn.style.background = 'var(--color-neon-green)';
            btn.style.color = '#000';
        } catch (err) {
            console.error('Error al conectar:', err);
            const detail = err && err.data ? (err.data.detail || JSON.stringify(err.data)) : 'Error';
            btn.textContent = typeof detail === 'string' ? detail.slice(0, 40) : 'Error';
            setTimeout(() => { btn.disabled = false; btn.textContent = 'Conectar'; }, 2500);
        }
    };
});
