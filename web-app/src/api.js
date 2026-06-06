// Central API Configuration for FinSights
// Uses Vite's environment variables to switch between localhost and live server

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Standardized fetch wrapper that automatically includes the base URL
 * and can be expanded to include JWT Bearer tokens.
 */
export async function apiFetch(endpoint, options = {}) {
    // 1. Get JWT from localStorage (assuming it's stored there after Firebase Auth)
    const token = localStorage.getItem("finsights_jwt");
    
    // 2. Set default headers
    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    };
    
    // 3. Inject Authorization header if token exists
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    // 4. Construct full URL and execute
    const url = `${API_BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });
        
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("API Request Failed:", error);
        throw error;
    }
}
