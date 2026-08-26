from data.api_integration.pipeline import ThermoGridPipeline


pipeline = ThermoGridPipeline()


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


response = pipeline.get_fortyguard_data(
    polygon_aoi=polygon,
    start_date="2025-07-15",
    start_time="14:00",
    granularity=100,
)


print("\n========== PIPELINE RESULT ==========")
print("Activity ID:", response["activity_id"])

print("\nSTATISTICS:")
print(response["statistics"])

print("\nNUMBER OF TILES:")
print(len(response["tiles"]))

print("\nFIRST TILE:")
print(response["tiles"][0])