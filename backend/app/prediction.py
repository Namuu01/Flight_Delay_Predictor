import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

# Ensure UTF-8 output on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Standard Airlines, Sources, Destinations
DEFAULT_AIRLINES = [
    'Air India', 'AirAsia India', 'Akasa Air', 'Alliance Air', 'GoAir',
    'IndiGo', 'SpiceJet', 'Star Air', 'TruJet', 'Vistara'
]
DEFAULT_CITIES = [
    'Ahmedabad', 'Bangalore', 'Bhubaneswar', 'Chennai', 'Cochin',
    'Delhi', 'Goa', 'Guwahati', 'Hyderabad', 'Indore', 'Jaipur',
    'Kolkata', 'Lucknow', 'Mumbai', 'Nagpur', 'Patna', 'Pune',
    'Raipur', 'Surat', 'Varanasi'
]

# Load dropdown choices dynamically if dataset exists
raw_airlines = DEFAULT_AIRLINES
raw_sources = DEFAULT_CITIES
raw_destinations = DEFAULT_CITIES

flight_csv = DATA_DIR / "clean_flights_9_columns.csv"
if flight_csv.exists():
    try:
        _sample_df = pd.read_csv(flight_csv)
        if "airline" in _sample_df.columns:
            raw_airlines = sorted(_sample_df["airline"].dropna().unique().tolist())
        if "Source" in _sample_df.columns:
            raw_sources = sorted(_sample_df["Source"].dropna().unique().tolist())
        if "destination" in _sample_df.columns:
            raw_destinations = sorted(_sample_df["destination"].dropna().unique().tolist())
    except Exception as _e:
        pass

# ---------------------------------------------------------------
# WEATHER CONDITION EXPLANATION
# ---------------------------------------------------------------

def explain_weather(temperature, visibility, wind_speed, rain):
    reasons = []

    # Temperature analysis
    if temperature < 10:
        temp_reason = (
            f"🌡️ Temperature: {temperature:.1f}°C — "
            "Very cold conditions may increase operational risk."
        )
    elif temperature < 24:
        temp_reason = (
            f"🌡️ Temperature: {temperature:.1f}°C — "
            "Cool and generally favorable conditions."
        )
    elif temperature <= 32:
        temp_reason = (
            f"🌡️ Temperature: {temperature:.1f}°C — "
            "Moderate temperature with low direct weather concern."
        )
    elif temperature <= 40:
        temp_reason = (
            f"🌡️ Temperature: {temperature:.1f}°C — "
            "High temperature may increase operational stress."
        )
    else:
        temp_reason = (
            f"🌡️ Temperature: {temperature:.1f}°C — "
            "Very high temperature may increase operational risk."
        )
    reasons.append(temp_reason)

    # Visibility analysis
    if visibility < 3:
        reasons.append(
            f"👁️ Visibility: {visibility:.1f} km — Poor visibility can "
            "significantly increase delay risk."
        )
    elif visibility < 7:
        reasons.append(
            f"👁️ Visibility: {visibility:.1f} km — Reduced visibility "
            "may contribute to operational delays."
        )
    else:
        reasons.append(
            f"👁️ Visibility: {visibility:.1f} km — Good visibility, "
            "so visibility-related risk is low."
        )

    # Wind analysis
    if wind_speed >= 30:
        reasons.append(
            f"💨 Wind: {wind_speed:.1f} km/h — Strong winds may "
            "increase operational delay risk."
        )
    elif wind_speed >= 15:
        reasons.append(
            f"💨 Wind: {wind_speed:.1f} km/h — Moderate winds may "
            "contribute slightly to operational risk."
        )
    else:
        reasons.append(
            f"💨 Wind: {wind_speed:.1f} km/h — Relatively calm conditions."
        )

    # Rain analysis
    if rain >= 10:
        reasons.append(
            f"🌧️ Rain: {rain:.1f} mm — Heavy precipitation can "
            "significantly increase delay risk."
        )
    elif rain > 0:
        reasons.append(
            f"🌧️ Rain: {rain:.1f} mm — Light precipitation adds "
            "some weather-related risk."
        )
    else:
        reasons.append(
            "🌧️ Rain: 0.0 mm — No precipitation-related risk detected."
        )

    return "\n".join(reasons)


# ---------------------------------------------------------------
# MODEL SCALING HELPER
# ---------------------------------------------------------------

def _apply_scaling(dataframe, fitted_scaler, cont_features, cat_features):
    scaled_df = dataframe.copy()
    if cont_features and fitted_scaler is not None:
        valid_cont = [c for c in cont_features if c in scaled_df.columns]
        if valid_cont:
            scaled_df[valid_cont] = fitted_scaler.transform(scaled_df[valid_cont])
    return scaled_df.values.astype(np.float32)


# ---------------------------------------------------------------
# MODEL LOADER
# ---------------------------------------------------------------

_artifacts_loaded = False
_tabnet_model = None
_xgb_model = None
_scaler = None
_meta = None

def load_artifacts():
    global _artifacts_loaded, _tabnet_model, _xgb_model, _scaler, _meta
    if _artifacts_loaded:
        return _tabnet_model, _xgb_model, _scaler, _meta

    meta_file = MODELS_DIR / "meta.joblib"
    scaler_file = MODELS_DIR / "scaler.joblib"
    xgb_file = MODELS_DIR / "xgb_model.json"
    tabnet_file = MODELS_DIR / "tabnet_model.zip"

    if meta_file.exists():
        try:
            _meta = joblib.load(meta_file)
        except Exception:
            _meta = None

    if scaler_file.exists():
        try:
            _scaler = joblib.load(scaler_file)
        except Exception:
            _scaler = None

    if xgb_file.exists():
        try:
            from xgboost import XGBRegressor
            _xgb_model = XGBRegressor()
            _xgb_model.load_model(str(xgb_file))
        except Exception:
            _xgb_model = None

    if tabnet_file.exists():
        try:
            from pytorch_tabnet.tab_model import TabNetRegressor
            _tabnet_model = TabNetRegressor()
            _tabnet_model.load_model(str(tabnet_file))
        except Exception:
            _tabnet_model = None

    _artifacts_loaded = True
    return _tabnet_model, _xgb_model, _scaler, _meta


# ---------------------------------------------------------------
# PREDICTION FUNCTION
# ---------------------------------------------------------------

def predict_flight_delay(
    airline,
    source,
    destination,
    total_stops,
    journey_year,
    journey_month,
    journey_day,
    dep_hour,
    vis_km,
    wind_kmh,
    rain_mm,
    temp_c,
):
    tabnet_mod, xgb_mod, scaler_obj, meta_obj = load_artifacts()

    ens_raw = None

    # If trained models exist in backend/models/, use them
    if tabnet_mod is not None and xgb_mod is not None and scaler_obj is not None and meta_obj is not None:
        try:
            all_encoded_columns = meta_obj.get("all_encoded_columns", [])
            enc_continuous = meta_obj.get("enc_continuous", [])
            enc_categorical = meta_obj.get("enc_categorical", [])
            opt_w_tab = meta_obj.get("opt_w_tab", 0.5)
            opt_w_xgb = meta_obj.get("opt_w_xgb", 0.5)

            input_row = pd.DataFrame(0, index=[0], columns=all_encoded_columns)
            input_row["Total_stops"] = int(total_stops)
            input_row["Journey_Year"] = int(journey_year)
            input_row["Journey_Month"] = int(journey_month)
            input_row["Journey_Day"] = int(journey_day)
            input_row["Dep_Hour"] = int(dep_hour)
            input_row["Visibility_km"] = float(vis_km)
            input_row["Wind_Speed_kmh"] = float(wind_kmh)
            input_row["Precipitation_mm"] = float(rain_mm)
            input_row["Temperature_C"] = float(temp_c)

            for key, val in {
                f"airline_{airline}": 1,
                f"Source_{source}": 1,
                f"destination_{destination}": 1,
            }.items():
                if key in input_row.columns:
                    input_row[key] = val

            final_input = _apply_scaling(
                input_row,
                scaler_obj,
                enc_continuous,
                enc_categorical
            )

            tab_val = float(tabnet_mod.predict(final_input).ravel()[0])
            xgb_val = float(xgb_mod.predict(final_input)[0])
            ens_raw = max(0.0, float(opt_w_tab * tab_val + opt_w_xgb * xgb_val))
        except Exception as e:
            print(f"⚠️ Model inference fallback triggered: {e}")
            ens_raw = None

    # Heuristic estimation if models haven't been trained and saved yet
    if ens_raw is None:
        base_friction = 6.0
        stop_penalty = int(total_stops) * 18.0
        peak_penalty = 16.0 if (17 <= int(dep_hour) <= 22) else 0.0
        vis_impact = (15.0 - min(float(vis_km), 15.0)) * 2.2
        rain_impact = (float(rain_mm) ** 1.2) * 6.0
        wind_impact = (float(wind_kmh) ** 1.05) * 0.3
        ens_raw = max(0.0, min(180.0, base_friction + stop_penalty + peak_penalty + vis_impact + rain_impact + wind_impact))

    # Risk classification
    if ens_raw < 10.0:
        risk_level = "LOW"
        risk_icon = "🟢"
    elif ens_raw < 30.0:
        risk_level = "MEDIUM"
        risk_icon = "🟡"
    else:
        risk_level = "HIGH"
        risk_icon = "🔴"

    # Delay factors
    reasons = []
    if float(temp_c) > 32:
        reasons.append(f"High temperature ({float(temp_c):.1f}°C)")
    elif float(temp_c) < 10:
        reasons.append(f"Low temperature ({float(temp_c):.1f}°C)")

    if float(vis_km) < 7:
        reasons.append(f"Reduced visibility ({float(vis_km):.1f} km)")

    if float(rain_mm) >= 10:
        reasons.append(f"Heavy rainfall ({float(rain_mm):.1f} mm)")
    elif float(rain_mm) > 0:
        reasons.append(f"Rainfall ({float(rain_mm):.1f} mm)")

    if float(wind_kmh) >= 30:
        reasons.append(f"Strong winds ({float(wind_kmh):.1f} km/h)")

    if 17 <= int(dep_hour) <= 22:
        reasons.append(f"Peak-hour departure ({int(dep_hour):02d}:00)")

    if int(total_stops) > 0:
        stops_text = "stop" if int(total_stops) == 1 else "stops"
        reasons.append(f"{int(total_stops)} {stops_text} in the journey")

    if not reasons:
        reasons.append("No major weather or operational risk factors detected")

    reason_text = "\n".join(f"• {r}" for r in reasons)

    return (
        f"✈️ FLIGHT DELAY PREDICTION\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⏱️ Predicted Delay: {round(ens_raw)} minutes\n"
        f"{risk_icon} Risk Level: {risk_level}\n\n"
        f"📌 Main Reasons:\n"
        f"{reason_text}\n\n"
        f"🌦️ Live Weather:\n"
        f"• Visibility: {float(vis_km):.1f} km\n"
        f"• Wind: {float(wind_kmh):.1f} km/h\n"
        f"• Rain: {float(rain_mm):.1f} mm\n"
    )