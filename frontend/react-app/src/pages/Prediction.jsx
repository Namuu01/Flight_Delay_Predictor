import React, { useState } from "react";

import FlightForm from "../components/FlightForm";
import WeatherCard from "../components/WeatherCard";
import PredictionResult from "../components/PredictionResult";
import Loading from "../components/Loading";

function Prediction() {
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [sourceCity, setSourceCity] = useState("Delhi");

    // ================================================================
    // HANDLE PREDICTION
    // ================================================================

    function handlePrediction(result) {
        setPrediction(result);
    }

    // ================================================================
    // HANDLE LOADING
    // ================================================================

    function handleLoading(value) {
        setLoading(value);
    }

    // ================================================================
    // HANDLE ERROR
    // ================================================================

    function handleError(message) {
        setError(message);

        if (message) {
            setPrediction(null);
        }
    }

    // ================================================================
    // HANDLE DEPARTURE CITY CHANGE
    // ================================================================

    function handleSourceChange(city) {
        setSourceCity(city);
    }

    return (
        <main className="prediction-page">

            {/* ============================================================
                PAGE HEADER
            ============================================================ */}

            <section className="prediction-hero">
                <p className="hero-tag">AI FLIGHT ANALYTICS</p>

                <h1>Predict Your Flight Delay</h1>

                <p>
                    Enter your flight details and let our machine learning
                    system analyze operational data and live weather conditions.
                </p>
            </section>

            {/* ============================================================
                ERROR MESSAGE
            ============================================================ */}

            {error && (
                <div className="error-message">
                    <span>⚠️</span>

                    <div>
                        <strong>Something went wrong</strong>

                        <p>{error}</p>
                    </div>
                </div>
            )}

            {/* ============================================================
                FLIGHT FORM + WEATHER
            ============================================================ */}

            <section className="prediction-content">

                {/* ========================================================
                    FLIGHT FORM
                ======================================================== */}

                <div className="prediction-form-section">

                    <FlightForm
                        onPrediction={handlePrediction}
                        onLoading={handleLoading}
                        onError={handleError}
                        onSourceChange={handleSourceChange}
                    />

                </div>

                {/* ========================================================
                    LIVE WEATHER
                ======================================================== */}

                <div className="prediction-side">

                    <WeatherCard city={sourceCity} />

                    {/* ====================================================
                        INFORMATION CARD
                    ==================================================== */}

                    <div className="info-card">

                        <div className="info-card-icon">
                            💡
                        </div>

                        <div>
                            <h3>How it works</h3>

                            <p>
                                Your flight details are combined with live weather
                                conditions from the departure city before being sent
                                to the AI prediction engine.
                            </p>
                        </div>

                    </div>

                </div>

            </section>

            {/* ============================================================
                LOADING
            ============================================================ */}

            {loading && (
                <section className="result-section">
                    <Loading />
                </section>
            )}

            {/* ============================================================
                PREDICTION RESULT
            ============================================================ */}

            {!loading && prediction && (
                <section className="result-section">
                    <PredictionResult result={prediction} />
                </section>
            )}

        </main>
    );
}

export default Prediction;