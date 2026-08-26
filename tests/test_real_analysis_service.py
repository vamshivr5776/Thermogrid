from thermal.analysis_service import ThermoGridAnalysisService


def test_real_analysis_service():

    service = ThermoGridAnalysisService()

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
                    ]],
                },
            }
        ],
    }

    result = service.analyze_transformer(
        latitude=40.707,
        longitude=-74.016,
        polygon_aoi=polygon,
        start_date="2025-07-15",
        start_time="14:00",
        load_profile=[
            0.50,
            0.60,
            0.70,
            0.80,
            0.90,
            1.00,
            0.90,
            0.80,
        ],
        dt_hours=1.0,
        granularity=100,
    )

    print("\n========== THERMOGRID ANALYSIS ==========")

    print(
        "Ambient:",
        result["environment"]["temperature_C"],
        "°C"
    )

    print(
        "Peak hotspot:",
        result["thermal"]["peak_hotspot_C"],
        "°C"
    )

    print(
        "Peak aging:",
        result["thermal"]["peak_aging_factor"],
        "x"
    )

    print(
        "Loss of life:",
        result["thermal"]["loss_of_life_percent"],
        "%"
    )

    print(
        "Risk:",
        result["risk"]["level"]
    )

    assert "environment" in result
    assert "thermal" in result
    assert "risk" in result
    assert "fortyguard" in result

    assert result["environment"]["temperature_C"] > 0
    assert result["thermal"]["peak_hotspot_C"] > 0
    assert result["thermal"]["peak_aging_factor"] >= 0