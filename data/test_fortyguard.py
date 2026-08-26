from api.fortyguard_client import FortyGuardClient


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

print("Activity ID:", activity_id)

result = client.wait_for_result(activity_id)

print("\nFORTYGUARD RESULT RECEIVED")
print("--------------------------------")
print("Statistics:")
print(result.get("stats_data"))
print("\nRESULT KEYS:")
print(result.keys())
print("\nMAP DATA TYPE:")
print(type(result.get("map_data")))

map_data = result.get("map_data", {})
features = map_data.get("features", [])

print("\nNUMBER OF FEATURES:")
print(len(features))

if features:
    print("\nFIRST FEATURE:")
    print(features[0])

    print("\nFIRST FEATURE KEYS:")
    print(features[0].keys())
    from api.fortyguard_adapter import FortyGuardAdapter
from thermal.spatial_mapper import SpatialMapper


# Convert the real FortyGuard response
tiles = FortyGuardAdapter.extract_tiles(result)

print("\n" + "=" * 50)
print("THERMOGRID REAL DATA PIPELINE")
print("=" * 50)

print(f"FortyGuard tiles received : {len(tiles)}")

# Create spatial mapper
mapper = SpatialMapper(tiles)

# Test transformer location
# This location is inside the example AOI used earlier.
transformer_latitude = 40.707
transformer_longitude = -74.016

mapped = mapper.map_transformer(
    latitude=transformer_latitude,
    longitude=transformer_longitude,
)

print("\nTRANSFORMER LOCATION")
print(f"Latitude  : {transformer_latitude}")
print(f"Longitude : {transformer_longitude}")

print("\nFORTYGUARD TEMPERATURE")
print(f"Tile ID   : {mapped['tile_id']}")
print(f"Temperature : {mapped['temperature_C']:.2f} °C")
print(f"Minimum     : {mapped['min_temperature_C']:.2f} °C")
print(f"Maximum     : {mapped['max_temperature_C']:.2f} °C")
print(f"Mapping     : {mapped['mapping_method']}")
print(f"Distance    : {mapped['distance_km']:.4f} km")