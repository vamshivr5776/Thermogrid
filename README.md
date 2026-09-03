I# 🌡️ ThermoGrid AI

### Location-Aware Transformer Thermal Intelligence

[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Deployment](https://img.shields.io/badge/Deployment-Cloudflare%20%2B%20Render-F38020?logo=cloudflare&logoColor=white)](https://www.cloudflare.com/)
[![Tests](https://img.shields.io/badge/Tests-8%20Passed-success)](#testing)

**ThermoGrid AI** is a full-stack platform for analyzing the thermal condition of distribution transformers by combining **transformer location, environmental temperature, electrical loading, thermal response, insulation aging, and risk assessment** in one workflow.

The core idea is simple:

> **A transformer does not experience the average temperature of an entire city. It experiences the environmental conditions around its own location.**

ThermoGrid connects location-specific environmental temperature data from **FortyGuard** to a transformer thermal analysis pipeline so that the effect of environmental conditions on transformer temperature and thermal aging can be evaluated alongside the transformer's loading profile.

---

## 🔗 Live Project

### 🌐 Production Dashboard

**https://thermogrid.netonline.in**

### 📦 Source Code

**https://github.com/vamshivr5776/Thermogrid**

---

# 1. The Real-World Problem

## Why transformer temperature matters

Distribution transformers continuously convert electrical energy while carrying changing loads.

Electrical loading produces losses inside the transformer, which appear as heat.

The resulting thermal condition depends on both:

- Electrical loading
- Ambient/environmental temperature
- Duration of operation
- Transformer thermal characteristics

The relationship can be simplified as:

```text
Higher Electrical Load
        ↓
Higher Transformer Losses
        ↓
More Heat Generated
        ↓
Higher Oil Temperature
        ↓
Higher Hot-Spot Temperature
        ↓
Accelerated Insulation Aging
````

But the surrounding environment is also important:

```text
High Ambient Temperature
        +
High Transformer Loading
        +
Long Duration
        ↓
Higher Thermal Stress
```

Therefore, transformer thermal analysis cannot be considered purely as an electrical loading problem.

---

# 2. The Environmental Data Gap

A transformer may be located in an urban environment where temperature varies across relatively small geographic areas.

A generic city-level temperature does not necessarily represent the environmental condition at a particular transformer.

Consider:

```text
Transformer A
Ambient = 30°C
Load    = 1.0 pu
```

and:

```text
Transformer B
Ambient = 42°C
Load    = 1.0 pu
```

Both transformers have the same electrical loading.

They do not have the same thermal operating condition.

The second transformer begins with a much higher ambient temperature, which directly affects the resulting top-oil and hot-spot temperatures.

This creates the engineering problem ThermoGrid addresses:

> **How can environmental conditions associated with a transformer's actual geographic location be incorporated into transformer thermal analysis?**

---

# 3. Why ThermoGrid Was Built

ThermoGrid was built to connect two areas that are often treated separately:

```text
Environmental Intelligence
          +
Transformer Thermal Engineering
```

The platform creates a continuous pipeline:

```text
Transformer Location
        ↓
Environmental Temperature
        ↓
Transformer Load Profile
        ↓
Thermal Simulation
        ↓
Top-Oil Temperature
        ↓
Hot-Spot Temperature
        ↓
Thermal Aging
        ↓
Risk Assessment
```

Instead of only asking:

> "How heavily is the transformer loaded?"

ThermoGrid helps answer:

> **"Given this transformer's location, environmental condition, and loading profile, what thermal condition is it experiencing?"**

---

# 4. What ThermoGrid Does

ThermoGrid currently provides four core capabilities.

| Capability                | Purpose                                                                                       |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| 🌡️ Environmental Mapping | Obtains environmental temperature information and associates it with the transformer location |
| ⚡ Thermal Simulation      | Simulates transformer thermal response for a specified load profile                           |
| 🧓 Aging Analysis         | Calculates thermal aging acceleration and equivalent aging                                    |
| 🚨 Risk Assessment        | Converts thermal results into an interpretable risk condition                                 |

---

# 5. End-to-End Workflow

```text
                    ┌───────────────────────┐
                    │ Transformer Location  │
                    │ Latitude / Longitude  │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      GeoJSON AOI       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │     FortyGuard API     │
                    │ Environmental Data     │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Spatial Temperature   │
                    │       Mapping         │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Transformer Thermal   │
                    │        Model          │
                    └───────────┬───────────┘
                                │
                   ┌────────────┴────────────┐
                   ▼                         ▼
          ┌─────────────────┐       ┌─────────────────┐
          │   Top-Oil Temp  │       │  Hot-Spot Temp  │
          └────────┬────────┘       └────────┬────────┘
                   │                         │
                   └────────────┬────────────┘
                                ▼
                    ┌───────────────────────┐
                    │   Aging Calculation   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │      Risk Engine      │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   ThermoGrid UI       │
                    └───────────────────────┘
```

---

# 6. Environmental Intelligence

ThermoGrid integrates **FortyGuard** environmental temperature data into the transformer analysis pipeline.

The analysis accepts:

* Transformer latitude
* Transformer longitude
* GeoJSON polygon / Area of Interest
* Analysis date
* Analysis start time
* FortyGuard granularity

The environmental processing returns information such as:

```json
{
  "temperature_C": 42.7158,
  "tile_id": 337,
  "minimum_C": 42.7158,
  "maximum_C": 42.7158,
  "mapping_method": "polygon_containment",
  "distance_km": 0
}
```

The FortyGuard response can also provide area-level statistics:

```json
{
  "minimum_C": 42.6882,
  "maximum_C": 42.7224,
  "mean_C": 42.7065,
  "tile_count": 802,
  "aoi_mode": "custom"
}
```

The mapped temperature is then passed into the thermal analysis.

---

# 7. Transformer Thermal Analysis

The thermal engine combines:

```text
Ambient Temperature
        +
Transformer Load Profile
        +
Simulation Time Step
        ↓
Thermal Response
```

For each time step, the system tracks:

* Ambient temperature
* Transformer load
* Top-oil temperature rise
* Top-oil temperature
* Hot-spot temperature rise
* Hot-spot temperature
* Aging factor
* Equivalent aging hours

Example thermal response:

```text
Time     Load       Top-Oil       Hot-Spot
------------------------------------------------
0 hr     0.5 pu      42.7 °C        42.7 °C
1 hr     0.6 pu      49.8 °C        62.8 °C
2 hr     0.7 pu      56.3 °C        73.2 °C
3 hr     0.8 pu      62.5 °C        83.4 °C
4 hr     0.9 pu      68.6 °C        93.8 °C
5 hr     1.0 pu      74.8 °C       104.7 °C
6 hr     1.1 pu      81.3 °C       116.2 °C
```

This is important because transformer temperature is not treated as an instantaneous response to load.

The model captures the **time-dependent thermal response**.

---

# 8. Thermal Aging

Transformer insulation aging is strongly influenced by hot-spot temperature.

ThermoGrid calculates:

* Peak aging factor
* Average aging factor
* Equivalent aging hours
* Estimated loss of life

The conceptual relationship is:

```text
Higher Hot-Spot Temperature
            ↓
Higher Aging Acceleration
            ↓
More Equivalent Aging
            ↓
Greater Thermal Life Consumption
```

This allows the system to translate a thermal condition into an indication of its potential effect on insulation life.

---

# 9. Risk Engine

ThermoGrid includes a dedicated thermal risk engine.

The risk engine evaluates the thermal simulation results and returns:

```text
Risk Level
Risk Score
Hot-Spot Temperature
Aging Factor
Risk Message
```

Example:

```json
{
  "level": "WARNING",
  "score": 90.92,
  "hotspot_temperature_C": 118.2,
  "aging_factor": 2.273,
  "message": "Transformer approaching thermal limit."
}
```

The risk layer provides a simple operational interpretation of the underlying engineering calculations.

---

# 10. Example Production Analysis

A complete production analysis was successfully executed for:

```text
Latitude:  33.4484
Longitude: -112.074
```

## Environmental Result

```text
Mapped Temperature:      42.7158 °C
Minimum Temperature:     42.7158 °C
Maximum Temperature:     42.7158 °C
Mapping Method:          polygon_containment
Distance:                0 km
Tile Count:              802
Mean Temperature:        42.7065 °C
```

## Thermal Result

```text
Peak Top-Oil Temperature:      90.83 °C
Peak Hot-Spot Temperature:    118.20 °C
Peak Aging Factor:              2.273
Average Aging Factor:           0.820
Equivalent Aging Hours:         9.02 h
Loss of Life:                   0.005%
```

## Risk Result

```text
Risk Level:       WARNING
Risk Score:       90.92
Hot-Spot:         118.2 °C
Aging Factor:     2.273

Message:
Transformer approaching thermal limit.
```

This demonstrates the complete production workflow:

```text
FortyGuard
    ↓
Environmental Temperature
    ↓
Spatial Mapping
    ↓
Thermal Simulation
    ↓
Hot-Spot Analysis
    ↓
Aging Analysis
    ↓
Risk Assessment
```

---

# 11. System Architecture

```text
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │ React + Vite UI │
                  └────────┬────────┘
                           │
                           │ HTTPS
                           ▼
                  ┌─────────────────┐
                  │ Cloudflare      │
                  │ Workers         │
                  │ Frontend        │
                  └────────┬────────┘
                           │
                           │ API Request
                           ▼
                  ┌─────────────────┐
                  │ FastAPI         │
                  │ Backend         │
                  │ Render          │
                  └────────┬────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
     ┌─────────────────┐      ┌──────────────────┐
     │ FortyGuard API  │      │ Thermal Analysis │
     │ Environmental   │      │ Service          │
     │ Temperature     │      └────────┬─────────┘
     └─────────────────┘               │
                                       ▼
                              ┌──────────────────┐
                              │ Thermal Model    │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Risk Engine      │
                              └──────────────────┘
```

---

# 12. Technology Stack

## Frontend

* React
* Vite
* JavaScript
* CSS

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

## Data Processing

* NumPy
* Pandas

## External Data

* FortyGuard API

## Testing

* Pytest
* HTTPX

## Deployment

* GitHub
* Render
* Cloudflare Workers

---

# 13. Project Structure

```text
Thermogrid/
│
├── api/
│   ├── main.py
│   └── fortyguard_client.py
│
├── data/
│   └── api_integration/
│       └── pipeline.py
│
├── thermal/
│   ├── analysis_service.py
│   ├── thermal_model.py
│   └── risk_engine.py
│
├── dashboard/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   │
│   ├── package.json
│   └── ...
│
├── tests/
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 14. API

ThermoGrid exposes its backend functionality through a REST API built with FastAPI.

## `GET /`

Returns basic API information.

### Response

```json
{
  "name": "ThermoGrid API",
  "status": "running",
  "version": "1.0.0"
}
```

---

## `GET /health`

Health check endpoint.

### Response

```json
{
  "status": "healthy"
}
```

---

## `POST /thermal/simulate`

Runs the standalone thermal simulation.

### Request

```json
{
  "load_profile": [
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0
  ],
  "ambient_profile": [
    30,
    30,
    31,
    31,
    32,
    32
  ],
  "dt_hours": 1
}
```

### Parameters

| Parameter         | Type      | Description                        |
| ----------------- | --------- | ---------------------------------- |
| `load_profile`    | `float[]` | Transformer load ratio in per-unit |
| `ambient_profile` | `float[]` | Ambient temperature in °C          |
| `dt_hours`        | `float`   | Simulation time step in hours      |

---

## `POST /analysis/transformer`

Runs the complete ThermoGrid transformer analysis pipeline.

### Request

```json
{
  "latitude": 33.4484,
  "longitude": -112.074,
  "polygon_aoi": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          [-112.08, 33.44],
          [-112.07, 33.44],
          [-112.07, 33.45],
          [-112.08, 33.45],
          [-112.08, 33.44]
        ]
      ]
    },
    "properties": {}
  },
  "start_date": "2026-08-26",
  "start_time": "12:00",
  "load_profile": [
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0
  ],
  "dt_hours": 1,
  "granularity": 100
}
```

### Parameters

| Parameter      | Type      | Description                                |
| -------------- | --------- | ------------------------------------------ |
| `latitude`     | `float`   | Transformer latitude                       |
| `longitude`    | `float`   | Transformer longitude                      |
| `polygon_aoi`  | `object`  | GeoJSON polygon / FeatureCollection        |
| `start_date`   | `string`  | Analysis date in `YYYY-MM-DD` format       |
| `start_time`   | `string`  | Analysis start time in `HH:MM` format      |
| `load_profile` | `float[]` | Transformer load ratio profile in per-unit |
| `dt_hours`     | `float`   | Simulation time step in hours              |
| `granularity`  | `int`     | FortyGuard heatmap granularity             |

---

# 15. API Documentation

FastAPI automatically provides interactive Swagger documentation.

When running locally:

**[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

Swagger allows you to:

* Inspect API endpoints
* View request schemas
* Submit test requests
* Inspect JSON responses
* Validate API behavior

---

# 16. Local Development

## Prerequisites

Install:

* Python
* Node.js
* npm
* Git

---

## Backend

Clone the repository:

```bash
git clone https://github.com/vamshivr5776/Thermogrid.git
cd Thermogrid
```

Create a Python virtual environment.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```env
FORTYGUARD_API_KEY=your_api_key_here
```

Start the backend:

```bash
uvicorn api.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# 17. Frontend Development

Move into the dashboard:

```bash
cd dashboard
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The terminal will display the local Vite development URL.

---

# 18. Environment & API Security

The FortyGuard API credential is kept on the backend.

The intended architecture is:

```text
Browser
   │
   │ No FortyGuard API Key
   ▼
React Frontend
   │
   │ HTTPS
   ▼
FastAPI Backend
   │
   │ Environment Variable
   ▼
FortyGuard API
```

For local development, the API key is stored in `.env`.

**Never commit `.env` or expose the API key in frontend source code.**

The following should remain private:

```text
.env
API keys
Secret tokens
Private credentials
```

---

# 19. Deployment

## Backend — Render

The FastAPI backend is deployed on Render.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Production environment variables are configured in the Render service rather than committed to the repository.

---

## Frontend — Cloudflare Workers

The React/Vite application is built using:

```bash
npm run build
```

The frontend deployment uses Wrangler:

```bash
npx wrangler deploy
```

Production application:

**[https://thermogrid.netonline.in](https://thermogrid.netonline.in)**

---

# 20. Testing

ThermoGrid includes automated backend tests using:

* Pytest
* HTTPX

The implemented test suite has been successfully executed:

```text
8 tests passed
```

The tests validate the implemented API and analysis functionality.

---

# 21. Production Validation

The deployed system has been tested through the complete workflow:

```text
User Input
    ↓
React Dashboard
    ↓
Production API
    ↓
FastAPI
    ↓
FortyGuard
    ↓
Spatial Mapping
    ↓
Thermal Model
    ↓
Aging Analysis
    ↓
Risk Engine
    ↓
JSON Response
    ↓
Dashboard
```

Validated components:

* [x] Frontend production build
* [x] Cloudflare deployment
* [x] Backend deployment
* [x] FastAPI startup
* [x] Health endpoint
* [x] Swagger API
* [x] FortyGuard integration
* [x] Environmental temperature mapping
* [x] Transformer thermal simulation
* [x] Hot-spot calculation
* [x] Aging calculation
* [x] Risk engine
* [x] Frontend-backend communication
* [x] End-to-end analysis
* [x] Automated tests

---

# 22. Engineering Significance

ThermoGrid demonstrates how environmental intelligence can be integrated into an electrical engineering workflow.

The project connects multiple engineering and software layers:

```text
Geospatial Data
      +
Environmental Intelligence
      +
Power Engineering
      +
Thermal Modeling
      +
Aging Analysis
      +
Risk Assessment
      +
Full-Stack Software
```

The important engineering transition is:

```text
Environmental Data
        ↓
Physical Transformer Model
        ↓
Engineering Interpretation
        ↓
Operational Risk
```

This is what makes ThermoGrid more than a temperature visualization dashboard.

---

# 23. Future Scope

The current system establishes the core environmental-to-thermal-to-risk pipeline.

Potential future extensions include:

### Transformer Fleet Intelligence

Analyze multiple transformers simultaneously and compare their thermal conditions.

### GIS Risk Mapping

Display transformer locations and thermal risk geographically.

### Forecast-Based Analysis

Use future environmental conditions to estimate upcoming thermal conditions.

### Dynamic Loadability

Calculate permissible loading under specified environmental and thermal constraints.

### Predictive Maintenance

Use historical thermal aging information to support maintenance prioritization.

### Automated Alerts

Notify operators when simulated thermal conditions cross defined thresholds.

### Network-Level Analysis

Extend the system from individual transformers to distribution-network thermal risk.

---

# 24. Project Vision

The long-term objective is to move transformer monitoring from a purely load-centric approach toward **location-aware thermal intelligence**.

Traditional view:

```text
Transformer
    +
Electrical Load
    ↓
Thermal Analysis
```

ThermoGrid:

```text
Transformer Location
        +
Environmental Conditions
        +
Electrical Loading
        +
Time
        ↓
Thermal Condition
        ↓
Hot-Spot
        ↓
Aging
        ↓
Risk
```

The platform can ultimately evolve from:

```text
One Transformer
      ↓
Transformer Fleet
      ↓
Distribution Network
      ↓
Predictive Thermal Management
```

---

# 25. Why This Project Matters

The practical problem is not simply that transformers become hot.

The problem is that **electrical loading, environmental conditions, and thermal aging are interconnected**.

ThermoGrid makes that connection explicit.

It provides a workflow where:

```text
WHERE
  ↓
Environmental Condition
  ↓
HOW MUCH LOAD
  ↓
THERMAL RESPONSE
  ↓
HOW HOT
  ↓
HOW FAST IT AGES
  ↓
WHAT IS THE RISK
```

That is the problem ThermoGrid AI was built to investigate and solve.

# 🧰 Technology Summary

```text
Frontend
├── React
├── Vite
├── JavaScript
└── CSS

Backend
├── Python
├── FastAPI
├── Uvicorn
└── Pydantic

Data Processing
├── NumPy
└── Pandas

External Integration
└── FortyGuard API

Testing
├── Pytest
└── HTTPX

Deployment
├── Cloudflare Workers
├── Render
└── GitHub
```

---

# 👨‍💻 Project

## ThermoGrid AI

**Location-aware transformer thermal analysis and risk assessment.**

### 🌐 Live Application

[https://thermogrid.netonline.in](https://thermogrid.netonline.in)

Better to view in desktop mode if you are using it in phone. 

### 📦 GitHub Repository

[https://github.com/vamshivr5776/Thermogrid](https://github.com/vamshivr5776/Thermogrid)

---

## 🌡️ ThermoGrid AI

> **Turning environmental temperature into transformer thermal intelligence.**
**ThermoGrid AI — Turning Hyperlocal Heat into Predictive Transformer Risk Intelligence**

