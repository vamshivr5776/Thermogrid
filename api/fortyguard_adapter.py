from typing import Any


class FortyGuardAdapter:
    """
    Converts FortyGuard heatmap responses into
    clean temperature data for ThermoGrid.
    """

    @staticmethod
    def extract_tiles(result: dict[str, Any]) -> list[dict[str, Any]]:
        map_data = result.get("map_data")

        if not isinstance(map_data, dict):
            raise ValueError("FortyGuard response missing map_data.")

        features = map_data.get("features")

        if not isinstance(features, list):
            raise ValueError("FortyGuard map_data missing features.")

        tiles = []

        for feature in features:
            if not isinstance(feature, dict):
                continue

            properties = feature.get("properties") or {}
            geometry = feature.get("geometry") or {}

            if not isinstance(properties, dict):
                continue

            average_temperature = properties.get(
                "average_temperature"
            )

            if average_temperature is None:
                average_temperature = properties.get(
                    "average_temperature_C"
                )

            if average_temperature is None:
                continue

            try:
                average_temperature = float(
                    average_temperature
                )
            except (TypeError, ValueError):
                continue

            min_temperature = properties.get(
                "min_temperature",
                properties.get(
                    "min_temperature_C",
                    average_temperature,
                ),
            )

            max_temperature = properties.get(
                "max_temperature",
                properties.get(
                    "max_temperature_C",
                    average_temperature,
                ),
            )

            try:
                min_temperature = float(min_temperature)
                max_temperature = float(max_temperature)
            except (TypeError, ValueError):
                min_temperature = average_temperature
                max_temperature = average_temperature

            tiles.append(
                {
                    "id": feature.get("id"),
                    "tile_id": properties.get("tile_id"),
                    "average_temperature_C": average_temperature,
                    "min_temperature_C": min_temperature,
                    "max_temperature_C": max_temperature,
                    "geometry": geometry,
                }
            )

        if not tiles:
            first_feature = features[0] if features else {}

            first_properties = (
                first_feature.get("properties", {})
                if isinstance(first_feature, dict)
                else {}
            )

            raise ValueError(
                "No temperature tiles found. "
                f"First feature properties: {first_properties}"
            )

        return tiles

    @staticmethod
    def temperature_statistics(
        tiles: list[dict[str, Any]]
    ) -> dict[str, float]:

        temperatures = [
            tile["average_temperature_C"]
            for tile in tiles
        ]

        return {
            "minimum_C": min(temperatures),
            "maximum_C": max(temperatures),
            "mean_C": sum(temperatures) / len(temperatures),
            "tile_count": len(temperatures),
        }