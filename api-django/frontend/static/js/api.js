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

    async _request(endpoint, options = {}) {
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
            
            // Si es un error 401 (no autorizado), podríamos manejar refresh token o redirigir
            if (response.status === 401) {
                console.warn("API: No autorizado o token expirado.");
                // Opcional: intentar refresh token automáticamente o redirigir
                // window.location.href = '/login/';
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
