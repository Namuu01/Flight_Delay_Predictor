// ================================================================
// FLIGHT DELAY PREDICTION FRONTEND - API SERVICE
// ================================================================

// Backend API URL
const API_BASE_URL = "http://127.0.0.1:8000";

// ================================================================
// GENERIC API REQUEST HELPER
// ================================================================

async function apiRequest(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
        ...options,
    });

    if (!response.ok) {
        let errorMessage = `API Error: ${response.status}`;

        try {
            const errorData = await response.json();

            if (errorData.detail) {
                errorMessage =
                    typeof errorData.detail === "string"
                        ? errorData.detail
                        : JSON.stringify(errorData.detail);
            }
        } catch {
            // Keep default error message
        }

        throw new Error(errorMessage);
    }

    return response.json();
}

// ================================================================
// HEALTH CHECK
// ================================================================

export async function checkHealth() {
    return apiRequest("/health");
}

// ================================================================
// GET AIRLINES, SOURCES AND DESTINATIONS
// ================================================================

export async function getOptions() {
    return apiRequest("/options");
}

// ================================================================
// GET LIVE WEATHER FOR A CITY
// ================================================================

export async function getWeather(city) {
    if (!city) {
        throw new Error("Source city is required to fetch weather.");
    }

    return apiRequest(`/weather/${encodeURIComponent(city)}`);
}

// ================================================================
// PREDICT FLIGHT DELAY
// ================================================================

export async function predictDelay(flightData) {
    return apiRequest("/predict", {
        method: "POST",
        body: JSON.stringify({
            airline: flightData.airline,
            source: flightData.source,
            destination: flightData.destination,
            total_stops: Number(flightData.total_stops),
            journey_year: Number(flightData.journey_year),
            journey_month: Number(flightData.journey_month),
            journey_day: Number(flightData.journey_day),
            dep_hour: Number(flightData.dep_hour),

            // Weather is intentionally omitted.
            // Backend automatically fetches live weather
            // when these values are not provided.
        }),
    });
}

// ================================================================
// EXPORT BASE URL
// ================================================================

export { API_BASE_URL };