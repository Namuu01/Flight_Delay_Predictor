import React, { useEffect, useState } from "react";
import { getOptions, predictDelay } from "../services/api";

function FlightForm({
    onPrediction,
    onLoading,
    onError,
    onSourceChange,
}) {
    const today = new Date();

    const formatDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");

        return `${year}-${month}-${day}`;
    };

    const [options, setOptions] = useState({
        airlines: [],
        sources: [],
        destinations: [],
    });

    const [formData, setFormData] = useState({
        airline: "IndiGo",
        source: "Delhi",
        destination: "Mumbai",
        total_stops: 0,
        journey_date: formatDate(today),
        dep_hour: 18,
    });

    const [errors, setErrors] = useState({});

    const [loadingOptions, setLoadingOptions] = useState(true);

    const [sourceSearch, setSourceSearch] = useState("");
    const [destinationSearch, setDestinationSearch] = useState("");

    const [showSourceDropdown, setShowSourceDropdown] =
        useState(false);

    const [showDestinationDropdown, setShowDestinationDropdown] =
        useState(false);

    // ================================================================
    // LOAD OPTIONS
    // ================================================================

    useEffect(() => {
        async function loadOptions() {
            try {
                setLoadingOptions(true);

                const data = await getOptions();

                const airlines = data.airlines || [];
                const sources = data.sources || [];
                const destinations = data.destinations || [];

                setOptions({
                    airlines,
                    sources,
                    destinations,
                });

                const selectedAirline =
                    airlines.includes(formData.airline)
                        ? formData.airline
                        : airlines[0] || formData.airline;

                const selectedSource =
                    sources.includes(formData.source)
                        ? formData.source
                        : sources[0] || formData.source;

                const selectedDestination =
                    destinations.includes(formData.destination)
                        ? formData.destination
                        : destinations[0] || formData.destination;

                setFormData((previous) => ({
                    ...previous,
                    airline: selectedAirline,
                    source: selectedSource,
                    destination: selectedDestination,
                }));

                setSourceSearch(selectedSource);
                setDestinationSearch(selectedDestination);

                onSourceChange?.(selectedSource);

            } catch (error) {
                onError?.(
                    `Could not load flight options: ${error.message}`
                );
            } finally {
                setLoadingOptions(false);
            }
        }

        loadOptions();
    }, []);

    // ================================================================
    // FILTER SEARCH RESULTS
    // ================================================================

    const filteredSources = options.sources.filter((source) =>
        source
            .toLowerCase()
            .includes(sourceSearch.toLowerCase())
    );

    const filteredDestinations = options.destinations.filter(
        (destination) =>
            destination
                .toLowerCase()
                .includes(destinationSearch.toLowerCase())
    );

    // ================================================================
    // HANDLE AIRLINE
    // ================================================================

    function handleAirlineChange(event) {
        const value = event.target.value;

        setFormData((previous) => ({
            ...previous,
            airline: value,
        }));

        setErrors((previous) => ({
            ...previous,
            airline: "",
        }));
    }

    // ================================================================
    // HANDLE SOURCE SEARCH
    // ================================================================

    function handleSourceSearch(event) {
        const value = event.target.value;

        setSourceSearch(value);

        setShowSourceDropdown(true);

        setErrors((previous) => ({
            ...previous,
            source: "",
        }));
    }

    // ================================================================
    // SELECT SOURCE
    // ================================================================

    function selectSource(city) {
        setFormData((previous) => ({
            ...previous,
            source: city,
        }));

        setSourceSearch(city);

        setShowSourceDropdown(false);

        setErrors((previous) => ({
            ...previous,
            source: "",
        }));

        onSourceChange?.(city);
    }

    // ================================================================
    // HANDLE DESTINATION SEARCH
    // ================================================================

    function handleDestinationSearch(event) {
        const value = event.target.value;

        setDestinationSearch(value);

        setShowDestinationDropdown(true);

        setErrors((previous) => ({
            ...previous,
            destination: "",
        }));
    }

    // ================================================================
    // SELECT DESTINATION
    // ================================================================

    function selectDestination(city) {
        setFormData((previous) => ({
            ...previous,
            destination: city,
        }));

        setDestinationSearch(city);

        setShowDestinationDropdown(false);

        setErrors((previous) => ({
            ...previous,
            destination: "",
        }));
    }

    // ================================================================
    // HANDLE DATE
    // ================================================================

    function handleDateChange(event) {
        const value = event.target.value;

        setFormData((previous) => ({
            ...previous,
            journey_date: value,
        }));

        setErrors((previous) => ({
            ...previous,
            journey_date: "",
        }));
    }

    // ================================================================
    // HANDLE STOPS
    // ================================================================

    function increaseStops() {
        setFormData((previous) => ({
            ...previous,
            total_stops: Math.min(
                Number(previous.total_stops) + 1,
                4
            ),
        }));

        setErrors((previous) => ({
            ...previous,
            total_stops: "",
        }));
    }

    function decreaseStops() {
        setFormData((previous) => ({
            ...previous,
            total_stops: Math.max(
                Number(previous.total_stops) - 1,
                0
            ),
        }));

        setErrors((previous) => ({
            ...previous,
            total_stops: "",
        }));
    }

    // ================================================================
    // HANDLE DEPARTURE HOUR
    // ================================================================

    function handleDepartureHour(event) {
        const value = event.target.value;

        setFormData((previous) => ({
            ...previous,
            dep_hour: value,
        }));

        setErrors((previous) => ({
            ...previous,
            dep_hour: "",
        }));
    }

    // ================================================================
    // VALIDATE FORM
    // ================================================================

    function validateForm() {
        const newErrors = {};

        // Airline
        if (!formData.airline) {
            newErrors.airline =
                "Please select an airline.";
        }

        // Source
        if (!formData.source) {
            newErrors.source =
                "Please select a departure city.";
        }

        // Destination
        if (!formData.destination) {
            newErrors.destination =
                "Please select a destination city.";
        }

        // Same city
        if (
            formData.source &&
            formData.destination &&
            formData.source === formData.destination
        ) {
            newErrors.destination =
                "Departure and destination cannot be the same.";
        }

        // Date
        if (!formData.journey_date) {
            newErrors.journey_date =
                "Please select a journey date.";
        } else {
            const selectedDate =
                new Date(
                    `${formData.journey_date}T00:00:00`
                );

            if (Number.isNaN(selectedDate.getTime())) {
                newErrors.journey_date =
                    "Please enter a valid date.";
            }
        }

        // Stops
        const stops =
            Number(formData.total_stops);

        if (
            !Number.isInteger(stops) ||
            stops < 0 ||
            stops > 4
        ) {
            newErrors.total_stops =
                "Stops must be between 0 and 4.";
        }

        // Departure hour
        const depHour =
            Number(formData.dep_hour);

        if (
            !Number.isInteger(depHour) ||
            depHour < 0 ||
            depHour > 23
        ) {
            newErrors.dep_hour =
                "Please select a valid departure hour.";
        }

        setErrors(newErrors);

        return Object.keys(newErrors).length === 0;
    }

    // ================================================================
    // SUBMIT
    // ================================================================

    async function handleSubmit(event) {
        event.preventDefault();

        onError?.("");

        const isValid = validateForm();

        if (!isValid) {
            onError?.(
                "Please correct the highlighted fields before continuing."
            );

            return;
        }

        try {
            onLoading?.(true);

            // Split date into backend-compatible values
            const [year, month, day] =
                formData.journey_date.split("-");

            const prediction = await predictDelay({
                airline: formData.airline,
                source: formData.source,
                destination: formData.destination,
                total_stops: Number(formData.total_stops),
                journey_year: Number(year),
                journey_month: Number(month),
                journey_day: Number(day),
                dep_hour: Number(formData.dep_hour),
            });

            onPrediction?.({
                ...prediction,

                flightDetails: {
                    airline: formData.airline,
                    source: formData.source,
                    destination: formData.destination,
                    total_stops: Number(formData.total_stops),
                    journey_year: Number(year),
                    journey_month: Number(month),
                    journey_day: Number(day),
                    dep_hour: Number(formData.dep_hour),
                },
            });

        } catch (error) {
            onError?.(
                `Prediction failed: ${error.message}`
            );

        } finally {
            onLoading?.(false);
        }
    }

    // ================================================================
    // FORM
    // ================================================================

    return (
        <form
            className="flight-form"
            onSubmit={handleSubmit}
            noValidate
        >

            {/* ========================================================
                HEADER
            ======================================================== */}

            <div className="form-header">

                <p className="form-tag">
                    FLIGHT DETAILS
                </p>

                <h2>
                    Enter Your Flight Information
                </h2>

                <p>
                    Provide your flight details and our AI model will
                    automatically use live weather conditions for the prediction.
                </p>

            </div>

            <div className="form-grid">

                {/* ====================================================
                    AIRLINE
                ==================================================== */}

                <div className="form-group">

                    <label htmlFor="airline">
                        Airline
                    </label>

                    <select
                        id="airline"
                        name="airline"
                        value={formData.airline}
                        onChange={handleAirlineChange}
                        disabled={loadingOptions}
                    >
                        <option value="">
                            Select Airline
                        </option>

                        {options.airlines.map((airline) => (
                            <option
                                key={airline}
                                value={airline}
                            >
                                {airline}
                            </option>
                        ))}
                    </select>

                    {errors.airline && (
                        <span className="field-error">
                            ⚠️ {errors.airline}
                        </span>
                    )}

                </div>

                {/* ====================================================
                    DEPARTURE CITY SEARCH
                ==================================================== */}

                <div className="form-group">

                    <label htmlFor="source-search">
                        Departure City
                    </label>

                    <div className="search-select">

                        <input
                            id="source-search"
                            type="text"
                            value={sourceSearch}
                            placeholder="Search departure city..."
                            onChange={handleSourceSearch}
                            onFocus={() =>
                                setShowSourceDropdown(true)
                            }
                            disabled={loadingOptions}
                            autoComplete="off"
                        />

                        <span className="search-icon">
                            🔎
                        </span>

                        {showSourceDropdown && (
                            <div className="search-dropdown">

                                {filteredSources.length > 0 ? (
                                    filteredSources.map(
                                        (city) => (
                                            <button
                                                type="button"
                                                className="search-option"
                                                key={city}
                                                onMouseDown={() =>
                                                    selectSource(city)
                                                }
                                            >
                                                ✈️ {city}
                                            </button>
                                        )
                                    )
                                ) : (
                                    <div className="no-search-results">
                                        No departure city found
                                    </div>
                                )}

                            </div>
                        )}

                    </div>

                    {errors.source && (
                        <span className="field-error">
                            ⚠️ {errors.source}
                        </span>
                    )}

                </div>

                {/* ====================================================
                    DESTINATION CITY SEARCH
                ==================================================== */}

                <div className="form-group">

                    <label htmlFor="destination-search">
                        Destination City
                    </label>

                    <div className="search-select">

                        <input
                            id="destination-search"
                            type="text"
                            value={destinationSearch}
                            placeholder="Search destination city..."
                            onChange={handleDestinationSearch}
                            onFocus={() =>
                                setShowDestinationDropdown(true)
                            }
                            disabled={loadingOptions}
                            autoComplete="off"
                        />

                        <span className="search-icon">
                            🔎
                        </span>

                        {showDestinationDropdown && (
                            <div className="search-dropdown">

                                {filteredDestinations.length > 0 ? (
                                    filteredDestinations.map(
                                        (city) => (
                                            <button
                                                type="button"
                                                className="search-option"
                                                key={city}
                                                onMouseDown={() =>
                                                    selectDestination(city)
                                                }
                                            >
                                                📍 {city}
                                            </button>
                                        )
                                    )
                                ) : (
                                    <div className="no-search-results">
                                        No destination city found
                                    </div>
                                )}

                            </div>
                        )}

                    </div>

                    {errors.destination && (
                        <span className="field-error">
                            ⚠️ {errors.destination}
                        </span>
                    )}

                </div>

                {/* ====================================================
                    NUMBER OF STOPS
                ==================================================== */}

                <div className="form-group">

                    <label>
                        Number of Stops
                    </label>

                    <div className="stops-control">

                        <button
                            type="button"
                            className="stops-button"
                            onClick={decreaseStops}
                            disabled={
                                Number(formData.total_stops) === 0
                            }
                            aria-label="Decrease number of stops"
                        >
                            −
                        </button>

                        <div className="stops-value">

                            <strong>
                                {formData.total_stops}
                            </strong>

                            <span>
                                {Number(formData.total_stops) === 1
                                    ? "Stop"
                                    : "Stops"}
                            </span>

                        </div>

                        <button
                            type="button"
                            className="stops-button"
                            onClick={increaseStops}
                            disabled={
                                Number(formData.total_stops) === 4
                            }
                            aria-label="Increase number of stops"
                        >
                            +
                        </button>

                    </div>

                    {errors.total_stops && (
                        <span className="field-error">
                            ⚠️ {errors.total_stops}
                        </span>
                    )}

                </div>

                {/* ====================================================
                    JOURNEY DATE
                ==================================================== */}

                <div className="form-group">

                    <label htmlFor="journey_date">
                        Journey Date
                    </label>

                    <div className="date-input-wrapper">

                        <input
                            id="journey_date"
                            name="journey_date"
                            type="date"
                            value={formData.journey_date}
                            onChange={handleDateChange}
                        />

                        <span className="date-icon">
                            📅
                        </span>

                    </div>

                    {errors.journey_date && (
                        <span className="field-error">
                            ⚠️ {errors.journey_date}
                        </span>
                    )}

                </div>

                {/* ====================================================
                    DEPARTURE HOUR
                ==================================================== */}

                <div className="form-group">

                    <label htmlFor="dep_hour">
                        Departure Hour
                    </label>

                    <select
                        id="dep_hour"
                        name="dep_hour"
                        value={formData.dep_hour}
                        onChange={handleDepartureHour}
                    >
                        {Array.from(
                            { length: 24 },
                            (_, hour) => (
                                <option
                                    key={hour}
                                    value={hour}
                                >
                                    {String(hour).padStart(2, "0")}:00
                                </option>
                            )
                        )}
                    </select>

                    {errors.dep_hour && (
                        <span className="field-error">
                            ⚠️ {errors.dep_hour}
                        </span>
                    )}

                </div>

            </div>

            {/* ========================================================
                WEATHER NOTICE
            ======================================================== */}

            <div className="weather-notice">

                <span>
                    🌦️
                </span>

                <div>

                    <strong>
                        Live Weather Enabled
                    </strong>

                    <p>
                        Current weather for the departure city will be
                        automatically fetched from the backend before prediction.
                    </p>

                </div>

            </div>

            {/* ========================================================
                SUBMIT
            ======================================================== */}

            <button
                type="submit"
                className="predict-button"
                disabled={loadingOptions}
            >
                {loadingOptions
                    ? "Loading Options..."
                    : "✈️ Predict Flight Delay"}
            </button>

        </form>
    );
}

export default FlightForm;