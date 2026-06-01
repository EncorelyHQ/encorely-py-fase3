/**
 * EncorelyAPI - Cliente HTTP Centralizado
 * Patrón: Facade
 * 
 * Encapsula la lógica de peticiones fetch y la inyección automática
 * del token JWT en las cabeceras de cada request. Facilita la comunicación
 * con la API de Django desde el Frontend.
 */
class EncorelyAPI {
    constructor(baseURL = '/api') {
        this.baseURL = baseURL;
    }

    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
        };
        const token = sessionStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    // Intenta renovar el access token con el refresh token guardado.
    async _refreshAccessToken() {
        const refresh = sessionStorage.getItem('refresh_token');
        if (!refresh) return false;
        try {
            const resp = await fetch(`${this.baseURL}/auth/token/refresh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh }),
            });
            if (!resp.ok) return false;
            const data = await resp.json();
            sessionStorage.setItem('access_token', data.access);
            // SimpleJWT rota el refresh token: si llega uno nuevo, se reemplaza.
            if (data.refresh) sessionStorage.setItem('refresh_token', data.refresh);
            return true;
        } catch (_) {
            return false;
        }
    }

    async _request(endpoint, options = {}, allowRefresh = true) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this._getHeaders(),
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);

            // Token expirado: intenta refrescar una vez y reintentar la petición original.
            // Se evita el bucle en los propios endpoints de auth.
            const isAuthEndpoint =
                endpoint.includes('/auth/login') || endpoint.includes('/auth/token/refresh');
            if (response.status === 401 && allowRefresh && !isAuthEndpoint) {
                if (await this._refreshAccessToken()) {
                    return this._request(endpoint, options, false);
                }
                // No se pudo refrescar: limpiar sesión y volver al login.
                sessionStorage.clear();
                window.location.href = '/login/';
                return null;
            }

            const isJson = response.headers.get('content-type')?.includes('application/json');
            const data = isJson ? await response.json() : null;

            if (!response.ok) {
                throw { status: response.status, data };
            }

            return data;
        } catch (error) {
            console.error(`API Error en ${url}:`, error);
            throw error;
        }
    }

    get(endpoint, headers = {}) {
        return this._request(endpoint, { method: 'GET', headers });
    }

    post(endpoint, body, headers = {}) {
        return this._request(endpoint, { 
            method: 'POST', 
            body: JSON.stringify(body), 
            headers 
        });
    }

    put(endpoint, body, headers = {}) {
        return this._request(endpoint, { 
            method: 'PUT', 
            body: JSON.stringify(body), 
            headers 
        });
    }

    delete(endpoint, headers = {}) {
        return this._request(endpoint, { method: 'DELETE', headers });
    }
}

// Instancia global para ser usada en todo el frontend
const api = new EncorelyAPI();
