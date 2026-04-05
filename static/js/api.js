/**
 * API Wrapper for Store Inventory System (SIS)
 * Provides a clean interface for all backend calls.
 */
const API = {
    /**
     * Common fetch handler
     */
    async request(url, options = {}) {
        const headers = {
            'X-Requested-With': 'XMLHttpRequest',
            ...options.headers
        };

        // Don't set Content-Type if using FormData (browser will set bridge/boundary)
        if (!options.body || !(options.body instanceof FormData)) {
            if (!headers['Content-Type']) {
                headers['Content-Type'] = 'application/json';
            }
        }

        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (csrfToken && (options.method === 'POST' || options.method === 'PUT' || options.method === 'DELETE')) {
            headers['X-CSRFToken'] = csrfToken;
        }

        const response = await fetch(url, { 
            ...options,
            headers
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({ message: 'An unexpected error occurred.' }));
            throw new Error(error.message || `Error ${response.status}: ${response.statusText}`);
        }

        return response.json();
    },

    /**
     * Inventory APIs
     */
    async getProducts() {
        return this.request('/store/data');
    },

    async addProduct(data) {
        // For traditional multipart forms, we might not use JSON
        const isFormData = data instanceof FormData;
        return this.request('/add_product', {
            method: 'POST',
            body: isFormData ? data : JSON.stringify(data)
        });
    },

    async deleteProduct(productId) {
        return this.request(`/delete_product/${productId}`, { method: 'POST' });
    },

    /**
     * Student & Assignment APIs
     */
    async assignProduct(studentId, productId, quantity = 1) {
        return this.request(`/assign_product/${studentId}`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity })
        });
    },

    async returnProduct(studentId, productId) {
        const formData = new FormData();
        formData.append('productId', productId);
        return this.request(`/return_product/${studentId}`, {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
    },

    /**
     * Analytics & Notifications
     */
    async getAnalytics() {
        return this.request('/api/analytics');
    }
};

window.API = API;
