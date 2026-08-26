from api.fortyguard_client import FortyGuardClient
from api.fortyguard_adapter import FortyGuardAdapter
from thermal.spatial_mapper import SpatialMapper
from thermal.thermal_model import TransformerThermalModel


def test_real_fortyguard_to_thermal():

    # ---------------------------------------------------------
    # 1. Get real FortyGuard data
    # ---------------------------------------------------------

    client = FortyGuardClient()

    polygon = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [-74.0170, 40.7050],
                        [-74.0030, 40.7050],
                        [-74.0030, 40.7180],
                        [-74.0170, 40.7180],
                        [-74.0170, 40.7050],
                    ]]
                },
            }
        ],
    }

    activity_id = client.create_heatmap(
        polygon_aoi=polygon,
        start_date="2025-07-15",
        start_time="14:00",
        granularity=100,
    )

    result = client.wait_for_result(activity_id)

    # ---------------------------------------------------------
    # 2. Convert FortyGuard response → ThermoGrid tiles
    # ---------------------------------------------------------

    tiles = FortyGuardAdapter.extract_tiles(result)

    assert len(tiles) > 0

    # ---------------------------------------------------------
    # 3. Map transformer → real ambient temperature
    # ---------------------------------------------------------

    mapper = SpatialMapper(tiles)

    transformer_latitude = 40.707
    transformer_longitude = -74.016

    mapped = mapper.map_transformer(
        latitude=transformer_latitude,
        longitude=transformer_longitude,
    )

    ambient_temperature = mapped["temperature_C"]

    print("\nREAL FORTYGUARD AMBIENT")
    print(f"Temperature: {ambient_temperature:.2f} °C")
    print(f"Tile ID: {mapped['tile_id']}")
    print(f"Mapping: {mapped['mapping_method']}")

    assert 0 < ambient_temperature < 60

    # ---------------------------------------------------------
    # 4. Feed real ambient temperature into thermal model
    # ---------------------------------------------------------

    model = TransformerThermalModel()

    load_profile = [
        0.40,
        0.60,
        0.80,
        1.00,
        1.20,
        1.00,
        0.70,
    ]

    # Use the real FortyGuard temperature
    # as the ambient temperature for every timestep.
    ambient_profile = [
        ambient_temperature
    ] * len(load_profile)

    thermal_result = model.simulate(
        load_profile=load_profile,
        ambient_profile=ambient_profile,
        dt_hours=1.0,
    )

    # ---------------------------------------------------------
    # 5. Verify thermal output
    # ---------------------------------------------------------

    assert len(thermal_result) == len(load_profile)

    assert "top_oil_C" in thermal_result
    assert "hotspot_C" in thermal_result
    assert "aging_factor" in thermal_result
    assert "equivalent_aging_hours" in thermal_result

    assert thermal_result["hotspot_C"].notna().all()
    assert thermal_result["aging_factor"].notna().all()

    print("\nTHERMAL RESULT")
    print("--------------------------------")
    print(
        f"Peak top-oil : "
        f"{thermal_result['top_oil_C'].max():.2f} °C"
    )

    print(
        f"Peak hotspot : "
        f"{thermal_result['hotspot_C'].max():.2f} °C"
    )

    print(
        f"Peak aging factor : "
        f"{thermal_result['aging_factor'].max():.3f}x"
    )

    print(
        f"Equivalent aging : "
        f"{thermal_result['equivalent_aging_hours'].iloc[-1]:.3f} h"
    )

    print(
        f"Loss of life : "
        f"{thermal_result.attrs['loss_of_life_percent']:.6f}%"
    )