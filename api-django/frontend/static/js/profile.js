document.addEventListener('DOMContentLoaded', async () => {
    if (!sessionStorage.getItem('access_token')) {
        window.location.href = '/login/';
        return;
    }

    try {
        // En una app real, aquí haríamos:
        // const userData = await api.get('/auth/me/');
        
        // Mock / Cache local
        const userData = JSON.parse(sessionStorage.getItem('user_info') || '{}');
        
        if (userData) {
            document.getElementById('profile-name').textContent = userData.display_name || userData.username || 'Usuario';
            document.getElementById('profile-username').textContent = `@${userData.username || 'user'}`;
            document.getElementById('profile-swipes').textContent = userData.swipe_count || 0;
            document.getElementById('profile-mood').textContent = (userData.concert_mood || 'Desconocido').replace('_', ' ').toUpperCase();
            document.getElementById('profile-city').textContent = userData.city || 'Desconocida';
        }
    } catch (err) {
        console.error("Error cargando perfil", err);
    }
});
