import os
import time
import requests
from dotenv import load_dotenv


load_dotenv()


class FortyGuardClient:
    BASE_URL = "https://api.fortyguard.com"

    def __init__(self):
        self.api_key = os.getenv("FORTYGUARD_API_KEY")

        if not self.api_key:
            raise RuntimeError(
                "FORTYGUARD_API_KEY is missing from .env"
            )

        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def create_heatmap(
        self,
        polygon_aoi,
        start_date,
        start_time,
        granularity=100,
    ):
        payload = {
            "polygon_aoi": polygon_aoi,
            "date_time": {
                "start_date": start_date,
                "start_time": start_time,
                "filter_type": 1,
            },
            "granularity": granularity,
        }

        response = requests.post(
            f"{self.BASE_URL}/v1/heatmap",
            headers=self.headers,
            json=payload,
            timeout=60,
        )

        if not response.ok:
            print(
                "FORTYGUARD HTTP STATUS:",
                response.status_code
            )
            print(
                "FORTYGUARD RESPONSE:",
                response.text
            )

        response.raise_for_status()

        data = response.json()

        if data.get("error"):
            raise RuntimeError(
                data.get(
                    "message",
                    "FortyGuard heatmap request failed"
                )
            )

        return data["data"]["activity_id"]

    def get_status(self, activity_id):
        response = requests.get(
            f"{self.BASE_URL}/v1/status/{activity_id}",
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def wait_for_result(
        self,
        activity_id,
        max_attempts=120,
        delay=5,
    ):
        for attempt in range(max_attempts):

            response = self.get_status(activity_id)

            data = response.get("data", {})
            status = str(
                data.get("status", "")
            ).lower()

            if status in (
                "completed",
                "succeeded",
            ):
                return data.get("result")

            if status in (
                "failed",
                "error",
            ):
                raise RuntimeError(
                    f"FortyGuard task failed: {activity_id}"
                )

            time.sleep(delay)

        raise TimeoutError(
            f"FortyGuard task did not finish: {activity_id}"
        )