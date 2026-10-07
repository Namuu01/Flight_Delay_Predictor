import React from "react";

function Navbar({ darkMode, onThemeToggle }) {
    return (
        <nav className="navbar">
            <div className="navbar-brand">
                <span className="navbar-icon">✈️</span>
                <span>Flight Delay Predictor</span>
            </div>

            <div className="navbar-links">
                <a href="/">Home</a>
                <a href="/predict">Predict Delay</a>

                <button
                    type="button"
                    className="theme-toggle"
                    onClick={onThemeToggle}
                    aria-label={
                        darkMode ? "Switch to light mode" : "Switch to dark mode"
                    }
                    title={
                        darkMode ? "Switch to light mode" : "Switch to dark mode"
                    }
                >
                    {darkMode ? "☀️" : "🌙"}
                </button>
            </div>
        </nav>
    );
}

export default Navbar;