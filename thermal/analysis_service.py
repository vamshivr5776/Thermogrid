from typing import Any

from data.api_integration.pipeline import ThermoGridPipeline
from thermal.aoi import create_aoi_around_point
from thermal.spatial_mapper import SpatialMapper
from thermal.thermal_model import TransformerThermalModel
from thermal.risk_engine import ThermalRiskEngine


class ThermoGridAnalysisService:
    """
    Orchestrates the complete ThermoGrid analysis:

        Transformer coordinates
            ↓
        AOI selection
            ↓
        FortyGuard
            ↓
        Temperature tiles
            ↓
        Spatial mapping
            ↓
        Ambient temperature
            ↓
        Thermal model
            ↓
        Risk engine

    AOI behavior:

        Custom polygon supplied
            ↓
        Use custom polygon

        No polygon supplied
            ↓
        Generate AOI automatically
        around transformer coordinates
    """

    def __init__(self):
        self.pipeline = ThermoGridPipeline()
        self.thermal_model = TransformerThermalModel()
        self.risk_engine = ThermalRiskEngine()

    def analyze_transformer(
        self,
        latitude: float,
        longitude: float,
        polygon_aoi: dict[str, Any] | None = None,
        start_date: str = "",
        start_time: str = "",
        load_profile: list[float] | None = None,
        dt_hours: float = 1.0,
        granularity: int = 100,
    ) -> dict[str, Any]:

        # ---------------------------------------------------------
        # 1. Validate transformer coordinates
        # ---------------------------------------------------------

        if not (-90 <= latitude <= 90):
            raise ValueError(
                "Transformer latitude must be between -90 and 90."
            )

        if not (-180 <= longitude <= 180):
            raise ValueError(
                "Transformer longitude must be between -180 and 180."
            )

        # ---------------------------------------------------------
        # 2. Validate load profile
        # ---------------------------------------------------------

        if not load_profile:
            raise ValueError(
                "load_profile cannot be empty."
            )

        if any(
            not isinstance(value, (int, float))
            for value in load_profile
        ):
            raise ValueError(
                "load_profile must contain only numeric values."
            )

        if any(value < 0 for value in load_profile):
            raise ValueError(
                "load_profile cannot contain negative values."
            )

        # ---------------------------------------------------------
        # 3. Validate simulation parameters
        # ---------------------------------------------------------

        if dt_hours <= 0:
            raise ValueError(
                "dt_hours must be greater than 0."
            )

        if granularity <= 0:
            raise ValueError(
                "granularity must be greater than 0."
            )

        # ---------------------------------------------------------
        # 4. Determine AOI
        # ---------------------------------------------------------
        #
        # If the caller provides a custom polygon, preserve it.
        #
        # Otherwise, automatically create an AOI around the
        # transformer coordinates.
        # ---------------------------------------------------------

        if polygon_aoi is not None:

            analysis_aoi = polygon_aoi

            aoi_mode = "custom"

        else:

            analysis_aoi = create_aoi_around_point(
                latitude=latitude,
                longitude=longitude,
            )

            aoi_mode = "automatic"

        # ---------------------------------------------------------
        # 5. Get real environmental data from FortyGuard
        # ---------------------------------------------------------

        fortyguard_data = self.pipeline.get_fortyguard_data(
            polygon_aoi=analysis_aoi,
            start_date=start_date,
            start_time=start_time,
            granularity=granularity,
        )

        # ---------------------------------------------------------
        # 6. Extract temperature tiles
        # ---------------------------------------------------------

        tiles = fortyguard_data.get("tiles")

        if not tiles:
            raise ValueError(
                "FortyGuard returned no temperature tiles."
            )

        # ---------------------------------------------------------
        # 7. Map transformer to environmental tile
        # ---------------------------------------------------------

        mapper = SpatialMapper(tiles)

        mapped = mapper.map_transformer(
            latitude=latitude,
            longitude=longitude,
        )

        ambient_temperature = mapped["temperature_C"]

        # ---------------------------------------------------------
        # 8. Build ambient temperature profile
        # ---------------------------------------------------------

        ambient_profile = [
            ambient_temperature
            for _ in load_profile
        ]

        # ---------------------------------------------------------
        # 9. Run transformer thermal simulation
        # ---------------------------------------------------------

        thermal_result = self.thermal_model.simulate(
            load_profile=load_profile,
            ambient_profile=ambient_profile,
            dt_hours=dt_hours,
        )

        # ---------------------------------------------------------
        # 10. Extract thermal indicators
        # ---------------------------------------------------------

        peak_top_oil = float(
            thermal_result["top_oil_C"].max()
        )

        peak_hotspot = float(
            thermal_result["hotspot_C"].max()
        )

        peak_aging = float(
            thermal_result["aging_factor"].max()
        )

        equivalent_aging_hours = float(
            thermal_result[
                "equivalent_aging_hours"
            ].iloc[-1]
        )

        average_aging = float(
            thermal_result.attrs[
                "average_aging_factor"
            ]
        )

        loss_of_life = float(
            thermal_result.attrs[
                "loss_of_life_percent"
            ]
        )

        # ---------------------------------------------------------
        # 11. Risk evaluation
        # ---------------------------------------------------------

        risk = self.risk_engine.evaluate(
            hotspot_temperature=peak_hotspot,
            aging_factor=peak_aging,
        )

        # ---------------------------------------------------------
        # 12. Final ThermoGrid result
        # ---------------------------------------------------------

        return {
            "transformer": {
                "latitude": latitude,
                "longitude": longitude,
            },

            "environment": {
                "temperature_C": float(
                    ambient_temperature
                ),

                "tile_id": mapped["tile_id"],

                "minimum_C": mapped[
                    "min_temperature_C"
                ],

                "maximum_C": mapped[
                    "max_temperature_C"
                ],

                "mapping_method": mapped[
                    "mapping_method"
                ],

                "distance_km": mapped[
                    "distance_km"
                ],
            },

            "thermal": {
                "peak_top_oil_C": peak_top_oil,

                "peak_hotspot_C": peak_hotspot,

                "peak_aging_factor": peak_aging,

                "average_aging_factor": average_aging,

                "equivalent_aging_hours": (
                    equivalent_aging_hours
                ),

                "loss_of_life_percent": (
                    loss_of_life
                ),
            },

            "risk": {
                "level": risk.level,

                "score": risk.score,

                "hotspot_temperature_C": (
                    risk.hotspot_temperature
                ),

                "aging_factor": risk.aging_factor,

                "message": risk.message,
            },

            "thermal_response": (
                thermal_result.to_dict(
                    orient="records"
                )
            ),

            "fortyguard": {
                "activity_id": (
                    fortyguard_data[
                        "activity_id"
                    ]
                ),

                "statistics": (
                    fortyguard_data[
                        "statistics"
                    ]
                ),

                "aoi_mode": aoi_mode,
            },
        }