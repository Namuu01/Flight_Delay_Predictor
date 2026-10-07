import React from "react";

function Home() {
    return (
        <main className="home-page">
            <section className="hero-section">
                <div className="hero-content">
                    <p className="hero-tag">AI-POWERED FLIGHT ANALYTICS</p>

                    <h1>
                        Predict Flight Delays
                        <br />
                        Before They Happen
                    </h1>

                    <p className="hero-description">
                        Get intelligent flight delay predictions using machine learning,
                        operational data, and real-time weather conditions.
                    </p>

                    <div className="hero-actions">
                        <a href="/predict" className="primary-button">
                            Predict Flight Delay
                        </a>
                    </div>
                </div>

                <div className="hero-visual">
                    <div className="airplane-icon">✈️</div>

                    <div className="weather-info">
                        <span>🌦️</span>
                        <span>Live Weather</span>
                    </div>

                    <div className="prediction-info">
                        <span>🤖</span>
                        <span>AI Prediction</span>
                    </div>
                </div>
            </section>

            <section className="features-section">
                <h2>How It Works</h2>

                <div className="feature-grid">
                    <div className="feature-card">
                        <div className="feature-icon">✈️</div>
                        <h3>Flight Details</h3>
                        <p>
                            Enter your airline, route, stops, travel date, and departure
                            time.
                        </p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon">🌦️</div>
                        <h3>Live Weather</h3>
                        <p>
                            Current weather conditions are automatically fetched for your
                            departure city.
                        </p>
                    </div>

                    <div className="feature-card">
                        <div className="feature-icon">🤖</div>
                        <h3>AI Prediction</h3>
                        <p>
                            TabNet and XGBoost work together to estimate the expected flight
                            delay.
                        </p>
                    </div>
                </div>
            </section>
        </main>
    );
}

export default Home;