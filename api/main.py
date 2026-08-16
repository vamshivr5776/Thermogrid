from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from thermal.thermal_model import TransformerThermalModel


app = FastAPI(
    title="ThermoGrid API",
    description="Thermal analysis API for urban distribution transformers",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ThermalRequest(BaseModel):
    load_profile: list[float] = Field(
        ...,
        min_length=1,
        description="Transformer load ratio in per-unit"
    )

    ambient_profile: list[float] = Field(
        ...,
        min_length=1,
        description="Ambient temperature in °C"
    )

    dt_hours: float = Field(
        default=1.0,
        gt=0,
        description="Simulation time step in hours"
    )

@app.get("/")
def root():
    return {
        "name": "ThermoGrid API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/thermal/simulate")
def simulate_thermal(request: ThermalRequest):

    try:
        model = TransformerThermalModel()

        result = model.simulate(
            load_profile=request.load_profile,
            ambient_profile=request.ambient_profile,
            dt_hours=request.dt_hours,
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
                "peak_hotspot_C": float(
                    result["hotspot_C"].max()
                ),
                "peak_aging_factor": float(
                    result["aging_factor"].max()
                ),
            },
            "thermal_response": result.to_dict(
                orient="records"
            ),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )