from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from thermal.analysis_service import ThermoGridAnalysisService
from thermal.thermal_model import TransformerThermalModel
from thermal.risk_engine import ThermalRiskEngine


app = FastAPI(
    title="ThermoGrid API",
    description="Thermal analysis API for urban distribution transformers",
    version="1.0.0",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "https://thermogrid.netonline.in",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class ThermalRequest(BaseModel):
    load_profile: list[float] = Field(
        ...,
        min_length=1,
        description="Transformer load ratio in per-unit",
    )

    ambient_profile: list[float] = Field(
        ...,
        min_length=1,
        description="Ambient temperature in °C",
    )

    dt_hours: float = Field(
        default=1.0,
        gt=0,
        description="Simulation time step in hours",
    )


class TransformerAnalysisRequest(BaseModel):
    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Transformer latitude",
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Transformer longitude",
    )

    polygon_aoi: dict[str, Any] = Field(
        ...,
        description="GeoJSON polygon/FeatureCollection used for FortyGuard",
    )

    start_date: str = Field(
        ...,
        description="Analysis date in YYYY-MM-DD format",
    )

    start_time: str = Field(
        ...,
        description="Analysis start time in HH:MM format",
    )

    load_profile: list[float] = Field(
        ...,
        min_length=1,
        description="Transformer load ratio profile in per-unit",
    )

    dt_hours: float = Field(
        default=1.0,
        gt=0,
        description="Simulation time step in hours",
    )

    granularity: int = Field(
        default=100,
        gt=0,
        description="FortyGuard heatmap granularity",
    )


# ---------------------------------------------------------
# Services
# ---------------------------------------------------------

analysis_service = ThermoGridAnalysisService()


# ---------------------------------------------------------
# Basic endpoints
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "ThermoGrid API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ---------------------------------------------------------
# Existing standalone thermal endpoint
# ---------------------------------------------------------

@app.post("/thermal/simulate")
def simulate_thermal(request: ThermalRequest):

    try:
        model = TransformerThermalModel()

        result = model.simulate(
            load_profile=request.load_profile,
            ambient_profile=request.ambient_profile,
            dt_hours=request.dt_hours,
        )

        risk_engine = ThermalRiskEngine()

        peak_hotspot = float(
            result["hotspot_C"].max()
        )

        peak_aging = float(
            result["aging_factor"].max()
        )

        risk = risk_engine.evaluate(
            hotspot_temperature=peak_hotspot,
            aging_factor=peak_aging,
        )

        return {
            "summary": {
                "ambient_temperature_C": float(
                    result["ambient_C"].iloc[0]
                ),
                "final_top_oil_C": float(
                    result["top_oil_C"].iloc[-1]
                ),
                "peak_top_oil_C": float(
                    result["top_oil_C"].max()
                ),
                "peak_hotspot_C": peak_hotspot,
                "peak_aging_factor": peak_aging,
            },

            "risk": {
                "level": risk.level,
                "score": risk.score,
                "hotspot_temperature_C": risk.hotspot_temperature,
                "aging_factor": risk.aging_factor,
                "message": risk.message,
            },

            "thermal_response": result.to_dict(
                orient="records"
            ),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


# ---------------------------------------------------------
# REAL THERMOGRID ANALYSIS
# ---------------------------------------------------------

@app.post("/analysis/transformer")
def analyze_transformer(
    request: TransformerAnalysisRequest,
):

    try:

        result = analysis_service.analyze_transformer(
            latitude=request.latitude,
            longitude=request.longitude,
            polygon_aoi=request.polygon_aoi,
            start_date=request.start_date,
            start_time=request.start_time,
            load_profile=request.load_profile,
            dt_hours=request.dt_hours,
            granularity=request.granularity,
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:

        raise HTTPException(
            status_code=502,
            detail=str(error),
        )

    except TimeoutError as error:

        raise HTTPException(
            status_code=504,
            detail=str(error),
        )