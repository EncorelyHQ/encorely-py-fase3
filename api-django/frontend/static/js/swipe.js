/**
 * Lógica para la pantalla Sound-Swipe (Descubrir).
 * Consume datos reales de la API: GET /songs/ y POST /swipes/.
 */

document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    const container = document.getElementById('swipe-container');
    const progressFill = document.getElementById('swipe-progress');
    const progressText = document.getElementById('swipe-counter-text');
    const noMoreSongsDiv = document.getElementById('no-more-songs');
    const radarReadyDiv = document.getElementById('radar-ready');

    let songs = [];
    let currentSongIndex = 0;

    let userInfo = JSON.parse(sessionStorage.getItem('user_info') || '{}');
    let currentSwipes = userInfo.swipe_count || 0;
    const requiredSwipes = 25;

    // Solo actualiza la barra y el texto de progreso. El aviso de "Radar
    // desbloqueado" se muestra una sola vez al cruzar el umbral (ver handleSwipe),
    // y el panel "Ir al Radar" solo cuando se acaban las canciones (ver renderCards).
    function updateProgress() {
        if (currentSwipes >= requiredSwipes) {
            progressFill.style.width = '100%';
            progressText.textContent = `${currentSwipes} Deslices · Radar desbloqueado`;
        } else {
            const percent = (currentSwipes / requiredSwipes) * 100;
            progressFill.style.width = `${percent}%`;
            progressText.textContent = `${currentSwipes} / ${requiredSwipes} Deslices`;
        }
    }

    // Toast puntual (autodestruible) para avisos como desbloquear el Radar.
    function showToast(message) {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.cssText =
            'position:fixed;top:1.5rem;left:50%;transform:translateX(-50%);z-index:9999;' +
            'background:var(--color-neon-green);color:#000;font-weight:700;padding:0.8rem 1.4rem;' +
            'border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.4);';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 3500);
    }

    // Mantiene sincronizado el contador real (swipe_count) desde el servidor.
    async function refreshUserInfo() {
        try {
            const me = await api.get('/auth/me/');
            userInfo = { ...userInfo, ...me };
            currentSwipes = me.swipe_count || currentSwipes;
            sessionStorage.setItem('user_info', JSON.stringify(userInfo));
        } catch (err) {
            console.warn('No se pudo refrescar el perfil:', err);
        }
    }

    async function fetchSongs() {
        try {
            const response = await api.get('/songs/');
            songs = Array.isArray(response) ? response : (response.results || []);
            currentSongIndex = 0;
            renderCards();
        } catch (error) {
            console.error('Error cargando canciones:', error);
            container.querySelectorAll('.swipe-card').forEach(c => c.remove());
            noMoreSongsDiv.style.display = 'block';
        }
    }

    function cardArtwork(song) {
        if (song.image_url) {
            return `<img src="${song.image_url}" alt="${song.title}" class="swipe-card-img">`;
        }
        // Sin carátula: placeholder con degradado neón en lugar de una imagen externa.
        return `<div class="swipe-card-img" style="display:flex;align-items:center;justify-content:center;
                background:linear-gradient(135deg, var(--color-neon-purple), var(--color-neon-blue));
                font-size:4rem;">🎵</div>`;
    }

    function renderCards() {
        container.querySelectorAll('.swipe-card').forEach(c => c.remove());
        // Mientras haya cartas, ningún panel de cierre debe estar visible.
        noMoreSongsDiv.style.display = 'none';
        radarReadyDiv.style.display = 'none';

        if (songs.length === 0 || currentSongIndex >= songs.length) {
            if (currentSwipes >= requiredSwipes) {
                radarReadyDiv.style.display = 'block';
            } else {
                noMoreSongsDiv.style.display = 'block';
            }
            return;
        }

        for (let i = songs.length - 1; i >= currentSongIndex; i--) {
            const song = songs[i];
            const card = document.createElement('div');
            card.className = 'swipe-card';
            card.id = `song-${song.id}`;
            card.dataset.id = song.id;

            const offset = (i - currentSongIndex) * 5;
            card.style.zIndex = songs.length - i;
            if (offset > 0) {
                card.style.transform = `translateY(${offset}px) scale(${1 - (offset / 200)})`;
                card.style.opacity = 1 - (offset / 40);
            }

            card.innerHTML = `
                ${cardArtwork(song)}
                <div class="swipe-card-info">
                    <h2 class="swipe-card-title">${song.title}</h2>
                    <p class="swipe-card-artist">${song.artist_name || ''}</p>
                    <div class="swipe-controls">
                        <button class="btn-swipe nope" onclick="handleSwipe(event, ${song.id}, 'left', this)">❌</button>
                        <button class="btn-swipe like" onclick="handleSwipe(event, ${song.id}, 'right', this)">✅</button>
                    </div>
                </div>
            `;
            container.appendChild(card);
        }
    }

    window.handleSwipe = async (e, songId, direction, btnElement) => {
        if (e) e.stopPropagation();

        const card = document.getElementById(`song-${songId}`);
        if (!card) return;

        // Bloquea doble click mientras se procesa.
        card.querySelectorAll('.btn-swipe').forEach(b => (b.disabled = true));
        card.classList.add(`swiped-${direction}`);

        try {
            const type = direction === 'right' ? 'RIGHT' : 'LEFT';
            const before = currentSwipes;
            await api.post('/swipes/', { song: songId, type });
            await refreshUserInfo();
            updateProgress();
            // Aviso puntual solo en el momento exacto de cruzar el umbral.
            if (before < requiredSwipes && currentSwipes >= requiredSwipes) {
                showToast('🎉 ¡Desbloqueaste el Radar musical!');
            }
        } catch (error) {
            console.error('Error al registrar swipe:', error);
        }

        setTimeout(() => {
            currentSongIndex++;
            renderCards();
        }, 300);
    };

    updateProgress();
    fetchSongs();
});
