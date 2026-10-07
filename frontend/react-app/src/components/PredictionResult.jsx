import React from "react";

function PredictionResult({ result }) {
    if (!result) {
        return null;
    }

    const forecast = result.forecast || "";

    // ================================================================
    // EXTRACT PREDICTED DELAY
    // ================================================================

    const delayMatch = forecast.match(
        /Predicted Delay:\s*(\d+(?:\.\d+)?)\s*minutes/i
    );

    const predictedDelay = delayMatch
        ? Math.round(Number(delayMatch[1]))
        : null;

    // ================================================================
    // DETERMINE RISK FROM PREDICTED DELAY
    // ================================================================

    let riskLevel = "UNKNOWN";
    let delayStatus = "Delay Status";
    let riskIcon = "⚪";

    if (predictedDelay !== null) {

        if (predictedDelay < 15) {
            riskLevel = "LOW";
            delayStatus = "Slight Delay: ";
            riskIcon = "🟢";

        } else if (predictedDelay < 60) {
            riskLevel = "MEDIUM";
            delayStatus = "Moderate Delay: ";
            riskIcon = "🟡";

        } else {
            riskLevel = "HIGH";
            delayStatus = "High Delay: ";
            riskIcon = "🔴";
        }
    }

    // ================================================================
    // EXTRACT MAIN REASONS
    // ================================================================

    const reasonsSection = forecast.match(
        /📌 Main Reasons:\s*([\s\S]*?)(?=\n\n🌦️ Live Weather:|$)/i
    );

    let reasons = [];

    if (reasonsSection) {
        reasons = reasonsSection[1]
            .split("\n")
            .map((reason) =>
                reason.replace(/^•\s*/, "").trim()
            )
            .filter(Boolean);
    }

    // ================================================================
    // WEATHER USED BY MODEL
    // ================================================================

    const weather = result.weather_used || {};

    return (
        <section className="prediction-result">

            {/* ========================================================
                RESULT HEADER
            ======================================================== */}

            <div className="result-header">

                <div>

                    <p className="result-label">
                        AI PREDICTION
                    </p>

                    <h2>
                        Flight Delay Forecast
                    </h2>

                </div>

                <span className="result-icon">
                    🤖
                </span>

            </div>

            {/* ========================================================
                MAIN PREDICTION
            ======================================================== */}

            <div className="prediction-main">

                <div className="delay-value">

                    {predictedDelay !== null
                        ? predictedDelay
                        : "--"}

                    <span>
                        minutes
                    </span>

                </div>

                <div
                    className={`risk-badge risk-${riskLevel.toLowerCase()}`}
                >

                    <span>
                        {riskIcon}
                    </span>

                    <span>
                        {riskLevel} RISK
                    </span>

                </div>

            </div>

            {/* ========================================================
                DELAY STATUS
            ======================================================== */}

            <div
                className={`delay-status status-${riskLevel.toLowerCase()}`}
            >

                <strong>
                    {delayStatus}
                </strong>

                <span>
                    {predictedDelay !== null
                        ? predictedDelay < 15
                            ? "Expected to have only a slight impact on your journey."
                            : predictedDelay < 60
                                ? "A moderate delay may affect your journey."
                                : "A significant delay is expected."
                        : "Unable to determine delay status."}
                </span>

            </div>

            {/* ========================================================
                MAIN REASONS
            ======================================================== */}

            <div className="prediction-reasons">

                <h3>
                    📌 Main Reasons
                </h3>

                {reasons.length > 0 ? (
                    <ul>
                        {reasons.map((reason, index) => (
                            <li key={index}>
                                {reason}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>
                        No major risk factors detected.
                    </p>
                )}

            </div>

            {/* ========================================================
                WEATHER USED
            ======================================================== */}

            <div className="prediction-weather">

                <h3>
                    🌦️ Weather Used for Prediction
                </h3>

                <div className="prediction-weather-grid">

                    <div>

                        <span>
                            Temperature
                        </span>

                        <strong>
                            {weather.temperature_c !== undefined
                                ? `${Number(
                                    weather.temperature_c
                                ).toFixed(1)} °C`
                                : "--"}
                        </strong>

                    </div>

                    <div>

                        <span>
                            Visibility
                        </span>

                        <strong>
                            {weather.visibility_km !== undefined
                                ? `${Number(
                                    weather.visibility_km
                                ).toFixed(1)} km`
                                : "--"}
                        </strong>

                    </div>

                    <div>

                        <span>
                            Wind
                        </span>

                        <strong>
                            {weather.wind_speed_kmh !== undefined
                                ? `${Number(
                                    weather.wind_speed_kmh
                                ).toFixed(1)} km/h`
                                : "--"}
                        </strong>

                    </div>

                    <div>

                        <span>
                            Rain
                        </span>

                        <strong>
                            {weather.precipitation_mm !== undefined
                                ? `${Number(
                                    weather.precipitation_mm
                                ).toFixed(1)} mm`
                                : "--"}
                        </strong>

                    </div>

                </div>

            </div>

            {/* ========================================================
                MODEL INFORMATION
            ======================================================== */}

            <div className="model-info">

                <span>
                    🧠
                </span>

                <p>
                    Prediction generated using the TabNet + XGBoost
                    ensemble model with live weather conditions.
                </p>

            </div>

        </section>
    );
}

export default PredictionResult;
