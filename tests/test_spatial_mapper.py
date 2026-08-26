import pytest

from thermal.spatial_mapper import SpatialMapper


def test_point_inside_tile():

    tiles = [
        {
            "tile_id": 1,
            "average_temperature_C": 31.5,
            "min_temperature_C": 31.2,
            "max_temperature_C": 31.8,
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
    ]

    mapper = SpatialMapper(tiles)

    result = mapper.map_transformer(
        latitude=40.705,
        longitude=-74.015,
    )

    assert result["tile_id"] == 1
    assert result["temperature_C"] == 31.5
    assert result["mapping_method"] == "polygon_containment"


def test_nearest_tile_fallback():

    tiles = [
        {
            "tile_id": 1,
            "average_temperature_C": 32.0,
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
    ]

    mapper = SpatialMapper(tiles)

    result = mapper.map_transformer(
        latitude=40.72,
        longitude=-74.00,
    )

    assert result["tile_id"] == 1
    assert result["mapping_method"] == "nearest_centroid"
    assert result["distance_km"] > 0


def test_invalid_coordinates():

    tiles = [
        {
            "tile_id": 1,
            "average_temperature_C": 30.0,
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
    ]

    mapper = SpatialMapper(tiles)

    with pytest.raises(ValueError):
        mapper.map_transformer(
            latitude=100,
            longitude=-74,
        )