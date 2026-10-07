import React, { useEffect, useState } from "react";
import { getWeather } from "../services/api";

function WeatherCard({ city }) {
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!city) {
            setWeather(null);
            return;
        }

        async function loadWeather() {
            try {
                setLoading(true);
                setError("");

                const data = await getWeather(city);

                setWeather(data);
            } catch (err) {
                setWeather(null);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        }

        loadWeather();
    }, [city]);

    // ================================================================
    // LOADING STATE
    // ================================================================

    if (loading) {
        return (
            <section className="weather-card">
                <div className="weather-card-header">
                    <span className="weather-icon">🌦️</span>

                    <div>
                        <p className="weather-label">LIVE WEATHER</p>
                        <h3>{city}</h3>
                    </div>
                </div>

                <div className="weather-loading">
                    Fetching current weather...
                </div>
            </section>
        );
    }

    // ================================================================
    // ERROR STATE
    // ================================================================

    if (error) {
        return (
            <section className="weather-card weather-error">
                <div className="weather-card-header">
                    <span className="weather-icon">⚠️</span>

                    <div>
                        <p className="weather-label">LIVE WEATHER</p>
                        <h3>{city}</h3>
                    </div>
                </div>

                <p className="weather-error-message">{error}</p>
            </section>
        );
    }

    // ================================================================
    // NO WEATHER YET
    // ================================================================

    if (!weather) {
        return null;
    }

    const weatherData = weather.weather || {};

    return (
        <section className="weather-card">
            <div className="weather-card-header">
                <span className="weather-icon">🌦️</span>

                <div>
                    <p className="weather-label">LIVE WEATHER</p>
                    <h3>{weather.city || city}</h3>
                </div>

                <span className="live-indicator">
                    ● LIVE
                </span>
            </div>

            <div className="weather-grid">

                {/* TEMPERATURE */}
                <div className="weather-item">
                    <span className="weather-item-icon">🌡️</span>

                    <div>
                        <span className="weather-item-label">
                            Temperature
                        </span>

                        <strong>
                            {Number(weatherData.Temperature_C ?? 0).toFixed(1)} °C
                        </strong>
                    </div>
                </div>

                {/* VISIBILITY */}
                <div className="weather-item">
                    <span className="weather-item-icon">👁️</span>

                    <div>
                        <span className="weather-item-label">
                            Visibility
                        </span>

                        <strong>
                            {Number(weatherData.Visibility_km ?? 0).toFixed(1)} km
                        </strong>
                    </div>
                </div>

                {/* WIND */}
                <div className="weather-item">
                    <span className="weather-item-icon">💨</span>

                    <div>
                        <span className="weather-item-label">
                            Wind Speed
                        </span>

                        <strong>
                            {Number(weatherData.Wind_Speed_kmh ?? 0).toFixed(1)} km/h
                        </strong>
                    </div>
                </div>

                {/* RAIN */}
                <div className="weather-item">
                    <span className="weather-item-icon">🌧️</span>

                    <div>
                        <span className="weather-item-label">
                            Precipitation
                        </span>

                        <strong>
                            {Number(weatherData.Precipitation_mm ?? 0).toFixed(1)} mm
                        </strong>
                    </div>
                </div>
            </div>
        </section>
    );
}

export default WeatherCard;