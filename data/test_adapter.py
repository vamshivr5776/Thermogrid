from api.fortyguard_adapter import FortyGuardAdapter


def test_extract_tiles():
    result = {
        "map_data": {
            "type": "FeatureCollection",
            "features": [
                {
                    "id": "0",
                    "type": "Feature",
                    "properties": {
                        "tile_id": 0,
                        "average_temperature": 30.4552,
                        "min_temperature": 30.4552,
                        "max_temperature": 30.4552,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-74.02, 40.70],
                            [-74.01, 40.70],
                            [-74.01, 40.71],
                            [-74.02, 40.71],
                            [-74.02, 40.70],
                        ]],
                    },
                }
            ],
        }
    }

    tiles = FortyGuardAdapter.extract_tiles(result)

    assert len(tiles) == 1
    assert tiles[0]["tile_id"] == 0
    assert tiles[0]["average_temperature_C"] == 30.4552


def test_temperature_statistics():

    tiles = [
        {
            "tile_id": 1,
            "average_temperature_C": 30.0,
            "min_temperature_C": 29.5,
            "max_temperature_C": 30.5,
        },
        {
            "tile_id": 2,
            "average_temperature_C": 32.0,
            "min_temperature_C": 31.5,
            "max_temperature_C": 32.5,
        },
    ]

    stats = FortyGuardAdapter.temperature_statistics(tiles)

    assert stats["minimum_C"] == 30.0
    assert stats["maximum_C"] == 32.0
    assert stats["mean_C"] == 31.0
    assert stats["tile_count"] == 2