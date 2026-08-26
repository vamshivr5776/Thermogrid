from typing import Any


def create_aoi_around_point(
    latitude: float,
    longitude: float,
    radius_latitude: float = 0.05,
    radius_longitude: float = 0.05,
) -> dict[str, Any]:
    """
    Create a rectangular GeoJSON Polygon around
    a transformer coordinate.

    The returned polygon is suitable for sending
    to the FortyGuard heatmap API.
    """

    if not -90 <= latitude <= 90:
        raise ValueError(
            "Latitude must be between -90 and 90."
        )

    if not -180 <= longitude <= 180:
        raise ValueError(
            "Longitude must be between -180 and 180."
        )

    if radius_latitude <= 0:
        raise ValueError(
            "radius_latitude must be greater than 0."
        )

    if radius_longitude <= 0:
        raise ValueError(
            "radius_longitude must be greater than 0."
        )

    south = latitude - radius_latitude
    north = latitude + radius_latitude

    west = longitude - radius_longitude
    east = longitude + radius_longitude

    if south < -90 or north > 90:
        raise ValueError(
            "Generated AOI exceeds latitude bounds."
        )

    if west < -180 or east > 180:
        raise ValueError(
            "Generated AOI exceeds longitude bounds."
        )

    return {
        "type": "Polygon",
        "coordinates": [[
            [west, south],
            [east, south],
            [east, north],
            [west, north],
            [west, south],
        ]],
    }