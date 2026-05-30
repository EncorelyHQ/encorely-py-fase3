document.addEventListener('DOMContentLoaded', () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    const eventsList = document.getElementById('events-list');
    const cityFilter = document.getElementById('city-filter');
    
    let allEvents = [];

    async function fetchEvents() {
        try {
            // const response = await api.get('/events/');
            // renderEvents(response.results);
            throw new Error('Mocks');
        } catch (error) {
            allEvents = [
                { id: 1, name: 'Estéreo Picnic 2026', date: '2026-03-20', city: 'bogota', city_name: 'Bogotá', location: 'Parque Simón Bolívar', image: 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?auto=format&fit=crop&w=500&q=60' },
                { id: 2, name: 'La Solar Festival', date: '2026-02-15', city: 'medellin', city_name: 'Medellín', location: 'Parque Norte', image: 'https://images.unsplash.com/photo-1540039155732-68473678d4dd?auto=format&fit=crop&w=500&q=60' },
                { id: 3, name: 'Baum Festival', date: '2026-05-18', city: 'bogota', city_name: 'Bogotá', location: 'Corferias', image: 'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=500&q=60' },
                { id: 4, name: 'Ritvales', date: '2026-11-04', city: 'medellin', city_name: 'Medellín', location: 'Parque Norte', image: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=500&q=60' }
            ];
            renderEvents(allEvents);
        }
    }

    function renderEvents(events) {
        eventsList.innerHTML = '';
        if (events.length === 0) {
            eventsList.innerHTML = '<p style="text-align: center; color: var(--color-text-muted);">No hay eventos en esta ciudad.</p>';
            return;
        }

        events.forEach(ev => {
            const card = document.createElement('div');
            card.className = 'panel';
            card.style.display = 'flex';
            card.style.padding = '0';
            card.style.overflow = 'hidden';
            card.style.gap = '1.5rem';
            
            // Si es pantalla pequeña, cambiar a columna
            if(window.innerWidth < 600) {
                card.style.flexDirection = 'column';
            }

            const d = new Date(ev.date);
            const dateStr = d.toLocaleDateString('es-CO', { day: 'numeric', month: 'short', year: 'numeric' });

            card.innerHTML = `
                <img src="${ev.image}" alt="${ev.name}" style="width: 250px; height: 100%; object-fit: cover; min-height: 200px;">
                <div style="padding: 1.5rem; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                    <h3 style="margin-bottom: 0.5rem; font-size: 1.3rem;">${ev.name}</h3>
                    <p style="color: var(--color-neon-blue); margin-bottom: 0.5rem; font-weight: 600;">📅 ${dateStr}</p>
                    <p style="color: var(--color-text-secondary); margin-bottom: 1.5rem;">📍 ${ev.location}, ${ev.city_name}</p>
                    <div style="margin-top: auto;">
                        <button class="btn btn-outline" style="padding: 0.5rem 1.5rem;" onclick="attendEvent(${ev.id}, this)">Asistiré</button>
                    </div>
                </div>
            `;
            eventsList.appendChild(card);
        });
    }

    cityFilter.addEventListener('change', (e) => {
        const selected = e.target.value;
        if (selected === 'all') {
            renderEvents(allEvents);
        } else {
            renderEvents(allEvents.filter(ev => ev.city === selected));
        }
    });

    window.attendEvent = async (eventId, btn) => {
        btn.disabled = true;
        btn.textContent = 'Procesando...';
        
        try {
            // await api.post(`/events/${eventId}/attend/`);
            setTimeout(() => {
                btn.textContent = '¡Confirmado!';
                btn.style.background = 'var(--color-neon-purple)';
                btn.style.borderColor = 'var(--color-neon-purple)';
                btn.style.color = '#fff';
            }, 500);
        } catch (err) {
            btn.textContent = 'Error';
            btn.disabled = false;
        }
    };

    // Responsive ajust
    window.addEventListener('resize', () => renderEvents(cityFilter.value === 'all' ? allEvents : allEvents.filter(e => e.city === cityFilter.value)));

    fetchEvents();
});
