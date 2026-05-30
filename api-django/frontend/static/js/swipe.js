/**
 * Lógica para la pantalla Sound-Swipe
 */

document.addEventListener('DOMContentLoaded', () => {
    // Si no está autenticado, fuera
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
    
    // Obtenemos los datos del usuario para el contador
    let userInfo = JSON.parse(sessionStorage.getItem('user_info') || '{}');
    let currentSwipes = userInfo.swipe_count || 0;
    const requiredSwipes = 25;

    // Actualiza la UI de progreso
    function updateProgress() {
        if (currentSwipes >= requiredSwipes) {
            progressFill.style.width = '100%';
            progressText.textContent = `${currentSwipes} Deslices - ¡Radar Desbloqueado!`;
            // Si ya cumplió y no quedan tarjetas, mostrar mensaje de radar
            if (currentSongIndex >= songs.length) {
                radarReadyDiv.style.display = 'block';
            }
        } else {
            const percent = (currentSwipes / requiredSwipes) * 100;
            progressFill.style.width = `${percent}%`;
            progressText.textContent = `${currentSwipes} / ${requiredSwipes} Deslices`;
        }
    }

    // Cargar canciones de la API
    async function fetchSongs() {
        try {
            // Nota: El backend todavía no tiene /api/songs/, así que por ahora simulamos
            // o hacemos una petición que devolverá 404 pero inyectamos mocks si falla.
            const response = await api.get('/songs/');
            // Manejar tanto respuesta paginada como lista plana
            songs = Array.isArray(response) ? response : (response.results || []);
            renderCards();
        } catch (error) {
            console.warn("Endpoints de canciones no listos, usando mocks para demostración...");
            songs = [
                { id: 1, title: 'Starboy', artist: 'The Weeknd', image_url: 'https://i.scdn.co/image/ab67616d0000b2734718e2b124f79258be7bc452' },
                { id: 2, title: 'Levitating', artist: 'Dua Lipa', image_url: 'https://i.scdn.co/image/ab67616d0000b273bd22dee6fa9b8bfb4be710b7' },
                { id: 3, title: 'Bad Habit', artist: 'Steve Lacy', image_url: 'https://i.scdn.co/image/ab67616d0000b273eb23ea5ec73b184fc9de1a86' },
                { id: 4, title: 'As It Was', artist: 'Harry Styles', image_url: 'https://i.scdn.co/image/ab67616d0000b273b46f74097655d7f353caab14' }
            ];
            renderCards();
        }
    }

    // Renderiza las tarjetas apiladas
    function renderCards() {
        container.querySelectorAll('.swipe-card').forEach(c => c.remove());
        
        if (songs.length === 0 || currentSongIndex >= songs.length) {
            if (currentSwipes >= requiredSwipes) {
                radarReadyDiv.style.display = 'block';
            } else {
                noMoreSongsDiv.style.display = 'block';
            }
            return;
        }

        // Renderizar de atrás hacia adelante para que la primera esté encima
        for (let i = songs.length - 1; i >= currentSongIndex; i--) {
            const song = songs[i];
            const card = document.createElement('div');
            card.className = 'swipe-card';
            card.id = `song-${song.id}`;
            card.dataset.id = song.id;
            
            // Z-index para apilarlas, y un ligero offset visual
            const offset = (i - currentSongIndex) * 5;
            card.style.zIndex = songs.length - i;
            if (offset > 0) {
                card.style.transform = `translateY(${offset}px) scale(${1 - (offset/200)})`;
                card.style.opacity = 1 - (offset/40);
            }
            
            card.innerHTML = `
                <img src="${song.image_url}" alt="${song.title}" class="swipe-card-img">
                <div class="swipe-card-info">
                    <h2 class="swipe-card-title">${song.title}</h2>
                    <p class="swipe-card-artist">${song.artist}</p>
                    <div class="swipe-controls">
                        <button class="btn-swipe nope" onclick="handleSwipe(event, ${song.id}, 'left', this)">❌</button>
                        <button class="btn-swipe like" onclick="handleSwipe(event, ${song.id}, 'right', this)">✅</button>
                    </div>
                </div>
            `;
            container.appendChild(card);
        }
    }

    // Maneja el evento de swipe
    window.handleSwipe = async (e, songId, direction, btnElement) => {
        if (e) e.stopPropagation();
        
        const card = document.getElementById(`song-${songId}`);
        if (!card) return;

        // Añadir clase de animación
        card.classList.add(`swiped-${direction}`);
        
        // Petición al backend
        try {
            const is_liked = direction === 'right';
            // await api.post('/swipes/', { song: songId, is_liked });
            console.log(`Swiped ${direction} on song ${songId}`);
            
            // Incrementar progreso en UI
            currentSwipes++;
            userInfo.swipe_count = currentSwipes;
            if(currentSwipes >= requiredSwipes) {
                userInfo.has_enough_swipes = true;
            }
            sessionStorage.setItem('user_info', JSON.stringify(userInfo));
            updateProgress();
            
        } catch (error) {
            console.error("Error al registrar swipe:", error);
            // Revertir animación si falla? Por simplicidad en MVP ignoramos el fallo visual
        }

        // Remover tarjeta después de la animación y renderizar la siguiente
        setTimeout(() => {
            currentSongIndex++;
            renderCards();
        }, 300);
    };

    // Inicializar
    updateProgress();
    fetchSongs();
});
