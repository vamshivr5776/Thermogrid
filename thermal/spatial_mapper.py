from math import radians, sin, cos, sqrt, atan2
from typing import Any


class SpatialMapper:
    """
    Maps transformer geographic coordinates to the
    most relevant FortyGuard temperature tile.

    Strategy:
    1. Try to find a tile containing the transformer.
    2. If no tile contains it, use the nearest tile centroid.

    The mapping logic is intentionally unchanged.
    Additional diagnostic information is returned so
    the selected FortyGuard tile can be verified.
    """

    def __init__(self, tiles: list[dict[str, Any]]):
        if not isinstance(tiles, list):
            raise ValueError("tiles must be a list.")

        if not tiles:
            raise ValueError("tiles cannot be empty.")

        self.tiles = tiles

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def map_transformer(
        self,
        latitude: float,
        longitude: float,
    ) -> dict[str, Any]:

        self._validate_coordinates(
            latitude,
            longitude,
        )

        # -----------------------------------------------------
        # First: exact spatial containment
        # -----------------------------------------------------

        for tile in self.tiles:

            geometry = tile.get(
                "geometry",
                {},
            )

            if self._point_in_geometry(
                longitude,
                latitude,
                geometry,
            ):
                return self._build_result(
                    tile,
                    method="polygon_containment",
                    distance_km=0.0,
                )

        # -----------------------------------------------------
        # Second: nearest tile fallback
        # -----------------------------------------------------

        nearest_tile = None
        nearest_distance = float("inf")

        for tile in self.tiles:

            centroid = self._tile_centroid(
                tile.get(
                    "geometry",
                    {},
                )
            )

            if centroid is None:
                continue

            centroid_lon, centroid_lat = centroid

            distance = self._haversine_km(
                latitude,
                longitude,
                centroid_lat,
                centroid_lon,
            )

            if distance < nearest_distance:
                nearest_distance = distance
                nearest_tile = tile

        if nearest_tile is None:
            raise ValueError(
                "Could not determine a suitable FortyGuard tile."
            )

        return self._build_result(
            nearest_tile,
            method="nearest_centroid",
            distance_km=nearest_distance,
        )

    # ---------------------------------------------------------
    # Geometry handling
    # ---------------------------------------------------------

    def _point_in_geometry(
        self,
        longitude: float,
        latitude: float,
        geometry: dict[str, Any],
    ) -> bool:

        if not isinstance(geometry, dict):
            return False

        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates")

        if not geometry_type or not coordinates:
            return False

        # -----------------------------------------------------
        # Polygon
        # -----------------------------------------------------

        if geometry_type == "Polygon":

            if not coordinates:
                return False

            outer_ring = coordinates[0]

            return self._point_in_polygon(
                longitude,
                latitude,
                outer_ring,
            )

        # -----------------------------------------------------
        # MultiPolygon
        # -----------------------------------------------------

        elif geometry_type == "MultiPolygon":

            for polygon in coordinates:

                if not polygon:
                    continue

                outer_ring = polygon[0]

                if self._point_in_polygon(
                    longitude,
                    latitude,
                    outer_ring,
                ):
                    return True

        return False

    # ---------------------------------------------------------
    # Point in polygon
    # ---------------------------------------------------------

    @staticmethod
    def _point_in_polygon(
        longitude: float,
        latitude: float,
        polygon: list[list[float]],
    ) -> bool:

        if not isinstance(polygon, list):
            return False

        if len(polygon) < 3:
            return False

        inside = False

        j = len(polygon) - 1

        for i in range(len(polygon)):

            try:
                xi, yi = polygon[i]
                xj, yj = polygon[j]
            except (TypeError, ValueError):
                j = i
                continue

            intersects = (
                ((yi > latitude) != (yj > latitude))
                and
                (
                    longitude
                    <
                    (xj - xi)
                    * (latitude - yi)
                    / (yj - yi)
                    + xi
                )
            )

            if intersects:
                inside = not inside

            j = i

        return inside

    # ---------------------------------------------------------
    # Centroid
    # ---------------------------------------------------------

    @staticmethod
    def _tile_centroid(
        geometry: dict[str, Any],
    ) -> tuple[float, float] | None:

        if not isinstance(geometry, dict):
            return None

        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates")

        if not coordinates:
            return None

        # -----------------------------------------------------
        # Polygon
        # -----------------------------------------------------

        if geometry_type == "Polygon":

            if not coordinates:
                return None

            ring = coordinates[0]

        # -----------------------------------------------------
        # MultiPolygon
        # -----------------------------------------------------

        elif geometry_type == "MultiPolygon":

            if not coordinates:
                return None

            if not coordinates[0]:
                return None

            ring = coordinates[0][0]

        else:
            return None

        if not ring:
            return None

        try:
            longitudes = [
                point[0]
                for point in ring
            ]

            latitudes = [
                point[1]
                for point in ring
            ]
        except (TypeError, IndexError):
            return None

        if not longitudes or not latitudes:
            return None

        return (
            sum(longitudes) / len(longitudes),
            sum(latitudes) / len(latitudes),
        )

    # ---------------------------------------------------------
    # Distance
    # ---------------------------------------------------------

    @staticmethod
    def _haversine_km(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:

        earth_radius_km = 6371.0

        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)

        delta_lat = radians(
            lat2 - lat1
        )

        delta_lon = radians(
            lon2 - lon1
        )

        a = (
            sin(delta_lat / 2) ** 2
            +
            cos(lat1_rad)
            * cos(lat2_rad)
            * sin(delta_lon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        return earth_radius_km * c

    # ---------------------------------------------------------
    # Result
    # ---------------------------------------------------------

    @staticmethod
    def _build_result(
        tile: dict[str, Any],
        method: str,
        distance_km: float,
    ) -> dict[str, Any]:

        temperature = tile.get(
            "average_temperature_C"
        )

        if temperature is None:
            raise ValueError(
                "Tile does not contain average temperature."
            )

        geometry = tile.get(
            "geometry",
            {},
        )

        centroid = SpatialMapper._tile_centroid(
            geometry
        )

        result = {
            "tile_id": tile.get(
                "tile_id"
            ),

            "temperature_C": float(
                temperature
            ),

            "min_temperature_C": float(
                tile.get(
                    "min_temperature_C",
                    temperature,
                )
            ),

            "max_temperature_C": float(
                tile.get(
                    "max_temperature_C",
                    temperature,
                )
            ),

            "mapping_method": method,

            "distance_km": float(
                distance_km
            ),

            # Diagnostic information:
            # Exact FortyGuard geometry selected
            # for the transformer.
            "geometry": geometry,

            # Diagnostic information:
            # Centroid of the selected FortyGuard tile.
            "tile_centroid": (
                {
                    "longitude": float(
                        centroid[0]
                    ),
                    "latitude": float(
                        centroid[1]
                    ),
                }
                if centroid is not None
                else None
            ),
        }

        return result

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_coordinates(
        latitude: float,
        longitude: float,
    ) -> None:

        if not (-90 <= latitude <= 90):
            raise ValueError(
                "Latitude must be between -90 and 90."
            )

        if not (-180 <= longitude <= 180):
            raise ValueError(
                "Longitude must be between -180 and 180."
            )