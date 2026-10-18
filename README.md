# ✈️ Flight Delay Prediction System

An intelligent flight delay prediction system that combines machine learning, historical flight data, historical weather observations, and live weather information to estimate potential flight delays.

The project integrates a **TabNet + XGBoost ensemble model** with an API-based backend and web interfaces to provide flight information, weather conditions, and delay predictions.

## 🎯 Overview

Flight delays can disrupt travel plans, airline operations, and airport scheduling. This project aims to estimate flight delays using flight details and weather conditions.

The system combines historical flight information with historical METAR weather observations and integrates live weather data through the OpenWeatherMap API.

A machine learning ensemble comprising TabNet and XGBoost is used to estimate delay duration. The backend exposes REST API endpoints that allow frontend applications to retrieve flight options, access weather information, and request predictions.

The project is designed to support both React.js and Streamlit interfaces.

## 🚀 Key Features

- **Flight delay prediction:** Estimates delay duration using flight-related input features.
- **Ensemble learning:** Combines TabNet and XGBoost predictions.
- **Historical weather integration:** Uses METAR observations to incorporate weather-related information into the dataset.
- **Live weather integration:** Retrieves current weather conditions using the OpenWeatherMap API.
- **REST API backend:** Provides endpoints for flight options, weather information, prediction requests, and health checks.
- **Multiple frontend options:** Supports a React.js interface and a Streamlit interface.
- **Prediction explanations:** Supports identifying weather and operational factors that may contribute to a prediction.
- **Model evaluation:** Uses MAE, RMSE, R², and prediction tolerance metrics to assess performance.
- **Feature analysis:** Uses SHAP to help interpret XGBoost predictions.

## 🏗️ System Architecture

The application follows a modular architecture consisting of data processing, machine learning, backend services, and frontend interfaces.

```text
             HISTORICAL FLIGHT DATA
                       |
                       v
             HISTORICAL METAR DATA
                       |
                       v
             DATA PREPROCESSING
                       |
                       v
              FEATURE ENGINEERING
                       |
                       v
          +-------------------------+
          |   MACHINE LEARNING      |
          |                         |
          |       TabNet            |
          |          +              |
          |       XGBoost            |
          |          |              |
          |   Ensemble Prediction   |
          +-------------------------+
                       |
                       v
                MODEL INFERENCE
                       |
                       v
              FASTAPI BACKEND <------- OpenWeatherMap API
                       |
                REST API Endpoints
                       |
             +---------+---------+
             |                   |
             v                   v
        React.js UI         Streamlit UI
```

The backend acts as the central interface between the trained prediction system, weather service, and frontend applications.

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| Data processing | Pandas, NumPy |
| Machine learning | PyTorch, PyTorch TabNet, XGBoost |
| Data preprocessing | Scikit-learn |
| Model interpretation | SHAP |
| Backend framework | FastAPI |
| API server | Uvicorn |
| Live weather | OpenWeatherMap API |
| Frontend | React.js |
| Frontend development server | Vite |
| Alternative frontend | Streamlit |
| Dataset format | CSV |
| Development environment | Google Colab, Visual Studio Code |

## 📊 Dataset and Weather Integration

### 1. Historical flight data

The project uses flight-related CSV data, including the `clean_flights_9_columns.csv` dataset or the alternative `flights.csv` file, depending on which file is available.

Flight information can include:

- Airline
- Source and destination
- Journey date
- Departure time
- Flight duration
- Number of stops
- Other available operational features

The exact features depend on the selected dataset and preprocessing configuration.

### 2. Historical weather data

Historical weather information is sourced from METAR/ASOS observations, including the `asos.csv` dataset.

The weather-processing pipeline converts relevant measurements into usable features.

| Weather measurement | Processed feature | Conversion |
|---|---|---|
| Temperature (`tmpf`) | Temperature_C | Fahrenheit to Celsius |
| Visibility (`vsby`) | Visibility_km | Miles to kilometres |
| Wind speed (`sknt`) | Wind_Speed_kmh | Knots to km/h |
| Precipitation (`p01i`) | Precipitation_mm | Inches to millimetres |

Weather observations are aligned with the relevant airport, date, and departure hour. Missing weather values are handled during preprocessing.

### 3. Live weather integration

The project uses the OpenWeatherMap API to retrieve current weather conditions.

The weather service can retrieve:

- Temperature
- Visibility
- Wind speed
- Precipitation, where available

These weather features can then be supplied to the prediction workflow.

**Configuration:** Store your OpenWeatherMap API key in an environment variable rather than hardcoding it in source code.

```env
OPENWEATHER_API_KEY=your_api_key_here
```

Replace the placeholder with your own API key. Do not commit the `.env` file or expose your API key in a public repository.

## 🤖 Machine Learning Model

The prediction engine uses a hybrid ensemble approach combining TabNet and XGBoost.

### 1. TabNet

TabNet is a deep learning architecture designed for tabular data. It uses sequential attention to select relevant features during prediction.

In this project, TabNet learns relationships between flight characteristics, weather measurements, and the target variable.

### 2. XGBoost

XGBoost is a gradient-boosted decision tree algorithm suitable for structured datasets.

It learns nonlinear relationships between the input features and the target and provides feature-importance analysis through SHAP.

### 3. Ensemble prediction

The system combines predictions from both models to obtain the final estimated delay.

Conceptually:

```text
Final Prediction =
    TabNet Weight × TabNet Prediction
  + XGBoost Weight × XGBoost Prediction
```

The model weights are selected using validation performance in the optimized training workflow.

### 4. Model evaluation

The following metrics are used to evaluate prediction performance:

- **MAE (Mean Absolute Error):** Average absolute difference between predicted and actual values.
- **RMSE (Root Mean Squared Error):** Penalizes larger prediction errors more heavily.
- **R² Score:** Measures how well the predictions explain variation in the target.
- **Within 10 minutes:** Measures the proportion of predictions falling within a 10-minute error tolerance.

### 5. Feature explainability

SHAP is used to analyze how input features influence XGBoost predictions. This can help identify which features contribute most strongly to individual predictions and overall model behaviour.

## 📁 Project Structure

The following is a suggested organization for the application. Adjust filenames to match the actual files in your repository.

```text
Flight_Delay_Predictor/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   ├── train_model.py
│   │
│   ├── app/
│   │   ├── main.py
│   │   ├── prediction.py
│   │   └── weather.py
│   │
│   └── data/
│       ├── clean_flights_9_columns.csv
│       └── asos.csv
│
├── frontend/
│   ├── react-app/
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── services/
│   │   │   ├── App.jsx
│   │   │   ├── main.jsx
│   │   │   └── index.css
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   └── streamlit-app/
│       ├── app.py
│       ├── requirements.txt
│       ├── components/
│       └── services/
│
├── notebooks/
│   └── flight_delay_prediction.ipynb
│
├── .gitignore
└── README.md
```

**Note:** This tree illustrates the intended modular structure. Keep the actual paths and filenames in the README synchronized with your GitHub repository.

## 🔌 API Endpoints

The backend provides the following endpoints.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Root or service information, if configured |
| GET | `/health` | Checks backend health |
| GET | `/options` | Retrieves available airlines, sources, and destinations |
| GET | `/weather/{city}` | Retrieves weather information for a specified city |
| POST | `/predict` | Accepts flight details and returns a delay prediction |

### 1. Health check

```http
GET /health
```

Checks whether the backend service is available.

### 2. Flight options

```http
GET /options
```

Returns the available values used to populate flight selection fields.

### 3. Weather information

```http
GET /weather/Bengaluru
```

Requests current weather information for Bengaluru.

### 4. Flight delay prediction

```http
POST /predict
Content-Type: application/json
```

Accepts flight details and weather-related input features and returns a prediction.

Example request structure (adapt the fields to the actual API schema):

```json
{
  "airline": "Example Airline",
  "source": "Bengaluru",
  "destination": "Delhi",
  "stops": 0,
  "departure_hour": 14,
  "temperature_c": 28.0,
  "visibility_km": 10.0,
  "wind_speed_kmh": 12.0,
  "precipitation_mm": 0.0
}
```

Example response structure (illustrative only):

```json
{
  "predicted_delay_minutes": 25.0,
  "status": "success"
}
```

The actual request and response field names must match the implemented FastAPI endpoint.

## ⚙️ Installation and Setup

### Prerequisites

Install the following before running the application:

- Python 3.10 or another version supported by the project's dependencies
- Node.js and npm for the React frontend
- Git
- An OpenWeatherMap API key for live weather integration

### Step 1: Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd Flight_Delay_Predictor
```

Replace the placeholder with your actual repository URL.

### Step 2: Create a Python virtual environment

```bash
python -m venv venv
```

Activate the environment on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use the appropriate environment activation method for your system.

### Step 3: Install backend dependencies

Navigate to the backend directory:

```powershell
cd backend
```

Install the dependencies listed in the backend requirements file:

```powershell
pip install -r requirements.txt
```

Ensure the requirements include the libraries needed by the implemented backend and model inference pipeline.

### Step 4: Configure environment variables

Create a `.env` file in the location expected by your backend.

```env
OPENWEATHER_API_KEY=your_api_key_here
```

Make sure your application loads this variable and that `.env` is included in `.gitignore`.

### Step 5: Prepare datasets and trained models

Place the required CSV datasets in the locations expected by the training or inference scripts.

Ensure any required trained model artifacts and preprocessing objects are generated and saved before starting a backend that depends on them.

The exact model artifact filenames depend on your implementation.

## ▶️ Running the Application

### 1. Start the FastAPI backend

From the `backend` directory, run:

```powershell
python -m uvicorn main:app --reload
```

This command assumes `backend/main.py` defines the FastAPI application as `app`.

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

If your FastAPI application is located at `backend/app/main.py` instead, use the corresponding module path:

```powershell
python -m uvicorn app.main:app --reload
```

Use the command that matches the actual location of your application.

### 2. Start the React frontend

Open a second terminal:

```powershell
cd frontend/react-app
npm install
npm run dev
```

Vite normally serves the application at:

```text
http://localhost:5173
```

Ensure the React API service is configured to communicate with the backend at `http://127.0.0.1:8000`.

If the frontend and backend use different origins, configure the appropriate CORS settings in FastAPI.

### 3. Start the Streamlit frontend

Open another terminal:

```powershell
cd frontend/streamlit-app
pip install -r requirements.txt
streamlit run app.py
```

Streamlit normally serves the application at:

```text
http://localhost:8501
```

The React and Streamlit interfaces are alternative frontends. Both can use the same backend API when configured accordingly.

## 🔄 Prediction Workflow

1. The user opens the React or Streamlit application.
2. The application retrieves available flight options from the backend.
3. The user selects the airline, source, destination, journey details, and other required features.
4. The backend retrieves live weather information when requested by the workflow.
5. The input features are validated and transformed using the preprocessing configuration expected by the trained models.
6. TabNet and XGBoost generate predictions.
7. The ensemble combines the model outputs.
8. The backend returns the prediction to the frontend.
9. The interface displays the estimated delay and any supported explanatory information.



**Project:** Flight Delay Prediction System  
**Primary objective:** Estimate flight delays using machine learning, flight data, and weather information.  
**Core model:** TabNet + XGBoost ensemble  
**Backend:** FastAPI  
**Frontends:** React.js and Streamlit  
**Weather provider:** OpenWeatherMap API
