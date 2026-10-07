import React from "react";

function Loading() {
    return (
        <div className="loading-container">

            <div className="loading-animation">

                <div className="loading-orbit orbit-one"></div>

                <div className="loading-orbit orbit-two"></div>

                <div className="loading-plane">
                    ✈️
                </div>

            </div>

            <h3>
                Analyzing Your Flight...
            </h3>

            <p>
                Fetching live weather and generating your AI prediction.
            </p>

            <div className="loading-steps">

                <span>
                    ✓ Flight details
                </span>

                <span>
                    ✓ Live weather
                </span>

                <span className="loading-active">
                    ◌ AI prediction
                </span>

            </div>

        </div>
    );
}

export default Loading;