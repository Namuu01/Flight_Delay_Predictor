#Ensemble + Historical weather data integrated trained model.
# ====================================================================
# MASTER AIRLINE OPERATIONAL DELAY PREDICTION ENGINE
# Architecture: TabNet + XGBoost + Leakage-Free OOF Stacked Ensemble
# Data: 2019-2025 Flight Data + Multi-Year Historical METAR Weather
# Workspace: Google Colab (GPU / CPU Compatible)
# ====================================================================


# ================================================================
# LIVE WEATHER API CONFIGURATION — OPENWEATHER
# ================================================================

import os
import sys

# Ensure UTF-8 output on Windows terminals to avoid charmap UnicodeEncodeError
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import requests

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# ================================================================
# LIVE WEATHER FETCH FUNCTION
# ================================================================

def get_live_weather(city):
    params = {
        "q": city,
        "appid": OPENWEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(OPENWEATHER_URL, params=params, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ OpenWeather API Warning {response.status_code}: {response.text}")
            print("Using default fallback weather parameters.")
            return {
                "Temperature_C": 28.0,
                "Visibility_km": 10.0,
                "Wind_Speed_kmh": 12.0,
                "Precipitation_mm": 0.0
            }

        data = response.json()
        temperature_c = data["main"]["temp"]
        visibility_km = data.get("visibility", 10000) / 1000
        wind_speed_kmh = data.get("wind", {}).get("speed", 0) * 3.6
        precipitation_mm = data.get("rain", {}).get("1h", 0)

        return {
            "Temperature_C": temperature_c,
            "Visibility_km": visibility_km,
            "Wind_Speed_kmh": wind_speed_kmh,
            "Precipitation_mm": precipitation_mm
        }
    except Exception as exc:
        print(f"⚠️ Could not fetch live weather ({exc}). Using defaults.")
        return {
            "Temperature_C": 28.0,
            "Visibility_km": 10.0,
            "Wind_Speed_kmh": 12.0,
            "Precipitation_mm": 0.0
        }

# Test live weather API

live_weather = get_live_weather("Bengaluru")

print("🌦️ LIVE WEATHER")
print("-----------------------------")

for key, value in live_weather.items():
    print(f"{key}: {value}")

# --------------------------------------------------------------------
# STEP 1: INITIALIZATION & PACKAGING CONFIGURATION
# --------------------------------------------------------------------
import os
import subprocess
import sys

# Install dependencies only if not already installed
required_libs = {"pytorch_tabnet": "pytorch-tabnet", "gradio": "gradio", "xgboost": "xgboost", "shap": "shap"}
missing_pkgs = []
for module_name, pkg_name in required_libs.items():
    try:
        __import__(module_name)
    except ImportError:
        missing_pkgs.append(pkg_name)

if missing_pkgs:
    print(f"📦 Installing missing libraries: {missing_pkgs}...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q"] + missing_pkgs,
        check=True,
    )

import re
import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pytorch_tabnet.tab_model import TabNetRegressor
from scipy.optimize import minimize
import shap
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler
import torch
from xgboost import XGBRegressor

# Robust RMSE helper
try:
  from sklearn.metrics import root_mean_squared_error as _rmse_fn

  def compute_rmse(y_true, y_pred):
    return _rmse_fn(y_true, y_pred)
except ImportError:
  from sklearn.metrics import mean_squared_error as _mse_fn

  def compute_rmse(y_true, y_pred):
    return float(np.sqrt(_mse_fn(y_true, y_pred)))


# --------------------------------------------------------------------
# STEP 2: DATASET LOADING
# --------------------------------------------------------------------
from pathlib import Path

def _find_file(candidates):
    search_dirs = [
        Path(__file__).resolve().parent / "data",
        Path(__file__).resolve().parent,
        Path.cwd() / "backend" / "data",
        Path.cwd() / "data",
        Path.cwd(),
    ]
    for d in search_dirs:
        for fname in candidates:
            p = d / fname
            if p.exists():
                return str(p)
    return None

FLIGHT_FILE = _find_file(["clean_flights_9_columns.csv", "flights.csv"])
WEATHER_FILE = _find_file(["asos (1).csv", "asos.csv"])

if not FLIGHT_FILE:
  raise FileNotFoundError(
      "❌ Flight dataset missing! Ensure 'clean_flights_9_columns.csv' is in backend/data/ or current folder."
  )
if not WEATHER_FILE:
  raise FileNotFoundError(
      "❌ Weather dataset missing! Ensure 'asos.csv' or 'asos (1).csv' is in backend/data/ or current folder."
  )

print(f"✅ Loading flight dataset '{FLIGHT_FILE}'...")
df = pd.read_csv(FLIGHT_FILE)

print(f"✅ Loading 2019-2025 historical METAR weather '{WEATHER_FILE}'...")
weather_raw = pd.read_csv(WEATHER_FILE, comment="#", low_memory=False)

# --------------------------------------------------------------------
# STEP 3: TEMPORAL FEATURE EXTRACTION & 2019-2025 WEATHER MERGE
# --------------------------------------------------------------------
print("\n🌦️ Processing & merging multi-year hourly METAR weather features...")

if "Total_stops" in df.columns and df["Total_stops"].dtype == object:

  def parse_stops(s):
    if pd.isna(s) or "non-stop" in str(s).lower():
      return 0
    m = re.search(r"(\d+)", str(s))
    return int(m.group(1)) if m else 0

  df["Total_stops"] = df["Total_stops"].apply(parse_stops)

if "date_of_journey" in df.columns:
  df["date"] = pd.to_datetime(df["date_of_journey"])
  df["Journey_Year"] = df["date"].dt.year
  df["Journey_Month"] = df["date"].dt.month
  df["Journey_Day"] = df["date"].dt.day

if "dep_time" in df.columns and "Dep_Hour" not in df.columns:
  df["Dep_Hour"] = (
      pd.to_datetime(df["dep_time"], format="%H:%M", errors="coerce")
      .dt.hour.fillna(12)
      .astype(int)
  )

if "Journey_Year" not in df.columns:
  df["Journey_Year"] = 2024

weather_df = weather_raw.copy()
weather_df["valid"] = pd.to_datetime(weather_df["valid"], errors="coerce")
weather_df["Journey_Year"] = weather_df["valid"].dt.year
weather_df["Journey_Month"] = weather_df["valid"].dt.month
weather_df["Journey_Day"] = weather_df["valid"].dt.day
weather_df["Dep_Hour"] = weather_df["valid"].dt.hour

station_map = {
    "VOBL": "Bangalore",
    "VIDP": "Delhi",
    "VABB": "Mumbai",
    "VECC": "Kolkata",
    "VOMM": "Chennai",
    "0": "Bangalore",
    "1": "Chennai",
    "2": "Delhi",
    "3": "Kolkata",
    "4": "Mumbai",
}

df["Source_Hub"] = df["Source"].astype(str).str.strip().map(station_map)
df["Source_Hub"] = df["Source_Hub"].fillna(df["Source"].astype(str))

weather_df["Source_Hub"] = weather_df["station"].str.upper().map(station_map)
weather_df = weather_df.dropna(subset=["Source_Hub", "valid"])

for col in ["vsby", "sknt", "p01i", "tmpf"]:
  weather_df[col] = (
      pd.to_numeric(weather_df[col], errors="coerce")
      if col in weather_df
      else np.nan
  )

weather_df["Visibility_km"] = weather_df["vsby"] * 1.60934
weather_df["Wind_Speed_kmh"] = weather_df["sknt"] * 1.852
weather_df["Precipitation_mm"] = weather_df["p01i"] * 25.4
weather_df["Temperature_C"] = (weather_df["tmpf"] - 32) * (5 / 9)

weather_hourly = (
    weather_df[[
        "Source_Hub",
        "Journey_Year",
        "Journey_Month",
        "Journey_Day",
        "Dep_Hour",
        "Visibility_km",
        "Wind_Speed_kmh",
        "Precipitation_mm",
        "Temperature_C",
    ]]
    .groupby([
        "Source_Hub",
        "Journey_Year",
        "Journey_Month",
        "Journey_Day",
        "Dep_Hour",
    ])
    .mean()
    .reset_index()
)

df = pd.merge(
    df,
    weather_hourly,
    on=[
        "Source_Hub",
        "Journey_Year",
        "Journey_Month",
        "Journey_Day",
        "Dep_Hour",
    ],
    how="left",
)

weather_cols = [
    "Visibility_km",
    "Wind_Speed_kmh",
    "Precipitation_mm",
    "Temperature_C",
]
for col in weather_cols:
  df[col] = df[col].fillna(df.groupby("Journey_Month")[col].transform("median"))
  df[col] = df[col].fillna(df[col].median())

# --------------------------------------------------------------------
# STEP 4: REALISTIC AVIATION DELAY GROUND TRUTH GENERATION
# --------------------------------------------------------------------
print("\n🎲 Simulating operational delay targets with realistic variance...")
np.random.seed(42)

# Operational delay drivers
base_friction = np.random.exponential(scale=6.0, size=len(df))
stop_penalty = df["Total_stops"] * np.random.choice(
    [14.0, 18.0, 24.0], size=len(df)
)
peak_penalty = np.where(
    (df["Dep_Hour"] >= 17) & (df["Dep_Hour"] <= 22),
    np.random.uniform(12.0, 26.0, size=len(df)),
    0.0,
)

# Meteorological friction
vis_impact = (15.0 - np.clip(df["Visibility_km"], 0, 15.0)) * 2.2
rain_impact = (df["Precipitation_mm"] ** 1.2) * 6.0
wind_impact = (df["Wind_Speed_kmh"] ** 1.05) * 0.3

# Cascading multi-factor interactions
cascade_risk = (df["Total_stops"] * 0.7) * (
    vis_impact * 0.35 + rain_impact * 0.45
)

# Realistic unobserved airport noise (ATC holds, gate variance)
unobserved_noise = np.random.normal(0.0, 7.5, size=len(df))

df["Delay_Minutes"] = np.round(
    base_friction
    + stop_penalty
    + peak_penalty
    + vis_impact
    + rain_impact
    + wind_impact
    + cascade_risk
    + unobserved_noise
).astype(int)
df["Delay_Minutes"] = df["Delay_Minutes"].clip(lower=0, upper=180)

print(
    f"📊 Delay Profile Summary — Mean: {df['Delay_Minutes'].mean():.1f} mins |"
    f" Max: {df['Delay_Minutes'].max()} mins"
)

# ====================================================================
# STEP 5: PREPROCESSING PIPELINE & LEAKAGE-FREE SPLITTING
# ====================================================================
TARGET = "Delay_Minutes"


def pipeline_build_feature_frame(dataframe, target_col):
  df_work = dataframe.drop(
      columns=[
          "route",
          "Arrival_time",
          "Duration",
          "date",
          "date_of_journey",
          "Source_Hub",
          "Additional_info",
          "Price",
          "index",
      ],
      errors="ignore",
  )

  continuous_cols = [
      c
      for c in [
          "Total_stops",
          "Journey_Year",
          "Journey_Month",
          "Journey_Day",
          "Dep_Hour",
          "Visibility_km",
          "Wind_Speed_kmh",
          "Precipitation_mm",
          "Temperature_C",
      ]
      if c in df_work.columns
  ]

  categorical_cols = [
      col
      for col in df_work.drop(columns=[target_col]).columns
      if col not in continuous_cols
  ]

  df_encoded = pd.get_dummies(
      df_work, columns=categorical_cols, drop_first=True
  )
  bool_cols = df_encoded.select_dtypes(include=["bool"]).columns
  df_encoded[bool_cols] = df_encoded[bool_cols].astype(int)

  X_df = df_encoded.drop(columns=[target_col])
  y = df_encoded[target_col].to_numpy().reshape(-1, 1)

  all_encoded_cols = X_df.columns.tolist()
  enc_continuous = [c for c in continuous_cols if c in all_encoded_cols]
  enc_categorical = [c for c in all_encoded_cols if c not in enc_continuous]

  return X_df, y, enc_continuous, enc_categorical


def _apply_scaling(dataframe, fitted_scaler, cont_features, cat_features):
  scaled_cont = fitted_scaler.transform(dataframe[cont_features])
  unscaled_cat = dataframe[cat_features].to_numpy()
  return np.hstack((scaled_cont, unscaled_cat))


def pipeline_split_and_scale(X_df, y, enc_continuous, enc_categorical):
  X_train_raw, X_temp_raw, y_train, y_temp = train_test_split(
      X_df, y, test_size=0.3, random_state=42
  )
  X_val_raw, X_test_raw, y_val, y_test = train_test_split(
      X_temp_raw, y_temp, test_size=0.5, random_state=42
  )

  scaler = StandardScaler()
  scaler.fit(X_train_raw[enc_continuous])

  X_train = _apply_scaling(
      X_train_raw, scaler, enc_continuous, enc_categorical
  )
  X_val = _apply_scaling(X_val_raw, scaler, enc_continuous, enc_categorical)
  X_test = _apply_scaling(X_test_raw, scaler, enc_continuous, enc_categorical)

  return X_train, X_val, X_test, y_train, y_val, y_test, scaler


X_df, y, enc_continuous, enc_categorical = pipeline_build_feature_frame(
    df, TARGET
)
all_encoded_columns = X_df.columns.tolist()

X_train, X_val, X_test, y_train, y_val, y_test, scaler = (
    pipeline_split_and_scale(X_df, y, enc_continuous, enc_categorical)
)

print(
    f"\n✅ Preprocessing Complete — Train: {X_train.shape[0]} | Val:"
    f" {X_val.shape[0]} | Test: {X_test.shape[0]} rows"
)

# --------------------------------------------------------------------
# --------------------------------------------------------------------
# STEP 6: TABNET BASE MODEL TRAINING & TEST EVALUATION (CPU-OPTIMIZED)
# --------------------------------------------------------------------
print("\n🧠 Training TabNet Neural Architecture (Fast CPU-Optimized)...")
tabnet_model = TabNetRegressor(
    n_d=16,
    n_a=16,
    n_steps=3,
    gamma=1.3,
    lambda_sparse=1e-4,
    optimizer_fn=torch.optim.Adam,
    optimizer_params=dict(lr=2e-2),
    mask_type="sparsemax",
    verbose=0,
)
tabnet_model.fit(
    X_train=X_train,
    y_train=y_train,
    eval_set=[(X_val, y_val)],
    eval_name=["val"],
    eval_metric=["mae"],
    max_epochs=25,
    patience=5,
    batch_size=1024,
    virtual_batch_size=128,
    loss_fn=torch.nn.L1Loss(),
)

y_pred_tab = tabnet_model.predict(X_test).ravel()
tabnet_mae = mean_absolute_error(y_test.ravel(), y_pred_tab)
tabnet_rmse = compute_rmse(y_test.ravel(), y_pred_tab)
tabnet_r2 = r2_score(y_test.ravel(), y_pred_tab) * 100
tabnet_tolerance = np.mean(np.abs(y_test.ravel() - y_pred_tab) <= 10.0) * 100

# --------------------------------------------------------------------
# STEP 7: XGBOOST BASE MODEL TRAINING & TEST EVALUATION
# --------------------------------------------------------------------
print("\n🌲 Training XGBoost Regressor...")
xgb_model = XGBRegressor(
    n_estimators=350,
    max_depth=6,
    learning_rate=0.04,
    subsample=0.85,
    colsample_bytree=0.80,
    random_state=42,
    tree_method="hist",
    verbosity=0,
)
xgb_model.fit(
    X_train, y_train.ravel(), eval_set=[(X_val, y_val.ravel())], verbose=False
)

y_pred_xgb = xgb_model.predict(X_test).ravel()
xgb_mae = mean_absolute_error(y_test.ravel(), y_pred_xgb)
xgb_rmse = compute_rmse(y_test.ravel(), y_pred_xgb)
xgb_r2 = r2_score(y_test.ravel(), y_pred_xgb) * 100
xgb_tolerance = np.mean(np.abs(y_test.ravel() - y_pred_xgb) <= 10.0) * 100

# --------------------------------------------------------------------
# STEP 8: SHAP EXPLAINABILITY FOR XGBOOST
# --------------------------------------------------------------------
print("\n🔍 Computing SHAP values for XGBoost...")
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer(X_test)

plt.figure(figsize=(14, 8))
shap.plots.beeswarm(shap_values, max_display=15, show=False)
plt.title("XGBoost — SHAP Feature Attribution", fontsize=13, pad=14)
plt.tight_layout()
plt.savefig("shap_beeswarm_xgb.png", dpi=150, bbox_inches="tight")
plt.close()

# --------------------------------------------------------------------
# STEP 9: FAST OPTIMAL STACKED ENSEMBLE WEIGHTS (VALIDATION-BASED)
# --------------------------------------------------------------------
print("\n🔗 Computing Optimal Stacking Weights (TabNet + XGBoost)...")
val_tab = tabnet_model.predict(X_val).ravel()
val_xgb = xgb_model.predict(X_val).ravel()

def blend_objective(w):
  pred = w[0] * val_tab + (1.0 - w[0]) * val_xgb
  return mean_absolute_error(y_val.ravel(), pred)

res = minimize(blend_objective, [0.5], bounds=[(0.05, 0.95)])
opt_w_tab = float(res.x[0])
opt_w_xgb = float(1.0 - opt_w_tab)

print(
    f"   ✅ Optimal Stacking Weights: TabNet = {opt_w_tab:.3f} | XGBoost = {opt_w_xgb:.3f}"
)

# Apply learned weights to test predictions
ensemble_pred = np.maximum(0.0, opt_w_tab * y_pred_tab + opt_w_xgb * y_pred_xgb)

ens_mae = mean_absolute_error(y_test.ravel(), ensemble_pred)
ens_rmse = compute_rmse(y_test.ravel(), ensemble_pred)
ens_r2 = r2_score(y_test.ravel(), ensemble_pred) * 100
ens_tolerance = np.mean(np.abs(y_test.ravel() - ensemble_pred) <= 10.0) * 100

# --------------------------------------------------------------------
# STEP 10: MODEL COMPARISON SCORECARD
# --------------------------------------------------------------------
SEP = "=" * 72
HSEP = "-" * 72
print(f"\n{SEP}")
print("  📊  MODEL COMPARISON — WEATHER-AUGMENTED PREDICTION SCORECARD")
print(SEP)
print(f"{'Metric':<36} {'TabNet':>10} {'XGBoost':>10} {'Ensemble':>10}")
print(HSEP)
print(
    f"{'Mean Absolute Error   (MAE)  [min]':<36} {tabnet_mae:>10.2f}"
    f" {xgb_mae:>10.2f} {ens_mae:>10.2f}"
)
print(
    f"{'Root Mean Sq. Error   (RMSE) [min]':<36} {tabnet_rmse:>10.2f}"
    f" {xgb_rmse:>10.2f} {ens_rmse:>10.2f}"
)
print(
    f"{'R² Score                      [%]':<36} {tabnet_r2:>10.1f}"
    f" {xgb_r2:>10.1f} {ens_r2:>10.1f}"
)
print(
    f"{'Tolerance Accuracy (±10 min)  [%]':<36} {tabnet_tolerance:>10.1f}"
    f" {xgb_tolerance:>10.1f} {ens_tolerance:>10.1f}"
)
print(SEP)

# ====================================================================
# STEP 11: SAVE TRAINED ARTIFACTS FOR INFERENCE ENGINE
# ====================================================================
import joblib

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print(f"\n💾 Saving model artifacts to '{MODELS_DIR}'...")
try:
    tabnet_model.save_model(str(MODELS_DIR / "tabnet_model.zip"))
    xgb_model.save_model(str(MODELS_DIR / "xgb_model.json"))
    joblib.dump(scaler, MODELS_DIR / "scaler.joblib")

    metadata = {
        "all_encoded_columns": all_encoded_columns,
        "enc_continuous": enc_continuous,
        "enc_categorical": enc_categorical,
        "opt_w_tab": opt_w_tab,
        "opt_w_xgb": opt_w_xgb,
        "raw_airlines": sorted(df["airline"].dropna().unique().tolist()) if "airline" in df.columns else [],
        "raw_sources": sorted(df["Source"].dropna().unique().tolist()) if "Source" in df.columns else [],
        "raw_destinations": sorted(df["destination"].dropna().unique().tolist()) if "destination" in df.columns else [],
    }
    joblib.dump(metadata, MODELS_DIR / "meta.joblib")
    print("✅ All artifacts successfully saved to backend/models/!")
except Exception as e:
    print(f"⚠️ Warning saving artifacts: {e}")
