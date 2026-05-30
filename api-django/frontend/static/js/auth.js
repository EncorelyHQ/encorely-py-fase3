document.addEventListener('DOMContentLoaded', () => {
    // ======== SISTEMA DE NOTIFICACIONES (TOAST) ========
    const showToast = (message, type = 'info') => {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = '🔔';
        if (type === 'success') icon = '✅';
        if (type === 'error') icon = '❌';

        toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
        container.appendChild(toast);

        // Auto-eliminar después de 4 segundos
        setTimeout(() => {
            toast.style.animation = 'toastFadeOut 0.5s ease-out forwards';
            setTimeout(() => toast.remove(), 500);
        }, 4000);
    };

    const clearErrors = (formId) => {
        const form = document.getElementById(formId);
        if (!form) return;
        form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.style.display = 'none';
            el.textContent = '';
        });
        form.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));
        
        const generalError = form.querySelector('.form-error');
        if (generalError) generalError.style.display = 'none';
    };

    const renderErrors = (formId, errors) => {
        const form = document.getElementById(formId);
        if (!form) return;

        // Si es un string, mostrar en error general
        if (typeof errors === 'string') {
            const generalError = form.querySelector('.form-error');
            if (generalError) {
                generalError.textContent = errors;
                generalError.style.display = 'block';
            }
            showToast(errors, 'error');
            return;
        }

        // Si es un objeto de DRF { field: [errors] }
        Object.keys(errors).forEach(field => {
            const errorMsg = Array.isArray(errors[field]) ? errors[field][0] : errors[field];
            
            // Intentar encontrar el input y su feedback div
            const input = form.querySelector(`[id*="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const feedback = input.parentElement.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.textContent = errorMsg;
                    feedback.style.display = 'block';
                }
            } else if (field === 'non_field_errors' || field === 'detail') {
                const generalError = form.querySelector('.form-error');
                if (generalError) {
                    generalError.textContent = errorMsg;
                    generalError.style.display = 'block';
                }
            }
        });

        showToast("Por favor verifica los campos marcados.", "error");
    };

    // ======== LÓGICA DE LOGIN ========
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearErrors('login-form');
            
            const btnSubmit = document.getElementById('btn-login-submit');
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            btnSubmit.querySelector('.btn-text').style.display = 'none';
            btnSubmit.querySelector('.btn-spinner').style.display = 'inline';
            btnSubmit.disabled = true;
            
            try {
                const data = await api.post('/auth/login/', { username, password });
                showToast(`¡Bienvenido de vuelta, ${data.user.display_name || data.user.username}!`, 'success');
                
                sessionStorage.setItem('access_token', data.access);
                sessionStorage.setItem('refresh_token', data.refresh);
                if (data.user) sessionStorage.setItem('user_info', JSON.stringify(data.user));
                
                setTimeout(() => {
                    const userInfo = data.user || {};
                    window.location.href = userInfo.has_enough_swipes ? '/radar/' : '/swipe/';
                }, 1000);
                
            } catch (err) {
                console.error("Login Error:", err);
                renderErrors('login-form', err.data || "Credenciales incorrectas.");
                
                btnSubmit.querySelector('.btn-text').style.display = 'inline';
                btnSubmit.querySelector('.btn-spinner').style.display = 'none';
                btnSubmit.disabled = false;
            }
        });
    }

    // ======== LÓGICA DE REGISTRO ========
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        const deptSelect = document.getElementById('reg-department');
        const citySelect = document.getElementById('reg-city');

        // (Carga de departamentos y ciudades permanece igual...)
        const loadDepartments = async () => {
            try {
                const response = await fetch('https://api-colombia.com/api/v1/Department');
                const departments = await response.json();
                
                deptSelect.innerHTML = '<option value="">Selecciona Departamento</option>';
                departments.sort((a, b) => a.name.localeCompare(b.name)).forEach(dept => {
                    const option = document.createElement('option');
                    option.value = dept.id;
                    option.textContent = dept.name;
                    deptSelect.appendChild(option);
                });
            } catch (err) {
                deptSelect.innerHTML = '<option value="">Error al cargar</option>';
            }
        };

        loadDepartments();

        deptSelect.addEventListener('change', async () => {
            const deptId = deptSelect.value;
            if (!deptId) {
                citySelect.innerHTML = '<option value="">Selecciona un departamento primero</option>';
                citySelect.disabled = true;
                return;
            }
            citySelect.disabled = true;
            citySelect.innerHTML = '<option value="">Cargando ciudades...</option>';
            try {
                const response = await fetch(`https://api-colombia.com/api/v1/Department/${deptId}/cities`);
                const cities = await response.json();
                citySelect.innerHTML = '<option value="">Selecciona Ciudad</option>';
                cities.sort((a, b) => a.name.localeCompare(b.name)).forEach(city => {
                    const option = document.createElement('option');
                    option.value = city.name;
                    option.textContent = city.name;
                    citySelect.appendChild(option);
                });
                citySelect.disabled = false;
            } catch (err) {
                citySelect.innerHTML = '<option value="">Error al cargar</option>';
            }
        });

        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            clearErrors('register-form');
            
            const btnSubmit = document.getElementById('btn-register-submit');
            
            const payload = {
                username: document.getElementById('reg-username').value,
                email: document.getElementById('reg-email').value,
                display_name: document.getElementById('reg-display-name').value,
                city: citySelect.value,
                concert_mood: document.getElementById('reg-concert-mood').value,
                password: document.getElementById('reg-password').value,
                password_confirm: document.getElementById('reg-password-confirm').value,
            };
            
            if (payload.password !== payload.password_confirm) {
                renderErrors('register-form', { password_confirm: "Las contraseñas no coinciden." });
                return;
            }

            if (!payload.city) {
                renderErrors('register-form', { city: "Por favor selecciona una ciudad." });
                return;
            }

            btnSubmit.querySelector('.btn-text').style.display = 'none';
            btnSubmit.querySelector('.btn-spinner').style.display = 'inline';
            btnSubmit.disabled = true;
            
            try {
                await api.post('/auth/register/', payload);
                showToast("¡Cuenta creada exitosamente! Iniciando sesión...", "success");
                
                const loginData = await api.post('/auth/login/', { 
                    username: payload.username, 
                    password: payload.password 
                });
                
                sessionStorage.setItem('access_token', loginData.access);
                sessionStorage.setItem('refresh_token', loginData.refresh);
                if (loginData.user) sessionStorage.setItem('user_info', JSON.stringify(loginData.user));
                
                setTimeout(() => {
                    window.location.href = '/swipe/';
                }, 1500);
                
            } catch (err) {
                console.error("Register Error:", err);
                renderErrors('register-form', err.data || "Error en el registro.");
                
                btnSubmit.querySelector('.btn-text').style.display = 'inline';
                btnSubmit.querySelector('.btn-spinner').style.display = 'none';
                btnSubmit.disabled = false;
            }
        });
    }
});
