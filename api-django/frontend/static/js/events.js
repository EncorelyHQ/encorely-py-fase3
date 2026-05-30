/**
 * Eventos y asistencia.
 * Consume datos reales: GET /events/ y POST /events/{id}/attend/.
 */
document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    const eventsList = document.getElementById('events-list');
    const cityFilter = document.getElementById('city-filter');

    let allEvents = [];

    const normalize = (s) =>
        (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().trim();

    async function fetchEvents() {
        try {
            const response = await api.get('/events/');
            allEvents = Array.isArray(response) ? response : (response.results || []);
            applyFilter();
        } catch (error) {
            console.error('Error cargando eventos:', error);
            eventsList.innerHTML =
                '<p style="text-align:center;color:var(--color-text-muted);">No se pudieron cargar los eventos.</p>';
        }
    }

    function applyFilter() {
        const selected = cityFilter.value;
        if (selected === 'all') {
            renderEvents(allEvents);
        } else {
            renderEvents(allEvents.filter(ev => normalize(ev.city) === normalize(selected)));
        }
    }

    function renderEvents(events) {
        eventsList.innerHTML = '';
        if (!events.length) {
            eventsList.innerHTML =
                '<p style="text-align: center; color: var(--color-text-muted);">No hay eventos en esta ciudad.</p>';
            return;
        }

        events.forEach(ev => {
            const card = document.createElement('div');
            card.className = 'panel';
            card.style.display = 'flex';
            card.style.padding = '0';
            card.style.overflow = 'hidden';
            card.style.gap = '1.5rem';
            if (window.innerWidth < 600) card.style.flexDirection = 'column';

            const d = new Date(ev.event_date);
            const dateStr = isNaN(d) ? '' : d.toLocaleDateString('es-CO', {
                day: 'numeric', month: 'short', year: 'numeric',
            });

            card.innerHTML = `
                <div style="width:250px;min-height:200px;display:flex;align-items:center;justify-content:center;
                     background:linear-gradient(135deg,var(--color-neon-purple),var(--color-neon-pink));font-size:3rem;">🎤</div>
                <div style="padding: 1.5rem; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                    <h3 style="margin-bottom: 0.5rem; font-size: 1.3rem;">${ev.title}</h3>
                    <p style="color: var(--color-neon-blue); margin-bottom: 0.3rem; font-weight: 600;">🎸 ${ev.artist_name}</p>
                    <p style="color: var(--color-neon-blue); margin-bottom: 0.5rem; font-weight: 600;">📅 ${dateStr}</p>
                    <p style="color: var(--color-text-secondary); margin-bottom: 1.5rem;">📍 ${ev.venue_name}, ${ev.city}</p>
                    <div style="margin-top: auto;">
                        <button class="btn btn-outline" style="padding: 0.5rem 1.5rem;" onclick="attendEvent(${ev.id}, this)">Asistiré</button>
                    </div>
                </div>
            `;
            eventsList.appendChild(card);
        });
    }

    cityFilter.addEventListener('change', applyFilter);
    window.addEventListener('resize', applyFilter);

    window.attendEvent = async (eventId, btn) => {
        btn.disabled = true;
        btn.textContent = 'Procesando...';
        try {
            await api.post(`/events/${eventId}/attend/`, { has_ticket: false });
            btn.textContent = '¡Confirmado!';
            btn.style.background = 'var(--color-neon-purple)';
            btn.style.borderColor = 'var(--color-neon-purple)';
            btn.style.color = '#fff';
        } catch (err) {
            console.error('Error al confirmar asistencia:', err);
            btn.textContent = 'Error';
            btn.disabled = false;
        }
    };

    fetchEvents();
});
