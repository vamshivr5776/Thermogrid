from api.fortyguard_client import FortyGuardClient
from api.fortyguard_adapter import FortyGuardAdapter


class ThermoGridPipeline:

    def __init__(self):
        self.fortyguard = FortyGuardClient()

    def get_fortyguard_data(
        self,
        polygon_aoi,
        start_date,
        start_time,
        granularity=100,
    ):
        # 1. Create FortyGuard heatmap job
        activity_id = self.fortyguard.create_heatmap(
            polygon_aoi=polygon_aoi,
            start_date=start_date,
            start_time=start_time,
            granularity=granularity,
        )

        print("\nACTIVITY ID:")
        print(activity_id)

        # 2. Wait for FortyGuard to finish
        result = self.fortyguard.wait_for_result(
            activity_id=activity_id
        )

        # 3. Inspect the real response
        print("\n========== FORTYGUARD RESULT ==========")
        print(type(result))

        if isinstance(result, dict):
            print("RESULT KEYS:")
            print(result.keys())

            map_data = result.get("map_data")

            print("\nMAP DATA TYPE:")
            print(type(map_data))

            if isinstance(map_data, dict):
                print("MAP DATA KEYS:")
                print(map_data.keys())

                features = map_data.get("features")

                print("\nFEATURES TYPE:")
                print(type(features))

                if isinstance(features, list):
                    print("FEATURE COUNT:")
                    print(len(features))

                    if features:
                        print("\n========== FIRST FEATURE ==========")
                        print(features[0])

        # 4. Convert FortyGuard response into ThermoGrid tiles
        tiles = FortyGuardAdapter.extract_tiles(result)

        # 5. Calculate temperature statistics
        statistics = FortyGuardAdapter.temperature_statistics(
            tiles
        )

        # 6. Return clean pipeline result
        return {
            "activity_id": activity_id,
            "result": result,
            "tiles": tiles,
            "statistics": statistics,
        }