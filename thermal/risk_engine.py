from dataclasses import dataclass


@dataclass
class ThermalRisk:
    level: str
    score: float
    hotspot_temperature: float
    aging_factor: float
    message: str


class ThermalRiskEngine:

    def __init__(
        self,
        warning_temperature=110.0,
        critical_temperature=120.0,
        emergency_temperature=130.0,
    ):
        self.warning_temperature = warning_temperature
        self.critical_temperature = critical_temperature
        self.emergency_temperature = emergency_temperature

    def evaluate(
        self,
        hotspot_temperature: float,
        aging_factor: float,
    ) -> ThermalRisk:

        if hotspot_temperature >= self.emergency_temperature:
            level = "EMERGENCY"
            message = "Immediate thermal overload risk."

        elif hotspot_temperature >= self.critical_temperature:
            level = "CRITICAL"
            message = "Transformer thermal stress is critical."

        elif hotspot_temperature >= self.warning_temperature:
            level = "WARNING"
            message = "Transformer approaching thermal limit."

        else:
            level = "SAFE"
            message = "Transformer operating within thermal limits."

        # Temperature contribution
        temperature_score = min(
            hotspot_temperature / self.emergency_temperature * 100,
            100,
        )

        # Aging contribution
        aging_score = min(
            aging_factor / 10.0 * 100,
            100,
        )

        score = max(
            temperature_score,
            aging_score,
        )

        return ThermalRisk(
            level=level,
            score=round(score, 2),
            hotspot_temperature=round(
                hotspot_temperature, 2
            ),
            aging_factor=round(
                aging_factor, 3
            ),
            message=message,
        )