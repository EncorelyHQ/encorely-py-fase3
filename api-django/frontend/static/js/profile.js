document.addEventListener('DOMContentLoaded', async () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    try {
        // Perfil real desde la API; cae al cache local solo si la petición falla.
        let userData;
        try {
            userData = await api.get('/auth/me/');
            sessionStorage.setItem('user_info', JSON.stringify(userData));
        } catch (_) {
            userData = JSON.parse(sessionStorage.getItem('user_info') || '{}');
        }

        document.getElementById('profile-name').textContent = userData.display_name || userData.username || 'Usuario';
        document.getElementById('profile-username').textContent = `@${userData.username || 'user'}`;
        document.getElementById('profile-swipes').textContent = userData.swipe_count || 0;
        document.getElementById('profile-mood').textContent = (userData.concert_mood || 'Desconocido').replace('_', ' ').toUpperCase();
        document.getElementById('profile-city').textContent = userData.city || 'Desconocida';
    } catch (err) {
        console.error('Error cargando perfil', err);
    }
});
