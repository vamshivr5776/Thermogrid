from thermal.aoi import create_aoi_around_point


def test_create_aoi_around_point():

    aoi = create_aoi_around_point(
        latitude=33.4484,
        longitude=-112.0740,
    )

    assert aoi["type"] == "Polygon"

    coordinates = aoi["coordinates"][0]

    assert len(coordinates) == 5

    assert coordinates[0] == coordinates[-1]


def test_aoi_contains_transformer_point():

    latitude = 33.4484
    longitude = -112.0740

    aoi = create_aoi_around_point(
        latitude=latitude,
        longitude=longitude,
    )

    coordinates = aoi["coordinates"][0]

    longitudes = [
        point[0]
        for point in coordinates
    ]

    latitudes = [
        point[1]
        for point in coordinates
    ]

    assert min(longitudes) < longitude < max(longitudes)
    assert min(latitudes) < latitude < max(latitudes)


def test_invalid_latitude():

    try:
        create_aoi_around_point(
            latitude=100,
            longitude=-112,
        )
        assert False
    except ValueError:
        assert True